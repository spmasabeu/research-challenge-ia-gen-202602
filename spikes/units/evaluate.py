"""Ejecutar inferencia o comprobar los resultados vigentes del spike."""

import argparse
import collections
import datetime
import hashlib
import json
import math
import platform
import shutil
import subprocess
import urllib.request
from pathlib import Path

from units import extract_answer, tasks, verify


def metrics(rows, ks=(1, 3)):
    """pass@k = 1 - C(n-c,k)/C(n,k); no imputar errores de razonamiento."""
    groups = collections.defaultdict(list)
    for row in rows:
        groups[row["id"]].append(row["status"])
    counts = collections.Counter(row["status"] for row in rows)
    total = sum(counts.values())
    parsed = total - counts["unparsed"]
    scores = {}
    upper_scores = {}
    for k in ks:
        if groups and all(len(statuses) >= k for statuses in groups.values()):
            scores[str(k)] = sum(
                (
                    math.comb(len(statuses), k)
                    - math.comb(len(statuses) - statuses.count("correct"), k)
                )
                / math.comb(len(statuses), k)
                for statuses in groups.values()
            ) / len(groups)
            upper_scores[str(k)] = sum(
                (
                    math.comb(len(statuses), k)
                    - math.comb(
                        len(statuses)
                        - statuses.count("correct")
                        - statuses.count("unparsed"),
                        k,
                    )
                )
                / math.comb(len(statuses), k)
                for statuses in groups.values()
            ) / len(groups)
    return {
        "tasks": len(groups),
        "responses": total,
        "statuses": dict(counts),
        "coverage": parsed / total if total else None,
        "accuracy_parsed": counts["correct"] / parsed if parsed else None,
        "pass_at_k": scores,
        "pass_at_k_upper_bound": upper_scores,
        "note": "pass@k mide éxito verificable; unparsed no demuestra fallo de razonamiento. accuracy_parsed es condicional, no un ranking general.",
    }


def api(path, payload=None, timeout=180):
    data = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(
        "http://127.0.0.1:11434/api/" + path,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def code_hashes():
    return {
        name + "_sha256": hashlib.sha256(
            Path(__file__).with_name(name + ".py").read_bytes()
        ).hexdigest()
        for name in ("units", "evaluate")
    }


def evaluate_response(task, row):
    completion = row["response"]["message"]["content"]
    automatic = extract_answer(completion)
    automatic_status = verify(task, completion)
    result = {
        "id": row["id"],
        "sample": row["sample"],
        "response": row["response"],
        "automatic_status": automatic_status,
        "automatic_extracted": list(automatic) if automatic is not None else None,
        "status": automatic_status,
        "extracted": list(automatic) if automatic is not None else None,
    }
    if "manual_review" in row:
        review = row["manual_review"]
        if automatic_status != "unparsed":
            raise ValueError("Revisión manual sobre una respuesta ya interpretable")
        if (
            not isinstance(review.get("evidence"), str)
            or not review["evidence"].strip()
        ):
            raise ValueError("Revisión manual sin evidencia")
        if (
            review["completion_sha256"]
            != hashlib.sha256(completion.encode()).hexdigest()
        ):
            raise ValueError("El hash de la respuesta revisada no coincide")
        status = verify(
            task, json.dumps({"value": review["value"], "unit": review["unit"]})
        )
        if status == "unparsed":
            raise ValueError("Extracción manual inválida")
        result.update(
            status=status,
            extracted=[review["value"], review["unit"]],
            manual_review=review,
        )
    return result


def summarize(dataset, rows, model):
    indexed = {task["id"]: task for task in dataset}
    views = {}
    for view, status_key in (("automatic", "automatic_status"), ("final", "status")):
        scored = [
            {
                "id": row["id"],
                "level": indexed[row["id"]]["level"],
                "family": indexed[row["id"]]["family"],
                "status": row[status_key],
            }
            for row in rows
        ]
        summary = {"overall": metrics(scored)}
        for key in ("level", "family"):
            summary[key] = {
                str(value): metrics([row for row in scored if row[key] == value])
                for value in sorted({row[key] for row in scored})
            }
        views[view] = summary
    return {
        "model": model,
        **views,
        "manual_reviews": sum("manual_review" in row for row in rows),
        "truncated": sum(
            row["response"].get("done_reason") == "length" for row in rows
        ),
    }


def analyze(source):
    metadata = json.loads((source / "metadata.json").read_text())
    raw_tasks = (source.parent / "tasks.jsonl").read_bytes()
    raw_responses = (source / "responses.jsonl").read_bytes()
    if hashlib.sha256(raw_tasks).hexdigest() != metadata["dataset_sha256"]:
        raise ValueError("El hash de tareas no coincide con los metadatos")
    if hashlib.sha256(raw_responses).hexdigest() != metadata["responses_sha256"]:
        raise ValueError("El hash de respuestas no coincide con los metadatos")
    for key, digest in code_hashes().items():
        if digest != metadata["evaluation"][key]:
            raise ValueError("El hash del evaluador no coincide con los metadatos")
    dataset = list(map(json.loads, raw_tasks.splitlines()))
    indexed = {task["id"]: task for task in dataset}
    if not dataset or len(indexed) != len(dataset):
        raise ValueError("Tareas vacías o IDs duplicados")
    rows = []
    seen = set()
    for row in map(json.loads, raw_responses.splitlines()):
        key = (row["id"], row["sample"])
        if type(row["sample"]) is not int or key in seen or row["id"] not in indexed:
            raise ValueError("Respuesta duplicada o tarea/muestra inválida")
        seen.add(key)
        computed = evaluate_response(indexed[row["id"]], row)
        if computed != row:
            raise ValueError(f"Clasificación o extracción inconsistente: {key}")
        rows.append(computed)
    expected = {
        (task_id, sample)
        for task_id in indexed
        for sample in range(metadata["samples"])
    }
    if seen != expected:
        raise ValueError("Ejecución incompleta o índices de muestra inválidos")
    return summarize(dataset, rows, metadata["model"])


def comparison(root):
    models = {}
    protocols = set()
    for source in sorted(root.iterdir()):
        if not source.is_dir():
            continue
        summary = analyze(source)
        saved = json.loads((source / "summary.json").read_text())
        if summary != saved:
            raise ValueError(f"Resumen inconsistente: {source.name}")
        metadata = json.loads((source / "metadata.json").read_text())
        protocols.add(
            (
                metadata["dataset_sha256"],
                json.dumps(metadata["options"], sort_keys=True),
                tuple(metadata["seeds"]),
                metadata["think"],
                metadata["samples"],
            )
        )
        models[source.name] = {
            "model": summary["model"],
            "automatic": summary["automatic"]["overall"],
            "final": summary["final"]["overall"],
            "manual_reviews": summary["manual_reviews"],
            "truncated": summary["truncated"],
        }
    if not models or len(protocols) != 1:
        raise ValueError(
            "No hay ejecuciones o sus tareas/configuraciones son diferentes"
        )
    return {
        "dataset_sha256": next(iter(protocols))[0],
        "models": models,
        "note": "Las cotas reflejan extracciones pendientes, no intervalos de confianza. La vista final conserva las revisiones contextuales documentadas.",
    }


def run(model, output, samples):
    if samples < 1:
        raise ValueError("samples debe ser positivo")
    if output.exists():
        raise FileExistsError(output)
    dataset = tasks()
    raw_tasks = "".join(
        json.dumps(task, ensure_ascii=False) + "\n" for task in dataset
    ).encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    task_file = output.parent / "tasks.jsonl"
    if task_file.exists():
        if task_file.read_bytes() != raw_tasks:
            raise ValueError("El conjunto compartido de tareas es diferente")
    else:
        with task_file.open("xb") as stream:
            stream.write(raw_tasks)
    output.mkdir()
    gpu = None
    if shutil.which("nvidia-smi"):
        gpu = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,driver_version",
                "--format=csv,noheader",
            ],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
    environment = {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "gpu": gpu,
        "ollama": api("version"),
    }
    environment_file = output.parent / "environment.json"
    if not environment_file.exists():
        with environment_file.open("x") as stream:
            json.dump(environment, stream, ensure_ascii=False, indent=2)
    tags = api("tags")
    metadata = {
        "model": model,
        "model_info": api("show", {"model": model}),
        "digest": next(tag["digest"] for tag in tags["models"] if tag["name"] == model),
        "ollama": environment["ollama"],
        "options": {
            "temperature": 0.7 if samples > 1 else 0,
            "num_predict": 1024,
            "num_ctx": 4096,
        },
        "think": False,
        "samples": samples,
        "seeds": list(range(42, 42 + samples)),
        "inference_utc": datetime.datetime.now(datetime.UTC).isoformat(),
        "inference_git_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        "inference_script_sha256": code_hashes()["evaluate_sha256"],
        "dataset_seed": 43,
        "dataset_sha256": hashlib.sha256(raw_tasks).hexdigest(),
        "evaluation": code_hashes(),
        "environment": environment,
        "note": "Spike exploratorio, sin entrenamiento ni test final. La clasificación automática se separa de la extracción contextual manual.",
    }
    metadata_file = output / "metadata.json"
    metadata_file.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
    indexed = {task["id"]: task for task in dataset}
    rows = []
    with (output / "responses.jsonl").open("x") as stream:
        for task in dataset:
            for sample in range(samples):
                response = api(
                    "chat",
                    {
                        "model": model,
                        "messages": [{"role": "user", "content": task["prompt"]}],
                        "stream": False,
                        "think": False,
                        "options": {**metadata["options"], "seed": 42 + sample},
                    },
                )
                row = evaluate_response(
                    indexed[task["id"]],
                    {"id": task["id"], "sample": sample, "response": response},
                )
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                stream.flush()
                rows.append(row)
                print(f"{task['id']} sample={sample}: {row['status']}", flush=True)
    metadata["responses_sha256"] = hashlib.sha256(
        (output / "responses.jsonl").read_bytes()
    ).hexdigest()
    metadata_file.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
    summary = summarize(dataset, rows, model)
    (output / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    )
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inference = commands.add_parser(
        "run", help="Ejecutar un modelo en una carpeta nueva"
    )
    inference.add_argument("--model", default="qwen3:1.7b")
    inference.add_argument("--samples", type=int, default=3)
    inference.add_argument("--output", type=Path, required=True)
    check = commands.add_parser(
        "check", help="Reevaluar respuestas y comprobar resúmenes sin inferencia"
    )
    check.add_argument(
        "root", type=Path, nargs="?", default=Path(__file__).parent / "results"
    )
    args = parser.parse_args()
    if args.command == "run":
        if args.samples < 1:
            parser.error("--samples debe ser positivo")
        result = run(args.model, args.output, args.samples)
    else:
        result = comparison(args.root)
        stored = args.root / "comparison.json"
        if stored.exists() and result != json.loads(stored.read_text()):
            raise ValueError("Comparación inconsistente")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

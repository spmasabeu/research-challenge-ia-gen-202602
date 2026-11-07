"""Línea base: inferencia local (Ollama), re-puntuación y métricas pass@k.

Las respuestas crudas se guardan siempre; `score` recalcula estados con el
verificador *actual*, así que corregir el parser no obliga a repetir inferencia
(el informe debe usar la versión final del verificador, como pide el curso).

Uso:
    PYTHONPATH=src python -m challenge.evaluate run --tasks data/units-v1/eval.jsonl \
        --model qwen3:1.7b --samples 4 --out runs/eval/qwen3-1.7b
    PYTHONPATH=src python -m challenge.evaluate score runs/eval/qwen3-1.7b
"""

import argparse
import collections
import datetime
import hashlib
import json
import math
import platform
import subprocess
import urllib.request
from pathlib import Path

from challenge.verifier import verify

OLLAMA = "http://127.0.0.1:11434/api/"


def pass_at_k(n, c, k):
    """Estimador insesgado de Chen et al. (2021): 1 - C(n-c,k)/C(n,k)."""
    if n < k:
        raise ValueError("n < k")
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


def metrics(rows, ks=(1, 3)):
    """rows: dicts con id y status. pass@k solo si todas las tareas tienen n >= k."""
    groups = collections.defaultdict(list)
    for row in rows:
        groups[row["id"]].append(row["status"])
    counts = collections.Counter(row["status"] for row in rows)
    total = sum(counts.values())
    parsed = total - counts["unparsed"] - counts["too_long"]
    result = {
        "tasks": len(groups),
        "responses": total,
        "statuses": dict(sorted(counts.items())),
        "coverage": parsed / total if total else None,
        "accuracy_parsed": counts["correct"] / parsed if parsed else None,
        "pass_at_k": {},
        # Cota superior: cuenta como correctas las respuestas no interpretadas.
        "pass_at_k_upper_bound": {},
    }
    for k in ks:
        if not groups or any(len(s) < k for s in groups.values()):
            continue
        for key, good in (
            ("pass_at_k", ("correct",)),
            ("pass_at_k_upper_bound", ("correct", "unparsed")),
        ):
            result[key][str(k)] = sum(
                pass_at_k(len(s), sum(x in good for x in s), k) for s in groups.values()
            ) / len(groups)
    return result


def summarize(tasks, rows, ks):
    indexed = {t["id"]: t for t in tasks}
    scored = [
        {**row, "level": indexed[row["id"]]["level"], "family": indexed[row["id"]]["family"]}
        for row in rows
    ]
    summary = {"overall": metrics(scored, ks)}
    for key in ("level", "family"):
        summary[key] = {
            value: metrics([r for r in scored if r[key] == value], ks)
            for value in sorted({r[key] for r in scored})
        }
    summary["family_level"] = {
        f"{f}/{lvl}": metrics(
            [r for r in scored if r["family"] == f and r["level"] == lvl], ks
        )
        for f, lvl in sorted({(r["family"], r["level"]) for r in scored})
    }
    # Tareas con aciertos y fallos entre sus muestras: señal útil para RL/DPO.
    by_task = collections.defaultdict(list)
    for r in scored:
        by_task[r["id"]].append(r["status"])
    summary["mixed_tasks"] = sum(
        "correct" in s and any(x in ("numeric", "unit") for x in s)
        for s in by_task.values()
    )
    return summary


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line]


def _api(path, payload=None, timeout=300):
    data = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(
        OLLAMA + path, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def _git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def run(tasks_path, model, out, samples, think=False, num_predict=1024, temperature=0.7):
    """Muestrear `samples` respuestas por tarea. Reanuda si `out` ya existe."""
    tasks = read_jsonl(tasks_path)
    out.mkdir(parents=True, exist_ok=True)
    raw_tasks = Path(tasks_path).read_bytes()
    metadata = {
        "model": model,
        "tasks_file": str(tasks_path),
        "tasks_sha256": hashlib.sha256(raw_tasks).hexdigest(),
        "samples": samples,
        "seeds": list(range(42, 42 + samples)),
        "think": think,
        "options": {"temperature": temperature, "num_predict": num_predict, "num_ctx": 4096},
        "git_commit": _git_commit(),
        "platform": platform.platform(),
    }
    meta_path = out / "metadata.json"
    if meta_path.exists():
        saved = json.loads(meta_path.read_text())
        keys = ("model", "tasks_sha256", "samples", "think", "options")
        if any(saved[k] != metadata[k] for k in keys):
            raise ValueError("La carpeta contiene otra configuración; usa otra --out")
    else:
        metadata["ollama"] = _api("version")
        metadata["started_utc"] = datetime.datetime.now(datetime.UTC).isoformat()
        meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n")
    responses = out / "responses.jsonl"
    done = {(r["id"], r["sample"]) for r in read_jsonl(responses)} if responses.exists() else set()
    with responses.open("a") as stream:
        for task in tasks:
            for sample in range(samples):
                if (task["id"], sample) in done:
                    continue
                response = _api(
                    "chat",
                    {
                        "model": model,
                        "messages": [{"role": "user", "content": task["prompt"]}],
                        "stream": False,
                        "think": think,
                        "options": {**metadata["options"], "seed": 42 + sample},
                    },
                )
                completion = response["message"]["content"]
                row = {
                    "id": task["id"],
                    "sample": sample,
                    "completion": completion,
                    "done_reason": response.get("done_reason"),
                    "eval_count": response.get("eval_count"),
                    "total_duration_ns": response.get("total_duration"),
                    "status": verify(task, completion),
                }
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                stream.flush()
                print(f"{task['id']} s={sample}: {row['status']}", flush=True)
    return score(out)


def score(out, ks=None):
    """Re-verificar respuestas guardadas con el verificador actual y resumir."""
    metadata = json.loads((out / "metadata.json").read_text())
    tasks = read_jsonl(metadata["tasks_file"])
    if hashlib.sha256(Path(metadata["tasks_file"]).read_bytes()).hexdigest() != metadata["tasks_sha256"]:
        raise ValueError("El archivo de tareas cambió desde la inferencia")
    indexed = {t["id"]: t for t in tasks}
    rows = [
        {"id": r["id"], "sample": r["sample"], "status": verify(indexed[r["id"]], r["completion"])}
        for r in read_jsonl(out / "responses.jsonl")
    ]
    if len({(r["id"], r["sample"]) for r in rows}) != len(rows):
        raise ValueError("Respuestas duplicadas")
    expected = len(tasks) * metadata["samples"]
    ks = ks or sorted({1, metadata["samples"]})
    summary = {
        "model": metadata["model"],
        "complete": len(rows) == expected,
        "verifier_sha256": _verifier_hash(),
        **summarize(tasks, rows, ks),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    return summary


def _verifier_hash():
    here = Path(__file__).parent
    digest = hashlib.sha256()
    for name in ("parser.py", "units.py", "verifier.py"):
        digest.update((here / name).read_bytes())
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    r = commands.add_parser("run", help="Inferencia con Ollama (reanudable)")
    r.add_argument("--tasks", type=Path, required=True)
    r.add_argument("--model", default="qwen3:1.7b")
    r.add_argument("--samples", type=int, default=4)
    r.add_argument("--out", type=Path, required=True)
    r.add_argument("--think", action="store_true")
    r.add_argument("--num-predict", type=int, default=1024)
    r.add_argument("--temperature", type=float, default=0.7)
    s = commands.add_parser("score", help="Re-verificar una carpeta de resultados")
    s.add_argument("out", type=Path)
    args = parser.parse_args()
    if args.command == "run":
        if args.samples < 1:
            parser.error("--samples debe ser positivo")
        result = run(
            args.tasks, args.model, args.out, args.samples,
            args.think, args.num_predict, args.temperature,
        )
    else:
        result = score(args.out)
    print(json.dumps(result["overall"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

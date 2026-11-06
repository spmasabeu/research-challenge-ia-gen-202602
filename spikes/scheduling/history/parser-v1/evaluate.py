"""Inferencia local secuencial y comprobación sin modelos; patrón de units."""

import argparse
import collections
import datetime
import fcntl
import hashlib
import json
import math
import platform
import subprocess
import time
import urllib.request
from pathlib import Path

import scheduling as domain

OPTIONS = {"temperature": 0.7, "num_predict": 1024, "num_ctx": 4096}
SEEDS = [42, 43, 44]


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes():
    return {p.name: digest(p) for p in (Path(__file__), Path(domain.__file__))}


def api(path, payload=None):
    request = urllib.request.Request(
        "http://127.0.0.1:11434/api/" + path,
        data=None if payload is None else json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        return json.load(response)


def metrics(rows):
    groups = collections.defaultdict(list)
    for row in rows:
        groups[row["id"]].append(row["status"])
    counts = collections.Counter(r["status"] for r in rows)
    scores = {}
    for k in (1, 3):
        if groups and all(len(s) >= k for s in groups.values()):
            scores[str(k)] = sum(
                1 - math.comb(len(s) - s.count("correct"), k) / math.comb(len(s), k)
                for s in groups.values()
            ) / len(groups)
    return {
        "tasks": len(groups),
        "responses": len(rows),
        "statuses": dict(counts),
        "coverage": 1 - counts["unparsed"] / len(rows) if rows else None,
        "pass_at_k": scores,
    }


def summarize(dataset, rows):
    indexed = {t["id"]: t for t in dataset}
    result = {
        "overall": metrics(rows),
        "level": {
            level: metrics([r for r in rows if indexed[r["id"]]["level"] == level])
            for level in ("easy", "medium", "hard")
        },
    }
    result["cost"] = {
        "wall_seconds": sum(r["wall_seconds"] for r in rows),
        "prompt_tokens": sum(
            c.get("prompt_eval_count", 0) for r in rows for c in r["calls"]
        ),
        "output_tokens": sum(c.get("eval_count", 0) for r in rows for c in r["calls"]),
        "truncated_calls": sum(
            c.get("done_reason") == "length" for r in rows for c in r["calls"]
        ),
        "calls": sum(len(r["calls"]) for r in rows),
    }
    result["distinct_completions_per_task"] = sum(
        len({r["completion"] for r in rows if r["id"] == key}) for key in indexed
    ) / len(dataset)
    return result


def freeze(root, pilot=False):
    dataset = domain.tasks(seed=99 if pilot else 43)
    if pilot:
        dataset = [
            next(t for t in dataset if t["level"] == level)
            for level in ("easy", "medium", "hard")
        ]
    raw = "".join(json.dumps(t, ensure_ascii=False) + "\n" for t in dataset)
    root.mkdir(parents=True, exist_ok=True)
    path = root / "tasks.jsonl"
    if path.exists():
        if path.read_text() != raw:
            raise ValueError("dataset congelado diferente")
    else:
        path.write_text(raw)
    return dataset


def attempt(task, model, seed):
    messages = [{"role": "user", "content": task["prompt"]}]
    response = api(
        "chat",
        {
            "model": model,
            "messages": messages,
            "stream": False,
            "think": False,
            "options": {**OPTIONS, "seed": seed},
        },
    )
    return response["message"]["content"], [response], messages


def analyze(source):
    metadata = json.loads((source / "metadata.json").read_text())
    root = source.parent
    for file, expected in metadata["artifacts"].items():
        path = root / file
        if digest(path) != expected:
            raise ValueError(f"hash incorrecto: {file}")
    if metadata["code"] != hashes():
        raise ValueError("código cambió desde la evaluación")
    if (
        metadata["options"] != OPTIONS
        or metadata["seeds"] != SEEDS
        or metadata["think"] is not False
    ):
        raise ValueError("protocolo diferente")
    dataset = [
        json.loads(line) for line in (root / "tasks.jsonl").read_text().splitlines()
    ]
    expected_tasks = domain.tasks(seed=99 if metadata["pilot"] else 43)
    if metadata["pilot"]:
        expected_tasks = [
            next(t for t in expected_tasks if t["level"] == level)
            for level in ("easy", "medium", "hard")
        ]
    if dataset != expected_tasks:
        raise ValueError("tareas no reproducibles")
    indexed = {t["id"]: t for t in dataset}
    rows = [
        json.loads(line)
        for line in (source / "responses.jsonl").read_text().splitlines()
    ]
    seen = set()
    for row in rows:
        key = row["id"], row["sample"]
        if (
            type(row["sample"]) is not int
            or not 0 <= row["sample"] < metadata["samples"]
            or key in seen
            or key[0] not in indexed
            or row["seed"] != SEEDS[row["sample"]]
        ):
            raise ValueError("muestra duplicada o inválida")
        seen.add(key)
        task = indexed[row["id"]]
        if row["prompt"] != task["prompt"] or row["messages"][0] != {
            "role": "user",
            "content": task["prompt"],
        }:
            raise ValueError("prompt diferente")
        if row["calls"][-1]["message"]["content"] != row["completion"]:
            raise ValueError("respuesta cruda diferente")
        if row["status"] != domain.verify(task, row["completion"]):
            raise ValueError("clasificación diferente")
    if seen != {(t["id"], s) for t in dataset for s in range(metadata["samples"])}:
        raise ValueError("corrida incompleta")
    return summarize(dataset, rows)


def comparison(root):
    result = {}
    for source in sorted(root.iterdir()):
        if not source.is_dir() or not (source / "metadata.json").exists():
            continue
        summary = analyze(source)
        if summary != json.loads((source / "summary.json").read_text()):
            raise ValueError("resumen diferente")
        result[source.name] = summary
    if not result:
        raise ValueError("sin modelos evaluados")
    return result


def run(model, output, pilot=False):
    if output.exists():
        raise FileExistsError(output)
    with (Path.home() / ".cache" / "research-challenge-local-inference.lock").open(
        "a"
    ) as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        dataset = freeze(output.parent, pilot)
        tags = api("tags")["models"]
        tag = next(t for t in tags if t["name"] == model)
        environment = {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "ollama": api("version"),
            "gpu": subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total,driver_version",
                    "--format=csv,noheader",
                ],
                capture_output=True,
                text=True,
                check=False,
            ).stdout.strip(),
        }
        environment_file = output.parent / "environment.json"
        if not environment_file.exists():
            dump(environment_file, environment)
        output.mkdir()
        samples = 1 if pilot else 3
        metadata = {
            "model": model,
            "model_tag": tag,
            "model_info": api("show", {"model": model}),
            "options": OPTIONS,
            "seeds": SEEDS,
            "think": False,
            "samples": samples,
            "pilot": pilot,
            "code": hashes(),
            "environment": environment,
            "started_utc": datetime.datetime.now(datetime.UTC).isoformat(),
            "git_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip(),
            "artifacts": {
                "tasks.jsonl": digest(output.parent / "tasks.jsonl"),
                "environment.json": digest(environment_file),
            },
        }
        dump(output / "metadata.json", metadata)
        rows = []
        with (output / "responses.jsonl").open("x") as stream:
            for task in dataset:
                for sample in range(samples):
                    started = time.monotonic()
                    completion, calls, messages = attempt(task, model, SEEDS[sample])
                    row = {
                        "id": task["id"],
                        "sample": sample,
                        "seed": SEEDS[sample],
                        "prompt": task["prompt"],
                        "completion": completion,
                        "calls": calls,
                        "messages": messages,
                        "wall_seconds": time.monotonic() - started,
                        "status": domain.verify(task, completion),
                    }
                    stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                    stream.flush()
                    rows.append(row)
                    print(f"{model} {task['id']} {sample}: {row['status']}", flush=True)
        metadata["artifacts"][output.name + "/responses.jsonl"] = digest(
            output / "responses.jsonl"
        )
        metadata["finished_utc"] = datetime.datetime.now(datetime.UTC).isoformat()
        dump(output / "metadata.json", metadata)
        dump(output / "summary.json", summarize(dataset, rows))
        dump(output.parent / "comparison.json", comparison(output.parent))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    runner = sub.add_parser("run")
    runner.add_argument("--model", required=True)
    runner.add_argument("--output", type=Path, required=True)
    runner.add_argument("--pilot", action="store_true")
    checker = sub.add_parser("check")
    checker.add_argument(
        "root", type=Path, nargs="?", default=Path(__file__).with_name("results")
    )
    args = parser.parse_args()
    if args.command == "run":
        run(args.model, args.output, args.pilot)
    else:
        result = comparison(args.root)
        if result != json.loads((args.root / "comparison.json").read_text()):
            raise ValueError("comparación diferente")
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

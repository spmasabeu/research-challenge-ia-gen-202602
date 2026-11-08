"""CLI del desafío. Ejecutar con PYTHONPATH=src python -m challenge.harness."""

import argparse
import json
from pathlib import Path

from .evaluate import summarize
from .generator import dump, generate
from .models import read_rows, run, sha256, validate_rows
from .verifier import VERSION, load_tasks


def main():
    parser = argparse.ArgumentParser(__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate")
    gen.add_argument("--seed", type=int, required=True)
    gen.add_argument("--groups", type=int, required=True)
    gen.add_argument("--out", type=Path, required=True)
    infer = sub.add_parser("run")
    infer.add_argument("--tasks", type=Path, required=True)
    infer.add_argument("--out", type=Path, required=True)
    infer.add_argument("--model", required=True)
    infer.add_argument("--samples", type=int, required=True)
    infer.add_argument("--max-tokens", type=int, default=1024)
    score = sub.add_parser("score")
    score.add_argument("--tasks", type=Path, required=True)
    score.add_argument("--run", type=Path, required=True)
    score.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "generate":
        tasks = generate(args.seed, args.groups)
        load_tasks(tasks)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        dump(args.out, tasks)
    elif args.command == "run":
        run(args.tasks, args.out, args.model, args.samples, args.max_tokens)
    else:
        tasks = read_rows(args.tasks)
        load_tasks(tasks)
        rows = read_rows(args.run / "responses.jsonl")
        config = json.loads((args.run / "metadata.json").read_text())["config"]
        if sha256(args.tasks) != config["tasks_sha256"]:
            raise ValueError("tareas cambiaron")
        validate_rows(tasks, rows, config["model"], config["samples"])
        for row in rows:
            expected = {**config["options"], "seed": 42 + row["sample_index"]}
            if row["request"]["options"] != expected or row["request"]["model"] != config["model"] or row["request"]["think"] != config["think"]:
                raise ValueError("configuración de respuesta inconsistente")
        scored, summary = summarize(tasks, rows)
        args.out.mkdir(parents=True, exist_ok=False)
        dump(args.out / "labels.jsonl", scored)
        metadata = {"verifier_version": VERSION, "source_sha256": sha256(Path(__file__).with_name("verifier.py")),
                    "metrics_source_sha256": sha256(Path(__file__).with_name("evaluate.py")),
                    "responses_sha256": sha256(args.run / "responses.jsonl"), "tasks_sha256": sha256(args.tasks)}
        for name, value in (("summary.json", summary), ("metadata.json", metadata)):
            (args.out / name).write_text(json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n")
        for name in ("verifier.py", "evaluate.py"):
            (args.out / name).write_bytes(Path(__file__).with_name(name).read_bytes())
        print(json.dumps(summary["all"], ensure_ascii=False))


if __name__ == "__main__":
    main()

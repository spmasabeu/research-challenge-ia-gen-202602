"""Respaldos E2: exclusiones históricas, recalificación y muestras de auditoría."""

import argparse
import importlib.util
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

from challenge.derive import collect, required_audits
from challenge.evaluate_hf import write_json
from challenge.generator import dump
from challenge.models import read_rows, sha256
from challenge.verifier import VERSION


def exclusions(root, out):
    keys, sources = set(), {}
    for path in sorted((root / "data/units").rglob("*.json*")):
        if "project-e2" in path.parts:
            continue
        found = set()
        if path.suffix == ".jsonl":
            found = {r["physical_key"] for r in read_rows(path) if "physical_key" in r}
        elif path.name == "exclusions.json":
            data = json.loads(path.read_text())
            found = set(data["keys"])
            # El manifiesto anterior registra también la conversión de los spikes.
            for source, digest in data.get("sources", {}).items():
                if sha256(root / source) != digest:
                    raise ValueError(f"fuente histórica cambió: {source}")
        if found:
            sources[str(path.relative_to(root))] = {"sha256": sha256(path), "keys": len(found)}
            keys.update(found)
    if not keys:
        raise ValueError("sin exclusiones históricas")
    write_json(out, {"keys": sorted(keys), "sources": sources,
                    "policy": "unión de claves físicas y exclusiones históricas; incluye spikes acreditados por sus fuentes"})


def regrade(tasks_path, run, out):
    from challenge.evaluate import summarize

    tasks, rows = read_rows(tasks_path), read_rows(run / "responses.jsonl")
    old = run / "code/verifier.py"
    spec = importlib.util.spec_from_file_location("historical_verifier", old)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    by_id = {t["id"]: t for t in tasks}
    labels, summary = summarize(tasks, rows)
    changes = []
    transitions = Counter()
    for row, label in zip(rows, labels):
        previous = module.verify(by_id[row["task_id"]], row["result"]["message"]["content"])
        if not row["result"]["done"]:
            previous = {"status": "unparsed", "reward": 0.0}
        transitions[previous["status"] + "->" + label["status"]] += 1
        if previous["status"] != label["status"]:
            changes.append({"task_id": row["task_id"], "sample_index": row["sample_index"],
                            "before": previous, "after": label})
    out.mkdir(parents=True, exist_ok=False)
    dump(out / "changes.jsonl", changes)
    dump(out / "labels.jsonl", labels)
    write_json(out / "summary.json", summary)
    write_json(out / "metadata.json", {"old_version": module.VERSION, "new_version": VERSION,
               "old_verifier_sha256": sha256(old), "responses_sha256": sha256(run / "responses.jsonl"),
               "tasks_sha256": sha256(tasks_path), "transitions": dict(transitions)})


def audit(tasks_path, run, out, teacher=False):
    if out.exists():
        raise FileExistsError(f"conservar auditoría existente: {out}")
    tasks, rows = read_rows(tasks_path), read_rows(run / "responses.jsonl")
    records, _ = collect(tasks, rows, str(run))
    if teacher:
        selected = required_audits(records)
    else:
        cells = defaultdict(list)
        for r in records:
            if r["status"] == "correct":
                cells[r["family"], r["level"]].append(r)
        selected = set()
        for cell in cells.values():
            cell.sort(key=lambda r: r["candidate_id"])
            selected.update(r["candidate_id"] for r in random.Random(7304).sample(cell, min(3, len(cell))))
    dump(out, [{**r, "completion_sha256": r["sources"][0]["completion_sha256"],
                "auditor": None, "reviewer_type": None, "judgment": None, "reason": None,
                "selection_seed": 4303 if teacher else 7304}
               for r in records if r["candidate_id"] in selected])


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("command", choices=("exclusions", "regrade", "audit"))
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--tasks", type=Path)
    parser.add_argument("--run", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--teacher", action="store_true")
    args = parser.parse_args()
    if args.command == "exclusions":
        exclusions(args.root, args.out)
    elif args.command == "regrade":
        regrade(args.tasks, args.run, args.out)
    else:
        audit(args.tasks, args.run, args.out, args.teacher)


if __name__ == "__main__":
    main()

"""Datos derivados desde ejecuciones sobre **train**: SFT y pares DPO.

- SFT: respuestas `correct` según el verificador actual (p. ej. de un modelo
  profesor más grande). Una respuesta final correcta no certifica el
  razonamiento: auditar una muestra a mano antes de entrenar.
- DPO: para un mismo prompt, chosen = correcta, rejected = respuesta legible e
  incorrecta (`numeric` o `unit`). Las `unparsed` no se usan como rejected: no
  prueban un error de razonamiento.

Uso:
    PYTHONPATH=src python -m challenge.derive --runs runs/train/qwen3-8b \
        runs/train/qwen3-1.7b --out data/units-v1/derived
"""

import argparse
import collections
import hashlib
import json
import random
from pathlib import Path

from challenge.evaluate import read_jsonl
from challenge.verifier import verify


def load_runs(run_dirs):
    """(task, model, completion, status) re-verificados con el verificador actual."""
    rows = []
    for run_dir in map(Path, run_dirs):
        metadata = json.loads((run_dir / "metadata.json").read_text())
        tasks = {t["id"]: t for t in read_jsonl(metadata["tasks_file"])}
        for r in read_jsonl(run_dir / "responses.jsonl"):
            task = tasks[r["id"]]
            if task["split"] != "train":
                raise ValueError(f"{r['id']} no es de train: SFT/DPO solo desde train")
            rows.append(
                {
                    "task": task,
                    "model": metadata["model"],
                    "completion": r["completion"],
                    "status": verify(task, r["completion"]),
                }
            )
    return rows


def build_sft(rows, max_per_task=2):
    by_task = collections.defaultdict(list)
    for row in rows:
        if row["status"] == "correct":
            by_task[row["task"]["id"]].append(row)
    out = []
    for task_id in sorted(by_task):
        seen = set()
        for row in by_task[task_id]:
            if row["completion"] in seen or len(seen) >= max_per_task:
                continue
            seen.add(row["completion"])
            out.append(
                {
                    "id": task_id,
                    "prompt": row["task"]["prompt"],
                    "completion": row["completion"],
                    "source_model": row["model"],
                    "level": row["task"]["level"],
                    "family": row["task"]["family"],
                }
            )
    return out


def build_dpo(rows, max_pairs_per_task=2, seed=0):
    rng = random.Random(seed)
    by_task = collections.defaultdict(lambda: {"good": [], "bad": []})
    for row in rows:
        if row["status"] == "correct":
            by_task[row["task"]["id"]]["good"].append(row)
        elif row["status"] in ("numeric", "unit"):
            by_task[row["task"]["id"]]["bad"].append(row)
    out = []
    for task_id in sorted(by_task):
        good, bad = by_task[task_id]["good"], by_task[task_id]["bad"]
        pairs = [(g, b) for g in good for b in bad]
        rng.shuffle(pairs)
        for g, b in pairs[:max_pairs_per_task]:
            out.append(
                {
                    "id": task_id,
                    "prompt": g["task"]["prompt"],
                    "chosen": g["completion"],
                    "rejected": b["completion"],
                    "chosen_model": g["model"],
                    "rejected_model": b["model"],
                    "rejected_status": b["status"],
                    "level": g["task"]["level"],
                    "family": g["task"]["family"],
                }
            )
    return out


def write_jsonl(path, rows):
    raw = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows).encode()
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", nargs="+", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--sft-per-task", type=int, default=2)
    parser.add_argument("--dpo-per-task", type=int, default=2)
    args = parser.parse_args()
    rows = load_runs(args.runs)
    args.out.mkdir(parents=True, exist_ok=True)
    sft = build_sft(rows, args.sft_per_task)
    dpo = build_dpo(rows, args.dpo_per_task)
    manifest = {
        "runs": args.runs,
        "sft": {"rows": len(sft), "sha256": write_jsonl(args.out / "sft.jsonl", sft)},
        "dpo": {"rows": len(dpo), "sha256": write_jsonl(args.out / "dpo.jsonl", dpo)},
    }
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

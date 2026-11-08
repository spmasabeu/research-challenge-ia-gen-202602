"""CLI del desafío. Ejecutar con PYTHONPATH=src python -m challenge.harness."""

import argparse
import json
from collections import Counter
from pathlib import Path

from .evaluate import summarize
from .generator import VERSION as GENERATOR_VERSION
from .generator import dump, generate, split_groups
from .models import OPTIONS, read_rows, run, sha256, validate_rows
from .verifier import UNITS, VERSION, load_tasks

FROZEN_FILES = ("generator.py", "verifier.py", "evaluate.py", "models.py")


def freeze(output, exclusions_path, models_path):
    exclusions = json.loads(exclusions_path.read_text())
    if not isinstance(exclusions["keys"], list) or not all(isinstance(k, str) for k in exclusions["keys"]):
        raise ValueError("exclusiones inválidas")
    tasks = generate(4301, 20, exclusions["keys"])
    splits = split_groups(tasks, 10, 4, 6)
    load_tasks(tasks)
    output.mkdir(parents=True, exist_ok=False)
    for directory in ("public", "private", "frozen-code"):
        (output / directory).mkdir()
    for split, rows in splits.items():
        dump(output / "private" / f"{split}.jsonl", rows)
        dump(output / "public" / f"{split}.jsonl", [{k: v for k, v in t.items() if k not in {"answer_si", "physical_key"}} for t in rows])
    (output / "exclusions.json").write_bytes(exclusions_path.read_bytes())
    (output / "models.json").write_bytes(models_path.read_bytes())
    protocol = {"dataset_version": "units-final-1", "generator_version": GENERATOR_VERSION, "verifier_version": VERSION,
                "generation_seed": 4301, "split_seed": 4302, "groups_per_family": 20,
                "groups": {"train": 10, "eval": 4, "test": 6}, "baseline_samples": 3, "teacher_train_samples": 4,
                "seed_base": 42, "think": False, "options": OPTIONS,
                "backend_incomplete_policy": "conservar intento como unparsed; no atribuir error matemático"}
    (output / "protocol.json").write_text(json.dumps(protocol, ensure_ascii=False, indent=2) + "\n")
    (output / "units.json").write_text(json.dumps(UNITS, ensure_ascii=False, indent=2) + "\n")
    for name in FROZEN_FILES:
        (output / "frozen-code" / name).write_bytes(Path(__file__).with_name(name).read_bytes())
    manifest = {"files": {str(p.relative_to(output)): sha256(p) for p in sorted(output.rglob("*")) if p.is_file()},
                "code": {name: sha256(Path(__file__).with_name(name)) for name in FROZEN_FILES}}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    check_dataset(output)


def check_dataset(root):
    manifest = json.loads((root / "manifest.json").read_text())
    if set(manifest["code"]) != set(FROZEN_FILES) or any(p.is_symlink() for p in root.rglob("*")):
        raise ValueError("código o enlaces inesperados")
    actual = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() and p.name != "manifest.json"}
    if actual != set(manifest["files"]):
        raise ValueError("archivos faltantes o extra en dataset congelado")
    for name, expected in manifest["files"].items():
        path = root / name
        if not path.resolve().is_relative_to(root.resolve()) or sha256(path) != expected:
            raise ValueError(f"archivo modificado o externo: {name}")
    for name, expected in manifest["code"].items():
        if sha256(Path(__file__).with_name(name)) != expected:
            raise ValueError(f"código normativo cambió: {name}")
    protocol = json.loads((root / "protocol.json").read_text())
    if protocol["generator_version"] != GENERATOR_VERSION or protocol["verifier_version"] != VERSION or protocol["options"] != OPTIONS:
        raise ValueError("versiones o parámetros inconsistentes")
    excluded = set(json.loads((root / "exclusions.json").read_text())["keys"])
    regenerated = generate(protocol["generation_seed"], protocol["groups_per_family"], excluded)
    groups = protocol["groups"]
    splits = split_groups(regenerated, groups["train"], groups["eval"], groups["test"], protocol["split_seed"])
    all_tasks = []
    seen = set()
    counts = {}
    for split, expected in splits.items():
        actual_tasks = read_rows(root / "private" / f"{split}.jsonl")
        if actual_tasks != expected:
            raise ValueError("regeneración no coincide con partición privada")
        public = [{k: v for k, v in t.items() if k not in {"answer_si", "physical_key"}} for t in expected]
        if read_rows(root / "public" / f"{split}.jsonl") != public:
            raise ValueError("prompts públicos o campos privados inconsistentes")
        keys = {t["physical_key"] for t in actual_tasks}
        if keys & (seen | excluded):
            raise ValueError("problemas físicos cruzados o excluidos")
        seen |= keys
        counts[split] = len(actual_tasks)
        cells = Counter((t["family"], t["level"], t["structure"]) for t in actual_tasks)
        if len(cells) != 18 or set(cells.values()) != {groups[split] // 2}:
            raise ValueError("celdas familia/nivel/estructura desbalanceadas")
        pairs = Counter(t["pair_id"] for t in actual_tasks)
        if set(pairs.values()) != {3}:
            raise ValueError("variantes físicas incompletas")
        all_tasks.extend(actual_tasks)
    load_tasks(all_tasks)
    if len({t["id"] for t in all_tasks}) != len(all_tasks):
        raise ValueError("IDs duplicados")
    return counts


def main():
    parser = argparse.ArgumentParser(__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate")
    gen.add_argument("--seed", type=int, required=True)
    gen.add_argument("--groups", type=int, required=True)
    gen.add_argument("--out", type=Path, required=True)
    frozen = sub.add_parser("freeze")
    frozen.add_argument("--out", type=Path, required=True)
    frozen.add_argument("--exclusions", type=Path, required=True)
    frozen.add_argument("--models", type=Path, required=True)
    check = sub.add_parser("check")
    check.add_argument("--dataset", type=Path, required=True)
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
    elif args.command == "freeze":
        freeze(args.out, args.exclusions, args.models)
    elif args.command == "check":
        print(json.dumps(check_dataset(args.dataset)))
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

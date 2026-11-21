"""Corridas E2 seriales en GPU: control, SFT, GRPO y SFT→GRPO, con evaluación común."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from challenge.evaluate_hf import write_json
from challenge.harness import check_dataset
from challenge.models import read_rows, sha256
from challenge.verifier import VERSION


def checkpoints_at_fractions(run, fractions):
    candidates = [(json.loads((p / "cost.json").read_text())["phase_train_seconds"], p)
                  for p in run.glob("checkpoint-*") if (p / "cost.json").exists()]
    if not candidates:
        raise ValueError("sin checkpoints con costo medido")
    duration = json.loads((run / "result.json").read_text())["phase_train_seconds"]
    selected = [min(candidates, key=lambda item: abs(item[0] - duration * fraction))[1] for fraction in fractions]
    if len(set(selected)) != len(selected):
        raise ValueError("checkpoints insuficientes para tres cortes distintos")
    return selected


def execute(args, log):
    args = list(map(str, args))
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a") as stream:
        stream.write(json.dumps({"command": args}) + "\n")
        stream.flush()
        subprocess.run([sys.executable, *args], env={**os.environ, "PYTHONPATH": "src"},
                       stdout=stream, stderr=subprocess.STDOUT, check=True)


def experiment(root, derived, stage):
    check_dataset(root / "dataset")
    runs = root / "runs"
    config = root / "config"
    train_path = root / "dataset/private/train.jsonl"
    evaluation = root / "dataset/private/eval.jsonl"
    curve_tasks = config / "eval-curves.jsonl"
    # Pertenencia exacta; nunca aceptar una muestra de test como curva de validación.
    eval_by_id = {t["id"]: t for t in read_rows(evaluation)}
    if any(t != eval_by_id.get(t["id"]) for t in read_rows(curve_tasks)):
        raise ValueError("curvas fuera de eval")
    full_config = json.loads((config / "evaluation.json").read_text())
    catalog = json.loads((root / "dataset/models.json").read_text())
    if full_config != catalog[full_config["model"]]["evaluation"] or full_config["samples"] != 3:
        raise ValueError("evaluación no coincide con protocolo congelado de tres muestras")
    curve_config = {**full_config, "samples": 1}
    curve_path = config / "curve-evaluation.json"
    if not curve_path.exists():
        write_json(curve_path, curve_config)
    elif json.loads(curve_path.read_text()) != curve_config:
        raise ValueError("protocolo de curvas cambió")

    def evaluate(name, tasks, protocol, adapter=None, seconds=0.0, step=0):
        output = runs / name
        command = ["-m", "challenge.evaluate_hf", "--tasks", tasks, "--config", protocol, "--out", output]
        if adapter:
            command += ["--adapter", adapter]
        execute(command, root / "validation" / f"{name}.log")
        point = {"evaluation": str(output), "tasks_sha256": sha256(tasks), "config_sha256": sha256(protocol),
                 "adapter": str(adapter) if adapter else None, "cumulative_train_seconds": seconds, "step": step}
        path = output / "training-point.json"
        if path.exists():
            if json.loads(path.read_text()) != point:
                raise ValueError("costo o referencia de evaluación cambió")
        else:
            write_json(path, point)

    evaluate("control", evaluation, config / "evaluation.json")
    evaluate("control-curves", curve_tasks, curve_path)
    if stage == "control":
        return
    if stage in {"sft", "hybrid", "all"}:
        if derived is None:
            raise ValueError("indicar derivados auditados para SFT")
        manifest = json.loads((derived / "manifest.json").read_text())
        if any(sha256(derived / name) != digest for name, digest in manifest.items()):
            raise ValueError("derivados modificados")
        stats = json.loads((derived / "stats.json").read_text())
        if stats["input_hashes"]["train"] != sha256(train_path) or stats["verifier"]["version"] != VERSION:
            raise ValueError("derivados de otros datos/verificador")
    methods = ("sft", "grpo", "hybrid") if stage == "all" else (stage,)
    for method in methods:
        name = "sft-grpo" if method == "hybrid" else method
        output = runs / name
        initial = None
        configuration = config / f"{'grpo' if method == 'hybrid' else method}.json"
        if method == "hybrid":
            sft = runs / "sft"
            initial = checkpoints_at_fractions(sft, [.25])[0]
            prior = json.loads((initial / "cost.json").read_text())["cumulative_train_seconds"]
            settings = json.loads(configuration.read_text())
            settings["budget_seconds"] -= prior
            if settings["budget_seconds"] <= 0:
                raise ValueError("SFT agotó presupuesto combinado")
            configuration = config / "sft-grpo.json"
            if configuration.exists():
                if json.loads(configuration.read_text()) != settings:
                    raise ValueError("presupuesto combinado cambió")
            else:
                write_json(configuration, settings)
            evaluate("sft-grpo-initial-curves", curve_tasks, curve_path, initial, prior, 0)
        if not (output / "result.json").exists():
            command = ["-m", "challenge.train", "--config", configuration, "--tasks", train_path, "--out", output]
            if method == "sft":
                command += ["--sft", derived / "sft.jsonl"]
            if initial:
                command += ["--initial-adapter", initial]
            if output.exists():
                checkpoints = sorted(output.glob("checkpoint-*"), key=lambda p: int(p.name.split("-")[-1]))
                if not checkpoints:
                    raise ValueError("intento sin checkpoint; conservarlo y usar destino nuevo")
                command += ["--resume", checkpoints[-1]]
            execute(command, root / "validation" / f"{name}.log")
        result = json.loads((output / "result.json").read_text())
        signature = json.loads((output / "metadata.json").read_text())["signature"]
        expected_method = "sft" if method == "sft" else "grpo"
        if result["pilot"] or result["method"] != expected_method or result["changed_tensors"] == 0 or signature["config"] != json.loads(configuration.read_text()):
            raise ValueError("corrida no válida para comparación")
        for checkpoint in checkpoints_at_fractions(output, [.25, .5, .75]):
            cost = json.loads((checkpoint / "cost.json").read_text())
            evaluate(f"{name}-{checkpoint.name}-eval", curve_tasks, curve_path, checkpoint,
                     cost["cumulative_train_seconds"], cost["step"])
        evaluate(f"{name}-final-curves", curve_tasks, curve_path, output / "final",
                 result["cumulative_train_seconds"], result["steps"])
        evaluate(f"{name}-final-eval", evaluation, config / "evaluation.json", output / "final",
                 result["cumulative_train_seconds"], result["steps"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--root", type=Path, default=Path("data/units/project-e2"))
    parser.add_argument("--derived", type=Path)
    parser.add_argument("--stage", choices=("control", "sft", "grpo", "hybrid", "all"), required=True)
    args = parser.parse_args()
    experiment(args.root, args.derived, args.stage)

"""Tablas, curvas sin suavizar y muestra humana desde artefactos; sin inferencia."""

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean, quantiles

from challenge.evaluate_hf import write_json
from challenge.models import read_rows, sha256
from challenge.verifier import VERSION


def paired_bootstrap(tasks, labels_by_route, repetitions=2000, seed=7305):
    """IC percentil pareado por problema, estratificado por familia/estructura."""
    by_id = {t["id"]: t for t in tasks}
    expected = {(t["id"], i) for t in tasks for i in range(3)}
    strata = defaultdict(set)
    groups = defaultdict(list)
    for task in tasks:
        groups[task["physical_key"]].append(task["id"])
        strata[task["family"], task["structure"]].add(task["physical_key"])
    if not tasks or any(len(ids) != 3 for ids in groups.values()) or "control" not in labels_by_route:
        raise ValueError("bootstrap requiere tríos físicos completos y control")
    scores = {}
    for route, labels in labels_by_route.items():
        if len(labels) != len(expected) or {(r["task_id"], r["sample_index"]) for r in labels} != expected:
            raise ValueError("bootstrap requiere las mismas tareas y tres respuestas completas")
        successes = defaultdict(list)
        for row in labels:
            successes[row["task_id"]].append(row["status"] == "correct")
        scores[route] = {key: {"1": mean(mean(successes[t]) for t in ids),
                              "3": mean(any(successes[t]) for t in ids)} for key, ids in groups.items()}
    rng = random.Random(seed)
    draws = {route: {k: [] for k in ("1", "3")} for route in scores}
    differences = {route: {k: [] for k in ("1", "3")} for route in scores}
    for _ in range(repetitions):
        selected = [key for cell in sorted(strata) for key in rng.choices(sorted(strata[cell]), k=len(strata[cell]))]
        sample = {route: {k: mean(points[key][k] for key in selected) for k in ("1", "3")}
                  for route, points in scores.items()}
        for route in scores:
            for k in ("1", "3"):
                draws[route][k].append(sample[route][k])
                differences[route][k].append(sample[route][k] - sample["control"][k])

    def interval(values):
        cuts = quantiles(values, n=40, method="inclusive")
        return [cuts[0], cuts[-1]]

    return {"physical_problems": len(groups), "tasks": len(by_id), "responses_per_route": len(expected),
            "seed": seed, "repetitions": repetitions, "method": "percentile 95%, paired physical blocks, family/structure strata",
            "limits": "Incertidumbre sobre problemas; no mide variación entre semillas de entrenamiento ni certifica pasos de razonamiento.",
            "routes": {route: {"pass_at_k": {k: mean(p[k] for p in points.values()) for k in ("1", "3")},
                               "ci95": {k: interval(draws[route][k]) for k in ("1", "3")},
                               "delta_control_ci95": {k: interval(differences[route][k]) for k in ("1", "3")}}
                       for route, points in scores.items()}}


def report(runs, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out.mkdir(parents=True, exist_ok=False)
    training, evaluation, sources = [], [], {}
    curve_points, checkpoints = [], {}
    comparable, protocols = {}, set()
    fig, axes = plt.subplots(2, 1, figsize=(8, 7), layout="constrained")
    plotted = [False, False]
    for run in sorted(runs.iterdir()):
        result = run / "result.json"
        if result.exists():
            sources[str(result)] = sha256(result)
            data = json.loads(result.read_text())
            checkpoints[run.name] = {p.name: json.loads((p / "cost.json").read_text())
                                     for p in sorted(run.glob("checkpoint-*")) if (p / "cost.json").exists()}
            training.append({"run": run.name, **{k: data[k] for k in (
                "method", "pilot", "steps", "changed_tensors", "phase_train_seconds",
                "prior_train_seconds", "cumulative_train_seconds", "peak_allocated_bytes", "termination")}})
            steps = read_rows(run / "steps.jsonl")
            sources[str(run / "steps.jsonl")] = sha256(run / "steps.jsonl")
            index = int(data["method"] == "grpo")
            field = "reward" if index else "loss"
            points = [r for r in steps if field in r]
            if points:
                label = run.name + (" (sin actualización)" if not data["changed_tensors"] else "")
                axes[index].plot([r["step"] for r in points], [r[field] for r in points], "o-", label=label)
                plotted[index] = True
        for summary in sorted((run / "scores").glob("*/summary.json")):
            sources[str(summary)] = sha256(summary)
            data = json.loads(summary.read_text())
            route_names = {"control": "control", "sft-final-eval": "sft", "grpo-final-eval": "grpo", "sft-grpo-final-eval": "sft-grpo"}
            if run.name in route_names and summary.parent.name == VERSION:
                for path in (run / "metadata.json", summary.parent / "metadata.json", summary.parent / "labels.jsonl"):
                    sources[str(path)] = sha256(path)
                metadata = json.loads((run / "metadata.json").read_text())
                cfg = metadata["config"]
                scoring = json.loads((summary.parent / "metadata.json").read_text())
                signature = {k: cfg[k] for k in ("model", "revision", "quantization", "samples", "generation",
                                               "max_context", "batch_size", "tasks_sha256", "runner_sha256")}
                protocols.add(json.dumps({**signature, "versions": metadata["versions"],
                                           "verifier": scoring["verifier_sha256"], "metrics": scoring["metrics_sha256"]}, sort_keys=True))
                comparable[route_names[run.name]] = read_rows(summary.parent / "labels.jsonl")
            point_path = run / "training-point.json"
            if point_path.exists() and data["all"]["n"] == 1:
                point = json.loads(point_path.read_text())
                curve_points.append({**point, "run": run.name, "pass_at_1": data["all"]["pass_at_k"]["1"]})
                sources[str(point_path)] = sha256(point_path)
            for cell, m in {"all": data["all"], **data["family_level"]}.items():
                assert sum(m["statuses"].values()) == m["responses"]
                evaluation.append({"run": run.name, "verifier": summary.parent.name, "cell": cell,
                    "tasks": m["tasks"], "responses": m["responses"], "samples": m["n"],
                    "pass_at_1": m["pass_at_k"]["1"], "pass_at_3": m["pass_at_k"].get("3"),
                    "coverage": m["coverage"], "truncated": m["truncated"],
                    **{s: m["statuses"].get(s, 0) for s in ("correct", "numeric", "unit", "unparsed", "too_long")}})
    for index, label in enumerate(("Pérdida SFT (train)", "Recompensa GRPO (train)")):
        axes[index].set(xlabel="Paso del optimizador", ylabel=label)
        if plotted[index]:
            axes[index].legend(fontsize=7)
        else:
            axes[index].text(.5, .5, "Sin datos ejecutados", ha="center", transform=axes[index].transAxes)
    axes[1].set_ylim(-.02, 1.02)
    fig.savefig(out / "training-curves.png", dpi=160)
    plt.close(fig)
    if curve_points:
        if len({(p["tasks_sha256"], p["config_sha256"]) for p in curve_points}) != 1:
            raise ValueError("no comparar curvas con muestra/protocolo distinto")
        fig, ax = plt.subplots(figsize=(8, 4), layout="constrained")
        control = [p for p in curve_points if p["run"] == "control-curves"]
        for route in ("sft", "grpo", "sft-grpo"):
            points = [p for p in curve_points if p["run"].startswith(route + "-")
                      and not (route == "sft" and p["run"].startswith("sft-grpo-"))]
            if points:
                points = sorted(control + points, key=lambda p: p["cumulative_train_seconds"])
                ax.plot([p["cumulative_train_seconds"] / 3600 for p in points],
                        [p["pass_at_1"] for p in points], "o-", label=route)
        if control:
            ax.axhline(control[0]["pass_at_1"], color="gray", linestyle="--", label="control")
        ax.set(xlabel="Horas acumuladas de entrenamiento (incluye SFT previo)", ylabel="pass@1 en eval fijo", ylim=(0, 1))
        ax.legend()
        fig.savefig(out / "validation-vs-compute.png", dpi=160)
        plt.close(fig)
        write_json(out / "validation-points.json", curve_points)
    write_json(out / "checkpoints.json", checkpoints)
    if "control" in comparable:
        if len(protocols) != 1:
            raise ValueError("comparación con protocolos, código o bibliotecas distintos")
        tasks_path = runs.parent / "dataset/private/eval.jsonl"
        sources[str(tasks_path)] = sha256(tasks_path)
        if json.loads(next(iter(protocols)))["tasks_sha256"] != sha256(tasks_path):
            raise ValueError("evaluación ajena al dataset")
        estimate = paired_bootstrap(read_rows(tasks_path), comparable)
        estimate["missing_routes"] = sorted({"control", "sft", "grpo", "sft-grpo"} - comparable.keys())
        write_json(out / "paired-uncertainty.json", estimate)
    for name, rows in (("training", training), ("evaluation", evaluation)):
        if rows:
            with (out / f"{name}.csv").open("x") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
    if evaluation:
        all_rows = [r for r in evaluation if r["cell"] == "all"]
        fig, ax = plt.subplots(figsize=(9, 4), layout="constrained")
        bottom = [0.0] * len(all_rows)
        for status in ("correct", "numeric", "unit", "unparsed", "too_long"):
            values = [r[status] / r["responses"] for r in all_rows]
            ax.bar([r["run"] for r in all_rows], values, bottom=bottom, label=status)
            bottom = [a + b for a, b in zip(bottom, values)]
        ax.set(ylabel="Fracción de todas las respuestas", ylim=(0, 1))
        ax.tick_params(axis="x", labelrotation=20)
        ax.legend()
        fig.savefig(out / "evaluation-errors.png", dpi=160)
        plt.close(fig)
    write_json(out / "manifest.json", {"sources": sources, "report_source_sha256": sha256(Path(__file__)),
               "artifacts": {p.name: sha256(p) for p in sorted(out.iterdir()) if p.is_file()},
               "limits": "Pilotos no son comparación de rutas. Pérdida/recompensa train no equivalen a validación. Sin suavizado."})
    return training, evaluation


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--runs", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    report(args.runs, args.out)

"""Figuras y tablas del informe desde métricas verificadas; no llama modelos."""

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

LEVELS = ("easy", "medium", "hard")
FAMILIES = ("speed", "energy", "luminosity")
MODELS = {
    "qwen3:1.7b": "Qwen3-1.7B",
    "llama3.2:1b": "Llama 3.2-1B",
    "smollm2:1.7b-instruct-q4_K_M": "SmolLM2-1.7B",
    "qwen3:8b": "Qwen3-8B (generador)",
    "deepseek/deepseek-v4-pro-0813": "DeepSeek-V4-Pro-0813",
}


def main():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--comparison", type=Path, required=True)
    parser.add_argument("--calibration", type=Path, required=True)
    parser.add_argument("--derived", type=Path, required=True)
    parser.add_argument("--frontier", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    comparison = json.loads(args.comparison.read_text())
    frontier_meta = json.loads((args.frontier / "metadata.json").read_text())
    if frontier_meta["verifier_sha256"] != comparison["verifier_sha256"] or frontier_meta["verifier_version"] != comparison["verifier_version"]:
        raise ValueError("referencia externa con evaluador diferente")
    comparison["models"]["deepseek/deepseek-v4-pro-0813"] = {"summary": json.loads((args.frontier / "summary.json").read_text())}
    calibration = json.loads(args.calibration.read_text())
    derived = json.loads(args.derived.read_text())
    if set(comparison["models"]) != set(MODELS) or comparison["verifier_version"] != derived["verifier"]["version"]:
        raise ValueError("matriz incompleta o evaluadores diferentes")
    assert all(r["summary"]["all"]["tasks"] == 54 and r["summary"]["all"]["responses"] == 162 for r in comparison["models"].values())
    assert sum(derived["sft_by_cell"].values()) == derived["sft"]
    assert sum(derived["dpo_by_cell"].values()) == derived["dpo"]
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / "figures").mkdir()
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "pdf.fonttype": 42})
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 4.0), layout="constrained")
    colors = ("#2563eb", "#d97706", "#059669", "#7c3aed", "#475569")
    hatches = ("", "//", "\\\\", "xx", "..")
    for index, (model, label) in enumerate(MODELS.items()):
        for ax, k in zip(axes, ("1", "3")):
            values = [100 * comparison["models"][model]["summary"]["level"][level]["pass_at_k"][k] for level in LEVELS]
            ax.bar([x + (index - 2) * .16 for x in range(3)], values, width=.15,
                   color=colors[index], hatch=hatches[index], edgecolor="black", linewidth=.3, label=label)
            ax.set(xticks=range(3), xticklabels=("Fácil", "Media", "Difícil"), ylim=(0, 100), title=f"pass@{k}")
            ax.grid(axis="y", alpha=.2)
            ax.set_axisbelow(True)
    axes[0].set_ylabel("Éxito verificable (%)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=2, frameon=False)
    for suffix in ("pdf", "png"):
        metadata = {"CreationDate": None, "ModDate": None} if suffix == "pdf" else {"Software": f"Matplotlib {matplotlib.__version__}"}
        fig.savefig(args.out / "figures" / f"baseline.{suffix}", dpi=180, metadata=metadata)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(5.2, 2.8), layout="constrained")
    values = [[100 * calibration["family_level"][f"{family}/{level}"]["pass_at_k"]["1"] for level in LEVELS] for family in FAMILIES]
    image = ax.imshow(values, cmap="Blues", vmin=0, vmax=100, aspect="auto")
    ax.set(xticks=range(3), xticklabels=("Fácil", "Media", "Difícil"), yticks=range(3),
           yticklabels=("Velocidad", "Energía", "Luminosidad"), title="Calibración: 30 respuestas por celda")
    for row in range(3):
        for column in range(3):
            value = values[row][column]
            ax.text(column, row, f"{value:.1f}%", ha="center", va="center", color="white" if value > 60 else "black")
    fig.colorbar(image, ax=ax, label="Éxito verificable (%)")
    for suffix in ("pdf", "png"):
        metadata = {"CreationDate": None, "ModDate": None} if suffix == "pdf" else {"Software": f"Matplotlib {matplotlib.__version__}"}
        fig.savefig(args.out / "figures" / f"calibration.{suffix}", dpi=180, metadata=metadata)
    plt.close(fig)
    with (args.out / "baseline.csv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["model", "level", "tasks", "responses", "correct", "numeric", "unit", "unparsed", "coverage", "pass_at_1", "upper_1", "pass_at_3", "upper_3", "truncated", "backend_incomplete"])
        for model in MODELS:
            for level in LEVELS:
                row = comparison["models"][model]["summary"]["level"][level]
                writer.writerow([model, level, row["tasks"], row["responses"], *[row["statuses"].get(status, 0) for status in ("correct", "numeric", "unit", "unparsed")], row["coverage"], row["pass_at_k"]["1"], row["pass_at_k_upper_bound"]["1"], row["pass_at_k"]["3"], row["pass_at_k_upper_bound"]["3"], row["truncated"], row["backend_incomplete"]])
    with (args.out / "derived.csv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["family", "level", "sft", "dpo"])
        for family in FAMILIES:
            for level in LEVELS:
                key = f"{family}/{level}"
                writer.writerow([family, level, derived["sft_by_cell"].get(key, 0), derived["dpo_by_cell"].get(key, 0)])
    tables = [r"\begingroup\small\setlength{\tabcolsep}{3pt}", r"\begin{table}[ht]", r"\centering", r"\begin{tabular}{lrrrr}",
              r"Modelo & pass@1 [sup.] & pass@3 [sup.] & Cobertura & No interpretadas \\", r"\midrule"]
    for model, label in MODELS.items():
        row = comparison["models"][model]["summary"]["all"]
        tables.append(f"{label} & {100 * row['pass_at_k']['1']:.2f} [{100 * row['pass_at_k_upper_bound']['1']:.2f}] & {100 * row['pass_at_k']['3']:.2f} [{100 * row['pass_at_k_upper_bound']['3']:.2f}] & {100 * row['coverage']:.2f} & {row['statuses'].get('unparsed', 0)} " + r"\\")
    tables += [r"\end{tabular}", r"\caption{Línea base: porcentajes sobre 54 tareas y 162 respuestas por modelo. Entre corchetes, cota optimista si todas las no interpretadas fueran correctas; no es intervalo de confianza.}",
               r"\label{tab:baseline}", r"\end{table}", r"\begin{table}[ht]", r"\centering", r"\begin{tabular}{llrr}",
               r"Modelo & Dificultad & pass@1 [sup.] & pass@3 [sup.] \\", r"\midrule"]
    for model, label in MODELS.items():
        for level, level_label in zip(LEVELS, ("Fácil", "Media", "Difícil")):
            row = comparison["models"][model]["summary"]["level"][level]
            tables.append(f"{label} & {level_label} & {100 * row['pass_at_k']['1']:.2f} [{100 * row['pass_at_k_upper_bound']['1']:.2f}] & {100 * row['pass_at_k']['3']:.2f} [{100 * row['pass_at_k_upper_bound']['3']:.2f}] " + r"\\")
    tables += [r"\end{tabular}", r"\caption{Resultados por dificultad: 18 tareas y 54 respuestas por fila. Corchetes: cota optimista de extracción, no intervalo de confianza.}", r"\label{tab:levels}", r"\end{table}"]
    tables.append(r"\endgroup")
    (args.out / "tables.tex").write_text("\n".join(tables) + "\n", encoding="utf-8")
    sources = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in {
        "local_comparison": args.comparison, "calibration": args.calibration, "derived": args.derived,
        "frontier_summary": args.frontier / "summary.json", "frontier_metadata": args.frontier / "metadata.json"}.items()}
    (args.out / "render-metadata.json").write_text(json.dumps({"python": sys.version, "matplotlib": matplotlib.__version__, "inputs": sources,
                                                            "renderer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                                                            "scope": "figuras de cuatro modelos locales y referencia externa; template aportado por usuario"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

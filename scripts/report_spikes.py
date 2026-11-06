"""Redactar tablas e informes desde resultados guardados, sin inferencia."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAMES = [
    "scheduling",
    "text_to_sql",
    "database_repair",
    "minesweeper",
    "cooperative_maze",
]
MODELS = ["qwen3-1.7b", "llama3.2-1b"]


def load(path):
    return json.loads(path.read_text())


def percent(value):
    return "—" if value is None else f"{100 * value:.2f}%"


def render(name):
    root = ROOT / "spikes" / name
    models = [m for m in MODELS if (root / "results" / m / "summary.json").exists()]
    if not models:
        return
    title = (root / "README.md").read_text().splitlines()[0].replace("# Spike: ", "")
    state = (
        "90 tareas y 540 respuestas/ trayectorias completas."
        if len(models) == 2
        else "Benchmark parcial: falta completar el segundo modelo."
    )
    lines = [
        f"# {title}",
        "",
        f"Resultados automáticos reales. {state}",
        "",
        "[Protocolo, generación, pruebas, alcance y comandos](README.md). [Artefactos](results/comparison.json).",
        "",
        "## Métricas",
        "",
        "| Modelo | Nivel | Aciertos / respuestas | pass@1 | pass@3 | Cobertura |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    summaries = {m: load(root / "results" / m / "summary.json") for m in models}
    for model, summary in summaries.items():
        if summary["overall"]["responses"] != 270:
            raise ValueError("No publicar una corrida incompleta como benchmark")
        for level, value in [("total", summary["overall"]), *summary["level"].items()]:
            lines.append(
                f"| {model} | {level} | {value['statuses'].get('correct', 0)}/{value['responses']} | {percent(value['pass_at_k'].get('1'))} | {percent(value['pass_at_k'].get('3'))} | {percent(value['coverage'])} |"
            )
    lines += [
        "",
        "## Costo",
        "",
        "| Modelo | Segundos de pared | Tokens entrada/salida | Llamadas | Truncadas | Textos distintos por tarea |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for model, summary in summaries.items():
        cost = summary["cost"]
        lines.append(
            f"| {model} | {cost['wall_seconds']:.1f} | {cost['prompt_tokens']}/{cost['output_tokens']} | {cost['calls']} | {cost['truncated_calls']} | {summary['distinct_completions_per_task']:.2f} |"
        )
    lines += [
        "",
        "Tiempo de pared suma llamadas con respuesta guardada; incluye carga/inferencia y herramientas. Tokens de entrada incluyen contextos reenviados. Textos distintos no prueban diversidad semántica. Las cuantizaciones difieren: Qwen Q4_K_M, Llama Q8_0. Versiones, pesos, entorno y hashes en metadata.json.",
        "",
        "## Estados y ejemplos automáticos",
        "",
    ]
    for model, summary in summaries.items():
        lines += [
            f"### {model}",
            "",
            "Estados: `"
            + json.dumps(summary["overall"]["statuses"], ensure_ascii=False)
            + "`.",
            "",
        ]
        rows = [
            json.loads(line)
            for line in (root / "results" / model / "responses.jsonl")
            .read_text()
            .splitlines()
        ]
        seen = set()
        for row in rows:
            if row["status"] in seen:
                continue
            seen.add(row["status"])
            text = row["completion"].replace("`", "'").replace("\n", " ")
            if len(text) > 240:
                text = text[:120] + " … " + text[-120:]
            lines.append(
                f"- `{row['id']}`, muestra {row['sample']}, `{row['status']}`: `{text}`"
            )
            if len(seen) == 5:
                break
        extra = {
            k: v
            for k, v in summary.items()
            if k not in {"overall", "level", "cost", "distinct_completions_per_task"}
        }
        if extra:
            lines += [
                "",
                "Diagnósticos específicos:",
                "",
                "```json",
                json.dumps(extra, ensure_ascii=False, indent=2),
                "```",
            ]
    lines += ["", "## Piloto separado", ""]
    pilot = root / ("pilot-v2" if name == "scheduling" else "pilot")
    for model in MODELS:
        path = pilot / model / "summary.json"
        if path.exists():
            value = load(path)
            cost = value["cost"]
            lines.append(
                f"- {model}: {value['overall']['responses']} respuestas; {cost['wall_seconds']:.1f} s; {cost['output_tokens']} tokens generados; {cost['truncated_calls']} truncamientos. Semilla 99, separado del benchmark."
            )
    lines += [
        "",
        "## Calibración y límites",
        "",
        "pass@k promedia 1-C(n-c,k)/C(n,k); pass@3 indica al menos un acierto en tres intentos. El éxito verificable depende del parser: unparsed y truncamiento no demuestran incapacidad lógica. Revisar aciertos y fallos interpretables por nivel junto a cobertura y truncamiento. Las etiquetas de dificultad son hipótesis generativas, no una escala cognitiva validada. No se incorporaron revisiones manuales a métricas ni reward.",
        "",
        "Las tareas se congelaron antes del benchmark, tras un piloto separado. Son exploratorias: no hay train/eval/test finales, SFT/DPO, entrenamiento ni baseline de frontera. Aumentar instancias de las mismas plantillas no asegura originalidad o profundidad. Una completion correcta no certifica sus pasos ni es SFT automáticamente. Ver README para debilidades específicas.",
        "",
    ]
    if name == "scheduling":
        lines += [
            "Ollama y la sesión se interrumpieron durante el experimento. Se retomaron solo muestras faltantes con mismos pesos, backend y código. Snapshots/hashes y eventos en interrupted/ y metadata.json. Costos excluyen llamadas abortadas sin respuesta y pausas entre sesiones; la velocidad del hardware varió.",
            "",
        ]
    if name == "minesweeper":
        lines += [
            "Baseline constante de clase mayoritaria: pass@1=pass@3=1/3. Una clasificación uniforme independiente al azar tendría pass@3=19/27≈70.37%; pass@3 alto por sí solo no prueba razonamiento.",
            "",
        ]
    if name == "database_repair":
        lines += [
            "Cada respuesta es una trayectoria de hasta cuatro llamadas; sus costos incluyen todas. No equivale a un turno de otros spikes. Las métricas clean/corrupted distinguen reparar de acertar con parche vacío en los nueve controles limpios.",
            "",
        ]
    path = root / "report.md"
    previous = path.read_text() if path.exists() else ""
    analysis = re.search(
        r"<!-- ANALYSIS_START -->[\s\S]*?<!-- ANALYSIS_END -->", previous
    )
    if analysis:
        lines += [analysis[0], ""]
    path.write_text("\n".join(lines))


def comparison():
    """Publicar la tabla solo cuando ambos modelos estén completos en cada tema."""
    topics = [
        ("units", "Unidades"),
        ("scheduling", "Scheduling"),
        ("text_to_sql", "SQL"),
        ("database_repair", "Reparación"),
        ("minesweeper", "Buscaminas"),
        ("cooperative_maze", "Laberinto"),
    ]
    required = [
        ROOT / "spikes" / name / "results" / model / "summary.json"
        for name, _ in topics
        for model in MODELS
    ]
    if not all(path.exists() for path in required):
        return False
    lines = [
        "## Comparación automática",
        "",
        "Éxito verificable con 90 tareas y tres muestras por tarea/modelo. Cada fila tiene su propio problema y protocolo; no es un ranking general de capacidad.",
        "",
        "| Tema | Qwen pass@1 / pass@3 | Cobertura Q | Llama pass@1 / pass@3 | Cobertura L | Minutos Q / L |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for name, title in topics:
        metrics = []
        minutes = []
        for model in MODELS:
            root = ROOT / "spikes" / name / "results"
            summary = load(root / model / "summary.json")
            if name == "units":
                value = summary["automatic"]["overall"]
                rows = [
                    json.loads(line)
                    for line in (root / model / "responses.jsonl")
                    .read_text()
                    .splitlines()
                ]
                duration = (
                    sum(row["response"].get("total_duration", 0) for row in rows) / 1e9
                )
            else:
                value = summary["overall"]
                duration = summary["cost"]["wall_seconds"]
            if value["responses"] != 270:
                raise ValueError("Comparación incompleta")
            metrics.append(value)
            minutes.append(None if duration is None else duration / 60)
        qwen, llama = metrics
        time_text = " / ".join(
            "—" if value is None else f"{value:.1f}" for value in minutes
        )
        lines.append(
            f"| [{title}]({name}/report.md) | {percent(qwen['pass_at_k'].get('1'))} / {percent(qwen['pass_at_k'].get('3'))} | {percent(qwen['coverage'])} | {percent(llama['pass_at_k'].get('1'))} / {percent(llama['pass_at_k'].get('3'))} | {percent(llama['coverage'])} | {time_text} |"
        )
    lines += [
        "",
        "La tabla usa exclusivamente métricas automáticas. Unidades conserva aparte cinco revisiones contextuales de Qwen: su resultado final 193/270 no se mezcla con el automático 191/270 ni con Llama sin revisión. unparsed no demuestra un error matemático; en Buscaminas incluye coordenadas equivocadas. Ver informes para categorías y límites.",
        "",
        "Costo orientativo: unidades suma duración del backend; los otros temas suman tiempo de los intentos con respuesta, incluyendo herramientas cuando existen. Se excluyen verificaciones posteriores, pausas y llamadas abortadas sin respuesta. Reparación usa hasta cuatro llamadas por trayectoria; los otros protocolos son de un turno. Hardware/velocidad y cuantización difieren; no atribuir diferencias causalmente a una sola variable.",
        "",
        "Temperatura 0.7, semillas 42/43/44, think=false, contexto 4096 y hasta 1024 tokens por llamada. Mismos problemas para ambos modelos dentro de cada tema. Los pilotos usan otras tareas (semilla 99); no entran en estas métricas.",
    ]
    begin, end = "<!-- COMPARISON_START -->", "<!-- COMPARISON_END -->"
    block = begin + "\n" + "\n".join(lines) + "\n" + end
    path = ROOT / "spikes/README.md"
    original = path.read_text() if path.exists() else "# Spikes\n"
    if begin in original and end in original:
        updated = re.sub(
            re.escape(begin) + r"[\s\S]*?" + re.escape(end), lambda _: block, original
        )
    else:
        updated = original.rstrip() + "\n\n" + block + "\n"
    path.write_text(updated)
    return True


if __name__ == "__main__":
    for spike in NAMES:
        render(spike)
    comparison()

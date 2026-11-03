# Spike: razonamiento cuantitativo con unidades

Pregunta: ¿Qwen3-1.7B tiene tanto aciertos como errores en problemas con fórmulas y conversiones explícitas? Comparación local con Llama 3.2-1B y Qwen3-8B sobre los mismos problemas.

Experimento exploratorio de 30 problemas, diez por dificultad. Código, pruebas, informe y resultados viven aquí. No importa módulos de `src/` ni necesita dependencias del proyecto. Usa solo la biblioteca estándar de Python; Ollama es un servicio externo local.

Ver el [informe del benchmark local](2026-11-03_165028_benchmark_local.md) para el protocolo, la comparación y sus límites. El resultado automático incluye cumplimiento del formato; no mide exclusivamente razonamiento numérico.

## Resultados guardados

| Modelo | Fácil /10 | Media /10 | Difícil /10 | Total /30 | Rechazos de formato |
| --- | --- | --- | --- | --- | --- |
| Qwen3-1.7B | 8 | 3 | 2 | 13 | 2 |
| Llama 3.2-1B | 0 | 0 | 0 | 0 | 30 |
| Qwen3-8B | 8 | 6 | 1 | 15 | 10 |

El 0/30 de Llama corresponde a rechazos de formato; se identificaron al menos cinco resultados numéricos correctos en su revisión cualitativa. Qwen3-8B también tiene respuestas correctas rechazadas por Markdown. Ver ejemplos en el informe antes de interpretar esta tabla como un ranking de razonamiento.

Las tres ejecuciones nuevas tardaron aproximadamente 10.7 minutos en total en el hardware documentado, sin contar descargas. No hubo respuestas truncadas. Los resultados agregados están en [comparison.json](results/benchmark-2026-11-03/comparison.json).

## Contenido

```text
spikes/units/
├── README.md
├── poc_units.py                          # generación, inferencia y verificación
├── test_poc_units.py                     # pruebas sin modelo
├── 2026-11-03_163130_poc_unidades.md       # informe, configuración y límites
├── 2026-11-03_165028_benchmark_local.md    # comparación de tres modelos
└── results/
    ├── 2026-11-03/                       # evidencia de la primera ejecución
    └── benchmark-2026-11-03/             # tres ejecuciones nuevas, una por modelo
```

## Requisitos

- Repositorio clonado con Git: el script registra el commit actual.
- `uv`, que selecciona o descarga Python 3.12.
- Ollama instalado y disponible en `http://127.0.0.1:11434`.
- Espacio para los tres modelos: aproximadamente 8 GB en total. La ejecución original usó una RTX 3050 de 6 GB; con CPU el tiempo puede aumentar. Ejecutar un modelo a la vez.

Los comandos usan `--no-project --isolated`: omiten el `pyproject.toml` principal y ejecutan en un entorno temporal aislado. No hace falta agregar dependencias, otro manifiesto ni Docker.

## Paso 1: entrar al spike

Desde la raíz del repositorio:

```bash
cd spikes/units
```

## Paso 2: preparar Ollama y el modelo

Si Ollama todavía no está corriendo, iniciar en otra terminal y dejarla abierta:

```bash
ollama serve
```

En la terminal del spike, descargar los tres modelos y comprobar que aparecen en la lista:

```bash
ollama pull qwen3:1.7b
ollama pull llama3.2:1b
ollama pull qwen3:8b
ollama list
```

Deben aparecer `qwen3:1.7b`, `llama3.2:1b` y `qwen3:8b`. Si la conexión es rechazada, comprobar que `ollama serve` sigue activo. Llama usa la variante Instruct distribuida por Ollama.

## Paso 3: comprobar el generador y el verificador

```bash
uv run --no-project --isolated --python 3.12 python -m unittest discover -s . -v
```

Se esperan tres pruebas correctas. No requieren Ollama ni GPU.

## Paso 4: ejecutar los mismos 30 problemas con los tres modelos

Ejecutar estos comandos uno después del otro; esperar a que termine cada uno:

```bash
uv run --no-project --isolated --python 3.12 python poc_units.py --model qwen3:1.7b --output results/repeticion-01/qwen3-1.7b
uv run --no-project --isolated --python 3.12 python poc_units.py --model llama3.2:1b --output results/repeticion-01/llama3.2-1b
uv run --no-project --isolated --python 3.12 python poc_units.py --model qwen3:8b --output results/repeticion-01/qwen3-8b
```

Cada directorio de salida debe ser nuevo: el script rechaza uno existente para preservar resultados. Para repetir, cambiar `repeticion-01` por `repeticion-02` en los tres comandos. La consola muestra cada problema y al final las tasas de acierto por dificultad. Si una ejecución falla, conservar sus archivos parciales y usar otro directorio al reintentar.

Configuración fija: semilla 42, temperatura 0, `think=false`, contexto 4096 y hasta 1024 tokens de salida. Tolerancia numérica relativa del 1%; unidades equivalentes dentro del catálogo del script. Puede cambiarse la etiqueta con `--model`, pero los resultados corresponderán a otro modelo.

## Paso 5: leer y comparar los resultados

Abrir el resumen de cada ejecución:

```bash
uv run --no-project --isolated --python 3.12 python -m json.tool results/repeticion-01/qwen3-1.7b/summary.json
uv run --no-project --isolated --python 3.12 python -m json.tool results/repeticion-01/llama3.2-1b/summary.json
uv run --no-project --isolated --python 3.12 python -m json.tool results/repeticion-01/qwen3-8b/summary.json
```

Para cada dificultad, `n` debe ser 10. `correct` indica aciertos, `accuracy` su proporción y `statuses` separa los tipos de resultado.

Cada ejecución produce:

| Archivo | Contenido |
| --- | --- |
| `tasks.jsonl` | Prompts, referencias y dificultad. Solo el prompt se envía al modelo. |
| `responses.jsonl` | Respuesta completa de Ollama y clasificación por problema. |
| `metadata.json` | Modelo, cuantización, versión de Ollama, parámetros, commit y hashes. |
| `summary.json` | Aciertos y tipos de error por dificultad. |

Estados: `correct` (respuesta aceptada), `numeric` (valor incorrecto), `unit` (unidad no admitida), `format` (respuesta no interpretable).

Para comparar las tres ejecuciones y comprobar que usan exactamente las mismas tareas y configuración, ejecutar lo siguiente. Genera `comparison.json` a partir de las respuestas guardadas; no llama al modelo. Para verificar nuestro benchmark, cambiar `results/repeticion-01` por `results/benchmark-2026-11-03`:

```bash
uv run --no-project --isolated --python 3.12 python - <<'PY'
import hashlib
import json
from collections import Counter
from pathlib import Path
from poc_units import verify

root = Path("results/repeticion-01")
runs = []
fingerprints = set()
for name in ("qwen3-1.7b", "llama3.2-1b", "qwen3-8b"):
    folder = root / name
    metadata = json.loads((folder / "metadata.json").read_text())
    raw_tasks = (folder / "tasks.jsonl").read_bytes()
    digest = hashlib.sha256(raw_tasks).hexdigest()
    assert digest == metadata["dataset_sha256"]
    fingerprints.add((digest, json.dumps(metadata["options"], sort_keys=True), metadata["think"], metadata["script_sha256"]))
    tasks = {task["id"]: task for task in map(json.loads, raw_tasks.splitlines())}
    responses = list(map(json.loads, (folder / "responses.jsonl").read_text().splitlines()))
    assert len(tasks) == len(responses) == len({row["id"] for row in responses}) == 30
    assert {row["id"] for row in responses} == set(tasks)
    counts = {level: Counter() for level in ("easy", "medium", "hard")}
    for row in responses:
        task = tasks[row["id"]]
        status = verify(task, row["response"]["message"]["content"])
        assert status == row["status"], row["id"]
        counts[task["level"]][status] += 1
    summary = json.loads((folder / "summary.json").read_text())
    for level, count in counts.items():
        assert count.total() == summary[level]["n"] == 10
        assert dict(count) == summary[level]["statuses"]
        assert count["correct"] == summary[level]["correct"]
        assert count["correct"] / 10 == summary[level]["accuracy"]
    totals = sum(counts.values(), Counter())
    run = {"model": metadata["model"], "details": metadata["model_info"]["details"], "summary": summary, "totals": dict(totals), "truncated": sum(row["response"].get("done_reason") == "length" for row in responses)}
    runs.append(run)
    print(metadata["model"], {level: count["correct"] for level, count in counts.items()}, dict(totals))
assert len(fingerprints) == 1, "Tareas, opciones o versión de script diferentes"
(root / "comparison.json").write_text(json.dumps(runs, ensure_ascii=False, indent=2))
print("90 respuestas verificadas; comparación guardada en", root / "comparison.json")
PY
```

La ejecución guardada en `results/2026-11-03/` incluye además `rescored.json`: **ese es el resultado válido del piloto original**. Su primer parser exigía `FINAL:` y rechazó todas las respuestas; se amplió para aceptar el JSON final sin prefijo y se reevaluaron las mismas salidas. Por eso su `summary.json` histórico muestra 0/30. Las ejecuciones nuevas usan directamente el parser corregido.

Resultado automático del piloto: 8/10 fáciles, 3/10 medias y 2/10 difíciles. Uno de los dos errores de formato era numéricamente correcto: 14/30 correctas tras revisión manual. Detalles y verificación de las puntuaciones guardadas en el [informe](2026-11-03_163130_poc_unidades.md).

Los archivos históricos se conservan sin cambios; sus hashes describen el código de aquella ejecución. Mover la carpeta no cambia los contenidos del script ni los datos originales.

## Paso 6: verificar la evidencia original sin inferencia

Este paso recalcula con el verificador actual las puntuaciones de las 30 respuestas que obtuvimos. No necesita Ollama y no modifica los archivos:

```bash
uv run --no-project --isolated --python 3.12 python - <<'PY'
import json
from collections import Counter
from pathlib import Path
from poc_units import verify

folder = Path("results/2026-11-03")
tasks = {
    task["id"]: task
    for task in map(json.loads, (folder / "tasks.jsonl").read_text().splitlines())
}
responses = [
    json.loads(line)
    for line in (folder / "responses.jsonl").read_text().splitlines()
]
saved = json.loads((folder / "rescored.json").read_text())
expected = {row["id"]: row["status"] for row in saved["results"]}
assert len(tasks) == len(responses) == len(expected) == 30
counts = {level: Counter() for level in ("easy", "medium", "hard")}
for response in responses:
    task = tasks[response["id"]]
    status = verify(task, response["response"]["message"]["content"])
    assert status == expected[task["id"]], task["id"]
    counts[task["level"]][status] += 1
for level, statuses in counts.items():
    print(f"{level}: {statuses['correct']}/10 correctas; {dict(statuses)}")
print("30 puntuaciones originales verificadas")
PY
```

Se esperan 8/10 en `easy`, 3/10 en `medium`, 2/10 en `hard` y el mensaje `30 puntuaciones originales verificadas`. Para reproducir la revisión manual, abrir en `responses.jsonl` los casos `medium-06` y `hard-03` y compararlos con las referencias descritas en el informe.

## Alcance

Este spike valida preliminarmente la elección del tema. No incluye entrenamiento, SFT/DPO, pass@k ni evaluación final. Las plantillas son limitadas y el verificador todavía no está endurecido contra ataques.

Comparar tres modelos locales no cubre por sí solo toda la línea base del desafío: todavía falta incorporar una referencia de frontera y el protocolo de múltiples muestras para pass@k. Los modelos usan cuantizaciones distintas (Llama Q8_0; Qwen Q4_K_M), por lo que tampoco se aísla el efecto de la familia o del tamaño.

No se garantiza repetir exactamente las respuestas entre versiones de Ollama, pesos o hardware. La etiqueta del modelo puede cambiar; comparar los metadatos antes de comparar tasas. No se probó `think=true`.

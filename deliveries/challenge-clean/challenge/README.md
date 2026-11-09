# Razonamiento cuantitativo con unidades

Entrega del desafío de investigación, IIC-3694, Pontificia Universidad Católica de Chile.
Fernando Fajardo, Sebastian Palma, Benjamin Prieto y Rodrigo Ugarte.

El [informe](informe.pdf) describe el problema, la generación del dataset, sus
particiones y niveles, los resultados y las limitaciones. Este paquete contiene
los archivos necesarios para usar el entorno y comprobar esos resultados.

| Contenido | Ubicación |
| --- | --- |
| Informe, descripción del dataset y línea base | `informe.pdf` |
| Generador, verificador, inferencia y pruebas | `code/src/challenge/`, `code/tests/` |
| Tareas train/eval/test sin soluciones | `data/tasks/public/` |
| Las mismas tareas con resultados esperados para evaluar | `data/tasks/private/` |
| Semillas, parámetros, unidades y modelos | `data/tasks/{protocol,units,models}.json` |
| 121 soluciones SFT y 35 pares DPO | `data/training/{sft,dpo}.jsonl` |
| Revisión de soluciones y cantidades por familia/nivel | `data/training/audits/`, `data/training/stats.json` |
| Instrucciones y comprobación de la entrega | `REPRODUCING.md`, `validation.json`, `manifest.json` |

Las 180 tareas representan 60 problemas físicos, cada uno con tres niveles.
Train/eval/test contienen 90/36/54 tareas. Para usar el entorno solo se necesita
Python 3.12 en Linux; el código usa su biblioteca estándar.

## Uso inicial

Desde esta carpeta, después de extraer el ZIP:

```bash
uv sync --locked --python 3.12
export PYTHONPATH="$PWD/code/src"
export PYTHONDONTWRITEBYTECODE=1
uv run --no-sync python -m unittest discover -s code/tests
uv run --no-sync python -m challenge.harness check --dataset data/tasks
```

El siguiente ejemplo carga las referencias de train y evalúa una respuesta,
sin consultar modelos:

```python
from pathlib import Path
from challenge import load_tasks, reward
from challenge.models import read_rows

tasks = read_rows(Path("data/tasks/private/train.jsonl"))
load_tasks(tasks)
task = tasks[0]
assert reward(task["prompt"], f'{task["answer_si"]} m/s') == 1.0
```

Al modelo se envía únicamente `task["prompt"]`. `answer_si` es el resultado
esperado en el Sistema Internacional y se reserva para evaluar. Un prompt no
registrado con `load_tasks` produce un error de integración.

## Por qué se incluye `results/`

| Carpeta | Qué permite comprobar |
| --- | --- |
| `baseline/` | Recalcular la línea base de los cuatro modelos locales a partir de sus respuestas y configuración. |
| `reference/` | Recalcular la referencia externa y comprobar los costos de test y controles sin llamadas pagadas. |
| `calibration/` | Recalcular las métricas de las pruebas preliminares del modelo objetivo. |
| `generation/` | Reconstruir SFT/DPO a partir de las respuestas originales del profesor y del objetivo y las auditorías. |

Cada corrida conserva respuestas, metadatos y los resultados finales pertinentes.
En la referencia externa se incluye `runner.py` para verificar la huella del
ejecutor que produjo las respuestas. No es un segundo evaluador.

SFT contiene `task_id`, `prompt`, `completion` y procedencia. DPO contiene
`task_id`, `prompt`, `chosen`, `rejected` y procedencia de ambas respuestas.
Los identificadores de tarea enlazan con train, y las fuentes `teacher` y
`negatives` remiten a las carpetas homónimas de `results/generation/`.

Las instrucciones completas están en [REPRODUCING.md](REPRODUCING.md).
Recalcular reproduce las cifras incluidas; generar respuestas nuevas puede
producir resultados distintos y requiere nuevas auditorías. No se entrenaron modelos.

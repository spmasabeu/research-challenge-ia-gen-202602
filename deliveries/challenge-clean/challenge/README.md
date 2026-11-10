# Razonamiento cuantitativo con unidades

Entrega del desafío de investigación, IIC-3694, Pontificia Universidad Católica de Chile.
Fernando Fajardo, Sebastian Palma, Benjamin Prieto y Rodrigo Ugarte.

El [informe](informe.pdf) describe el problema, la generación del dataset, sus
particiones y niveles, los resultados y las limitaciones. Este paquete contiene
los archivos necesarios para usar el entorno y los datos derivados.

| Contenido | Ubicación |
| --- | --- |
| Informe, descripción del dataset y línea base | `informe.pdf` |
| Generador, verificador, inferencia y pruebas | `code/src/challenge/`, `code/tests/` |
| Tareas train/eval/test sin soluciones | `data/tasks/public/` |
| Las mismas tareas con resultados esperados para evaluar | `data/tasks/private/` |
| Semillas, parámetros, unidades y modelos | `data/tasks/{protocol,units,models}.json` |
| 121 soluciones SFT y 35 pares DPO | `data/training/{sft,dpo}.jsonl` |
| Revisión de soluciones y cantidades por familia/nivel | `data/training/audits/`, `data/training/stats.json` |
| Instrucciones e integridad | `REPRODUCING.md`, `manifest.json` |

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

## Datos derivados y alcance

SFT contiene `task_id`, `prompt`, `completion` y procedencia. DPO contiene
`task_id`, `prompt`, `chosen`, `rejected` y procedencia de ambas respuestas.
Los identificadores enlazan con las tareas de train. El modelo generador,
filtrado, auditorías y cantidades se describen en el informe y en
`data/training/stats.json`.

[REPRODUCING.md](REPRODUCING.md) permite regenerar tareas, evaluar respuestas
y comprobar los SFT/DPO entregados usando los archivos de esta carpeta. Los
nombres `teacher` y `negatives` en los metadatos identifican la procedencia de
las respuestas y no son rutas que deban abrirse.

La entrega incluye los datasets finales y el informe de resultados, sin las
corridas experimentales. No se entrenaron modelos.

Para consultar mayor detalle de las iteraciones, las respuestas experimentales
y los resultados completos, puede solicitarse al equipo acceso a su
[repositorio de trabajo](https://github.com/spmasabeu/research-challenge-ia-gen-202602).
Es información complementaria y no se necesita para usar este paquete.

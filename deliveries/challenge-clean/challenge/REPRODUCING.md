# Reproducción de la entrega

Trabajar desde la carpeta `challenge/` extraída. Los pasos 1–5 usan archivos
incluidos y no realizan inferencias. Las nuevas salidas se guardan en un
directorio temporal para conservar intacta la evidencia entregada.

## 1. Comprobar integridad y preparar Python

Con Python 3.12 disponible, comprobar primero las huellas de los archivos:

```bash
python3 - <<'PY'
import hashlib
import json
from pathlib import Path

root = Path(".")
files = json.loads((root / "manifest.json").read_text())["files"]
assert all(hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
           for name, digest in files.items())
print("Integridad correcta")
PY
```

Preparar el entorno sin dependencias externas y un destino nuevo de trabajo:

```bash
uv sync --locked --python 3.12
export PYTHONPATH="$PWD/code/src"
export PYTHONDONTWRITEBYTECODE=1
units_check_dir=$(mktemp -d)
export units_check_dir
uv run --no-sync python -m unittest discover -s code/tests
```

También se puede utilizar directamente Python 3.12 con ese `PYTHONPATH`,
sustituyendo `uv run --no-sync python` por `python3` en los pasos siguientes.

## 2. Validar y regenerar las tareas

```bash
uv run --no-sync python -m challenge.harness check --dataset data/tasks
uv run --no-sync python -m challenge.harness freeze --out "$units_check_dir/tasks" --exclusions data/tasks/exclusions.json --models data/tasks/models.json
diff -qr data/tasks "$units_check_dir/tasks"
```

El resultado esperado es train/eval/test = 90/36/54, sin diferencias de archivos.
La regeneración usa las semillas, rangos y particiones del protocolo entregado,
incluidas las exclusiones que impiden reutilizar problemas de desarrollo.

Para generar un conjunto distinto con tres niveles por problema:

```bash
uv run --no-sync python -m challenge.harness generate --seed 5000 --groups 10 --out "$units_check_dir/new-tasks.jsonl"
```

`--groups 10` genera diez problemas por cada familia, con tres variantes cada
uno, es decir, 90 tareas. Esos datos nuevos no reemplazan el test entregado.

## 3. Reconstruir SFT y DPO

```bash
uv run --no-sync python -m challenge.harness check-derived --dataset data/tasks --teacher results/generation/teacher --audits data/training/audits/*.jsonl --negative-tasks results/generation/negatives/tasks.jsonl --negative-run results/generation/negatives --out data/training
uv run --no-sync python -m challenge.harness derive --dataset data/tasks --teacher results/generation/teacher --audits data/training/audits/*.jsonl --negative-tasks results/generation/negatives/tasks.jsonl --negative-run results/generation/negatives --out "$units_check_dir/training"
diff -qr data/training "$units_check_dir/training"
```

Se esperan 121 soluciones SFT y 35 pares DPO, idénticos a los entregados,
incluidas sus auditorías y procedencia. Las respuestas nuevas necesitarían
auditorías nuevas; los juicios existentes solo corresponden a los textos cuyos
identificadores y huellas están registrados.

## 4. Recalcular la línea base local y la referencia externa

```bash
uv run --no-sync python -m challenge.harness compare --dataset data/tasks --runs results/baseline --out "$units_check_dir/comparison.json"
cmp results/baseline/comparison.json "$units_check_dir/comparison.json"
uv run --no-sync python -m challenge.frontier score --tasks data/tasks/private/test.jsonl --run results/reference --out "$units_check_dir/reference"
diff -qr results/reference/scores "$units_check_dir/reference"
```

La comparación local comprueba configuración, integridad y las etiquetas y
métricas guardadas de los cuatro modelos. La evaluación externa verifica los
162 intentos y vuelve a calcular etiquetas, métricas y costo de test. Ninguno
de estos comandos se conecta con un proveedor.

## 5. Recalcular calibración y costos

```bash
uv run --no-sync python - <<'PY'
import json
from pathlib import Path
from challenge.evaluate import summarize
from challenge.models import read_rows

root = Path("results/calibration")
labels, summary = summarize(read_rows(root / "tasks.jsonl"),
                            read_rows(root / "responses.jsonl"))
assert labels == read_rows(root / "scores/labels.jsonl")
assert summary == json.loads((root / "scores/summary.json").read_text())
print("Calibración:", summary["all"]["pass_at_k"])

reference = Path("results/reference")
test = read_rows(reference / "responses.jsonl")
controls = read_rows(reference / "controls.jsonl")
test_cost = sum(row["result"]["usage"]["cost"] for row in test)
control_cost = sum(row["result"]["usage"]["cost"] for row in controls)
assert abs(test_cost - 0.0905151) < 1e-10
assert abs(control_cost - 0.0029965) < 1e-10
print("Costo USD, test + controles:", test_cost + control_cost)
PY
```

La calibración debe reproducir pass@1 = 48,89%, pass@3 = 65,56% y cobertura
95,56%. El costo externo total es USD 0,0935116. Un `diff` o `cmp` sin salida
y con retorno cero indica igualdad.

## Inferencias nuevas, opcionales

Para consultar modelos locales se necesita Ollama 0.18.0 y los pesos identificados
en `data/tasks/models.json`. Verificar sus huellas antes de ejecutar, porque
los nombres de descarga pueden pasar a señalar pesos diferentes.

```bash
uv run --no-sync python -m challenge.harness run --tasks data/tasks/private/test.jsonl --out "$units_check_dir/new-run" --model qwen3:1.7b --samples 3
uv run --no-sync python -m challenge.harness score --tasks data/tasks/private/test.jsonl --run "$units_check_dir/new-run" --out "$units_check_dir/new-scores"
```

Este último bloque sí genera respuestas y no es necesario para comprobar la
entrega. Solo se envía el campo `prompt` al modelo. Las semillas y configuración
se registran, pero las respuestas pueden variar entre motores o hardware.

La inferencia externa requiere una credencial OpenRouter y presupuesto propios.
Su interfaz se describe con `python -m challenge.frontier run --help`; usar un
destino y registro presupuestario nuevos para una ejecución nueva. Los archivos
incluidos se utilizan únicamente para recalcular y no para reanudar llamadas.

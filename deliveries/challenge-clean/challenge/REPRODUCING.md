# Reproducción de la entrega

Trabajar desde la carpeta `challenge/` extraída. Los pasos 1–3 usan archivos
incluidos y no realizan inferencias. Las nuevas salidas se guardan en un
directorio temporal para conservar intacta la datos entregados.

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

## 3. Cargar y comprobar SFT/DPO

Estos archivos contienen los datos finales. Se pueden cargar y verificar contra
las tareas de train sin acceder a las generaciones originales:

```bash
uv run --no-sync python - <<'PY'
import json
from pathlib import Path
from challenge.models import read_rows
from challenge.verifier import verify

train = {row["id"]: row for row in read_rows(Path("data/tasks/private/train.jsonl"))}
sft = read_rows(Path("data/training/sft.jsonl"))
dpo = read_rows(Path("data/training/dpo.jsonl"))
stats = json.loads(Path("data/training/stats.json").read_text())
assert len(sft) == stats["sft"] == 121
assert len(dpo) == stats["dpo"] == 35

for row in sft:
    task = train[row["task_id"]]
    assert row["prompt"] == task["prompt"]
    assert verify(task, row["completion"])["reward"] == 1.0

for row in dpo:
    task = train[row["task_id"]]
    assert row["prompt"] == task["prompt"]
    assert verify(task, row["chosen"])["reward"] == 1.0
    assert verify(task, row["rejected"])["status"] in {"numeric", "unit"}

print("121 soluciones SFT y 35 pares DPO válidos, todos de train")
PY
```

La comprobación confirma pertenencia a train y clasificación del resultado final,
no la coherencia de todos los pasos del razonamiento. Las revisiones registradas
están en `data/training/audits/` y su alcance se explica en el informe.

El ZIP permite usar estos datos, pero no reconstruir su selección desde todas
las respuestas generadas ni recalcular las métricas experimentales originales.
Un `diff` sin salida y con retorno cero en el paso 2 indica regeneración idéntica.

Todas las rutas de estas instrucciones parten de la carpeta `challenge/`
extraída. Para antecedentes adicionales del estudio, README indica cómo
solicitar acceso al repositorio de trabajo del equipo.

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
destino y registro presupuestario nuevos para una ejecución nueva. Las generaciones nuevas deben mantenerse separadas de los datos entregados y
requieren su propia evaluación y auditoría.

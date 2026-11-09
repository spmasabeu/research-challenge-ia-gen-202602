# Guía para repetir el experimento

Ejecutar desde la carpeta `challenge/` extraída del ZIP. Los comandos de este
documento presuponen Linux y Bash. El README contiene las recetas offline para
regenerar tareas, reconstruir SFT/DPO desde las fuentes incluidas y recalcular
métricas, figuras y PDF. Esas recetas no necesitan GPU, Ollama ni credenciales.

**Recalcular resultados guardados es determinista. Generar respuestas nuevas
puede dar resultados distintos**, incluso con las mismas semillas. En ese caso
se reportan las cantidades y métricas nuevas; no se fuerzan las cifras originales.

## 1. Preparar Python

Instalar [uv](https://docs.astral.sh/uv/getting-started/installation/) si falta.
La ejecución original usó uv 0.11.16 y Python 3.12.13. Después:

```bash
uv sync --python 3.12.13 --locked --group report
export PYTHONPATH="$PWD/code/src"
uv run --no-sync python -m unittest discover -s code/tests -v
uv run --no-sync python -m challenge.harness check --dataset data/final-v2
```

Esperado: 13 pruebas correctas y tamaños train/eval/test 90/36/54.
La instalación inicial requiere Internet o caché de dependencias; los recálculos
posteriores usan archivos incluidos. Con dependencias en caché se admite `uv sync --offline`.
El PDF requiere además los paquetes LaTeX enumerados en el README.

## 2. Preparar inferencia local

Solo para generar respuestas nuevas. Equipo original: RTX 3050 Laptop de
6144 MiB y 30,47 GiB de RAM. El runner usa `lscpu`, `free` y `nvidia-smi` para
registrar hardware; esta receta de inferencia se comprobó en Linux con NVIDIA.
No se validó ejecución del runner en Windows/macOS o en equipos sin NVIDIA.

Instalar Ollama 0.18.0 siguiendo la [guía oficial de Linux](https://docs.ollama.com/linux).
El instalador oficial permite seleccionar versión:

```bash
curl -fsSL https://ollama.com/install.sh | OLLAMA_VERSION=0.18.0 sh
ollama --version
lscpu
free -b
nvidia-smi
```

Iniciar `ollama serve` en otra terminal si no hay un servicio Ollama ejecutándose.
El harness se conecta a `http://127.0.0.1:11434`. Descargar los cuatro modelos
necesarios ([referencia de CLI](https://docs.ollama.com/cli)):

```bash
ollama pull qwen3:1.7b
ollama pull llama3.2:1b
ollama pull smollm2:1.7b-instruct-q4_K_M
ollama pull qwen3:8b
```

Los pesos originales suman aproximadamente 9 GB en disco, además de entornos y
resultados. Consultar las licencias de `data/final-v2/models.json` antes de usarlos.
Comprobar las revisiones locales contra el catálogo congelado, sin inferencia:

```bash
uv run --no-sync python - <<'PY'
import json
import urllib.request
from pathlib import Path

catalog = json.loads(Path("data/final-v2/models.json").read_text())
with urllib.request.urlopen("http://127.0.0.1:11434/api/tags") as response:
    installed = {m["name"]: m for m in json.load(response)["models"]}
for name, expected in catalog.items():
    assert name in installed, f"Falta modelo: {name}"
    assert installed[name]["digest"] == expected["digest"], f"Revisión distinta: {name}"
    print(name, "digest correcto")
PY
```

Si cambió un tag, detenerse: no modificar el catálogo ni el manifiesto para
simular igualdad. Obtener la revisión original o declarar otra condición
experimental en archivos nuevos. No están incluidos los pesos en el ZIP.

## 3. Repetir piloto y línea base local

En la raíz del paquete, crear un directorio de trabajo nuevo y mantener su ruta
para reanudar. No escribir sobre `results/`. Se ejecuta un solo modelo a la vez.

```bash
set -euo pipefail
export PYTHONPATH="$PWD/code/src"
units_runs=$(mktemp -d /tmp/units-new-run-XXXXXX)
export UNITS_RUNS="$units_runs"
printf 'Resultados nuevos: %s\n' "$units_runs"

uv run --no-sync python -m challenge.harness run --tasks results/calibration/controls.jsonl --out "$units_runs/control-qwen17" --model qwen3:1.7b --samples 1
uv run --no-sync python -m challenge.harness run --tasks results/calibration/tasks.jsonl --out "$units_runs/pilot" --model qwen3:1.7b --samples 3
uv run --no-sync python -m challenge.harness score --tasks results/calibration/tasks.jsonl --run "$units_runs/pilot" --out "$units_runs/pilot/scores/v9"

while read -r folder model; do
  uv run --no-sync python -m challenge.harness run --tasks results/calibration/controls.jsonl --out "$units_runs/control-$folder" --model "$model" --samples 1
  uv run --no-sync python -m challenge.harness run --tasks data/final-v2/private/test.jsonl --out "$units_runs/baseline/$folder" --model "$model" --samples 3
  uv run --no-sync python -m challenge.harness score --tasks data/final-v2/private/test.jsonl --run "$units_runs/baseline/$folder" --out "$units_runs/baseline/$folder/scores/v9"
done <<'MODELS'
qwen17 qwen3:1.7b
llama llama3.2:1b
smol smollm2:1.7b-instruct-q4_K_M
qwen8 qwen3:8b
MODELS

uv run --no-sync python -m challenge.harness compare --dataset data/final-v2 --runs "$units_runs/baseline" --out "$units_runs/comparison.json"
```

Esperado: 5 controles por modelo, 270 respuestas del piloto y 162 de test por
modelo local. El control de Qwen17 anterior al piloto es independiente del
control previo a su test. No usar los resultados de test para cambiar tareas,
parser, verificador o parámetros. Si se plantea un ajuste, reservar otro test
independiente y documentar versiones antes de evaluar la nueva condición.

Los parámetros están fijados en `code/src/challenge/models.py` y
`data/final-v2/protocol.json`; no hay que introducirlos manualmente.
En el equipo original la línea base local sumó unos 46,5 minutos de solicitudes.
Otros equipos pueden requerir más tiempo o no alojar íntegro el profesor en GPU.

Para reanudar una inferencia, repetir **su comando run** con la misma carpeta,
archivo de tareas, modelo, backend y configuración; no volver a ejecutar `mktemp`.
Se completan solo claves faltantes. `score`, `freeze`, `derive` y `compare`
requieren destinos nuevos; no volver a lanzarlos sobre una salida ya creada.

Para sobrevivir al cierre de terminal puede lanzarse una corrida como servicio
de usuario (sustituye al `run` directo correspondiente, no se ejecutan ambos):

```bash
mkdir -p "$units_runs/persistent-qwen17"
systemd-run --user --unit=units-qwen17-repro \
  --property="WorkingDirectory=$PWD" \
  --property="Environment=PYTHONPATH=$PWD/code/src" \
  --property="StandardOutput=append:$units_runs/persistent-qwen17/inference.log" \
  --property=StandardError=inherit \
  "$PWD/.venv/bin/python" -m challenge.harness run \
  --tasks data/final-v2/private/test.jsonl --out "$units_runs/persistent-qwen17" \
  --model qwen3:1.7b --samples 3
systemctl --user status units-qwen17-repro
```

## 4. Generar nuevas respuestas SFT/DPO

Para reconstruir exactamente los archivos originales basta con `derive` del
README y las respuestas/auditorías incluidas. Para nueva inferencia:

```bash
uv run --no-sync python -m challenge.harness run --tasks data/final-v2/private/train.jsonl --out "$units_runs/train-teacher" --model qwen3:8b --samples 4
uv run --no-sync python -m challenge.harness run --tasks data/negative-tasks.jsonl --out "$units_runs/train-negatives" --model qwen3:1.7b --samples 3
```

Son 360 respuestas del profesor y 114 sobre el subconjunto original de 38 tareas
de train para negativos. Repite ese subconjunto; no vuelve a seleccionar tareas
según las nuevas respuestas. El profesor original tomó unos 42,3 minutos.

**Las auditorías incluidas corresponden a los hashes de las respuestas originales**.
No reutilizarlas como si certificaran respuestas nuevas. Para revisar todas las
candidatas correctas nuevas, preparar un archivo de trabajo:

```bash
uv run --no-sync python - <<'PY'
import json
import os
from pathlib import Path
from challenge.derive import collect
from challenge.models import read_rows

work = Path(os.environ["UNITS_RUNS"])
records, _ = collect(read_rows(Path("data/final-v2/private/train.jsonl")),
                     read_rows(work / "train-teacher/responses.jsonl"), "train-teacher")
with (work / "audits.jsonl").open("x") as stream:
    for candidate in records:
        if candidate["status"] == "correct":
            audit = {**candidate, "completion_sha256": candidate["sources"][0]["completion_sha256"],
                     "judgment": "uncertain", "reason": "Pendiente de revisión", "reviewer": ""}
            stream.write(json.dumps(audit, ensure_ascii=False) + "\n")
PY
```

Revisar datos, conversiones, operaciones y conclusión de cada candidata. Editar
`judgment` a `keep` o `reject`, explicar `reason` y completar `reviewer` sin
alterar ID, texto o hash. Dejar `uncertain` excluye la traza; no marcar todo como
correcto por pasar el 1%. Esta receta revisa todas las candidatas, cubriendo
también la expansión obligatoria de celdas con defectos.

```bash
uv run --no-sync python -m challenge.harness derive --dataset data/final-v2 --teacher "$units_runs/train-teacher" --audits "$units_runs/audits.jsonl" --negative-tasks data/negative-tasks.jsonl --negative-run "$units_runs/train-negatives" --out "$units_runs/derived"
```

Las cantidades pueden diferir de 121/35. No rellenar cuotas, reutilizar pares
ni incorporar eval/test. Esto genera datos; no entrena modelos.

## 5. Repetir la referencia externa — genera gasto

No es necesario para validar la entrega. Requiere credencial y presupuesto
propios explícitamente autorizados. El programa limita reservas a USD5 por
ledger; no interpreta ese límite como autorización para gastar. Los precios,
disponibilidad y políticas del servicio pueden cambiar.

Crear fuera del paquete un archivo privado con una línea
`OPENROUTER_API_KEY=SU_CLAVE`, sin compartirlo. Desde la raíz y con `units_runs`
definido, reemplazar únicamente la ruta privada:

```bash
units_api_env=/ruta/privada/openrouter.env
uv run --no-sync python -m challenge.frontier run --tasks results/calibration/controls.jsonl --out "$units_runs/frontier/controls" --samples 1 --env-file "$units_api_env" --ledger "$units_runs/frontier/attempts.jsonl"
uv run --no-sync python -m challenge.frontier run --tasks data/final-v2/private/test.jsonl --out "$units_runs/frontier/test" --samples 3 --env-file "$units_api_env" --ledger "$units_runs/frontier/attempts.jsonl"
uv run --no-sync python -m challenge.frontier score --tasks data/final-v2/private/test.jsonl --run "$units_runs/frontier/test" --out "$units_runs/frontier/test/scores/v9"
```

Se fija DeepSeek-V4-Pro-0813, ruta DeepInfra, sin fallback, mismos prompts y
verificador. Conservar **un único ledger** para controles y test; no borrarlo
ni cambiarlo al reanudar. Un HTTP404 requiere revisar disponibilidad/política;
no desactivar privacidad ni cambiar silenciosamente de modelo. Los fallos
quedan registrados; no hay reintentos automáticos. La revisión original del
runner está preservada en `results/frontier-v1/test/runner.py`; el runner actual
añade la vinculación del ledger a la configuración.

Las nuevas métricas se calculan con el mismo `score`. Para crear figuras nuevas,
usar `report/render.py` con la comparación, los nuevos derivados y el score
externo nuevos, y un `--out` nuevo. El PDF entregado referencia `report/final-v2`;
mantenerlo intacto o trabajar en una copia al integrar un experimento nuevo.

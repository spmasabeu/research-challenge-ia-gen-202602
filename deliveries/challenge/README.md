# Desafío de investigación: razonamiento cuantitativo con unidades

Fernando Fajardo, Sebastian Palma, Benjamin Prieto y Rodrigo Ugarte.
IIC-3694, Pontificia Universidad Católica de Chile. 7 de noviembre de 2026.

Paquete autocontenido de los cuatro entregables. No contiene pesos, credenciales,
entornos virtuales ni entrenamiento. Informe: [report/informe.pdf](report/informe.pdf).
Código, referencias privadas y respuestas se entregan para reproducir resultados;
a cada modelo se envió exclusivamente el prompt público, un turno sin herramientas.

| Entregable | Evidencia |
| --- | --- |
| E1 Entorno y tareas | code/src/challenge, code/tests, data/final-v2 |
| E2 Descripción | report/content.tex, informe.pdf, protocolo y catálogo en data/final-v2 |
| E3 SFT/DPO | data/derived-v3; fuentes results/train-teacher-v1 y train-negatives-v1 |
| E4 Línea base y calibración | results/baseline-v1, frontier-v1, calibration; tablas/figuras en report/final-v2 |

Mapa detallado: [EVIDENCE.md](EVIDENCE.md). Integridad: manifest.json y
results/validation/. Estado del repositorio al ejecutar: HEAD previo
ba1afddf36c318a0b6f60e564c550b46e5f6c5b1, cambios sin commit; el código se
identifica por sus archivos y hashes, no por ese HEAD histórico.

## Por dónde empezar

| Objetivo | Instrucciones |
| --- | --- |
| Verificar tareas, SFT/DPO, métricas y PDF incluidos, sin GPU ni API | Sección Reproducción offline de este README |
| Volver a descargar modelos y generar respuestas | [REPRODUCING.md](REPRODUCING.md), secciones 1–3 |
| Generar nuevas respuestas de train y auditarlas | [REPRODUCING.md](REPRODUCING.md), sección 4 |
| Repetir DeepSeek en OpenRouter con presupuesto propio | [REPRODUCING.md](REPRODUCING.md), sección 5 |

Trabajar desde la carpeta `challenge/` extraída, no desde la raíz del repositorio.
Recalcular las fuentes guardadas reproduce los resultados; generar respuestas
nuevas puede cambiar métricas y cantidades aun con las mismas semillas.

## Resultados efectivos

180 tareas, 60 problemas físicos: train/eval/test 90/36/54. Cada grupo de tres
variantes queda unido. Semillas 4301/4302; 95 claves físicas de desarrollo excluidas.
Por dificultad fácil/media/difícil: train 30/30/30; eval 12/12/12; test 18/18/18.
121 SFT de 46 tareas/20 grupos y 35 DPO de 25 tareas/17 grupos.
SFT por dificultad 51/46/24; DPO 7/15/13. De 360 respuestas del profesor,
193 pasan resultado, 178 son correctas distintas y todas fueron auditadas:
121 retenidas, 57 excluidas por calidad contextual. Auditoría de agentes,
no certificación humana. Rechazadas DPO: 22 profesor, 13 objetivo; cero unparsed.

| Modelo | pass@1 | pass@3 | Cobertura |
| --- | ---: | ---: | ---: |
| Qwen3-1.7B Q4_K_M | 51,85% | 68,52% | 95,68% |
| Llama 3.2-1B Q8_0 | 2,47% | 7,41% | 44,44% |
| SmolLM2-1.7B Q4_K_M | 3,09% | 7,41% | 23,46% |
| Qwen3-8B Q4_K_M, profesor abierto | 50,62% | 72,22% | 96,30% |
| DeepSeek-V4-Pro-0813, OpenRouter/DeepInfra FP8 | 82,10% | 90,74% | 82,10% |

162 respuestas por modelo, mismo test y verificador 9; n=k=3 para pass@3.
Unparsed no demuestra error matemático. El informe y CSV incluyen cotas optimistas,
conteos, truncamientos y resultados por dificultad. Algunos aciertos finales
contienen pasos incorrectos; la tolerancia del 1% no valida explicaciones.
Tríos y plantillas compartidas limitan independencia y generalización.
Qwen3-8B es profesor abierto mayor, no modelo de frontera. No se entrenó.

Hardware: Intel Core 5 210H, 12 CPU lógicas, RAM 30,47GiB, RTX3050 Laptop6144MiB,
driver595.71.05, Ollama0.18.0. CUDA13.2 es compatibilidad anunciada por NVIDIA-SMI,
no versión del runtime comprobada. GGUF/digests/templates/licencias en metadata.
Todos los locales solicitan temperatura0,7/top_p0,9/top_k40/min_p0,
contexto2048/batch128/num_gpu99/máximo1024/think=false; semillas42–44.
Profesor train: cuatro muestras42–45. API externa: mismo muestreo y máximo1024,
reasoning.enabled=false, ruta fija DeepInfra FP8, contexto anunciado1M; cuantización
remota procede del catálogo. Defaults/motores distintos impiden atribuir solo tamaño.

Costo API reportado: USD0,0935116 (test0,0905151 + controles0,0029965), conciliado
con uso de la clave, bajo autorización USD5. Ledger168intentos/reservaUSD3,36,
incluido un rechazo404 sin generación de otra ruta. Local APIUSD0; electricidad
no medida. Sin compra adicional de créditos. Inferencias finalizadas.

## Reproducción offline

Comprobado en Linux con Python3.12.13 y uv0.11.16. Núcleo: biblioteca estándar.
El grupo opcional report fija Matplotlib3.11.2; uv.lock fija transitivas.
Desde esta carpeta, usando destinos nuevos (los comandos NO llaman modelos):

```bash
uv sync --python 3.12.13 --locked --group report
export PYTHONPATH=code/src
uv run --no-sync python -m unittest discover -s code/tests -v
uv run --no-sync python -m challenge.harness check --dataset data/final-v2
uv run --no-sync python -m challenge.harness freeze --out /tmp/units-regenerated --exclusions data/final-v2/exclusions.json --models data/final-v2/models.json
uv run --no-sync python -m challenge.harness check-derived --dataset data/final-v2 --teacher results/train-teacher-v1 --audits data/derived-v3/audits/audit-speed.jsonl data/derived-v3/audits/audit-speed-extra.jsonl data/derived-v3/audits/audit-energy.jsonl data/derived-v3/audits/audit-luminosity.jsonl --negative-tasks data/negative-tasks.jsonl --negative-run results/train-negatives-v1 --out data/derived-v3
uv run --no-sync python -m challenge.harness derive --dataset data/final-v2 --teacher results/train-teacher-v1 --audits data/derived-v3/audits/audit-speed.jsonl data/derived-v3/audits/audit-speed-extra.jsonl data/derived-v3/audits/audit-energy.jsonl data/derived-v3/audits/audit-luminosity.jsonl --negative-tasks data/negative-tasks.jsonl --negative-run results/train-negatives-v1 --out /tmp/units-derived-reproduced
uv run --no-sync python -m challenge.harness compare --dataset data/final-v2 --runs results/baseline-v1 --out /tmp/units-comparison.json
uv run --no-sync python -m challenge.frontier score --tasks data/final-v2/private/test.jsonl --run results/frontier-v1/test --out /tmp/units-frontier-score
uv run --no-sync python report/render.py --comparison /tmp/units-comparison.json --calibration results/calibration/scores/v9/summary.json --derived data/derived-v3/stats.json --frontier /tmp/units-frontier-score --out /tmp/units-report-assets
```

Comprobar las salidas reconstruidas contra las incluidas:

```bash
diff -qr data/final-v2 /tmp/units-regenerated
diff -qr data/derived-v3 /tmp/units-derived-reproduced
cmp results/baseline-v1/comparison-v9.json /tmp/units-comparison.json
cmp results/frontier-v1/test/scores/v9-adapter3/labels.jsonl /tmp/units-frontier-score/labels.jsonl
cmp results/frontier-v1/test/scores/v9-adapter3/summary.json /tmp/units-frontier-score/summary.json
cmp report/final-v2/baseline.csv /tmp/units-report-assets/baseline.csv
cmp report/final-v2/derived.csv /tmp/units-report-assets/derived.csv
cmp report/final-v2/tables.tex /tmp/units-report-assets/tables.tex
```

Sin salida y código de retorno cero significa igualdad. Diferencias de formato
PDF o metadatos entre toolchains no equivalen a diferencias numéricas.
 Para recalcular calibración sin inferencia:

```python
from pathlib import Path
from challenge.models import read_rows
from challenge.evaluate import summarize
labels, summary = summarize(read_rows(Path("results/calibration/tasks.jsonl")),
                            read_rows(Path("results/calibration/responses.jsonl")))
```

Interfaz común, sin backend:

```python
from pathlib import Path
from challenge import load_tasks, reward
from challenge.models import read_rows
train = read_rows(Path("data/final-v2/private/train.jsonl"))
load_tasks(train)
prompt = next(t["prompt"] for t in train if t["id"] == "14c34d569bd092efd278-medium")
assert reward(prompt, "57.95 m/s") == 1.0
assert reward(prompt, "0 m/s") == 0.0
```

SFT JSONL contiene task_id,prompt,completion,metadata con fuentes; DPO añade
chosen/rejected y procedencia. Cárguelos con read_rows o json.loads por línea.
Todos derivan de train. Referencias privadas solo para evaluación.

## PDF y repetición de inferencia

```bash
cd report
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=/tmp/units-pdf-reproduced main.tex
cd ..
```

TeX Live2026/pdfTeX1.40.29, latexmk4.88; paquetes lmodern,graphicx,xcolor,
amsmath,booktabs,hyperref,babel-spanish,hyphen-spanish. En instalación mínima, habilitar
patrones españoles y regenerar formato pdflatex. Template original en template/;
main.tex adapta contenido, amsmath, tamaño del escudo y metadata reproducible.

Repetir inferencia local requiere Ollama0.18.0 y las revisiones/licencias de
models.json; los tags pueden cambiar. Verifique digests antes del lote. Comando:
`python -m challenge.harness run --tasks data/final-v2/private/test.jsonl --out NUEVO_DESTINO --model TAG --samples 3`.
Guardado/fsync por respuesta, reanudación con configuración idéntica y lock local;
para procesos largos usar servicio persistente como los logs de la ejecución.

La API externa necesita OPENROUTER_API_KEY en archivo privado externo al paquete
y presupuesto nuevo explícitamente autorizado; no ejecutar para reproducir métricas.
El runner actual fija ledger_path a config; el snapshot runner.py de inferencia
anterior se conserva. Cambió solo la protección de reanudación: scores v9 y
v9-adapter3 tienen idénticas etiquetas/métricas; no hay mejora de modelo ni ajuste
post-test del verificador. El ledger debe ser único para controles/test de una
misma ejecución; no borrar ni reiniciar para eludir presupuesto.

El historial completo de trabajo se conserva en el repositorio; el paquete incluye
resultados finales y evidencia mínima de recálculos, fuentes y errores operativos.
Envío previsto por correo al profesor a cargo del equipo, sin envío automático.
Plazo informado por equipo:12/11/2026 23:59 Santiago; esa fecha cae jueves, aunque
se comunicó como viernes. Intención de entrega alrededor del martes10.

Integridad de archivos (antes de crear entornos o nuevos resultados):

```python
import hashlib, json
from pathlib import Path
root = Path('.')
manifest = json.loads((root / 'manifest.json').read_text())['files']
assert all(hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
           for name, digest in manifest.items())
```

Revisión de formato del 8 de noviembre: más espacio alrededor de reglas del encabezado y tablas; filas1,15x y booktabs. Contenido, métricas, datos y código del entorno sin cambios. Entrega reconciliada en una única versión definitiva.

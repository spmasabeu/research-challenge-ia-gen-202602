# Ejecución del desafío units

Estado y decisiones: [bitácora](../../docs/contexto/2026-11-07_200958_bitacora_ejecucion_desafio_units.md).
`preflight/` contiene controles de desarrollo, entorno real, metadata de pesos,
respuestas y mediciones. `pilot-v1/` y `runs/pilot-v1-qwen/` contienen el piloto
independiente y sus respuestas incrementales; no son train ni test finales.

Desde raíz, con Python 3.12 (`uv sync --locked`):

```bash
PYTHONPATH=src uv run python -m challenge.harness generate --seed 4300 --groups 10 --out /tmp/units-pilot/tasks.jsonl
PYTHONPATH=src uv run python -m challenge.harness run --tasks /tmp/units-pilot/tasks.jsonl --out /tmp/units-pilot/qwen --model qwen3:1.7b --samples 3
PYTHONPATH=src uv run python -m challenge.harness score --tasks /tmp/units-pilot/tasks.jsonl --run /tmp/units-pilot/qwen --out /tmp/units-pilot/qwen/scores/v1
```

`generate` y `score` requieren destinos nuevos. `run` reanuda solamente las claves
faltantes si coinciden tareas, digest, backend y configuración. Una corrida
incompleta no pasa `score`; las respuestas vacías/truncadas completadas permanecen.
El runner guarda respuesta completa de Ollama, prompt, semilla, parámetros,
duración, tokens y residencia del modelo en memoria. Un candado de usuario
impide dos runners de este harness a la vez. En trabajo se usa systemd de usuario
para sobrevivir al cierre de terminal, con logs append.

La API común se utiliza sin backend:

```python
import json
from pathlib import Path
from challenge import load_tasks, reward

tasks = [json.loads(line) for line in Path("data/units/pilot-v1/tasks.jsonl").read_text().splitlines()]
load_tasks(tasks)  # tabla privada, con referencias recalculadas desde el prompt
score = reward(tasks[0]["prompt"], "22 m/s")
```

Enviar exclusivamente `task["prompt"]` al modelo. No enviar `answer_si`, registro
privado ni archivos de respuestas. El parser nunca consulta la referencia para
extraer. Los prompts desconocidos generan ValueError. Equivalencias y tolerancia
1% en SI se aplican automáticamente. `unparsed` significa falta de resultado
admitido/inequívoco; no prueba error matemático. Métricas separan esta categoría
y publican cotas superiores que la tratan como correcta.

No hay entrenamiento. C0–C7 cerrados; entrega técnica validada. La comparación externa autorizada usa OpenRouter con tope USD 5 y costo reportado de USD 0,0935116.

## Dataset congelado

`final-v2/public/{train,eval,test}.jsonl`: 90/36/54 tareas sin referencias.
`final-v2/private/`: las mismas tareas con referencias SI; enviar solo el prompt.
Son 10/4/6 grupos físicos por familia, tres variantes juntas y dos estructuras
balanceadas. Se excluyen 95 problemas del spike, pilotos y controles. `protocol.json`,
`models.json`, `units.json` y `manifest.json` fijan configuración y huellas.

```bash
PYTHONPATH=src uv run python -m challenge.harness check --dataset data/units/final-v2
PYTHONPATH=src uv run python -m challenge.harness freeze --out /tmp/units-regenerated --exclusions data/units/final-v2/exclusions.json --models data/units/final-v2/models.json
```

Comprobado desde copia aislada: diez pruebas, referencias, disjunción, celdas y
regeneración de 15 archivos idénticos. Evidencia `validation/c4-isolated.json`.
El código actual tiene además pruebas del exportador SFT/DPO (once en total).

## Datos derivados validados

Profesor: `runs/train-teacher-v1/`, cuatro muestras por tarea exclusivamente de
train. Inferencia Ollama 0.18.0, Qwen3-8B Q4_K_M; contexto 2048, batch 128,
GPU completa solicitada, máximo 1024 tokens, temperatura 0,7, top_p 0,9,
top_k 40, min_p 0, semillas 42–45, think=false. Modelo y digest efectivos en metadata.

`derivation-v1/` conserva entradas de auditoría inmutables y juicios de agentes,
identificados como revisión contextual, no docente humano. Cinco candidatas por
familia/nivel con semilla 4303 en cada celda; un defecto obliga a revisar todas
las candidatas correctas de esa celda. Un resultado dentro del 1% puede tener
pasos incorrectos y quedar excluido de SFT sin cambiar su recompensa automática.

Resultado: 121 trazas SFT (46 tareas) y 35 pares DPO (25 tareas). Fácil/media/difícil: SFT 51/46/24; DPO 7/15/13. Las nueve celdas tienen datos, con cobertura muy baja en algunas. Auditoría contextual: 178 candidatas revisadas individualmente, 121 keep y 57 reject; no quedan candidatas correctas sin revisar.

Reproducir desde fuentes conservadas (usar un destino nuevo para derive):

```bash
PYTHONPATH=src uv run python -m challenge.harness derive --dataset data/units/final-v2 --teacher data/units/runs/train-teacher-v1 --audits data/units/derivation-v1/audit-speed.jsonl data/units/derivation-v1/audit-speed-extra.jsonl data/units/derivation-v1/audit-energy.jsonl data/units/derivation-v1/audit-luminosity.jsonl --negative-tasks data/units/derivation-v1/negative-tasks.jsonl --negative-run data/units/runs/train-negatives-v1 --out /tmp/units-derived-reproduced
PYTHONPATH=src uv run python -m challenge.harness check-derived --dataset data/units/final-v2 --teacher data/units/runs/train-teacher-v1 --audits data/units/derived-v3/audits/audit-speed.jsonl data/units/derived-v3/audits/audit-speed-extra.jsonl data/units/derived-v3/audits/audit-energy.jsonl data/units/derived-v3/audits/audit-luminosity.jsonl --negative-tasks data/units/derivation-v1/negative-tasks.jsonl --negative-run data/units/runs/train-negatives-v1 --out data/units/derived-v3
```

Si se necesitan negativos adicionales, ambos comandos admiten `--negative-tasks`
y `--negative-run`, con el subconjunto exacto de train y su corrida completa de
un pequeño, hasta tres muestras. DPO usa solo `numeric/unit`, mismo problema,
máximo dos pares por orden de muestra. No usa `unparsed` ni producto cartesiano.
SFT conserva todas las correctas distintas elegibles del profesor; deduplicación
por tarea/texto salvo espacios, con todos los orígenes. Los volúmenes efectivos
están en `derived-v3/stats.json`; las metas 4.000/2.000 no son mínimos rígidos. Se generaron 360 respuestas del profesor (193 correctas por resultado, 178 distintas, 121 retenidas tras calidad) y 114 del objetivo sobre 38 tareas para negativas (19 errores numéricos utilizables). No se usan sus 6 unparsed. El DPO crece de 22 a 35 pares por nuevas respuestas, sin cambiar el evaluador.

Reproducción C5 desde copia aislada, sin modelos: `validation/c5-isolated.json`. Costo profesor: 2.537,21 s y 56.563 tokens de salida; media 7,05 s. Alcanzar 4.000 SFT a esa tasa de retención proyectaría unas 23,30 h solo de profesor, sin garantizar igual calidad al ampliar. Costo API local cero; electricidad no medida.

Calibración y límites: [informe C3](../../docs/contexto/2026-11-07_211432_calibracion_units.md).
Frontera OpenRouter completada: DeepSeek-V4-Pro-0813, ruta DeepInfra FP8, 162 respuestas de test; resultados en `runs/frontier-v1/test/scores/v9-adapter3/`. El template LaTeX fue aportado y preservado en `docs/report/template/`; integración, figuras, PDF y autoría se siguen en `docs/report/README.md`.

La validación vigente de final-v2/derived-v3 con verifier-9 está en `validation/v9-isolated.json`: once pruebas, check-derived y quince archivos regenerados idénticos desde copia aislada. Los registros C4/C5 anteriores se conservan como historia de sus versiones.


## Línea base final y referencia externa

Cuatro locales completos en `runs/baseline-v1/`, 162 respuestas por modelo;
`comparison-v9.json` reconstruido y cotejado desde crudos. Referencia externa:
133 correct/29 unparsed, pass@1 82,10%, pass@3 90,74%, cobertura 82,10%.
No convertir las 29 no interpretadas en errores matemáticos. Control externo:
cinco respuestas por USD0,0029965; test USD0,0905151. Se conservan solicitudes,
respuestas completas, costos, parámetros, provider y ledger de 168 intentos.

```bash
PYTHONPATH=src uv run python -m challenge.harness compare --dataset data/units/final-v2 --runs data/units/runs/baseline-v1 --out /tmp/units-comparison-reproduced.json
PYTHONPATH=src uv run python -m challenge.frontier score --tasks data/units/final-v2/private/test.jsonl --run data/units/runs/frontier-v1/test --out /tmp/units-frontier-score-reproduced
```

Ambos comandos son offline y usan destinos nuevos. El adaptador 3 vincula ledger
con configuración y comprueba el snapshot real del runner; etiquetas y métricas
son idénticas a la versión 2 que realizó inferencia, conservada como `runner.py`.
No repetir inferencia pagada sin un presupuesto nuevo. La reanudación conserva
configuración y fuentes: cambiar de ledger en una corrida nueva ya iniciada
produce error. No se entregan credenciales ni pesos. Trece pruebas actuales;
las evidencias anteriores de once pruebas conservan la versión histórica.

Snapshot final: `deliveries/challenge/`, 211 archivos sin pesos/secretos/entornos; ZIP `deliveries/challenge-2026-11-07.zip`. Validación final en `validation/c7-delivery-isolated.json`: entorno nuevo, trece pruebas, regeneración 15 archivos de tareas y 8 derivados, métricas/etiquetas/figuras/tablas y PDF idénticos byte a byte.

Formato definitivo actualizado y reconciliado en los nombres originales; validación vigente de maquetación y ZIP en `validation/report-format.json`. La evidencia C7 previa documenta contenido y resultados, que permanecen idénticos.

# E2: respaldo técnico, auditoría humana e informe pendientes

Rama `feat/project-e2`, base `061ca08`. I9 (informe) queda fuera de esta ejecución.
No confundir los pilotos `smoke-*` con corridas comparables del proyecto.
Los respaldos previos están en `validation/plan-original.md` y
`validation/original-local.patch`. No se modifican datasets ni scores históricos.

## Actualización de auditoría al 23 de noviembre

Muestras de los PR #7/#8/#9 integradas: 274 dictámenes humanos conservados y
13 correcciones de agente pendientes de confirmación por personas (5 Fernando,
8 Rodrigo). Los 104 registros de Benjamín no se modifican. El detalle y conteos
provisionales están en [audits/README.md](audits/README.md). El estado de cero
dictámenes del cierre técnico del 18 de noviembre que sigue es histórico.
La auditoría humana no está cerrada; informe/PDF/envío siguen pendientes.
No se cambiaron entrenamientos, recompensas, resultados automáticos ni test.

## Estado técnico al 18 de noviembre

I2–I7 ejecutadas; I5 tiene excepciones de cobertura e I7 límites de comparación
por perfil energético e interrupción, documentados. I8: análisis y muestra listos,
auditoría humana pendiente. I9 no iniciado. **E2 no está completa.**

Resultados sobre360tareas de validación ×3muestras,120problemas físicos:

| Ruta | Pasos | Entrenamiento acumulado | Tokens train acumulados | pass@1 | pass@3 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Control | 0 | 0s | 0 | 69,44% | 84,17% |
| SFT | 377 | 1.201,81s | 506.829 | 76,57% | 86,11% |
| GRPO | 40 | 1.297,77s | 58.408 | 69,35% | 84,17% |
| SFT→GRPO | 90SFT+31RL | 1.236,85s | 169.155 | 73,89% | 86,94% |

Las tres rutas entrenadas modificaron112tensores finitos y guardaron/recargaron
exactamente. Híbrido incluye288,879s y121.125tokens del checkpoint90 SFT;
no contabilizar solo su RL. Los tiempos superan el nominal1.200s por cerrar el
último paso. Hay trabajo interrumpido adicional, no medido exactamente, separado
en el ledger; no se cuenta la reunión. Test permanece reservado.

SFT mejora pass@1 en7,13pp frente al control (IC95pareado[4,17;10,09]pp).
Híbrido supera GRPO en4,54pp (IC95[1,11;7,87]pp), pero SFT solo tiene el mayor
pass@1 observado. Los contrastes pass@3 incluyen cero. No se demuestra aporte
incremental del RL respecto del SFT inicial con evaluación completa. Una semilla,
cobertura desigual y perfil energético inicial desconocido limitan generalización
y eficiencia causal. SFT degrada energía/luminosidad mientras mejora otras familias;
la pérdida train y la recompensa RL se mantienen separadas de la validación.

Respaldos principales:

- [Comparación final](analysis/comparison-final-v1/): CSV, cinco figuras, bootstrap,
  curvas por tiempo/tokens y fuentes/hashes. Curvas frecuentes36tareas×1; cierres360×3.
- [Hallazgos y límites](analysis/final-findings-v1.json),
  [costos medidos](analysis/production-cost-ledger-v1.json) y
  [decisión de cobertura](analysis/production-data-decision-v1.json).
- [Validación final](validation/final-checks.json),
  [integridad y test reservado](validation/final-integrity.json),
  [13artefactos idénticos al regenerar](validation/comparison-final-reproduction.json).
- [Matriz R1–R11/V1–V12](validation/traceability.json) distingue aprobado,
  excepción, auditoría humana e informe pendientes.
- [Auditoría humana](audits/README.md):208éxitos de las rutas y53trazas SFT,
  más calibración, seleccionados y sin dictámenes. Las revisiones de agentes
  permanecen separadas; incluyen falsos pasos aritméticos con recompensa1.

Comprobaciones:42pruebas CPU, Ruff0.17.4 y Mypy2.4.1 (23archivos) aprobados;
Bandit1.9.4 sin hallazgos medios/altos (41bajos). Pilotos GPUv3 probaron
actualización, recarga y reanudación bit a bit; la producción confirma las tres
rutas. Todos los pesos/checkpoints se conservan localmente y están excluidos de
Git; no publicar el código solo como si incluyera esos pesos.

Para verificar o regenerar sin entrenar de nuevo (destino de reporte nuevo):

```bash
rtk proxy env PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
rtk proxy env PYTHONPATH=src .venv/bin/python scripts/run_e2.py \
  --stage all --derived data/units/project-e2/derived
rtk proxy env PYTHONPATH=src .venv/bin/python scripts/report_training.py \
  --runs data/units/project-e2/runs --out /tmp/e2-comparison-new
```

Con todas las corridas completas, `run_e2.py` verifica/reutiliza respuestas,
proveniencia y checkpoints; no repite GPU. Conservar originales de auditoría y
completar copias según `audits/README.md`. El siguiente trabajo requiere personas
para esa revisión e I9 para redactar/compilar el informe. DPO se exportó como
769pares; su entrenamiento y sensibilidad50% pertenecen a E3.

Las secciones posteriores conservan decisiones y estados históricos de ejecución;
el estado vigente de auditoría figura en la actualización del 23 de noviembre
y en `validation/work-state.json`.

## Entorno

RTX 3050 Laptop 6 GiB local. A30 no accesible por nombre desde este equipo:
`validation/a30-access.log`. No se usan servicios pagados.
Instalación: `rtk proxy uv sync --locked --group training`.
Las pruebas CPU pueden ejecutarse sin ese grupo:
`rtk proxy uv run python -m unittest discover -s tests -v`.

Checkpoint: Qwen/Qwen3-1.7B, revisión inmutable en `config/model.json`.
QLoRA NF4, cómputo BF16, LoRA r=8 sobre q_proj/v_proj; evaluación comparte carga.
Dependencias directas exactas y transitivas fijadas en `pyproject.toml`/`uv.lock`.
Fuentes consultadas: [TRL SFT 0.24.0](https://huggingface.co/docs/trl/v0.24.0/en/sft_trainer),
[TRL GRPO 0.24.0](https://huggingface.co/docs/trl/v0.24.0/en/grpo_trainer) y
[Qwen3-1.7B](https://huggingface.co/Qwen/Qwen3-1.7B).
Se inspeccionó también el código instalado de preparación PEFT y máscaras SFT.

## Contrato verifier-11

- Extracción independiente de la referencia; `reward(prompt, completion)` exige
  registro privado mediante `load_tasks`. Prompt desconocido provoca error.
- Unidad pedida obligatoria; alias del catálogo admitidos. Una unidad equivalente
  diferente recibe `unit`, recompensa 0 y `equivalent_si=true` cuando corresponde.
- Tolerancia relativa inclusiva del 1% respecto de la referencia; factores y
  fórmulas se recalculan desde los datos visibles con implementación independiente.
- Punto decimal, sin separadores de miles. Coma decimal aceptada salvo formas
  ambiguas como `1,234` o `41,879`. `0,123` sí se interpreta como decimal.
- JSON terminal con exactamente `value` y `unit`, o cantidad/unidad terminal;
  no se evalúan expresiones. Alias, notación científica y envolturas LaTeX limitadas
  conservan el contrato anterior. No se incorporó el parser completo del PR #2.
- Declaraciones explícitas de resultados, incluidas cantidades aisladas anteriores
  al JSON, deben concordar en SI (tolerancia de consistencia 1e-10).
  No se toma la respuesta numéricamente más próxima a la referencia.
- No finitos, claves duplicadas, alternativas y contradicciones: `unparsed`.
  Más de 4.000 caracteres: `too_long`, recompensa 0. El límite protege el proceso
  antes del parsing; el prompt ya pide hasta 80 palabras.
- `unparsed`/`too_long` no se transforman en errores matemáticos ni negativos DPO.
  Tasas de equivalencia SI y unidad pedida usan todas las respuestas como denominador.
- Snapshots anteriores siguen usando su propio código. La recalificación nueva es
  diagnóstico separado en `analysis/pilot-regrade-v11/`.

## Iteraciones

| Caso | Evidencia | Decisión / impacto |
| --- | --- | --- |
| Placeholder de unidad copiado literalmente | `runs/calibration-nf4-v1/`: 10 de 36 respuestas usan `unidad`; 11 unparsed, sin truncamientos | `generate(..., project=True)` muestra la unidad pedida y explicita punto decimal. Las tareas históricas se regeneran sin cambios. Repetir calibración antes de freeze. No atribuir la diferencia a aprendizaje. |
| Generación GRPO fuera de autocast | `validation/smoke-grpo-v1.log`: Float/BFloat16 incompatibles | Aplicar autocast CUDA BF16 solo a la generación GRPO; conservar intento y repetir. |
| GRPO sin señal con tres grupos históricos | `runs/smoke-grpo-v2/`: recompensas 0/0/0, gradientes cero, ningún tensor modificado | Intento fallido explícito. Repetir con prompt corregido y hasta 12 grupos/budget 300 s; no usar el descenso de pérdida como criterio. |
| Reanudación no bit a bit con kernels no deterministas | `validation/gpu-check-v1-driver.log`; RNG CPU/CUDA iguales pero delta máximo de adaptador 5,47e-4 | Activar algoritmos deterministas y CUBLAS antes de cargar el modelo. `gpu-check-v2-sft` y `gpu-check-v2-resume` dan adaptadores idénticos. No se reemplazan resultados del intento anterior. |

Calibración del prompt, mismos 36 problemas de desarrollo, una muestra por tarea:
38,89% → 72,22% pass@1; cobertura 69,44% → 100%; ningún truncamiento.
`calibration-nf4-v1` y `calibration-explicit-v1` conservan los crudos. No se entrenó
entre ambos. El cambio mide sensibilidad al formato del prompt.
Persisten errores aritméticos y factores 1.000 en luminosidad/tensión difíciles.
No se cambian rangos físicos basándose en solo dos tareas por celda: se mantienen
los casos difíciles para medir la señal en GRPO y ampliar el diagnóstico con eval.
La muestra humana inicial está en `audits/pending/calibration-human-pending.jsonl`;
auditor, tipo, dictamen y motivo siguen sin completar. No constituye revisión humana.

## Particiones y presupuesto

`dataset/`: 1.800 train, 360 eval, 360 test; 840 problemas físicos, seis familias,
tres variantes por problema, balance directa/suma. Semillas 7301/7302.
Se excluyen 215 claves físicas históricas, con fuentes y hashes en `exclusions.json`.
`config/subsets.json` identifica las muestras estratificadas de curvas y piloto del
modelo generador; ambas conservan tríos físicos. La muestra del modelo generador pertenece a train.
La del modelo generador no sustituye silenciosamente las 1.800 tareas previstas.

`config/budget.json` fija inicialmente B=1.200 s por ruta en esta GPU, aproximadamente
30 pasos GRPO según el piloto. SFT→GRPO toma el checkpoint SFT más próximo al corte
del 25% y resta su costo real del presupuesto RL. `scripts/run_e2.py` evalúa paso cero,
tres checkpoints distintos y cierre; control/cierres usan eval completo × 3 muestras.
Las curvas frecuentes usan una muestra fija de 36 tareas × 1 muestra. El costo de
SFT se incluye en las coordenadas de la rama combinada. Cómputo compartido, pruebas
de infraestructura y evaluación se registran aparte. El límite se comprueba al
terminar un paso: no ocultar el posible sobrepaso de un paso.

Los presupuestos son configuración de ejecución; disponer de estos archivos no
acredita corridas completadas. Test permanece reservado y el runner E2 lo rechaza.

## Artefactos y continuidad

Cada corrida guarda configuración, hashes del código y los datos, versiones,
hardware, crudos/logs y tiempos. `checkpoint-*` guarda optimizador, scheduler y RNG;
`cost.json` registra hashes y cómputo acumulado. Pesos y checkpoints se conservan
localmente, excluidos de Git. No moverlos sin copiar también los manifiestos.

`--initial-adapter` en GRPO carga el adaptador SFT como entrenable y exige
datos/checkpoint/precisión compatibles. Cuenta su costo previo; reinicia optimizador.
Se fija beta=0 para ambas ramas: sin KL ni modelo de referencia.
Grupos constantes siguen produciendo ventaja nula: no se inventan recompensas.
Un intento sin cambio de parámetros falla explícitamente y conserva los crudos.

La máscara SFT solo habilita la conclusión/traza del asistente y EOS; nunca el
prompt. Una traza demasiado larga se rechaza, sin truncar silenciosamente su final.
GRPO conserva grupos completos, registra su variación y enmascara completions
truncadas. Evaluación reporta truncamiento por separado.

Comandos disponibles (usar destinos nuevos; los artefactos se crean sin sobrescribir):

```bash
rtk proxy env PYTHONPATH=src uv run --locked --group training python -m challenge.evaluate_hf \
  --tasks data/units/project-e2/config/development-explicit.jsonl \
  --config data/units/project-e2/config/pilot-eval.json \
  --out data/units/project-e2/runs/calibration-explicit-v1

rtk proxy env PYTHONPATH=src uv run --locked --group training python -m challenge.train \
  --config data/units/project-e2/config/smoke-sft.json \
  --tasks data/units/project-e2/config/smoke-explicit-tasks.jsonl \
  --sft data/units/project-e2/config/smoke-explicit-sft.jsonl \
  --out data/units/project-e2/runs/smoke-sft-new --pilot

rtk proxy env PYTHONPATH=src uv run --locked --group training python -m challenge.train \
  --config data/units/project-e2/config/smoke-grpo-signal.json \
  --tasks data/units/project-e2/config/smoke-explicit-tasks.jsonl \
  --out data/units/project-e2/runs/smoke-grpo-new --pilot
```

El sufijo `--pilot` habilita tareas históricas de desarrollo solo para verificar
infraestructura. Las corridas reportables exigen `private/train.jsonl` de un dataset
que pase `check_dataset`. Test queda reservado. Las semillas 42–44 de inferencia
no son réplicas de entrenamiento.

### Secuencia y límites de inferencia

Se adelanta I6 mientras se mide I5: el control usa únicamente eval, el dataset y
el verificador ya están congelados y no depende de trazas del modelo generador. Esto
permite comprobar la evaluación completa sin consumir test ni cambiar el corpus.
La producción del modelo generador y el entrenamiento se serializan con la evaluación
porque comparten la RTX 3050; no se presupone acceso a la A30.

El reporte remuestrea problemas físicos completos dentro de familia/estructura
(2.000 réplicas, semilla 7305). Mantiene juntas variantes y respuestas, y usa los
mismos bloques para diferencias pareadas contra control. Solo admite cierres
completos con el mismo protocolo. Los intervalos no representan variación entre
semillas de entrenamiento ni certifican la corrección del razonamiento.

### Comandos de producción

Ejecutar desde la raíz, una tarea GPU a la vez. `run` y `evaluate_hf` reanudan
sus destinos verificando hashes; `derive` y `report_training` requieren destinos
nuevos. No ejecutar dos procesos sobre el mismo directorio.

```bash
rtk proxy uv sync --locked --group training --group report
rtk proxy env PYTHONPATH=src .venv/bin/python -m challenge.harness check \
  --dataset data/units/project-e2/dataset
rtk proxy env PYTHONPATH=src .venv/bin/python scripts/run_e2.py --stage control

# Completar piloto de costo por celda (36 tareas de train × 6 respuestas).
rtk proxy env PYTHONPATH=src .venv/bin/python -m challenge.harness run \
  --tasks data/units/project-e2/config/teacher-pilot.jsonl \
  --model qwen3:8b --samples 6 --max-tokens 1024 \
  --out data/units/project-e2/runs/teacher-pilot

# Producción elegida tras piloto (1.800 tareas × 4 respuestas).
rtk proxy env PYTHONPATH=src .venv/bin/python -m challenge.harness run \
  --tasks data/units/project-e2/config/teacher-production-tasks.jsonl \
  --model qwen3:8b --samples 4 --max-tokens 1024 \
  --out data/units/project-e2/runs/teacher

rtk proxy env PYTHONPATH=src .venv/bin/python scripts/prepare_e2.py audit \
  --tasks data/units/project-e2/dataset/private/train.jsonl \
  --run data/units/project-e2/runs/teacher --teacher \
  --out data/units/project-e2/audits/teacher-pending.jsonl
```

Completar dictámenes tras inspeccionar las trazas; no rellenarlos automáticamente
como `keep`. Una celda con rechazo o incertidumbre exige revisar todas sus
candidatas correctas. Registrar `reviewer_type=agent` para inspección de agentes;
la auditoría humana posterior sigue separada. `derive --help` documenta entradas
de auditoría y negativos adicionales cuando las respuestas del modelo generador no basten.

```bash
# Independiente de los derivados SFT.
rtk proxy env PYTHONPATH=src .venv/bin/python scripts/run_e2.py --stage grpo
# Después de producir y revalidar derived/ con challenge.harness derive.
rtk proxy env PYTHONPATH=src .venv/bin/python scripts/run_e2.py \
  --stage all --derived data/units/project-e2/derived
# Solo artefactos guardados; salida nueva en cada versión.
rtk proxy env PYTHONPATH=src .venv/bin/python scripts/report_training.py \
  --runs data/units/project-e2/runs --out data/units/project-e2/analysis/comparison-v1
```

### Control nuevo completado (I6)

`runs/control/`: 360 tareas × 3 muestras; **pass@1 69,44%, pass@3 84,17%**.
750 correctas, 314 errores numéricos, 16 no interpretables; cobertura 98,52%,
cero truncamientos. Inferencia medida: 3.007,13 s, 167.797 tokens de salida.
IC 95% por problemas físicos: pass@1 [66,39%; 72,41%], pass@3 [81,11%; 86,94%].
`analysis/control-v1/` contiene tablas, figura, IC y hashes; recálculo exacto desde
crudos en `validation/control-reproduction.log`.

`analysis/control-findings.json` registra suelo en luminosidad difícil (1/60) y
techo en velocidad fácil (60/60) y media (59/60). Se mantiene el dataset congelado
para comparar rutas; evaluar variación de recompensa por grupo y estrato. Una
recalibración posterior requeriría nueva versión y repetición de comparación.

Cuatro casos dirigidos inspeccionados por agente en
`analysis/control-inspection-agent.json`: omisión/inversión de conversión de flujo,
un éxito final con justificación dimensional inválida y un JSON correcto rechazado
por declaración previa fuera de la gramática admitida. No equivalen a estimación
de calidad humana ni demuestran reward hacking. El verificador comprueba la
conclusión y contradicciones explícitas, no todos los pasos del razonamiento.
`audits/pending/control-human-pending.jsonl` contiene 52 éxitos seleccionados con semilla
7304; hasta tres por celda, solo uno disponible en luminosidad difícil. Todos los
dictámenes humanos permanecen vacíos.

### Contabilidad de tokens

La inspección de TRL 0.24 encontró que `SFTTrainer._total_train_tokens` se reinicia
al reanudar, mientras GRPO acumula en `TrainerState.num_input_tokens_seen`.
El runner ahora habilita el contador persistente de Transformers para SFT y guarda
tokens de fase, prefijo y total en `cost.json`/`result.json`. Cuenta prompt y
completion procesados; no equivale a FLOPs ni permite equiparar GPU diferentes.
La comparación grafica tiempo y tokens acumulados, incluyendo el prefijo SFT.
Para la corrida GRPO iniciada con la versión anterior se lee el estado original
del checkpoint, con hash registrado; no se alteran sus artefactos. Los pilotos SFT
anteriores sin contador persistente se mantienen con tokens desconocidos.
La nueva comprobación GPU de este contador queda registrada por separado de las
pruebas previas de actualización/recarga; ver `validation/work-state.json`.

El reloj de entrenamiento abarca `trainer.train`, incluidas escrituras de
checkpoints; excluye descarga, carga del modelo y preparación/tokenización previa.
El reloj de evaluación mide generación sincronizada CUDA, sin carga inicial.
Los tiempos del modelo generador provienen de su API local y se conservan separados.
Son tiempos medidos con alcance explícito, no FLOPs ni medición de energía.

### GRPO reportable: entrenamiento y evaluación completados

`runs/grpo/`: 40 pasos reales, 112 tensores modificados, delta máximo 0,000252916;
pesos finitos y recarga idéntica de logits. 58.408 tokens de prompt/completion;
20 grupos mixtos, 15 con todo 1, cinco con todo 0. Respuestas truncadas: 1/160, con
límite de 512 tokens y máscara en la pérdida. El último paso demoró unos
102 s y dejó duración total de **1.297,77 s**, sobrepaso de 97,77 s (8,15%) sobre
B=1.200. Comparar costos reales, sin afirmar idéntica duración entre rutas.
`analysis/grpo-training.json` conserva el resumen con hashes. La comparación completa está en `analysis/control-grpo-v1/`.

`analysis/grpo-curves-v1/` contiene recompensa train y pass@1 en validación frente
a tiempo y tokens: 61,11% (control), 58,33% (paso 13), 63,89% (25), 55,56% (33)
y 61,11% (40). No hay tendencia clara ni mejora del cierre en estas 36 tareas.
La comprobación `validation/grpo-curves-reproduction.json` regeneró doce artefactos
idénticos byte a byte, incluidas figuras. El cierre completo de 360 tareas figura a continuación.
La muestra para auditoría usa éxitos únicos tras deduplicar diferencias de espacios;
sus registros conservan todos los orígenes. No es una revisión humana realizada.

Revalidación adicional de `derived-v3`: 121/121 trazas SFT y 35/35 pares DPO
mantienen validez con verifier-11 (`analysis/historical-derived-v11/`). Se verificó
el hash de su train original. No se alteraron ni se incorporaron al corpus E2.

### Comparación control–GRPO

Ambas rutas completaron 360 tareas de eval × 3 respuestas. GRPO: pass@1
**69,35%**, pass@3 **84,17%**, frente a 69,44%/84,17% del control. Diferencia
pass@1 −0,0926 puntos; IC95 pareado por 120 problemas físicos [−1,7593;+1,5764]
puntos (2.000 réplicas). No hay mejora agregada demostrada; tampoco prueba de
equivalencia ni conclusión sobre otras semillas o presupuestos.

749 correctas,313 errores numéricos,18 no interpretables, un truncamiento.
Cobertura98,33% (control98,52%). `analysis/grpo-comparison-findings.json` conserva
transiciones y diferencias por las18 celdas; `analysis/control-grpo-v1/` contiene
las figuras y datos de comparación. Recalificación exacta de crudos comprobada en
`validation/grpo-final-reproduction.log`.

Seis casos dirigidos en `analysis/grpo-inspection-agent.json`: errores aritméticos,
JSON escapado, un bucle truncado y dos éxitos de luminosidad difícil con pasos
inválidos. La tolerancia del1% sobre conclusión no certifica el razonamiento.
No se modifica la política congelada ni se afirma reward hacking.
`audits/pending/grpo-human-pending.jsonl`:53 éxitos únicos seleccionados con semilla7304,
sin dictámenes humanos. Inspección de agente separada de esa muestra.

La evaluación sufrió SIGTERM después de928 respuestas; origen no determinado.
Se reanudó con idéntico modelo/configuración y conservando filas previas; llegó a
1.080 y pasó recalificación exacta. `validation/execution-interruption.json` y
`validation/resume-queue.py` documentan recuperación y cola serial.

### Piloto del modelo generador y decisión de producción

`runs/teacher-pilot/`:216 respuestas,1.413,14s medidos.196 textos únicos,130
candidatas con recompensa1;99 inspecciones de agente y19 rechazos dejan111 SFT
y16 pares DPO,30/12 tareas respectivamente. Siete celdas revisadas por completo
tras defectos. `analysis/teacher-pilot-derived/` pasa `check-derived`; es piloto
de producción, no el corpus ampliado ni evidencia de entrenamiento reportable.
Luminosidad queda sin positivos utilizables en las tres dificultades.

`analysis/teacher-pilot-cost-retention.json` compara las primeras4 y las6 muestras
reales. Se eligen **4 por cada una de las1.800 tareas**, conservando cobertura de
muestreo completa: proyección3.700 SFT y13,22h frente a5.550 y19,63h con6. Son
proyecciones de solo2 tareas/celda; no garantizan retención ni calidad. DPO del
modelo generador proyecta550 pares y necesita negativos reales adicionales.
`config/teacher-production-decision.json` conserva motivo, evidencia e impacto.
No se reescribe el protocolo congelado:6 era la propuesta inicial; la ejecución
llevará4 explícito en metadata. Las tareas de producción se ordenan por celda
para permitir auditoría incremental, con diccionarios idénticos al train original.
La política de calidad rechaza operaciones incorrectas aun dentro del1% final;
no cambia la recompensa. Las revisiones de agente no cuentan como humanas.

### Validación GPU v3 aprobada

`validation/gpu-check-v3-gpu.json`: SFT3 pasos y su reanudación producen pesos
idénticos bit a bit y3.531 tokens acumulados. GRPO6 pasos y reanudación desde el
checkpoint2 producen pesos idénticos y9.734 tokens. Cada ruta modifica112 tensores
y pasa recarga con pesos/logits finitos e idénticos. Híbrido10 pasos:304,473s RL
más11,382s SFT;18.651 tokens totales, incluidos3.531 previos. Sin OOM.
Estos resultados son pilotos de infraestructura y permanecen separados de las
corridas reportables. La contabilidad persistente está validada en GPU real.

Producción activa en `runs/teacher/`, con4 respuestas por cada una de las1.800
tareas de `config/teacher-production-tasks.jsonl`. Cola y log preservados en
`validation/teacher-production-queue.py` y `teacher-production-driver.log`;
PID de lanzamiento en `teacher-production-pid.json`. Reanudar con el comando
`challenge.harness run` documentado arriba, cuando no haya otro proceso activo
sobre ese destino. No lanzar una segunda tarea GPU concurrente.

La producción se interrumpió tras112 respuestas por `RemoteDisconnected` del
servidor local. Después de comprobar versión/digest y dataset, se reanudó en el
mismo destino; el prefijo previo mantiene su hash. Evidencia en
`validation/teacher-production-resume-1.json` y su log. El costo de la petición
interrumpida no quedó medido; se separará del tiempo de respuestas completadas.

Una segunda desconexión dejó1.144 respuestas. Se verificaron nuevamente versión,
digest y dataset antes de reanudar; `validation/teacher-production-resume-2.json`
conserva hash/longitud del prefijo, comando, PID y log nuevo. Tampoco se conoce el
costo de esa petición interrumpida. Ambos fallos permanecen en sus logs originales.

Las celdas terminadas se respaldan en `analysis/teacher-production-cells/` y
`audits/teacher-production/`. Densidad fácil:400 respuestas,374 candidatas SFT
únicas de100 tareas tras revisión;10 inspecciones de agente incluyen las5
obligatorias y6 dirigidas con1 solapamiento. Ningún error numérico/de unidad
del modelo generador para DPO; negativos adicionales pendientes. Una celda cerrada no
acredita I5 completo ni revisión humana.

Densidad media:400 respuestas,367 candidatas SFT únicas de100 tareas y1 par DPO
del modelo generador;5 inspecciones aleatorias de agente, sin rechazos. Las dos
celdas comparten los mismos100 problemas físicos con distinta representación:
las200 tareas no son200 problemas independientes.

Densidad difícil:400 respuestas (354 correctas,45 numéricas,1 no interpretable),
335 candidatas SFT únicas de100 tareas y37 pares DPO. Las5 revisiones aleatorias
de agente verificaron conversiones y operaciones; señalaron separadores de miles
en pasos intermedios como incumplimiento de formato, sin error físico. Una salida
repetitiva truncada se excluye de negativos DPO. Total densidad:1.076 candidatas
SFT y38 pares;300 tareas sobre100 problemas físicos. Esto no anticipa la retención
de las otras familias ni certifica individualmente las trazas no inspeccionadas.

Energía fácil:400 respuestas,306 con recompensa1 y305 positivas únicas. Cuatro
de las5 inspecciones aleatorias encontraron productos incorrectos dentro del1%.
Se revisaron las305 positivas:229 rechazos y76 trazas retenidas de33/100 tareas,
con10 pares DPO del modelo generador. Las100 referencias se recalcularon desde
los datos visibles con aritmética decimal independiente y coincidieron. Los
rechazos de calidad con recompensa1 se excluyen también de negativos DPO.
La retención19% sobre respuestas crudas y la cobertura33% son resultados reales,
no una falla de duplicación ni motivo para relajar la política. El cierre de I5
deberá justificar ese déficit y los de las celdas restantes antes del entrenamiento.
Evidencia: `analysis/teacher-production-cells/energy-easy.json` y auditoría asociada;
la revisión completa fue de agente, no humana.

Energía media:400 respuestas,253 con recompensa1 y252 positivas únicas. La muestra
detectó4/5 trazas defectuosas; la revisión completa dejó50 SFT de25/100 tareas y17
pares DPO, tras202 rechazos aritméticos. Retención12,5% sobre respuestas crudas.
Las100 referencias, incluida conversión g→kg, coinciden con recálculo decimal.
`analysis/teacher-production-cells/energy-medium.json` conserva conteos y hashes;
los252 dictámenes son de agente. No se cambió la tolerancia del verificador.

Terminología alineada con la entrega anterior: Qwen3-8B es el modelo generador;
el verificador programático calcula la recompensa. Los identificadores internos
`teacher` conservan la procedencia de archivos y corridas; no designan un modelo
evaluador. Las fuentes y snapshots históricos mantienen su contenido original.

Energía difícil:400 respuestas,153 con recompensa1 y152 positivas únicas.
La muestra detectó4/5 defectos; se inspeccionaron las152 y quedaron28 SFT de
12/100 tareas,7 pares DPO y124 rechazos. Retención7% sobre respuestas crudas;
81,58% de rechazo entre positivas únicas. Las100 referencias se comprobaron
con aritmética decimal independiente, incluidas g→kg y km/h→m/s. Los dictámenes
son de agente. Evidencia: `analysis/teacher-production-cells/energy-hard.json`.
La cobertura de12 tareas queda bajo el objetivo interno20; deberá registrarse
como excepción al cerrar el corpus, sin sustituir soluciones ni duplicarlas.

Las seis primeras celdas completas suman1.230 candidatas SFT y72 pares DPO.
Densidad aporta1.076 trazas; energía154. Este desequilibrio de retención es un
confusor para interpretar diferencias de aprendizaje por familia: los prompts
GRPO conservan la mezcla equilibrada de train, mientras SFT depende de soluciones
utilizables del modelo generador. No afirmar que las rutas reciben igual número
de ejemplos por celda; conservar la mezcla efectiva en el manifiesto final.

Luminosidad fácil:400 respuestas,177 positivas únicas,217 errores numéricos
y6 no interpretables. Tras defectos en inspección dirigida, se revisaron las177
positivas (incluidas las5 aleatorias obligatorias:2 conservadas/3 rechazadas).
Quedaron58 SFT de28/100 tareas y20 pares DPO;119 rechazos de calidad. Retención
14,5% sobre respuestas crudas. Se recalcularon las100 referencias con Decimal
y el pi visible; todas coincidieron. Se aceptan redondeos/truncamientos coherentes
y precisión de máquina; se rechazan operaciones incorrectas a la precisión escrita,
incluidos errores muy pequeños. Esa política cualitativa es más estricta que la
recompensa final y no modifica sus etiquetas. Evidencia y hashes en
`analysis/teacher-production-cells/luminosity-easy.json`. Revisión de agente.

Las instrucciones para las muestras humanas están en `audits/README.md`.
Control y GRPO tienen52 y53 trazas pendientes; los campos de dictamen siguen
vacíos. Preparar las muestras e instrucciones no acredita R10/V11.

Luminosidad media:400 respuestas,83 con recompensa1 y82 positivas únicas.
Se revisaron todas:36 SFT de19/100 tareas,16 pares DPO y46 rechazos de calidad.
Las5 trazas de la muestra obligatoria resultaron rechazadas. Cobertura19 tareas,
una bajo la meta interna20; registrar excepción e impacto antes de entrenar.
Las100 referencias coinciden con recálculo Decimal, incluida conversión km→m.
Evidencia: `analysis/teacher-production-cells/luminosity-medium.json`.

Esta celda incluye3 respuestas Ollama con `done:false`, entre5 no interpretables.
Se conservaron completas tal como llegaron, sin sustituirlas ni reintentar sus
claves. El evaluador existente las fuerza a `unparsed`, recompensa0; no son
negativos matemáticos confirmados. Sus tokens son desconocidos:65.758 es solo
el subtotal informado por las otras397 respuestas. Los3 tiempos de petición
sí están medidos. No confundir ausencia de `done_reason:length` con finalización.
Diagnóstico con hash del prefijo en `analysis/teacher-production-cells/`
(`backend-incomplete-first-diagnostic.json`); regresión existente aprobada en
`validation/backend-incomplete-regression.log`. No cambió código congelado.

Luminosidad difícil:400 respuestas,382 errores numéricos,8 no interpretables y
10 positivas únicas. Se revisaron las10:2 SFT de2 tareas,2 pares DPO y8 rechazos.
La muestra obligatoria de5 incluye1 conservada/4 rechazadas. Las100 referencias
coinciden con recálculo decimal independiente de distancia, flujo y pi.
Costo medido:3.865,554 s de peticiones y84.257 tokens generados. No hubo respuestas
incompletas del backend ni terminación por límite en esta celda. La retención0,5%
y cobertura2% incumplen ampliamente los objetivos internos20/10 tareas; ese
déficit debe justificar la decisión de ampliación/excepción antes de entrenar.
No extrapolar automáticamente esta retención a muestras adicionales.

Tres errores numéricos dirigidos muestran inversión de la conversión de flujo
(multiplica1000 en vez de dividir1000) y productos incorrectos adicionales. Una
respuesta con recompensa1 presenta conversión inversa, factor1e-7 improcedente
y otro error aritmético, terminando cerca de la referencia; fue rechazada. Estos
casos acreditan falsos éxitos respecto del razonamiento, no intención de engaño
ni prevalencia estimada. Fuentes: `analysis/teacher-production-cells/` y los
10 dictámenes de agente en `audits/teacher-production/luminosity-hard.jsonl`.

Al cerrar las primeras9/18 celdas hay1.326 candidatas SFT y110 pares DPO del
modelo generador. Son conteos parciales; aún faltan presión, velocidad, tensión,
negativos complementarios y construcción/revalidación del corpus completo.

Presión fácil:400 respuestas con recompensa1,271 únicas de100 tareas. Las5
inspecciones aleatorias de agente verificaron sumas/divisiones y redondeos;
ningún defecto detectado, sin expansión. Las271 son elegibles según la política
de muestreo, no certificadas individualmente. Las100 referencias coinciden con
recálculo Decimal. Sin negativos del generador:0 pares DPO hasta complementar
con el modelo pequeño. Evidencia: `analysis/teacher-production-cells/pressure-easy.json`.

Presión media:400 respuestas,395 correctas y5 errores numéricos;367 positivas
únicas de100 tareas y3 pares DPO. Las5 revisiones aleatorias de agente comprobaron
kN→N, sumas, división y redondeo, sin defectos. Una traza aproxima a decenas de Pa,
con precisión reducida pero coherente. Las100 referencias coinciden con recálculo
Decimal. Las no inspeccionadas son elegibles bajo muestreo, no certificadas.
Evidencia: `analysis/teacher-production-cells/pressure-medium.json`.

Presión difícil:400 respuestas,330 correctas según verificador y70 errores
numéricos. Un defecto entre5 muestras obligó a inspeccionar las296 positivas
únicas:272 retenidas de92 tareas,24 rechazadas por divisiones incorrectas aunque
pasaban la tolerancia del1%. Se aceptaron redondeos/truncamientos coherentes,
incluidos resultados de menor precisión. Las100 referencias coinciden con
recálculo Decimal.32 pares DPO del generador;2.891,864s de solicitudes y62.501
tokens de salida. Auditoría de agente completa para esta celda, sin revisión
humana. Evidencia: `analysis/teacher-production-cells/pressure-hard.json`.

Acumulado de12/18 celdas cerradas:2.236 candidatas SFT y145 pares DPO del
generador. Todavía falta generar/revisar velocidad y tensión eléctrica, obtener
negativos complementarios y construir/revalidar el corpus completo.

Decisión previa a SFT sobre cobertura escasa: se mantiene el corte congelado
de1.800 tareas y4 muestras por tarea, ampliado desde2 a100 tareas por celda
respecto del piloto. Energía difícil, luminosidad media y difícil conservan
respectivamente12,19 y2 tareas SFT. Se documenta la excepción a la meta interna
de20 tareas, sin flexibilizar calidad ni duplicar trazas. Ampliar problemas
físicos ahora cambiaría la distribución train de la corrida GRPO reportable
ya ejecutada. Las proyecciones lineales de retención y costo, sus límites y
el efecto potencial sobre la comparación están en
`analysis/teacher-production-cells/low-coverage-decision-v1.json`. Los conteos
DPO finales y sus excepciones se cerrarán tras los negativos complementarios.

Velocidad fácil: 400 respuestas, 340 correctas según verificador, 52 errores
numéricos y 8 no interpretadas. Un defecto en la muestra aleatoria motivó
revisar las 294 positivas únicas: 263 retenidas de 88 tareas y 31 rechazadas.
Se distinguen aproximaciones coherentes de cocientes incorrectos; también se
registran rechazos conservadores por precisión decimal afirmada incorrecta,
aunque la diferencia sea diminuta. Las 100 referencias coinciden con recálculo
Decimal. Resultado parcial: 13 pares DPO, 1.861,664 s y 39.793 tokens de salida.
Fuente: `analysis/teacher-production-cells/speed-easy.json`. Las 13 celdas
cerradas suman 2.499 trazas SFT elegibles y 158 pares DPO del generador.

Velocidad media: 400 respuestas, 351 correctas según verificador y 49 errores
numéricos. Un defecto en la muestra aleatoria motivó revisar las 321 positivas
únicas: 276 retenidas de 84 tareas, 45 rechazadas por cocientes incorrectos.
Las 100 referencias coinciden con recálculo Decimal desde km y segundos.
Resultado parcial: 12 pares DPO, 2.185,406 s y 46.952 tokens de salida.
Fuente: `analysis/teacher-production-cells/speed-medium.json`. Las 14 celdas
cerradas suman 2.775 trazas SFT elegibles y 170 pares DPO del generador.

Velocidad difícil: 400 respuestas, 220 correctas según verificador y 180
errores numéricos. Dos defectos en la muestra aleatoria motivaron revisar las
202 positivas únicas: 163 retenidas de 67 tareas, 39 rechazadas. Se aceptan
redondeos coherentes y se excluyen operaciones falsas incluso dentro del 1%.
Las 100 referencias coinciden con recálculo Decimal. Resultado parcial:
47 pares DPO, 2.742,413 s y 59.251 tokens de salida. Fuente:
`analysis/teacher-production-cells/speed-hard.json`. Las 15 celdas cerradas
suman 2.938 trazas SFT elegibles y 217 pares DPO del generador. Falta tensión
eléctrica; estos conteos todavía no corresponden al corpus final.

Corrección de metadatos de auditoría: 83 motivos de rechazo en velocidad
mostraban la etiqueta kPa heredada de presión; ahora dicen m/s (fácil/media)
o km/h (difícil). No cambian respuestas, referencias, dictámenes ni conteos.
Versiones previas, hashes y comprobación de campos idénticos conservados en
`validation/audit-unit-label-correction-v1/`.

Tensión eléctrica fácil: 400 respuestas, 301 correctas según verificador,
76 errores numéricos y 23 no interpretadas. Cinco defectos en una muestra
dirigida temprana motivaron revisar las 301 positivas únicas, incluyendo
la muestra aleatoria de cinco al cierre: 144 retenidas de 54 tareas y
157 rechazadas. Tres rechazos corresponden a supuestos injustificados de
resistencias iguales; los demás, a productos incorrectos. Referencias de
las 100 tareas confirmadas con Decimal. Resultado parcial: 39 pares DPO,
2.555,570 s y 55.134 tokens. Fuente:
`analysis/teacher-production-cells/voltage-easy.json`. Las 16 celdas cerradas
suman 3.082 trazas SFT elegibles y 256 pares DPO del generador.

Tensión eléctrica media: 400 respuestas, 311 correctas según verificador,
83 errores numéricos y 6 no interpretadas. Un defecto dirigido temprano
motivó revisar las 311 positivas únicas, incluyendo la muestra aleatoria
al cierre: 141 retenidas de 63 tareas y 170 rechazadas. Se documentan
supuestos injustificados, productos incorrectos y dos rechazos conservadores
por precisión de redondeo. Referencias de100 tareas confirmadas con Decimal.
Resultado parcial: 40 pares DPO, 2.703,141 s y58.430 tokens. Fuente:
`analysis/teacher-production-cells/voltage-medium.json`. Las17 celdas cerradas
suman3.223 trazas SFT elegibles y296 pares DPO del generador.

Tensión eléctrica difícil cerrada: 400 respuestas, 301 correctas según
verificador y 99 errores numéricos. Se inspeccionaron las 299 positivas únicas:
139 retenidas de 56 tareas y 160 rechazadas; 34 pares DPO del generador.
Las 100 referencias fueron recalculadas con Decimal. Evidencia:
`analysis/teacher-production-cells/voltage-hard.json`.

Producción completa del 18-11: 7.200 respuestas de 1.800 tareas train,
cuatro muestras por tarea. El verificador clasifica 5.083 correctas, 2.020 errores
numéricos y 97 no interpretadas; hay un truncamiento y tres respuestas
`done:false`, conservadas y excluidas. Estas métricas de train del generador
no se comparan directamente con la validación del modelo entrenable.

`analysis/teacher-production-derived/` contiene 3.362 trazas SFT de 1.123 tareas
y 443 problemas físicos, y 330 pares DPO provisionales de 267 tareas.
`check-derived` reproduce los archivos. De 6.788 respuestas únicas, 4.716 pasan
el verificador; las 3.032 revisiones de agente descartan 1.354. Entre las trazas
retenidas, 1.678 se revisaron individualmente y 1.684 pertenecen a celdas sin
defectos en la muestra; estas últimas no están certificadas individualmente.
No hay auditoría humana completada.

La desviación respecto de 4.000 trazas y las excepciones de cobertura se
registran antes del entrenamiento en `analysis/production-sft-decision-v1.json`.
No se duplican trazas ni se relajan criterios. El corpus concentra 1.076 trazas
de densidad, 910 de presión y 702 de velocidad, frente a 154 de energía,
96 de luminosidad y 424 de tensión; directa/suma queda en 1.682/1.680.
Las 3.362 trazas pasan validación de pertenencia, recompensa y tokenización:
246–487 tokens, ninguna truncada, máscara de respuesta y EOS conservados.
Evidencia: `validation/sft-production-tokenization.json`.

Solicitudes guardadas del generador: 49.384,645 s (13,718 h), 1.063.102 tokens
de salida conocidos; tres filas no tienen contador. Los costos de solicitudes
interrumpidas por tres desconexiones son desconocidos, no cero. Los prefijos
de 112, 1.144 y 7.083 respuestas se conservaron byte a byte al reanudar.
`analysis/teacher-production-cost.json` registra alcance y hashes; el tiempo
no equivale a horas exclusivas de GPU ni al costo total del proyecto.

Negativos complementarios en curso: `config/negative-selection.json` y
`config/negative-tasks.jsonl` seleccionan 948 tareas de train con preferida
válida y menos de dos pares disponibles, respetando el número de preferidas.
`runs/negatives/` genera 2.844 respuestas con el checkpoint HF inicial, tres
por tarea, protocolo congelado. Solo errores numéricos/de unidad pueden
integrar DPO; las respuestas correctas adicionales no amplían SFT.
La previsión de 7.918,772 s usa el costo medido del control y no es un resultado.
Falta cerrar estos negativos y sus excepciones antes de las corridas SFT/híbrida.

El usuario cambió el perfil energético de ahorro a performance durante los
negativos. Se conserva la observación previa y el número de filas/lotes al
observar el cambio en `validation/negative-user-performance-switch.json` y
`validation/negative-power-profile-observation.json`. Un lote puede cruzar el
instante del cambio; no se normalizan ni reemplazan sus tiempos. El perfil de
las corridas anteriores no fue capturado, lo que limita la comparación temporal;
también se comparan tokens y pasos efectivos. Las métricas de los negativos
corresponden a tareas seleccionadas por disponibilidad de preferidas y no son
una evaluación representativa del modelo pequeño.

El análisis incorpora el contraste directo SFT→GRPO menos GRPO, además de cada
ruta frente al control, reutilizando los mismos bloques físicos remuestreados.
No habrá resultado de ese contraste hasta completar ambas rutas. La regresión
y las 41 pruebas CPU pasan en `validation/tests-after-contrast.log`; controles
estáticos del cambio en `validation/static-after-contrast.json`.
La muestra `audits/pending/sft-data-human-pending.jsonl` conserva 53 trazas SFT para
revisión humana; sus dictámenes permanecen vacíos.

Cierre I5 del 18-11, antes de entrenar: `derived/` contiene **3.362 trazas SFT
y 769 pares DPO**, de 1.123/526 tareas y 443/351 problemas físicos. Hay como
máximo dos pares por tarea y ninguna preferida/rechazada reutilizada. Las
18 celdas contienen ambos formatos. Las excepciones mínimas son SFT energía
difícil (12 tareas), luminosidad media (19) y difícil (2), y DPO luminosidad
difícil (2). Las metas orientativas 4.000/2.000 no se alcanzan: el filtrado de
calidad reduce las preferidas y el modelo pequeño responde correctamente en
gran parte de los prompts seleccionados. No se inflan cantidades.
Decisión, evidencia e impacto: `analysis/production-data-decision-v1.json`;
tabla por celda: `analysis/production-data-coverage.csv`.

Los 2.844 complementarios incluyen 2.253 correctos, 557 errores numéricos y
34 no interpretados, sin truncamientos. Aportaron 439 pares nuevos después de
deduplicar y limitar el emparejamiento. Generación medida: 6.632,143 s,
566.718 tokens de entrada y 374.670 de salida;
`analysis/negative-production-cost.json` delimita el costo. Recálculo offline
exacto en `validation/negative-score-reproduction.log`; comprobación integral
de derivados en `validation/derived-production-check.log`. SFT conserva
exactamente el hash del archivo validado sin truncamiento.

Corridas reportables SFT/híbrida iniciadas con perfil performance:
`validation/production-routes-launch.json` conserva PID, comando, hashes y
decisión previa. `scripts/run_e2.py` verifica/reutiliza control y GRPO existentes,
y ejecuta SFT, sus curvas/evaluación, y SFT→GRPO con su costo SFT descontado.
El test permanece reservado. Para continuar la misma secuencia:

```bash
rtk proxy env PYTHONPATH=src .venv/bin/python scripts/run_e2.py \
  --stage all --derived data/units/project-e2/derived
```

No iniciar un segundo proceso mientras el driver registrado siga activo.

SFT reportable terminó 377 pasos en 1.201,811 s, 506.829 tokens: los 112
tensores del adaptador cambiaron, con pesos finitos y recarga exacta.
`runs/sft/result.json` conserva la evidencia; su evaluación sigue en curso.
La reutilización de corridas terminadas verifica ahora los hashes de train, SFT
y adaptador inicial, además de configuración y estado no piloto. El script
exacto del driver activo se preserva en
`validation/production-routes-driver-source.py`; no se cambió el entrenador
ni el evaluador. Regresión y 42 pruebas CPU aprobadas, Ruff/Mypy aprobados,
Bandit sin hallazgos medios/altos: `validation/static-after-reuse.json`.

SFT reportable evaluado: **76,57% pass@1 / 86,11% pass@3**, 827 correctas,
245 numéricas y8 no interpretables; sin truncamiento. Diferencia frente al control
+7,13pp en pass@1, IC95 pareado[+4,17,+10,09]pp; el intervalo pass@3 incluye cero.
La mejora agregada convive con degradación en energía y luminosidad; ver
`analysis/sft-findings-v1.json` y `analysis/control-sft-grpo-v1/`.
No interpretar la distribución desigual de trazas como prueba causal de esos cambios.
`analysis/sft-curve-directed-review.json` conserva seis inspecciones de agente,
con un falso paso aritmético aceptado por tolerancia; no son auditoría humana.
`audits/pending/sft-human-pending.jsonl`:51 éxitos pendientes; luminosidad difícil no aporta
ninguno porque obtuvo0/60. Recálculo exacto: `validation/sft-final-reproduction.log`.

El reporte añade longitud media en tokens/caracteres y segundos de generación
por celda, reconciliados contra los crudos de control, GRPO y curva SFT.
`validation/static-after-lengths.json` registra esa integración real,42 pruebas
CPU y controles estáticos aprobados. El tiempo por celda amortiza cada lote entre
sus respuestas; no es latencia individual. `lengths-preliminary-v1/` es un corte
incompleto explícito, conservado junto con las versiones anteriores.

Pausa solicitada por el usuario para una reunión: procesos GPU detenidos,
checkpoint7 híbrido con pesos/optimizador/RNG verificados. Estado y respaldos:
`validation/user-pause-20261118.json` y `validation/user-pause-20261118/`.
No reiniciar automáticamente: al continuar, conciliar los logs del intento
interrumpido con checkpoint7 y conservar los descartados; reanudar desde disco
para excluir el tiempo de reunión del presupuesto. SFT completo se conserva.

Reanudación autorizada por el usuario: `validation/production-routes-resume.json`.
Los siete grupos y siete pasos coinciden byte a byte con el respaldo; no se
recortó ningún log. Checkpoint7, código, versiones y perfil performance comprobados.
Se retoman212,631s de RL más288,879s del prefijo SFT; la reunión queda fuera.
La generación interrumpida no persistió tokens ni respuestas: costo exacto
desconocido, con cota temporal externa de31,276s desde el último checkpoint
hasta la suspensión, incluidos posibles gastos de escritura/monitoreo. Este
trabajo se informa aparte del costo de la trayectoria guardada.

Entrenamiento híbrido completado:31 pasos RL,947,970s RL más288,879s SFT,
**1.236,849s acumulados y169.155 tokens** (48.030RL+121.125SFT). Sobrepaso
36,849s al cerrar el último paso; el intento interrumpido se informa aparte.
Los112 tensores cambian frente al SFT inicial; delta máximo0,000184886 en
`analysis/hybrid-weight-update-v1.json`. `result.json` compara contra checkpoint7
al reanudar; no confundir ese delta con el de toda la ruta. Su pico de memoria
corresponde al segmento reanudado. Pesos finitos y recarga exacta.

`analysis/hybrid-signal-v1.json` recalcula exactamente124 recompensas:12grupos
mixtos,16todo1 y3todo0;19/31pasos con gradiente cero. Media0,709677, con una
completion truncada/enmascarada en el último paso. Se visitan31problemas físicos
y16/18celdas; velocidad media/difícil no aparecen en esos31prompts RL. Los prompts
coinciden con el prefijo de31pasos del GRPO puro. Eso permite un diagnóstico
pareado descriptivo, pero la recompensa de train no acredita mejora en eval.

Cierre técnico: `comparison-final-v1/` incluye las cuatro rutas sin faltantes;
13archivos regenerados byte a byte. Los cinco PNG fueron inspeccionados.
La verificación final del orquestador reutilizó todas las respuestas completas,
con hashes de datos/adaptadores/configuración compatibles. Se comprobaron1.635
archivos de checkpoints y15.156respuestas guardadas, sin IDs/prompts de test.

Iteraciones adicionales conservadas: contador persistente de tokens SFT probado
con GPUv3; contraste híbrido-GRPO con bootstrap pareado y regresión; reutilización
de entrenamientos con validación de hashes y regresión; longitud/costos por celda
reconciliados con crudos. Revisiones de datos rechazaron1.354trazas entre3.032
inspecciones reales de agente, sin relajar el verificador ni declararlas humanas.
Pausa/reanudación solicitada por el usuario preservó siete pasos/grupos y retomó
el checkpoint exacto. Los fallos numéricos del modelo y la tolerancia del1% se
analizan como límites de la recompensa final; no se cambió la política tras observar
resultados para hacerlos favorables.

# Spike: scheduling

Horarios enteros con recursos alternativos, precedencias y plazos. Se aceptan todas las soluciones factibles; intervalos semiabiertos. [Informe](report.md).

## Reproducción
Desde la raíz, con Python 3.12 (aquí `.venv/bin/python`):

```sh
.venv/bin/python -m unittest discover -s spikes/scheduling -v
.venv/bin/python spikes/scheduling/evaluate.py run --pilot --model qwen3:1.7b --output spikes/scheduling/pilot-nuevo/qwen3-1.7b
.venv/bin/python spikes/scheduling/evaluate.py run --model qwen3:1.7b --output spikes/scheduling/results-nuevos/qwen3-1.7b
.venv/bin/python spikes/scheduling/evaluate.py run --model llama3.2:1b --output spikes/scheduling/results-nuevos/llama3.2-1b
.venv/bin/python spikes/scheduling/evaluate.py check spikes/scheduling/results
```

Ollama localhost:11434, modelos instalados. Carpetas nuevas por corrida; se rechaza sobrescribir. Lock compartido entre spikes para serializar inferencia. Piloto separado: tres tareas, semilla 99, una muestra a temperatura 0.7. Evaluación: 90 tareas, semilla 43, 30 por nivel, tres muestras, semillas 42/43/44, temperatura 0.7, think=false, contexto 4096, 1024 tokens. Sin JSON forzado ni referencias en prompt. Cada respuesta conserva prompt, llamada cruda, semilla, tiempo, tokens y truncamiento. Metadatos: pesos, cuantización, versiones, entorno, commit y hashes. Check recalcula etiquetas, métricas e integridad sin inferencia.

## Alcance
Tres niveles: 3/5/7 tareas, 2/2/3 recursos, menos holgura y más precedencias. Generación desde un horario válido; IDs aleatorios y presentación barajada. No garantiza monotonía de dificultad ni independencia causal de factores. No exige optimalidad. Reward binaria; errores de formato separados de restricciones. El parser acepta array JSON o candidatos en cercos Markdown que coincidan entre sí; admite prosa y tablas de entrada; rechaza salidas estructuradas adicionales y candidatos contradictorios. Nunca selecciona un candidato por coincidir con la referencia. Piloto inicial y snapshots históricos en pilot/; piloto vigente en pilot-v2/. No inferir fallo de planificación solo de formato.

No hay particiones finales, SFT/DPO, entrenamiento ni baseline de frontera. No cambia el tema acordado.

## Reanudación tras interrupción

Una desconexión dejó 180 respuestas de Qwen guardadas. `resume.py` valida el prefijo con el evaluador congelado, conserva un snapshot en interrupted/ y registra hashes, fecha, pesos y backend antes de anexar muestras faltantes. El código de generación/evaluación no cambia. Comando: `rtk proxy .venv/bin/python spikes/scheduling/resume.py spikes/scheduling/results/qwen3-1.7b`. Rechaza pesos/backend distintos y corridas ya completas. Ver manifest.json del snapshot y resumptions de metadata.json. La interrupción implica dos sesiones de hardware; costo de pared es descriptivo.

El costo agregado excluye la llamada abortada sin respuesta y la pausa entre sesiones; duración/tokens de esa llamada son desconocidos, documentados como null en interruption.json del snapshot.

## Revisión automática del parser

La versión vigente (V3) empareja cercos de cualquier idioma antes de seleccionar JSON. Se corrigió la confusión entre un cierre JavaScript y una apertura JSON. V2 rechazaba tablas de entrada con predecesoras vacías; V3 distingue esas tablas de otra respuesta estructurada. Las inferencias NO se repitieron: solo se recalcularon etiquetas con el mismo parser para ambos modelos. Esto es calibración exploratoria del verificador después de observar formatos, no un test independiente.

V1 y V2 preservan código, informe, metadatos y archivos originales en history/parser-v1/ y history/parser-v2/. metadata.json vigente separa inference_code, code, inference_resumptions y reevaluation (fuente y hashes). Las llamadas crudas y todos los campos excepto status permanecen iguales entre versiones. staged/scheduling.py conserva la propuesta aplicada; rescore.py rehúsa reaplicarla sin cambios.

Comprobaciones históricas, sin modelos:

```sh
rtk proxy .venv/bin/python spikes/scheduling/history/parser-v1/evaluate.py check spikes/scheduling/history/parser-v1/results
rtk proxy .venv/bin/python spikes/scheduling/history/parser-v2/evaluate.py check spikes/scheduling/history/parser-v2/results
```

El segundo piloto (pilot-v2/) conserva su evaluación original, anterior a las revisiones del benchmark. Validarlo con el evaluador V1 archivado: `rtk proxy .venv/bin/python spikes/scheduling/history/parser-v1/evaluate.py check spikes/scheduling/pilot-v2`. El primer piloto usa su propio snapshot en pilot/. Los nombres de pilotos y de revisiones del parser son historias distintas.

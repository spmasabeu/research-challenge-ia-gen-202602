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
Tres niveles: 3/5/7 tareas, 2/2/3 recursos, menos holgura y más precedencias. Generación desde un horario válido; IDs aleatorios y presentación barajada. No garantiza monotonía de dificultad ni independencia causal de factores. No exige optimalidad. Reward binaria; errores de formato separados de restricciones. El parser acepta array JSON o candidatos en cercos Markdown que coincidan entre sí; rechaza texto después del último cerco y candidatos contradictorios. Puede dejar sin interpretar un horario escrito con explicaciones posteriores. Piloto inicial y snapshots históricos en pilot/; piloto vigente en pilot-v2/. No inferir fallo de planificación solo de formato.

No hay particiones finales, SFT/DPO, entrenamiento ni baseline de frontera. No cambia el tema acordado.

## Reanudación tras interrupción

Una desconexión dejó 180 respuestas de Qwen guardadas. `resume.py` valida el prefijo con el evaluador congelado, conserva un snapshot en interrupted/ y registra hashes, fecha, pesos y backend antes de anexar muestras faltantes. El código de generación/evaluación no cambia. Comando: `rtk proxy .venv/bin/python spikes/scheduling/resume.py spikes/scheduling/results/qwen3-1.7b`. Rechaza pesos/backend distintos y corridas ya completas. Ver manifest.json del snapshot y resumptions de metadata.json. La interrupción implica dos sesiones de hardware; costo de pared es descriptivo.

El costo agregado excluye la llamada abortada sin respuesta y la pausa entre sesiones; duración/tokens de esa llamada son desconocidos, documentados como null en interruption.json del snapshot.

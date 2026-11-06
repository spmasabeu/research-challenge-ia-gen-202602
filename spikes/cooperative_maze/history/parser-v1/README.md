# Spike: Laberinto cooperativo

Cuadrícula pequeña con coordenadas [fila,columna] base cero y acciones U/D/L/R de un agente por paso. Colisiones prohibidas. Llave compartida y persistente: al recoger k, todas las puertas D se vuelven transitables para cualquier agente, sin consumo. Todos deben alcanzar sus metas. Fácil: navegación con paredes; medio: un agente, llave y puerta; difícil: dos agentes a lados opuestos de una barrera, A debe recoger la llave para que B cruce. [Informe](report.md).

BFS explora estado completo (posiciones, inventario); máximo 100000 estados. Descarta imposibles, exceso de estados y soluciones fuera de 2–26 acciones; no etiqueta timeout como imposible. Comprueba cooperación bloqueando A y buscando SOLO la meta de B: imposible sin participación de A. No basta con que dos agentes tengan metas distintas. Se registran descartes y estados. Pocas estructuras de mapas, sin afirmar originalidad suficiente todavía.

El presupuesto explícito es longitud BFS+6, máximo 36 acciones. No se exige optimalidad: desvíos válidos se aceptan. JSON de acciones, sin omitir movimientos inválidos. Verificación distingue unparsed, malformed, unknown_agent, bounds, wall, locked, collision, budget e incomplete; registra índice base cero de primera acción inválida y longitud descriptiva. BFS no es la única prueba del simulador: fixtures manuales comprueban estados e inventario compartido, movimientos alternativos, colisiones e imposibilidad.

El límite de generación mantiene soluciones de referencia compactas para 1024 tokens; se medirá truncamiento real del modelo y longitud de salida en piloto. Una respuesta truncada no demuestra incapacidad de planificación. Solo se puntúan acciones, nunca su explicación.

## Protocolo y artefactos

Piloto separado: tres tareas (una por nivel), semilla 99, una muestra por modelo a temperatura 0.7. Benchmark: 90 tareas compartidas, semilla 43, 30 por nivel; tres muestras con semillas 42/43/44, temperatura 0.7, think=false, contexto 4096 y máximo 1024 tokens por llamada. Un modelo local a la vez, sin JSON forzado. Solo prompts visibles al modelo; referencias y datos ocultos permanecen en tasks.jsonl.

Cada carpeta de modelo conserva metadata.json, responses.jsonl y summary.json; la raíz tiene tasks.jsonl, environment.json y comparison.json. Se registran prompts, respuestas crudas, semillas, pesos/digest/cuantización, versiones, tokens, tiempo y truncamiento. Se rechazan carpetas existentes. Check regenera tareas, comprueba hashes y completitud, reproduce clasificación y métricas; no usa modelos ni escribe archivos. Metadatos identifican código y commit, aunque los archivos nuevos todavía no están comprometidos.

pass@k = promedio por tarea de 1-C(n-c,k)/C(n,k); pass@3 indica al menos un acierto en tres intentos. Cobertura significa salida seleccionada por el parser; no certifica razonamiento. Estados unparsed no equivalen a errores lógicos. No hay revisión manual incorporada en reward ni en métricas. Diversidad de completions mide textos distintos, no diversidad semántica.

## Reproducción
Desde raíz del repositorio; Python 3.12, biblioteca estándar, Ollama localhost:11434 y modelos instalados. Aquí se usa .venv/bin/python. Usar carpetas NUEVAS para repetir:

```sh
.venv/bin/python -m unittest discover -s spikes/cooperative_maze -v
.venv/bin/python spikes/cooperative_maze/evaluate.py run --pilot --model qwen3:1.7b --output spikes/cooperative_maze/pilot-nuevo/qwen3-1.7b
.venv/bin/python spikes/cooperative_maze/evaluate.py run --pilot --model llama3.2:1b --output spikes/cooperative_maze/pilot-nuevo/llama3.2-1b
.venv/bin/python spikes/cooperative_maze/evaluate.py run --model qwen3:1.7b --output spikes/cooperative_maze/results-nuevos/qwen3-1.7b
.venv/bin/python spikes/cooperative_maze/evaluate.py run --model llama3.2:1b --output spikes/cooperative_maze/results-nuevos/llama3.2-1b
.venv/bin/python spikes/cooperative_maze/evaluate.py check spikes/cooperative_maze/results
```

No se generan datos SFT/DPO ni se entrena. Faltan particiones independientes, diversidad adicional, baseline de frontera y validación del futuro dataset según el PDF. Este spike no cambia el tema acordado. Inferencia exploratoria no equivale a entrega completa.

Para semilla 43: longitudes BFS fácil 2–7, medio 5–14, cooperación 10–25; seis candidatos fáciles imposibles y dos demasiado cortos descartados, sin excesos de estados. Son propiedades generadas, no resultados de modelos.

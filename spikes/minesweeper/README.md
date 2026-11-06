# Spike: Buscaminas deductivo

Clasifica objetivo segura, mina o indeterminada según TODAS las configuraciones compatibles, sin usar mina real generadora. Total de minas desconocido, explícito en prompt. Pistas visibles seguras, vecindad de ocho casillas, coordenadas base cero. [Informe](report.md).

Solver exacto con backtracking y poda por mínimos/máximos de cada restricción: hasta 16 ocultas y 100000 estados. Un timeout descarta instancia; nunca se etiqueta indeterminada. Se enumeran configuraciones compatibles y se comprueba al menos una. Nivel fácil: 3×3 con tres pistas; medio: 3×4 con cuatro; difícil: 4×4 con cinco. Para niveles medio/difícil, objetivos forzados no se deducen directamente de una sola pista cero o saturada: requieren combinar restricciones. No se afirma que esto mida dificultad cognitiva exacta. Generación balanceada: diez tareas por clase en cada nivel; registra descartes y estados.

Solver contrastado con enumeración independiente en 100 tableros diminutos. Parser acepta una clase aislada (también safe/mine/undetermined) con punto/énfasis o prefijo Respuesta/Clasificación, o JSON classification con coordenadas correctas si se incluyen, opcionalmente en cerco. Rechaza claves duplicadas, coordenadas ambiguas y clases contradictorias; explicaciones no se puntúan. Errores de formato separados de lógica. Se publican matriz de confusión, métricas por clase/nivel y baseline mayoritaria de 1/3. Con tres clases, acertar al azar es posible: pass@3 alto por sí solo no certifica razonamiento.

## Protocolo y artefactos

Piloto separado: tres tareas (una por nivel), semilla 99, una muestra por modelo a temperatura 0.7. Benchmark: 90 tareas compartidas, semilla 43, 30 por nivel; tres muestras con semillas 42/43/44, temperatura 0.7, think=false, contexto 4096 y máximo 1024 tokens por llamada. Un modelo local a la vez, sin JSON forzado. Solo prompts visibles al modelo; referencias y datos ocultos permanecen en tasks.jsonl.

Cada carpeta de modelo conserva metadata.json, responses.jsonl y summary.json; la raíz tiene tasks.jsonl, environment.json y comparison.json. Se registran prompts, respuestas crudas, semillas, pesos/digest/cuantización, versiones, tokens, tiempo y truncamiento. Se rechazan carpetas existentes. Check regenera tareas, comprueba hashes y completitud, reproduce clasificación y métricas; no usa modelos ni escribe archivos. Metadatos identifican código y commit, aunque los archivos nuevos todavía no están comprometidos.

pass@k = promedio por tarea de 1-C(n-c,k)/C(n,k); pass@3 indica al menos un acierto en tres intentos. Cobertura significa salida seleccionada por el parser; no certifica razonamiento. Estados unparsed no equivalen a errores lógicos. No hay revisión manual incorporada en reward ni en métricas. Diversidad de completions mide textos distintos, no diversidad semántica.

## Reproducción
Desde raíz del repositorio; Python 3.12, biblioteca estándar, Ollama localhost:11434 y modelos instalados. Aquí se usa .venv/bin/python. Usar carpetas NUEVAS para repetir:

```sh
.venv/bin/python -m unittest discover -s spikes/minesweeper -v
.venv/bin/python spikes/minesweeper/evaluate.py run --pilot --model qwen3:1.7b --output spikes/minesweeper/pilot-nuevo/qwen3-1.7b
.venv/bin/python spikes/minesweeper/evaluate.py run --pilot --model llama3.2:1b --output spikes/minesweeper/pilot-nuevo/llama3.2-1b
.venv/bin/python spikes/minesweeper/evaluate.py run --model qwen3:1.7b --output spikes/minesweeper/results-nuevos/qwen3-1.7b
.venv/bin/python spikes/minesweeper/evaluate.py run --model llama3.2:1b --output spikes/minesweeper/results-nuevos/llama3.2-1b
.venv/bin/python spikes/minesweeper/evaluate.py check spikes/minesweeper/results
```

No se generan datos SFT/DPO ni se entrena. Faltan particiones independientes, diversidad adicional, baseline de frontera y validación del futuro dataset según el PDF. Este spike no cambia el tema acordado. Inferencia exploratoria no equivale a entrega completa.

Para semilla 43: estados explorados por referencia fácil 13–33, medio 17–63, difícil 29–173. Descartes por deducción directa: 36 en medio y 24 en difícil; cero excesos de presupuesto. Estos son costos del solver, no inferencias ni dificultad humana medida.

## Revisión del parser y cobertura

La evaluación vigente distingue matrices de pistas y objetos de entrada de la clasificación final. También admite una etiqueta única dentro de un cerco o como string JSON. La inferencia no se repitió; se recalcularon etiquetas automáticamente para ambos modelos. V1 conserva código, informe y resultados en history/parser-v1/. Metadatos vigentes separan inference_code, code y reevaluation con hashes de la fuente. Esta revisión usa formatos observados y no constituye un test independiente del verificador.

La cobertura exige una clasificación interpretable para el objetivo indicado. Incluye validar coordenadas, no solo sintaxis JSON. Un diagnóstico adicional de los casos unparsed detectó 153/178 de Qwen y 74/268 de Llama que serían interpretables si se cambiara el objetivo a las coordenadas que declararon: son respuestas sobre otra casilla, rechazadas deliberadamente. No se cambió su recompensa ni se tomó su clase como respuesta al objetivo real.

Los pilotos conservan su evaluación original V1: comprobarlos con `rtk proxy .venv/bin/python spikes/minesweeper/history/parser-v1/evaluate.py check spikes/minesweeper/pilot`. Los resultados históricos del benchmark usan el mismo evaluador: `rtk proxy .venv/bin/python spikes/minesweeper/history/parser-v1/evaluate.py check spikes/minesweeper/history/parser-v1/results`. La cola identifica evaluadores históricos por sus hashes sin alterar metadatos.

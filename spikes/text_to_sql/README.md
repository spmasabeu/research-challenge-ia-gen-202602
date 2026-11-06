# Spike: Text-to-SQL con bases ocultas

Pregunta en español, esquema SQLite y datos visibles; sin interacción con herramientas. Fácil: filtros inclusivos de importes/fechas. Medio: joins que conservan duplicados y SUM/HAVING. Difícil: subconsultas correlacionadas, COUNT incluyendo importes NULL, clientes sin pedidos y empates. Tres bases ocultas por tarea comparten esquema y cambian datos con fronteras deliberadas; una deja a todos los clientes de la región consultada sin pedidos (máximo cero con empates), otra fuerza empates con pedidos. [Informe](report.md).

La consulta debe acertar en las cuatro bases; pruebas finitas, no equivalencia universal. Comparación multiconjunto: orden irrelevante, duplicados conservados, columnas en orden, NULL/texto/bytes distintos; INTEGER y REAL finitos se comparan por igualdad numérica exacta (sin tolerancia). No se pide ordenar ni redondear.

Sandbox: SQLite en memoria con query_only, authorizer de lectura y funciones permitidas; sin extensiones, ATTACH, PRAGMA ni acceso al esquema interno. execute rechaza varias sentencias. Límites: 12000 caracteres SQL, 100000 bytes por valor, profundidad 50, 100000 instrucciones y 150 ms medidos cada 100 instrucciones; 200 filas. Se niegan funciones externas y generadoras de blobs. El timeout de conexión SQLite no limita duración de consulta: se usa progress_handler. [Referencia oficial](https://docs.python.org/3.12/library/sqlite3.html). El conjunto de funciones es cerrado y determinista: funciones de fecha/reloj quedan fuera para evitar consultas dependientes del momento de check; comparar fechas ISO con operadores. Una consulta equivalente que use funciones no permitidas se informa como ejecución no soportada. No se pretende aislar vulnerabilidades nativas de SQLite.

El parser selecciona SQL completo o un cerco inequívoco; múltiples cercos distintos o SQL adicional se rechazan. Cobertura requiere una salida que comience con palabra SQL reconocida; no valida sintaxis ni autoriza operaciones. La seguridad depende del authorizer, nunca de ese prefijo. Estados: unparsed, syntax, execution (incluye autorización), timeout, limit y semantic. Se contabilizan consultas que pasan visible y fallan ocultas. Fixtures Python independientes comprueban cada plantilla sobre las cuatro bases, además de ataques y hardcoding. Reward reconoce prompts exactos del registro reproducible de semilla 43; para datasets nuevos extender el registro, sin exponer bases ocultas.

## Protocolo y artefactos

Piloto separado: tres tareas (una por nivel), semilla 99, una muestra por modelo a temperatura 0.7. Benchmark: 90 tareas compartidas, semilla 43, 30 por nivel; tres muestras con semillas 42/43/44, temperatura 0.7, think=false, contexto 4096 y máximo 1024 tokens por llamada. Un modelo local a la vez, sin JSON forzado. Solo prompts visibles al modelo; referencias y datos ocultos permanecen en tasks.jsonl.

Cada carpeta de modelo conserva metadata.json, responses.jsonl y summary.json; la raíz tiene tasks.jsonl, environment.json y comparison.json. Se registran prompts, respuestas crudas, semillas, pesos/digest/cuantización, versiones, tokens, tiempo y truncamiento. Se rechazan carpetas existentes. Check regenera tareas, comprueba hashes y completitud, reproduce clasificación y métricas; no usa modelos ni escribe archivos. Metadatos identifican código y commit, aunque los archivos nuevos todavía no están comprometidos.

pass@k = promedio por tarea de 1-C(n-c,k)/C(n,k); pass@3 indica al menos un acierto en tres intentos. Cobertura significa salida seleccionada por el parser; no certifica razonamiento. Estados unparsed no equivalen a errores lógicos. No hay revisión manual incorporada en reward ni en métricas. Diversidad de completions mide textos distintos, no diversidad semántica.

## Reproducción
Desde raíz del repositorio; Python 3.12, biblioteca estándar, Ollama localhost:11434 y modelos instalados. Aquí se usa .venv/bin/python. Usar carpetas NUEVAS para repetir:

```sh
.venv/bin/python -m unittest discover -s spikes/text_to_sql -v
.venv/bin/python spikes/text_to_sql/evaluate.py run --pilot --model qwen3:1.7b --output spikes/text_to_sql/pilot-nuevo/qwen3-1.7b
.venv/bin/python spikes/text_to_sql/evaluate.py run --pilot --model llama3.2:1b --output spikes/text_to_sql/pilot-nuevo/llama3.2-1b
.venv/bin/python spikes/text_to_sql/evaluate.py run --model qwen3:1.7b --output spikes/text_to_sql/results-nuevos/qwen3-1.7b
.venv/bin/python spikes/text_to_sql/evaluate.py run --model llama3.2:1b --output spikes/text_to_sql/results-nuevos/llama3.2-1b
.venv/bin/python spikes/text_to_sql/evaluate.py check spikes/text_to_sql/results
```

No se generan datos SFT/DPO ni se entrena. Faltan particiones independientes, diversidad adicional, baseline de frontera y validación del futuro dataset según el PDF. Este spike no cambia el tema acordado. Inferencia exploratoria no equivale a entrega completa.

Sandbox de proceso adicional: cada consulta se ejecuta en un hijo Linux (fork), con watchdog de 250 ms de pared más cierre del proceso (hasta 20 ms), salida máxima de 64000 bytes y terminación forzosa si excede el plazo. Esto cubre compilación y funciones nativas además del progress_handler. No requiere dependencias.

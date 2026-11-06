# Spike: Reparación de bases con herramientas

Tres tablas: catálogo products inmutable; líneas con sku/units/order_id inmutables y product_id/unit_price/amount reparables; orders.total reparable. Regla explícita de precios actuales de catálogo, sin inferir precios históricos. Los totales se derivan desde fuentes inmutables. Fácil: dos líneas y un error de precio/importe; medio: cuatro líneas y tres errores; difícil: siete líneas y seis errores en referencias, precios, importes o totales. Nueve controles limpios (tres por nivel). [Informe](report.md).

El modelo recibe esquema/reglas, consulta JSON de solo lectura y termina con un parche de celdas. Máximo cuatro llamadas: tres consultas y un turno final; 40 filas por consulta, 1024 tokens generados por llamada, 4096 por trayectoria, contexto 4096 por llamada. Son presupuestos máximos, no obligación de consultar. Consulta fallida consume turno; recuperación permitida. Sin herramientas nativas ni SQL de escritura: mensajes de asistente/usuario implementan el protocolo explícito. El historial devuelve la consulta normalizada (sin prosa de razonamiento) para limitar contexto; todas las salidas crudas se conservan en calls.

SQLite en memoria por consulta: authorizer restrictivo, query_only, extensiones desactivadas, funciones cerradas; SQL hasta 6000 caracteres, valores de 50000 bytes, profundidad 40, 50000 instrucciones/100 ms, control cada 100 instrucciones. No ATTACH, PRAGMA ni sqlite_master. Parches se aplican a una copia aislada Python y se comprueban contra valores derivados. Se rechazan cambios en catálogo o columnas inmutables, IDs inexistentes, duplicados, tipos ambiguos, modificaciones innecesarias, parches parciales y daño colateral.

Completion para reward es JSON {"trajectory":[{"query":"...","result":{...}}],"final":{"patch":[...]}}. El evaluador lo construye desde llamadas crudas; reward reproduce las consultas y comprueba el parche. Se acepta cualquier orden equivalente. El registro reproducible reconoce prompts exactos de semilla 43; nuevas semillas requieren registrar sus tareas. Referencias y estado limpio nunca se envían al modelo. Errores: unparsed/protocol, unauthorized, duplicate, unknown_id, unnecessary, detection (faltan celdas), repair (valor incorrecto). La cobertura de este protocolo exige una estructura de parche interpretable: excluye unparsed y protocol. Query_errors cuenta herramientas fallidas incluso en trayectorias que logran recuperarse. El costo total incluye TODAS las llamadas; no compararlo con un único turno de otros spikes.

## Protocolo y artefactos

Piloto separado: tres tareas (control limpio fácil, reparación media y difícil), semilla 99, una muestra por modelo a temperatura 0.7. Benchmark: 90 tareas compartidas, semilla 43, 30 por nivel; tres muestras con semillas 42/43/44, temperatura 0.7, think=false, contexto 4096 y máximo 1024 tokens por llamada. Un modelo local a la vez, sin JSON forzado. Solo prompts visibles al modelo; referencias y datos ocultos permanecen en tasks.jsonl.

Cada carpeta de modelo conserva metadata.json, responses.jsonl y summary.json; la raíz tiene tasks.jsonl, environment.json y comparison.json. Se registran prompts, respuestas crudas, semillas, pesos/digest/cuantización, versiones, tokens, tiempo y truncamiento. Se rechazan carpetas existentes. Check regenera tareas, comprueba hashes y completitud, reproduce clasificación y métricas; no usa modelos ni escribe archivos. Metadatos identifican código y commit, aunque los archivos nuevos todavía no están comprometidos.

pass@k = promedio por tarea de 1-C(n-c,k)/C(n,k); pass@3 indica al menos un acierto en tres intentos. Cobertura significa salida seleccionada por el parser; no certifica razonamiento. Estados unparsed no equivalen a errores lógicos. No hay revisión manual incorporada en reward ni en métricas. Diversidad de completions mide textos distintos, no diversidad semántica.

## Reproducción
Desde raíz del repositorio; Python 3.12, biblioteca estándar, Ollama localhost:11434 y modelos instalados. Aquí se usa .venv/bin/python. Usar carpetas NUEVAS para repetir:

```sh
.venv/bin/python -m unittest discover -s spikes/database_repair -v
.venv/bin/python spikes/database_repair/evaluate.py run --pilot --model qwen3:1.7b --output spikes/database_repair/pilot-nuevo/qwen3-1.7b
.venv/bin/python spikes/database_repair/evaluate.py run --pilot --model llama3.2:1b --output spikes/database_repair/pilot-nuevo/llama3.2-1b
.venv/bin/python spikes/database_repair/evaluate.py run --model qwen3:1.7b --output spikes/database_repair/results-nuevos/qwen3-1.7b
.venv/bin/python spikes/database_repair/evaluate.py run --model llama3.2:1b --output spikes/database_repair/results-nuevos/llama3.2-1b
.venv/bin/python spikes/database_repair/evaluate.py check spikes/database_repair/results
```

No se generan datos SFT/DPO ni se entrena. Faltan particiones independientes, diversidad adicional, baseline de frontera y validación del futuro dataset según el PDF. Este spike no cambia el tema acordado. Inferencia exploratoria no equivale a entrega completa.

Sandbox de proceso adicional: cada consulta se ejecuta en un hijo Linux (fork), con watchdog de 200 ms de pared más cierre del proceso (hasta 20 ms), salida máxima de 64000 bytes y terminación forzosa si excede el plazo. Esto cubre compilación y funciones nativas además del progress_handler. No requiere dependencias.

Se separan métricas de los nueve controles limpios y las 81 bases corruptas en controls de summary.json. Esto distingue reparación efectiva de acertar mediante parche vacío.

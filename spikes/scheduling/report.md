# scheduling

Resultados automáticos reales. 90 tareas y 540 respuestas/ trayectorias completas.

[Protocolo, generación, pruebas, alcance y comandos](README.md). [Artefactos](results/comparison.json).

## Métricas

| Modelo | Nivel | Aciertos / respuestas | pass@1 | pass@3 | Cobertura |
| --- | --- | --- | --- | --- | --- |
| qwen3-1.7b | total | 61/270 | 22.59% | 35.56% | 61.11% |
| qwen3-1.7b | easy | 56/90 | 62.22% | 93.33% | 93.33% |
| qwen3-1.7b | medium | 5/90 | 5.56% | 13.33% | 66.67% |
| qwen3-1.7b | hard | 0/90 | 0.00% | 0.00% | 23.33% |
| llama3.2-1b | total | 0/270 | 0.00% | 0.00% | 15.93% |
| llama3.2-1b | easy | 0/90 | 0.00% | 0.00% | 13.33% |
| llama3.2-1b | medium | 0/90 | 0.00% | 0.00% | 21.11% |
| llama3.2-1b | hard | 0/90 | 0.00% | 0.00% | 13.33% |

## Costo

| Modelo | Segundos de pared | Tokens entrada/salida | Llamadas | Truncadas | Textos distintos por tarea |
| --- | --- | --- | --- | --- | --- |
| qwen3-1.7b | 3613.5 | 93156/243217 | 270 | 117 | 3.00 |
| llama3.2-1b | 2199.9 | 92586/167610 | 270 | 52 | 3.00 |

Tiempo de pared suma llamadas con respuesta guardada; incluye carga/inferencia y herramientas. Tokens de entrada incluyen contextos reenviados. Textos distintos no prueban diversidad semántica. Las cuantizaciones difieren: Qwen Q4_K_M, Llama Q8_0. Versiones, pesos, entorno y hashes en metadata.json.

## Estados y ejemplos automáticos

### qwen3-1.7b

Estados: `{"correct": 61, "deadline": 34, "unparsed": 105, "overlap": 30, "precedence": 28, "ids": 11, "resource": 1}`.

- `easy-00`, muestra 0, `correct`: `Para construir un **horario factible** con los requisitos dados, debemos:  - Asignar **tareas** a **recursos**. - Garant … as terminan antes o al inicio de su sucesora:   - T14 → T46 (3 → 8 ✅)   - T46 → T28 (8 → 13 ✅)  ✅ **Horario factible** ✅`
- `easy-00`, muestra 2, `deadline`: `Vamos a construir un **horario factible** que cumple con todas las condiciones dadas:  ### DATOS: - Tareas:     - 'T28': …  Todas las tareas tienen predecesores vacíos.   - Todos los recursos son permitidos.  ✅ **Horario factible construido.**`
- `easy-01`, muestra 1, `unparsed`: `Para construir un **horario factible** con los requisitos dados, seguimos los siguientes pasos:  ---  ### **Requisitos c … *T17** → start = 0, R0, R1   - **T23** → start = 2, R1   - **T25** → start = 6, R1    ---  ### ✅ **Respuesta final (JSON`
- `easy-04`, muestra 1, `overlap`: `Para construir un **horario factible** con los requisitos dados, seguimos los siguientes pasos:  ---  ### **Requisitos c … s o al inicio de sus sucesoras. - Todas las tareas terminan dentro de sus deadlines.  ✅ **Horario factible construido.**`
- `easy-07`, muestra 0, `precedence`: `Vamos a construir un **horario factible** que cumple con todos los requisitos:  ### Datos: - Tareas:   - T84: duración 2 … 0, "resource": "R0"},   {"id": "T84", "start": 2, "resource": "R0"},   {"id": "T43", "start": 4, "resource": "R0"} ] '''`
### llama3.2-1b

Estados: `{"unparsed": 227, "deadline": 5, "resource": 14, "ids": 21, "precedence": 3}`.

- `easy-00`, muestra 0, `unparsed`: `¡Claro! A continuación, te presento un posible horario factible para las tareas dadas:  '''json {     "T28": {         " … decesora de cada tarea finalice antes o al inicio de su sucesora. Todas las tareas terminan a más tardar en su deadline.`
- `easy-00`, muestra 1, `deadline`: `Para crear un horario factible con los requisitos especificados, podemos utilizar algoritmos de programación para ordena … ": "T14",     "start": 3,     "resource": "R1"   },   {     "id": "T46",     "start": 16,     "resource": "R0"   } ] '''`
- `easy-05`, muestra 0, `resource`: `Aquí te presento un posible horario factible para las tareas proporcionadas:  ''' [     {         "id": "T68",         " … icio de su predecesora. *   Cada tarea utiliza un recurso permitido. *   Toda tarea termina a más tardar en su deadline.`
- `easy-07`, muestra 0, `ids`: `Aquí te presento un posible horario factible basado en los datos proporcionados:  '''json [     {         "id": "T0",    … tervalos [inicio,inicio+duración); tareas consecutivas sí se permiten. - Toda tarea termina a más tardar en su deadline.`
- `easy-14`, muestra 0, `precedence`: `Aquí te presento un posible horario factible:  ''' [     {         "id": "T71",         "start": 0,         "resource":  … : 4,         "resource": "R0"     },     {         "id": "T96",         "start": 8,         "resource": "R0"     } ] '''`

## Piloto separado

- qwen3-1.7b: 3 respuestas; 38.0 s; 2630 tokens generados; 1 truncamientos. Semilla 99, separado del benchmark.

## Calibración y límites

pass@k promedia 1-C(n-c,k)/C(n,k); pass@3 indica al menos un acierto en tres intentos. El éxito verificable depende del parser: unparsed y truncamiento no demuestran incapacidad lógica. Revisar aciertos y fallos interpretables por nivel junto a cobertura y truncamiento. Las etiquetas de dificultad son hipótesis generativas, no una escala cognitiva validada. No se incorporaron revisiones manuales a métricas ni reward.

Las tareas se congelaron antes del benchmark, tras un piloto separado. Son exploratorias: no hay train/eval/test finales, SFT/DPO, entrenamiento ni baseline de frontera. Aumentar instancias de las mismas plantillas no asegura originalidad o profundidad. Una completion correcta no certifica sus pasos ni es SFT automáticamente. Ver README para debilidades específicas.

Ollama y la sesión se interrumpieron durante el experimento. Se retomaron solo muestras faltantes con mismos pesos, backend y código. Snapshots/hashes y eventos en interrupted/ y metadata.json. Costos excluyen llamadas abortadas sin respuesta y pausas entre sesiones; la velocidad del hardware varió.

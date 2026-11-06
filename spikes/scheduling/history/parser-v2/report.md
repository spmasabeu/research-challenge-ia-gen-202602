# scheduling

Resultados automáticos reales. 90 tareas y 540 respuestas/ trayectorias completas.

[Protocolo, generación, pruebas, alcance y comandos](README.md). [Artefactos](results/comparison.json).

## Métricas

| Modelo | Nivel | Aciertos / respuestas | pass@1 | pass@3 | Cobertura |
| --- | --- | --- | --- | --- | --- |
| qwen3-1.7b | total | 14/270 | 5.19% | 13.33% | 19.63% |
| qwen3-1.7b | easy | 11/90 | 12.22% | 30.00% | 16.67% |
| qwen3-1.7b | medium | 3/90 | 3.33% | 10.00% | 28.89% |
| qwen3-1.7b | hard | 0/90 | 0.00% | 0.00% | 13.33% |
| llama3.2-1b | total | 0/270 | 0.00% | 0.00% | 13.70% |
| llama3.2-1b | easy | 0/90 | 0.00% | 0.00% | 10.00% |
| llama3.2-1b | medium | 0/90 | 0.00% | 0.00% | 18.89% |
| llama3.2-1b | hard | 0/90 | 0.00% | 0.00% | 12.22% |

## Costo

| Modelo | Segundos de pared | Tokens entrada/salida | Llamadas | Truncadas | Textos distintos por tarea |
| --- | --- | --- | --- | --- | --- |
| qwen3-1.7b | 3613.5 | 93156/243217 | 270 | 117 | 3.00 |
| llama3.2-1b | 2199.9 | 92586/167610 | 270 | 52 | 3.00 |

Tiempo de pared suma llamadas con respuesta guardada; incluye carga/inferencia y herramientas. Tokens de entrada incluyen contextos reenviados. Textos distintos no prueban diversidad semántica. Las cuantizaciones difieren: Qwen Q4_K_M, Llama Q8_0. Versiones, pesos, entorno y hashes en metadata.json.

## Estados y ejemplos automáticos

### qwen3-1.7b

Estados: `{"unparsed": 217, "deadline": 7, "correct": 14, "overlap": 8, "ids": 7, "precedence": 16, "resource": 1}`.

- `easy-00`, muestra 0, `unparsed`: Para construir un **horario factible** con los requisitos dados, debemos:  - Asignar **tareas** a **recursos**. - Garant … as terminan antes o al inicio de su sucesora:   - T14 → T46 (3 → 8 ✅)   - T46 → T28 (8 → 13 ✅)  ✅ **Horario factible** ✅
- `easy-05`, muestra 1, `deadline`: Para construir un **horario factible** con los requisitos dados, seguimos estos pasos:  ---  ### **DATOS DEL PROBLEMA:** … 0, "resource": "R0"},   {"id": "T53", "start": 4, "resource": "R0"},   {"id": "T43", "start": 9, "resource": "R1"} ] '''
- `easy-07`, muestra 2, `correct`: Para construir un **horario factible** con los requisitos dados, debemos cumplir con las siguientes reglas:  - Cada tare … 0, "resource": "R0"},   {"id": "T54", "start": 2, "resource": "R0"},   {"id": "T43", "start": 4, "resource": "R1"} ] '''
- `easy-08`, muestra 1, `overlap`: Para construir un **horario factible** con los requisitos dados, seguimos los siguientes pasos:  ---  ### **Requisitos c … 0, "resource": "R0"},   {"id": "T27", "start": 3, "resource": "R0"},   {"id": "T43", "start": 5, "resource": "R0"} ] '''
- `medium-02`, muestra 1, `ids`: Para construir un **horario factible** con los requisitos especificados, debemos asignar **tareas a recursos** de manera … én disponible, pero no se necesita).  ---  ¿Quieres una versión **más detallada** (con todos los recursos y intervalos)?
### llama3.2-1b

Estados: `{"unparsed": 233, "deadline": 4, "resource": 12, "precedence": 3, "ids": 18}`.

- `easy-00`, muestra 0, `unparsed`: ¡Claro! A continuación, te presento un posible horario factible para las tareas dadas:  '''json {     "T28": {         " … decesora de cada tarea finalice antes o al inicio de su sucesora. Todas las tareas terminan a más tardar en su deadline.
- `easy-00`, muestra 1, `deadline`: Para crear un horario factible con los requisitos especificados, podemos utilizar algoritmos de programación para ordena … ": "T14",     "start": 3,     "resource": "R1"   },   {     "id": "T46",     "start": 16,     "resource": "R0"   } ] '''
- `easy-05`, muestra 0, `resource`: Aquí te presento un posible horario factible para las tareas proporcionadas:  ''' [     {         "id": "T68",         " … icio de su predecesora. *   Cada tarea utiliza un recurso permitido. *   Toda tarea termina a más tardar en su deadline.
- `easy-14`, muestra 0, `precedence`: Aquí te presento un posible horario factible:  ''' [     {         "id": "T71",         "start": 0,         "resource":  … : 4,         "resource": "R0"     },     {         "id": "T96",         "start": 8,         "resource": "R0"     } ] '''
- `easy-23`, muestra 0, `ids`: Aquí te presento un posible horario factible:  ''' [     {         "id": "T75",         "start": 0,         "resource":  … minutos para T80) * No se solapan intervalos en el mismo recurso * Todas las tareas terminan a más tardar en su deadline

## Piloto separado

- qwen3-1.7b: 3 respuestas; 38.0 s; 2630 tokens generados; 1 truncamientos. Semilla 99, separado del benchmark.

## Calibración y límites

pass@k promedia 1-C(n-c,k)/C(n,k); pass@3 indica al menos un acierto en tres intentos. El éxito verificable depende del parser: unparsed y truncamiento no demuestran incapacidad lógica. Revisar aciertos y fallos interpretables por nivel junto a cobertura y truncamiento. Las etiquetas de dificultad son hipótesis generativas, no una escala cognitiva validada. No se incorporaron revisiones manuales a métricas ni reward.

Las tareas se congelaron antes del benchmark, tras un piloto separado. Son exploratorias: no hay train/eval/test finales, SFT/DPO, entrenamiento ni baseline de frontera. Aumentar instancias de las mismas plantillas no asegura originalidad o profundidad. Una completion correcta no certifica sus pasos ni es SFT automáticamente. Ver README para debilidades específicas.

Ollama y la sesión se interrumpieron durante el experimento. Se retomaron solo muestras faltantes con mismos pesos, backend y código. Snapshots/hashes y eventos en interrupted/ y metadata.json. Costos excluyen llamadas abortadas sin respuesta y pausas entre sesiones; la velocidad del hardware varió.

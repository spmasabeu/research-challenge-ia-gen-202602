# scheduling

Resultados automáticos reales. 90 tareas y 540 respuestas/ trayectorias completas.

[Protocolo, generación, pruebas, alcance y comandos](README.md). [Artefactos](results/comparison.json).

## Métricas

| Modelo | Nivel | Aciertos / respuestas | pass@1 | pass@3 | Cobertura |
| --- | --- | --- | --- | --- | --- |
| qwen3-1.7b | total | 38/270 | 14.07% | 27.78% | 34.81% |
| qwen3-1.7b | easy | 34/90 | 37.78% | 73.33% | 57.78% |
| qwen3-1.7b | medium | 4/90 | 4.44% | 10.00% | 36.67% |
| qwen3-1.7b | hard | 0/90 | 0.00% | 0.00% | 10.00% |
| llama3.2-1b | total | 0/270 | 0.00% | 0.00% | 2.22% |
| llama3.2-1b | easy | 0/90 | 0.00% | 0.00% | 1.11% |
| llama3.2-1b | medium | 0/90 | 0.00% | 0.00% | 2.22% |
| llama3.2-1b | hard | 0/90 | 0.00% | 0.00% | 3.33% |

## Costo

| Modelo | Segundos de pared | Tokens entrada/salida | Llamadas | Truncadas | Textos distintos por tarea |
| --- | --- | --- | --- | --- | --- |
| qwen3-1.7b | 3613.5 | 93156/243217 | 270 | 117 | 3.00 |
| llama3.2-1b | 2199.9 | 92586/167610 | 270 | 52 | 3.00 |

Tiempo de pared suma llamadas con respuesta guardada; incluye carga/inferencia y herramientas. Tokens de entrada incluyen contextos reenviados. Textos distintos no prueban diversidad semántica. Las cuantizaciones difieren: Qwen Q4_K_M, Llama Q8_0. Versiones, pesos, entorno y hashes en metadata.json.

## Estados y ejemplos automáticos

### qwen3-1.7b

Estados: `{"unparsed": 176, "correct": 38, "overlap": 15, "deadline": 20, "precedence": 17, "resource": 1, "ids": 3}`.

- `easy-00`, muestra 0, `unparsed`: Para construir un **horario factible** con los requisitos dados, debemos:  - Asignar **tareas** a **recursos**. - Garant … as terminan antes o al inicio de su sucesora:   - T14 → T46 (3 → 8 ✅)   - T46 → T28 (8 → 13 ✅)  ✅ **Horario factible** ✅
- `easy-02`, muestra 0, `correct`: Para construir un **horario factible** con los requisitos dados, debemos asignar tareas a recursos (R0, R1) de manera qu … 0, "resource": "R0"},   {"id": "T45", "start": 3, "resource": "R0"},   {"id": "T47", "start": 4, "resource": "R0"} ] '''
- `easy-04`, muestra 2, `overlap`: Vamos a construir un **horario factible** que cumple con todas las condiciones dadas:  ### DATOS: - Tareas: T83, T29, T9 … 0, "resource": "R1"},   {"id": "T29", "start": 1, "resource": "R0"},   {"id": "T83", "start": 1, "resource": "R0"} ] '''
- `easy-05`, muestra 0, `deadline`: Para construir un **horario factible** con los requisitos dados, seguimos estos pasos:  ### Datos de entrada: - **Tareas … 0, "resource": "R0"},   {"id": "T53", "start": 4, "resource": "R0"},   {"id": "T43", "start": 0, "resource": "R1"} ] '''
- `easy-07`, muestra 0, `precedence`: Vamos a construir un **horario factible** que cumple con todos los requisitos:  ### Datos: - Tareas:   - T84: duración 2 … 0, "resource": "R0"},   {"id": "T84", "start": 2, "resource": "R0"},   {"id": "T43", "start": 4, "resource": "R0"} ] '''
### llama3.2-1b

Estados: `{"unparsed": 264, "precedence": 2, "ids": 3, "resource": 1}`.

- `easy-00`, muestra 0, `unparsed`: ¡Claro! A continuación, te presento un posible horario factible para las tareas dadas:  '''json {     "T28": {         " … decesora de cada tarea finalice antes o al inicio de su sucesora. Todas las tareas terminan a más tardar en su deadline.
- `easy-14`, muestra 0, `precedence`: Aquí te presento un posible horario factible:  ''' [     {         "id": "T71",         "start": 0,         "resource":  … : 4,         "resource": "R0"     },     {         "id": "T96",         "start": 8,         "resource": "R0"     } ] '''
- `medium-29`, muestra 1, `ids`: Para crear un horario factible con los datos proporcionados, podemos seguir estos pasos:  1. Crear una lista de tareas ( …  {   "T48": { "start": 0 },   "T81": { "start": 7 } };  Object.assign(horario2, jobs["T85"]); console.log(horario2); '''
- `hard-06`, muestra 1, `resource`: Para crear un horario factible con las especificaciones dadas, necesitamos seguir los siguientes pasos:  1. Identificar  … : "T11",     "start": 17,     "resource": "R1"   },   {     "id": "T22",     "start": 21,     "resource": "R1"   } ] '''

## Piloto separado

- qwen3-1.7b: 3 respuestas; 38.0 s; 2630 tokens generados; 1 truncamientos. Semilla 99, separado del benchmark.

## Calibración y límites

pass@k promedia 1-C(n-c,k)/C(n,k); pass@3 indica al menos un acierto en tres intentos. El éxito verificable depende del parser: unparsed y truncamiento no demuestran incapacidad lógica. Revisar aciertos y fallos interpretables por nivel junto a cobertura y truncamiento. Las etiquetas de dificultad son hipótesis generativas, no una escala cognitiva validada. No se incorporaron revisiones manuales a métricas ni reward.

Las tareas se congelaron antes del benchmark, tras un piloto separado. Son exploratorias: no hay train/eval/test finales, SFT/DPO, entrenamiento ni baseline de frontera. Aumentar instancias de las mismas plantillas no asegura originalidad o profundidad. Una completion correcta no certifica sus pasos ni es SFT automáticamente. Ver README para debilidades específicas.

Ollama y la sesión se interrumpieron durante el experimento. Se retomaron solo muestras faltantes con mismos pesos, backend y código. Snapshots/hashes y eventos en interrupted/ y metadata.json. Costos excluyen llamadas abortadas sin respuesta y pausas entre sesiones; la velocidad del hardware varió.

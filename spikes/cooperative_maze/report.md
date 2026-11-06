# Laberinto cooperativo

Resultados automáticos reales. 90 tareas y 540 respuestas/ trayectorias completas.

[Protocolo, generación, pruebas, alcance y comandos](README.md). [Artefactos](results/comparison.json).

## Métricas

| Modelo | Nivel | Aciertos / respuestas | pass@1 | pass@3 | Cobertura |
| --- | --- | --- | --- | --- | --- |
| qwen3-1.7b | total | 2/270 | 0.74% | 2.22% | 31.11% |
| qwen3-1.7b | easy | 2/90 | 2.22% | 6.67% | 38.89% |
| qwen3-1.7b | medium | 0/90 | 0.00% | 0.00% | 34.44% |
| qwen3-1.7b | hard | 0/90 | 0.00% | 0.00% | 20.00% |
| llama3.2-1b | total | 0/270 | 0.00% | 0.00% | 45.56% |
| llama3.2-1b | easy | 0/90 | 0.00% | 0.00% | 47.78% |
| llama3.2-1b | medium | 0/90 | 0.00% | 0.00% | 42.22% |
| llama3.2-1b | hard | 0/90 | 0.00% | 0.00% | 46.67% |

## Costo

| Modelo | Segundos de pared | Tokens entrada/salida | Llamadas | Truncadas | Textos distintos por tarea |
| --- | --- | --- | --- | --- | --- |
| qwen3-1.7b | 3343.2 | 75537/253771 | 270 | 150 | 3.00 |
| llama3.2-1b | 2012.4 | 77748/144512 | 270 | 50 | 3.00 |

Tiempo de pared suma llamadas con respuesta guardada; incluye carga/inferencia y herramientas. Tokens de entrada incluyen contextos reenviados. Textos distintos no prueban diversidad semántica. Las cuantizaciones difieren: Qwen Q4_K_M, Llama Q8_0. Versiones, pesos, entorno y hashes en metadata.json.

## Estados y ejemplos automáticos

### qwen3-1.7b

Estados: `{"unparsed": 186, "bounds": 27, "wall": 45, "correct": 2, "unknown_agent": 1, "locked": 7, "budget": 2}`.

- `easy-00`, muestra 0, `unparsed`: `Vamos a planificar un **laberinto** que cumple con todas las reglas dadas, utilizando un **acción_budget de 8** y devolv … ": "R"},   {"agent": "A", "move": "R"},   {"agent": "A", "move": "R"},   {"agent": "A", "move": "R"},   {"agent": "A", "`
- `easy-00`, muestra 2, `bounds`: `### Información del laberinto:  - **Grid (base cero):**   '''   [0][0] [0][1] [0][2] [0][3]   [1][0] . . . .   [2][0] .  … t": "A", "move": "R"},   {"agent": "A", "move": "R"},   {"agent": "A", "move": "R"},   {"agent": "A", "move": "R"} ] '''`
- `easy-04`, muestra 1, `wall`: `### **Instrucciones:** - El laberinto se representa como una matriz de 5 filas y 4 columnas. - Las coordenadas son **[fi …  **No se compartieron casillas**. - **No se salieron del tablero**.  ✅ **Solución válida** dentro del **action_budget**.`
- `easy-06`, muestra 0, `correct`: `### Descripción del laberinto:  - **Grid (4x4):**   '''   . . # .   . . . #   . . . .   # . . .   '''  - **Agentes:**    … rray JSON):  '''json [   {"agent": "A", "move": "R"},   {"agent": "A", "move": "R"},   {"agent": "A", "move": "D"} ] '''`
- `easy-12`, muestra 0, `unknown_agent`: `### Descripción del laberinto:  - **Grid (10x10):**   '''   ....   ###.   ....   #.#.   ...#   '''  - **Casillas:**   -  … uzar puertas).  ---  ¿Quieres que se incluya la recuperación de la llave o la visualización del laberinto en un gráfico?`

Diagnósticos específicos:

```json
{
  "first_invalid_action": {
    "2": 15,
    "1": 22,
    "0": 32,
    "3": 5,
    "6": 1,
    "7": 1,
    "8": 2,
    "4": 1,
    "10": 1
  },
  "mean_parsed_length": 9.44047619047619
}
```
### llama3.2-1b

Estados: `{"budget": 1, "unparsed": 147, "unknown_agent": 66, "malformed": 6, "bounds": 12, "incomplete": 14, "locked": 4, "wall": 20}`.

- `easy-00`, muestra 0, `budget`: `¡Claro! A continuación, te presento una posible solución para el laberinto:  ''' [   {"agent":"E","move":"L"},   {"agent … )  Los agentes comienzan en la casilla D, y el objetivo es llegar a la meta K sin salir del tablero o cruzar una puerta.`
- `easy-00`, muestra 1, `unparsed`: `Para resolver este laberinto, podemos seguir estos pasos:  **Paso 1: Identificar las posibles metas y la estrategia**  * … t": "A",     "move": "R"   },   {     "agent": "B",     "move": "U"   },   {     "agent": "C",     "move": "D"   } ] '''`
- `easy-01`, muestra 0, `unknown_agent`: `¡Claro! A continuación, te presento una posible solución para el laberinto:  ''' [   {"agent":"C","move":"R"},   {"agent … ecogen la llave cuando llegan a ella. Todos los agentes terminan en sus metas, cumpliendo con el objetivo del laberinto.`
- `easy-02`, muestra 0, `malformed`: `¡Claro! A continuación, te presento una posible solución para el laberinto:  '''json [   {     "agent": "A",     "move": …  (no puede moverse hacia arriba). Además, los agentes no pueden cruzar la puerta D ni compartir casilla con el agente D.`
- `easy-05`, muestra 2, `bounds`: `Para resolver este laberinto, necesitamos seguir un enfoque dinámico y exploratorio. Aquí te presento una posible soluci … ro cumple con todas las condiciones de la problema y puede ser usada como base para explorar soluciones más optimizadas.`

Diagnósticos específicos:

```json
{
  "first_invalid_action": {
    "0": 67,
    "1": 31,
    "3": 4,
    "2": 6
  },
  "mean_parsed_length": 4.5528455284552845
}
```

## Piloto separado

- qwen3-1.7b: 3 respuestas; 43.4 s; 2718 tokens generados; 1 truncamientos. Semilla 99, separado del benchmark.
- llama3.2-1b: 3 respuestas; 13.8 s; 905 tokens generados; 0 truncamientos. Semilla 99, separado del benchmark.

## Calibración y límites

pass@k promedia 1-C(n-c,k)/C(n,k); pass@3 indica al menos un acierto en tres intentos. El éxito verificable depende del parser: unparsed y truncamiento no demuestran incapacidad lógica. Revisar aciertos y fallos interpretables por nivel junto a cobertura y truncamiento. Las etiquetas de dificultad son hipótesis generativas, no una escala cognitiva validada. No se incorporaron revisiones manuales a métricas ni reward.

Las tareas se congelaron antes del benchmark, tras un piloto separado. Son exploratorias: no hay train/eval/test finales, SFT/DPO, entrenamiento ni baseline de frontera. Aumentar instancias de las mismas plantillas no asegura originalidad o profundidad. Una completion correcta no certifica sus pasos ni es SFT automáticamente. Ver README para debilidades específicas.

<!-- ANALYSIS_START -->
## Interpretación del spike

V2 registra Qwen 2/270 respuestas correctas (pass@1 0.74%, pass@3 2.22%), ambas fáciles; Llama 0/270. Cobertura 31.11% y 45.56%. No hay señal positiva observada en llave/puerta o cooperación. Entre planes interpretados, Qwen tiene 80 primeras acciones inválidas y dos excesos de presupuesto; Llama tiene 108 primeras acciones inválidas, 14 planes con metas incompletas y un exceso de presupuesto. El índice inicial concentra fallos: 32 Qwen y 67 Llama fallan en su primera acción.

Los 150/270 truncamientos Qwen y 50/270 Llama son un factor material. Aunque las referencias BFS caben en el presupuesto, las explicaciones del modelo consumen salida antes de completar un plan. El bajo éxito no permite atribuir todos los fallos a incapacidad de planificación; falta separar seguimiento de coordenadas/formato, presupuesto de salida y razonamiento. Los dos aciertos no prueban aprendizaje futuro ni calidad de sus explicaciones.

Se corrigió la confusión entre mapas ASCII/coordenadas informativas y el array final. V1 y sus fuentes permanecen en history/parser-v1; V2 modifica 73 status Qwen y dos Llama sobre las mismas llamadas guardadas. Es una revisión automática tras observar respuestas, sin revisión manual de etiquetas, sin selección por referencia y sin nuevas inferencias; no equivale a evaluar un test independiente.

Como temática, ofrece metas verificables y cooperación real, pero requiere un piloto nuevo con representación más simple, escalones de longitud y presupuesto comprobado antes de construir el dataset final. No ampliar directamente estos mapas para entrenamiento: primero obtener una franja de aciertos y errores interpretables y después diversificar estructuras y dependencias.
<!-- ANALYSIS_END -->

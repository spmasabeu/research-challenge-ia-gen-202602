# Laberinto cooperativo

Resultados automáticos reales. 90 tareas y 540 respuestas/ trayectorias completas.

[Protocolo, generación, pruebas, alcance y comandos](README.md). [Artefactos](results/comparison.json).

## Métricas

| Modelo | Nivel | Aciertos / respuestas | pass@1 | pass@3 | Cobertura |
| --- | --- | --- | --- | --- | --- |
| qwen3-1.7b | total | 0/270 | 0.00% | 0.00% | 4.07% |
| qwen3-1.7b | easy | 0/90 | 0.00% | 0.00% | 3.33% |
| qwen3-1.7b | medium | 0/90 | 0.00% | 0.00% | 7.78% |
| qwen3-1.7b | hard | 0/90 | 0.00% | 0.00% | 1.11% |
| llama3.2-1b | total | 0/270 | 0.00% | 0.00% | 44.81% |
| llama3.2-1b | easy | 0/90 | 0.00% | 0.00% | 47.78% |
| llama3.2-1b | medium | 0/90 | 0.00% | 0.00% | 41.11% |
| llama3.2-1b | hard | 0/90 | 0.00% | 0.00% | 45.56% |

## Costo

| Modelo | Segundos de pared | Tokens entrada/salida | Llamadas | Truncadas | Textos distintos por tarea |
| --- | --- | --- | --- | --- | --- |
| qwen3-1.7b | 3343.2 | 75537/253771 | 270 | 150 | 3.00 |
| llama3.2-1b | 2012.4 | 77748/144512 | 270 | 50 | 3.00 |

Tiempo de pared suma llamadas con respuesta guardada; incluye carga/inferencia y herramientas. Tokens de entrada incluyen contextos reenviados. Textos distintos no prueban diversidad semántica. Las cuantizaciones difieren: Qwen Q4_K_M, Llama Q8_0. Versiones, pesos, entorno y hashes en metadata.json.

## Estados y ejemplos automáticos

### qwen3-1.7b

Estados: `{"unparsed": 259, "bounds": 5, "wall": 6}`.

- `easy-00`, muestra 0, `unparsed`: Vamos a planificar un **laberinto** que cumple con todas las reglas dadas, utilizando un **acción_budget de 8** y devolv … ": "R"},   {"agent": "A", "move": "R"},   {"agent": "A", "move": "R"},   {"agent": "A", "move": "R"},   {"agent": "A", "
- `easy-02`, muestra 2, `bounds`: ### Información del Laberinto  - **Tamaño del tablero**: 4x4 (fila 0 a 3, columna 0 a 3) - **Grid**:   - '#' = pared   - … t": "A", "move": "U"},   {"agent": "A", "move": "U"},   {"agent": "A", "move": "L"},   {"agent": "A", "move": "L"} ] '''
- `medium-00`, muestra 1, `wall`: ### **Instrucciones:**  - **Base de coordenadas:** Fila crece hacia abajo, columna crece a la derecha. - **Grid:**   - ' … t": "A", "move": "R"},   {"agent": "A", "move": "D"},   {"agent": "A", "move": "R"},   {"agent": "A", "move": "D"} ] '''

Diagnósticos específicos:

```json
{
  "first_invalid_action": {
    "1": 2,
    "2": 3,
    "0": 5,
    "8": 1
  },
  "mean_parsed_length": 8.909090909090908
}
```
### llama3.2-1b

Estados: `{"budget": 1, "unparsed": 149, "unknown_agent": 65, "malformed": 6, "bounds": 12, "incomplete": 14, "locked": 4, "wall": 19}`.

- `easy-00`, muestra 0, `budget`: ¡Claro! A continuación, te presento una posible solución para el laberinto:  ''' [   {"agent":"E","move":"L"},   {"agent … )  Los agentes comienzan en la casilla D, y el objetivo es llegar a la meta K sin salir del tablero o cruzar una puerta.
- `easy-00`, muestra 1, `unparsed`: Para resolver este laberinto, podemos seguir estos pasos:  **Paso 1: Identificar las posibles metas y la estrategia**  * … t": "A",     "move": "R"   },   {     "agent": "B",     "move": "U"   },   {     "agent": "C",     "move": "D"   } ] '''
- `easy-01`, muestra 0, `unknown_agent`: ¡Claro! A continuación, te presento una posible solución para el laberinto:  ''' [   {"agent":"C","move":"R"},   {"agent … ecogen la llave cuando llegan a ella. Todos los agentes terminan en sus metas, cumpliendo con el objetivo del laberinto.
- `easy-02`, muestra 0, `malformed`: ¡Claro! A continuación, te presento una posible solución para el laberinto:  '''json [   {     "agent": "A",     "move": …  (no puede moverse hacia arriba). Además, los agentes no pueden cruzar la puerta D ni compartir casilla con el agente D.
- `easy-05`, muestra 2, `bounds`: Para resolver este laberinto, necesitamos seguir un enfoque dinámico y exploratorio. Aquí te presento una posible soluci … ro cumple con todas las condiciones de la problema y puede ser usada como base para explorar soluciones más optimizadas.

Diagnósticos específicos:

```json
{
  "first_invalid_action": {
    "0": 66,
    "1": 30,
    "3": 4,
    "2": 6
  },
  "mean_parsed_length": 4.570247933884297
}
```

## Piloto separado

- qwen3-1.7b: 3 respuestas; 43.4 s; 2718 tokens generados; 1 truncamientos. Semilla 99, separado del benchmark.
- llama3.2-1b: 3 respuestas; 13.8 s; 905 tokens generados; 0 truncamientos. Semilla 99, separado del benchmark.

## Calibración y límites

pass@k promedia 1-C(n-c,k)/C(n,k); pass@3 indica al menos un acierto en tres intentos. El éxito verificable depende del parser: unparsed y truncamiento no demuestran incapacidad lógica. Revisar aciertos y fallos interpretables por nivel junto a cobertura y truncamiento. Las etiquetas de dificultad son hipótesis generativas, no una escala cognitiva validada. No se incorporaron revisiones manuales a métricas ni reward.

Las tareas se congelaron antes del benchmark, tras un piloto separado. Son exploratorias: no hay train/eval/test finales, SFT/DPO, entrenamiento ni baseline de frontera. Aumentar instancias de las mismas plantillas no asegura originalidad o profundidad. Una completion correcta no certifica sus pasos ni es SFT automáticamente. Ver README para debilidades específicas.

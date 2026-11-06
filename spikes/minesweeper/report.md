# Buscaminas deductivo

Resultados automáticos reales. 90 tareas y 540 respuestas/ trayectorias completas.

[Protocolo, generación, pruebas, alcance y comandos](README.md). [Artefactos](results/comparison.json).

## Métricas

| Modelo | Nivel | Aciertos / respuestas | pass@1 | pass@3 | Cobertura |
| --- | --- | --- | --- | --- | --- |
| qwen3-1.7b | total | 29/270 | 10.74% | 23.33% | 34.07% |
| qwen3-1.7b | easy | 10/90 | 11.11% | 26.67% | 25.56% |
| qwen3-1.7b | medium | 16/90 | 17.78% | 33.33% | 57.78% |
| qwen3-1.7b | hard | 3/90 | 3.33% | 10.00% | 18.89% |
| llama3.2-1b | total | 1/270 | 0.37% | 1.11% | 0.74% |
| llama3.2-1b | easy | 0/90 | 0.00% | 0.00% | 0.00% |
| llama3.2-1b | medium | 1/90 | 1.11% | 3.33% | 2.22% |
| llama3.2-1b | hard | 0/90 | 0.00% | 0.00% | 0.00% |

## Costo

| Modelo | Segundos de pared | Tokens entrada/salida | Llamadas | Truncadas | Textos distintos por tarea |
| --- | --- | --- | --- | --- | --- |
| qwen3-1.7b | 642.9 | 65610/47040 | 270 | 1 | 2.47 |
| llama3.2-1b | 997.5 | 68040/68309 | 270 | 3 | 3.00 |

Tiempo de pared suma llamadas con respuesta guardada; incluye carga/inferencia y herramientas. Tokens de entrada incluyen contextos reenviados. Textos distintos no prueban diversidad semántica. Las cuantizaciones difieren: Qwen Q4_K_M, Llama Q8_0. Versiones, pesos, entorno y hashes en metadata.json.

## Estados y ejemplos automáticos

### qwen3-1.7b

Estados: `{"unparsed": 178, "logic": 63, "correct": 29}`.

- `easy-00`, muestra 0, `unparsed`: `{   "row": 1,   "col": 1,   "classification": "indeterminada" }`
- `easy-00`, muestra 2, `logic`: `La posición objetivo es la coordenada (2, 1) en una matriz de 3x3. Las pistas visibles son:  - Fila 0: [1, 2, 2] - Fila  … es donde es mina y donde es segura).  **Respuesta JSON:** '''json {"row":2,"col":1,"classification":"indeterminada"} '''`
- `easy-03`, muestra 0, `correct`: `{"classification": "indeterminada"}`

Diagnósticos específicos:

```json
{
  "class": {
    "segura": {
      "tasks": 30,
      "responses": 90,
      "statuses": {
        "unparsed": 57,
        "logic": 29,
        "correct": 4
      },
      "coverage": 0.3666666666666667,
      "pass_at_k": {
        "1": 0.044444444444444446,
        "3": 0.13333333333333333
      }
    },
    "mina": {
      "tasks": 30,
      "responses": 90,
      "statuses": {
        "unparsed": 63,
        "logic": 25,
        "correct": 2
      },
      "coverage": 0.30000000000000004,
      "pass_at_k": {
        "1": 0.022222222222222223,
        "3": 0.06666666666666667
      }
    },
    "indeterminada": {
      "tasks": 30,
      "responses": 90,
      "statuses": {
        "unparsed": 58,
        "correct": 23,
        "logic": 9
      },
      "coverage": 0.3555555555555555,
      "pass_at_k": {
        "1": 0.2555555555555556,
        "3": 0.5
      }
    }
  },
  "confusion": {
    "segura": {
      "unparsed": 57,
      "indeterminada": 29,
      "segura": 4
    },
    "mina": {
      "unparsed": 63,
      "indeterminada": 22,
      "mina": 2,
      "segura": 3
    },
    "indeterminada": {
      "unparsed": 58,
      "indeterminada": 23,
      "segura": 9
    }
  },
  "majority_baseline": 0.3333333333333333
}
```
### llama3.2-1b

Estados: `{"unparsed": 268, "correct": 1, "logic": 1}`.

- `easy-00`, muestra 0, `unparsed`: `La configuración objetivos es la siguiente:  *   Fila: 8 *   Coluna: 7 *   Clasificación: segura/mina/mina/indeterminada  Y la coordenadas del objetivo son (4, 3).`
- `medium-00`, muestra 1, `correct`: `Para determinar el objetivo de la búsqueda dinámica Buscaminas deductivo, debemos analizar las pistas visibles y su comp … ordenadas del objetivo son (0, 0), y su clasificación es indeterminada debido a que solo se conocen las pistas visibles.`
- `medium-16`, muestra 1, `logic`: `Para determinar el objetivo, debemos analizar las pistas visibles y la configuración de mina y no mina.  Las pistas visi … eterminada'.  Aquí está el JSON correspondiente: ''' {   "row": 0,   "col": 0,   "classification": "indeterminada" } '''`

Diagnósticos específicos:

```json
{
  "class": {
    "segura": {
      "tasks": 30,
      "responses": 90,
      "statuses": {
        "unparsed": 89,
        "logic": 1
      },
      "coverage": 0.011111111111111072,
      "pass_at_k": {
        "1": 0.0,
        "3": 0.0
      }
    },
    "mina": {
      "tasks": 30,
      "responses": 90,
      "statuses": {
        "unparsed": 90
      },
      "coverage": 0.0,
      "pass_at_k": {
        "1": 0.0,
        "3": 0.0
      }
    },
    "indeterminada": {
      "tasks": 30,
      "responses": 90,
      "statuses": {
        "unparsed": 89,
        "correct": 1
      },
      "coverage": 0.011111111111111072,
      "pass_at_k": {
        "1": 0.011111111111111112,
        "3": 0.03333333333333333
      }
    }
  },
  "confusion": {
    "segura": {
      "unparsed": 89,
      "indeterminada": 1
    },
    "mina": {
      "unparsed": 90
    },
    "indeterminada": {
      "unparsed": 89,
      "indeterminada": 1
    }
  },
  "majority_baseline": 0.3333333333333333
}
```

## Piloto separado

- qwen3-1.7b: 3 respuestas; 14.8 s; 633 tokens generados; 0 truncamientos. Semilla 99, separado del benchmark.
- llama3.2-1b: 3 respuestas; 13.5 s; 817 tokens generados; 0 truncamientos. Semilla 99, separado del benchmark.

## Calibración y límites

pass@k promedia 1-C(n-c,k)/C(n,k); pass@3 indica al menos un acierto en tres intentos. El éxito verificable depende del parser: unparsed y truncamiento no demuestran incapacidad lógica. Revisar aciertos y fallos interpretables por nivel junto a cobertura y truncamiento. Las etiquetas de dificultad son hipótesis generativas, no una escala cognitiva validada. No se incorporaron revisiones manuales a métricas ni reward.

Las tareas se congelaron antes del benchmark, tras un piloto separado. Son exploratorias: no hay train/eval/test finales, SFT/DPO, entrenamiento ni baseline de frontera. Aumentar instancias de las mismas plantillas no asegura originalidad o profundidad. Una completion correcta no certifica sus pasos ni es SFT automáticamente. Ver README para debilidades específicas.

Baseline constante de clase mayoritaria: pass@1=pass@3=1/3. Una clasificación uniforme independiente al azar tendría pass@3=19/27≈70.37%; pass@3 alto por sí solo no prueba razonamiento.

<!-- ANALYSIS_START -->
## Lectura de la evidencia

El éxito verificable de Qwen (10.74%, pass@3 23.33%) queda debajo de la política constante indeterminada (33.33% en ambas métricas). La cobertura sobre el objetivo es baja: 153 de sus 178 casos unparsed contienen JSON interpretable con coordenadas incorrectas; en Llama sucede en 74 de 268. Esto mezcla fallos de atención al objetivo con otros formatos no interpretados, no demuestra incapacidad universal de resolver restricciones. La matriz de confusión y métricas por clase muestran qué se verificó realmente.

La revisión automática separó matrices de entrada de clasificaciones, preservando V1 y todas las llamadas crudas. No usó la referencia para escoger una respuesta, ni incorporó juicios sobre la explicación. Un ejemplo del piloto presenta una matriz inventada y una justificación contradictoria, aunque su etiqueta final coincide con la referencia: acertar una clase de tres no certifica los pasos. No filtrar SFT por la etiqueta únicamente.

Originalidad limitada por un juego conocido y salida de tres clases; profundidad controlada por restricciones combinadas y tamaño de frontera. El solver exacto y balance de clases son bases robustas, pero primero habría que corregir la lectura del objetivo y demostrar señal de deducción sobre el baseline antes de priorizar este tema para entrenamiento.
<!-- ANALYSIS_END -->

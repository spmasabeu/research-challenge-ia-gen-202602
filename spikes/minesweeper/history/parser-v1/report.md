# Buscaminas deductivo

Resultados automáticos reales. 90 tareas y 540 respuestas/ trayectorias completas.

[Protocolo, generación, pruebas, alcance y comandos](README.md). [Artefactos](results/comparison.json).

## Métricas

| Modelo | Nivel | Aciertos / respuestas | pass@1 | pass@3 | Cobertura |
| --- | --- | --- | --- | --- | --- |
| qwen3-1.7b | total | 27/270 | 10.00% | 22.22% | 31.85% |
| qwen3-1.7b | easy | 10/90 | 11.11% | 26.67% | 21.11% |
| qwen3-1.7b | medium | 15/90 | 16.67% | 33.33% | 56.67% |
| qwen3-1.7b | hard | 2/90 | 2.22% | 6.67% | 17.78% |
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

Estados: `{"unparsed": 184, "logic": 59, "correct": 27}`.

- `easy-00`, muestra 0, `unparsed`: {   "row": 1,   "col": 1,   "classification": "indeterminada" }
- `easy-00`, muestra 2, `logic`: La posición objetivo es la coordenada (2, 1) en una matriz de 3x3. Las pistas visibles son:  - Fila 0: [1, 2, 2] - Fila  … es donde es mina y donde es segura).  **Respuesta JSON:** '''json {"row":2,"col":1,"classification":"indeterminada"} '''
- `easy-03`, muestra 0, `correct`: {"classification": "indeterminada"}

Diagnósticos específicos:

```json
{
  "class": {
    "segura": {
      "tasks": 30,
      "responses": 90,
      "statuses": {
        "unparsed": 60,
        "logic": 27,
        "correct": 3
      },
      "coverage": 0.33333333333333337,
      "pass_at_k": {
        "1": 0.03333333333333333,
        "3": 0.1
      }
    },
    "mina": {
      "tasks": 30,
      "responses": 90,
      "statuses": {
        "unparsed": 64,
        "logic": 24,
        "correct": 2
      },
      "coverage": 0.28888888888888886,
      "pass_at_k": {
        "1": 0.022222222222222223,
        "3": 0.06666666666666667
      }
    },
    "indeterminada": {
      "tasks": 30,
      "responses": 90,
      "statuses": {
        "unparsed": 60,
        "correct": 22,
        "logic": 8
      },
      "coverage": 0.33333333333333337,
      "pass_at_k": {
        "1": 0.24444444444444446,
        "3": 0.5
      }
    }
  },
  "confusion": {
    "segura": {
      "unparsed": 60,
      "indeterminada": 27,
      "segura": 3
    },
    "mina": {
      "unparsed": 64,
      "indeterminada": 21,
      "mina": 2,
      "segura": 3
    },
    "indeterminada": {
      "unparsed": 60,
      "indeterminada": 22,
      "segura": 8
    }
  },
  "majority_baseline": 0.3333333333333333
}
```
### llama3.2-1b

Estados: `{"unparsed": 268, "correct": 1, "logic": 1}`.

- `easy-00`, muestra 0, `unparsed`: La configuración objetivos es la siguiente:  *   Fila: 8 *   Coluna: 7 *   Clasificación: segura/mina/mina/indeterminada  Y la coordenadas del objetivo son (4, 3).
- `medium-00`, muestra 1, `correct`: Para determinar el objetivo de la búsqueda dinámica Buscaminas deductivo, debemos analizar las pistas visibles y su comp … ordenadas del objetivo son (0, 0), y su clasificación es indeterminada debido a que solo se conocen las pistas visibles.
- `medium-16`, muestra 1, `logic`: Para determinar el objetivo, debemos analizar las pistas visibles y la configuración de mina y no mina.  Las pistas visi … eterminada'.  Aquí está el JSON correspondiente: ''' {   "row": 0,   "col": 0,   "classification": "indeterminada" } '''

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

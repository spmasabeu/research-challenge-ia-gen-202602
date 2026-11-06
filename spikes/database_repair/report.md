# Reparación de bases con herramientas

Resultados automáticos reales. 90 tareas y 540 respuestas/ trayectorias completas.

[Protocolo, generación, pruebas, alcance y comandos](README.md). [Artefactos](results/comparison.json).

## Métricas

| Modelo | Nivel | Aciertos / respuestas | pass@1 | pass@3 | Cobertura |
| --- | --- | --- | --- | --- | --- |
| qwen3-1.7b | total | 0/270 | 0.00% | 0.00% | 85.56% |
| qwen3-1.7b | easy | 0/90 | 0.00% | 0.00% | 93.33% |
| qwen3-1.7b | medium | 0/90 | 0.00% | 0.00% | 90.00% |
| qwen3-1.7b | hard | 0/90 | 0.00% | 0.00% | 73.33% |
| llama3.2-1b | total | 0/270 | 0.00% | 0.00% | 0.00% |
| llama3.2-1b | easy | 0/90 | 0.00% | 0.00% | 0.00% |
| llama3.2-1b | medium | 0/90 | 0.00% | 0.00% | 0.00% |
| llama3.2-1b | hard | 0/90 | 0.00% | 0.00% | 0.00% |

## Costo

| Modelo | Segundos de pared | Tokens entrada/salida | Llamadas | Truncadas | Textos distintos por tarea |
| --- | --- | --- | --- | --- | --- |
| qwen3-1.7b | 472.2 | 283725/29244 | 604 | 0 | 2.71 |
| llama3.2-1b | 940.3 | 112388/65052 | 322 | 8 | 3.00 |

Tiempo de pared suma llamadas con respuesta guardada; incluye carga/inferencia y herramientas. Tokens de entrada incluyen contextos reenviados. Textos distintos no prueban diversidad semántica. Las cuantizaciones difieren: Qwen Q4_K_M, Llama Q8_0. Versiones, pesos, entorno y hashes en metadata.json.

## Estados y ejemplos automáticos

### qwen3-1.7b

Estados: `{"unnecessary": 184, "protocol": 39, "repair": 47}`.

- `easy-00`, muestra 0, `unnecessary`: `{"trajectory": [{"query": "SELECT lines.id, lines.order_id, lines.sku, lines.units, lines.product_id, lines.unit_price,  … U7060-3", 4, 3, 23, 92, 23, 207]]}}], "final": {"patch": [{"table": "lines", "id": 1, "column": "amount", "value": 2}]}}`
- `easy-00`, muestra 2, `protocol`: `{"trajectory": [{"query": "SELECT lines.id, lines.order_id, lines.sku, lines.units, lines.product_id, lines.unit_price,  … t": {"error": "query", "message": "not authorized"}}], "final": {"error": "access_denied", "message": "not authorized"}}`
- `easy-04`, muestra 0, `repair`: `{"trajectory": [{"query": "SELECT lines.id, lines.order_id, lines.sku, lines.units, lines.product_id, lines.unit_price,  … "SKU3069-3", 3, 3, 29, 87, 105]]}}], "final": {"patch": [{"table": "lines", "id": 1, "column": "amount", "value": 20}]}}`

Diagnósticos específicos:

```json
{
  "controls": {
    "clean": {
      "tasks": 9,
      "responses": 27,
      "statuses": {
        "unnecessary": 24,
        "protocol": 3
      },
      "coverage": 0.8888888888888888,
      "pass_at_k": {
        "1": 0.0,
        "3": 0.0
      }
    },
    "corrupted": {
      "tasks": 81,
      "responses": 243,
      "statuses": {
        "unnecessary": 160,
        "repair": 47,
        "protocol": 36
      },
      "coverage": 0.8518518518518519,
      "pass_at_k": {
        "1": 0.0,
        "3": 0.0
      }
    }
  },
  "query_errors": 2,
  "mean_calls_per_trajectory": 2.237037037037037
}
```
### llama3.2-1b

Estados: `{"protocol": 270}`.

- `easy-00`, muestra 0, `protocol`: `{"trajectory": [], "final": {"invalid": "'''json\n{\n  \"query\": \"SELECT * FROM lines WHERE order_id IN (SELECT id FRO … \n            {\"amount\":13,\"product_id\":2,\"units\":7,\"unit_price\":200,\"sku\":\"GHI789\"}\n          ]\n}\n'''"}}`

Diagnósticos específicos:

```json
{
  "controls": {
    "clean": {
      "tasks": 9,
      "responses": 27,
      "statuses": {
        "protocol": 27
      },
      "coverage": 0.0,
      "pass_at_k": {
        "1": 0.0,
        "3": 0.0
      }
    },
    "corrupted": {
      "tasks": 81,
      "responses": 243,
      "statuses": {
        "protocol": 243
      },
      "coverage": 0.0,
      "pass_at_k": {
        "1": 0.0,
        "3": 0.0
      }
    }
  },
  "query_errors": 45,
  "mean_calls_per_trajectory": 1.1925925925925926
}
```

## Piloto separado

- qwen3-1.7b: 3 respuestas; 5.6 s; 348 tokens generados; 0 truncamientos. Semilla 99, separado del benchmark.
- llama3.2-1b: 3 respuestas; 17.7 s; 1364 tokens generados; 1 truncamientos. Semilla 99, separado del benchmark.

## Calibración y límites

pass@k promedia 1-C(n-c,k)/C(n,k); pass@3 indica al menos un acierto en tres intentos. El éxito verificable depende del parser: unparsed y truncamiento no demuestran incapacidad lógica. Revisar aciertos y fallos interpretables por nivel junto a cobertura y truncamiento. Las etiquetas de dificultad son hipótesis generativas, no una escala cognitiva validada. No se incorporaron revisiones manuales a métricas ni reward.

Las tareas se congelaron antes del benchmark, tras un piloto separado. Son exploratorias: no hay train/eval/test finales, SFT/DPO, entrenamiento ni baseline de frontera. Aumentar instancias de las mismas plantillas no asegura originalidad o profundidad. Una completion correcta no certifica sus pasos ni es SFT automáticamente. Ver README para debilidades específicas.

Cada respuesta es una trayectoria de hasta cuatro llamadas; sus costos incluyen todas. No equivale a un turno de otros spikes. Las métricas clean/corrupted distinguen reparar de acertar con parche vacío en los nueve controles limpios.

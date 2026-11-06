# Text-to-SQL con bases ocultas

Resultados automáticos reales. 90 tareas y 540 respuestas/ trayectorias completas.

[Protocolo, generación, pruebas, alcance y comandos](README.md). [Artefactos](results/comparison.json).

## Métricas

| Modelo | Nivel | Aciertos / respuestas | pass@1 | pass@3 | Cobertura |
| --- | --- | --- | --- | --- | --- |
| qwen3-1.7b | total | 90/270 | 33.33% | 33.33% | 99.63% |
| qwen3-1.7b | easy | 90/90 | 100.00% | 100.00% | 100.00% |
| qwen3-1.7b | medium | 0/90 | 0.00% | 0.00% | 100.00% |
| qwen3-1.7b | hard | 0/90 | 0.00% | 0.00% | 98.89% |
| llama3.2-1b | total | 6/270 | 2.22% | 6.67% | 99.63% |
| llama3.2-1b | easy | 6/90 | 6.67% | 20.00% | 100.00% |
| llama3.2-1b | medium | 0/90 | 0.00% | 0.00% | 98.89% |
| llama3.2-1b | hard | 0/90 | 0.00% | 0.00% | 100.00% |

## Costo

| Modelo | Segundos de pared | Tokens entrada/salida | Llamadas | Truncadas | Textos distintos por tarea |
| --- | --- | --- | --- | --- | --- |
| qwen3-1.7b | 194.3 | 114285/12557 | 270 | 1 | 2.03 |
| llama3.2-1b | 229.2 | 109683/15012 | 270 | 0 | 2.88 |

Tiempo de pared suma llamadas con respuesta guardada; incluye carga/inferencia y herramientas. Tokens de entrada incluyen contextos reenviados. Textos distintos no prueban diversidad semántica. Las cuantizaciones difieren: Qwen Q4_K_M, Llama Q8_0. Versiones, pesos, entorno y hashes en metadata.json.

## Estados y ejemplos automáticos

### qwen3-1.7b

Estados: `{"correct": 90, "execution": 85, "semantic": 50, "syntax": 44, "unparsed": 1}`.

- `easy-00`, muestra 0, `correct`: `SELECT id, amount FROM orders WHERE amount >= 17 AND ordered_at >= '2026-10-24';`
- `medium-00`, muestra 0, `execution`: `SELECT name FROM customers WHERE region = 'Sur' AND amount >= 35 UNION SELECT name FROM orders WHERE customer_id IN (SELECT id FROM customers WHERE region = 'Sur') AND amount >= 35;`
- `medium-02`, muestra 0, `semantic`: `SELECT name FROM customers WHERE region = 'Norte' AND id IN (     SELECT customer_id FROM orders     WHERE amount >= 30 )`
- `medium-18`, muestra 0, `syntax`: `SELECT name, amount FROM customers WHERE region = 'Centro' AND amount >= 30 WITH orders WHERE customer_id = customers.id AND amount >= 30 ORDER BY amount;`
- `hard-04`, muestra 1, `unparsed`: `SELECT id, name FROM customers WHERE region = 'Sur' ORDER BY (     SUM(CASE WHEN orders.amount IS NOT NULL THEN orders.a …                                                                                                            SUM(CASE WHEN`

Diagnósticos específicos:

```json
{
  "visible_pass_hidden_fail": 18
}
```
### llama3.2-1b

Estados: `{"execution": 194, "correct": 6, "semantic": 64, "syntax": 5, "unparsed": 1}`.

- `easy-00`, muestra 0, `execution`: `SELECT o.id, o.amount FROM orders AS o INNER JOIN customers AS c ON o.customer_id = c.id WHERE o.amount >= 17 AND o.ordered_at >= '2026-10-24'`
- `easy-02`, muestra 0, `correct`: `SELECT id, amount FROM orders WHERE amount >= 19 AND ordered_at >= '2026-10-20'`
- `medium-00`, muestra 0, `semantic`: `SELECT T1.name FROM customers AS T1 INNER JOIN orders AS T2 ON T1.id = T2.customer_id WHERE T2.amount >= 35 AND T1.region = 'Sur' GROUP BY T1.name ORDER BY COUNT(T2.id);`
- `medium-05`, muestra 1, `syntax`: `SELECT c.id, SUM(i.amount) FROM customers c LEFT JOIN orders o ON c.id = o.customer_id WHERE o.amount IS NOT NULL AND c.name ILIKE 'Cliente%' GROUP BY c.id`
- `medium-09`, muestra 1, `unparsed`: `SELECT c.id, SUM(i.amount) AS suma_Importes FROM customers c JOIN orders o ON c.id = o.customer_id WHERE o.amount > 10 G … s o ON c.id = o.customer_id WHERE o.amount > 10 GROUP BY c.id; '''  Esta consulta debería devolver el resultado deseado.`

Diagnósticos específicos:

```json
{
  "visible_pass_hidden_fail": 17
}
```

## Piloto separado

- qwen3-1.7b: 3 respuestas; 3.5 s; 120 tokens generados; 0 truncamientos. Semilla 99, separado del benchmark.
- llama3.2-1b: 3 respuestas; 3.2 s; 212 tokens generados; 0 truncamientos. Semilla 99, separado del benchmark.

## Calibración y límites

pass@k promedia 1-C(n-c,k)/C(n,k); pass@3 indica al menos un acierto en tres intentos. El éxito verificable depende del parser: unparsed y truncamiento no demuestran incapacidad lógica. Revisar aciertos y fallos interpretables por nivel junto a cobertura y truncamiento. Las etiquetas de dificultad son hipótesis generativas, no una escala cognitiva validada. No se incorporaron revisiones manuales a métricas ni reward.

Las tareas se congelaron antes del benchmark, tras un piloto separado. Son exploratorias: no hay train/eval/test finales, SFT/DPO, entrenamiento ni baseline de frontera. Aumentar instancias de las mismas plantillas no asegura originalidad o profundidad. Una completion correcta no certifica sus pasos ni es SFT automáticamente. Ver README para debilidades específicas.

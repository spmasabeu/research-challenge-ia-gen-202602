# Desafío de investigación · IIC3694

Harness y dataset reproducibles para mejorar el **razonamiento cuantitativo con
unidades** de un LLM pequeño (objetivo: Qwen3-1.7B). [Enunciado](DesafioInvestigacion-2026.pdf).
El tema se eligió entre seis spikes ([comparación](spikes/README.md)); ver
[decisiones](docs/2026-10-29_093018_decisiones.md).

**Estado (2026-11-07):** entorno base en `src/challenge/` con
`reward(prompt, completion) -> float`, generador con particiones sin fuga
(`data/units-v1/`), verificador endurecido, runner de línea base y exportador
SFT/DPO, con 21 pruebas. **Pendiente para la entrega:** línea base sobre
`units-v1`, trazas SFT/pares DPO, más familias/composición y el informe (ver
[Pendientes](#pendientes-para-la-entrega)).

## Uso rápido

Solo biblioteca estándar, Python 3.12. Con `uv` (`uv run …`) o con `python3`
directamente, siempre con `PYTHONPATH=src`:

```bash
python3 -m unittest discover -s tests -t .          # pruebas, sin modelos
PYTHONPATH=src python3 -m challenge.generator --out data/units-v1   # regenerar (idempotente)
```

```python
from challenge import reward          # interfaz común del curso
reward(task["prompt"], "FINAL: 50.4 km/h")   # -> 1.0 o 0.0
```

Línea base con Ollama (reanudable; guarda respuestas crudas):

```bash
ollama pull qwen3:1.7b
PYTHONPATH=src python3 -m challenge.evaluate run --tasks data/units-v1/eval.jsonl \
    --model qwen3:1.7b --samples 4 --out runs/eval/qwen3-1.7b
PYTHONPATH=src python3 -m challenge.evaluate score runs/eval/qwen3-1.7b   # re-verifica con el verificador actual
```

`summary.json` trae pass@k (estimador insesgado de Chen et al.), cobertura y
estados por nivel, por familia y por familia×nivel, más `mixed_tasks` (tareas
con aciertos y fallos: la señal que usa RL/DPO).

Datos derivados, **solo desde train** (el script se niega con otro split):

```bash
PYTHONPATH=src python3 -m challenge.evaluate run --tasks data/units-v1/train.jsonl \
    --model qwen3:8b --samples 4 --out runs/train/qwen3-8b
PYTHONPATH=src python3 -m challenge.derive --runs runs/train/qwen3-8b runs/train/qwen3-1.7b \
    --out data/units-v1/derived
```

## Estructura

```text
src/challenge/
  units.py      catálogo de unidades/alias, familias (fórmulas en SI) y solve(spec)
  generator.py  instancias, niveles, prompt y splits por hash  → data/units-v1/
  parser.py     extracción de (valor, unidad) de la respuesta final
  verifier.py   verify(spec, completion) -> estado; reward(prompt, completion) -> float
  evaluate.py   run (Ollama) / score; métricas pass@k
  derive.py     sft.jsonl y dpo.jsonl desde ejecuciones sobre train
tests/          generador, verificador (equivalencias y ataques), métricas y derive
data/units-v1/  train/eval/test.jsonl + manifest.json (sha256)
runs/           salidas de inferencia (no versionadas salvo las del informe)
spikes/         experimentos de selección de tema; congelados, no se editan
docs/           decisiones, temas y notas
```

## Diseño del entorno

**Tareas.** Cada *instancia física* (familia + parámetros enteros) se presenta
en tres niveles con la misma respuesta física: `easy` (todo en SI), `medium`
(una conversión de entrada), `hard` (conversiones de entrada y unidad de salida
no SI). Familias actuales: rapidez `v=d/t`, energía cinética `E=0.5*m*v^2`,
luminosidad `L=4*pi*d^2*F`. Fórmula y factores de conversión van en el prompt:
el problema es de razonamiento, no de memorización. La referencia se calcula
por código (`units.solve`).

**Splits sin fuga.** El split de una instancia es `sha256(familia, base) % 10`
(70/20/10): no depende de la semilla, así que train/eval regenerados nunca tocan
test, y los tres niveles de una instancia siempre caen juntos.
`write_dataset` se niega a sobrescribir un split que cambió. **Test se congela:**
no mirar sus resultados para ajustar nada.

**Prompt.** Termina con un bloque `DATOS: {json}` con los mismos datos del
enunciado (sin la respuesta). `reward` recalcula la referencia desde ahí, así que
otros grupos pueden usarlo sin nuestros archivos.

**Política del verificador** (decidida el 2026-11-07, ver decisiones):

| Caso | Resultado |
| --- | --- |
| Valor dentro del 1% en la unidad pedida o un alias (`kph`, `km h^-1`, `kilómetros por hora`, `Km/h`) | `correct` |
| JSON, Markdown, LaTeX (`\boxed`, `\times 10^{-6}`, `\cdot`), superíndices (`10⁻⁶`), coma decimal, número en palabras (`cuarenta m/s`) | se interpreta |
| Cantidad equivalente en **otra** unidad (pide km/h, responde m/s) | `unit` (0) |
| Varias respuestas, alternativas (`o`, `entre … y …`), cantidad final antes del JSON | `unparsed` (0) |
| Coma con exactamente 3 dígitos (`1,000`, `41,879`): ¿miles o decimal? | `unparsed` (0) |
| Punto: siempre decimal (`3.380` = 3.38; el prompt lo fija) | según valor |
| Sin unidad, expresión sin evaluar (`110/5 m/s`), `<think>` sin cerrar, JSON con claves extra/duplicadas | `unparsed` (0) |
| Más de 4000 caracteres | `too_long` (0) |

Nunca se buscan en el desarrollo números que coincidan con la referencia ni se
ejecuta código del modelo. Cada fila tiene pruebas en `tests/test_verifier.py`.

## Pendientes para la entrega

Reparto sugerido (ver [plan](docs/2026-11-07_205307_plan-entrega.md)):

1. **Línea base:** `qwen3:1.7b`, `llama3.2:1b`, `qwen2.5:1.5b` y un modelo
   mayor (`qwen3:4b`/`qwen3:8b`) sobre `eval` (y `test` una sola vez al final),
   `--samples 4`. Reportar pass@1/pass@4 por nivel **y** familia×nivel.
2. **Datos derivados:** profesor sobre `train`, `derive`, auditar ~20 trazas a mano.
3. **Profundidad/calibración:** el spike mostró rapidez/energía en techo y
   luminosidad-hard en piso. Agregar familias o composición (fórmulas
   encadenadas, despejar una variable, datos distractores, prefijos SI) en
   `units.FAMILIES` + `generator.variants`, y regenerar como `units-v2`.
4. **Informe:** problema, generación, splits, ejemplos, robustez (tabla de
   arriba + casos de prueba), calibración y debilidades.

## Reproducibilidad

- Tareas con ID, versión, split, parámetros base y sha256 en el manifiesto.
- `run` guarda modelo, semillas, opciones, commit y respuestas crudas; `score`
  re-verifica siempre con el verificador actual y registra su hash. Reportar
  resultados finales con la versión final del verificador.
- SFT/DPO exclusivamente desde train; DPO empareja respuestas del mismo prompt y
  no usa `unparsed` como rechazada.
- No subir secretos ni pesos. Una rama por cambio; revisar antes de integrar.

# Razonamiento cuantitativo con unidades

Fecha del experimento: 2026-11-05, America/Santiago.

## Resultado

Qwen3-1.7B tiene aciertos y errores cuantitativos reales en este conjunto: **193 respuestas correctas y 77 valores incorrectos sobre 270 intentos**, después de revisar contextualmente los cinco casos no interpretados por el parser. pass@1 estimado: **71.48%**. pass@3: **85.56%**, equivalente a 77/90 problemas con al menos un acierto.

La señal respalda continuar con el problema como candidato para el desafío. No demuestra que entrenar vaya a mejorarlo ni completa la entrega. Un resultado correcto escrito con Markdown no es un fallo matemático. Perder un exponente y cambiar la magnitud del resultado sí lo es.

## Tareas y protocolo

Se generan diez instancias físicas por familia (velocidad, energía cinética y luminosidad), cada una en tres variantes: sin conversiones, una conversión y tres conversiones entre entrada y salida. Son 90 tareas agrupadas en 30 tríos por `pair_id`. Dentro de cada trío se conservan magnitudes físicas y fórmula; las fórmulas y equivalencias se entregan en el prompt. La referencia se calcula por código y no se envía al modelo.

Los niveles son hipótesis que se contrastan con los aciertos observados. También cambian la representación numérica y la unidad de salida, por lo que el diseño no aísla causalmente una única fuente de dificultad. Las variantes de un trío no son problemas físicos independientes; deben mantenerse juntas al crear particiones.

Cada modelo responde tres veces por tarea: 540 respuestas entre ambos. Dataset con semilla 43; inferencia con semillas 42, 43 y 44, temperatura 0.7, `think=false`, contexto 4096, hasta 1024 tokens, un turno y sin esquema JSON forzado. No hubo truncamientos. Las tareas son idénticas byte a byte y la evaluación usa el mismo código.

Ollama 0.18.0, Python 3.12.13, NVIDIA RTX 3050 Laptop de 6 GB. Qwen3-1.7B usa Q4_K_M; Llama 3.2-1B usa Q8_0. Los metadatos de Qwen reportan 2.0B y los de Llama 1.2B; se mantienen las etiquetas comerciales de los modelos. [Entorno](results/environment.json), [tareas](results/tasks.jsonl) y [comparación](results/comparison.json).

## Corrección e interpretación

El parser extrae una cantidad y unidad terminales sin consultar la referencia. El verificador admite equivalencias y tolerancia relativa del 1%. Los estados distinguen valor incorrecto (`numeric`), unidad fuera del catálogo (`unit`) y respuesta sin interpretar (`unparsed`). El último no demuestra un error de razonamiento.

Cada respuesta guarda la clasificación automática y el resultado final. Una extracción contextual documentada permite resolver un caso no interpretado; vuelve a pasar por la misma comparación numérica y conserva evidencia y hash del texto revisado. No se modifica la referencia ni se ejecuta texto del modelo.

| Modelo | Aciertos automáticos /270 | Valor incorrecto automático | Unidad fuera del catálogo | Sin interpretar | Cobertura automática |
| --- | --- | --- | --- | --- | --- |
| Qwen3-1.7B | 191 | 74 | 0 | 5 | 98.15% |
| Llama 3.2-1B | 32 | 97 | 26 | 115 | 57.41% |

| Modelo | Cotas automáticas pass@1 | Cotas automáticas pass@3 |
| --- | --- | --- |
| Qwen3-1.7B | 70.74%–72.59% | 85.56%–85.56% |
| Llama 3.2-1B | 11.85%–54.44% | 24.44%–85.56% |

Se estima pass@k como `1 - C(n-c,k)/C(n,k)` por problema y se promedia. Con n=3, pass@3 indica si alguno de los tres intentos acertó. La cota inferior usa solo aciertos verificados y la superior considera correctos todos los casos sin interpretar. Son cotas por falta de interpretación, no intervalos de confianza.

Los 115 casos pendientes de Llama no se revisaron todos manualmente: incluyen unidad omitida, texto no soportado o ausencia de respuesta inequívoca. **11.85% no es una estimación puntual de su exactitud matemática.** Sus 26 casos `unit` corresponden a dimensiones incompatibles con luminosidad. Las respuestas en kW se convierten a W y se evalúan por su valor.

## Revisión contextual de Qwen

Se revisaron los cinco casos que el parser no interpretó, incluyendo aciertos y errores. Dos resultan correctos y tres contienen valores incorrectos. La extracción y su justificación están integradas en [responses.jsonl](results/qwen3-1.7b/responses.jsonl); las métricas automáticas y finales están en [summary.json](results/qwen3-1.7b/summary.json).

| Caso | Muestra | Cantidad interpretada | Resultado final | Motivo de revisión |
| --- | --- | --- | --- | --- |
| `energy-09-medium` | 1 | 4384 J | Correcto dentro del 1% | JSON sin unidad; el desarrollo la declara. |
| `luminosity-04-easy` | 1 | 2.75232e-5 W | Incorrecto | Cantidad y unidad en líneas separadas con LaTeX. |
| `luminosity-05-easy` | 2 | 0.006191 W | Incorrecto | Repite exactamente el mismo JSON. |
| `luminosity-09-easy` | 0 | 6.54846139066154e-4 W | Correcto | Expresión aritmética explícita sin evaluar. |
| `luminosity-09-hard` | 0 | 4173.568 erg/s | Incorrecto | Unidad reiterada tras punto y coma. |

La revisión contextual deja 193 aciertos y 77 errores numéricos, con todas las respuestas del objetivo interpretadas. No comparar su 71.48% final con el 11.85% automático de Llama como si tuvieran el mismo procedimiento. La comparación automática aplica el mismo parser a ambos modelos; la revisión del objetivo se identifica aparte.

## Dificultad observada del modelo objetivo

Resultados finales de Qwen, incluida la revisión contextual:

| Nivel propuesto | Correctas /90 respuestas | pass@1 | pass@3 |
| --- | --- | --- | --- |
| Fácil | 76 | 84.44% | 100.00% |
| Medio | 69 | 76.67% | 90.00% |
| Difícil | 48 | 53.33% | 66.67% |

| Familia | Correctas /90 respuestas | pass@1 | pass@3 |
| --- | --- | --- | --- |
| Velocidad | 82 | 91.11% | 96.67% |
| Energía cinética | 83 | 92.22% | 96.67% |
| Luminosidad | 28 | 31.11% | 63.33% |

La caída agregada concuerda con los niveles propuestos en esta muestra. Velocidad y energía están cerca del techo con estas plantillas. Luminosidad ofrece mayor margen y varios problemas se resuelven solo en algunos intentos: permite investigar notación científica y conversiones, sin garantizar mejora mediante entrenamiento.

## Errores de razonamiento observados

Ejemplos del conjunto vigente; las muestras se numeran desde cero. Las categorías describen lo observado en cada traza, no se deducen automáticamente del estado `numeric`.

| Modelo y caso | Evidencia | Tipo de fallo |
| --- | --- | --- |
| Qwen, `speed-01-hard`, muestra 1 | Convierte 0.183333333333 min en 183.333 s en lugar de aproximadamente 11 s. Entrega 9.9 km/h frente a 165.6 km/h. | Conversión incorrecta y propagación al resultado. |
| Qwen, `energy-00-hard`, muestra 2 | Convierte correctamente masa y velocidad, pero evalúa `0.5*29*729` como 1458 J en lugar de 10570.5 J. | Aritmética incorrecta. |
| Qwen, `luminosity-00-easy`, muestra 2 | Afirma `4*pi*36 = 48*pi` y termina en 754 W frente a 2.26195e-6 W. | Aritmética y pérdida de exponente. |
| Qwen, `luminosity-05-easy`, muestra 2 | Sustituye el flujo 4.1e-8 por 4.1e-7 W/m². | Sustitución incorrecta de un dato. |
| Llama, `speed-00-medium`, muestra 1 | Calcula tiempo/distancia y entrega 0.25 m/s frente a 4 m/s. | Selección incorrecta de la operación. |
| Llama, `luminosity-00-easy`, muestra 1 | Reemplaza la fórmula explícita por flujo×distancia y termina en J en vez de W. | Fórmula y dimensión incorrectas. |

Un resultado aceptado no certifica los pasos: 4384 J frente a 4394 J se acepta por tolerancia, aunque la multiplicación del desarrollo sea incorrecta. No usar estas trazas como SFT solo porque obtuvieron una recompensa positiva.

## Qué falta para la entrega

El [enunciado](../../DesafioInvestigacion-2026.pdf) exige un entorno y dataset completos. Este spike aporta generación verificable, calibración exploratoria y evaluación local con múltiples muestras.

| Requisito | Evidencia disponible | Pendiente |
| --- | --- | --- |
| Problema con aciertos y errores reales | 193 aciertos y 77 errores numéricos del objetivo. | Ampliar diversidad y composición de fórmulas en familias cercanas al techo. |
| Tareas con dificultad y particiones | 90 variantes pareadas y métricas por familia/nivel. | Crear train/eval/test independientes y congelar test tras calibrar. |
| Verificador robusto | Equivalencias, categorías separadas y pruebas adversariales. | Ampliar notaciones y reducir intervención manual sin convertir formato en objetivo. |
| Línea base | Dos modelos locales, pass@1/pass@3, cobertura y cotas. | Incorporar una referencia de frontera con el mismo protocolo. |
| Harness interoperable | Prototipo autocontenido. | Integrar `reward(prompt, completion) -> float` en el entorno elegido. |
| Datos SFT y DPO | Respuestas completas y ejemplos cualitativos. | Generar trazas de un modelo abierto mayor sobre train, verificar pasos y resultado, y emparejar respuestas del mismo problema para DPO. |

El entrenamiento corresponde al proyecto posterior. No convertir este conjunto exploratorio en train y después presentarlo como test independiente. Aumentar el número de instancias de tres plantillas tampoco resuelve por sí solo originalidad y profundidad.

## Validación y límites

Diez pruebas sin modelos: generación, referencias recalculadas desde los 90 prompts, equivalencias, formatos, entradas adversariales, métricas, integridad/completitud, revisiones contextuales, conservación de prompts/semillas y resultados guardados. Ruff y MyPy pasan. Bandit no encuentra hallazgos medios/altos excluyendo B310: la llamada señalada usa una URL HTTP fija en localhost. [Comandos de reproducción y comprobación](README.md).

Muestra pequeña, tres intentos, tríos relacionados y pocas plantillas. Los modelos difieren en familia, tamaño y cuantización; no se atribuyen los errores causalmente a esas variables ni a `think=false`. No se probó entrenamiento ni razonamiento extendido. El conjunto se usó para desarrollar y calibrar el verificador; no es un test independiente congelado.

# Spikes exploratorios

Evaluaciones para comparar temas; no cambian el tema acordado ni sustituyen los entregables del PDF.

| Spike | Evidencia |
| --- | --- |
| [Unidades](units/README.md) | [Informe](units/report.md), 90 tareas y 540 respuestas existentes; 10 tests y check pasaron; sin inferencia nueva. |
| [Scheduling](scheduling/README.md) | [Informe](scheduling/report.md): 90 tareas, 540 respuestas; parser revisado con historial, tests y check. |
| [Text-to-SQL con bases ocultas](text_to_sql/README.md) | [Informe](text_to_sql/report.md): 90 tareas, 540 respuestas, tests y check. |
| [Reparación de bases con herramientas](database_repair/README.md) | [Informe](database_repair/report.md): 90 bases, 540 trayectorias, tests y check. |
| [Buscaminas deductivo](minesweeper/README.md) | [Informe](minesweeper/report.md): 90 tableros, 540 respuestas; parser revisado con historial y check. |
| [Laberinto cooperativo](cooperative_maze/README.md) | [Informe](cooperative_maze/report.md): 90 mapas, 540 respuestas; parser revisado con historial, tests y check. |

Comparar calibración, robustez, diversidad, originalidad y costo; mayor exactitud no implica mejor tema para entrenar. Mantener resultados automáticos separados de revisiones manuales.

## Cola local

`scripts/run_spikes.py` ejecuta scheduling → SQL → reparación → Buscaminas → laberinto, un modelo a la vez; omite corridas completas tras conservar sus artefactos. Estado local en `spikes/queue/status.json`, salida en `spikes/queue/run-*.log`; estos archivos operativos no se versionan. Se inició como proceso separado para que una interrupción del chat no corte la inferencia. Al completar cada corrida, `scripts/report_spikes.py` actualiza su informe desde métricas guardadas. Reanudar la cola: `rtk proxy .venv/bin/python -u scripts/run_spikes.py`. Un lock evita dos colas simultáneas. Si un spike queda parcial sin reanudador, se detiene y conserva evidencia.

<!-- COMPARISON_START -->
## Comparación automática

Éxito verificable con 90 tareas y tres muestras por tarea/modelo. Cada fila tiene su propio problema y protocolo; no es un ranking general de capacidad.

| Tema | Qwen pass@1 / pass@3 | Cobertura Q | Llama pass@1 / pass@3 | Cobertura L | Minutos Q / L |
| --- | --- | --- | --- | --- | --- |
| [Unidades](units/report.md) | 70.74% / 85.56% | 98.15% | 11.85% / 24.44% | 57.41% | 12.4 / 12.1 |
| [Scheduling](scheduling/report.md) | 22.59% / 35.56% | 61.11% | 0.00% / 0.00% | 15.93% | 60.2 / 36.7 |
| [SQL](text_to_sql/report.md) | 33.33% / 33.33% | 99.63% | 2.22% / 6.67% | 99.63% | 3.2 / 3.8 |
| [Reparación](database_repair/report.md) | 0.00% / 0.00% | 85.56% | 0.00% / 0.00% | 0.00% | 7.9 / 15.7 |
| [Buscaminas](minesweeper/report.md) | 10.74% / 23.33% | 34.07% | 0.37% / 1.11% | 0.74% | 10.7 / 16.6 |
| [Laberinto](cooperative_maze/report.md) | 0.74% / 2.22% | 31.11% | 0.00% / 0.00% | 45.56% | 55.7 / 33.5 |

La tabla usa exclusivamente métricas automáticas. Unidades conserva aparte cinco revisiones contextuales de Qwen: su resultado final 193/270 no se mezcla con el automático 191/270 ni con Llama sin revisión. unparsed no demuestra un error matemático; en Buscaminas incluye coordenadas equivocadas. Ver informes para categorías y límites.

Costo orientativo: unidades suma duración del backend; los otros temas suman tiempo de los intentos con respuesta, incluyendo herramientas cuando existen. Se excluyen verificaciones posteriores, pausas y llamadas abortadas sin respuesta. Reparación usa hasta cuatro llamadas por trayectoria; los otros protocolos son de un turno. Hardware/velocidad y cuantización difieren; no atribuir diferencias causalmente a una sola variable.

Temperatura 0.7, semillas 42/43/44, think=false, contexto 4096 y hasta 1024 tokens por llamada. Mismos problemas para ambos modelos dentro de cada tema. Los pilotos usan otras tareas (semilla 99); no entran en estas métricas.
<!-- COMPARISON_END -->

## Lectura para elegir temática

Los cinco spikes nuevos están completos: 450 tareas y 2700 intentos, más 540 respuestas existentes de unidades. Reparación contiene trayectorias de varias llamadas; contar intentos no equivale a contar llamadas. Esta evidencia explora modelos sin entrenamiento y no mide cuánto aprenderían después.

| Tema | Calibración observada | Profundidad y diversidad actuales | Robustez y principal límite |
| --- | --- | --- | --- |
| Unidades | Qwen tiene aciertos y errores con cobertura alta; Llama ofrece otro rango de dificultad. | Solo tres familias de fórmulas; ampliar composición de operaciones y dimensiones. | Verificador numérico con unidades y revisiones identificadas. Las mismas 30 parejas físicas aparecen en tres niveles: agrupar por pair_id al separar particiones. |
| Scheduling | Qwen: 56/90 fáciles, 5/90 medias, 0/90 difíciles. Hay 61 aciertos y 104 violaciones interpretadas en total. | Dependencias, recursos y holguras admiten más combinaciones y soluciones alternativas. | Se verifica factibilidad completa; cobertura y 117 truncamientos de Qwen confunden parte de la dificultad. Ajustar especialmente el nivel medio. |
| SQL | Qwen: 90/90 fáciles y 0/90 en cada nivel restante; el promedio 33% oculta techo/suelo. | Cuatro familias sobre un esquema fijo; ampliar esquemas y escalones de dificultad. | Cuatro bases detectan 18 consultas Qwen y 17 Llama que pasan visible y fallan ocultas. Oracle finito y subconjunto SQLite documentado, sin equivalencia universal. |
| Reparación | Ningún parche completo correcto; tampoco aciertos en controles limpios. | Combina consulta, detección y parche; tres tablas fijas y dependencia del protocolo. | Preserva celdas correctas y fuentes autoritativas. Falta señal positiva observada; simplificar el currículo y diagnosticar protocolo antes de elegirlo para entrenamiento. |
| Buscaminas | Qwen pass@1 inferior al baseline constante de 1/3; niveles no ordenados por acierto. | Combina pistas con solver exacto; tamaño y clase no garantizan dificultad cognitiva. | Coordenadas incorrectas explican gran parte de unparsed. Clasificación de tres opciones permite azar: acertar etiqueta no certifica razonamiento. |
| Laberinto | Dos respuestas Qwen correctas, ambas fáciles; ninguna Llama. | BFS y cooperación obligatoria dan profundidad, pero pocas estructuras de mapas. | Simulación completa y acciones inválidas preservadas. Cobertura baja y 150/50 truncamientos Qwen/Llama: presupuesto y representación requieren recalibración. |

**Recomendación para esta entrega: desarrollar unidades como razonamiento dimensional de varios pasos.** Ofrece la evidencia de calibración más clara: cobertura Qwen 98.15%, sin truncamientos y errores numéricos comprobados, además de aciertos. Su alcance estrecho exige ampliar la profundidad; su mayor exactitud no basta para elegirla. Scheduling es la segunda opción si priorizan investigación en planificación y mantiene el tema ya acordado: hay señal positiva, fallos de restricciones y espacio para graduar dependencias, pero primero debe suavizarse la transición fácil→medio y reducirse la pérdida por formato y truncamiento. Esta recomendación no modifica la decisión del equipo.

SQL sería una tercera opción por su bajo costo observado y buena cobertura, tras romper el patrón techo/suelo. Reparación, Buscaminas y laberinto requieren mayor recalibración con estos modelos antes de comprometer la entrega a cualquiera de ellos. Esta priorización combina evidencia práctica, costo y potencial de profundidad; no demuestra aprendibilidad ni originalidad académica.

Según los criterios del [PDF](../DesafioInvestigacion-2026.pdf), la originalidad de ninguno queda acreditada por este experimento: el aporte deberá concretarse en generación, composición de restricciones, controles adversarios y generalización. La robustez tiene pruebas y límites documentados por tema; aún falta validarla sobre datos independientes. Los parsers de scheduling, Buscaminas y laberinto se revisaron después de observar respuestas y preservan historial: estos resultados son exploratorios, no un test final congelado.

### Por qué unidades encaja mejor con el desafío

La sección I del PDF exige un problema que el modelo pequeño resuelva a veces, con corrección calculable por código; no pide maximizar el error ni presentar únicamente un porcentaje medio atractivo. En unidades, las tres dificultades tienen tanto aciertos como errores: Qwen obtiene automáticamente 75/90, 68/90 y 48/90 respuestas correctas. La revisión contextual separada da 76/90, 69/90 y 48/90, con 77 errores numéricos comprobados en total. Es una señal más clara que el techo/suelo de SQL o el suelo de reparación y laberinto.

Un diagnóstico adicional cuenta cuántas de las tres muestras Qwen aciertan por tarea, usando exclusivamente etiquetas automáticas:

| Tema | 0 aciertos | 1 acierto | 2 aciertos | 3 aciertos | Tareas con acierto y fallo verificados entre sus muestras |
| --- | --- | --- | --- | --- | --- |
| Unidades | 13 | 16 | 8 | 53 | 24 |
| Scheduling | 58 | 11 | 13 | 8 | 21 |
| SQL | 60 | 0 | 0 | 30 | 0 |
| Reparación | 90 | 0 | 0 | 0 | 0 |
| Buscaminas | 69 | 16 | 2 | 3 | 10 |
| Laberinto | 88 | 2 | 0 | 0 | 0 |

La última columna exige al menos un correct y al menos un fallo interpretable en la misma tarea; unparsed por sí solo no sirve como respuesta incorrecta certificada. Las cifras se recalculan desde responses.jsonl y no son datos DPO generados. Tres muestras no permiten estimar de forma fiable la probabilidad de éxito de cada problema ni garantizan mejora con RL. Unidades y scheduling ofrecen una franja de resultados mixtos observada; la mayor cobertura de unidades reduce la confusión entre formato y razonamiento.

| Criterio del PDF | Qué respalda unidades | Qué falta para cumplirlo bien |
| --- | --- | --- |
| Originalidad | Permite estudiar composición de conversiones, exponentes y consistencia dimensional con errores verificables. | Las tres fórmulas actuales son clásicas. Aportar un generador de composiciones y controles nuevos; aumentar instancias de las mismas plantillas no basta. |
| Profundidad | Tres niveles y una caída de éxito observada; luminosidad presenta margen especialmente amplio. | Diversificar operaciones, variables desconocidas y cadenas de dependencias. Crear train/eval/test sin compartir pair_id ni copias de una misma instancia física. |
| Robustez | Acepta unidades equivalentes, notación científica y tolerancia documentada; pruebas adversariales y separación entre parser y referencia. | Ampliar formatos sobre validación, fijar el parser antes de test y revisar sensibilidad a la tolerancia del 1%. La corrección del resultado no certifica los pasos. |
| Calibración | Errores numéricos reales, aciertos en cada nivel, buena cobertura y cero truncamientos del objetivo. | Recalibrar familias cercanas al techo, evaluar instancias nuevas y una referencia abierta de mayor capacidad. No se probó aprendibilidad mediante entrenamiento. |

Además falta exponer `reward(prompt, completion) -> float` en unidades: hoy dispone de `verify(task, completion)`, no de la interfaz común. Los cinco spikes nuevos sí exponen reward, aunque SQL y reparación usan un registro de prompts de las tareas congeladas; deberán aceptar el futuro dataset completo al integrar train/eval/test. Son prototipos para selección, no entornos finales interoperables.

Para llevar el candidato a la entrega: integrar la interfaz común sin incorporar revisiones manuales a reward; ampliar generación y calibrar solo sobre piloto/eval; separar y congelar test; evaluar un modelo abierto mayor con el mismo protocolo; generar sobre train trazas SFT verificadas y pares DPO de un mismo problema, identificando modelo y procedimiento. El PDF exige esos datos en esta etapa, mientras que entrenar corresponde al proyecto posterior. No se generaron esos datos en esta sesión.

## Verificación y trabajo posterior

50 pruebas automatizadas pasan. Los seis checks recalculan métricas y comprueban integridad sin modelos; pilotos y versiones históricas usan su evaluador correspondiente. Ruff y MyPy pasan para los cinco spikes nuevos y scripts. Bandit sin hallazgos medios/altos tras revisar y excluir B310: los evaluadores usan una URL fija de Ollama en 127.0.0.1. Las reevaluaciones verifican que solo cambie status; las dos reanudaciones de scheduling conservan byte a byte sus prefijos de inferencia.

No hubo commits, inferencias pagadas ni cambios en los artefactos existentes de unidades. Pendientes del proyecto final: ampliar y calibrar el tema elegido con un piloto nuevo, crear particiones independientes agrupando familias/instancias relacionadas, congelar un test nuevo con parser fijo, ejecutar baseline de frontera y preparar/validar SFT/DPO exclusivamente desde train. No se generaron datos de entrenamiento ni se entrenó en esta sesión. Comprobar manualmente la calidad de las trazas antes de usarlas como supervisión: una respuesta final correcta no valida su explicación.

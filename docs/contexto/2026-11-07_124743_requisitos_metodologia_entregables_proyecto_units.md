# Plan del proyecto de requisitos metodología y entregables para units

Fecha: 2026-11-07, America/Santiago.

**Etapa: Proyecto de Investigación.** El proyecto utiliza un entorno y dataset del desafío para entrenar un LLM pequeño y comparar estrategias de postentrenamiento. Para el tema seleccionado, **razonamiento cuantitativo con unidades**, debe estudiar cómo cambian el rendimiento, la generalización y la fiabilidad de las respuestas al aplicar distintas estrategias sobre un mismo entorno y con cómputo comparable.

Este plan responde qué se pide, cómo desarrollarlo y qué entregar. Distingue requisitos explícitos de propuestas metodológicas. Es solo planificación: no registra entrenamientos ni resultados nuevos. Las casillas permanecen abiertas hasta contar con evidencia de cumplimiento.

Actualización de contexto, 2026-11-09: los pendientes del desafío de la sección 4
describen el estado exploratorio original y ya no son el estado vigente. Para
la primera entrega del proyecto, consultar los [requisitos y decisiones actuales](2026-11-09_202333_requisitos_entrega_1_proyecto.md)
y su [plan de ejecución](../plans/2026-11-09_202333_entrega_1_proyecto.md).

Fuente normativa: [ProyectoCurso-2026.pdf](../../ProyectoCurso-2026.pdf). Las páginas citadas corresponden al PDF, incluida su primera página sin número impreso. Antecedentes: [plan del desafío](2026-11-07_123729_requisitos_metodologia_entregables_units.md), [spike de unidades](../../spikes/units/README.md) e [informe exploratorio](../../spikes/units/report.md).

## 1 Qué se pide

### Objetivo y alcance de esta etapa

Entrenar un modelo pequeño para mejorar razonamiento o uso de herramientas y comparar estrategias de entrenamiento. Se puede usar el entorno propio del desafío o uno compartido por compañeros, mantener el grupo o cambiarlo, con un máximo de cuatro personas. El foco es el **postentrenamiento**, no el preentrenamiento. [PDF, introducción, p. 1; sección 2, p. 2](../../ProyectoCurso-2026.pdf#page=1).

### Separación entre desafío y proyecto

| Aspecto | Desafío de Investigación | Proyecto de Investigación |
| --- | --- | --- |
| Objetivo | Construir entorno, dataset y evidencia de que pueden sustentar entrenamiento posterior. | Entrenar y comparar estrategias sobre un entorno y dataset disponibles. |
| Harness y verificador | Diseñarlos, implementar la interfaz y analizar robustez. | Utilizarlos, detectar problemas durante el entrenamiento, corregirlos y documentar sus efectos. |
| Datos SFT y DPO | Generar y entregar trazas y pares con su procedencia y filtrado. | Utilizarlos para entrenar las estrategias correspondientes y documentar su uso. |
| Línea base | Comparar varios modelos, incluido el objetivo y referencias de frontera. | Medir el modelo inicial sin ajuste adicional como control de los caminos de entrenamiento. |
| Experimentos | Inferencia para evaluar robustez y calibración del entorno. | SFT, SFT seguido de RL, solo RL y DPO, comparados con el control sin ajuste. |
| Evaluación | pass@1 y pass@k por dificultad, ejemplos y análisis de calibración. | pass@1 y pass@k por dificultad, análisis de resultados, sensibilidad y auditoría manual de trazas exitosas. |
| Entrega | Código, descripción del entorno y dataset, datos derivados e informe de línea base. | Propuesta inicial, informe de avance y entrega final con paper, poster y video de presentación oral. |

Las obligaciones del desafío no se trasladan automáticamente como nuevos entregables formales del proyecto. Por ejemplo, el proyecto no vuelve a exigir explícitamente una comparación de modelos de frontera. Sí necesita una línea base del modelo antes de entrenar.

### Requisitos explícitos y aplicación a unidades

| ID | Lo que exige el proyecto | Aplicación al tema seleccionado | Fuente |
| --- | --- | --- | --- |
| P1 | Comparar cinco caminos sobre un mismo entorno y con presupuesto de cómputo comparable. | Usar el entorno de unidades para contrastar el modelo inicial, solo SFT, SFT seguido de RL, solo RL y DPO. | Introducción, p. 1 |
| P2 | Entrenar un LLM pequeño en razonamiento o herramientas. | Partir de un mismo checkpoint pequeño y estudiar cambios en resolución cuantitativa con unidades. | Introducción, p. 1 |
| P3 | Documentar el ciclo de iteración: problemas, correcciones del entorno o verificador y efecto del reentrenamiento. | Registrar falta de señal, errores de extracción o explotación de tolerancias y cómo se trataron. | Introducción, p. 1; sección 4, p. 3 |
| P4 | Reportar todos los resultados finales con la versión final del verificador. | Aplicar el mismo verificador final a las salidas de los cinco caminos para asegurar comparabilidad. | Introducción, p. 1 |
| P5 | Auditar manualmente una muestra de trazas exitosas para estimar cuántos aciertos son genuinos. | Revisar respuestas recompensadas y sus pasos, distinguiendo resolución válida de acierto aparente o explotación del verificador. | Introducción, p. 1 |
| P6 | Utilizar pass@1 y pass@k por dificultad; en lo posible probar varias semillas. | Reportar métricas por nivel del dataset de unidades y variación entre semillas si los recursos lo permiten. | Introducción, p. 1 |
| P7 | Sustentar el estudio con análisis de resultados, sensibilidad, visualizaciones, casos de prueba y comparación con alternativas, especialmente para los niveles 1 y 2. | Diseñar un análisis de factores que afecten el aprendizaje y casos que muestren fortalezas y fallos. | Sección 1, pp. 1–2 |
| P8 | Entregar propuesta inicial e informe de avance con sus mínimos requeridos. | Formular pregunta, bibliografía y entorno; después presentar implementación inicial, control sin entrenar y curvas iniciales. | Sección 3, pp. 2–3 |
| P9 | Entregar paper de máximo 7 páginas a doble columna, sin contar referencias, con las secciones indicadas. | Documentar investigación, métodos, resultados, iteraciones y conclusiones del trabajo sobre unidades. | Sección 4, p. 3 |
| P10 | Entregar poster y presentación oral en video. | Comunicar pregunta, diseño, comparación, resultados y conclusiones. | Secciones 3–4, p. 3 |

**RL en los cinco caminos:** el enunciado usa la expresión RLVR/GRPO/PPO. Este plan propone elegir y justificar una implementación de RL con recompensa verificable para las ramas con RL; no interpreta la expresión como una obligación de ejecutar por separado todos esos algoritmos. SFT seguido de RL y solo RL sí son caminos distintos que deben compararse.

**Semillas:** probar varias se solicita «en lo posible», por lo que se conserva como recomendación condicionada a recursos. La auditoría manual y el uso del verificador final sí se solicitan explícitamente.

### Nivel de complejidad y preguntas de investigación

El PDF presenta cinco niveles posibles, de complejidad creciente; no son cinco trabajos acumulativos:

1. Estudiar un método existente con código público, con análisis bajo distintas condiciones, sensibilidad y casos de prueba.
2. Implementar un método existente sin código público y analizarlo de forma equivalente.
3. Proponer una mejora incremental y compararla con el algoritmo base.
4. Realizar una innovación mayor o desarrollar un método nuevo.
5. Realizar un estudio teórico sustentado por bibliografía e información pertinente.

El enunciado indica que un buen trabajo en cualquiera de ellos puede obtener buena calificación. Para units se propone inicialmente el **nivel 1**, reutilizando implementaciones existentes y concentrando el esfuerzo en la comparación y el análisis experimental. No hace falta proponer un algoritmo nuevo para este enfoque. Una eventual ruta teórica requeriría acordar con el curso cómo se articula con la comparación experimental central; no se adopta en este plan.

Las preguntas de la introducción orientan la investigación, pero no constituyen una lista de experimentos independientes obligatorios. Pregunta principal propuesta: **¿cómo influye el SFT previo en el aprendizaje con RL de problemas cuantitativos con unidades, frente a solo RL, solo SFT y DPO, bajo un presupuesto comparable?** Generalización y reward hacking pueden incorporarse como análisis complementarios delimitados.

### Aspectos que el PDF no fija

No fija modelo, algoritmo concreto de RL, cantidad de tareas o entrenamientos, k, número de semillas, tamaño de auditoría manual, hiperparámetros, duración del video ni dimensiones del poster. Tampoco define una unidad exacta de presupuesto comparable. Deben acordarse y justificarse.

LoRA, Colab y las bibliotecas citadas son opciones prácticas, no tecnologías obligatorias. El acceso a Peteroa con H100 requiere justificación y coordinación según las indicaciones del curso; no se presupone disponible. El PDF no enumera código ni pesos como entregables finales separados: conservarlos es una propuesta de reproducibilidad, sujeta a otras instrucciones que publique el curso.

## 2 Cómo debe desarrollarse

La siguiente secuencia es una **propuesta metodológica**, aplicada a units. Los compromisos explícitos se identifican en P1–P10; la organización experimental concreta se propone para poder cumplirlos y revisarlos.

### Paso 1 Formular la propuesta y elegir el enfoque

- [ ] Confirmar grupo, entorno y checkpoint inicial del modelo pequeño.
- [ ] Adoptar o ajustar la pregunta principal y justificar su relevancia.
- [ ] Seleccionar el nivel de complejidad; para el nivel 1, identificar implementaciones existentes de SFT, RL y DPO.
- [ ] Revisar bibliografía pertinente, incluyendo al menos dos trabajos relevantes que puedan sustentar el paper final.
- [ ] Delimitar hipótesis y resultados que permitirían apoyarlas o cuestionarlas, sin asumir que entrenar necesariamente mejorará el rendimiento.
- [ ] Preparar la entrega 1 con bibliografía, propuesta tentativa y entorno.

**Salida del paso:** propuesta de investigación y alcance viable para el cómputo disponible.

### Paso 2 Preparar los insumos y fijar la comparación

- [ ] Disponer del harness, train/eval/test y datos SFT/DPO preparados en el desafío, o documentar el entorno compartido que se utilizará.
- [ ] Corregir las brechas que impidan entrenar o medir; no asumir que el spike equivale al entorno final del desafío.
- [ ] Mantener variantes relacionadas dentro de un mismo split y excluir test de entrenamiento, selección de hiperparámetros y ajuste del verificador.
- [ ] Definir formato de respuesta, recompensa, dificultad y criterios de evaluación de unidades.
- [ ] Fijar política de cómputo comparable: hardware, tiempo o GPU-horas, tokens procesados, pasos y límites de generación que se registrarán.
- [ ] Contabilizar ambas fases de SFT seguido de RL dentro de su presupuesto total; explicar cómo se tratan generación de datos y costos compartidos.
- [ ] Fijar muestras por tarea, k, semillas de evaluación y criterios de selección de checkpoints usando validación.

**Salida del paso:** protocolo común y tabla de condiciones. El control sin ajuste no consume presupuesto de entrenamiento; las cuatro rutas entrenadas deben tener una comparación de recursos justificada. Igual número de pasos no implica necesariamente igual costo.

### Paso 3 Medir el control e iniciar los entrenamientos

- [ ] Evaluar el checkpoint inicial sin entrenamiento adicional, con métricas por dificultad.
- [ ] Implementar una ejecución inicial de entrenamiento y comprobar que se registra la señal de recompensa.
- [ ] Guardar curvas de recompensa de los primeros entrenamientos y distinguir recompensa de entrenamiento de rendimiento en validación.
- [ ] Revisar si hay falta de señal, saturación, truncamientos o problemas de formato antes de consumir el presupuesto completo.
- [ ] Preparar la entrega 2 con implementación inicial, línea base previa al entrenamiento y curvas disponibles.

**Salida del paso:** avance que permite detectar temprano si el entorno y el entrenamiento producen una señal útil. El PDF no exige haber completado los cinco caminos para este hito.

### Paso 4 Ejecutar los cinco caminos y el análisis de sensibilidad

- [ ] Conservar el checkpoint inicial como control sin ajuste adicional.
- [ ] Entrenar y evaluar solo SFT desde ese checkpoint.
- [ ] Entrenar y evaluar SFT seguido de RL, documentando el checkpoint intermedio y el presupuesto de cada fase.
- [ ] Entrenar y evaluar solo RL desde el checkpoint inicial, sin SFT previo en el experimento.
- [ ] Entrenar y evaluar DPO; proponer el mismo punto de partida para aislar su efecto y documentar cualquier preajuste si se adopta.
- [ ] Registrar hiperparámetros, datos, semillas, cómputo, versiones y checkpoints de cada corrida.
- [ ] Realizar análisis de sensibilidad pertinente al enfoque: por ejemplo, tamaño de grupo, coeficiente KL, recompensa o mezcla de dificultades; justificar qué factores se estudian.
- [ ] Probar varias semillas si el presupuesto lo permite y declarar la limitación si se utiliza una sola.

**Salida del paso:** resultados comparables y evidencia de cómo cambian bajo las condiciones estudiadas. Los factores de sensibilidad son ejemplos del PDF, no una obligación de ejecutar todos ni de explorar una grilla exhaustiva.

### Paso 5 Auditar trazas e iterar sobre problemas reales

- [ ] Inspeccionar trazas para detectar explotación del formato, tolerancias o unidades, además de errores de razonamiento.
- [ ] Definir y documentar una muestra de trazas exitosas para auditoría manual, con criterios de selección y de acierto genuino.
- [ ] Clasificar los casos auditados y estimar la proporción de éxitos genuinos, identificando el denominador y límites del muestreo.
- [ ] Registrar cada problema detectado, versión afectada, corrección propuesta y evidencia que la motiva.
- [ ] Aplicar correcciones justificadas al entorno o verificador y reentrenar cuando corresponda al problema detectado.
- [ ] Comparar el efecto de las iteraciones y preservar las versiones anteriores para explicar el cambio.

**Salida del paso:** historial del ciclo de investigación y auditoría. En units, obtener una cantidad dentro de la tolerancia no garantiza que el desarrollo sea correcto. No se deben inventar episodios de reward hacking: si no se detectan, reportar qué se examinó y el alcance de esa observación.

### Paso 6 Evaluar todos los caminos con el verificador final

- [ ] Fijar la versión final del verificador y aplicarla a los resultados finales de todos los caminos, incluido el control.
- [ ] Recalcular recompensas desde las respuestas guardadas cuando sea suficiente; repetir inferencia si cambió la tarea o el protocolo de interacción y las salidas ya no son comparables.
- [ ] Medir pass@1 y pass@k por dificultad sobre test, con un protocolo de inferencia comparable.
- [ ] Analizar desempeño por familia y tipos de error para explicar los promedios.
- [ ] Estudiar generalización a test y, si forma parte de la pregunta adoptada, a dificultades no vistas durante el entrenamiento.
- [ ] Presentar curvas, comparación de estrategias, sensibilidad y costo; documentar variación entre semillas cuando exista.
- [ ] Distinguir recompensa automática, éxito genuino según auditoría y limitaciones de extracción.

**Salida del paso:** tablas y figuras finales con una base de evaluación común. Entrenamientos históricos pueden haber usado verificadores anteriores; sus métricas finales deben reportarse con el verificador final y sus condiciones de entrenamiento deben seguir identificadas.

### Paso 7 Preparar la comunicación y revisar el cumplimiento

- [ ] Redactar el paper con todas las secciones exigidas, sin superar siete páginas de contenido a doble columna.
- [ ] Elaborar el diagrama de bloques y explicar sus componentes.
- [ ] Preparar el poster y grabar la presentación oral en video.
- [ ] Comprobar correspondencia entre pregunta, métodos, cinco caminos, resultados, iteraciones y conclusiones.
- [ ] Verificar que cada requisito P1–P10 tenga evidencia y que cifras y versiones coincidan entre paper, poster y video.
- [ ] Revisar los templates y las instrucciones de envío publicadas por el curso antes de entregar.

**Salida del paso:** entrega final consistente con el estudio realizado y el checklist siguiente.

## 3 Qué hay que entregar

### Hitos oficiales y condiciones de plazo

| Hito | Fecha indicada | Ponderación indicada | Producto |
| --- | --- | --- | --- |
| Entrega 1 | 11 de noviembre | 5% | Informe escrito con propuesta inicial. |
| Entrega 2 | 25 de noviembre | 10% | Informe escrito de avance. |
| Entrega 3 | 9 de diciembre | 25% | Entrega final: paper, poster y presentación oral en video. |

Fuente: [PDF, sección 3, pp. 2–3](../../ProyectoCurso-2026.pdf#page=2). El encabezado fija la entrega final para el **miércoles 9 de diciembre a las 23:59**. No se explicita una hora para los hitos intermedios. Las entregas 1 y 2 admiten atraso con descuento de **1,0 punto por día**; la entrega final **no admite atraso**. Estas son las condiciones del PDF; cualquier modificación posterior debe verificarse con el curso.

### E1 Informe escrito de propuesta inicial

- [ ] Incluir revisión bibliográfica.
- [ ] Formular una propuesta tentativa de investigación.
- [ ] Identificar el entorno que se utilizará.

**Evidencia de aceptación:** están presentes los tres mínimos explícitos de la entrega 1. Como complemento propuesto, identificar modelo, cinco caminos, nivel de complejidad y presupuesto previsto permite evaluar la viabilidad. Cubre la primera parte de P8.

### E2 Informe escrito de avance

- [ ] Describir la implementación inicial del trabajo propuesto.
- [ ] Presentar la línea base del modelo antes de entrenar.
- [ ] Presentar curvas de recompensa de los primeros entrenamientos.

**Evidencia de aceptación:** se puede observar qué está implementado, cuál es el rendimiento inicial y si los entrenamientos empiezan a producir señal. Explicar dificultades y próximos ajustes es un complemento metodológico propuesto. Cubre la segunda parte de P8.

### E3 Paper final

- [ ] Utilizar formato de paper a doble columna, con máximo siete páginas sin contar las páginas de referencias.
- [ ] Incluir una introducción breve con los aspectos principales y relevancia del proyecto.
- [ ] Incluir revisión bibliográfica de al menos dos trabajos relevantes.
- [ ] Describir el proyecto con un diagrama de bloques y una explicación breve de cada bloque.
- [ ] Presentar resultados experimentales o teóricos según el enfoque; para el enfoque experimental propuesto, documentar los cinco caminos y el presupuesto comparable.
- [ ] Reportar pass@1 y pass@k por dificultad con el verificador final.
- [ ] Incluir análisis de resultados, sensibilidad, visualizaciones, casos de prueba y comparación con alternativas pertinentes al enfoque elegido.
- [ ] Describir los problemas detectados, las correcciones y su efecto durante el ciclo de iteración.
- [ ] Incorporar la auditoría manual de una muestra de trazas exitosas y la estimación de aciertos genuinos.
- [ ] Exponer las principales conclusiones, sustentadas por resultados y limitaciones.
- [ ] Incluir referencias en formato paper.
- [ ] Ajustarse al template que publique el curso y verificar las instrucciones de envío.

**Evidencia de aceptación:** el paper cubre las secciones de la sección 4 y permite evaluar los requisitos de investigación P1–P7. Cubre P9. No basta con entregar una tabla de resultados finales sin metodología, auditoría y ciclo de iteración.

### E4 Poster y presentación oral en video

- [ ] Entregar una presentación en formato poster.
- [ ] Acompañarla de una presentación oral en formato video.
- [ ] Mantener consistencia con la pregunta, los métodos, resultados y conclusiones del paper.
- [ ] Comprobar dimensiones, duración y formato de archivo en las instrucciones adicionales del curso, si se publican.

**Evidencia de aceptación:** están presentes los dos productos explícitos y comunican el estudio realizado. Cubre P10. El PDF no indica que se requiera un segundo juego de diapositivas independiente del poster.

### Artefactos de respaldo propuestos

Para poder verificar el estudio se propone conservar código y configuraciones de entrenamiento, versiones del entorno, datos o sus identificadores, checkpoints o adaptadores, logs, curvas, respuestas de evaluación y registro de auditoría e iteraciones. Son respaldo metodológico; **el PDF no los enumera como un envío separado obligatorio**. Si el curso publica requisitos adicionales de repositorio o pesos, incorporarlos al checklist.

## 4 Qué aporta units y qué sigue pendiente

Estado según el [informe del spike](../../spikes/units/report.md) y el [plan del desafío](2026-11-07_123729_requisitos_metodologia_entregables_units.md). Los resultados existentes son exploratorios y no acreditan entrenamientos del proyecto.

| Componente | Antecedente disponible | Brecha para el proyecto |
| --- | --- | --- |
| Problema y entorno | Prototipo de razonamiento cuantitativo con unidades. | Completar o adoptar el harness y los datasets necesarios para entrenar. |
| Calibración | Aciertos y errores del objetivo observados en el spike. | Confirmar que el diseño final conserva señal útil durante el entrenamiento. |
| Línea base | Comparación exploratoria de dos modelos pequeños sin ajuste adicional. | Evaluar el checkpoint inicial con el protocolo definitivo del proyecto. |
| Datos de entrenamiento | Respuestas exploratorias; SFT/DPO finales pendientes en el plan del desafío. | Disponer de datos SFT/DPO válidos y particiones independientes. |
| Cinco caminos | No hay resultados de entrenamiento documentados en el spike. | Implementar y ejecutar SFT, SFT seguido de RL, solo RL y DPO, además del control. |
| Robustez | Pruebas del verificador y límites conocidos del parser y tolerancia. | Auditar éxitos del entrenamiento y documentar correcciones e iteraciones reales. |
| Evaluación final | Métricas exploratorias y ejemplos cualitativos. | Comparar estrategias con el verificador final, sensibilidad y cómputo documentado. |
| Comunicación | Informe exploratorio del entorno. | Preparar propuesta, avance, paper, poster y video del proyecto. |

## 5 Decisiones pendientes antes de ejecutar

1. Confirmar integrantes, entorno definitivo y checkpoint inicial.
2. Adoptar el nivel de complejidad y precisar pregunta e hipótesis.
3. Elegir implementaciones de entrenamiento y algoritmo para las ramas con RL.
4. Acordar cómputo disponible y cómo comparar presupuestos entre estrategias.
5. Definir análisis de sensibilidad, semillas, k y selección de checkpoints.
6. Definir tamaño y selección de la muestra para auditoría, y criterio de acierto genuino.
7. Asignar responsables y fechas internas por hito; consultar templates e instrucciones complementarias del curso.

El desafío queda cubierto por la construcción del entorno y sus datos. El proyecto se completa con el estudio de entrenamiento y comparación, sus iteraciones y las entregas formales descritas aquí. Son dos checklists separados, aunque el primero provee los insumos del segundo.

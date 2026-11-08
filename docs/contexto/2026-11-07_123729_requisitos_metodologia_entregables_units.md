# Plan del desafío de requisitos metodología y entregables para units

Fecha: 2026-11-07, America/Santiago.

**Etapa: Desafío de Investigación.** Para el entrenamiento, la comparación de estrategias y sus entregas, consultar el [plan del proyecto de curso](2026-11-07_124743_requisitos_metodologia_entregables_proyecto_units.md). Son etapas y entregables distintos.

Esta bajada identifica los requisitos. La secuencia para realizarlos está en el [borrador del plan de ejecución](../plans/2026-11-07_130305_ejecucion_desafio_units.md).

El desafío consiste en construir un entorno y un dataset que permitan entrenar posteriormente un LLM pequeño en razonamiento o uso de herramientas. Para el tema seleccionado, **razonamiento cuantitativo con unidades**, la entrega debe demostrar que las tareas tienen respuestas calculables, que el verificador es robusto y que el modelo objetivo tiene tanto aciertos como errores aprovechables para aprender.

Este plan responde tres preguntas: qué se pide, cómo desarrollarlo y qué entregar. Es una bajada de requisitos y una propuesta de procedimiento; no autoriza ni registra implementación, nuevas inferencias o entrenamiento. Las casillas de esta bajada conservan el diseño inicial; el seguimiento vigente es el plan C0–C7 y su bitácora. Ejecución completada: snapshot técnico validado en deliveries/challenge/. El envío al profesor queda a cargo del equipo.

Fuente normativa: [DesafioInvestigacion-2026.pdf](../../DesafioInvestigacion-2026.pdf), secciones I a III. Contexto existente: [spike de unidades](../../spikes/units/README.md) e [informe exploratorio](../../spikes/units/report.md). Las referencias de página siguientes corresponden al PDF, incluida su primera página sin número impreso.

## Aclaración docente incorporada el 2026-11-07

La [respuesta compartida por el usuario](2026-11-07_193927_aclaraciones_docentes_desafio.md) complementa el PDF: mínimo **tres modelos pequeños (~1–2B)**, incluido el objetivo, preferiblemente de familias distintas. Sumar mediano y grande es ideal; si no se pueden evaluar, justificarlo. Esto actualiza la interpretación anterior de una referencia de frontera incondicional. Para esta ejecución se acordó omitir la referencia de frontera, justificarlo por recursos y usar tres pequeños locales (Qwen3-1.7B, Llama 3.2-1B y SmolLM2-1.7B-Instruct), con Qwen3-8B como profesor abierto sujeto a validación local.

Para datos derivados, recomienda **4–8 respuestas por problema de train**, unas **4.000 trazas correctas SFT** y **2.000 pares DPO**, cubriendo dificultad. Son metas orientativas, no mínimos rígidos: volúmenes menores requieren justificación y análisis. Las trazas programáticas no sustituyen las del profesor abierto mayor; las referencias siguen calculándose por código y no por el modelo.

## 1 Qué se pide

### Objetivo y alcance de esta etapa

El grupo, de hasta cuatro personas, debe elegir un problema que un modelo de aproximadamente 1–2B parámetros resuelva mal y construir los componentes que harán posible su entrenamiento posterior. La calibración exige evitar tanto el fracaso total como el acierto permanente. El problema debe requerir razonamiento o uso de herramientas, no memorización de datos. [PDF, sección I, pp. 1–2](../../DesafioInvestigacion-2026.pdf#page=1).

El ciclo de SFT, evaluación, RL e iteración que presenta la introducción explica el uso futuro del entorno. **Entrenar mediante SFT, DPO o RL y demostrar mejoras posteriores corresponde al proyecto de curso, no a esta entrega.** Sí corresponde generar y entregar los datos derivados para SFT y DPO.

### Requisitos explícitos y aplicación a unidades

| ID | Lo que exige el desafío | Aplicación al tema seleccionado | Fuente |
| --- | --- | --- | --- |
| R1 | Elegir un problema de razonamiento o herramientas adecuado para un modelo pequeño. | Resolver problemas cuantitativos de varios pasos, con fórmulas y conversiones dadas; justificar dónde falla el modelo objetivo. | I, pp. 1–2 |
| R2 | Construir un harness con formato de prompt, herramientas si aplica, parser y verificador, siguiendo la interfaz común `reward(prompt, completion) -> float`. | Estandarizar entrada y respuesta, extraer cantidad y unidad, comprobar compatibilidad y valor, y devolver recompensa numérica. | I.1, p. 2 |
| R3 | Crear tareas con respuestas calculadas por código, niveles de dificultad y particiones train/eval/test. | Generar problemas, referencias y variantes de unidades de forma programática, con separación entre entrenamiento, validación y prueba. | I.2, p. 2 |
| R4 | Generar trazas SFT con un modelo abierto de mayor tamaño y filtrarlas con el verificador. | Obtener soluciones verificadas sobre las tareas destinadas a entrenamiento, documentando profesor y procedimiento. | I.3, p. 2; III, p. 3 |
| R5 | Producir pares de preferencia DPO/RLHF. | Emparejar una respuesta correcta y otra incorrecta para un mismo problema, con etiquetas verificables. | Introducción, p. 1; I.3, p. 2; III, p. 3 |
| R6 | Medir pass@1 y pass@k por dificultad; la aclaración precisa mínimo tres pequeños, incluido el objetivo, y ampliación ideal con mediano/grande, privilegiando abiertos. | Añadir un tercer pequeño a los dos del spike; evaluar mayores si es viable y justificar su omisión por recursos. | I.4 y II, p. 2; III, p. 3; aclaración docente enlazada |
| R7 | Aceptar respuestas equivalentes y resistir reward hacking. | Admitir unidades equivalentes y formas de respuesta válidas; rechazar ambigüedades, respuestas múltiples y formatos que produzcan falsos aciertos. | II, p. 2 |
| R8 | Describir entorno y dataset, con generación, particiones, dificultad, ejemplos, fortalezas y debilidades. | Explicar el diseño de los problemas de unidades y sus límites, además de entregar los artefactos. | III, p. 3 |
| R9 | Informar línea base, ejemplos cualitativos, robustez del verificador y calibración del objetivo. | Separar errores numéricos, de unidad y de extracción; explicar qué evidencia respalda que las tareas son aprendibles. | III, p. 3 |
| R10 | Compartir el código del entorno con el curso para que otros grupos puedan usarlo. | Entregar código y documentación suficientes para ejecutar el entorno y consumir su interfaz. | III, p. 3 |

Las herramientas son condicionales: el PDF no obliga a incorporar calculadora, intérprete u otras herramientas. Si se eligen, recomienda pocos turnos de interacción. Para este plan se propone conservar inicialmente la modalidad de respuesta directa del spike.

### Criterios con que se evaluará la calidad

| Criterio explícito | Pregunta que debe responder la entrega de unidades |
| --- | --- |
| Originalidad | ¿Qué aporta el problema o su método de generación más allá de repetir ejercicios de conversión? |
| Profundidad | ¿Existe volumen y diversidad sustantiva, con niveles de dificultad justificados? |
| Robustez | ¿El verificador acepta equivalencias y resiste intentos de obtener recompensa sin resolver el problema? |
| Calibración | ¿Hay evidencia de aciertos y errores reales del objetivo, sin confundir fallos del parser con fallos de razonamiento? |

Fuente: [PDF, sección I, p. 2](../../DesafioInvestigacion-2026.pdf#page=2). Aumentar únicamente el número de instancias de las mismas plantillas no demuestra por sí solo originalidad ni profundidad.

### Aspectos que el PDF no fija

El PDF no establece cantidades mínimas de tareas o trazas, proporciones de splits, valor de k, umbrales de acierto, tolerancia numérica, extensión ni empaquetado. La aclaración sí fija tres pequeños como mínimo y aporta las metas orientativas SFT/DPO anteriores. No convertir estas metas en umbrales rígidos ni omitir la justificación si se obtiene menos.

La interfaz se presenta como una firma orientativa: falta confirmar sus tipos concretos y convenciones con la especificación común del curso. El PDF indica como fecha máxima el viernes 6 de noviembre a las 23:59; cualquier prórroga o instrucción posterior debe confirmarse con el curso, pues no consta en esta fuente.

## 2 Cómo debe desarrollarse

Esta secuencia es una **propuesta metodológica para cumplir los requisitos**, no una secuencia obligatoria dictada por el PDF. Los controles de separación, congelamiento y reproducibilidad concretan acuerdos ya presentes en el [README del repositorio](../../README.md).

### Paso 1 Formalizar el problema y el protocolo

- [ ] Registrar unidades como tema seleccionado y actualizar después las referencias vigentes a scheduling en la documentación del equipo.
- [ ] Delimitar capacidades a evaluar: composición de operaciones, conversión de unidades, consistencia dimensional y manejo de magnitudes o notación científica.
- [ ] Mantener explícitas en el prompt las fórmulas y equivalencias necesarias para que la tarea evalúe razonamiento y no recuerdo de constantes o conocimiento físico.
- [ ] Definir objetivo y otros dos modelos pequeños, más profesor abierto mayor; considerar mediano/grande para ampliar la línea base o justificar su omisión.
- [ ] Acordar tamaños de dataset, particiones, cantidad de muestras, k y presupuesto de respuesta antes de la evaluación final.
- [ ] Confirmar el contrato común del curso y documentar el formato de respuesta y la política de recompensa.

**Salida del paso:** especificación del problema y protocolo experimental, con decisiones pendientes identificadas. Un modelo puede cubrir varios roles si se justifica; un modelo mayor no se considera automáticamente de frontera.

### Paso 2 Diseñar generación dificultad y particiones

- [ ] Definir familias y variaciones que aporten diversidad real, considerando que velocidad y energía del spike están cerca del techo.
- [ ] Especificar qué cambia entre niveles y por qué debería aumentar la dificultad; evitar atribuir causalidad a una sola variable si cambian varias.
- [ ] Calcular referencias por código y comprobar que concuerdan con los datos efectivamente presentados en el prompt.
- [ ] Asignar identificadores y conservar parámetros, semilla y versión necesarios para reconstruir las tareas.
- [ ] Separar train/eval/test sin duplicados ni variantes relacionadas repartidas entre splits; mantener cada `pair_id` del diseño actual en una sola partición.
- [ ] Reservar el conjunto exploratorio ya observado para desarrollo o calibración y construir un test independiente del ajuste del generador y verificador.

**Salida del paso:** diseño del generador y manifiesto de particiones. Los 90 problemas exploratorios no deben presentarse como un test independiente después de haber servido para ajustar el parser.

### Paso 3 Consolidar el harness y la robustez

- [ ] Definir cómo `reward` obtiene la referencia a partir del prompt o de la representación admitida por el curso, sin exponer la respuesta de referencia al modelo.
- [ ] Separar extracción de respuesta y comprobación del valor; impedir que el parser busque en el desarrollo un número que coincida con la referencia.
- [ ] Definir unidades aceptadas, conversiones, redondeo y tolerancia; justificar si se conserva el 1% relativo del spike.
- [ ] Probar respuestas equivalentes, notación científica, formatos numéricos y representaciones válidas dentro del contrato documentado.
- [ ] Probar respuestas múltiples o contradictorias, unidad ausente o incompatible, valores no finitos, salidas malformadas e intentos de explotar el parser.
- [ ] Documentar falsos positivos, falsos negativos y límites conocidos; conservar los casos adversariales como pruebas reproducibles.
- [ ] Mantener la recompensa automática independiente de revisiones humanas; publicar estas últimas como diagnóstico separado si siguen siendo necesarias.

**Salida del paso:** contrato del harness y evidencia de robustez. Una corrección manual posterior no sustituye una función de recompensa ejecutable por otros grupos.

### Paso 4 Calibrar y congelar la evaluación

- [ ] Evaluar el objetivo en piloto o validación y analizar aciertos por nivel y familia.
- [ ] Distinguir errores de cálculo o conversión, unidades incompatibles, respuestas no interpretadas y truncamientos.
- [ ] Ajustar familias o dificultad donde haya techo o suelo, sin imponer un umbral de éxito que el PDF no define.
- [ ] Revisar ejemplos de aciertos y errores para comprobar que la señal corresponde al razonamiento buscado.
- [ ] Congelar generador, particiones de prueba, parser, verificador y protocolo antes de evaluar el test final.

**Salida del paso:** justificación de calibración y versiones congeladas. La mezcla de aciertos y errores respalda la viabilidad; no prueba que un entrenamiento futuro mejorará el modelo.

### Paso 5 Generar los datos para entrenamiento posterior

- [ ] Generar soluciones sobre train con el profesor abierto mayor, muestreando preferentemente 4–8 respuestas por tarea y registrando revisión y configuración; trazas programáticas solo como complemento.
- [ ] Filtrar trazas SFT mediante el verificador y revisar la coherencia de los pasos: una respuesta aceptada por tolerancia puede contener un desarrollo incorrecto.
- [ ] Construir pares DPO con respuesta preferida correcta y rechazada incorrecta del mismo problema, conservando la evidencia de clasificación.
- [ ] Evitar usar una salida no interpretada como ejemplo matemáticamente incorrecto sin resolver primero su clasificación.
- [ ] Conservar procedencia, identificador de tarea y resultados de verificación; excluir eval/test de los datos derivados de entrenamiento.
- [ ] Informar cantidades generadas, retenidas y descartadas por dificultad y familia; contrastar con metas orientativas de 4.000 SFT/2.000 DPO y justificar resultados menores.

**Salida del paso:** dataset SFT y dataset de pares DPO, con procedimiento y modelo de generación documentados. No se entrena ningún modelo en esta etapa.

### Paso 6 Medir la línea base final

- [ ] Evaluar al menos tres pequeños, incluido el objetivo, sobre las mismas tareas de prueba con protocolo comparable; ampliar con mediano/grande si es viable o justificar su omisión.
- [ ] Obtener suficientes muestras por tarea para el k elegido; registrar muestreo, semillas y presupuesto de generación.
- [ ] Calcular pass@1 y pass@k por dificultad y explicar el estimador utilizado; complementar por familia para evitar que el promedio oculte techo y suelo.
- [ ] Reportar cobertura del parser y respuestas no interpretadas junto con las métricas; aplicar el mismo procedimiento automático a todos los modelos.
- [ ] Conservar prompts, respuestas y recompensas, además de versiones de modelos, código, dataset y entorno.
- [ ] Seleccionar ejemplos cualitativos de fortalezas y fallos y explicar los límites de la comparación.

**Salida del paso:** informe y artefactos de la línea base. Como opción inicial puede mantenerse k=3, pero su valor final debe acordarse. Con n muestras y c aciertos por tarea, el estimador usado en el spike es `1 - C(n-c,k)/C(n,k)`, promediado entre tareas, con n ≥ k. Con n=k=3, pass@3 mide la proporción de tareas con al menos un acierto observado.

### Paso 7 Preparar y auditar la entrega

- [ ] Reunir código, datasets, documentación e informe en una entrega accesible al curso.
- [ ] Documentar instalación, generación de tareas, uso de `reward` y reproducción de métricas desde respuestas guardadas.
- [ ] Comprobar correspondencia entre cada requisito R1–R10 y su evidencia concreta.
- [ ] Revisar que cifras, ejemplos, versiones y particiones coincidan en todos los documentos y artefactos.
- [ ] Ejecutar posteriormente la revisión final del checklist siguiente y registrar brechas explícitas.

**Salida del paso:** entrega verificable por otro grupo, con los cuatro entregables oficiales cubiertos.

## 3 Qué hay que entregar

El PDF enumera cuatro entregables. El dataset de tareas se incluye dentro de la entrega del entorno y dataset porque es un requisito explícito de I.2, aunque no aparezca como una quinta viñeta independiente en III. Los formatos concretos quedan a elección del equipo o de instrucciones adicionales del curso.

### E1 Código del harness y dataset de tareas

- [ ] Entregar el código del harness con formato de prompt, parser y verificador.
- [ ] Exponer `reward(prompt, completion) -> float` conforme al contrato común confirmado.
- [ ] Entregar herramientas y protocolo de interacción si se incorporan.
- [ ] Incluir generación programática y referencias verificables por código.
- [ ] Entregar o permitir reconstruir inequívocamente train/eval/test y sus niveles de dificultad.
- [ ] Adjuntar pruebas del generador y verificador, incluidas equivalencias e intentos de reward hacking.
- [ ] Incluir instrucciones y dependencias para que otro grupo pueda utilizar el entorno.
- [ ] Asegurar que el curso tenga acceso al código y a los artefactos necesarios.

**Evidencia de aceptación:** otro grupo puede obtener tareas, evaluar respuestas válidas e inválidas y usar la interfaz sin depender de decisiones manuales no documentadas. Cubre R2, R3, R7 y R10.

### E2 Descripción del entorno y del dataset

- [ ] Describir problema, capacidades evaluadas y adecuación al modelo pequeño.
- [ ] Explicar método de generación y cálculo de las referencias.
- [ ] Documentar familias, volumen, diversidad, niveles de dificultad y tamaños de partición.
- [ ] Explicar separación entre splits y tratamiento de variantes relacionadas.
- [ ] Mostrar ejemplos representativos de tareas, respuestas y verificación.
- [ ] Explicar fortalezas y debilidades del diseño.
- [ ] Justificar originalidad y profundidad con evidencia del diseño final.

**Evidencia de aceptación:** se entiende qué mide el entorno, cómo se construyó el dataset y qué límites tiene. Cubre R1, R3 y R8, además de los criterios de originalidad y profundidad.

### E3 Datos derivados para SFT y DPO

- [ ] Entregar trazas SFT generadas con un modelo abierto mayor y filtradas con el verificador; las programáticas no las reemplazan.
- [ ] Entregar pares DPO de respuestas correcta e incorrecta para el mismo problema.
- [ ] Identificar modelo, revisión, procedimiento de generación y criterios de selección.
- [ ] Vincular cada ejemplo con su tarea de train y evidencia de verificación.
- [ ] Documentar esquema y cantidades generadas/filtradas por dificultad, procedencia de rechazadas de pequeños y desviaciones de las metas orientativas SFT/DPO.
- [ ] Comprobar que los datos derivados no incorporen ejemplos de eval/test.

**Evidencia de aceptación:** ambos datasets pueden cargarse y su procedencia y selección pueden auditarse. Un archivo de respuestas del spike no satisface por sí solo este entregable. Cubre R4 y R5.

### E4 Informe de línea base robustez y calibración

- [ ] Identificar al menos tres modelos pequeños evaluados, incluido el objetivo; añadir mediano/grande si es viable o justificar por qué no se evaluaron.
- [ ] Describir configuración y protocolo de evaluación comparables.
- [ ] Presentar pass@1 y pass@k por nivel de dificultad.
- [ ] Incluir ejemplos cualitativos que muestren fortalezas y debilidades.
- [ ] Analizar aceptación de respuestas equivalentes y resistencia al reward hacking.
- [ ] Demostrar calibración del objetivo con aciertos y errores verificables.
- [ ] Separar rendimiento automático, limitaciones de extracción y revisiones humanas.
- [ ] Explicar incertidumbres y evitar afirmar mejoras de entrenamiento no evaluadas.
- [ ] Vincular tablas y conclusiones con respuestas y resultados reproducibles.

**Evidencia de aceptación:** las conclusiones pueden contrastarse con los artefactos y responden a robustez y calibración, además de reportar las métricas solicitadas. Cubre R6, R7 y R9.

## 4 Qué aporta units y qué sigue pendiente

Estado según la documentación del spike; esta planificación no vuelve a ejecutar sus comprobaciones.

| Componente | Evidencia exploratoria disponible | Brecha para la entrega final |
| --- | --- | --- |
| Tema | Unidades seleccionado en la conversación actual. | Actualizar después las decisiones y referencias antiguas a scheduling. |
| Generación | 90 tareas, tres familias y tres niveles; referencias por código. | Justificar diversidad y originalidad, ampliar donde corresponda y construir particiones finales. |
| Harness | Prototipo autocontenido con extracción, conversión y verificación. | Consolidar la interfaz común y la documentación de uso compartido. |
| Verificador | Equivalencias, tolerancia del 1% y pruebas documentadas. | Completar análisis de robustez y tratamiento automático de formatos admitidos. |
| Calibración | Qwen tiene 191/270 aciertos automáticos; 193/270 tras cinco revisiones contextuales. | Calibrar diseño final y validar con test independiente; no tratar revisión manual como recompensa automática. |
| Comparación | Qwen3-1.7B y Llama 3.2-1B, tres muestras por tarea. | Incorporar tercer pequeño, aplicar protocolo uniforme y evaluar mayores o justificar su omisión. |
| Datos derivados | Respuestas completas y ejemplos cualitativos. | Generar trazas con profesor abierto mayor y preparar datasets SFT y DPO sobre train. |
| Informe | Protocolo, métricas, ejemplos y límites exploratorios documentados. | Redactar descripción e informe de la entrega con evidencia del diseño final. |

Fuente: [informe de units](../../spikes/units/report.md). La cifra final de Qwen incorpora revisión humana y no debe compararse directamente con la cifra automática de Llama. El spike es un antecedente para diseñar la entrega; ninguna de sus piezas se marca automáticamente como cumplimiento final.

## 5 Decisiones pendientes antes de ejecutar

1. Confirmar la especificación concreta de la interfaz y cualquier instrucción de entrega posterior al PDF, incluida la fecha aplicable.
2. Acordar familias y variaciones finales, tamaños de splits y criterio de dificultad.
3. Validar ejecución de los cuatro modelos acordados; decidir si se evalúa también al profesor y documentar la omisión de referencia de frontera.
4. Dimensionar train y muestreo para las metas orientativas de 4.000 SFT/2.000 DPO o justificar una escala menor con calidad y diversidad.
5. Definir el alcance de formatos equivalentes y la tolerancia numérica del verificador.
6. Fijar fechas internas por fase y criterios de cierre, sin confundirlos con exigencias del curso.

La entrega estará lista cuando E1–E4 tengan sus casillas respaldadas por artefactos concretos y la matriz R1–R10 no tenga requisitos sin evidencia. Completar el spike o ejecutar una línea base aislada no cubre por sí solo el desafío.

## Actualización de alcance al iniciar ejecución

La última instrucción del usuario sustituye la exclusión de frontera indicada arriba: completar primero todo lo local y, tras C6, comparar candidato DeepSeek-V4-Pro-0813 mediante Together AI, sujeto a credencial propia y presupuesto específicamente autorizado. C7 permanece abierto si falta esa comparación o template LaTeX. Plan y bitácora vigentes registran ejecución y cantidades; las cifras anteriores son propuestas históricas, no resultados.

Actualización de ejecución, 2026-11-07: tras completar C6, el usuario habilita OpenRouter en lugar de Together AI, autoriza USD 5 máximo y permite escoger un DeepSeek adecuado. Se mantiene DeepSeek-V4-Pro-0813, ruta DeepInfra FP8 compatible con la política de la cuenta. Mismo test congelado y verificador 9, tres respuestas por tarea; sin entrenamiento. Template y autores recibidos. Canal previsto informado: correo al profesor.

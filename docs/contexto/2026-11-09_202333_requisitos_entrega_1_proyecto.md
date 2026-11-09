# Proyecto: requisitos y decisiones de la entrega 1

Fecha: 9 de noviembre de 2026, America/Santiago. Estado: requisitos contrastados y decisiones de alcance
confirmadas por el usuario. Este documento describe qué se pide y
qué podemos reutilizar. El [plan de ejecución](../plans/2026-11-09_202333_entrega_1_proyecto.md)
define cómo preparar el informe.

## Fuente y alcance

Fuente normativa: [ProyectoCurso-2026.pdf](../../ProyectoCurso-2026.pdf), sección 3,
páginas 2–3. El proyecto estudia postentrenamiento de un modelo pequeño usando
un entorno del desafío. La entrega 1 es una propuesta, no el informe final del
experimento. El usuario confirma como instrucción vigente para la entrega 1 el
11 de noviembre de 2026 a las 23:59, por la casilla de Canvas. Hora y canal
provienen de esa confirmación, no del PDF.

## Tres entregas y nombres propuestos

| Hito | Fecha del PDF | Ponderación | Producto requerido | Carpeta propuesta |
| --- | --- | --- | --- | --- |
| 1: propuesta | 11 de noviembre | 5% | Informe escrito con bibliografía, investigación tentativa y entorno. | `deliveries/project-1-proposal/` |
| 2: avance | 25 de noviembre | 10% | Informe con implementación inicial, línea base y primeras curvas de recompensa. | `deliveries/project-2-progress/` |
| 3: cierre | 9 de diciembre | 25% | Paper, poster y presentación oral en video. | `deliveries/project-3-final/` |

El PDF fija las 23:59 para la entrega final, pero no especifica hora para los dos
hitos intermedios. Admite atraso en las entregas 1 y 2 con descuento de un punto
por día; la final no admite atraso. Estas condiciones no sustituyen anuncios
posteriores del curso. Para E1 se aplica la confirmación del usuario: 23:59
por Canvas. No se crean aún carpetas para los hitos 2 y 3.

## Mínimos obligatorios de la primera entrega

| Requisito | Qué debe explicar el informe | Evidencia prevista |
| --- | --- | --- |
| Revisión bibliográfica | Qué aportan los trabajos relevantes y cómo orientan nuestra pregunta y método. | Sección de antecedentes, citas en el texto y referencias con autores y URL. |
| Propuesta tentativa de investigación | Qué queremos averiguar y cómo planeamos comprobarlo. | Pregunta, hipótesis, comparación experimental y criterios de evaluación. |
| Entorno a utilizar | Qué problema resuelve el modelo y cómo se generan tareas y verifican respuestas. | Síntesis del entorno de unidades y sus datos, con ejemplo y límites. |

El entregable formal es un informe escrito. Se propone enviar solo
`propuesta.pdf`; las fuentes se conservarán junto al PDF en el repositorio.
El PDF del curso no exige para este hito código, pesos, datasets, resultados de
entrenamiento, poster, video ni un ZIP adicional. Tampoco fija extensión,
doble columna, template o cantidad mínima de referencias para la entrega 1.
El máximo de siete páginas a doble columna y el mínimo de dos trabajos se
especifican para el paper final, no para esta propuesta.

## Compromisos del proyecto que debe anticipar la propuesta

La propuesta debe ser compatible con la comparación exigida de cinco caminos
en un mismo entorno: modelo inicial sin ajuste adicional, solo SFT, SFT seguido
de RL, solo RL y DPO. SFT es ajuste supervisado con soluciones; RL aprende con
la recompensa del verificador y DPO usa pares de respuesta preferida y rechazada.
La rama SFT→RL debe contabilizar ambas fases dentro de su presupuesto total.

El proyecto pide pass@1 y pass@k por dificultad, uso del verificador final para
todos los resultados finales, auditoría manual de una muestra de respuestas
exitosas y documentación de problemas, correcciones y efecto del reentrenamiento.
Se solicita probar varias semillas en lo posible y analizar sensibilidad y
fortalezas/fallos de acuerdo con el nivel de complejidad elegido. En esta entrega
se propone cómo cumplirlo, sin presentar trabajo futuro como ejecutado.

## Insumos actuales que se reutilizan

La tabla de pendientes del documento general de proyecto del 7 de noviembre
corresponde a un estado exploratorio anterior. El estado vigente del desafío es:

| Insumo disponible | Uso para la propuesta | Límite que debe declararse |
| --- | --- | --- |
| Harness y `reward(prompt, completion)` comprobados | Describir interacción y recompensa verificable. | Registro previo de tareas y formatos admitidos. |
| Tres familias: velocidad, energía y luminosidad | Justificar el entorno y la dificultad. | No equivalen a generalización a problemas arbitrarios. |
| 180 tareas / 60 problemas físicos, splits 90/36/54 | Presentar datos iniciales y separación de particiones. | Solo 18 problemas físicos en test y variantes relacionadas. |
| 121 SFT y 35 DPO con procedencia y auditorías | Identificar los insumos de entrenamiento disponibles. | Volumen pequeño, celdas difíciles escasas y revisión realizada por agentes. |
| Calibración del objetivo: pass@1 48,89%, pass@3 65,56% | Fundamentar una mezcla de aciertos y errores previa al entrenamiento. | No todas las combinaciones están bien calibradas. |
| Línea base del objetivo: pass@1 51,85%, pass@3 68,52% | Presentar evidencia preliminar, no resultados del proyecto. | Usa Ollama y pesos GGUF cuantizados. |
| Informe y template LaTeX del desafío | Reutilizar formato, bibliografía pertinente y síntesis técnica. | No copiar el informe completo ni el historial del repositorio. |

Fuentes: [informe del desafío](../../deliveries/challenge-clean/challenge/informe.pdf),
[protocolo](../../deliveries/challenge-clean/challenge/data/tasks/protocol.json),
[datos derivados](../../deliveries/challenge-clean/challenge/data/training/stats.json)
y [comprobaciones](../../data/units/validation/minimal-delivery.json).

Si cambia el checkpoint, motor, precisión o formato de interacción al entrenar,
se medirá nuevamente el control sin ajuste bajo esas condiciones. Los recursos
que permitieron inferencia no demuestran viabilidad de entrenamiento en la misma
GPU. Los datos derivados deben revalidarse si cambia la política de recompensa.

## Decisiones confirmadas y opciones técnicas

| Tema | Estado | Criterio |
| --- | --- | --- |
| Reutilizar el template LaTeX | Acordado por el usuario | Conservar formato y legibilidad, adaptando título, hito y fecha. |
| Redacción autocontenida y conectada | Acordado por el usuario | Definir términos, explicar cifras y conectar decisiones con el método. |
| Contexto separado del plan | Acordado por el usuario | Requisitos aquí; pasos y comprobaciones en `docs/plans/`. |
| Solo informe como envío formal | Sustentado por el PDF | Fuentes versionadas como respaldo de edición. |
| Nombres de los tres hitos | Convención adoptada para organizar las entregas | `project-1-proposal`, `project-2-progress`, `project-3-final`. |
| Entorno y modelo objetivo | Confirmado por el usuario: unidades y Qwen3-1.7B | Aprovechar evidencia existente sin asumir suficiencia del dataset. |
| Pregunta principal | Confirmada por el usuario: efecto del SFT previo sobre RL | Comparar con solo SFT, solo RL, DPO y control sin ajuste. Generalización y fiabilidad serán análisis complementarios. |
| Complejidad | Propuesto nivel 1 | Usar métodos con código público y aportar comparación y análisis experimental. |
| Recursos | RTX 3050 local como primera opción | Puede ampliarse con cómputo de un colaborador si se confirma disponibilidad; no se presupone. |
| Gasto | Sin presupuesto monetario adicional autorizado | No planificar compras ni servicios pagados como recursos disponibles. |
| Extensión | Confirmada: tres páginas de contenido más referencias | Meta editorial propia, manteniendo tipografía y legibilidad del template. |
| Plazo y canal de E1 | Confirmados por el usuario | 11 de noviembre de 2026, 23:59, casilla de Canvas. |
| Autores | Confirmado mantener el equipo del desafío | Fernando Fajardo, Sebastian Palma, Benjamin Prieto y Rodrigo Ugarte. |

El alcance de la propuesta queda cerrado. Implementación de entrenamiento,
algoritmo RL, límites concretos de cómputo y sensibilidad se concretarán tras
revisar bibliografía y viabilidad en la RTX 3050. No se da por demostrada la
viabilidad de RL en sus 6 GiB de VRAM por haber completado inferencia. Si se
incorpora otra GPU, se documentará su efecto sobre la comparación de cómputo.

## Pregunta acordada

¿Cómo influye el ajuste supervisado previo en el aprendizaje por refuerzo de
Qwen3-1.7B sobre problemas cuantitativos con unidades, frente a solo RL, solo
SFT y DPO, bajo un presupuesto de cómputo comparable?

La propuesta estudiará si el SFT previo mejora la eficiencia del aprendizaje,
sin suponer de antemano superioridad en exactitud. Los criterios experimentales
deben distinguir mejora de formato de respuesta, mejora numérica y aceptación
aparente por límites del verificador. Las hipótesis concretas se redactarán a
partir de la revisión bibliográfica y se identificarán como predicciones, no
como resultados observados.

## Bibliografía revisada para la propuesta

- [DPO, Rafailov et al.](https://arxiv.org/abs/2305.18290): fundamento de la rama de preferencias.
- [DeepSeekMath, Shao et al.](https://arxiv.org/abs/2402.03300): referencia para GRPO como candidato de RL.
- [Reasoning Gym, Stojanovski et al.](https://arxiv.org/abs/2505.24760): generación y recompensas verificables, ya usado en el desafío.
- [GSM-Symbolic, Mirzadeh et al.](https://arxiv.org/abs/2410.05229): sensibilidad de evaluación a variantes, ya usado en el desafío.
- [SWE-Bench+, Aleithan et al.](https://arxiv.org/abs/2410.06992): auditoría de éxitos aparentes como antecedente metodológico, sin extrapolar sus tasas al entorno de unidades.

Se revisaron las fuentes primarias de métodos y resultados, con énfasis en
DPO (secciones 4 y 6), DeepSeekMath (sección 4), Reasoning Gym y GSM-Symbolic.
La revisión de SWE-Bench+ sustenta la motivación de auditoría manual, no cifras
de éxito esperables. El informe explica aporte, límite y relación de cada
trabajo con el diseño, e incluye además el informe propio del desafío para
identificar la procedencia de los resultados preliminares.

## Criterio de aceptación

La propuesta estará lista cuando un lector sin contexto del repositorio pueda
entender qué se quiere investigar, por qué, con qué entorno y datos y cómo se
planea evaluarlo. Los tres mínimos del PDF deben tener evidencia en el informe,
con los recursos no confirmados y los riesgos separados del trabajo realizado.

## Diseño tentativo concretado en el informe

GRPO es la opción propuesta de RL, condicionada a comprobar memoria y tiempo.
El piloto fijará un presupuesto B comparable; SFT→RL contabiliza sus dos fases
dentro de ese total. Se propone estudiar fracciones de 25% y 50% del presupuesto
para SFT si los recursos permiten ambas condiciones, manteniendo el resto de
hiperparámetros RL comunes. Se auditarán hasta tres éxitos por familia/nivel/ruta,
con denominadores por estrato. Estas decisiones son parte del diseño tentativo,
no parámetros de experimentos ya ejecutados.

El usuario solicita un PR separado a main. Rama: `docs/project-1-proposal`,
creada desde `origin/main` después de comprobar que el desafío ya estaba
integrado mediante el commit e99f9e9. El PR incluirá requisitos, plan y propuesta
PDF/fuentes, siguiendo Conventional Commits y las cuatro secciones del repositorio.

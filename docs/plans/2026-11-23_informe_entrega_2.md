# Informe de avance de E2 · Requisitos y plan de escritura

El informe debe mostrar qué se implementó desde la propuesta y qué indican los primeros entrenamientos. El recorrido comienza con la pregunta sobre SFT previo, explica cómo se obtuvo una comparación común y cierra con lo que permiten concluir las curvas, los resultados y la auditoría.

## Checklist de aceptación

La fuente normativa es el [enunciado del proyecto](../../ProyectoCurso-2026.pdf#page=3), p. 3, §3. E2 es un informe escrito de avance, fechado el 25 de noviembre y ponderado en 10 %. El PDF del curso no especifica un tope de páginas, maqueta, hora ni canal para E2. La regla de siete páginas a doble columna pertenece al artículo final (§4).

| Control | Origen | Criterio de éxito |
| --- | --- | --- |
| [x] Informe escrito | E2 §3, R1 | PDF legible y autocontenido. Pregunta, implementación, línea base, curvas y resultados se entienden sin acceso al repositorio. |
| [x] Implementación inicial | E2 §3, R2 | El texto describe generación, particiones, verificación, SFT y GRPO. Identifica el modelo y la GPU, el aislamiento por problema y evidencia de actualización y recarga. |
| [x] Línea base previa al ajuste | E2 §3, R3 | Informa *pass@1* y *pass@3* del modelo base previo al ajuste propio, con unidad de análisis, denominador y resultados por dificultad. El protocolo coincide con el de los cierres. |
| [x] Primeras curvas de recompensa | E2 §3, R4 | Se muestran recompensas observadas por paso para GRPO e híbrido y se cuenta cuántos grupos aportan señal relativa. La pérdida SFT y el desempeño en validación tienen ejes y explicaciones propios. |
| [x] Datos y comparación | Alcance acordado, R5–R9 | Se consigna el paso a seis familias, los volúmenes efectivos y los límites de cobertura. Las cuatro rutas usan el mismo verificador y la misma validación. El costo híbrido incluye SFT. |
| [x] Reporte de auditoría e iteraciones | Proyecto § inicial, alcance acordado, R10 | El informe registra los denominadores y los 287 dictámenes humanos originales. Incluye un caso comprobable y una iteración con efecto medido. |
| [x] Cifras y conclusiones | Alcance acordado, R11/V12 | Tablas y figuras concuerdan con datos, fases y denominadores. El PDF revisado delimita una semilla, cobertura desigual y comparabilidad temporal. |

DPO entrenado, prueba reservada, sensibilidad de la asignación de tiempo, repeticiones y productos finales quedan para E3. En E2 se informa que los pares DPO se prepararon. El [plan de ejecución de E2](2026-11-16_095503_entrega_2_proyecto.md) conserva el alcance técnico y la numeración R/V. El [estado vigente de auditoría](../../data/units/project-e2/audits/README.md) reemplaza los conteos iniciales de ese plan.

## Plan de escritura

El [formato de E1](../../deliveries/project-1-proposal/proyecto_entrega_1.pdf) se conserva en LaTeX: carta, una columna, 10 puntos, encabezado institucional, escudo y autores. Objetivo editorial de tres a cuatro páginas de cuerpo, más anexos y referencias. Reservar el cuerpo para explicar decisiones e interpretar resultados. Usar los anexos para curvas, desglose por dificultad, auditoría y detalles técnicos que sustenten las afirmaciones. Las leyendas deben indicar fase, muestra y unidad.

1. [x] Extraer los mínimos del enunciado y distinguirlos del alcance acordado.
2. [x] Reutilizar la maqueta de E1 y estructurar las secciones según la secuencia pregunta, método, evidencia y próximos pasos.
3. [x] Cargar los resultados medidos de validación, cómputo, curvas e iteraciones y redactar su interpretación inicial.
4. [x] Cotejar la tabla de auditoría con los seis registros de revisión y contar los dictámenes humanos según su procedencia. Mantener calibración y corpus SFT separados de las cuatro rutas evaluadas.
5. [x] Revisar la secuencia del informe y resolver referencias de tablas, figuras, anexos y bibliografía dentro del PDF.
6. [x] Compilar la versión de entrega, revisar página por página y cotejar sus cifras con los resultados guardados.
7. [ ] Corroborar hora, canal y requisitos adicionales de envío, y archivar la versión final y el comprobante al entregar.

## Contenido por sección

| Sección | Información que debe quedar |
| --- | --- |
| Pregunta y alcance | Pregunta heredada de E1, modelo objetivo y comparación que ya se ejecutó. Un párrafo. |
| Implementación y evaluación | Entorno, datos, separación por problema, verificador, cuatro rutas y protocolo de validación. Definir SFT, GRPO y DPO según su papel. |
| Resultados y señal de aprendizaje | Tabla principal, contrastes con control y GRPO, cambios por familia y diagnóstico de grupos con recompensa constante. Remitir a curvas y desgloses. |
| Iteraciones y auditoría | Un cambio de formato medido y un diagnóstico de señal. Resumir selección, criterios, hallazgos y dictámenes pendientes. Adjuntar casos con el cálculo necesario para entenderlos. |
| Conclusiones y trabajo restante | Respuesta provisional a la pregunta, límites que afectan esa respuesta y experimentos que faltan para E3. |
| Anexos y referencias | Curvas de entrenamiento y validación, detalle por dificultad, auditoría y referencias citadas. |

Terminología acordada desde E1. **Qwen3-8B** es el **modelo generador** de soluciones candidatas. **Qwen3-1.7B** es el **modelo objetivo**. La puntuación la calcula el **verificador programático** con una referencia independiente de la respuesta.

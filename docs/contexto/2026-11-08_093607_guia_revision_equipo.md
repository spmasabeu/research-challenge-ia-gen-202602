# Mensaje sugerido para el equipo

Hola equipo, dejé implementado y validado el Desafío de Investigación de unidades.
Lo separé por responsabilidad para que podamos revisarlo sin recorrer un commit gigante.
Está en la rama [implement-units-challenge-20261107](https://github.com/spmasabeu/research-challenge-ia-gen-202602/tree/implement-units-challenge-20261107).

Les propongo este recorrido:

1. **Código del entorno y pruebas** — `src/challenge/`, `tests/`, dependencias:
   [harness, generador, referencias y recompensa](https://github.com/spmasabeu/research-challenge-ia-gen-202602/commit/d76143f449b96f8f2c7f140e8a8a21c6aec57a98).
2. **Tareas y calibración** — `data/units/final-*`, pilotos y exclusiones:
   [particiones train/eval/test](https://github.com/spmasabeu/research-challenge-ia-gen-202602/commit/aa1cb1624feac824c21a9808382fc7e9561da597).
3. **Inferencia y evaluación** — runners, respuestas crudas, parámetros, metadatos
   y métricas locales/DeepSeek:
   [línea base y referencia externa](https://github.com/spmasabeu/research-challenge-ia-gen-202602/commit/aad74c897d4c2761a816a7771dbf177157cccb40).
4. **Datos para entrenamiento posterior** — auditorías y exportación:
   [SFT y DPO](https://github.com/spmasabeu/research-challenge-ia-gen-202602/commit/bfeead033c9c4e93bdd995f4ca97615dce4ebe97).
   Quedaron 121 trazas SFT y 35 pares DPO; el informe justifica el volumen y sus límites.
5. **Informe** — `docs/report/`, template, fuentes LaTeX, figuras y PDF:
   [análisis del desafío](https://github.com/spmasabeu/research-challenge-ia-gen-202602/commit/3503ffde755f55498beaec4f36203a32ec541c15).
6. **Seguimiento y decisiones** — `docs/contexto/` y `docs/plans/`:
   [requisitos, acuerdos y ejecución](https://github.com/spmasabeu/research-challenge-ia-gen-202602/commit/810fa3af4c25f483318644c480c6cde283caf577).
   En particular, [plan C0–C7](https://github.com/spmasabeu/research-challenge-ia-gen-202602/blob/implement-units-challenge-20261107/docs/plans/2026-11-07_130305_ejecucion_desafio_units.md)
   y [bitácora con comandos, cambios y evidencia](https://github.com/spmasabeu/research-challenge-ia-gen-202602/blob/implement-units-challenge-20261107/docs/contexto/2026-11-07_200958_bitacora_ejecucion_desafio_units.md).
7. **Entrega para reproducir o enviar** — una sola versión, en `deliveries/challenge/`:
   [paquete y validaciones](https://github.com/spmasabeu/research-challenge-ia-gen-202602/commit/9a87385125a1796b94c4de0ce4fa32860e2f7e17).
   Empezar por el [README](https://github.com/spmasabeu/research-challenge-ia-gen-202602/blob/implement-units-challenge-20261107/deliveries/challenge/README.md) y la
   [guía de reinferencia](https://github.com/spmasabeu/research-challenge-ia-gen-202602/blob/implement-units-challenge-20261107/deliveries/challenge/REPRODUCING.md).
   También están el [PDF final](https://github.com/spmasabeu/research-challenge-ia-gen-202602/blob/implement-units-challenge-20261107/deliveries/challenge/report/informe.pdf)
   y el [ZIP](https://github.com/spmasabeu/research-challenge-ia-gen-202602/blob/implement-units-challenge-20261107/deliveries/challenge-2026-11-07.zip).
8. **Archivos locales y compilación**:
   [reglas de exclusión](https://github.com/spmasabeu/research-challenge-ia-gen-202602/commit/4bcdb87f6f3df7480d0086a899d59658b6d843fa).

Para revisar resultados no necesitan GPU ni credenciales: se reconstruyen desde
las respuestas incluidas. Las 13 pruebas y la reproducción aislada pasan.
Para generar respuestas nuevas sí necesitan Ollama/modelos; OpenRouter requiere
credencial y presupuesto propios. Las nuevas generaciones pueden variar y sus
trazas necesitan una auditoría nueva.

Hay 180 tareas (90/36/54), tres modelos pequeños, Qwen3-8B como profesor abierto
mayor y DeepSeek-V4-Pro-0813 como referencia externa. El costo API de la corrida
original fue USD0,0935116. `unparsed` no significa error matemático: revisen la
cobertura y las cotas que acompañan las métricas.

No se entrenó ningún modelo; esta entrega deja preparados los insumos del proyecto.
Podemos revisar por bloques y luego coordinar el envío por correo al profesor.

## Nota de publicación

Los enlaces de commits identifican cambios concretos. Los enlaces de archivos
apuntan a la rama de revisión, que reúne la serie completa; no implican un merge
a la rama principal. El mensaje está preparado para copiar y enviar por el equipo.

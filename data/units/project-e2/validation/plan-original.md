# Plan de implementación y aceptación de la entrega 2

Estado: integración de familias completada; implementación restante de E2 planificada. Organización por dependencias y criterios de cierre, sin calendario. Este documento reúne requisitos, entregables, implementación, pruebas y análisis experimental. Las casillas marcadas tienen evidencia de ejecución; las demás siguen pendientes.

El resultado buscado es un informe de avance con una implementación operativa sobre **seis familias**, un dataset ampliado y trazable, una línea base nueva y las primeras curvas de entrenamiento. La pregunta se mantiene: **¿cómo influye el SFT previo en la eficiencia del aprendizaje con RL de Qwen3-1.7B bajo cómputo comparable?** El plan permite evaluar esa pregunta sin confundir una mejor extracción de respuestas con una mejora de cálculo.

## 1 Fuentes y decisiones de alcance

| Fuente | Qué establece y cómo se aplica |
| --- | --- |
| [Enunciado del proyecto, sección 3, p. 3](../../ProyectoCurso-2026.pdf#page=3) | E2 exige informe de avance, implementación inicial, línea base antes de entrenar y curvas de recompensa de los primeros entrenamientos. |
| [E1 entregada](../../deliveries/project-1-proposal/proyecto_entrega_1.pdf) y [fuentes](../../deliveries/project-1-proposal/source/content.tex) | Qwen3-1.7B; comparación de cinco rutas; piloto de cómputo; control entrenable nuevo; revisión del verificador; test independiente; ampliación posible de familias/datos; auditoría humana. |
| [Aclaración docente transcrita](../contexto/2026-11-07_193927_aclaraciones_docentes_desafio.md) | Profesor abierto mayor, referencias calculadas por código, 4–8 muestras por tarea de train y metas orientativas de 4.000 SFT/2.000 DPO. Menos datos requieren justificación y análisis. La fecha y el enlace originales de esa respuesta no están disponibles. |
| [Decisiones del equipo](../contexto/2026-10-29_093018_decisiones.md) | El desafío conserva sus resultados; mejoras del verificador antes del proyecto; nuevo test tras diagnosticar el antiguo. Se había propuesto dimensionar 1.800 tareas de train, sujeto a recursos. |
| [PR #6 de familias](https://github.com/spmasabeu/research-challenge-ia-gen-202602/pull/6) | Añade densidad, presión y tensión eléctrica, catálogo de fórmulas, verifier-10, pruebas y piloto de seis familias. Integrado en main mediante `061ca08`; es la base de la ampliación. |
| [PR #2 del entorno](https://github.com/spmasabeu/research-challenge-ia-gen-202602/pull/2) | Antecedente de políticas de unidad pedida, números ambiguos, contradicciones y longitud. Portar cambios pertinentes con pruebas; no sustituir todo el entorno vigente por esta implementación anterior. |

La aclaración docente se refiere al **desafío**: orienta cómo producir mejores datos, pero no convierte 4.000/2.000 en mínimos normativos de E2 ni obliga a repetir aquí la comparación de tres modelos pequeños. La ampliación a seis familias y de la muestra queda dentro del alcance de este plan por instrucción del equipo.

E2 es un avance: no requiere terminar la comparación final, sensibilidad completa, póster o video. Para cerrar este plan sí se propone ejecutar control, SFT, solo GRPO y SFT→GRPO, porque las dos ramas RL permiten examinar la pregunta central. DPO queda preparado como dataset e interfaz de entrada; su entrenamiento completo pertenece a E3. Tener solo una rama RL no cierra el alcance experimental acordado aquí, aunque pueda satisfacer parte de los mínimos del enunciado.

## 2 Estado comprobado e integración de familias

Inspección del 16 de noviembre de 2026:

- **PR #6 aprobado y mergeado** mediante squash en `061ca0892c9327b43ee2a04307eeec4d0c35f811`. Autor original: `gaspcr`. [Revisión de aprobación](https://github.com/spmasabeu/research-challenge-ia-gen-202602/pull/6#pullrequestreview-5927586104).
- `main` local, `origin/main` y la base de `docs/project-2-plan` están actualizados a ese commit. El plan y su índice se conservan como cambios documentales locales.
- Antes de aprobar se corrigieron únicamente imports señalados por Ruff, en `d7bacc5`, y se revalidó el código: **23/23 pruebas**, Ruff 0.17.4 y Mypy 2.4.1 correctos; Bandit 1.9.4 sin hallazgos medios/altos. La integración con main se comprobó sin conflictos en una copia aislada.
- Se recalcularon offline las **540 respuestas** del piloto: `labels.jsonl` y `summary.json` coinciden byte a byte con los guardados; pass@1 61,1% y pass@3 78,3%. No se realizaron inferencias nuevas.
- **PR #2 cerrado, sin mergear**. Sus mejoras requieren adaptación selectiva; no es un PR pendiente para merge directo.
- El piloto usa una **NVIDIA A30 de 24 GB** en `astronodo-gpu01`. Esto acredita inferencia pasada en ese equipo; falta confirmar acceso y viabilidad de entrenamiento. La RTX 3050 de 6 GiB sigue siendo el recurso inicial de E1.

El PR #6 no completa la ampliación por sí solo: `generate --families` admite seis familias, pero `freeze` aún usa tres y los tamaños antiguos; `check_dataset` espera 18 celdas familia×nivel×estructura. Con seis familias debe comprobar 36. Las mejoras de política previstas para verifier-10 pasan a una versión posterior —previsiblemente verifier-11—, porque el PR ya usa verifier-10 para extender el catálogo.

El PR conserva las filas originales, pero cambiar el código invalida sus hashes normativos para comprobaciones históricas. Preservar `final-v2`, `derived-v3`, los paquetes entregados y su reproducción con el código congelado. No reescribir sus manifiestos para hacerlos pasar con código nuevo.

## 3 Qué se debe entregar

**Entrega formal:** informe escrito de avance en `deliveries/project-2-progress/proyecto_entrega_2.pdf`. El enunciado no fija para E2 extensión, doble columna, hora ni canal específicos; comprobar instrucciones vigentes del curso al preparar el envío.

El informe debe permitir entender y verificar:

1. La pregunta, hipótesis y cambios respecto de E1, incluyendo el paso de tres a seis familias.
2. Qué está implementado: generación, verificación, datos, entrenamiento, evaluación y registro de corridas.
3. Cómo se construyó la muestra: problemas físicos, tareas, particiones, candidatas, trazas retenidas y pares, por familia y dificultad.
4. La línea base nueva del checkpoint entrenable y los resultados iniciales de las rutas ejecutadas.
5. Las curvas de recompensa, condiciones de cómputo y diagnóstico de señal, sobreajuste, truncamiento y errores.
6. La auditoría humana inicial, las iteraciones realizadas y sus efectos; limitaciones y trabajo restante de E3.

**Respaldo reproducible en el repositorio:** código y pruebas; configuración y dependencias fijadas; manifiestos de datos; generaciones crudas y procedencia; logs, adaptadores o ubicación/checksum; evaluaciones; auditorías; tablas/figuras regenerables; fuentes LaTeX y README de reproducción. El PDF del curso no enumera estos respaldos como un ZIP o envío separado obligatorio.

### Checklist de requisitos con trazabilidad

Origen: **E** = explícito de E2; **P** = compromiso metodológico de E1/proyecto; **A** = alcance de ampliación acordado para este plan. Los IDs conectan requisito, etapa y prueba.

| ID | Origen | Requisito pendiente | Evidencia de cumplimiento | Etapa / pruebas |
| --- | --- | --- | --- | --- |
| R1 | E | [ ] Entregar informe escrito de avance. | PDF compilado, legible, autocontenido y cotejado con artefactos. | I9 / V12 |
| R2 | E | [ ] Disponer de implementación inicial ejecutable. | Comandos reales desde entorno limpio; entrenamiento, guardado y evaluación. | I1–I7 / V1–V9 |
| R3 | E/P | [ ] Medir el modelo antes de entrenar con protocolo comparable. | Respuestas del control y tabla pass@1/pass@3 por familia/nivel. | I6 / V8 |
| R4 | E | [ ] Mostrar curvas reales de recompensa inicial. | Logs por paso/checkpoint, figuras y diagnóstico; pérdida SFT complementaria. | I7–I8 / V9–V10 |
| R5 | A | [ ] Integrar seis familias y calibrar su dificultad. | Catálogo, referencias independientes y evaluación piloto de las 18 celdas. | I1–I3 / V1–V4 |
| R6 | A/P | [ ] Ampliar y congelar tareas sin fuga de información. | Dataset versionado, conteos, hashes, exclusiones y test nuevo reservado. | I3 / V3–V4 |
| R7 | A/P | [ ] Ampliar SFT/DPO con calidad y procedencia. | Generaciones de train, filtrado, auditorías y comparación con metas 4.000/2.000. | I5 / V5–V6 |
| R8 | P | [ ] Fijar política robusta del verificador y revalidar datos. | Contrato, regresiones y tabla de cambios de etiquetas entre versiones. | I2–I5 / V2, V5 |
| R9 | P | [ ] Comparar SFT previo frente a RL con costo completo. | Control, SFT y ambas ramas GRPO; curvas sobre validación común y presupuesto registrado. | I4, I6–I8 / V7–V10 |
| R10 | P | [ ] Auditar éxitos y documentar iteraciones. | Muestra humana identificada; problema, cambio y efecto con evidencia. | I8 / V11 |
| R11 | P | [ ] Reproducir métricas y separar evidencia de conclusiones. | Recálculo offline, pruebas conocidas, denominadores e incertidumbre explícitos. | I8–I9 / V8, V10–V12 |

## 4 Diseño de familias y ampliación de muestra

### Familias y calibración

| Familia | Fórmula base | Qué aporta o requiere revisar |
| --- | --- | --- |
| Velocidad | v=d/t | Conversión de distancia/tiempo y salida. El piloto del PR muestra techo en fácil/media. |
| Energía cinética | E=mv²/2 | Composición de operaciones y conversión al cuadrado; reforzar cobertura SFT difícil. |
| Luminosidad | L=4πd²F | Notación y conversiones de flujo; el piloto muestra suelo, sobre todo en difícil. |
| Densidad — nueva | ρ=m/V | Masa/volumen y conversión a g/cm³; diagnosticar errores de factor 1.000. |
| Presión — nueva | P=F/A | Conversión de área y salida en kPa; dificultad empírica no necesariamente monótona. |
| Tensión eléctrica — nueva | V=IR | Corriente, resistencia en serie y salida en mV; fácil/media están cerca del techo. |

Mantener tres niveles y estructuras directa/suma como punto de partida. Recalibrar con el checkpoint entrenable sobre desarrollo, empezando por techo en velocidad/tensión y suelo en luminosidad. Revisar primero parser y truncamiento; después rangos o conversiones. Toda modificación debe conservar referencias calculables y queda congelada antes del control reportable. La mezcla de entrenamiento será común a las rutas; no cambiarla solo para favorecer una.

Añadir familias aumenta diversidad, pero si todas aparecen en train/eval/test seguimos midiendo generalización a nuevas instancias dentro de familias conocidas. No afirmar generalización a fórmulas no vistas. Un experimento con familia retenida sería otro estudio, fuera de este alcance.

### Tamaños propuestos y regla de ampliación

Punto de partida propuesto, **no mínimo del curso**:

| Partición | Problemas físicos por familia | Total de problemas físicos | Tareas, con tres niveles | Tareas por familia/nivel |
| --- | --- | --- | --- | --- |
| Train | 100 | 600 | 1.800 | 100 |
| Eval | 20 | 120 | 360 | 20 |
| Test reservado | 20 | 120 | 360 | 20 |
| Total | 140 | 840 | 2.520 | 140 |

Mantener mitad directa y mitad suma por familia en cada partición; las tres variantes de cada problema permanecen juntas. El tamaño de train retoma el dimensionamiento anterior; eval/test se proponen en 360 para dar 20 tareas por celda en seis familias. Usar una nueva versión del proyecto, con semillas y familias explícitas.

Para un corte limpio, generar los splits nuevos excluyendo todos los problemas históricos conocidos: spike, pilotos, controles, final-v2 y piloto del PR #6. Los datos antiguos siguen sirviendo para depuración y contraste; no concatenar silenciosamente sus 121 SFT/35 DPO al dataset nuevo. Si se decide reutilizar antiguos ejemplos de train, incorporarlos explícitamente al manifiesto y revisar otra vez exclusiones y balance.

- Muestrear inicialmente seis respuestas del profesor por tarea de train: 10.800 candidatas para 1.800 tareas; usar 4–8 según el piloto de costo y calidad.
- Apuntar a unas **4.000 trazas SFT y 2.000 pares DPO** válidos. Son objetivos de producción, no cantidades que se puedan prometer antes del filtrado.
- Estimar por celda retención única tras verificación/auditoría y disponibilidad de negativos. Proyectar `candidatas necesarias ≈ objetivo SFT / retención medida` y registrar tiempo/tokens; no trasladar automáticamente la tasa histórica a familias nuevas.
- Ampliar primero las celdas escasas mediante nuevos problemas de train o muestras adicionales. Conservar variantes físicas juntas y excluir eval/test e historial. Congelar nuevamente el train ampliado antes de las corridas comparables.
- DPO conserva el máximo actual de dos pares por tarea: con 1.800 tareas, el techo es 3.600 pares, y llegar a 2.000 exige al menos 1.000 tareas con pares utilizables. Ese conteo no se resuelve con duplicación o producto cartesiano.
- Si el profesor casi no falla, generar negativos con el modelo pequeño solo en train. No convertir respuestas no interpretadas en errores matemáticos confirmados.
- Aceptar un volumen menor a las metas únicamente con conteos por celda, tareas únicas, razones de descarte, costo medido y análisis de cobertura. Como objetivo interno inicial, buscar SFT en al menos 20 tareas distintas y DPO en al menos 10 tareas distintas por familia/nivel; si no se logra, registrar la excepción y su efecto antes de entrenar. No ocultar celdas vacías tras un total grande.

La revisión de calidad también consume recursos: el derivador actual exige ampliar la revisión a toda celda donde se detecta un defecto. Contabilizar ese trabajo al dimensionar la producción y distinguir auditoría automática/de agentes de revisión humana.

## 5 Plan de implementación por dependencias

Secuencia principal: **I1 → (I2 e I4) → I3 → I5 → I6 → I7 → I8 → I9**. I2 e I4 pueden avanzar de forma independiente usando tareas de desarrollo; I3 necesita el contrato de I2 y el backend viable de I4 para calibrar. La generación masiva depende de ambos pilotos, técnico y de dificultad. La línea base definitiva depende del mismo protocolo congelado que los modelos entrenados.

### I1 Integrar la ampliación existente

- [x] Revisar estado, head, diff, llamadores, pruebas y compatibilidad del PR #6 con main.
- [x] Ejecutar 23 pruebas y Ruff/Mypy/Bandit; comprobar regeneración histórica en la suite y recalcular el piloto desde crudos.
- [x] Corregir imports, aprobar el head validado, mergear el PR y actualizar main y `docs/project-2-plan` a `061ca08`.
- [x] Conservar snapshots del desafío y la reproducción documentada en `data/units/README.md`; mantener PR #2 cerrado.

**Salida completada:** seis familias integradas —velocidad, energía, luminosidad, densidad, presión y tensión eléctrica— y verifier-10. La integración no implementa aún freeze/check ampliado ni entrenamiento; esos trabajos siguen en I2–I7.

Validación ejecutada en copia aislada:

```bash
PYTHONPATH=src uv run --locked python -m unittest discover -s tests -q
uvx --from ruff==0.17.4 ruff check src/challenge tests docs/report/render.py
uvx --from mypy==2.4.1 mypy --ignore-missing-imports src/challenge tests docs/report/render.py
uvx --from bandit==1.9.4 bandit -r src/challenge docs/report/render.py -ll
```

El piloto se reprodujo con `challenge.harness score` sobre `data/units/pilot-families-v1/tasks.jsonl` y `data/units/pilot-families-v1/qwen17`; las etiquetas y el resumen se compararon byte a byte con `scores/v10/`. Repetir pruebas afectadas cuando cambie la implementación posterior.

### I2 Cerrar contrato del verificador del proyecto

- [ ] Portar selectivamente mejoras del PR #2 y fijar política de separadores decimales, formatos, alias, contradicciones y longitud.
- [ ] Adoptar como política propuesta exigir la unidad solicitada, aceptando alias de esa unidad. Registrar por separado equivalencia física en SI, para distinguir conversión omitida de resultado numérico incorrecto. Este cambio debe reflejarse en pruebas y datos revalidados.
- [ ] Mantener tolerancia relativa del 1%, rechazo de no finitos y ausencia de acceso a referencia durante extracción; comprobar referencias desde el prompt con implementación independiente del generador.
- [ ] Preservar `reward(prompt, completion)` y error explícito por prompt no registrado. Cargar referencias en el proceso que evalúa; nunca transformarlas en mensajes visibles al modelo ni ocultar fallos de integración devolviendo cero.
- [ ] Recalificar respuestas históricas como diagnóstico con una versión nueva y guardar cambios de etiqueta; preservar resultados oficiales anteriores.

**Salida:** contrato documentado, versión/hash únicos y pruebas V2. Si se exige unidad pedida, actualizar también las pruebas del PR #6 que actualmente premian otras unidades equivalentes.

### I3 Calibrar y congelar las seis familias con muestra ampliada

- [ ] Reutilizar el catálogo del PR y el piloto como antecedente; medir las 18 celdas con el backend entrenable y resolver techo/suelo conforme al diagnóstico.
- [ ] Parametrizar `freeze` y `check_dataset` con familias, grupos por split y semillas del protocolo. Eliminar supuestos fijos de tres familias/18 celdas en la ruta del proyecto; mantener comprobación estricta de integridad.
- [ ] Reunir exclusiones por `physical_key`, generar la muestra ampliada y comprobar identidad física incluso si cambia estructura o representación. Evitar bucles indefinidos ante agotamiento del espacio de generación.
- [ ] Guardar particiones públicas/privadas, protocolo, catálogo, exclusiones, código normativo y hashes. Asignar versión inequívoca al dataset nuevo sin alterar filas históricas.
- [ ] Reservar test nuevo; seleccionar checkpoints y ajustar parámetros solo con desarrollo/eval. No evaluar test para mejorar el avance.

**Salida:** dataset reproducible de seis familias, conteos acordados, cero cruces y V3/V4 aprobadas.

### I4 Habilitar entrenamiento y medir recursos

- [ ] Confirmar disponibilidad real de RTX 3050/A30 u otro recurso; elegir un entorno común para la comparación.
- [ ] Fijar versiones compatibles de PyTorch, Transformers, TRL y PEFT en dependencias y lock; usar implementaciones públicas de SFT/GRPO. Revisar la documentación de las versiones instaladas.
- [ ] Probar LoRA y, si hace falta, cuantización; ejecutar generación, backward, actualización, guardado y recarga con el checkpoint Qwen3-1.7B elegido.
- [ ] Habilitar una ruta mínima de inferencia y puntuación del piloto con `verify`/`metrics`, reutilizable en la evaluación completa de I6; emplearla para calibrar I3 antes de congelar datos.
- [ ] Repetir con GRPO, incluyendo varias respuestas por prompt y recompensa propia. Medir memoria máxima, segundos/paso, tokens, truncamiento y grupos con recompensa variable.
- [ ] Fijar presupuesto B y límites a partir de esas mediciones; separar entrenamiento, evaluación y generación compartida. Si una GPU no es viable, cambiar el recurso y repetir el piloto antes de fijar corridas.

**Salida:** actualizaciones reales finitas y adaptadores recargables; presupuesto y configuración justificables. Cargar el modelo o ejecutar solo inferencia no satisface este paso. Referencias de integración: [SFTTrainer](https://huggingface.co/docs/trl/main/en/sft_trainer) y [GRPOTrainer](https://huggingface.co/docs/trl/main/en/grpo_trainer).

### I5 Producir y validar SFT y DPO ampliados

- [ ] Generar respuestas de un profesor abierto mayor, inicialmente Qwen3-8B, exclusivamente para train con 4–8 muestras, revisión de pesos y parámetros registrados.
- [ ] Reutilizar `derive.collect`, `required_audits` y `build`; preservar deduplicación, procedencia, controles de pertenencia y expansión de auditoría ante defectos.
- [ ] Completar negativos reales del pequeño donde falten; verificar preferida y rechazada del mismo prompt con la versión definitiva del verificador.
- [ ] Publicar por celda candidatas, aceptadas, descartadas, únicas, auditadas y tareas cubiertas; aplicar la regla de ampliación de la sección 4.
- [ ] Exportar formatos SFT y preferencias manteniendo IDs/metadata para trazabilidad; probar template y máscara de pérdida. No sustituir trazas del profesor por soluciones programáticas.

**Salida:** `sft.jsonl`, `dpo.jsonl`, estadísticas, auditorías y manifiesto reproducibles; metas alcanzadas o desviación justificada, con cobertura explícita de todas las familias/niveles.

### I6 Implementar evaluación común y medir el control

- [ ] Incorporar evaluación del checkpoint base y adaptadores con el backend entrenable; reutilizar `verify` y `metrics`.
- [ ] Guardar prompts, respuestas, índices de muestra, semillas, tokens, terminación, modelo/adaptador y hashes. No simular metadata Ollama para resultados de otro backend.
- [ ] Evaluar el control sin ajuste propio sobre eval completo con tres muestras por tarea, semillas de generación 42–44 y protocolo fijo. Con 360 tareas son 1.080 respuestas.
- [ ] Generar pass@1/pass@3, cobertura, errores y truncamientos por familia/nivel, además del promedio general. Los 51,85%/68,52% históricos y el piloto del PR siguen siendo antecedentes separados.

**Salida:** control reproducible con paso cero y pruebas V8. El modelo base significa aquí checkpoint inicial sin nuestro ajuste, no necesariamente un modelo sin postentrenamiento de sus autores.

### I7 Ejecutar SFT y las dos ramas GRPO

- [ ] Ejecutar SFT desde los pesos iniciales; registrar pérdida y evaluar recompensa verificable en checkpoints.
- [ ] Ejecutar solo GRPO desde los mismos pesos iniciales con prompts de train y recompensa común.
- [ ] Ejecutar SFT→GRPO cargando los pesos del adaptador SFT como política entrenable; comprobar que no se reinicializa el adaptador ni se congela accidentalmente. Documentar política de referencia/KL y reinicio del optimizador entre fases.
- [ ] Usar presupuesto total B comparable: SFT→GRPO contabiliza ambas fases. Probar inicialmente 25% SFT/75% RL como condición de E1; reservar 50% para la sensibilidad posterior. Guardar el checkpoint SFT en ese corte aunque la ruta solo SFT continúe.
- [ ] Mantener constantes entorno, datos, muestreo de evaluación y configuración RL pertinente. Guardar estados de RNG/optimizador necesarios para reanudar; rechazar reanudaciones con configuración o datos incompatibles.
- [ ] Registrar recompensa por paso y evaluar paso cero y al menos tres checkpoints posteriores como criterio operativo del plan. Para reducir costo, fijar un subconjunto estratificado de eval para curvas frecuentes; usar eval completo con tres muestras en control y cierre de cada ruta.

**Salida:** control, SFT, GRPO y SFT→GRPO con checkpoints y curvas reales. El descenso de pérdida SFT no sustituye la curva de recompensa. Un resultado plano o negativo puede ser científicamente válido si se descarta un fallo de implementación y se analiza.

### I8 Analizar aprendizaje, auditar e iterar

- [ ] Comparar recompensas de train con validación; separar aprendizaje numérico, unidad solicitada, cobertura del parser y longitud.
- [ ] Seleccionar aleatoriamente hasta tres éxitos por familia/nivel/ruta disponible para revisión humana; revisar datos, conversiones, operaciones y conclusión. Registrar auditor, semilla, IDs, dictamen y razones; incluir fallos ilustrativos aparte de esa muestra.
- [ ] Diagnosticar grupos GRPO sin variación, celdas en techo/suelo, pérdida no finita, sobreajuste y posibles falsos éxitos.
- [ ] Cuando haya un defecto, registrar evidencia, corregir, añadir regresión, revalidar y repetir las corridas afectadas. Recalcular evaluaciones con el verificador común; recalificar logs no equivale a entrenar con la nueva recompensa.
- [ ] Producir tablas, curvas y análisis de la sección 7 desde artefactos, conservando resultados fallidos o nulos con su versión.

**Salida:** análisis sustentado y bitácora del ciclo de iteración. Si no aparecen defectos, documentar qué se inspeccionó; no inventar un caso de reward hacking.

### I9 Construir y comprobar el entregable

- [ ] Reutilizar template de E1; redactar el informe siguiendo la sección 3 y enlazar cada resultado a su corrida.
- [ ] Regenerar tablas/figuras offline y compilar PDF desde una copia limpia; revisar legibilidad, referencias y consistencia entre texto y cifras.
- [ ] Completar la matriz R1–R11 y la matriz de validación con comando, resultado y artefacto; distinguir pendiente, aprobado y excepción justificada.
- [ ] Verificar instrucciones de envío y conservar archivo final y comprobante de entrega.

**Salida:** E2 revisada y reproducible. El documento preparado no se marca como enviado sin comprobante.

## 6 Archivos a modificar y artefactos de respaldo

Reutilizar estructura y funciones actuales; los archivos nuevos siguientes son destinos propuestos, no implementación existente.

| Ubicación | Responsabilidad y puntos afectados |
| --- | --- |
| `src/challenge/generator.py` | Integrar catálogo del PR, calibración, exclusiones y protección ante espacio agotado. Mantener referencias independientes en verifier. |
| `src/challenge/verifier.py`, `src/challenge/__init__.py` | Políticas del proyecto e interfaz pública. Revisar exportaciones y llamadores sin cambiar el contrato innecesariamente. |
| `src/challenge/harness.py` | Freeze/check de seis familias y tamaños configurados; protocolo y manifiestos; actualizar CLI, fixtures y README correspondientes. |
| `src/challenge/derive.py`, `models.py` | Generaciones/procedencia y datos ampliados; adaptar solo restricciones realmente necesarias. Hoy `build` exige Qwen3-8B y `checked_run` metadata Ollama; un cambio de profesor/backend obliga a adaptar y probar esos controles explícitamente. |
| `src/challenge/evaluate.py` | Reutilizar `verify`/`metrics`; no usar `compare_local` como comparación de entrenamiento: exige cuatro modelos locales y protocolo histórico. |
| `src/challenge/train.py` — nuevo | Entradas SFT/GRPO, adaptadores, continuación, configuración, logs y reanudación. |
| `src/challenge/evaluate_hf.py` — nuevo | Control y checkpoints con backend entrenable; salida cruda trazable y puntuación común. |
| `pyproject.toml`, `uv.lock` | Dependencias fijadas en grupo de entrenamiento; conservar pruebas sin GPU. |
| `tests/test_challenge.py`, `tests/test_families.py`, `tests/test_training.py` — último nuevo | Regresiones históricas, seis familias, datos, recompensas, integración y métricas. Ajustar fixtures a política nueva, no borrar pruebas que revelen incompatibilidades. |
| `scripts/report_training.py` — nuevo | Tablas y curvas desde logs/evaluaciones, sin nuevas inferencias; reutilizar matplotlib ya disponible en el grupo report. |
| `data/units/project-e2/` — nuevo | `dataset/`, `derived/`, `runs/`, `analysis/`, `audits/`, `validation/`: solo crear carpetas al producir su contenido. |
| `deliveries/project-2-progress/` — nuevo | PDF, fuentes, figuras/tablas y README de reproducción. Pesos/adaptadores grandes fuera de Git, con ubicación y checksum. |

Por corrida registrar commit, versiones de librerías, checkpoint/tokenizer, adaptador inicial/final, dataset/verificador y hashes, GPU/VRAM, precisión, configuración LoRA, semillas, grupo/batch, KL/referencia, muestreo, límites, pasos, duración, tokens y causa de terminación. Separar métricas de entrenamiento y evaluación. No guardar credenciales en artefactos.

## 7 Cómo medir y analizar la implementación

| Pregunta de análisis | Medición y comparación | Interpretación permitida |
| --- | --- | --- |
| ¿La ampliación aporta diversidad útil? | Conteos por familia/nivel/estructura, problemas físicos únicos, conversiones y errores del control; tabla antes/después de cobertura. | Más familias/filas no garantizan señal. Comparar rutas sobre el mismo dataset nuevo, no atribuir diferencias contra el desafío solo al entrenamiento. |
| ¿El modelo recibe señal en GRPO? | Media de recompensa, desviación dentro de grupos y fracción de grupos con todo 0, todo 1 o mezcla; pérdida/gradientes finitos. | Si todos los grupos son constantes, investigar falta de ventaja por recompensa, integración o calibración; la media global por sí sola no basta. |
| ¿Mejora respecto del control? | pass@1/pass@3 y errores por celda en eval común; diferencia contra paso cero; recompensa en train frente a eval. | Reportar mejora, estabilidad o degradación. Éxito del proyecto no equivale a confirmar la hipótesis. |
| ¿El SFT previo es más eficiente? | Curvas pass@1 en eval frente a horas acumuladas de entrenamiento y tokens; comparar ambas ramas a presupuestos comunes incluyendo SFT. | No comparar solo el tiempo de RL posterior. No equiparar una hora de A30 con una de RTX 3050. |
| ¿Aprende cálculo o formato? | Tasas de resultado interpretable, equivalencia numérica en SI, unidad pedida, errores numéricos y truncamiento, calculadas sobre todas las respuestas. | No restringir exactitud a respuestas parseadas y presentar ese subconjunto como exactitud global. Mantener `unparsed` separado de error matemático. |
| ¿Son genuinos los éxitos? | Número revisado y proporción humana de éxitos genuinos por estrato, con ejemplos y motivos de rechazo. | La recompensa final no certifica pasos; una muestra pequeña no certifica todo el corpus. |
| ¿Qué produjo una corrección? | Caso original, versión/configuración anterior, cambio, regresión y repetición comparable posterior. | Evitar atribuir causalidad si cambian a la vez dataset, modelo y recompensa; declarar los factores cambiados. |

Métricas obligatorias del protocolo propio: pass@1 y pass@3 por familia/nivel. Con tres muestras por tarea, pass@1 es el promedio de aciertos entre las muestras y pass@3 indica si hubo al menos un acierto. Si hay distinto número de muestras, no mezclar corridas incompletas ni publicar pass@3 con menos de tres; usar la validación y estimador existentes.

Las semillas de generación 42–44 no son tres semillas de entrenamiento. Para E2, registrar al menos una semilla de entrenamiento por ruta; repetir con varias en E3 si el cómputo permite. Si se presentan intervalos de incertidumbre, remuestrear por problema físico, manteniendo juntas sus variantes y respuestas; no tratar todas las generaciones como observaciones independientes. Esos intervalos no capturan variación entre semillas de entrenamiento que no se hayan ejecutado.

Figuras previstas: **recompensa GRPO frente a pasos**, **pass@1 en eval frente a cómputo acumulado** y **desglose de errores por familia/nivel**. Conservar datos sin suavizar; identificar cualquier ventana de suavizado. La pérdida SFT puede añadirse como diagnóstico, nunca como reemplazo de recompensa.

## 8 Pruebas necesarias y criterios de éxito

Esta matriz define la validación del alcance completo de E2. La validación ya ejecutada de I1 figura en las secciones 2 y 5; no acredita los componentes aún pendientes. Registrar cada ejecución en `data/units/project-e2/validation/` con comando, commit, configuración, resultado y ruta de evidencia.

| ID | Prueba | Criterio de aceptación |
| --- | --- | --- |
| V1 | Suite existente y del PR #6; análisis estático de archivos afectados. | Todas las pruebas aplicables pasan; sin regresiones no explicadas; reproducción histórica conserva datos y código normativo correspondiente. |
| V2 | Fixtures independientes y ataques al verificador, en seis familias. | Cantidades correctas y alias admitidos reciben 1; errores fuera de tolerancia, unidades incorrectas, contradicciones, no finitos y ambigüedades rechazadas. Casos en ambos lados del límite del 1%; prompt desconocido produce error explícito. |
| V3 | Regeneración y chequeo integral del dataset. | Misma configuración reproduce filas/manifiesto; cambiar datos, código o protocolo se detecta; 36 celdas equilibradas y tres variantes por problema. |
| V4 | Cruces y campos privados. | Intersección vacía de `physical_key` entre splits y con exclusiones; ID/prompt únicos; ningún answer_si o registro privado pasa a entradas del modelo. |
| V5 | Revalidación completa de derivados y procedencia. | 100% de SFT pertenece a train y obtiene recompensa 1; 100% de pares comparte tarea/prompt, con preferida 1 y rechazada 0 clasificada como error válido; hashes/orígenes y deduplicación verificables. |
| V6 | Cobertura y auditoría de datos. | Conteos por las 18 celdas, tareas únicas y descartes; metas comparadas con resultados; excepciones justificadas; ninguna revisión de agentes se presenta como humana. |
| V7 | Prueba de entrenamiento pequeña en GPU real. | Pérdida/gradientes finitos, parámetros entrenables cambian, guardado/recarga conserva pesos y evaluación; reanudación preserva estado necesario y rechaza mezcla incompatible. Sin OOM en la configuración seleccionada. |
| V8 | Métricas con fixtures conocidos y evaluación del control. | Ejemplo de dos tareas con 3 muestras cada una, una con 1 acierto y otra con 0: pass@1=1/6 y pass@3=1/2; cobertura/truncamiento correctos; mismas respuestas producen mismas métricas con cualquier runner. |
| V9 | Integración SFT/GRPO y continuación. | Máscara de pérdida correcta; recompensas adaptadas iguales a `reward`; pasos reales; ramas parten de checkpoint correcto; SFT→GRPO carga el adaptador SFT y registra su costo. |
| V10 | Logs, curvas y costo comparable. | Paso cero y al menos tres checkpoints posteriores; ramas RL con datos por paso; figuras recalculables; costo SFT incluido; resultados incompletos claramente identificados y fuera de comparaciones definitivas. |
| V11 | Auditoría humana e iteraciones. | Muestra seleccionada reproduciblemente, auditores y denominadores; defectos encontrados tienen regresión, revalidación y repetición pertinente, o permanecen identificados como pendientes. |
| V12 | Reproducción editorial desde copia limpia. | Tablas/figuras coinciden con evaluaciones guardadas; PDF compila sin citas rotas ni desbordamientos; lectura visual y cotejo de cifras; README contiene comandos ejecutables y requisitos R1–R11 trazables. |

Comando base existente: `uv run python -m unittest discover -s tests -v`. Ejecutar lint/tipado/seguridad sobre el código modificado siguiendo [tests/README.md](../../tests/README.md), con herramientas compatibles y fijadas. Añadir pruebas de integración pequeñas que no requieran descargas a la suite ordinaria; la prueba GPU es una validación separada y obligatoria antes de corridas largas. Los comandos nuevos de entrenamiento y reporte se documentarán cuando estén implementados, sin presentar CLI inexistentes como ejecutables.

### Criterio global de cierre

- [ ] R1–R11 tienen evidencia asociada y las pruebas aplicables V1–V12 están aprobadas.
- [ ] Seis familias integradas, datos ampliados/revisados y evaluación sin fuga; cualquier desviación de volumen está justificada cuantitativamente.
- [ ] Control, SFT, solo GRPO y SFT→GRPO ejecutados con protocolo y costo trazables; curvas y diagnóstico disponibles.
- [ ] Las conclusiones distinguen progreso técnico, señal de aprendizaje y efecto científico del SFT previo.
- [ ] Informe revisado y respaldo reproducible; envío registrado por separado cuando ocurra.

No se exige una mejora artificial para declarar exitosa la implementación. Sí se exige evidencia de ejecución correcta y análisis de resultados, incluso nulos. Un fallo de infraestructura o una curva producida sin actualizar pesos no se presenta como resultado científico negativo. Si falta una parte del alcance, permanece pendiente: no se redefine silenciosamente E2 como solo planificación.

## 9 Riesgos y decisiones durante la ejecución

| Riesgo | Respuesta prevista |
| --- | --- |
| Cambios posteriores sobre las familias integradas | Partir de `061ca08`, revisar el nuevo diff y repetir regresiones de familias, referencias y datos afectados. |
| GRPO no cabe en la GPU disponible | Ajustar batch/grupo/longitud sin destruir señal; si sigue inviable, gestionar recurso alternativo y repetir piloto. Acceso pasado a A30 no garantiza disponibilidad actual. |
| Volumen de generación o auditoría excede capacidad | Medir retención/costo por celda y producir por lotes reanudables; priorizar cobertura y problemas únicos; justificar reducción sin inflar conteos. |
| Suelo o techo impide señal | Revisar errores de integración, extracción y truncamiento antes de cambiar tareas; recalibrar solo con desarrollo/eval, versionar y repetir control. |
| Cambia verificador o dataset después de iniciar | Conservar evidencia previa, identificar rutas afectadas y repetir comparaciones con versión común; mantener test independiente. |
| Datos grandes o servicios externos | Conservar ubicaciones/versiones/checksums; no subir pesos ni secretos. Cualquier generación pagada requiere presupuesto específico, no reutilizar autorizaciones históricas del desafío. |

Estado actualizado: PR #6 aprobado, mergeado y traído a ambas ramas locales; I1 completada con pruebas y reproducción offline. El plan adopta las seis familias como base integrada. Continúan I2 e I4, seguidas por la ampliación/congelamiento de datos y los entrenamientos. No se han generado datos nuevos ni ejecutado entrenamientos o pruebas de GPU; el cierre sigue la matriz de aceptación.

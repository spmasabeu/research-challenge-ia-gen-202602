# Plan de ejecución del desafío de unidades

Fecha base: 2026-11-07, America/Santiago. Estado: ejecución autorizada; C0 cerrado; C1 cerrado; C2 cerrado; C3 cerrado; C4 cerrado; C5 cerrado; C6 cerrado; C7 cerrado.
Objetivo: entregar entorno, tareas, datos SFT/DPO e informe de evaluación; no entrenar modelos.
Fuentes: [aclaración docente compartida](../contexto/2026-11-07_193927_aclaraciones_docentes_desafio.md), [enunciado](../../DesafioInvestigacion-2026.pdf), [requisitos desglosados](../contexto/2026-11-07_123729_requisitos_metodologia_entregables_units.md), [spike](../../spikes/units/README.md) e [informe exploratorio](../../spikes/units/report.md).

## Reglas y registro

- Units es el tema seleccionado. `src/challenge/` contenía placeholders al inicio: escribir código nuevo; el spike sirve como evidencia, no como código que deba reutilizarse.
- Implementar el mínimo que cumpla el contrato: biblioteca estándar, flujo directo, sin abstracciones, funciones de un uso ni ramas para escenarios ajenos al alcance. Mantener pruebas y validación de entradas que puedan producir falsos aciertos.
- Seguir C0–C7; C5 y C6 pueden avanzar después de C4 sin competir por recursos. Implementación autorizada; crear snapshot solo tras validación.
- Bitácora vigente: [ejecución y evidencia](../contexto/2026-11-07_200958_bitacora_ejecucion_desafio_units.md). Registrar checkpoint, fecha, configuración, versiones, comandos, resultados y pendientes; continuar desde el primero incompleto.
- Guardar experimentos en `data/units/runs/<id>/`, sin sobrescribir; distinguir inferencia nueva de recalificación de respuestas existentes.
- Cantidades, semillas, umbrales y muestreo siguientes son decisiones propuestas para este plan, no mínimos del PDF; confirmar en C1 y revisar con el piloto.
- Recursos confirmados el 2026-11-07: RTX 3050 Laptop de 6 GB, RAM física detectada 30,5 GiB (aproximadamente 32 GB), reserva histórica OpenAI USD 10 (no autoriza OpenRouter); OpenRouter habilitado con tope autorizado USD 5 para esta comparación. Registrar además CPU, driver, backend, cuantización y tiempos reales al ejecutar.
- La credencial OpenAI permanece en `.env` local ignorado por Git, fuera de logs y entrega; no usarla. OpenRouter requiere credencial propia y presupuesto específico antes de llamadas pagadas.
- Alcance acordado: tres pequeños locales y Qwen3-8B como profesor abierto; frontera comprometida después de C6 y antes de cerrar C7: candidato DeepSeek-V4-Pro-0813 vía OpenRouter, acceso habilitado y tope USD 5 autorizado; el profesor no sustituye al tercer pequeño ni es frontera.

## Fase 0 Verificar antecedentes y entorno

**Dependencias:** acceso al repositorio; no requiere modelos ni GPU.

1. [x] Leer las instrucciones AGENTS.md aportadas en la conversación y sus referencias `/home/spalmam/.codex/RTK.md` y `/home/spalmam/.codex/CAVEMAN.md`; consultar el README raíz para convenciones del repositorio.
2. [x] Extraer obligaciones de `DesafioInvestigacion-2026.pdf`, secciones I–III; leer también la aclaración docente enlazada y usar la bajada actualizada para distinguir mínimos, recomendaciones y propuestas; no mezclar con `ProyectoCurso-2026.pdf`.
3. [x] Revisar Git e inventariar `spikes/units/{README.md,report.md,results/}`; preservar artefactos y cambios existentes. Registrar que `src/challenge/` todavía no implementa el entorno.
4. [x] Preparar Git, uv y Python 3.12; ejecutar `uv sync --locked`. `pyproject.toml` no declara dependencias Python externas: generación, verificación, pruebas y hashes usarán la biblioteca estándar.
5. [x] Desde la raíz ejecutar `uv run --no-project --isolated --python 3.12 python -m unittest discover -s spikes/units -v` y `uv run --no-project --isolated --python 3.12 python spikes/units/evaluate.py check spikes/units/results`.
6. [x] Registrar resultados automáticos y revisiones humanas por separado; actualizar decisiones y descripciones vigentes para dejar units seleccionado y scheduling como antecedente histórico.

**Salida:** inventario, comprobación y selección documentados en la bitácora.
**Éxito C0:** resultados exploratorios verificables y brechas identificadas. Si falla, corregir integridad o documentar bloqueo antes de continuar; no alterar hashes para ocultarlo.

## Fase 1 Definir exactamente el problema y los recursos

**Dependencia:** C0 cerrado.

1. [x] Delimitar idioma español, datos positivos, fórmulas y equivalencias explícitas, respuesta directa en un turno y resultado de cantidad más unidad; sin herramientas ni necesidad de memorizar física. Fijar rangos y unidades admitidos por familia.
2. [x] Usar familias de problemas físicos: velocidad `v=d/t` (distancia/tiempo), energía cinética `E=m*v²/2` (masa y velocidad) y luminosidad `L=4*pi*d²*F` (distancia y flujo recibido). Familia significa fórmula y magnitudes implicadas, no modelo ni dificultad.
3. [x] Definir operaciones como pasos aritméticos de la fórmula; conversiones como cambios de unidad antes/después del cálculo; representación como decimal o notación científica. Son posibles fuentes de dificultad, no causas demostradas de error.
4. [x] Calibrado: fácil sin conversiones, medio con una y difícil con tres (luminosidad: dos, salidaW) entre entradas/salida. Registrar operaciones y representación por tarea; si cambian simultáneamente, no atribuir la caída solo a conversiones. Contrastar estos niveles en C3.
5. [x] Comparar con bibliografía pertinente y justificar diversidad y originalidad mediante composición, variaciones de pregunta o diseño de generación; cambiar solo números no basta. Ajustar el diseño antes de C4 si esa justificación es débil.
6. [x] Confirmar tipos y reglas de la interfaz común. Proponer `reward(prompt: str, completion: str) -> float`, con tabla privada que asocia cada prompt exacto a su tarea/referencia; esta tabla no se envía al modelo y se entrega con el entorno.
7. [x] Registrar los tres pequeños acordados: Qwen3-1.7B objetivo, Llama 3.2-1B y SmolLM2-1.7B-Instruct comparadores; confirmar ejecución local y comportamiento en español mediante piloto. No contar al profesor 8B como tercer pequeño.
8. [x] Elegir profesor abierto mayor: modelo con pesos accesibles y más parámetros que el objetivo, usado para producir soluciones SFT; no es un docente humano ni necesariamente un modelo de frontera. Selección acordada: Qwen3-8B cuantizado local; comprobar memoria, velocidad y calidad antes del lote completo. Evaluarlo también como comparador mayor si es viable y dejar la frontera para después de C6.
9. [x] Para cada modelo fijar identificador, revisión, licencia, parámetros, cuantización, acceso y backend: programa/servicio que ejecuta inferencia. Ollama es el backend local del spike; no es obligatorio y no se instala para comprobar artefactos sin inferencia.
10. [x] Medir cinco respuestas preliminares por modelo fuera de test; estimar tokens, segundos, espacio y costo por respuesta. Multiplicar por intentos previstos y fijar presupuesto y límites antes de lotes grandes.

| Elemento | Propuesta y motivo |
| --- | --- |
| Piloto | 90 tareas: 10 problemas físicos por familia, cada uno en tres niveles; cubre nueve combinaciones familia/nivel. |
| Final | C1: 180 tareas, con 90 train, 36 eval y 54 test; reduce ~36–75 h de profesor originales a ~1,2 h. Confirmar cobertura y tamaño en C3; justificación y mediciones en bitácora. |
| Muestras de línea base | Tres respuestas por prompt, índices 0–2, semillas 42/43/44 cuando se admitan; separado del muestreo de train. Tres pequeños × 54 tareas × 3 = 486 respuestas; profesor viable añade 162. |
| Inferencia | C1: temperatura 0,7, contexto 2048, batch128, num_gpu99 y hasta1024 tokens; profesor inicialmente2048 tokens, ajustar tras control conciso y memoria. Documentar efectivos. |
| SFT/DPO | Metas orientativas docentes: ~4.000 trazas y ~2.000 pares, con todos los niveles. C1: cuatro respuestas del profesor por tarea (360 candidatas); hasta tres del objetivo para negativos si faltan. Menor escala justificada por cómputo; sin inflar cuotas. Conservar respuestas correctas distintas; justificar menores volúmenes. |

**Salida:** especificación y protocolo fechados con modelos, rangos, formatos, tolerancia y presupuesto.
**Éxito C1:** opciones accesibles y decisiones ejecutables. El PDF no fija cantidades: estas permiten cobertura balanceada, sin garantizar suficiencia estadística ni originalidad. Si falta cómputo, ajustar y justificar antes de ejecutar.

## Fase 2 Escribir generador recompensa y pruebas mínimas

**Dependencia:** C1 cerrado. Escribir desde cero en `src/challenge/`, con pruebas en `tests/`.

1. [x] Crear generador determinista que reciba semilla y número de problemas por familia; cada problema produce tres variantes con el mismo `pair_id`, datos físicos equivalentes, ID, familia, nivel, prompt y referencia privada en unidades SI.
2. [x] Generar primero las 90 tareas piloto; las 180 finales propuestas se generan solo en C4 tras calibrar. Las referencias se calculan por fórmula, nunca se copian de respuestas de modelos.
3. [x] Crear fixtures independientes con resultados fijados: `110 m/5 s=22 m/s`, `m=2 kg,v=3 m/s => 9 J`, `d=1 m,F=1 W/m² => 4*pi W`; añadir equivalentes convertidos con valores esperados explícitos. No llamar al generador para obtener el valor esperado del test.
4. [x] Para cada tarea, recalcular además la referencia desde las cantidades que aparecen en el prompt, con fórmulas y conversiones del comprobador, sin leer su referencia. Comparar con tolerancia de redondeo de generación, por ejemplo `1e-10` relativa, distinta del 1% de recompensa.
5. [x] Definir salida aceptada: un resultado terminal inequívoco en JSON con `value` y `unit`, o cantidad/unidad terminal; admitir texto de desarrollo previo. Cubrir equivalencias de unidad, coma decimal y notación científica sin ejecutar expresiones del modelo.
6. [x] Implementar `reward`: localizar tarea por prompt, extraer resultado, convertir a SI y devolver `1.0` si dimensión compatible y `abs(valor-ref) <= 0.01*abs(ref)`; devolver `0.0` para resultado incorrecto o inválido. Referencias positivas por alcance; prompt desconocido es error de entrada del harness, no fallo matemático del modelo.
7. [x] Probar contradicciones con pares entrada/etiqueta esperada: dos resultados finales `22 m/s` y `0 m/s` se rechazan; `79.2 km/h` y `22 m/s` expresan el mismo resultado; desarrollo `22 m/s` seguido de `FINAL: 0 m/s` es incorrecto, sin rescatar el número previo.
8. [x] Añadir pruebas concretas para cantidad ausente, unidad incompatible, JSON con claves duplicadas y números no finitos; no construir soporte para formatos hipotéticos. Todo nuevo formato observado se decide y prueba en desarrollo, nunca buscando coincidencias con la referencia.
9. [x] Comprobar recompensa y métricas con fixtures pequeños conocidos; ejecutar pruebas y controles del código escrito. Funciones solo para interfaz exigida o lógica compartida; sin plataforma genérica ni duplicación de ramas por modelo.

**Salida:** código mínimo, fixtures, pruebas y contrato del verificador; este mismo verificador se usará en fases 3–6.
**Éxito C2:** referencias comprobadas, equivalencias previstas aceptadas y contradicciones inválidas rechazadas. Si falla, corregir la causa y conservar un test que la reproduzca antes de inferir.

## Fase 3 Generar piloto calibrar y registrar cambios

**Dependencia:** C2 cerrado y objetivo accesible.

1. [x] Generar piloto con semilla 4300: diez problemas por familia y tres variantes cada uno. Excluir sus datos físicos de los finales; ejecutar las tres muestras de todas las tareas, no seleccionar solo fáciles o errores.
2. [x] Guardar una fila por `(modelo, task_id, sample_index)` con prompt exacto, respuesta cruda, configuración, duración, tokens disponibles y motivo de finalización.
3. [x] Etiquetar `correct` si recompensa 1; `numeric` si se extrae unidad compatible pero valor fuera de tolerancia; `unit` si unidad incompatible; `unparsed` si falta resultado inequívoco o formato admitido. Truncamiento es una marca adicional, no una causa matemática demostrada.
4. [x] Definir formato nuevo como una estructura no cubierta por el parser —por ejemplo, número y unidad en líneas distintas—; guardar ejemplo y decidir si es válido según contrato. `unparsed` no demuestra error de razonamiento.
5. [x] Agrupar filas por familia, nivel y ambos; contar cada etiqueta. Cobertura = respuestas interpretadas / total; aciertos = `correct` / total. Las categorías de fallo son las etiquetas anteriores, no explicaciones causales; describir conversión o aritmética tras revisar la traza.
6. [x] Revisar cinco respuestas por combinación familia/nivel, ordenadas por ID y muestra, procurando incluir acierto y error donde existan; revisar también todos los patrones nuevos de formato.
7. [x] Usar como alarmas propuestas techo ≥90% y suelo ≤10% de aciertos por combinación. Techo: casi todo se resuelve; suelo: casi nada. Aumentar/reducir conversiones, pasos o rango numérico y volver a medir; conservar fáciles como controles si se justifica, sin imponer estos porcentajes como regla del curso.
8. [x] Antes de cada cambio conservar código/configuración exactos como versión v1, v2… y respuestas intactas; registrar motivo. Recalificar según fase 6 si cambia solo el verificador; si cambia prompt, tarea o generación, repetir inferencia en una carpeta nueva con modelos y parámetros documentados.
9. [x] Registrar segundos y tokens por intento, GB de artefactos, hardware y tarifa si hay servicio pago; totalizar costo real y proyectar restantes. Informar limitaciones observadas: tamaño de muestra, dependencia entre tríos, formatos sin interpretar y truncamientos.

**Salida:** piloto, tablas por familia/nivel, ejemplos y bitácora de ajustes, límites y costo.
**Éxito C3:** hay aciertos y errores verificables en el núcleo de tareas; niveles contrastados y extracción suficiente para interpretar resultados. Si falla, volver a C1/C2 y repetir piloto antes de congelar.

## Fase 4 Aplicar split comprobar y congelar

**Dependencia:** C3 cerrado.

1. [x] Con semilla 4301 generar 20 problemas físicos distintos por familia, excluyendo spike original y todos los pilotos; producir tres variantes por problema. Representar cada problema por familia, estructura y magnitudes normalizadas a SI para detectar equivalentes.
2. [x] Barajar los 20 grupos por familia con semilla 4302 y asignar 10 a train, 4 a eval y 6 a test; incluir las tres variantes juntas. Resultado propuesto: 90/36/54 tareas. Revisar estas cantidades en C1/C3 según recursos, antes de congelar.
3. [x] Contar `(split,familia,nivel)`: esperar 10/4/6 tareas en cada celda. Comprobar IDs y prompts únicos, y conjuntos de claves físicas y `pair_id` disjuntos entre splits; documentar que compartir plantillas limita la generalización medida.
4. [x] Recalcular todas las referencias con el comprobador independiente de fase 2 y verificar que los mensajes al modelo no incorporen campos privados. Usar eval para ajustes, sin observar resultados de test.
5. [x] Congelar archivos JSONL, semillas, configuración, código y catálogo de unidades en un manifiesto con SHA-256. Congelar significa guardar versión y dejar de modificarla; un cambio produce una versión nueva, no reemplaza la anterior.
6. [x] Los hashes son huellas de archivos para comprobar que no cambiaron; el PDF no los exige expresamente. Calcularlos con `hashlib` de Python sobre tareas, código evaluador y configuración; registrar también versión del modelo cuando sea identificable.

**Salida:** splits y manifiesto en `data/units/`; instrucciones para regenerar y comparar huellas.
**Éxito C4:** cantidades correctas, referencias verificadas y sin grupos cruzados. Si test se usa para ajustar, reservar uno nuevo; revisar y versionar todos los artefactos afectados.

## Fase 5 Crear verificar y auditar SFT y DPO

**Dependencias:** C4 cerrado y profesor abierto mayor elegido en C1; usar exactamente el verificador definido en C2 y congelado en C4.

1. [x] Enviar solo train al profesor y muestrear cuatro respuestas por tarea con semillas registradas; verificar cada una. Si faltan datos en alguna dificultad, ampliar hasta ocho; registrar tiempo, rendimiento y necesidad de reducir o ampliar la generación sin asumir que todas pasarán.
2. [x] Para SFT conservar soluciones correctas distintas, permitiendo varias por tarea; no limitar a una ni copiar trazas programáticas para llegar a 4.000. Comprobar coherencia de pasos. Auditar significa contrastar manualmente datos usados, conversiones, operaciones y conclusión con el problema; no basta con que el número final pase el 1%.
3. [x] Auditar cinco candidatas por combinación familia/nivel usando selección aleatoria con semilla 4303 —o todas si hay menos—; registrar ID, juicio, motivo y acción. Si aparece un defecto, descartar o regenerar la traza manteniendo procedencia y ampliar revisión a la familia/nivel afectada. Declarar que una muestra no certifica todas las trazas.
4. [x] Para DPO, agrupar respuestas por `task_id`: emparejar correctas e incorrectas inequívocas del mismo prompt por orden de muestra, hasta dos pares distintos por tarea; evitar producto cartesiano y contabilizar tareas únicas y reutilización. No limitar todo el dataset a un par por tarea. Si falta negativo, usar hasta tres respuestas adicionales del objetivo sobre esa tarea de train; no fabricar negativos a partir de `unparsed` sin resolver su interpretación.
5. [x] Guardar SFT como `{task_id,prompt,completion}` y DPO como `{task_id,prompt,chosen,rejected}`, con procedencia de ambas respuestas y versión del verificador en metadatos.
6. [x] Deduplicar por `(task_id,completion)` en SFT y `(task_id,chosen,rejected)` en DPO, conservando IDs de origen; comprobar que todo `task_id` pertenece a train. No borrar variantes físicas legítimas por tener la misma respuesta numérica.
7. [x] Comprobar carga de archivos, recompensa de preferidos y error explícito de rechazados; publicar generados, retenidos, descartados y cobertura por familia/nivel, sin rellenar cuotas con ejemplos inválidos.

**Salida:** SFT/DPO, respuestas originales y registro de filtrado/auditoría bajo `data/units/`.
**Éxito C5:** ambos datasets utilizables, trazables y derivados solo de train; reportar retenidas por dificultad frente a ~4.000/~2.000. Si falla el verificador, volver a C2 y revisar C3–C4. Si se obtiene menos, justificar con cómputo, tasa de filtrado y diversidad; no duplicar para cumplir cifras orientativas.

## Fase 6 Evaluar con trazabilidad de resultados y recálculos

**Dependencias:** C4 cerrado y modelos accesibles; no necesita esperar C5.

1. [x] Verificar las huellas del manifiesto para evitar evaluar otra versión accidentalmente; probar cinco prompts de desarrollo en cada motor/servicio de inferencia y guardar sus parámetros efectivos.
2. [x] Evaluar los mismos 54 prompts de test con los tres pequeños sin entrenar, tres respuestas cada uno: 486 filas previstas. Evaluar además el profesor si es viable; justificar por recursos la omisión de mediano/grande, dejando frontera para después de C6. Documentar diferencias inevitables de motor, contexto, cuantización y semillas no admitidas.
3. [x] Guardar cada respuesta inmediatamente con su clave `(modelo,task_id,muestra)`; reanudar únicamente claves faltantes con configuración idéntica. Completar corridas interrumpidas antes de comparar modelos.
4. [x] Verificar completitud comparando claves esperadas y guardadas; unicidad comprobando una fila por clave; prompts comparando texto exacto con la tarea; configuración cotejando modelo, muestras y versión con el manifiesto. Registrar truncamientos y respuestas vacías, sin omitirlas del denominador.
5. [x] Para cada tarea contar `c` aciertos de `n=3`; pass@1 estimado es `c/3` y pass@3 es 1 si `c>0`, 0 si no. Promediar por dificultad; para otro k usar `1-C(n-c,k)/C(n,k)` con `n>=k`. Informar n, k y número de tareas por tabla.
6. [x] Recalcular pass@1/pass@3, cobertura y conteos `correct/numeric/unit/unparsed` por dificultad y familia desde respuestas guardadas, sin inferencia; contrastar con resúmenes. Mantener resultados manuales aparte.
7. [x] Guardar cada recalificación en `runs/<id>/scores/vN/` con métricas y etiquetas; registrar versión anterior/nueva del verificador, motivo, IDs que cambiaron de estado y diferencias de métricas. Preservar código de ambas versiones y huellas de respuestas para demostrar que no cambiaron.
8. [x] En la bitácora escribir «v1: X; cambio Z; v2: Y», separando mejora del parser de cambio en capacidad del modelo. Si cambia la tarea, generar una corrida nueva; si test motivó ajustes, aplicar la regla de independencia de C4.
9. [x] Publicar todos los modelos con una misma versión final del verificador y ejemplos de fortalezas/fallos; explicar dependencia de variantes, incertidumbre de extracción y costos. No afirmar mejora por entrenamiento: aquí no se entrenó.

**Salida:** respuestas, metadatos, métricas versionadas, historial de recálculos e informe de línea base.
**Éxito C6:** corridas completas y métricas reproducibles con evaluación común; cada cambio puede reconstruirse. Si falla, completar datos o corregir cálculo sin sobrescribir evidencia.

## Fase 7 Validar informe y producir snapshot de entrega

**Dependencias:** C5 y C6 cerrados; comparación de frontera y template LaTeX del usuario.

0. [x] Tras C6, verificar candidato OpenRouter, acceso y presupuesto específico; mismo test/verificador congelados, tres muestras/tarea. Registrar versión, parámetros efectivos, límites, costo, métricas, ejemplos y limitaciones. Sin acceso, validar todo lo local y mantener frontera y C7 pendientes.

1. [x] Preparar descripción e informe con el template LaTeX: problema, generación, volumen, particiones, niveles, ejemplos, fortalezas/debilidades, modelos, pass@1/pass@k, robustez y calibración; compilar PDF y comprobar tablas y referencias. LaTeX es elección del equipo, no formato impuesto por el desafío.
2. [x] Documentar comandos reales de instalación, pruebas, generación, uso de `reward`, carga SFT/DPO y reproducción de métricas; ejecutar desde un entorno limpio y corregir rutas personales o dependencias ocultas.
3. [x] Revisar evidencia por requisito y preparar defensa: por qué estas familias/dificultades, cómo se comprobaron referencias, equivalencias y ataques, separación de splits, calidad de SFT/DPO y límites de comparación.
4. [x] Solo cuando todo esté validado, crear `deliveries/challenge/` y copiar la versión final: `code/`, `data/`, `results/`, `report/` con fuentes LaTeX/template/figuras/PDF y `README.md` con requisitos, comandos y mapa de evidencia. Incluir el entorno Python fijado; no depender de archivos fuera de esa carpeta ni de symlinks al repositorio.
5. [x] Incluir únicamente resultados finales en el snapshot; adjuntar resumen y evidencias mínimas del historial de recálculos, conservando el historial completo en trabajo. No copiar secretos, entornos virtuales ni pesos de modelos; documentar cómo obtener modelos si se desea repetir inferencia.
6. [x] Repetir pruebas y recálculo desde una copia aislada del snapshot; cotejar hashes, comprobar acceso y plazo/canal vigentes del curso. Registrar validación y mantener inmutable el snapshot; cualquier corrección exige validarlo de nuevo.

| Entregable oficial | Evidencia autocontenida en `deliveries/challenge/` |
| --- | --- |
| E1 Harness | Código, interfaz común, pruebas, instrucciones, generador y train/eval/test. |
| E2 Descripción del entorno/dataset | Informe: problema, generación, particiones, dificultad, ejemplos, fortalezas y debilidades. |
| E3 Datos SFT/DPO | Ambos datasets, modelo abierto mayor, procedimiento, procedencia, filtrado y auditoría. |
| E4 Informe de línea base | Al menos tres pequeños, pass@1/pass@k por dificultad, ejemplos, robustez y calibración; justificar ampliaciones mediano/grande omitidas. |

**Éxito C7:** cuatro entregables completos, PDF compilado y snapshot validado sin archivos externos; cualquier recurso externo de inferencia queda declarado. Si falta template o evidencia, mantener la fase abierta y no crear una entrega aparente.
**Fuera de alcance:** entrenamiento SFT/DPO/RL, comparación de cinco caminos, paper/poster/video del proyecto. En este desafío sí se entregan datos SFT/DPO.

## Revisión posterior del PR #3, 2026-11-09

C0–C7 conservan su cierre técnico. Se incorpora el feedback como límites
explícitos del informe y del paquete, preservando verifier-9, métricas y SFT/DPO.
Se recompilan PDF y ZIP y se verifica integridad y reproducción offline;
no se reabren inferencias ni se cambia el test. Las mejoras del verificador
quedan para antes del entrenamiento del proyecto, con versión nueva y pruebas.
Evidencia de esta revisión: `data/units/validation/pr3-feedback.json`.

## Empaquetado mínimo autorizado, 2026-11-09

La entrega vigente es `deliveries/challenge-clean/challenge.zip`; el paquete
anterior se conserva sin cambios. Los nombres `data/tasks` y `data/training`
identifican los únicos conjuntos entregados, y README integra el mapa de evidencia.
Las fuentes LaTeX, figuras, enunciados y el historial quedan en el repositorio.
La aceptación del paquete consiste en reproducir tareas, SFT/DPO, métricas y
costos desde sus archivos, sin requerir recompilar el PDF ni repetir inferencias.
Los siete bloques offline documentados y las 13 pruebas pasan desde una copia
aislada con entorno nuevo. Evidencia: `data/units/validation/clean-delivery.json`.

## Restricción al mínimo del enunciado, 2026-11-09

Por instrucción del usuario, `challenge-clean` excluye `results/` y
`validation.json`. La aceptación del ZIP se limita a instalación/pruebas,
regeneración de tareas y comprobación de SFT/DPO, con cinco bloques offline
validados desde copia aislada. Las métricas quedan en el informe y su recálculo
requiere el respaldo del repositorio enlazado en README. Este alcance sustituye
la reproducción completa descrita en el apartado anterior. Evidencia de trabajo,
fuera de la entrega: `data/units/validation/minimal-delivery.json`.

# Bitácora de ejecución del desafío units

Inicio: 2026-11-07T20:10:02.057186-03:00. Responsable: agente principal.
Plan: [C0–C7](../plans/2026-11-07_130305_ejecucion_desafio_units.md).

## Estado

C0 cerrado. C1 en curso. C2–C7 pendientes. No existía bitácora previa.
Cambios existentes preservados; sin commits. Inventario inicial: `../../data/units/preflight/2026-11-07_200958/git.txt`.

## Alcance vigente

Última instrucción sustituye exclusión anterior: primero tres pequeños locales y profesor Qwen3-8B; después de C6 frontera candidata DeepSeek-V4-Pro-0813 vía Together AI, tres respuestas por tarea del mismo test/verificador. Requiere credencial y presupuesto específicos; no usar OpenAI ni realizar llamadas pagadas ahora. C7 abierto si faltan frontera o template del usuario. Sin entrenamiento.

## C0 — evidencia y brechas

Leídos README, RTK/CAVEMAN, PDF desafío mediante pdftotext, aclaración docente, requisitos, decisiones, plan y documentación del spike. No hay AGENTS.md físicos aplicables ni .codegraph en raíz. src/challenge contiene placeholders sin llamadores implementados. PDF exige E1–E4, recompensa, referencias por código, splits, SFT de profesor abierto y DPO. Aclaración fija tres pequeños; metas de datos orientativas. Fecha PDF: 6 noviembre 23:59; prórroga y canal no acreditados.

Comandos y salidas completos: `../../data/units/preflight/2026-11-07_200958/`. uv sync --locked correcto; diez pruebas pasan; comprobación de 540 respuestas y 90 tareas correcta. Qwen automático 191/270; contextual 193/270. Llama automático 32/270, con 115 unparsed. Antecedentes, no resultados finales. Inventario SHA-256 conserva artefactos.

Hardware: Core 5 210H, 12 CPU lógicos, RAM 32722059264 bytes (30,47 GiB), RTX 3050 Laptop 6144 MiB, driver 595.71.05, CUDA reportada 13.2; Ollama 0.18.0, Python 3.12.13. Pesos locales Qwen3-1.7B Q4_K_M, Llama 3.2-1B Q8_0, Qwen3-8B Q4_K_M. Falta SmolLM2; descarga autorizada en curso. Recursos libres variables.

Brechas: generador/recompensa finales, protocolo y bibliografía, calibración independiente, splits, inferencias train/test, SFT/DPO y auditoría, informe, frontera, snapshot aislado.

Incidencia: `rtk proxy python` no existe en sistema (exit 1); se usa python3 o uv run python. No modificó archivos.

## C1 cerrado — recursos y protocolo

Especificación: [contrato, rangos, modelos y bibliografía](2026-11-07_201130_especificacion_units.md). Cinco respuestas por modelo conservadas en `data/units/preflight/2026-11-07_200958/responses.jsonl`, `/api/show` incluye licencia, tokenizer/template, parámetros y metadatos GGUF; tags contienen digest. Resumen en summary.json. Medias con primera carga: Qwen pequeño 5,80 s/341 tokens; Llama 5,18 s/281; SmolLM2 16,94 s/379 (primera carga 63,83 s; siguientes ~4–6 s); profesor automático 25,01 s/259. Sin truncamientos. Calidad inspeccionada: objetivo 4/5 resultados correctos, profesor 5/5 dentro del 1%; una multiplicación del desarrollo del profesor luminosidad es imprecisa pese a resultado aceptable. Llama y SmolLM2 producen errores reales y formatos no interpretables; no se reporta exactitud inferida de formatos ambiguos. Controles excluidos de finales.

Calibración adicional del profesor, secuencial: `data/units/preflight/2026-11-07_200958/fullgpu.py`, fullgpu.jsonl/log. Contexto 2048, batch 128, num_gpu=99, máximo 1024; cinco respuestas, media 12.10 s, cero truncamientos. PS: 5569119360 bytes de modelo, todos en VRAM; salida previa automática dejaba capa de salida en CPU. Se adopta contexto 2048/batch128/num_gpu99 común, temp0,7, top_k40/top_p0,9/min_p0 explícitos y 1024 tokens baseline. Profesor train parte de 2048 tokens con contexto4096/num_gpu99 sujeto a control piloto de memoria, o 1024/2048 si el control conciso lo respalda; fijar antes de congelar.

Escala propuesta previa a C3: 20 grupos físicos/familia, 10/4/6 grupos por train/eval/test =>90/36/54 tareas; cuatro muestras profesor/train (360 candidatas). Con 25 s/consulta propuesta original10.800 exige75 h solo profesor; incluso12,1 s requiere36 h. Propuesta reducida ~1,2 h profesor + calibración/baseline y auditoría; presupuesto operativo local ~3 h, costo API cero, sin asumir costo eléctrico. Metas4.000/2.000 no alcanzables a esta escala: priorizar trazas auditables sin duplicados ni cuotas, reportar cobertura y baja potencia estadística. Confirmar tras C3. Profesor viable como cuarto comparador sobre test.

Persistencia: primer nohup no sobrevivió al cierre de shell (ninguna inferencia ejecutada); sustituido por systemd-run --user con WorkingDirectory y logs append. Servicios units-preflight-20261107 y units-fullgpu-20261107 terminaron sin errores. Un intento de shell con heredoc anidado falló por comillas; se escribió vía apply_patch.

Calidad preflight: Ruff y MyPy pasan; Bandit B310 sobre urlopen con URL fija127.0.0.1 (sin entrada externa) documentado; repetir con excepción B310.

## C2 cerrado — implementación y comprobación

Código nuevo en src/challenge: generator, verifier, models, evaluate, harness y exports. Placeholder derive se implementará en C5. Alcance alcanzado: catálogo, referencias, prompt, interfaz común, runner/reanudación, clasificación y métricas. Callers: CLI y tests; no llamadores de placeholders previos. Sin dependencias Python nuevas.

Ocho pruebas pasan: fixtures independientes (22m/s,9J,4piW y conversiones),90 referencias visibles, tríos, splits90/36/54 balanceados por estructura, tolerancia, equivalencias, ataques, métricas conocidas y runner simulado/reanudación/configuración. Comandos: uv run python -m unittest discover -s tests -v; uvx ruff check src/challenge tests/test_challenge.py; uvx mypy src/challenge tests/test_challenge.py; uvx bandit -r src/challenge -ll. Ruff/MyPy pasan. Bandit alertó lock en /tmp; corregido a caché del usuario con directorio700, nuevo análisis sin hallazgos medios/altos. URL fija localhost con B310 explicado en código.

Piloto generado: PYTHONPATH=src uv run python -m challenge.harness generate --seed4300 --groups10 --out data/units/pilot-v1/tasks.jsonl (usar espacios entre flags/valores).90 tareas y30grupos. load_tasks recalculó todas las referencias desde el prompt. No finales aún. Profesor adoptará máximo1024/contexto2048: cinco controles concisos fullgpu completos sin truncar; el piloto verificará formato y extensión antes de congelar.

## C3 en curso — piloto y revisión independiente

Inferencia persistente: systemd-run --user --unit=units-pilot-v1, WorkingDirectory=raíz, Environment=PYTHONPATH=src, StandardOutput=append:data/units/pilot-v1/inference.log, comando .venv/bin/python -m challenge.harness run --tasks data/units/pilot-v1/tasks.jsonl --out data/units/runs/pilot-v1-qwen --model qwen3:1.7b --samples3. Configuración efectiva en metadata.json; seeds42/43/44, top_k40/top_p0,9/min_p0, temp0,7, contexto2048, batch128,num_gpu99,máximo1024,think=false. No otras inferencias activas.

Auxiliar audit_c2 (solo lectura, sin inferencias/ediciones) comprobó1800 referencias de cinco semillas, fórmulas, agrupación y métricas. Halló FINAL multilínea/alternativas que escapaban al parser; SI infinito no serializable; comprobador sin validar dimensión de entrada; etiqueta científica fija; y cautela sobre unidades desconocidas para DPO. Primeros tres corregidos en verifier-2 con regresiones. Historial: data/units/pilot-v1/evaluator-history/v1 y v2; copia de37 respuestas intactas. v1:33correct,2numeric,2unparsed; cambio: contradicciones y finitud/dimensión; v2:33correct,2numeric,2unparsed; cero respuestas afectadas. No cambio de modelo ni inferencia.

Incidencias de validación: apply_patch inicial no coincidió tras Ruff expandir re.I a re.IGNORECASE, no modificó archivos; corregido contexto. Test falló por import json ausente (Ruff lo había retirado cuando no se usaba) y candado ocupado por piloto real. Corregido import y mock de flock únicamente en backend simulado. Ocho pruebas/Ruff/MyPy pasan. Bandit previo sin hallazgos medios/altos.

Pendientes de esta revisión antes de C4: derivar representation del texto real en generador, separar unidad desconocida de incompatible, soportar frase terminal observada «3. El resultado es boxed1.553 km/h» sin expresiones ni búsqueda de referencia. Riesgo menor de runner: PS después de chat puede perder respuesta si falla consulta; corregir antes de corridas finales y mantener runner original del piloto para reanudar si hiciera falta.

### Historial del evaluador durante C3

- v2→v3 sobre120 respuestas idénticas:90correct/24numeric/6unparsed →92correct/28numeric/0unparsed. Se admite frase terminal boxed observada y unidad desconocida pasa a unparsed. Seis casos afectados, IDs y hashes en evaluator-history/v3/comparison.json. Mejora de extracción, no del modelo.
- v3→v4 sobre155 respuestas idénticas:107correct/48numeric →106correct/43numeric/6unparsed. Se amplía detección de declaraciones finales/prefijos/negaciones por revisión adversarial. Seis casos afectados; aparecieron falsos negativos de aproximadamente y envoltorios LaTeX, conservados en historial.
- v4→v5 sobre167 respuestas idénticas:113correct/47numeric/7unparsed →114correct/48numeric/5unparsed. Admite aproximadamente y\approx. Persistía espacio antes de punto de cierre; test lo detectó y v6 corrige rstrip de puntuación terminal. Final se recalculará sobre270 respuestas para comparar todas las versiones en mismo corpus.
- Todos los códigos previos y corpus exactos preservados en data/units/pilot-v1/evaluator-history/. v6 y pruebas actuales pasan Ruff/MyPy;9 pruebas tras corrección de backend. No se ha visto test ni generado split final.

### Interrupción real y recuperación

Servicio units-pilot-v1 falló tras219 respuestas: el runner exigía done:true antes de escribir. Diagnóstico conservado en runs/pilot-v1-qwen/probe-219.json reprodujo HTTP200/done:false, texto parcial, sin tokens/timing ni razón final. Primera respuesta fallida no fue guardada por el defecto del runner; no puede recuperarse y se declara la pérdida. Una consulta diagnóstica adicional, misma clave/semilla/parámetros, queda conservada. No se afirma causa matemática ni truncamiento por límite.

Antecedente técnico consultado: https://github.com/ollama/ollama/pull/19458 y https://docs.ollama.com/api/chat describen respuestas200/done:false ante ciertos errores de backend; no prueba que nuestra causa concreta sea idéntica. No se actualiza Ollama durante el experimento.

Corregido runner para persistir toda respuesta con estructura válida, incluso done:false; evaluación la marca unparsed/backend_incomplete y conserva denominador. Monitoreo PS fallido ya no pierde respuesta. Nueve pruebas incluyendo backend parcial, salida vacía y fallo PS, Ruff/MyPy/Bandit sin medios/altos. Cambio solo de infraestructura, mismo muestreo. Nueva carpeta inmutable de continuación runs/pilot-v1-qwen-recovered/:219 filas copiadas byte a byte, su hash-prefix y metadata fuente en lineage.json/source_metadata.json; consulta diagnóstica incorporada como clave faltante con seconds:null porque no fue medido por el probe. Se infieren únicamente50 claves restantes. Servicio units-pilot-v1-recovered, recovered.log. Original intacto.

Corrección de interpretación C1:4*pi*49=615,7521601035994; el profesor escribió615,7521603589793, diferencia~4e-10 relativa. Es imprecisión despreciable de últimas cifras, no evidencia de error relevante. Los fallos aritméticos dentro de1% sí se observaron claramente en trazas del objetivo del piloto.

### Piloto1 terminado; alarma de calibración

270 respuestas en runs/pilot-v1-qwen-recovered; score v7:125correct,134numeric,11unparsed, cobertura95,93%, pass@1=46,30%, pass@3=58,89%; cotas superiores50,37%/67,78%. Dos truncamientos y un backend_incomplete dentro de unparsed. Fácil55,56%,medio54,44%,difícil28,89%; velocidad fácil100% y medio96,67% se retienen como controles. Luminosidad tiene2/30=6,67% en cada nivel: alarma de suelo. C3 NO cerrado.

45 trazas revisadas (5/celda) por agente, no revisión humana docente. audit-speed-energy.jsonl,audit-luminosity.jsonl y audit-metadata.json vinculan IDs, muestras, hashes, notas y selección. Confirman fallos de cálculo, sustitución, exponentes, conversión temporal y mezcla m²/cm²; varios resultados aceptados por1% tienen pasos defectuosos. No convertirlos en SFT. Historial completo sobre mismo corpus270 en evaluator-history/full-corpus-comparison.json, códigosv1–v7 y cambios por ID/muestra. v7 incorpora «El resultado es:» como declaración explícita para detectar contradicciones; respecto v6 dos casos pasan a unparsed, no se considera mejora del modelo.

Decisión C3: reducir dificultad numérica únicamente en luminosidad, conservando fórmula, estructuras y conversiones0/1/3. generator units-2: d entero2–30m; F0,01–0,99W/m². Actualiza representation desde campos visibles, no etiqueta fija por familia (corrige observación del auxiliar). No se cambian respuestas anteriores. Nueva semilla4304;90 tareas guardadas en pilot-v2/all-generated.jsonl, se infieren las30 luminosas de pilot-v2/tasks.jsonl con3muestras, todos los niveles y sin seleccionar errores. Velocidad/energía permanecen con evidencia piloto1 porque su generación/prompt no cambió; ambos conjuntos generados se excluirán del final. Servicio units-pilot-v2 con mismos parámetros;9 pruebas/Ruff correctos. Magnitudes actualizadas antes de congelar; no se ha visto test.

Rama creada según convención README: implement-units-challenge-20261107, sin commits ni staging; cambios preexistentes preservados. Descripción pyproject corregida de planificación a unidades; uv sync --locked pasa sin cambios de dependencias.

### Piloto2 y ajuste final propuesto

Piloto2 (30 luminosidad ×3) completo, score v7:11correct,71numeric,6unparsed,2unit; cobertura93,33%; fácil4/30,medio7/30,difícil0/30;un truncamiento. Fuente runs/pilot-v2-qwen/scores/v7/. Los rangos nuevos mejoran cobertura de aciertos en fácil/medio, pero difícil sigue en suelo. No hay cambio de parser por esos resultados.

Se prueba units-3: únicamente luminosidad/hard pideW en vez deerg/s; mantiene conversiones de distancia y flujo, por lo que nominalmente tiene2conversiones, no3. Velocidad/energía conservan0/1/3. Nueva carpeta pilot-v3/ con mismos grupos físicos/semilla4304 de piloto2 para aislar esta modificación;solo10tareas difíciles×3=30respuestas nuevas, no repetir fáciles/medias sin cambios. IDs se mantienen por problema/nivel pero prompts/versiones/hashes y carpeta distinguen corridas. Servicio units-pilot-v3;9 pruebas/Ruff correctos. C3 sigue abierto hasta medir y revisar.

Las conversiones registradas son factores mínimos por magnitud agregada: en estructuras sum se puede sumar primero en una misma unidad y convertir el total. Una traza que convierta dos componentes separadamente realiza más operaciones que ese conteo nominal. No atribuir causalmente el desempeño solo al número de conversiones.

## C3 cerrado — calibración global y límites

Piloto3 (solo10luminosidad/hard×3) conserva2/30correct,23numeric,5unparsed;paso de cero a dos aciertos automáticos, todavía cerca del suelo. Cobertura83,33%;un truncamiento. Se retiene luminosidad/hard como estrato de estrés explícito, sin afirmar que esté bien calibrado individualmente: las alarmas10%/90% son propuestas, no criterios rígidos del curso. Dos iteraciones de reducción documentadas; no seguir ajustando a un piloto pequeño. La revisión muestra que ambas respuestas aceptadas de este estrato contienen una equivalencia de potencia mal explicada que numéricamente aplica el factor del flujo: no son trazas SFT coherentes. El núcleo de energía y velocidad difícil sí contiene aciertos y errores y garantiza señal global verificable.

Composición calibrada, sin elegir respuestas individuales: velocidad/energía de piloto1, luminosidad fácil/media de piloto2 y difícil de piloto3. Mismos parámetros de muestreo;90tareas/30problemasfísicos×3=270respuestas, referencias y claves validadas. Archivos en data/units/pilot-calibrated/{tasks,responses,labels}.jsonl,summary.json,sources.json. Resultado132correct,126numeric,12unparsed; cobertura95,56%;pass@1=48,89%,pass@3=65,56%,cotas superiores53,33%/71,11%. Por nivel57,78%/60,00%/28,89%;fácil y medio no demuestran separación empírica estricta, difícil agregado sí cae. No afirmar causalidad ni generalización a todas las celdas. Tres truncamientos, cero backend_incomplete en esta composición (el parcial queda en historia de luminosidadv1).

45trazas de la composición revisadas contextualmentepor agente,5/celda, en pilot-calibrated/audit.jsonl; hashes enlazan respuestas intactas. Se mantienen auditorías originales. Contradicciones, expresiones sin evaluar y variantes de formato no soportadas permanecenunparsed; no se ejecutan expresiones ni se reclasifica manualmente para mejorar métricas. Verificadorv8 corrige negación de JSON en línea previa descubierta por auxiliar; regresiones y9pruebas/Ruff/MyPy pasan. Recálculo v7→v8 sobre pilotos1/2/3 conserva125/270,11/90,2/30aciertos respectivamente, cero cambios; versiones anteriores intactas. Comparación v1–v7 sobre mismo corpus disponible;v8 se conserva en scores/v8.

Controles finales profesor: cinco prompts de desarrollo en pilot-calibrated/controls.jsonl, corrida controls-qwen8. Contexto2048,batch128,num_gpu99,max1024,top_p0,9/top_k40/min_p0,temp0,7,seed42,thinkfalse, idénticos parámetros base finales. Duraciones12,73/5,62/8,47/6,12/8,63s,122–194tokens,ningún truncamiento, modelo completo enVRAM. Queda viable para train y test; costo esperado360respuestas~50min, no se proyecta retener todas.

Se confirma escala final90train/36eval/54test,20grupos/familia con10/4/6;cuatro muestras profesor/train360candidatas. Cantidades orientativas4000/2000 quedan lejos por límite operativo local~3h, filtrado y auditoría; publicar escala efectiva sin inflar ni prometer suficiencia para entrenamiento. Semillasfinal4301/split4302;excluir todos los pilotos y controles/spike. No test generado ni observado aún.

## C4 cerrado — particiones congeladas y reproducción aislada

Congelado data/units/final-v1/:90train/36eval/54test;20grupos/familia con10/4/6,18celdas familia/nivel/estructura por split;variantes juntas,IDs/prompts únicos y claves físicas disjuntas.95claves excluidas de spike,pilotos generados y controles; fuentes/hashes en exclusions.json. Modelos/digests/licencias en models.json;protocol.json incluye seeds4301/4302,muestras3baseline/4profesortrain,parámetros OPTIONS compartidos con runner,verificadorv8,generadorunits-3. Catálogo units.json y código normativo(fourfiles)copiados;manifest.json fija15archivos incluyendo manifiesto.

Comandos reales: PYTHONPATH=src uv run python -m challenge.harness freeze --out data/units/final-v1 --exclusions data/units/freeze-inputs/exclusions.json --models data/units/freeze-inputs/models.json; check --dataset data/units/final-v1. check verifica hashes,código,regenera splits,compara archivos públicos/privados,exclusión,grupos,celdas y referencias visibles. Los modelos no reciben ninguna referencia. No se ha inferido test.

Diez pruebas,Ruff,MyPy y Bandit sin hallazgos medios/altos. Las pruebas de runner simulado ahora también simulan comandos de hardware; no requieren GPU ni nvidia-smi. Cambios no afectan código normativo congelado. Copia temporal aislada de src/tests/dataset: unittest,check yfreeze desde entradas incluidas;15archivos regenerados idénticos byte a byte. Evidencia data/units/validation/c4-isolated.json. No depende de archivos del repositorio externo,ni modelos ni Ollama para comprobar/regenerar. Es validaciónC4, no snapshot final ni C7.

Control profesor con versión final:1/5correct,4numeric,cobertura100%,sintruncamientos; fuente controls-qwen8/scores/v8. Capacidad técnica viable; calidad aritmética baja en controles difíciles, no suponer que360candidatas produzcan360trazas. Filtrado y auditoría obligatorios.

## C5 en curso

Servicio persistente units-train-teacher-v1: .venv/bin/python -m challenge.harness run --tasks data/units/final-v1/private/train.jsonl --out data/units/runs/train-teacher-v1 --model qwen3:8b --samples4. Log append inference.log dentro de corrida. Una inferencia local activa. Hasta360claves; reanudar solo faltantes. No entrenar. Código de derivación/auditoría se añadirá sin modificar generador/verificador/evaluador/runner congelados.

### C5 exportador y control de calidad

Implementado derive.py: collect deduplica solo espacios por tarea/status y conserva fuentes; required_audits usa semilla4303 por celda; checked_run valida dataset/config/digest/completitud; build conserva correctas distintas del profesor y aplica auditoría (5/celda o todas si menos), expande toda celda con reject/uncertain, excluye esas trazas sin convertirlas en negativas; DPOsolo numeric/unit del mismo train/prompt, máximo2sin cartesiano, conserva procedencia. CLIderive/check-derived reproduce desde respuestas y juicios con hashes. Oncepruebas incluyen dedup, procedencia mixta, rechazo de tareas ajenas a train,unparsed excluido y expansión obligatoria. Ruff0.17.4,MyPy2.4.1,Bandit1.9.4 pasan sin medios/altos; uv0.11.16. Exportador revisado por auxiliar sin bloqueos; no certifica todavía cantidades reales. Código normativo congelado intacto(check pasa).

Velocidad completa:120respuestas,79candidatas correctas distintas,15seleccionadas inicialmente. Snapshot inmutable en derivation-v1/audit-input-speed.jsonl,source-speed-rows.jsonl,speed-snapshot.json. Auxiliar audit_c2 revisa y escribe solo audit-speed.jsonl; detectó cocientesincorrectos dentro1% y amplía fácil/medio completas. No inferencias auxiliares ni edición simultánea de archivos.

Resumen humano legible C3:[calibración](2026-11-07_211432_calibracion_units.md). No se han generado resultados de test ni iniciado entrenamiento.

### Auditoría de velocidad terminada

Auxiliar:61revisadas,57keep/4reject. Easy29completas27keep/2reject;medium27completas25keep/2reject;hard5muestreadas5keep (18hardno certificadas). Casos excluidos:dos trazas5558/17≈327,529 frente326,941176 ydos7220/27≈266,67 frente267,407407, pese a recompensa1. Redondeos legítimos mantenidos; juicio explícito sobre31,0 como redondeo grueso de30,917... en notas. Archivoaudit-speed.jsonl; parentcheck confirma selección,IDs,hashes y expansión: audit-speed-check.json.75de79candidatas siguen elegibles (57auditadaskeep+18hardnoauditadas), sujeto a control final. No se añaden al dataset todavía.

Historial v7→v8 sobre mismas270respuestas del primerpiloto: cero etiquetas cambiadas; guardia de negación previa al JSON corregida por ataque artificial, no ganancia del modelo. Archivo evaluator-history/v7-v8-comparison.json y código v8.

### Auditoría de energía terminada

120respuestas de energía;67candidatas correctas distintas. Muestra15 detectó defectos en los3niveles; se revisaron67/67. Resultado24keep/43reject:easy13/20,medium10/14,hard1/9. Ejemplos de producto erróneo con recompensa1:8,95×655,36=5867,31 frente5865,472;0,5×42×16,5²=5681,25 frente5717,25;5,7×59,29/2=167,953 frente168,9765. Única difícil retenida contiene42kg×16,5²/2=5717,25J=5,71725kJ. Auditoría contextual del auxiliar, no certificación docente. Archivoaudit-energy.jsonl; validación principal de selección/IDs/hashes/cobertura enaudit-energy-check.json. No se modifica recompensa ni se usan correctas descartadas como negativas.

Casos de formato de C3:12unparsed de la composición revisados, decisiones en pilot-calibrated/format-decisions-v2.jsonl. Incluyen expresiones no evaluadas, camposvalue/unit adicionales en prosa/LaTeX y números con varias comas como separadores de miles; estos últimos no son la coma decimal soportada. No se cambia evaluador congelado. Historia de decisiones inicial conservada.

### Profesor completo y auditoría final de C5

360respuestas train completas:193correct,154numeric,13unparsed,ningún truncamiento/backend_incomplete; cobertura96,39%. Correctas únicas178 tras dedup de espacios. Auditoría160candidatas:104keep/56reject;18hardvelocidad restantes amparadas solo por muestreo. ElegiblesSFT122:51fáciles,46medias,25difíciles. Por celda:velocidad27/25/23;energía13/10/1;luminosidad11/11/1. Todaslas nueve celdas tienen candidatas retenidas, pero cobertura escasa en difíciles de energía/luminosidad. La auditoría es de agente, no humana docente.

Luminosidad32/32 revisadas (muestra inicial5/5/1),easy11keep/6reject,medium11/3,hard1/0. Hashes/selección/expansión comprobados por principal enaudit-luminosity-check.json. Hardcorrecta convierte90erg/s/cm²÷1000=0,09W/m². No se usan expresiones sin evaluar ni unparsed como negativas.

Con solo profesor se forman22paresDPO; estado previo entero en teacher-only-stats.json. Se seleccionan38tareas con SFT elegible y menos errores únicos que min(2,preferidas elegibles). Fuente negative-tasks.jsonl es subconjunto idéntico de train; regla yIDs en negative-selection.json. Servicio units-train-negatives-v1 genera3respuestas del objetivo por tarea=114máximo, mismas opciones/seeds42–44. No otras inferencias locales activas.

Costo profesor medido:2537.21s de llamadas (media7.05s),56563tokens de salida; todas las cuentas disponibles;868387bytes crudos; costoAPI0, electricidad no medida. Proyección condicional para4000SFT con retención122/360:23.11h solo profesor; no garantiza misma tasa al ampliar. Datos menores se justifican por límite operativo local, filtro de coherencia y distribución declarada, sin duplicar ni productos cartesianos.

Incidencia de preparación: comillas anidadas de shell quitaron comillas de claves de un f-string al crear negative-selection.json (NameErrorfamily). negative-tasks.jsonl ya estaba correctamente creado. Se cambió a rtk proxy env PYTHONPATH=src uv run python con heredoc directo, se cotejó el archivo existente contra la selección recalculada y se escribió únicamente la selección faltante. Ninguna respuesta ni referencia sobrescrita.

## C5 cerrado — datos reales y reproducción

114respuestas adicionales del objetivo:89correct,19numeric,6unparsed,ningún truncamiento/backend_incomplete;selección dirigida de38tareastrain, no línea base representativa. Filtrar esas fuentes amplía DPOde22a35pares (+13) sin cambiar verificador ni respuestas del profesor. SFTpermanece122.

Artefactos finales deC5:data/units/derived-v1/{sft,dpo}.jsonl,stats.json,manifest.json,audits/.122SFT/46tareas y35DPO/25tareas. Por nivel(fácil/medio/difícil):SFT51/46/25;DPO7/15/13. Las nueve celdas físicas/nivel tienen datos, pero algunas solo1traza/par. Máximo2pares/tarea,sin reutilización dechosen/rejected y sin cartesiano. Fuentes repetidas por espacios se preservan en metadatos; correctas distintas del profesor no se limitan auna.193correctas automáticas→178únicas→122retenidas;56descartadas porcoherencia. Auditoría160con104keep y56reject;18hardvelocidad no revisadas individualmente, limitación explícita.

Comandos derive ycheck-derived con datasetfinal-v1,profesortrain-teacher-v1,audits3,negative-tasks.jsonl ycorridatrain-negatives-v1. Ambas ejecuciones pasan. Copia temporal aislada(src/tests/dataset/derivados/sourcesmetadata+responses/negative-tasks),11pruebas ycheck-derived idéntico, sin Ollama/pesos ni archivos externos. Evidencia validation/c5-isolated.json. Revisión independiente de artefactos encargada al auxiliar duranteC6. No snapshotsdeentrega creados.

## C6 en curso

Preflight de integridad:check_dataset confirma90/36/54;cuatro digests locales coinciden con catálogo congelado ybackend0.18.0. Inicio controles de desarrollo finales:5prompts de pilot-calibrated/controls.jsonl por pequeño, una muestra; profesor ya tiene5controles mismos parámetros. Servicios secuenciales, sin otra inferencia local activa. No usar resultados de test para cambios de diseño/verificador.

### C5 revisión de calidad2 y C6 congelamiento final9

La revisión independiente confirmó integridad/procedencia de derived-v1 y observó8chosenDPO procedentes de18hardvelocidad cubiertas solo por muestreo. Para cerrar esa incertidumbre se auditaron las18restantes sin tocar archivos previos: audit-speed-extra.jsonl,17keep/1reject. Error descubierto en task1ed14d6a67017130be8c-hard:8,827km/(172/3600h)=184,7511627906977km/h, no183,12. Se revisaron ahora178/178candidatas correctas únicas:121keep/57reject. Es auditoría contextual de agentes, no humana docente.

Derivadosv2:121SFT/35DPO,todas las retenidas con revisión individual. La traza retirada afectaba1chosenDPO; reemparejar por orden cambió2pares (uno por reemplazar elegida y otro por desplazar el emparejamiento),sin variar35total. Archivo derivation-v1/revision-history.json conservaIDs/completions anteriores/nuevos. Derivadosv1 intactos como historial. Regla/etiquetas automáticas no cambian por estos juicios.

Controles finales Smol (antes de primer test):5unparsed con verifierv8, sin truncamientos; contienen «Valor final =2,45872km/h» y JSONunitWatts, formatos inequívocos observados. Verifierv9 admite esos prefijos y alias sin usar referencia; tests añaden equivalencia y contradicción con prefijo nuevo.11pruebas,Ruff,MyPy yBandit sin medios/altos pasan. Recalificación con mismas respuestas:Smol0correct/5unparsed→0correct/2numeric/3unparsed, cobertura0→40%; ningún cambio de aciertos. Profesor360,negativos114,otroscontrolesypilotos mantienen etiquetas. Historialcódigov8/v9, hashes ycasos enverifier-v8-v9/. Se trata de mejora de extracción, no de modelo.

Datasetactualfinal-v2 congela verifierv9;las seisparticiones públicas/privadas son byte a byte idénticas afinal-v1, con mismoSHA de test. Solo protocolo.verifier_version/código/manifest cambian. No se había inferido test; fuente dataset-comparison.json. Derivadosactualesderived-v3 contienen121SFT/35DPO, contenido igual av2, metadatosverificador9. DistribuciónSFT51/46/24;DPO7/15/13; todas9celdas cubiertas, algunascon1ejemplo.

Reproducciónv9 desde copia aislada:11pruebas,check-derived yregeneración15archivos idénticos. Evidencia validation/v9-isolated.json. Código normativo9 queda fijo desde primera inferencia de test. Primer servicio units-test-qwen17-v1 usa final-v2/private/test.jsonl,54tareas×3muestras,carpeta runs/baseline-v1/qwen17,logpersistente. No adaptar a sus resultados. Todos los modelos se puntuarán con verifierv9.

Incidencia al registrar revisión: unassert esperaba1parDPOreemplazado; al recalcular se comprobó que zipdesplaza2pares. Ningún artefacto escrito en ese intento; se registraron2retiros/2altas reales, sin inventar la diferencia. Archivos anteriores preservados.

### C6 matriz local y procedencia

Controles finales de desarrollo5/modelo completados:Qwen objetivo3correct/2numeric;Llama1correct/2numeric/2unparsed;Smol0correct/2numeric/3unparsed trasv9;profesor1correct/4numeric. Sin truncamientos. Parámetros iguales,backend0.18.0,digests contra catálogo. No interpretar0correctSmol como exactitud matemática0: persisten3salidasnointerpretadas. Se mantienen sus5respuestas antes de test y sin ajustar tareas.

Qwen3-1.7B test completó162filas;scorev9 guardado. Inicio servicio units-test-llama-v1 sobre losmismos54prompts×3,mismasopciones. No se cambian datos/verificador por resultados test. Harness incorpora compare_local/CLIcompare:solo integración/reproducción fuera del código normativo congelado, reutiliza checked_run/summarize y coteja modelo,muestreo,metadata/hashes,etiquetas/métricasguardadas ydigest/contextoobservado enPS. Exige cuatro modelos y backendlocal común.11pruebas,Ruff/MyPy pasan;orquestación no cambia fórmulas/parser/métricas.

Cada corrida tiene sidecarworkspace.json conHEAD/ramayestado sincommits, además de snapshots/hashes. HEAD es elpuntodepartida, no identifica estos cambios sincommit; la entrega debe reproducirse con código incluido y huellas, no checkoutdelHEAD. No se copian secretos ni pesos.

## C6: avance y preparación independiente del informe (22:24 CLST)

Qwen17 y Llama completos, 162 respuestas cada uno. Qwen17 v9: 84 correct, 71 numeric, 7 unparsed; pass@1 51,8519%, pass@3 68,5185%, cobertura 95,6790%. Llama v9: 4 correct, 68 numeric, 90 unparsed; pass@1 2,4691%, pass@3 7,4074%, cobertura 44,4444%. No interpretar sus no extraídas como errores matemáticos. Smol sigue en servicio persistente, sin superponer inferencias; Qwen8 test será el siguiente.

Revisión auxiliar cualitativa: qwen17/qualitative.jsonl SHA256 8421dabe171f9a71ec2aecd062eeaf04e8e27b5638b47a69d7edb1e6658732fd; llama/qualitative.jsonl 6f4bef5dddcab2b1b839f75f4b9331db4f0ac5a61b54a15f12b5569511e825e3. Ejemplos no exhaustivos; algunos valores aceptados al 1% muestran pasos defectuosos, sin cambiar etiquetas ni métricas.

Preparación independiente: docs/report/content.tex es fragmento de contenido, sin documentclass ni template inventado; README y evidence.md documentan reproducción y brechas. render.py genera figuras vectoriales/PNG, tablas TeX y CSV desde matriz verificada; pendiente ejecutarlo tras completar los cuatro modelos. Matplotlib 3.11.2 se fijó como grupo opcional report (núcleo sigue sin dependencias). uv sync --locked --group report correcto; renderer --help correcto. Ruff 0.17.4 y MyPy 2.4.1 pasan código/renderer; once pruebas pasan. Un intento uv run --no-sync ruff falló por no estar instalado en el entorno; se usó uvx con versiones fijadas, sin cambiar código por ello.

Se consultó ruta del template y autorización/ubicación de credencial Together mediante pregunta asíncrona. Pendientes, sin llamadas pagadas ni lectura de secretos. C7 permanece abierto; deliveries/challenge no creado.

Revisión independiente del borrador C6: cifras 121/35, 178 auditorías, 22/13 procedencia DPO, splits, exclusiones, tokens y tiempos coinciden. Hallazgo material: las tablas TeX inicialmente omitían cotas optimistas aunque estaban en CSV; se corrigió render.py antes de generar artefactos, añadiéndolas entre corchetes con aclaración de que no son intervalos de confianza. También se explicitó en content.tex que el piloto consolidado tiene tres truncamientos. Ruff correcto tras cambio. Bandit 1.9.4: cero medios/altos; ocho avisos bajos por aserciones y una excepción B310 para URL local fija, sin escaneo de secretos.

### Smol completo; profesor test iniciado (22:30 CLST)

Smol162/162; score v9 sobre final-v2: 5 correct,33 numeric,124 unparsed; cobertura23,4568%,pass@1=3,0864%,pass@3=7,4074%; cotas optimistas79,6296%/100%. Diez truncamientos y un backend_incomplete, todos conservados en denominadores. No se modifica parser tras observar test; baja cobertura limita comparación matemática. Servicio units-test-smol-v1 inactivo antes de iniciar units-test-qwen8-v1 (invocación a89438b6b34f49228db61f2cb09ba8bd),162respuestas planificadas con misma configuración/dataset. Corrida Qwen8 única activa. Auxiliar revisa exclusivamente artefactos Smol ya completos; no inferencias ni parciales profesor.

Revisión cualitativa Smol (solo corpus completo): seis ejemplos, SHA2567221c078449170a5c4b77ae2eb4e1fb85847e420ce592ea62c25d93bc8b58d64. Cero aciertos automáticos en energía/luminosidad; los cinco son velocidad. Auxiliar incluyó length1024 y done=false como límites separados, sin retocar parser. El principal comprobó IDs, índices, hashes y etiquetas de los tres cualitativos existentes frente a respuestas y scores/v9; todos coinciden. Negativos objetivo:242,9536s,18052tokens para114respuestas. Comprobación de memoria Qwen8 durante test: size=size_vram=5569119360bytes,context_length2048,digest500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41; residencia completa en GPU según Ollama.

### Template recibido (22:38–22:40 CLST)

El usuario indicó sandbox/latex_template. Sin AGENTS adicional encontrado. Original main.tex y escudo-uc.png copiados byte a byte a docs/report/template con SHA256/origin.json; sandbox permanece intacto. main.tex adaptado conserva article10pt/letterpaper, paquetes, geometría y cabecera de UC; sustituye instrucciones del proyecto por content.tex del desafío. No se ejecutan entrenamientos. Título/fecha/etapa definidos; nombres de autores preguntados, pendientes. Se preguntó también por prórroga/canal porque en las fuentes no consta cambio del plazo original. latexmk4.88,pdfTeX1.40.29/TeXLive2026 y paquetes lmodern/graphicx/babel-spanish confirmados. Compilación tras disponer de tablas/figuras reales de cuatro modelos. Frontera aún sin presupuesto específico autorizado.

### Cambio de proveedor externo indicado por usuario (22:45 CLST)

El usuario respondió «habilitare openrouter». Se actualiza el proveedor de la comparación comprometida de Together AI a OpenRouter, conservando candidato DeepSeek-V4-Pro-0813 sujeto a disponibilidad, mismo test54/verificador9 y tres respuestas por tarea. Se alineó el plan conservando160líneas y documentos vigentes; la bitácora conserva el acuerdo anterior como historia. Habilitar proveedor no indica tope de gasto: se solicitó presupuesto USD y ubicación de la credencial, sin pedir ni mostrar claves. No hay llamadas pagadas autorizadas todavía. Consulta de disponibilidad después de C6; ejecución externa depende del acceso y presupuesto reales.

### Autoría y plazo informados por usuario (22:46 CLST)

Autoría ordenada alfabéticamente por apellido, respetando grafías aportadas: Fernando Fajardo, Sebastian Palma, Benjamin Prieto y Rodrigo Ugarte. Se actualizó main.tex sin tocar template original. El usuario informa extensión hasta «viernes12de noviembre23:59» e intención de entregar alrededor del martes. datetime.date(2026,11,12).weekday()==3 confirma jueves; se registra conservadoramente la fecha numérica explícita12/11/2026 23:59, con discrepancia del día advertida, y martes10como intención. Prórroga atribuida a comunicación del usuario, no comprobada en anuncio externo. Canal no indicado.

## C6 cerrado (22:48–22:53 CLST)

Los cuatro modelos completaron162respuestas cada uno,648total,sobre mismo54test a43cb708c74d20b89c399762b881d39eaea402e64b7f9077730eee9bca490344 yverifier9. compare reconstruye etiquetas/métricas, compara scoresv9 ymetadata,contextos2048,digests,cfg,seeds,prompts yrunnerSHA. Matriz comparison-v9.json creada sin sobrescribir. Profesor82correct74numeric6unparsed;pass@1=50,6173%,pass@3=72,2222%,cobertura96,2963%;sintruncamientos/backend. CuatrocorridasCPU/GPUcompletas;unidadesinactivas,Qwen8descargado deVRAM con ollamastop(sinborrar pesos). Ejemplosprofesor7verificadosporauxiliar,SHA499b9cdbdf032d9281222c50e0877e5c5fc5821dda29046969a081f7ff6df2fc.

Costobaseline:Qwen17435,1224s/31521tokens;Llama395,5756s/26414;Smol869,4208s/71009;Qwen81088,1607s/24315.Total2788,2794s/153259tokens. APIlocalUSD0,electricidadnomedida. Todas162observacionesporcorrida reportanmodelbytes=size_vram; Qwen81.7 no corresponde: Qwen17=1612852352,Llama1447075840,Smol1495278080,Qwen85569119360bytes. Figuras reales generadas en docs/report/local-v1 e inspeccionadas, sin recortes ni solapes observados. Historial de cambiosdevv8→v9preservado; ninguna correcciónmotivadaentest.

C7 externo: usuario autorizaOpenRouterhastaUSD5(ha cargadoUSD10),credencialen.env; comprobaciónimprimeúnicamenteOPENROUTER_API_KEYpresente,ningúnvalor. SolicitaunDeepSeekbaratoybueno. Catálogopúblico yendpointsconservadosenopenrouter-preflight. DeepSeekV4Pro0813disponible;seeligeelcandidatoyaacordado,pinandoproveedorDeepSeekparaevitarmezclarcuantizaciones/rutas. Precioobservadofin desemanaUSD0,66/1,98por1Mentrada/salida; topecaps1,32/3,96paraevitaraltasrutas. Tresrespuestas/test162+5controlescabenampliamentebajoUSD5conmáx1024tokens. Seed/top_k/min_pnoestánadmitidosporproveedornativo,seomitenydeclaran;temperatura0,7,top_p0,9,reasoningenabled=false. Aúnnocallspagadasenescribir estaentrada.

### C7: controles y ruta externa efectiva (22:55–22:59 CLST)

La primera solicitud al proveedor nativo DeepSeek devolvió HTTP404 antes de generar: política de la cuenta excluye proveedores que permiten entrenamiento con datos pagos. Error completo en frontier-v1/controls/errors.jsonl; no se modificó privacidad de la cuenta. Se conserva código original y metadata del intento. Se eligió otra ruta del MISMO modelo: DeepInfra FP8, precio público USD1,30/2,60 por millón de tokens entrada/salida, caps1,32/3,96 y sin fallback. Sus parámetros admiten semillas, top_k y min_p; ahora 42+i,40,0 respectivamente, además de temperatura0,7/top_p0,9/máx1024/reasoning.enabled=false. Cambio anterior al test externo, documentado como controls-v2, sin modificar verificador ni tareas.

Cinco controles completos:3correct,2unparsed, sin truncamiento; costoUSD0,0029965. Todos reportan modelo0813,providerDeepInfra y reasoning_tokens0. Test externo iniciado en servicio units-frontier-test-v1, invocación895e62777f0c4802a50f6e7342264730; misma huella test y162solicitudes. Guardado incremental/fsync y reanudación de claves faltantes. Cada intento se registra antes de enviar y reserva USD0,02 conservadores, también si falla; tope acumuladoUSD5. 168intentos previstos contando404+5controles+162test reservanUSD3,36. No hay reintentos automáticos. Trece pruebas (incluye presupuesto, reanudación, normalización de truncamiento sin red),Ruff/MyPy yBandit sin medios/altos. Módulos normativos4 siguen intactos.

El usuario informa canal previsto de entrega por correo al profesor. Se registra como información aportada por el equipo; no se envían correos ni se adivina dirección. Autores Fajardo/Palma/Prieto/Ugarte incorporados.

## C7 cerrado: entrega técnica validada (2026-11-07)

Template real recibido, autores ordenados por apellido y canal previsto por correo
informados por usuario. Informe final: docs/report/build/final-v5/main.pdf, siete
páginas; original del template intacto. Se añadió amsmath, ajuste del escudo al
ancho de su caja y metadata PDF estable. Compilación inicial falló por binom sin
amsmath; corregido sin alterar el template original. TinyTeX requirió actualizar
solo texlive.infra (466k) y añadir hyphen-spanish (17k), después regenerar formato
pdflatex. Última compilación sin advertencias, referencias pendientes, overfull
ni underfull. Se revisaron visualmente las siete páginas; precisión final aclara
que los 153259 tokens locales son reportados y falta conteo en un intento Smol.
Versiones anteriores de fuentes de ejecución, scores y builds se conservan.

Frontera final: DeepSeek-V4-Pro-0813/OpenRouter/DeepInfra FP8; 162 respuestas,
133 correct, 29 unparsed, cero numeric/unit/truncamiento/backend incompleto.
Pass@1=82,0988%,pass@3=90,7407%; cotas optimistas100% y cobertura82,0988%.
25377 tokens de entrada,22125 salida, reasoning_tokens0 presente en162/162;
341,1449 segundos. Costo test USD0,0905151, controles USD0,0029965;
total USD0,0935116. GET key gratuito concilia incremento exacto de uso desde0:
diferencia0, sin compra adicional. Un intento404 previo no generó ni incrementó
uso; se mantiene reserva conservadora,168 intentos/USD3,36 < máximoUSD5.

Revisión auxiliar final: 32 ejemplos cualitativos de cinco modelos con hashes y
etiquetas cotejados; no son auditoría humana ni clasificación exhaustiva. Hallazgo
ledger: cambiar ruta podía reiniciar reserva al reanudar; config actual fija ruta
y test simulado lo rechaza antes de API. Snapshot del runner real preservado.
Scores v9→v9-adapter3: idénticos labels/summary, cero respuestas afectadas,
cero inferencias nuevas; solo cambió protección/procedencia del adaptador.
Verificador9, generador3, métricas y runner local conservan hashes congelados.

Primer candidato aislado:202 entradas de manifiesto,13tests,check/freeze15archivos,
check-derived/derive8archivos,compare local,frontier score,calibración,32ejemplos,
figuras/tablas/CSV y PDF idénticos. Auxiliar repitió checks desde copia sin red
ni inferencia y no encontró otros hallazgos materiales. Tras precisión editorial,
segundo candidato volvió a pasar11comandos de reproducción y PDF idéntico.

Solo entonces se creó deliveries/challenge/, con code/data/results/report,
README/EVIDENCE, pyproject/uv.lock y manifest:207 entradas + manifiesto propio,
208 archivos. Se volvió a copiar FUERA del repositorio e instalar entorno nuevo
Python3.12.13/Matplotlib3.11.2, offline desde dependencias fijadas. Reproducción
completa, sin API/GPU ni datos externos:13tests,15 archivos generador y8 derivados
idénticos, matrices/etiquetas/métricas/figuras/tablas/CSV iguales y PDF idéntico
byte a byte. Sin symlinks, pesos, entornos ni credenciales; se comprobó también
contra la clave real sin imprimirla. Un intento de instalación usó ruta temporal
incompleta y falló antes de crear entorno; se corrigió con ruta explícita. uv
avisó fallback de hardlinks a copia entre filesystems, sin afectar resultados.

ZIP verificado por CRC y cada SHA del manifiesto: deliveries/challenge-2026-11-07.zip,
1513999 bytes. Evidencia final: data/units/validation/c7-delivery-isolated.json.
No se hicieron commits, entrenamientos ni envíos de correo. Cambios preexistentes
y originales preservados. El plan sigue en160líneas, C0–C7 cerrados técnicamente.
Plazo/canal registrados según usuario:12nov23:59Santiago (jueves en2026, aunque
lo llamó viernes), intención martes10, correo al profesor a cargo del equipo.

SHA256 ZIP: 376f7ed8fc3c41330025e33c0d6204239495ca149da899d5b623ce2f552bb1e0
SHA256 manifest: 97ce3f11d0923cfb7a5ddfacd55ec1b4af87d6ecb332b62ee282000f63d282d1

## Revisión de maquetación, 2026-11-08

Usuario solicita más espacio alrededor de líneas horizontales del encabezado y
tablas. main.tex añade separación6pt antes y8pt después de primera regla,6pt
antes de última; arraystretch1,15. Se usa booktabs (ya instalado) para midrule
con separación vertical en las tres tablas. Cambio propagado al generador
render.py y tabla estática; nuevas figuras/tablas en final-v3-spacing.

PDF docs/report/build/spacing-v1/main.pdf,7páginas,sin advertencias/cajas
desbordadas/referencias pendientes. Revisión visual páginas1,4,5,6,7. Ruff
correcto. Comparación de fuentes/tablas normalizando comandos de espaciado
confirma contenido numérico idéntico; figuras y CSV idénticos byte a byte.
Copia aislada recompila PDF idéntico byte a byte. No nuevas pruebas matemáticas
ni inferencias: código del entorno y datos comprobados idénticos al snapshot
anterior. Entrega nueva deliveries/challenge-v2 y ZIP challenge-v2-2026-11-08.zip,
con manifiesto recalculado y CRC/SHA del ZIP comprobados; entrega anterior
conservada íntegra. Evidencia data/units/validation/report-spacing-v2.json.

## Reconciliación definitiva solicitada por usuario, 2026-11-08

La indicación de dejar una sola versión sustituye la conservación de entregas
duplicadas del ajuste anterior. Se promovió el informe con espaciado corregido
a deliveries/challenge/ y challenge-2026-11-07.zip, nombres originales. Se
retiraron challenge-v2 y su ZIP, y los builds/figuras de informes obsoletos en
docs/report; permanecen una fuente vigente, assets final-v2 y build/final-v5.
No se tocaron versiones experimentales de datos/evaluadores ni respuestas crudas.

Copia temporal aislada recompila PDF idéntico byte a byte; sin advertencias.
Código/datos idénticos al paquete previo, siete páginas. Manifiesto recalculado
para209archivos y ZIP verificado por CRC y todos los SHA. Enlaces y documentación
actualizados. Evidencia vigente de formato: data/units/validation/report-format.json.
Las validaciones C7 anteriores siguen como evidencia histórica del contenido
y resultados, no como hash del ZIP actualizado. Sin inferencias ni gasto nuevo.

## Revisión de instrucciones para colegas, 2026-11-08

El README offline ya reproducía tareas, derivados, métricas y PDF. Se detectaron
ejemplos genéricos para reinferencia y falta de retorno a raíz tras cd report.
Se corrigió cwd y se añadió REPRODUCING.md: instalación oficial versionada,
descargas4modelos, comprobación exacta de digests, controles/piloto/baselines,
profesor/negativos, auditorías NUEVAS con hashes, persistencia/reanudación y
OpenRouter con credencial/presupuesto propios. No se prometen generaciones
idénticas por compartir semillas. Diez bloques Bash pasan bash -n; snippet
de auditorías ejecutado sobre fuentes guardadas produce178candidatas inciertas,
sin aprobarlas automáticamente. CLI run/score contrastada con argparse.
Sin descarga de pesos, inferencias ni gasto nuevo. Manifiesto y ZIP canónicos
actualizados; evidencia reproduction-docs.json.

El usuario autoriza ahora commits separados por responsabilidad/carpeta y un
mensaje guiado para colegas con URLs. Esta autorización sustituye la prohibición
previa de hacer commits; no autoriza enviar mensajes a terceros ni entrenar.

## Commits por responsabilidad autorizados, 2026-11-08

- 4bcdb87f6f3df7480d0086a899d59658b6d843fa: chore(repo): ignore local build artifacts
- d76143f449b96f8f2c7f140e8a8a21c6aec57a98: feat(challenge): add units harness and tests
- aa1cb1624feac824c21a9808382fc7e9561da597: feat(data): freeze calibrated task splits
- aad74c897d4c2761a816a7771dbf177157cccb40: feat(eval): add local and frontier baselines
- bfeead033c9c4e93bdd995f4ca97615dce4ebe97: feat(data): add audited SFT and DPO sets
- 3503ffde755f55498beaec4f36203a32ec541c15: docs(report): add validated challenge report
- 810fa3af4c25f483318644c480c6cde283caf577: docs(context): record plan and execution
- 9a87385125a1796b94c4de0ce4fa32860e2f7e17: build(delivery): package reproducible challenge

Trece pruebas pasan. Las evidencias crudas conservan espacios originales; git diff --check se aplica a código, no a logs de hardware. ProyectoCurso-2026.pdf queda sin añadir, ajeno al desafío actual. Mensaje guiado preparado en docs/contexto/2026-11-08_093607_guia_revision_equipo.md. No se envió a terceros. Se publicará la rama de revisión para habilitar URLs, sin merge a main.

Publicación completada: rama implement-units-challenge-20261107 en origin,
sin merge a main. Serie de ocho commits temáticos y mensaje guiado9b83643.
Verificación posterior:211 archivos de entrega, manifiesto y ZIP coincidentes;
solo ProyectoCurso-2026.pdf permanece sin seguimiento, por estar fuera del desafío.
Se concilia el hash del ZIP del registro de formato tras ampliar documentación;
los registros C7 previos conservan sus hashes originales como evidencia histórica.
No se enviaron mensajes a colegas.

## Estándar de PR y nombre de rama, 2026-11-08

Usuario solicita PR a main, Conventional Commits y esquema de cuatro partes,
además de rama con prefijo feat/. Se adopta feat/units-research-challenge;
se actualizan enlaces activos de la guía y se preserva la rama histórica en
metadata de inferencia (no modifica datos/hashes). Se añaden CONTRIBUTING.md
y .github/pull_request_template.md con Problema/ Cambios/ Validación/ Limitaciones.
Los diez commits anteriores cumplen el formato convencional; no se reescriben.
La rama anterior se retira del remoto solo después de publicar el nuevo nombre.

## Referencias compartidas y explicación del historial, 2026-11-08

El usuario pide compartir toda la documentación y aclarar versiones de data/units.
Verificación Git: todos los documentos de docs/ ya estaban en el PR; solo se
ignoran auxiliares regenerables de LaTeX. Faltaba ProyectoCurso-2026.pdf, antes
excluido por alcance. Se añade como referencia documental, sin iniciar proyecto
ni entrenamiento. docs/README.md indexa seguimiento; data/units/README.md separa
final-v2/derived-v3 vigentes de pilotos y derivados históricos. Se conserva
evidencia cruda y una única entrega definitiva.

## Feedback del PR #3 incorporado, 2026-11-09

Usuario confirma cierre documental para el desafío y mejoras del verificador
antes del entrenamiento del proyecto; autoriza responder al colega con citas.
Se amplían informe, README, mapa de evidencia, decisiones y plan. Verifier-9,
tareas, particiones, respuestas, métricas, tablas/figuras y 121 SFT/35 DPO se
conservan. Diagnóstico posterior separado: tres JSON finales del objetivo y
cuatro del profesor pasan la tolerancia, pero las respuestas completas siguen
unparsed; una respuesta Llama correcta usa otra unidad equivalente. No se
convierten esos casos en nuevas métricas oficiales ni se certifican sus pasos.

Validación: 13 pruebas, referencias/splits, regeneración idéntica, reconstrucción
SFT/DPO y métricas de los cinco modelos desde copia aislada. Código/datos y
resultados originales: 136 archivos protegidos idénticos. PDF de ocho páginas,
sin advertencias, recompilación aislada idéntica; tabla nueva revisada visualmente.
Evidencia: data/units/validation/pr3-feedback.json y copia en el paquete.
Manifiesto renovado: 211 archivos, ZIP: 212 entradas verificadas byte a byte.
SHA-256 ZIP actual: 4f2e66249eb327672bdfe99e0c0a376d10af0f79590dabcabe39e9d793cae7b8.
Registros C7/formato previos conservan sus hashes históricos; manifiesto y ZIP
actuales identifican la revisión documental. Cero inferencias nuevas y llamadas
pagadas. Pendiente de proyecto: versión 10 con pruebas, políticas de formato,
unidad, longitud e integración; evaluación independiente sobre nuevo test
reservado si se ajusta el evaluador con los casos actuales.

## Referencias completas, 2026-11-09

Usuario solicita autores y URL de papers. Reasoning Gym y GSM-Symbolic incluyen
todos sus autores (inicial y apellido), citas narrativas autor/año y URL de arXiv,
con autoría y orden contrastados con las fichas oficiales. Fuentes de trabajo
y entrega sincronizadas; PDF de ocho páginas sin advertencias, enlaces clicables
comprobados y recompilación aislada idéntica. Datos, código y métricas sin cambios.
Evidencia: data/units/validation/references.json y copia dentro del paquete.
Manifiesto renovado y ZIP con 213 entradas verificadas byte a byte.
SHA-256 ZIP: 5303e08cef53bf0b58eb456f3d3b955c1cffdaa4a02ac6ccf342826d0d13497d. Cero inferencias nuevas. Los registros
anteriores conservan los hashes de sus revisiones históricas del informe.

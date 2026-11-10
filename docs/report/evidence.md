# Mapa de evidencia del desafío

Rutas relativas a la raíz del repositorio. Este mapa describe la evidencia de trabajo; la entrega autocontenida y validada
está en `deliveries/challenge-clean/challenge/`, con mapa de contenidos en su
README y manifiesto. `deliveries/challenge/` conserva el paquete anterior.

| Entregable / requisitos | Evidencia concreta | Comprobación |
| --- | --- | --- |
| E1: harness, R2/R7/R10 | `src/challenge/{generator,verifier,models,evaluate,harness}.py`, `__init__.py`, `tests/test_challenge.py` | Trece pruebas con fixtures independientes, equivalencias, ataques, métricas y reanudación; `reward` sin backend |
| E1: tareas y particiones, R3 | `data/units/final-v2/{public,private}`, `protocol.json`, `units.json`, `exclusions.json`, `manifest.json`, `frozen-code/` | `harness check`; regeneración de quince archivos idénticos; 90/36/54 tareas, sin claves físicas cruzadas |
| E2: problema y diseño, R1/R3/R8 | `docs/report/content.tex`, especificación y calibración en `docs/contexto/` | Tres familias, dos estructuras, tres variantes agrupadas; límites de dificultad y originalidad explícitos |
| E3: SFT/DPO, R4/R5 | `data/units/derived-v3/{sft,dpo}.jsonl`, `stats.json`, `manifest.json`, `audits/` | `harness check-derived`; 121 SFT y 35 DPO solo de train; preferred aceptadas y rejected con error numérico |
| E3: procedencia y calidad | `data/units/runs/{train-teacher-v1,train-negatives-v1}`, `data/units/derivation-v1/negative-tasks.jsonl`, cuatro archivos `audit-*.jsonl` | 360 respuestas de Qwen3-8B, 114 de Qwen3-1.7B; 178 candidatas auditadas, 121 keep/57 reject; máximo dos pares sin reutilización |
| E4: calibración, R1/R9 | `data/units/pilot-calibrated/`, `data/units/pilot-v{1,2,3}/`, corridas piloto, informe C3 | Respuestas anteriores preservadas; 132/270 aciertos en composición calibrada; luminosidad difícil cerca del suelo |
| E4: línea base, R6/R9 | `data/units/runs/baseline-v1/{qwen17,llama,smol,qwen8}/` | Cada corrida completa debe tener 162 respuestas y `scores/v9`; `harness compare` reconstruye matriz, etiquetas y huellas |
| E4: ejemplos y límites | `baseline-v1/*/qualitative.jsonl`, `docs/report/content.tex` | Ejemplos con ID, muestra y hash; revisión auxiliar identificada; no alteran las métricas automáticas |
| Robustez / recálculos, R7/R9 | `data/units/verifier-v8-v9/`, historias de evaluador del piloto, tests | Motivo y respuestas afectadas; v9 congelado antes del test; no confundir mejora del parser con mejora del modelo |
| Recursos / reproducción | `data/units/preflight/2026-11-07_200958/`, metadata de corridas, `data/units/validation/`, `pyproject.toml`, `uv.lock` | CPU/GPU/RAM/driver/backend/cuántización reales; pruebas y reconstrucción desde copias aisladas sin pesos |
| Informe y snapshot final | Template del usuario, PDF compilado, comparación OpenRouter y `deliveries/challenge/` | Template recibido en `docs/report/template/`; Completos: `deliveries/challenge/` y ZIP, segunda copia aislada validada |

La distribución SFT fácil/media/difícil es 51/46/24; DPO 7/15/13. Las nueve
celdas contienen ejemplos, pero algunas tienen solo una traza: no se declara
balance ni suficiencia para el proyecto. No se inició ningún entrenamiento.

La aceptación por número final y tolerancia del 1% es una medida automática;
la coherencia de los pasos se revisa por separado. `unparsed` no equivale a un
error matemático. El informe debe conservar cobertura y cotas optimistas junto
con pass@1/pass@3. Las variantes relacionadas reducen independencia estadística.

C7 cerrado técnicamente: template y autoría recibidos, inferencias externas
completas, PDF original de siete páginas revisado y paquete reproducido desde segunda
copia aislada con entorno nuevo. Evidencia `data/units/validation/c7-delivery-isolated.json`.
Referencia: 162 respuestas, 133 correctas y 29 unparsed; costo con controles
USD0,0935116. No se entrenó ni se enviaron correos.

Plazo informado por el usuario el 7 de noviembre: 12 de noviembre de 2026,
23:59; intención de entregar alrededor del martes 10. La palabra viernes
no coincide con esa fecha (jueves); se registra la fecha numérica explícita.
Canal previsto informado por el usuario: correo al docente, envío a cargo del equipo.

Reconciliación de formato 2026-11-08: única entrega definitiva `deliveries/challenge/` y `challenge-2026-11-07.zip`; PDF con espaciado revisado. Validación de esta revisión: `data/units/validation/report-format.json`.

Revisión documental 2026-11-09, feedback del PR #3: PDF entonces de ocho páginas,
tabla de límites confirmados y diagnósticos separados de las métricas oficiales.
Verificador 9, tareas, respuestas, SFT/DPO, tablas y figuras sin cambios;
sin nuevas inferencias. Evidencia de recálculo, integridad y recompilación aislada:
`data/units/validation/pr3-feedback.json`. Los registros C7 anteriores describen
sus paquetes históricos; el manifiesto actual identifica el paquete revisado.

Síntesis editorial posterior: PDF vigente de siete páginas, sin contexto interno
del repositorio. Se conservan límites confirmados, especificación y resultados;
evidencia actual: `data/units/validation/report-concision.json`.

Revisión posterior de claridad: misma extensión de siete páginas, con tabla
explícita de particiones y definiciones para lectores sin contexto del repositorio.
Comprobaciones de cantidades y artefactos: `data/units/validation/report-clarity.json`.

Entrega mínima vigente: `deliveries/challenge-clean/challenge.zip`. Mantiene
el mismo dataset y textos SFT/DPO con rutas limpias y métricas documentadas en
el informe. Las rutas de uso apuntan a archivos incluidos en `challenge/`. README
e informe ofrecen acceso al repositorio como consulta complementaria opcional,
sin remitir a rutas internas ni necesitarlo para los comandos documentados. Los registros
anteriores corresponden a sus snapshots históricos; la verificación actual está
en `data/units/validation/self-contained-delivery.json`.

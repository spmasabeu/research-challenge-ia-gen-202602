# Mapa de los cuatro entregables

| Requisito | Evidencia y comprobación |
| --- | --- |
| E1 / R2,R3,R7,R10 | code/src/challenge;13tests;data/final-v2 con manifest,refs privadas,prompts públicos,semillas,exclusiones;harness check/freeze |
| E2 / R1,R3,R8 | report/informe.pdf secciones1–4;content.tex;protocol.json;ejemplo train57,95m/s;calibración y límites |
| E3 / R4,R5 | data/derived-v3:121SFT/35DPO;audits178;raw teacher360 y objetivo114;check-derived/derive reproduce fuentes,deduplicación y pares sin reutilización |
| E4 / R6,R9 | results/baseline-v1 y frontier-v1/test;810respuestas comunes;pass@1/3,cobertura,cotas,ejemplos,calibración;compare y frontier score |
| Reproducción / robustez | results/validation;manifest;historial v8–v9 y adaptador2–3;fixtures numéricos,contradicciones,JSON duplicado,no finitos,unidades y presupuesto;sin pesos ni secretos |

Auditorías contextuales de agentes identificadas, no certificación humana.
No se realizó entrenamiento. El PDF explica cantidades menores que metas
orientativas4000/2000,desbalance y posibles falsos negativos del parser.

Revisión documental del PR #3, 2026-11-09: PDF entonces de ocho páginas con límites
confirmados, diagnóstico de extracción y decisión de conservar verifier-9.
Resultados oficiales y SFT/DPO sin cambios; mejoras previstas antes del
entrenamiento del proyecto. Validación: `results/validation/pr3-feedback.json`.
Los registros de validación anteriores conservan sus paquetes y fechas originales.

Informe vigente: siete páginas tras síntesis editorial, con los mismos datos,
métricas y límites técnicos. Validación: `results/validation/report-concision.json`.

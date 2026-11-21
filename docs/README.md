# Documentación del equipo

| Carpeta | Contenido | Por dónde empezar |
| --- | --- | --- |
| `contexto/` | Requisitos, aclaraciones docentes, decisiones, especificación, calibración y bitácora | [Requisitos del desafío](contexto/2026-11-07_123729_requisitos_metodologia_entregables_units.md) |
| `plans/` | Plan de ejecución y checklist C0–C7, con evidencia de cierre | [Checklist del desafío](plans/2026-11-07_130305_ejecucion_desafio_units.md) |
| `report/` | Informe vigente: fuentes LaTeX, template original, figuras, tablas y PDF | [Informe y reproducción](report/README.md) |

Para revisar lo implementado por responsabilidad: [guía del equipo](contexto/2026-11-08_093607_guia_revision_equipo.md).
Para reconstruir cómo se llegó al resultado: [bitácora](contexto/2026-11-07_200958_bitacora_ejecucion_desafio_units.md).
Para comprobar requisitos contra archivos: [mapa de evidencia](report/evidence.md).

Proyecto, entrega 1: [requisitos y decisiones](contexto/2026-11-09_202333_requisitos_entrega_1_proyecto.md),
[plan de ejecución](plans/2026-11-09_202333_entrega_1_proyecto.md) y
[propuesta PDF y fuentes](../deliveries/project-1-proposal/README.md).
Estado: E1 entregada según confirmación del equipo, tres páginas de contenido más referencias;
[PR #4](https://github.com/spmasabeu/research-challenge-ia-gen-202602/pull/4) integrado en main.

Proyecto, entrega 2: [requisitos, entregable, implementación por dependencias, pruebas y análisis](plans/2026-11-16_095503_entrega_2_proyecto.md).
PR #6 integrado: seis familias disponibles. La ejecución técnica conserva
verifier-11, dataset1.800/360/360,3.362trazas SFT y769pares DPO con excepciones
justificadas,42pruebas CPU y pruebas GPU reales. Control, SFT, GRPO y SFT→GRPO
completaron evaluación común360×3; curvas, intervalos, costos y checkpoints están
en el [respaldo técnico](../data/units/project-e2/README.md). I2–I7 ejecutadas;
I8 tiene análisis técnico y muestras, pero falta revisión humana. I9 (informe/PDF)
queda para una etapa posterior. E2 todavía no está completa.

Los enunciados están en la raíz: [Desafío](../DesafioInvestigacion-2026.pdf) y
[Proyecto posterior](../ProyectoCurso-2026.pdf). El segundo se comparte como
referencia; en la entrega del desafío no se ejecutaron entrenamientos del proyecto.

La entrega vigente está en [deliveries/challenge-clean](../deliveries/challenge-clean/README.md),
con ZIP mínimo de informe, código y datos, y nombres de carpetas sin versiones. El paquete
anterior se conserva intacto en `deliveries/challenge/`.
El historial de experimentos está en [data/units](../data/units/README.md).
Los directorios `derived-v1`, `pilot-v1`, etc. preservan intentos, ajustes y
filtrado; no son otras entregas finales. Su estado se identifica en ese README.

Todos estos documentos, fuentes y PDFs están versionados. Solo se excluyen
auxiliares de compilación LaTeX y archivos locales como credenciales, entornos
y pesos. Esos auxiliares se regeneran al compilar y no hacen falta para replicar.

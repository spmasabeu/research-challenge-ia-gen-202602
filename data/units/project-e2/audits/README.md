# Auditoría humana pendiente de E2

Las muestras `pending/control-human-pending.jsonl` (52 trazas) y
`pending/grpo-human-pending.jsonl` (53 trazas) están seleccionadas, pero no revisadas por
personas. `pending/sft-human-pending.jsonl` añade51 respuestas del adaptador SFT;
luminosidad difícil no aporta ninguna al no haber éxitos.
`pending/hybrid-human-pending.jsonl` contiene52 éxitos SFT→GRPO. Son208 respuestas
de las cuatro rutas en total, todas pendientes de revisión humana.
`pending/sft-data-human-pending.jsonl` añade 53 trazas del corpus de entrenamiento
retenido, también sin revisar por personas. Su población y hashes están en
`sft-data-human-selection.json`; no son respuestas del adaptador SFT evaluado.
Los archivos de producción y las inspecciones con `reviewer_type: agent`
registran trabajo de agentes; no satisfacen la auditoría humana.

Cada muestra contiene hasta tres éxitos únicos por familia/nivel, seleccionados
con semilla 7304. La deduplicación solo elimina diferencias de espacios y conserva
las fuentes. Hay menos de 54 registros cuando alguna celda no tiene tres éxitos
únicos. `status: correct` significa recompensa programática 1, no razonamiento
certificado. `reference_si` está en unidades SI; convertir antes de compararla con
la unidad solicitada en el prompt.

Los originales se conservan en `pending/`. Las copias para completar ya están
en `reviewed/`, por ejemplo `reviewed/control-human-reviewed.jsonl`. El nombre
`reviewed` no acredita revisión: los dictámenes siguen vacíos hasta que una
persona los complete. Una persona debe leer
el prompt y la respuesta, recalcular los pasos y completar únicamente:

- `auditor`: identificador de la persona responsable.
- `reviewer_type`: `human`.
- `judgment`: `keep`, `reject` o `uncertain`.
- `reason`: cálculo comprobado o defecto concreto; no basta repetir la etiqueta
  del verificador.

Comprobar datos usados, suma de magnitudes cuando corresponda, conversiones,
fórmula, operaciones y conclusión. Aceptar redondeos/truncamientos coherentes;
señalar operaciones incorrectas aunque la respuesta final esté dentro del 1 %.
Distinguir un error de cálculo de una infracción de formato. Si no se puede
resolver un caso, usar `uncertain` y explicar qué falta. Mantener IDs, prompts,
respuestas, fuentes, semillas y hashes intactos. No corregir la respuesta del
modelo en el registro auditado ni cambiar retrospectivamente su recompensa.

Al analizar, informar revisados, pendientes y dictámenes por ruta y celda. No
presentar las trazas como problemas físicos independientes ni usar la
proporción estratificada sin ponderar como estimación de todos los éxitos. Una
muestra pequeña tampoco certifica todo el corpus. Los casos dirigidos de error
permanecen separados de estas muestras aleatorias.

Esta guía y las muestras preparadas no completan R10/V11. Registrar la fecha y
los archivos efectivamente revisados al recibir los dictámenes humanos.

La calibración contiene 26 casos en `pending/calibration-human-pending.jsonl`,
con su copia en `reviewed/calibration-human-reviewed.jsonl`. En total hay
287 casos para revisar en seis archivos.

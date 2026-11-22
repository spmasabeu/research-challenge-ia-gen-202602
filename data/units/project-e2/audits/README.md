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

## Responsables asignados

| Auditor | Archivos en `reviewed/` | Casos |
| --- | --- | ---: |
| fernando | `calibration-human-reviewed.jsonl`, `control-human-reviewed.jsonl` | 78 |
| rodrigo | `grpo-human-reviewed.jsonl`, `hybrid-human-reviewed.jsonl` | 105 |
| benjamin | `sft-human-reviewed.jsonl`, `sft-data-human-reviewed.jsonl` | 104 |

El campo `auditor` registra la asignación; no acredita revisión completada.
`reviewer_type`, `judgment` y `reason` permanecen vacíos hasta que el responsable
compruebe cada caso. Solo entonces debe registrar `reviewer_type: human`, su
dictamen y motivo. Los originales de `pending/` se conservan intactos.

## Criterio acordado para operaciones

El 1 % es la tolerancia del verificador automático; la revisión humana comprueba
además cada operación escrita. Un redondeo o truncamiento coherente se acepta
(`10/3 ≈ 3.33` → `keep`). Un dígito que no proviene de redondear el valor
correcto es un error aritmético aunque el resultado final pase el 1 %
(`10/3 ≈ 3.31` → `reject`). El motivo distingue el tipo de error, por ejemplo
`Planteamiento correcto, error aritmético: 0.222 * 827 = 184.586 (correcto: 183.594)`,
para que el informe pueda reportar por separado errores aritméticos y de
procedimiento. El rechazo humano no cambia la recompensa automática.

## Herramienta de revisión

`scripts/audit_review_server.py` abre una interfaz local que muestra cada caso
con el prompt, la respuesta renderizada y una calculadora determinista
(`scripts/audit_calc.py`). La calculadora recalcula el valor esperado a partir
de los datos del prompt y comprueba cada igualdad y conversión escrita:
`OK` (redondeo coherente), `≈ trunc.` (truncamiento exacto), `⚠️ DESVÍO`
(< 0.5 %, no proviene de redondear) y `❌ ERROR` (≥ 0.5 %). No emite dictámenes:
no evalúa la elección de fórmula, los datos copiados ni la coherencia conceptual,
y puede omitir pasos escritos solo en prosa.

```bash
python scripts/audit_review_server.py grpo hybrid   # prefijos de reviewed/
```

La interfaz solo escribe `reviewer_type`, `judgment` y `reason` en la línea
correspondiente, comprueba que el resto del registro no cambie y reescribe el
archivo de forma atómica. `python scripts/audit_calc.py <archivo.jsonl>` genera
la misma información como hoja Markdown.

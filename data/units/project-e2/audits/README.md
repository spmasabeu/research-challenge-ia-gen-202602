# Auditoría humana de E2

## Resultados de la revisión humana

El informe de E2 usa los 287 dictámenes originales de Fernando, Rodrigo y
Benjamín. Los conteos describen las muestras revisadas. La selección
estratificada por familia y dificultad limita su extrapolación al conjunto
de las respuestas.

| Archivo | Revisados | `keep` | `reject` | `uncertain` |
| --- | ---: | ---: | ---: | ---: |
| [Calibración](reviewed/calibration-human-reviewed.jsonl) | 26 | 2 | 24 | 0 |
| [Control](reviewed/control-human-reviewed.jsonl) | 52 | 12 | 40 | 0 |
| [GRPO](reviewed/grpo-human-reviewed.jsonl) | 53 | 25 | 28 | 0 |
| [Híbrido](reviewed/hybrid-human-reviewed.jsonl) | 52 | 21 | 31 | 0 |
| [Corpus SFT](reviewed/sft-data-human-reviewed.jsonl) | 53 | 48 | 5 | 0 |
| [SFT](reviewed/sft-human-reviewed.jsonl) | 51 | 21 | 30 | 0 |
| **Total** | **287** | **129** | **158** | **0** |

Versiones de los dictámenes originales: Fernando en `dcf2ead`, Rodrigo
en `6904833` y Benjamín en `7ce9c28`. Los resultados se presentan en el
[informe de E2](../../../../deliveries/project-2-progress/proyecto_entrega_2.pdf).

## Estado de la revisión de Benjamín — 22 de noviembre de 2026

Los 104 casos asignados a `benjamin` tienen dictamen y motivo en las copias de
`reviewed/`. Los dictámenes se analizaron con apoyo de IA y fueron confirmados
por Benjamín. Los dos casos inicialmente dudosos se clasificaron como `reject`
por errores de explicación; no quedan dictámenes `uncertain`.

| Archivo | Casos | `keep` | `reject` | `uncertain` |
| --- | ---: | ---: | ---: | ---: |
| [sft-human-reviewed.jsonl](reviewed/sft-human-reviewed.jsonl) | 51 | 21 | 30 | 0 |
| [sft-data-human-reviewed.jsonl](reviewed/sft-data-human-reviewed.jsonl) | 53 | 48 | 5 | 0 |
| **Total** | **104** | **69** | **35** | **0** |

Los 35 rechazos se distinguen por tipo de error:

- 30 respuestas con errores aritméticos que pasan el margen automático del 1 %.
- 3 respuestas con conversiones mal justificadas, aunque su resultado numérico
  sea correcto.
- 2 respuestas con errores de explicación: calculan correctamente la tensión,
  pero afirman que hay dos resistencias cuando el problema proporciona una sola.
  Corresponden a las líneas 47 y 48 de `sft-data-human-reviewed.jsonl`
  (casos 98 y 99 de la revisión conjunta).

Se aceptaron redondeos y truncamientos coherentes.

Estos conteos describen las muestras revisadas, no la tasa global de errores del
modelo o del corpus. Se conservaron los originales de `pending/`, las respuestas
y las etiquetas automáticas. Esta sección detalla la parte de la muestra que revisó Benjamín.

## Preparación inicial de las muestras e instrucciones

Las referencias a revisiones pendientes o campos vacíos a continuación describen
el estado inicial de preparación. La tabla de resultados reúne todos los
dictámenes registrados.

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
y puede omitir operaciones no reconocidas, incluso fórmulas explícitas. La ausencia
de alertas no acredita que los pasos estén comprobados.

```bash
python scripts/audit_review_server.py grpo hybrid   # prefijos de reviewed/
```

La interfaz solo escribe `reviewer_type`, `judgment` y `reason` en la línea
correspondiente, comprueba que el resto del registro no cambie y reescribe el
archivo de forma atómica. `python scripts/audit_calc.py <archivo.jsonl>` genera
la misma información como hoja Markdown.

La calculadora contempla ahora cadenas de una misma variable entre líneas y
cantidades intermedias en km/s; reconoce separadores de miles para inspeccionar
la aritmética, sin cambiar la política de formato del verificador. Sus 11 pruebas
incluyen regresiones de las operaciones omitidas. Evalúa solo un árbol de
números y operadores, sin `eval`. No produce ni confirma dictámenes humanos.

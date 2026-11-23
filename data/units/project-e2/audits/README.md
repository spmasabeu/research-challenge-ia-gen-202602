# Auditoría humana de E2

## Estado integrado — 23 de noviembre de 2026

Se incorporan las muestras de los PR #7, #8 y #9. Hay **274 dictámenes humanos
conservados y 13 correcciones de agente pendientes de confirmación humana**.
Estas últimas llevan `auditor: codex` y `reviewer_type: agent`; los originales
humanos se conservan en los commits indicados en las secciones de correcciones.
No se presenta esta revisión de agente como una nueva auditoría humana.

Los siguientes conteos mezclan dictámenes humanos y propuestas de corrección;
son **provisionales**, no tasas globales ni un ranking entre modelos:

| Archivo | Casos | keep | reject | Humanos | Correcciones de agente |
| --- | ---: | ---: | ---: | ---: | ---: |
| `calibration-human-reviewed.jsonl` | 26 | 2 | 24 | 24 | 2 |
| `control-human-reviewed.jsonl` | 52 | 12 | 40 | 49 | 3 |
| `grpo-human-reviewed.jsonl` | 53 | 19 | 34 | 47 | 6 |
| `hybrid-human-reviewed.jsonl` | 52 | 20 | 32 | 50 | 2 |
| `sft-data-human-reviewed.jsonl` | 53 | 48 | 5 | 53 | 0 |
| `sft-human-reviewed.jsonl` | 51 | 21 | 30 | 51 | 0 |
| **Total** | **287** | **122** | **165** | **274** | **13** |

La auditoría sigue abierta hasta que las personas responsables contrasten las
13 correcciones (5 de Fernando y 8 de Rodrigo). Para confirmarlas deben registrar
su propio `auditor`, `reviewer_type: human`, el dictamen que determinen y su
motivo; las correcciones del agente permanecen respaldadas en Git. No confirmar
en bloque ni copiar dictámenes sin comprobar los casos. Los 104 registros de
Benjamín se conservaron íntegros. Las 287 filas tienen motivo, pero eso no
significa 287 dictámenes humanos finales. R10/V11 e I8 siguen parcialmente
pendientes. El [informe de E2](../../../../deliveries/project-2-progress/proyecto_entrega_2.pdf)
presenta los conteos humanos y el número de correcciones de agente. Test permanece reservado.

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
y las etiquetas automáticas. Este estado solo corresponde a la revisión de
Benjamín; no declara completada la auditoría del equipo ni la Entrega 2.

## Preparación inicial de las muestras e instrucciones

Las referencias a revisiones pendientes o campos vacíos a continuación describen
el estado inicial de preparación. Para los dos archivos de Benjamín, prevalece
el estado actualizado de la sección anterior.

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

## Correcciones de revisión del PR #8 — 23 de noviembre de 2026

Se corrigen 8 registros tras contrastar las operaciones. Sus dictámenes
humanos originales permanecen en el commit `6904833092b4ae8c52e5d34286646cf0ca3e5975`.
Los registros modificados llevan `auditor: codex` y `reviewer_type: agent`: son
correcciones asistidas, **pendientes de confirmación humana**, incluso cuando
solo cambia el motivo. No se atribuyen al auditor original ni cambian la
recompensa automática. El resto de los dictámenes humanos se conserva intacto.

| Archivo (prefijo) | Línea | Dictamen original → corrección |
| --- | ---: | --- |
| `grpo` | 16 | keep → reject |
| `grpo` | 18 | keep → reject |
| `grpo` | 19 | keep → reject |
| `grpo` | 21 | keep → reject |
| `grpo` | 24 | keep → reject |
| `grpo` | 25 | keep → reject |
| `hybrid` | 1 | keep → reject |
| `hybrid` | 2 | keep → keep |

La calculadora contempla ahora cadenas de una misma variable entre líneas y
cantidades intermedias en km/s; reconoce separadores de miles para inspeccionar
la aritmética, sin cambiar la política de formato del verificador. Sus 11 pruebas
incluyen regresiones de las operaciones omitidas. Evalúa solo un árbol de
números y operadores, sin `eval`. No produce ni confirma dictámenes humanos.

## Correcciones de revisión del PR #7 — 23 de noviembre de 2026

Se corrigen 5 registros tras contrastar las operaciones. Sus dictámenes
humanos originales permanecen en el commit `dcf2ead8435c005b49bb211db9a57adf3f24b08b`.
Los registros modificados llevan `auditor: codex` y `reviewer_type: agent`: son
correcciones asistidas, **pendientes de confirmación humana**, incluso cuando
solo cambia el motivo. No se atribuyen al auditor original ni cambian la
recompensa automática. El resto de los dictámenes humanos se conserva intacto.

| Archivo (prefijo) | Línea | Dictamen original → corrección |
| --- | ---: | --- |
| `calibration` | 13 | reject → reject |
| `calibration` | 23 | reject → reject |
| `control` | 6 | keep → reject |
| `control` | 29 | reject → reject |
| `control` | 33 | reject → keep |

# Datos

- `units-v1/`: `train.jsonl` (900), `eval.jsonl` (270), `test.jsonl` (270) y
  `manifest.json` con sha256. Generado con
  `PYTHONPATH=src python3 -m challenge.generator --out data/units-v1` (idempotente;
  se niega a sobrescribir un split distinto). Una nueva versión del generador va
  en otra carpeta (`units-v2/`), nunca encima.
- `units-v1/derived/`: `sft.jsonl` y `dpo.jsonl` exportados con `challenge.derive`,
  solo desde train.

Cada tarea incluye `id`, `instance_id`, `split`, `family`, `level`, `base`, `spec`,
`prompt`, `requested_unit` y `answer` (la referencia; no se envía al modelo,
y el bloque `DATOS` del prompt no la contiene).

`test` está congelado: no ajustar nada mirando sus resultados. Las ejecuciones
de modelos van en `runs/` (no versionado); copiar aquí o a `docs/` solo los
resúmenes que use el informe.

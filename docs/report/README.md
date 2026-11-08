# Informe del desafío de unidades

Autores por apellido: Fernando Fajardo, Sebastian Palma, Benjamin Prieto y
Rodrigo Ugarte. `main.tex` adapta el template del usuario; `template/` preserva
original y escudo con huellas. Se añadieron amsmath y ajuste del tamaño del
escudo, manteniendo geometría, clase y cabecera. `content.tex` corresponde al
desafío, sin entrenamientos del proyecto posterior.

Las tablas y figuras proceden de los cuatro locales y DeepSeek-V4-Pro-0813
vía OpenRouter/DeepInfra FP8. Son 162 respuestas por modelo con verificador 9.
Las cotas optimistas de extracción se muestran junto a pass@1/pass@3;
no son intervalos de confianza. La autoría de las revisiones contextuales
auxiliares está identificada, sin presentarla como certificación humana.

Desde la raíz, usando destinos nuevos:

```bash
uv sync --locked --group report
PYTHONPATH=src uv run --no-sync python -m challenge.harness compare --dataset data/units/final-v2 --runs data/units/runs/baseline-v1 --out /tmp/units-comparison.json
PYTHONPATH=src uv run --no-sync python -m challenge.frontier score --tasks data/units/final-v2/private/test.jsonl --run data/units/runs/frontier-v1/test --out /tmp/units-frontier-score
uv run --no-sync python docs/report/render.py --comparison /tmp/units-comparison.json --calibration data/units/pilot-calibrated/scores/v9/summary.json --derived data/units/derived-v3/stats.json --frontier /tmp/units-frontier-score --out /tmp/units-report-assets
cd docs/report
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build/reproduced main.tex
```

`final-v2/` contiene las figuras PDF vectoriales/PNG, tablas LaTeX y CSV y sus
huellas, referenciadas por content.tex. El destino temporal del renderer permite
compararlas sin sobrescribir; para integrarlas se conservan nombres relativos.
Se conserva una única versión definitiva del informe y sus figuras.
Ningún comando anterior realiza inferencia ni necesita credenciales o pesos.

Herramientas: Python 3.12.13, uv 0.11.16, Matplotlib 3.11.2 opcional; latexmk
4.88, pdfTeX 1.40.29/TeX Live 2026, lmodern, graphicx, amsmath, booktabs, hyperref y
babel-spanish con hyphen-spanish. PDF vigente: `build/final-v5/main.pdf`, siete páginas, sin advertencias finales
de LaTeX, revisado y copiado a `deliveries/challenge/report/informe.pdf`.
C7 cerrado tras reproducción completa aislada y revisión independiente. El PDF de vista previa aportado
en sandbox no es el informe.

[Mapa de evidencia](evidence.md) y [bitácora](../contexto/2026-11-07_200958_bitacora_ejecucion_desafio_units.md).

Revisión 2026-11-08: separación 6/8pt alrededor de la primera regla del encabezado, 6pt antes de la última; filas de tablas1,15x y reglas booktabs con espacio superior/inferior. PDF siete páginas, sin advertencias; recompilación aislada idéntica byte a byte. Código/datos/figuras/CSV sin cambios y entrega reconciliada con el nombre original.

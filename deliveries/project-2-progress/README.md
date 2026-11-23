# Proyecto · Entrega 2

[Informe de la Entrega 2](proyecto_entrega_2.pdf). El PDF sigue la maqueta de la Entrega 1 y reúne los resultados de validación, las curvas de entrenamiento y los 287 dictámenes humanos originales.

Las fuentes incluyen el [texto](source/content.tex), las [tablas de anexos](source/tables.tex), el [encabezado](source/main.tex) y las figuras. La documentación de trabajo reúne el [checklist de aceptación](../../docs/plans/2026-11-23_informe_entrega_2.md), el [respaldo técnico](../../data/units/project-e2/README.md) y el [registro de auditoría](../../data/units/project-e2/audits/README.md).

Para compilar desde esta carpeta, con pdfLaTeX y latexmk:

```bash
e2_build=$(mktemp -d)
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error -outdir="$e2_build" source/main.tex
```

El resultado queda en `$e2_build/main.pdf`.

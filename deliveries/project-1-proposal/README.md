# Proyecto · Entrega 1: propuesta

Entrega: [propuesta.pdf](propuesta.pdf), tres páginas de contenido y una de
referencias. Incluye revisión bibliográfica, investigación tentativa y entorno.

Enviar únicamente `propuesta.pdf` por la casilla de Canvas el **11 de noviembre
de 2026 a las 23:59**, según confirmación del usuario. Las fuentes LaTeX están
en `source/` y reutilizan el template del desafío.

- [Requisitos y decisiones](../../docs/contexto/2026-11-09_202333_requisitos_entrega_1_proyecto.md).
- [Plan de ejecución](../../docs/plans/2026-11-09_202333_entrega_1_proyecto.md).

La propuesta estudiará el efecto del SFT previo sobre RL con Qwen3-1.7B en
el entorno de unidades. Se mantienen los autores del desafío y la RTX 3050
como recurso inicial, con ampliación posible mediante otro colaborador.

El documento propone cinco caminos, GRPO como candidato para las ramas de RL,
comparación de cómputo y auditoría humana. Los límites concretos de entrenamiento
dependen de un piloto de memoria y tiempo todavía no realizado. Los resultados
del desafío se presentan como antecedentes, no como resultados del proyecto.

## Compilar

Requiere pdfLaTeX, latexmk y los paquetes del template: lmodern, geometry,
graphicx, xcolor, amsmath, booktabs, hyperref y babel con soporte de español.
Desde esta carpeta:

```bash
project_proposal_build=$(mktemp -d)
export project_proposal_build
cd source
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir="$project_proposal_build" main.tex
cd ..
cmp propuesta.pdf "$project_proposal_build/main.pdf"
```

Con la misma instalación TeX, `cmp` sin salida verifica igualdad byte a byte.
Otras versiones pueden alterar la maquetación o los bytes sin cambiar contenido.
Los auxiliares se generan fuera de la entrega. Si se editan las fuentes, revisar
el nuevo PDF y copiarlo a `propuesta.pdf` después de validar su contenido.

No se ejecutaron entrenamientos ni inferencias nuevas para elaborar la propuesta.

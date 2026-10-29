# Desafío de investigación · IIC3694

Construir un harness y dataset reproducibles para mejorar razonamiento de un LLM
pequeño (1–2B). [Enunciado](DesafioInvestigacion-2026.pdf).

**Estado:** estructura inicial; implementación pendiente. El entrenamiento queda
para el proyecto posterior.

## Entregables

- Harness con prompts, parser y `reward(prompt, completion) -> float`.
- Tareas generadas por código, dificultad graduada y particiones `train/eval/test`.
- Trazas verificadas para SFT y pares correcto/incorrecto para DPO.
- Línea base de varios modelos: pass@1 y pass@k por dificultad.
- Informe de calibración, robustez del verificador y limitaciones.

## Estructura

```text
src/     # código del entorno, generación y evaluación
tests/   # pruebas, especialmente del generador y verificador
 data/   # tareas, trazas y resultados de experimentos
 docs/   # decisiones, referencias e informe
```

Crear subdivisiones solo cuando haya contenido que las necesite.

## Entorno

Requisito: [uv](https://docs.astral.sh/uv/). Python 3.12 y dependencias fijadas:

```bash
uv sync --locked
uv run python --version
```

Todavía no hay comandos de generación o evaluación. Al agregar dependencias,
versionar juntos `pyproject.toml` y `uv.lock`. No subir secretos ni pesos de modelos.

## Trabajo del equipo

- Una rama por cambio; revisar antes de integrar.
- Registrar acuerdos en [docs/decisiones.md](docs/decisiones.md) y preguntas,
  modelos y referencias en [docs/temas.md](docs/temas.md).
- Empezar con 50–100 tareas piloto de planificación con restricciones. Ajustar
  dificultad para que el modelo pequeño tenga aciertos y errores.
- Probar soluciones equivalentes e intentos de engañar al verificador.
- Calibrar con piloto/validación; congelar test antes de la evaluación final.

## Reproducibilidad

- Compartir tareas con IDs, semillas, versión y hashes; evitar duplicados entre
  splits y mantener las respuestas de referencia fuera del prompt.
- Registrar commit, configuración, revisión del modelo/tokenizer, backend,
  hardware, cuantización, modo de razonamiento, muestreo, tokens y turnos.
- Guardar prompts, respuestas, recompensas y versiones del dataset/verificador.
  pass@k requiere múltiples muestras por problema y un protocolo común.
- Derivar SFT/DPO exclusivamente de train; para DPO emparejar respuestas del mismo
  problema. Para artefactos grandes, compartir ubicación, versión y checksum.
- Conservar respuestas permite recalcular métricas; regenerarlas puede variar
  entre hardware o servicios, incluso con semilla.

# Desafío de investigación · IIC3694

Construir un harness y dataset reproducibles para mejorar razonamiento de un LLM
pequeño (1–2B). [Enunciado](DesafioInvestigacion-2026.pdf).

**Estado:** cinco spikes nuevos implementados y evaluados; spike de unidades
validado. El harness principal, las particiones finales y los datos SFT/DPO
siguen pendientes. El entrenamiento queda para el proyecto posterior.

Spike exploratorio: [problemas cuantitativos con unidades](spikes/units/README.md), con instrucciones para comparar Qwen3-1.7B y Llama 3.2-1B sobre 90 tareas con tres intentos por tarea y modelo y comprobar los resultados vigentes. No cambia el tema acordado automáticamente.

[Comparación de los seis temas, resultados y recomendación para el desafío](spikes/README.md).

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
data/    # tareas, trazas y resultados de experimentos
docs/    # decisiones, referencias e informe
spikes/  # experimentos autocontenidos, separados del harness principal
```

Crear subdivisiones solo cuando haya contenido que las necesite.

## Entorno

Requisito: [uv](https://docs.astral.sh/uv/). Python 3.12 y dependencias fijadas:

```bash
uv sync --locked
uv run python --version
```

Los comandos del spike están en [su README](spikes/units/README.md). Al agregar dependencias,
versionar juntos `pyproject.toml` y `uv.lock`. No subir secretos ni pesos de modelos.

## Trabajo del equipo

- Una rama por cambio; revisar antes de integrar.
- Registrar acuerdos en [Decisiones](docs/2026-10-29_093018_decisiones.md) y preguntas,
  modelos y referencias en [Temas](docs/2026-10-29_093018_temas.md).
- Nombrar documentos `AAAA-MM-DD_HHMMSS_tema.md` con hora de Santiago. Mantener
  el nombre al editar; fechar nuevas entradas dentro del documento.
  En `spikes/units/`, conservar los nombres estables `README.md` y `report.md`.
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

# Desafío de investigación · IIC3694

Construir un harness y dataset reproducibles para mejorar razonamiento de un LLM
pequeño (1–2B). [Enunciado](DesafioInvestigacion-2026.pdf).

**Estado:** C0–C7 cerrados; entrega técnica validada. [Bitácora](docs/contexto/2026-11-07_200958_bitacora_ejecucion_desafio_units.md). Harness y trece pruebas implementados. Splits 90/36/54 congelados; 121 trazas SFT y 35 pares DPO validados. [Comandos](data/units/README.md). El entrenamiento queda para el proyecto posterior.

Spike exploratorio: [problemas cuantitativos con unidades](spikes/units/README.md), con instrucciones para comparar Qwen3-1.7B y Llama 3.2-1B sobre 90 tareas con tres intentos por tarea y modelo y comprobar los resultados vigentes. Es un antecedente de desarrollo, separado del test final.

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
docs/contexto/ # decisiones, referencias y requisitos de los enunciados
docs/plans/    # planes de ejecución con checkpoints y criterios de éxito
spikes/  # experimentos autocontenidos, separados del harness principal
```

Crear subdivisiones solo cuando haya contenido que las necesite.

## Documentación y planificación

- [Requisitos y entregables del desafío](docs/contexto/2026-11-07_123729_requisitos_metodologia_entregables_units.md).
- [Requisitos y entregables del proyecto](docs/contexto/2026-11-07_124743_requisitos_metodologia_entregables_proyecto_units.md).
- [Borrador del plan de ejecución del desafío de unidades](docs/plans/2026-11-07_130305_ejecucion_desafio_units.md).

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
- Registrar acuerdos en [Decisiones](docs/contexto/2026-10-29_093018_decisiones.md) y preguntas,
  modelos y referencias en [Temas](docs/contexto/2026-10-29_093018_temas.md).
- Nombrar documentos `AAAA-MM-DD_HHMMSS_tema.md` con hora de Santiago. Mantener
  el nombre al editar; fechar nuevas entradas dentro del documento.
  En `spikes/units/`, conservar los nombres estables `README.md` y `report.md`.
- Empezar con 50–100 tareas piloto del tema seleccionado. Ajustar
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

Informe con el template aportado y comparación de cinco modelos: [fuentes y reproducción](docs/report/README.md). Referencia externa DeepSeek-V4-Pro-0813 vía OpenRouter/DeepInfra FP8: costo reportado USD 0,0935116, bajo el tope autorizado USD 5. No se entrenaron modelos.

Entrega mínima para enviar: [README](deliveries/challenge-clean/challenge/README.md), [PDF](deliveries/challenge-clean/challenge/informe.pdf), [ZIP](deliveries/challenge-clean/challenge.zip). Incluye código, tareas, SFT/DPO e informe, sin corridas experimentales; [comprobación aislada](data/units/validation/self-contained-delivery.json). Los resultados originales y el paquete anterior se conservan en el repositorio.


Revisión anterior de formato (2026-11-08): paquete conservado en `deliveries/challenge/` y su ZIP. Incluye el espaciado corregido del encabezado y tablas; [registro histórico](data/units/validation/report-format.json).

Guía de la entrega vigente: [regenerar tareas, comprobar SFT/DPO y generar respuestas nuevas](deliveries/challenge-clean/challenge/REPRODUCING.md). Todas las rutas de uso parten de la carpeta extraída. README ofrece únicamente un enlace general y opcional al repositorio para solicitar más antecedentes al equipo.

[Guía de revisión por commits para el equipo](docs/contexto/2026-11-08_093607_guia_revision_equipo.md).

Estándar de colaboración: [ramas, Conventional Commits y PR de cuatro partes](CONTRIBUTING.md).

[Índice de toda la documentación](docs/README.md) · [Mapa de datos vigentes e históricos](data/units/README.md#datos-vigentes-e-historial). Ambos enunciados se comparten como referencia; la implementación entregada corresponde al desafío.

Revisión del PR #3 (2026-11-09): [decisión y limitaciones](docs/report/README.md).
Informe vigente de siete páginas tras síntesis editorial; verifier-9, datos y métricas originales conservados.
Sin nuevas inferencias; mejoras del verificador previstas antes de entrenar en el proyecto.

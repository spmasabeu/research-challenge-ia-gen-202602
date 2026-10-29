# Temas por investigar

## Abiertos · 2026-10-29 · Equipo

- Hardware disponible por participante y presupuesto para inferencia externa.
- Reglas concretas de planificación y parámetros de dificultad.
- Formato de respuesta y tratamiento de soluciones equivalentes.
- Interfaz detallada del curso: representación de prompt/completion y herramientas.
- Elección definitiva de modelos, revisiones, licencias y modo de razonamiento.
- Protocolo pass@k: k, muestras, muestreo e incertidumbre de las métricas.
- Tamaño de splits, diversidad y separación por estructura de las tareas.
- Almacenamiento compartido de datos y trazas; control de versiones y checksums.

## Referencias iniciales

- Enunciado: `../DesafioInvestigacion-2026.pdf`.
- Qwen3-1.7B: https://huggingface.co/Qwen/Qwen3-1.7B
- Qwen2.5-1.5B-Instruct: https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct
- Qwen3-8B: https://huggingface.co/Qwen/Qwen3-8B
- Qwen3-32B: https://huggingface.co/Qwen/Qwen3-32B
- DeepSeek-V3.2: https://huggingface.co/deepseek-ai/DeepSeek-V3.2

Para nuevos hallazgos: fecha, autor, fuente, observación y efecto sobre el proyecto.

## Pool propuesto y piloto

Candidatos pendientes de validar con recursos y presupuesto del equipo:

| Rol | Modelo |
| --- | --- |
| Objetivo | Qwen/Qwen3-1.7B |
| Alternativa pequeña | Qwen/Qwen2.5-1.5B-Instruct |
| Comparador | Qwen/Qwen3-8B |
| Profesor para trazas | Qwen/Qwen3-32B |
| Referencia externa | deepseek-ai/DeepSeek-V3.2 |

Piloto propuesto: 100 tareas de planificación con recursos, buscando factibilidad,
con dificultad fácil/media/difícil y semilla inicial 42. Fijar revisiones de modelos,
modo de razonamiento, muestreo, presupuestos y k antes de evaluar. Confirmar que
la referencia externa cumple la expectativa de modelo de frontera del curso.

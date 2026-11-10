# Piloto de familias nuevas (2026-11-10)

Primera medición de Qwen3-1.7B sobre el catálogo de seis familias, para ver si
densidad, presión y tensión caen en la zona aprendible. Es un piloto de
desarrollo: sus problemas no pertenecen a ningún dataset congelado y no deben
reutilizarse como test.

- Tareas: `generate --seed 4401 --groups 10` con las seis familias, 180 tareas
  (10 problemas por familia × 3 niveles). Las familias originales sirven de
  control en el mismo hardware; sus problemas difieren de la calibración del desafío.
- Modelo: `qwen3:1.7b`, digest `8f68893c…`, idéntico al del desafío. Tres
  muestras por tarea, semillas 42–44 y las opciones de `models.OPTIONS`, `think=false`.
- Hardware: NVIDIA A30 24 GB (astronodo-gpu01), Ollama 0.18.0, Python 3.12.16.
  El desafío usó una RTX 3050 Laptop; las semillas no garantizan iguales respuestas.
- Evaluación: verifier-10, `scores/v10/`, reproducible offline:

```bash
PYTHONPATH=src python -m challenge.harness score --tasks data/units/pilot-families-v1/tasks.jsonl --run data/units/pilot-families-v1/qwen17 --out /tmp/pilot-families-rescore
```

## Resultados

pass@1 / pass@3 (%), 30 respuestas y 10 tareas por celda.

| Familia | Fácil | Media | Difícil | pass@1 familia | Cobertura |
| --- | --- | --- | --- | --- | --- |
| speed | 96,7 / 100 | 96,7 / 100 | 76,7 / 90 | 90,0 | 97,8 |
| energy | 80,0 / 100 | 63,3 / 80 | 40,0 / 70 | 61,1 | 97,8 |
| luminosity | 33,3 / 80 | 10,0 / 20 | 3,3 / 10 | 15,6 | 90,0 |
| density | 56,7 / 80 | 33,3 / 40 | 33,3 / 70 | 41,1 | 97,8 |
| pressure | 73,3 / 90 | 86,7 / 100 | 63,3 / 80 | 74,4 | 94,4 |
| voltage | 96,7 / 100 | 100 / 100 | 56,7 / 100 | 84,4 | 97,8 |

Total: 330 correctas, 188 errores numéricos y 22 no interpretadas de 540;
pass@1 61,1 %, pass@3 78,3 %, cobertura 95,9 %, cuatro truncamientos; 579 s de inferencia.

## Lectura

- Densidad queda en la zona aprendible en los tres niveles. En difícil, 17 de
  19 errores numéricos son exactamente ×1000: el modelo divide gramos por m³ y
  trata g/m³ como si fueran kg/m³.
- En tensión difícil, 9 de 12 errores son exactamente ÷1000 (mA·kohm = V tratado
  como mV). Fácil y media están en el techo y aportan poca señal para RL.
- Presión media supera a fácil: los niveles describen operaciones previstas,
  no un orden garantizado de dificultad, igual que en el desafío.
- Las familias originales reproducen el patrón de la calibración del desafío
  (velocidad alta, luminosidad baja); con 10 tareas por celda las diferencias
  puntuales no son concluyentes.

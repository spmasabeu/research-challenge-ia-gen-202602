# Pruebas del desafío units

Desde la raíz: `uv run python -m unittest discover -s tests -v`.
Sin modelos, GPU ni red. Fixtures numéricos independientes, referencias recalculadas
desde los prompts, determinismo, exclusión y agrupación de variantes, balance de
estructuras, equivalencias, tolerancia, ataques JSON/texto, recompensa pública,
pass@1/pass@3 conocidos y reanudación con backend simulado.

Comprobaciones estáticas usadas:

```bash
uvx --from ruff==0.17.4 ruff check src/challenge tests scripts docs/report/render.py
uvx --from mypy==2.4.1 mypy --ignore-missing-imports src/challenge tests scripts docs/report/render.py
uvx --from bandit==1.9.4 bandit -r src/challenge scripts docs/report/render.py -ll
```

Bandit se ejecuta con umbral medio/alto; las aserciones de comprobación producen
avisos bajos. La excepción B310 del runner corresponde a su URL local fija.
La suite ordinaria no descarga ni entrena modelos. `test_training.py` comprueba
política E2, congelación 1.800/360/360, aislamiento de particiones, máscaras, bootstrap por problema físico,
recompensas, paridad entre backends, terminación EOS y selección por cómputo.

Total actual: 42 pruebas, incluidos el contraste pareado SFT→GRPO menos GRPO
y el rechazo de reutilización de entrenamientos con datos/adaptador incompatibles.
Ninguna realiza llamadas pagadas.

Integración CUDA separada, con descargas públicas y cómputo local:

```bash
rtk proxy env PYTHONPATH=src uv run --locked --group training python scripts/check_training_gpu.py \
  --prefix gpu-check-new
```

El prefijo debe ser nuevo. Comprueba actualización y recarga, máscara SFT,
reanudación exacta SFT y GRPO con optimizador/RNG y tokens persistentes, variación de recompensa y carga
SFT→GRPO con costo previo. Usa trazas históricas reales únicamente como fixtures
de infraestructura; no son resultados de entrenamiento del dataset E2.
Ejecución aprobada: `data/units/project-e2/validation/gpu-check-v3-gpu.json`.
Dependencias exactas en el grupo `training` y `uv.lock`; pesos fuera de Git.

Con el entorno de entrenamiento ya preparado, ejecutar las pruebas mediante
`PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v` para conservar
los grupos opcionales instalados durante corridas largas.

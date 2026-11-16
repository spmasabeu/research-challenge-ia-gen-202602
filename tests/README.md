# Pruebas del desafío units

Desde la raíz: `uv run python -m unittest discover -s tests -v`.
Sin modelos, GPU ni red. Fixtures numéricos independientes, referencias recalculadas
desde los prompts, determinismo, exclusión y agrupación de variantes, balance de
estructuras, equivalencias, tolerancia, ataques JSON/texto, recompensa pública,
pass@1/pass@3 conocidos y reanudación con backend simulado.

Comprobaciones estáticas usadas:

```bash
uvx --from ruff==0.17.4 ruff check src/challenge tests docs/report/render.py
uvx --from mypy==2.4.1 mypy --ignore-missing-imports src/challenge tests docs/report/render.py
uvx --from bandit==1.9.4 bandit -r src/challenge docs/report/render.py -ll
```

Bandit se ejecuta con umbral medio/alto; las aserciones de comprobación producen
avisos bajos. La excepción B310 del runner corresponde a su URL local fija.
No se entrenan modelos.

Total actual: veintitrés pruebas (once núcleo/SFT/DPO, dos de API externa simulada y diez del
catálogo de familias en `test_families.py`). Ninguna realiza llamadas pagadas.

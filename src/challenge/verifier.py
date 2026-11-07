"""Verificador y recompensa con la interfaz común del curso.

    reward(prompt, completion) -> float

La referencia se recalcula desde el bloque DATOS del prompt (mismos datos que ve
el modelo, sin la respuesta), así que cualquier grupo puede usar el entorno sin
nuestros archivos de tareas.
"""

import json
import math

from challenge.generator import DATA_MARKER
from challenge.parser import extract_answer
from challenge.units import solve

MAX_CHARS = 4000  # respuestas más largas reciben 0: evita premiar divagación en RL
REL_TOL = 0.01  # el prompt pide >= 3 cifras significativas

STATUSES = ("correct", "numeric", "unit", "unparsed", "too_long")


def verify(spec, completion):
    """Clasificar una respuesta.

    - correct: cantidad en la unidad pedida (o un alias suyo), dentro de REL_TOL.
    - numeric: unidad pedida, cantidad incorrecta.
    - unit: cantidad legible en otra unidad (aunque sea equivalente: se exige
      la unidad pedida para que la conversión final cuente).
    - unparsed: ambigua, sin unidad o ilegible. No prueba un error matemático.
    - too_long: supera MAX_CHARS.
    """
    spec = spec.get("spec", spec)
    if len(completion) > MAX_CHARS:
        return "too_long"
    final = extract_answer(completion)
    if final is None:
        return "unparsed"
    value, unit = final
    if unit != spec["requested_unit"]:
        return "unit"
    expected = solve(spec)
    return (
        "correct"
        if math.isclose(value, expected, rel_tol=REL_TOL, abs_tol=0)
        else "numeric"
    )


def spec_from_prompt(prompt):
    head, sep, data = prompt.rpartition(DATA_MARKER)
    if not sep:
        raise ValueError("Prompt sin bloque DATOS")
    return json.loads(data)


def reward(prompt, completion):
    """1.0 si la respuesta final es correcta, 0.0 en cualquier otro caso."""
    try:
        return float(verify(spec_from_prompt(prompt), completion) == "correct")
    except (ValueError, KeyError, TypeError, RecursionError):
        return 0.0

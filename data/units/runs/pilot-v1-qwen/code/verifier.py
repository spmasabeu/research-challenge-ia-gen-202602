"""Extraer sin referencia, comprobar dimensión y comparar en SI."""

import json
import math
import re

VERSION = "verifier-1"
NUMBER = r"[+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+)(?:[eE][+-]?\d+)?"
SCALAR = rf"({NUMBER})(?:\s*[×x*]\s*10\^([+-]?\d+))?"
UNITS = {
    "m/s": ("speed", 1), "km/h": ("speed", 1 / 3.6),
    "J": ("energy", 1), "kJ": ("energy", 1000), "erg": ("energy", 1e-7),
    "W": ("luminosity", 1), "kW": ("luminosity", 1000),
    "erg/s": ("luminosity", 1e-7), "Lsun": ("luminosity", 3.828e26),
}
ALIASES = {"metros por segundo": "m/s", "vatios": "W", "julios": "J", "L☉": "Lsun"}
_TASKS: dict[str, dict] = {}


def number(text):
    match = re.fullmatch(SCALAR, str(text).strip())
    if not match:
        raise ValueError("escalar inválido")
    value = float(match[1].replace(",", ".")) * 10.0 ** int(match[2] or 0)
    if not math.isfinite(value):
        raise ValueError("escalar no finito")
    return value


def unique_object(pairs):
    if len(dict(pairs)) != len(pairs):
        raise ValueError("claves duplicadas")
    return dict(pairs)


def quantity(text):
    """Una sola cantidad; nunca evaluar una expresión producida por el modelo."""
    text = re.sub(r"\^\{([+-]?\d+)\}", r"^\1", text.strip())
    for _ in range(2):
        text = re.sub(r"\\(?:boxed|mathrm|text)\{([^{}]*)\}", r"\1", text)
    text = text.replace(r"\times", "×").replace(r"\,", " ").replace("$", "").strip()
    text = re.sub(r"^(?:(?:v|E|L)\s*[=≈]\s*)", "", text)
    match = re.fullmatch(rf"{SCALAR}\s+([\w/^☉]+(?: por segundo)?)\.?", text)
    if not match:
        return None
    unit = ALIASES.get(match[3], match[3])
    return number(match[1] + ("*10^" + match[2] if match[2] else "")), unit


def extract_answer(completion):
    """Terminal JSON o cantidad; resultados explícitos contradictorios inválidos."""
    if not isinstance(completion, str):
        return None
    text = re.sub(r"```(?:json)?", "", completion, flags=re.IGNORECASE)
    text = text.replace("**", "").replace("`", "").strip()
    candidates = []
    try:
        objects = list(re.finditer(r'\{\s*"', text))
        last_end = -1
        for match in objects:
            obj, length = json.JSONDecoder(object_pairs_hook=unique_object).raw_decode(text[match.start():])
            if set(obj) != {"value", "unit"} or type(obj["value"]) not in (int, float, str) or not isinstance(obj["unit"], str):
                return None
            candidates.append((number(obj["value"]), ALIASES.get(obj["unit"].strip(), obj["unit"].strip())))
            last_end = match.start() + length
        if objects and text[last_end:].strip(" \n\t."):
            return None
        marked = []
        for line in text.splitlines():
            match = re.match(r"^\s*(?:FINAL|Respuesta final|Resultado final)\s*:\s*(.*)$", line, re.IGNORECASE)
            if match and match[1].strip() and not match[1].lstrip().startswith("{"):
                q = quantity(match[1])
                if q is None:
                    return None
                marked.append(q)
        candidates.extend(marked)
        if not objects:
            lines = [line.strip() for line in text.splitlines() if line.strip() and line.strip() not in (r"\[", r"\]", "$$")]
            if not lines:
                return None
            final = re.sub(r"^(?:FINAL|Respuesta final|Resultado final)\s*:\s*", "", lines[-1], flags=re.IGNORECASE)
            q = quantity(final)
            if q is None:
                return None
            if not marked:
                candidates = [q for line in lines if (q := quantity(line)) is not None]
            else:
                candidates.append(q)
        if not candidates:
            return None
        value, unit = candidates[-1]
        dimension, factor = UNITS.get(unit, (unit, 1))
        for other_value, other_unit in candidates:
            other_dimension, other_factor = UNITS.get(other_unit, (other_unit, 1))
            if other_dimension != dimension or not math.isclose(value * factor, other_value * other_factor, rel_tol=1e-10, abs_tol=0):
                return None
        return value, unit
    except (ValueError, TypeError, OverflowError, KeyError):
        return None


def verify(task, completion):
    answer = extract_answer(completion)
    if answer is None:
        return {"status": "unparsed", "reward": 0.0}
    value, unit = answer
    dimension, factor = UNITS.get(unit, (None, 1))
    if dimension != task["family"]:
        return {"status": "unit", "reward": 0.0, "value": value, "unit": unit}
    si = value * factor
    correct = math.isfinite(si) and abs(si - task["answer_si"]) <= .01 * abs(task["answer_si"])
    return {"status": "correct" if correct else "numeric", "reward": float(correct), "value": value, "unit": unit, "value_si": si}


def reference_from_prompt(prompt, family):
    """Comprobador independiente: datos visibles y factores propios, sin answer_si."""
    data = re.search(r"^Datos: (.+)$", prompt, re.MULTILINE)
    if data is None:
        raise ValueError("faltan datos visibles")
    factors = {"m": 1, "km": 1000, "s": 1, "min": 60, "kg": 1, "g": .001,
               "m/s": 1, "km/h": 1 / 3.6, "W/m^2": 1, "erg/s/cm^2": .001}
    values = {}
    for field in data[1].split("; "):
        match = re.fullmatch(rf"([dmvtF][12]?)=({NUMBER}) (\S+)", field)
        if match is None or match[1] in values:
            raise ValueError("dato visible inválido")
        values[match[1]] = number(match[2]) * factors[match[3]]
    if any(not math.isfinite(v) or v <= 0 for v in values.values()):
        raise ValueError("dato fuera de alcance")
    if family == "speed":
        distance = values["d"] if "d" in values else values["d1"] + values["d2"]
        return distance / values["t"]
    if family == "energy":
        mass = values["m"] if "m" in values else values["m1"] + values["m2"]
        return .5 * mass * values["v"] * values["v"]
    if family == "luminosity":
        flux = values["F"] if "F" in values else values["F1"] + values["F2"]
        return (4 * 3.141592653589793) * values["d"] * values["d"] * flux
    raise ValueError("familia desconocida")


def load_tasks(tasks):
    """Registrar referencias privadas comprobadas; prompt exacto como clave."""
    registry = {}
    for task in tasks:
        ref = task["answer_si"]
        if not math.isfinite(ref) or ref <= 0 or not math.isclose(ref, reference_from_prompt(task["prompt"], task["family"]), rel_tol=1e-10):
            raise ValueError("referencia inconsistente")
        if task["prompt"] in registry:
            raise ValueError("prompt duplicado")
        registry[task["prompt"]] = task.copy()
    _TASKS.clear()
    _TASKS.update(registry)


def reward(prompt: str, completion: str) -> float:
    if prompt not in _TASKS:
        raise ValueError("prompt desconocido: cargar tabla privada con load_tasks")
    return verify(_TASKS[prompt], completion)["reward"]

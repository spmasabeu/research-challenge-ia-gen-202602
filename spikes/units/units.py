"""Tareas cuantitativas, extracción y verificación; solo biblioteca estándar."""

import json
import math
import random
import re

# shortcut: catálogo cerrado de unidades para el piloto; ampliar con análisis dimensional en el harness final.
UNITS = {
    "speed": {"m/s": 1, "km/h": 1 / 3.6},
    "energy": {"J": 1, "kJ": 1000, "erg": 1e-7},
    "luminosity": {"W": 1, "kW": 1000, "Lsun": 3.828e26, "erg/s": 1e-7},
}


def tasks():
    """90 tareas: diez instancias por familia, cada una en tres niveles pareados."""
    rng = random.Random(43)
    result = []
    for family in ("speed", "energy", "luminosity"):
        for i in range(10):
            a, b = rng.sample(range(2, 50), 2)
            if family == "speed":
                variants = (
                    (f"Distancia {a * b} m; tiempo {b} s.", "m/s", 0),
                    (
                        f"Distancia {a * b / 1000:g} km; tiempo {b} s. 1 km=1000 m.",
                        "m/s",
                        1,
                    ),
                    (
                        f"Distancia {a * b / 1000:g} km; tiempo {b / 60:.12g} min. 1 km=1000 m; 1 min=60 s; 1 m/s=3.6 km/h.",
                        "km/h",
                        3,
                    ),
                )
                formula, answer = "v=d/t", float(a)
            elif family == "energy":
                variants = (
                    (f"Masa {a} kg; velocidad {b} m/s.", "J", 0),
                    (f"Masa {a * 1000} g; velocidad {b} m/s. 1 kg=1000 g.", "J", 1),
                    (
                        f"Masa {a * 1000} g; velocidad {b * 3.6:.12g} km/h. 1 kg=1000 g; 1 m/s=3.6 km/h; 1 kJ=1000 J.",
                        "kJ",
                        3,
                    ),
                )
                formula, answer = "E=0.5*m*v^2", 0.5 * a * b**2
            else:
                flux = b * 1e-9
                variants = (
                    (f"Distancia {a} m; flujo {flux:.8e} W/m^2.", "W", 0),
                    (
                        f"Distancia {a / 1000:g} km; flujo {flux:.8e} W/m^2. 1 km=1000 m.",
                        "W",
                        1,
                    ),
                    (
                        f"Distancia {a / 1000:g} km; flujo {flux * 1000:.8e} erg/s/cm^2. 1 km=1000 m; 1 W/m^2=1000 erg/s/cm^2; 1 W=1e7 erg/s.",
                        "erg/s",
                        3,
                    ),
                )
                formula, answer = "L=4*pi*d^2*F", 4 * math.pi * a**2 * flux
            for level, (text, unit, conversions) in zip(
                ("easy", "medium", "hard"), variants
            ):
                result.append(
                    {
                        "id": f"{family}-{i:02d}-{level}",
                        "pair_id": f"{family}-{i:02d}",
                        "family": family,
                        "level": level,
                        "conversions": conversions,
                        "prompt": text
                        + f" Calcula {formula} en {unit}. Puedes razonar brevemente. Termina con una única respuesta numérica y su unidad; puedes usar JSON o texto. No entregues alternativas.",
                        "answer_si": answer,
                        "dimension": family,
                        "requested_unit": unit,
                    }
                )
    return result


NUMBER = r"[+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+)(?:[eE][+-]?\d+)?"
SCALAR = rf"({NUMBER})(?:\s*(?:\*|×|x)\s*10\s*\^\s*([+-]?\d+))?"
FINAL_MARKER = r"(?:FINAL\s*:|(?:la\s+)?respuesta(?:\s+final)?\s*(?:es\s*:?|:))"


def number(text):
    """Leer notación decimal/científica sin ejecutar expresiones del modelo."""
    match = re.fullmatch(SCALAR, text.strip())
    if not match:
        raise ValueError("Número no interpretable")
    value = float(match[1].replace(",", "."))
    return value * 10.0 ** int(match[2] or 0)


def unique_object(pairs):
    if len(dict(pairs)) != len(pairs):
        raise ValueError("Claves JSON duplicadas")
    return dict(pairs)


def extract_answer(completion):
    """Extraer una respuesta terminal sin consultar el valor de referencia."""
    text = completion.strip()
    text = re.sub(r"```(?:json)?\s*", "", text, flags=re.IGNORECASE).strip()
    text = text.replace("**", "").replace("__", "").replace("`", "")
    if (
        len(
            re.findall(r"^\s*" + FINAL_MARKER, text, flags=re.IGNORECASE | re.MULTILINE)
        )
        > 1
    ):
        return None
    objects = list(re.finditer(r'\{(?=\s*")', text))
    try:
        if objects:
            if len(objects) != 1:
                return None
            start = objects[0].start()
            prefix = text[:start].split("\n")[-1].strip()
            # Desarrollo y JSON pueden compartir línea, separados por punto.
            if (
                prefix
                and not re.fullmatch(FINAL_MARKER, prefix, re.IGNORECASE)
                and (
                    not prefix.endswith(".")
                    or re.search(r"\b(?:o|alternativa)\b", prefix)
                )
            ):
                return None
            final, end = json.JSONDecoder(object_pairs_hook=unique_object).raw_decode(
                text[start:]
            )
            suffix = text[start + end :].strip()
            if isinstance(final, dict) and len(final) == 1 and not suffix:
                key = next(iter(final))
                if key in {"value", "valor", "v", "E", "L"} and isinstance(
                    final[key], str
                ):
                    return extract_answer(final[key])
            if not isinstance(final, dict) or len(final) != 2:
                return None
            value_keys = set(final) & {"value", "valor", "v", "E", "L"}
            unit_keys = set(final) & {"unit", "unidad"}
            if len(value_keys) != 1 or len(unit_keys) != 1:
                return None
            value, unit = final[value_keys.pop()], final[unit_keys.pop()]
            if isinstance(value, str):
                value = number(value)
            if type(value) not in (int, float) or not isinstance(unit, str):
                return None
            if suffix:
                # Aceptar solo reiteración explícita e idéntica de la cantidad final.
                repeated = re.sub(
                    r"^Respuesta numérica(?: y unidad)?:\s*",
                    "",
                    suffix,
                    flags=re.IGNORECASE,
                )
                if repeated == suffix or extract_answer(repeated) != (
                    value,
                    unit.replace("²", "^2"),
                ):
                    return None
        else:
            # shortcut: texto libre limitado a cantidad y unidad terminales; ampliar con casos auditados.
            quantity_lines = re.findall(
                rf"^(?:{FINAL_MARKER}\s*)?{SCALAR}\s+[\w/^²]+\.?$",
                text,
                re.MULTILINE | re.IGNORECASE,
            )
            if len(quantity_lines) > 1:
                return None
            lines = [
                line.strip()
                for line in text.splitlines()
                if line.strip() not in ("$$", r"\[", r"\]")
            ]
            line = lines[-1] if lines else ""
            if (
                re.fullmatch(r"Unidad:\s*[\w/^²]+", line, re.IGNORECASE)
                and len(lines) >= 2
            ):
                line = lines[-2] + "; " + line
            line = re.sub(r"\^\{([+-]?\d+)\}", r"^\1", line)
            for _ in range(2):
                line = re.sub(r"\\(?:boxed|text|mathrm)\s*\{([^{}]*)\}", r"\1", line)
            line = line.replace(r"\times", "×").replace(r"\approx", "≈")
            line = (
                line.replace("$", "")
                .replace("`", "")
                .replace(r"\,", " ")
                .replace("\\ ", " ")
                .strip()
            )
            line = re.sub(
                r"^Respuesta numérica:\s*(.*?)\s*;\s*unidad:\s*",
                r"\1 ",
                line,
                flags=re.IGNORECASE,
            )
            line = re.sub(
                r"^Por lo tanto, .*?aproximadamente\s+", "", line, flags=re.IGNORECASE
            )
            line = re.sub(FINAL_MARKER, "", line, flags=re.IGNORECASE).strip()
            line = re.sub(r"^Respuesta numérica:\s*", "", line, flags=re.IGNORECASE)
            if re.match(r"^[tm]\s*=", line):
                return (
                    None  # Tiempo y masa solo son entradas en las tareas de este spike.
                )
            line = re.split(r"=|≈", line)[-1].strip().rstrip(".").strip()
            for name, symbol in (
                ("metros por segundo", "m/s"),
                ("kilómetros por hora", "km/h"),
                ("kilojulios", "kJ"),
                ("julios", "J"),
                ("joules", "J"),
                ("vatios", "W"),
                ("watts", "W"),
            ):
                line = re.sub(r"\b" + name + r"\b", symbol, line, flags=re.IGNORECASE)
            match = re.fullmatch(
                rf"[^\d{{}}=≈]*?(?>{SCALAR})\s*([A-Za-z][\w/^²]*)(?:,\s*unidad:\s*([\w/^²]+))?",
                line,
                re.IGNORECASE,
            )
            if not match:
                return None
            if match[4] and match[4] != match[3]:
                return None
            value = number(match[1] + ("*10^" + match[2] if match[2] else ""))
            unit = match[3]
        unit = unit.replace("²", "^2")
        unit = {"metros/segundo": "m/s", "kms/h": "km/h"}.get(unit, unit)
        if not math.isfinite(value):
            return None
        return value, unit
    except (ValueError, TypeError, OverflowError):
        return None


def verify(task, completion):
    final = extract_answer(completion)
    if final is None:
        return "unparsed"
    value, unit = final
    if unit not in UNITS[task["dimension"]]:
        return "unit"
    return (
        "correct"
        if math.isclose(
            value * UNITS[task["dimension"]][unit],
            task["answer_si"],
            rel_tol=0.01,
            abs_tol=0,
        )
        else "numeric"
    )

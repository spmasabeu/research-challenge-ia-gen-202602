"""Extracción de la respuesta final (cantidad, unidad) sin consultar la referencia.

Principios:
- Se interpreta solo la respuesta terminal; no se buscan en el desarrollo números
  que coincidan con la referencia ni se ejecutan expresiones del modelo.
- Ante ambigüedad (varias respuestas, alternativas, separador de miles) se
  devuelve None: mejor un falso negativo que una recompensa explotable.
"""

import json
import math
import re
import unicodedata

from challenge.units import canonical_unit

NUMBER = r"[+-]?(?:\d+(?:[.,]\d+)?|[.,]\d+)(?:[eE][+-]?\d+)?"
SCALAR = rf"({NUMBER})(?:\s*(?:\*|×|x|·)\s*10\s*\^\s*([+-]?\d+))?"
FINAL_MARKER = r"(?:FINAL\s*:|(?:la\s+)?respuesta(?:\s+final)?\s*(?:es\s*:?|:))"
# El prompt fija punto decimal sin separador de miles, así que "3.380" es 3.38.
# La coma sigue aceptándose como decimal ("22,5"), salvo con exactamente tres
# dígitos ("1,000", "41,879"): ¿miles en inglés o decimal en español? Aceptar
# cualquiera de las dos lecturas sería un hedge x1000, así que es ambiguo.
THOUSANDS = re.compile(r"[+-]?[1-9]\d{0,2},\d{3}")
QUANTITY_LINE = rf"^\s*(?:{FINAL_MARKER}\s*)?{SCALAR}\s*[^\W\d][\w/^²*]*\.?\s*$"
VALUE_KEYS = {"value", "valor", "v", "E", "L"}
UNIT_KEYS = {"unit", "unidad"}
SUPERSCRIPTS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺", "0123456789-+")
HEDGE_WORDS = re.compile(r"\b(?:o|ó|or|y|and|entre|between)\b", re.IGNORECASE)


def number(text):
    """Leer notación decimal/científica; rechazar separadores de miles."""
    match = re.fullmatch(SCALAR, text.strip())
    if not match:
        raise ValueError("Número no interpretable")
    if THOUSANDS.fullmatch(match[1]):
        raise ValueError("Separador de miles ambiguo")
    value = float(match[1].replace(",", "."))
    return value * 10.0 ** int(match[2] or 0)


_ONES = {
    # español
    "cero": 0, "un": 1, "uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4,
    "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
    "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15,
    "dieciseis": 16, "diecisiete": 17, "dieciocho": 18, "diecinueve": 19,
    "veinte": 20, "veintiun": 21, "veintiuno": 21, "veintiuna": 21,
    "veintidos": 22, "veintitres": 23, "veinticuatro": 24, "veinticinco": 25,
    "veintiseis": 26, "veintisiete": 27, "veintiocho": 28, "veintinueve": 29,
    "treinta": 30, "cuarenta": 40, "cincuenta": 50, "sesenta": 60,
    "setenta": 70, "ochenta": 80, "noventa": 90, "cien": 100, "ciento": 100,
    "doscientos": 200, "doscientas": 200, "trescientos": 300,
    "trescientas": 300, "cuatrocientos": 400, "cuatrocientas": 400,
    "quinientos": 500, "quinientas": 500, "seiscientos": 600,
    "seiscientas": 600, "setecientos": 700, "setecientas": 700,
    "ochocientos": 800, "ochocientas": 800, "novecientos": 900,
    "novecientas": 900,
    # inglés
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90,
}  # fmt: skip


def words_to_number(words):
    """Entero escrito en palabras (español o inglés, < 1 000 000), o None."""
    text = unicodedata.normalize("NFKD", " ".join(words).lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    tokens = text.replace("-", " ").split()
    if not tokens or tokens[0] in {"y", "and"} or tokens[-1] in {"y", "and"}:
        return None
    total = current = 0
    seen_number = False
    for token in tokens:
        if token in {"y", "and"}:
            continue
        if token in _ONES:
            current += _ONES[token]
        elif token == "hundred":
            current = (current or 1) * 100
        elif token in {"mil", "thousand"}:
            total += (current or 1) * 1000
            current = 0
        else:
            return None
        seen_number = True
    return total + current if seen_number else None


def unique_object(pairs):
    if len(dict(pairs)) != len(pairs):
        raise ValueError("Claves JSON duplicadas")
    return dict(pairs)


def _clean_unit(unit):
    """Unidad canónica o la cadena original; None si esconde otra cantidad."""
    unit = unit.strip().rstrip(".").strip()
    if not unit or HEDGE_WORDS.search(unit) or re.search(r"(?<![\^\-\d])\d", unit):
        return None
    return canonical_unit(unit) or unit


def _words_answer(line):
    """'cuarenta m/s', 'la rapidez es de cuarenta metros por segundo'."""
    tokens = line.split()
    for i in range(len(tokens)):
        for j in range(len(tokens), i, -1):
            value = words_to_number(tokens[i:j])
            if value is None:
                continue
            unit = " ".join(tokens[j:])
            canonical = canonical_unit(unit) if unit else None
            if canonical:
                return float(value), canonical
            break
    return None


def _json_answer(text, start):
    before = text[:start]
    # Una cantidad final declarada antes del JSON es una segunda respuesta.
    if re.search(rf"{FINAL_MARKER}\s*{SCALAR}", before, re.IGNORECASE) or re.search(
        QUANTITY_LINE, before, re.MULTILINE | re.IGNORECASE
    ):
        return None
    prefix = before.split("\n")[-1].strip()
    # Desarrollo y JSON pueden compartir línea, separados por punto.
    if (
        prefix
        and not re.fullmatch(FINAL_MARKER, prefix, re.IGNORECASE)
        and (not prefix.endswith(".") or HEDGE_WORDS.search(prefix))
    ):
        return None
    final, end = json.JSONDecoder(object_pairs_hook=unique_object).raw_decode(
        text[start:]
    )
    suffix = text[start + end :].strip()
    if isinstance(final, dict) and len(final) == 1 and not suffix:
        key = next(iter(final))
        if key in VALUE_KEYS and isinstance(final[key], str):
            return extract_answer(final[key])
    if not isinstance(final, dict) or len(final) != 2:
        return None
    value_keys = set(final) & VALUE_KEYS
    unit_keys = set(final) & UNIT_KEYS
    if len(value_keys) != 1 or len(unit_keys) != 1:
        return None
    value, unit = final[value_keys.pop()], final[unit_keys.pop()]
    if isinstance(value, str):
        value = number(value)
    if type(value) not in (int, float) or not isinstance(unit, str):
        return None
    unit = _clean_unit(unit)
    if unit is None:
        return None
    if suffix:
        # Aceptar solo reiteración explícita e idéntica de la cantidad final.
        repeated = re.sub(
            r"^Respuesta numérica(?: y unidad)?:\s*", "", suffix, flags=re.IGNORECASE
        )
        if repeated == suffix or extract_answer(repeated) != (float(value), unit):
            return None
    return float(value), unit


def _text_answer(text):
    if len(re.findall(QUANTITY_LINE, text, re.MULTILINE | re.IGNORECASE)) > 1:
        return None
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip() not in ("", "$$", r"\[", r"\]")
    ]
    line = lines[-1] if lines else ""
    used = 1
    if re.fullmatch(r"Unidad:\s*\S.*", line, re.IGNORECASE) and len(lines) >= 2:
        line = lines[-2] + "; " + line
        used = 2
    # Una línea "FINAL: <cantidad>" anterior a la usada sería otra respuesta.
    for earlier in lines[:-used]:
        if re.match(rf"{FINAL_MARKER}.*\d", earlier, re.IGNORECASE):
            return None
    line = re.sub(r"\^\{([+-]?\d+)\}", r"^\1", line)
    line = re.sub(
        r"10([⁻⁺]?[⁰¹²³⁴⁵⁶⁷⁸⁹]+)", lambda m: "10^" + m[1].translate(SUPERSCRIPTS), line
    )
    for _ in range(2):
        line = re.sub(r"\\(?:boxed|text|mathrm)\s*\{([^{}]*)\}", r"\1", line)
    line = (
        line.replace(r"\times", "×")
        .replace(r"\cdot", "·")
        .replace(r"\approx", "≈")
        .replace("$", "")
        .replace(r"\,", " ")
        .replace("\\ ", " ")
        .strip()
    )
    line = re.sub(
        r"^Respuesta numérica:\s*(.*?)\s*;\s*unidad:\s*(.*)$",
        r"\1, unidad: \2",
        line,
        flags=re.IGNORECASE,
    )
    line = re.sub(r"^Por lo tanto, .*?aproximadamente\s+", "", line, flags=re.I)
    line = re.sub(FINAL_MARKER, "", line, flags=re.IGNORECASE).strip()
    line = re.sub(r"^Respuesta numérica:\s*", "", line, flags=re.IGNORECASE)
    line = re.split(r"=|≈", line)[-1].strip().rstrip(".").strip()
    if not re.search(r"\d", line):
        return _words_answer(line)
    match = re.fullmatch(
        rf"[^\d{{}}=≈]*?(?>{SCALAR})(?:\s*([^\d\s,;].*?))?(?:\s*[,;]\s*unidad:\s*(.+))?",
        line,
        re.IGNORECASE,
    )
    if not match or not (match[3] or match[4]):
        return None
    units = {_clean_unit(u) for u in (match[3], match[4]) if u}
    if len(units) != 1 or None in units:
        return None
    unit = units.pop()
    return number(match[1] + ("*10^" + match[2] if match[2] else "")), unit


def extract_answer(completion):
    """(valor, unidad) de la respuesta terminal, o None si es ambigua/ilegible.

    La unidad se devuelve canónica si se reconoce (``kph`` → ``km/h``); si no,
    tal cual, para que el verificador la clasifique como unidad incorrecta.
    """
    text = completion.strip()
    if text.startswith("<think>"):
        closed = re.match(r"<think>.*?</think>", text, re.DOTALL)
        if not closed:
            return None
        text = text[closed.end() :].strip()
    text = re.sub(r"```(?:json)?\s*", "", text, flags=re.IGNORECASE).strip()
    text = text.replace("**", "").replace("__", "").replace("`", "")
    marker_lines = re.findall(
        r"^\s*" + FINAL_MARKER, text, flags=re.IGNORECASE | re.MULTILINE
    )
    if len(marker_lines) > 1:
        return None
    try:
        objects = list(re.finditer(r'\{(?=\s*")', text))
        if len(objects) > 1:
            return None
        result = _json_answer(text, objects[0].start()) if objects else _text_answer(text)
    except (ValueError, TypeError, OverflowError, RecursionError):
        return None
    if result is None or not math.isfinite(result[0]):
        return None
    return result

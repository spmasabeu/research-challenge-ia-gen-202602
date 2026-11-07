"""Catálogo de unidades y familias de problemas; solo biblioteca estándar.

Cada unidad canónica tiene un factor a SI. Los alias solo identifican la *misma*
unidad (``kph`` → ``km/h``); nunca convierten entre unidades distintas: el
verificador exige la unidad pedida.
"""

import math
import re
import unicodedata

# Factor de cada unidad canónica a la unidad SI de su dimensión.
UNITS = {
    "length": {"m": 1.0, "km": 1000.0},
    "time": {"s": 1.0, "min": 60.0},
    "mass": {"kg": 1.0, "g": 1e-3},
    "speed": {"m/s": 1.0, "km/h": 1 / 3.6},
    "energy": {"J": 1.0, "kJ": 1000.0, "erg": 1e-7},
    "power": {"W": 1.0, "kW": 1000.0, "erg/s": 1e-7},
    "flux": {"W/m^2": 1.0, "erg/s/cm^2": 1e-3},
}

# Alias por unidad canónica. Se comparan tras `normalize_unit`.
ALIASES = {
    "m/s": [
        "m s^-1",
        "m*s^-1",
        "m/seg",
        "metro por segundo",
        "metros por segundo",
        "metros/segundo",
        "meter per second",
        "meters per second",
        "metre per second",
        "metres per second",
    ],
    "km/h": [
        "km h^-1",
        "km*h^-1",
        "kmh",
        "km/hr",
        "km/hora",
        "kph",
        "kms/h",
        "kilometro por hora",
        "kilometros por hora",
        "kilometer per hour",
        "kilometers per hour",
        "kilometre per hour",
        "kilometres per hour",
    ],
    "J": ["joule", "joules", "julio", "julios"],
    "kJ": ["kilojoule", "kilojoules", "kilojulio", "kilojulios"],
    "erg": ["ergs", "ergio", "ergios"],
    "W": ["watt", "watts", "vatio", "vatios"],
    "kW": ["kilowatt", "kilowatts", "kilovatio", "kilovatios"],
    "erg/s": [
        "erg s^-1",
        "erg*s^-1",
        "ergs/s",
        "erg/seg",
        "ergio por segundo",
        "ergios por segundo",
        "ergs per second",
        "erg per second",
    ],
}


def normalize_unit(text):
    """Forma comparable: minúsculas, sin tildes ni adornos tipográficos."""
    # Superíndices antes de NFKD, que los convertiría en dígitos sueltos.
    text = text.replace("⁻¹", "^-1").replace("⁻", "^-").replace("²", "^2")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.replace("·", "*").replace("⋅", "*").replace("\\cdot", "*")
    text = re.sub(r"\^\{([^{}]*)\}", r"^\1", text)
    text = re.sub(r"\s*([*/^])\s*", r"\1", text)
    return re.sub(r"\s+", " ", text).strip().rstrip(".").strip().lower()


# Todas las unidades canónicas son distinguibles sin mayúsculas (no hay m/M).
_LOOKUP = {}
for _units in UNITS.values():
    for _unit in _units:
        _LOOKUP[normalize_unit(_unit)] = _unit
for _unit, _aliases in ALIASES.items():
    for _alias in _aliases:
        _LOOKUP[normalize_unit(_alias)] = _unit


def canonical_unit(text):
    """Unidad canónica de un texto, o None si no se reconoce."""
    return _LOOKUP.get(normalize_unit(text))


# Familias: fórmula con variables en SI. `inputs` asigna dimensión a cada
# variable; `compute` recibe valores SI y devuelve la respuesta SI.
FAMILIES = {
    "speed": {
        "formula": "v = d/t",
        "quantity": "la rapidez media v",
        "inputs": {"d": ("distancia", "length"), "t": ("tiempo", "time")},
        "output": "speed",
        "compute": lambda d, t: d / t,
    },
    "energy": {
        "formula": "E = 0.5*m*v^2",
        "quantity": "la energía cinética E",
        "inputs": {"m": ("masa", "mass"), "v": ("velocidad", "speed")},
        "output": "energy",
        "compute": lambda m, v: 0.5 * m * v**2,
    },
    "luminosity": {
        "formula": "L = 4*pi*d^2*F",
        "quantity": "la luminosidad L",
        "inputs": {"d": ("distancia", "length"), "F": ("flujo", "flux")},
        "output": "power",
        "compute": lambda d, F: 4 * math.pi * d**2 * F,
    },
}


def dimension_of(unit):
    for dimension, units in UNITS.items():
        if unit in units:
            return dimension
    raise KeyError(unit)


def to_si(value, unit):
    return value * UNITS[dimension_of(unit)][unit]


def from_si(value, unit):
    return value / UNITS[dimension_of(unit)][unit]


def solve(spec):
    """Respuesta de referencia en la unidad pedida, calculada desde los datos."""
    family = FAMILIES[spec["family"]]
    given = spec["given"]
    if set(given) != set(family["inputs"]):
        raise ValueError("Datos incompletos para la familia")
    values = {}
    for name, (_, dimension) in family["inputs"].items():
        value, unit = given[name]
        if dimension_of(unit) != dimension:
            raise ValueError(f"Unidad {unit} no corresponde a {dimension}")
        values[name] = to_si(float(value), unit)
    requested = spec["requested_unit"]
    if dimension_of(requested) != family["output"]:
        raise ValueError("Unidad pedida de otra dimensión")
    return from_si(family["compute"](**values), requested)

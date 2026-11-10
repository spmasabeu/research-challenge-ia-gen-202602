"""Problemas físicos positivos con tres representaciones de unidades.

Cada familia es una fila de `CATALOG`: dos magnitudes muestreadas, una fórmula,
unidades por nivel y unidad pedida. Las familias originales conservan el orden
de muestreo y producen exactamente las tareas del dataset congelado `units-3`.
"""

import hashlib
import json
import math
import random
from dataclasses import dataclass
from typing import Callable

VERSION = "units-3"
LEVELS = ("easy", "medium", "hard")


@dataclass(frozen=True)
class Family:
    """Plantilla de una familia: magnitudes `a` y `b`, fórmula y representaciones."""

    names: tuple[str, str]
    # (mínimo, máximo, escala): valor = randint(mínimo, máximo) / escala; escala 1 conserva enteros.
    ranges: tuple[tuple[int, int, int], tuple[int, int, int]]
    split: int  # magnitud que la estructura "sum" reparte en dos componentes
    formulas: tuple[str, str]  # directa, suma
    answer: Callable[[float, float], float]  # resultado SI desde a y b
    units: tuple[dict, dict, dict]  # por nivel: letra -> (unidad, factor desde SI)
    output: tuple[str, str, str]  # unidad pedida por nivel
    equivalences: str
    operations: int  # operaciones de la estructura directa; la suma agrega una
    conversions: tuple[int, int, int]
    context: str


CATALOG = {
    "speed": Family(
        names=("d", "t"), ranges=((101, 9999, 1), (7, 199, 1)), split=0,
        formulas=("v=d/t", "v=(d1+d2)/t"), answer=lambda a, b: a / b,
        units=({"d": ("m", 1), "t": ("s", 1)}, {"d": ("km", .001), "t": ("s", 1)}, {"d": ("km", .001), "t": ("min", 1 / 60)}),
        output=("m/s", "m/s", "km/h"),
        equivalences="1 km=1000 m; 1 min=60 s; 1 m/s=3.6 km/h.",
        operations=1, conversions=(0, 1, 3),
        context="Calcula la velocidad media del recorrido con el tiempo total dado."),
    "energy": Family(
        names=("m", "v"), ranges=((11, 499, 10), (11, 499, 10)), split=0,
        formulas=("E=m*v^2/2", "E=(m1+m2)*v^2/2"), answer=lambda a, b: a * b**2 / 2,
        units=({"m": ("kg", 1), "v": ("m/s", 1)}, {"m": ("g", 1000), "v": ("m/s", 1)}, {"m": ("g", 1000), "v": ("km/h", 3.6)}),
        output=("J", "J", "kJ"),
        equivalences="1 kg=1000 g; 1 m/s=3.6 km/h; 1 kJ=1000 J.",
        operations=3, conversions=(0, 1, 3),
        context="Calcula la energía cinética total; las masas indicadas tienen la misma velocidad."),
    "luminosity": Family(
        # C3: flujos diminutos dejaron las tres celdas luminosas en suelo.
        names=("d", "F"), ranges=((2, 30, 1), (1, 99, 100)), split=1,
        formulas=("L=4*pi*d^2*F", "L=4*pi*d^2*(F1+F2)"), answer=lambda a, b: 4 * math.pi * a**2 * b,
        units=({"d": ("m", 1), "F": ("W/m^2", 1)}, {"d": ("km", .001), "F": ("W/m^2", 1)}, {"d": ("km", .001), "F": ("erg/s/cm^2", 1000)}),
        output=("W", "W", "W"),
        equivalences="1 km=1000 m; 1 W/m^2=1000 erg/s/cm^2; 1 W=1e7 erg/s.",
        operations=4, conversions=(0, 1, 2),
        context="Calcula la luminosidad isotrópica; suma los flujos de las dos bandas si hay F1 y F2."),
    "density": Family(
        names=("m", "V"), ranges=((11, 999, 10), (1, 99, 100)), split=0,
        formulas=("rho=m/V", "rho=(m1+m2)/V"), answer=lambda a, b: a / b,
        units=({"m": ("kg", 1), "V": ("m^3", 1)}, {"m": ("g", 1000), "V": ("m^3", 1)}, {"m": ("g", 1000), "V": ("L", 1000)}),
        output=("kg/m^3", "kg/m^3", "g/cm^3"),
        equivalences="1 kg=1000 g; 1 m^3=1000 L; 1 g/cm^3=1000 kg/m^3.",
        operations=1, conversions=(0, 1, 3),
        context="Calcula la densidad media; si hay m1 y m2, ambas masas ocupan juntas el volumen dado."),
    "pressure": Family(
        names=("F", "A"), ranges=((10, 9999, 1), (1, 99, 100)), split=0,
        formulas=("P=F/A", "P=(F1+F2)/A"), answer=lambda a, b: a / b,
        units=({"F": ("N", 1), "A": ("m^2", 1)}, {"F": ("kN", .001), "A": ("m^2", 1)}, {"F": ("kN", .001), "A": ("cm^2", 10000)}),
        output=("Pa", "Pa", "kPa"),
        equivalences="1 kN=1000 N; 1 m^2=10000 cm^2; 1 kPa=1000 Pa.",
        operations=1, conversions=(0, 1, 3),
        context="Calcula la presión media; si hay F1 y F2, ambas fuerzas actúan perpendiculares sobre la misma área."),
    "voltage": Family(
        names=("I", "R"), ranges=((11, 999, 1000), (10, 999, 1)), split=1,
        formulas=("V=I*R", "V=I*(R1+R2)"), answer=lambda a, b: a * b,
        units=({"I": ("A", 1), "R": ("ohm", 1)}, {"I": ("mA", 1000), "R": ("ohm", 1)}, {"I": ("mA", 1000), "R": ("kohm", .001)}),
        output=("V", "V", "mV"),
        equivalences="1 A=1000 mA; 1 kohm=1000 ohm; 1 V=1000 mV.",
        operations=1, conversions=(0, 1, 3),
        context="Calcula la caída de tensión total; si hay R1 y R2, están en serie y las recorre la misma corriente."),
}
FAMILIES = tuple(CATALOG)
ORIGINAL_FAMILIES = ("speed", "energy", "luminosity")


def physical_key(family, a, b):
    """La estructura y las unidades no alteran identidad física agregada."""
    return f"{family}:{a:.10g}:{b:.10g}"


def draw(rng, low, high, scale):
    value = rng.randint(low, high)
    return value if scale == 1 else value / scale


def generate(seed, groups_per_family, excluded=(), families=ORIGINAL_FAMILIES):
    """Un único generador aleatorio recorre las familias en el orden pedido.

    Con las familias originales primero, sus tareas no cambian al agregar otras.
    """
    if type(groups_per_family) is not int or groups_per_family <= 0:
        raise ValueError("groups_per_family debe ser entero positivo")
    families = tuple(families)
    if not families or len(set(families)) != len(families) or any(f not in CATALOG for f in families):
        raise ValueError(f"familias deben ser distintas y estar en {FAMILIES}")
    rng = random.Random(seed)
    seen = set(excluded)
    tasks = []
    for family in families:
        spec = CATALOG[family]
        for index in range(groups_per_family):
            while True:
                a, b = (draw(rng, *bounds) for bounds in spec.ranges)
                key = physical_key(family, a, b)
                if key not in seen:
                    seen.add(key)
                    break
            structure = "direct" if index % 2 == 0 else "sum"
            fraction = rng.randint(2, 8) / 10
            values = {}
            for position, (name, value) in enumerate(zip(spec.names, (a, b))):
                if structure == "sum" and position == spec.split:
                    values[name + "1"] = value * fraction
                    values[name + "2"] = value * (1 - fraction)
                else:
                    values[name] = value
            formula = spec.formulas[structure == "sum"]
            answer = spec.answer(a, b)
            operations = spec.operations + (structure == "sum")
            pair_id = hashlib.sha256(key.encode()).hexdigest()[:20]
            for level, catalog, requested, conversions in zip(LEVELS, spec.units, spec.output, spec.conversions):
                fields = []
                for name, value in values.items():
                    unit, factor = catalog[name[0]]
                    fields.append(f"{name}={value * factor:.15g} {unit}")
                prompt = (
                    f"{spec.context}\nDatos: {'; '.join(fields)}\nFórmula: {formula}. Usa pi=3.141592653589793.\n"
                    f"Equivalencias: {spec.equivalences}\nExpresa el resultado en {requested}. "
                    'Explica en español los pasos en hasta 80 palabras. Termina con un único resultado, '
                    'en JSON {"value": numero, "unit": "unidad"} o cantidad y unidad. No des alternativas.'
                )
                tasks.append({"id": f"{pair_id}-{level}", "pair_id": pair_id, "physical_key": key,
                              "version": VERSION, "seed": seed, "family": family, "level": level,
                              "structure": structure, "operations": operations,
                              "conversions": conversions,
                              "representation": "scientific" if any("e" in field.split()[0].lower() for field in fields) else "decimal",
                              "prompt": prompt, "answer_si": answer, "requested_unit": requested})
    return tasks


def split_groups(tasks, train, evaluation, test, seed=4302):
    """Balancear estructura y conservar tríos; cantidades de grupos por familia."""
    if any(type(n) is not int or n <= 0 or n % 2 for n in (train, evaluation, test)):
        raise ValueError("cantidades deben ser positivas y pares para balancear estructuras")
    rng = random.Random(seed)
    result = {name: [] for name in ("train", "eval", "test")}
    for family in dict.fromkeys(t["family"] for t in tasks):
        for structure in ("direct", "sum"):
            groups = sorted({t["pair_id"] for t in tasks if t["family"] == family and t["structure"] == structure})
            if len(groups) != (train + evaluation + test) // 2:
                raise ValueError("número de grupos inconsistente")
            rng.shuffle(groups)
            offset = 0
            for name, count in zip(result, (train, evaluation, test)):
                selected = set(groups[offset:offset + count // 2])
                result[name].extend(t for t in tasks if t["pair_id"] in selected)
                offset += count // 2
    return result


def dump(path, rows):
    """Creación exclusiva: los artefactos anteriores nunca se reemplazan."""
    with path.open("x", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")

"""Problemas físicos positivos con tres representaciones de unidades."""

import hashlib
import json
import math
import random

VERSION = "units-3"
FAMILIES = ("speed", "energy", "luminosity")
LEVELS = ("easy", "medium", "hard")


def physical_key(family, a, b):
    """La estructura y las unidades no alteran identidad física agregada."""
    return f"{family}:{a:.10g}:{b:.10g}"


def generate(seed, groups_per_family, excluded=()):
    if type(groups_per_family) is not int or groups_per_family <= 0:
        raise ValueError("groups_per_family debe ser entero positivo")
    rng = random.Random(seed)
    seen = set(excluded)
    tasks = []
    for family in FAMILIES:
        for index in range(groups_per_family):
            while True:
                if family == "speed":
                    a, b = rng.randint(101, 9999), rng.randint(7, 199)
                elif family == "energy":
                    a, b = rng.randint(11, 499) / 10, rng.randint(11, 499) / 10
                else:
                    # C3: flujos diminutos dejaron las tres celdas luminosas en suelo.
                    a, b = rng.randint(2, 30), rng.randint(1, 99) / 100
                key = physical_key(family, a, b)
                if key not in seen:
                    seen.add(key)
                    break
            structure = "direct" if index % 2 == 0 else "sum"
            fraction = rng.randint(2, 8) / 10
            if family == "speed":
                values = {"d": a, "t": b}
                if structure == "sum":
                    values = {"d1": a * fraction, "d2": a * (1 - fraction), "t": b}
                formula = "v=d/t" if structure == "direct" else "v=(d1+d2)/t"
                answer = a / b
                units = ({"d": ("m", 1), "t": ("s", 1)}, {"d": ("km", .001), "t": ("s", 1)}, {"d": ("km", .001), "t": ("min", 1 / 60)})
                output = ("m/s", "m/s", "km/h")
                equivalences = "1 km=1000 m; 1 min=60 s; 1 m/s=3.6 km/h."
                operations = 1 + (structure == "sum")
                context = "Calcula la velocidad media del recorrido con el tiempo total dado."
            elif family == "energy":
                values = {"m": a, "v": b}
                if structure == "sum":
                    values = {"m1": a * fraction, "m2": a * (1 - fraction), "v": b}
                formula = "E=m*v^2/2" if structure == "direct" else "E=(m1+m2)*v^2/2"
                answer = a * b**2 / 2
                units = ({"m": ("kg", 1), "v": ("m/s", 1)}, {"m": ("g", 1000), "v": ("m/s", 1)}, {"m": ("g", 1000), "v": ("km/h", 3.6)})
                output = ("J", "J", "kJ")
                equivalences = "1 kg=1000 g; 1 m/s=3.6 km/h; 1 kJ=1000 J."
                operations = 3 + (structure == "sum")
                context = "Calcula la energía cinética total; las masas indicadas tienen la misma velocidad."
            else:
                values = {"d": a, "F": b}
                if structure == "sum":
                    values = {"d": a, "F1": b * fraction, "F2": b * (1 - fraction)}
                formula = "L=4*pi*d^2*F" if structure == "direct" else "L=4*pi*d^2*(F1+F2)"
                answer = 4 * math.pi * a**2 * b
                units = ({"d": ("m", 1), "F": ("W/m^2", 1)}, {"d": ("km", .001), "F": ("W/m^2", 1)}, {"d": ("km", .001), "F": ("erg/s/cm^2", 1000)})
                output = ("W", "W", "W")
                equivalences = "1 km=1000 m; 1 W/m^2=1000 erg/s/cm^2; 1 W=1e7 erg/s."
                operations = 4 + (structure == "sum")
                context = "Calcula la luminosidad isotrópica; suma los flujos de las dos bandas si hay F1 y F2."
            pair_id = hashlib.sha256(key.encode()).hexdigest()[:20]
            for level, catalog, requested in zip(LEVELS, units, output):
                fields = []
                for name, value in values.items():
                    unit, factor = catalog[name[0]]
                    fields.append(f"{name}={value * factor:.15g} {unit}")
                prompt = (
                    f"{context}\nDatos: {'; '.join(fields)}\nFórmula: {formula}. Usa pi=3.141592653589793.\n"
                    f"Equivalencias: {equivalences}\nExpresa el resultado en {requested}. "
                    'Explica en español los pasos en hasta 80 palabras. Termina con un único resultado, '
                    'en JSON {"value": numero, "unit": "unidad"} o cantidad y unidad. No des alternativas.'
                )
                tasks.append({"id": f"{pair_id}-{level}", "pair_id": pair_id, "physical_key": key,
                              "version": VERSION, "seed": seed, "family": family, "level": level,
                              "structure": structure, "operations": operations,
                              "conversions": {"easy": 0, "medium": 1, "hard": 2 if family == "luminosity" else 3}[level],
                              "representation": "scientific" if any("e" in field.split()[0].lower() for field in fields) else "decimal",
                              "prompt": prompt, "answer_si": answer, "requested_unit": requested})
    return tasks


def split_groups(tasks, train, evaluation, test, seed=4302):
    """Balancear estructura y conservar tríos; cantidades de grupos por familia."""
    if any(type(n) is not int or n <= 0 or n % 2 for n in (train, evaluation, test)):
        raise ValueError("cantidades deben ser positivas y pares para balancear estructuras")
    rng = random.Random(seed)
    result = {name: [] for name in ("train", "eval", "test")}
    for family in FAMILIES:
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

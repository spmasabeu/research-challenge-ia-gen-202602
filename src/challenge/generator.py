"""Generación de tareas con particiones sin fuga.

Cada *instancia física* (familia + parámetros base) se asigna a un split por un
hash de su contenido, independiente de la semilla: ninguna instancia de test
puede aparecer en train/eval aunque se regeneren con otra semilla. Los tres
niveles de una instancia comparten respuesta física y siempre quedan juntos.

Uso:
    PYTHONPATH=src python -m challenge.generator --out data/units-v1
"""

import argparse
import hashlib
import json
import random
from pathlib import Path

from challenge.units import FAMILIES, solve

VERSION = "units-v1"
LEVELS = ("easy", "medium", "hard")
# Buckets de hash (0-9) por split: 70% / 20% / 10% del espacio de instancias.
SPLIT_BUCKETS = {"train": range(0, 7), "eval": range(7, 9), "test": range(9, 10)}
DATA_MARKER = "\nDATOS: "

CONVERSION_FACTS = {
    "km": "1 km = 1000 m",
    "min": "1 min = 60 s",
    "g": "1 kg = 1000 g",
    "km/h": "1 m/s = 3.6 km/h",
    "kJ": "1 kJ = 1000 J",
    "erg": "1 J = 1e7 erg",
    "erg/s": "1 W = 1e7 erg/s",
    "erg/s/cm^2": "1 W/m^2 = 1000 erg/s/cm^2",
}

INSTRUCTIONS = (
    "Puedes razonar brevemente. Termina con una única línea de la forma "
    "`FINAL: <número> <unidad>`. Usa punto decimal, sin separador de miles, y al "
    "menos 3 cifras significativas (se permite notación científica, p. ej. 1.23e-5). "
    "No entregues alternativas."
)


def _clean(x):
    """Evitar artefactos binarios (0.30000000000000004) en los datos del prompt."""
    return float(f"{x:.12g}")


def sample_base(family, rng):
    """Parámetros base enteros; la respuesta física depende solo de ellos."""
    if family == "speed":
        return {"v": rng.randint(2, 49), "t_min": rng.randint(1, 29)}
    if family in ("energy", "luminosity"):
        return {"a": rng.randint(2, 49), "b": rng.randint(2, 49)}
    raise KeyError(family)


def variants(family, base):
    """(given, requested_unit) por nivel. El nivel suma conversiones necesarias."""
    if family == "speed":
        t_s = 60 * base["t_min"]
        d_m = base["v"] * t_s
        return {
            "easy": ({"d": [d_m, "m"], "t": [t_s, "s"]}, "m/s"),
            "medium": ({"d": [d_m / 1000, "km"], "t": [t_s, "s"]}, "m/s"),
            "hard": ({"d": [d_m / 1000, "km"], "t": [base["t_min"], "min"]}, "km/h"),
        }
    if family == "energy":
        m, v = base["a"], base["b"]
        return {
            "easy": ({"m": [m, "kg"], "v": [v, "m/s"]}, "J"),
            "medium": ({"m": [m * 1000, "g"], "v": [v, "m/s"]}, "J"),
            "hard": ({"m": [m * 1000, "g"], "v": [v * 3.6, "km/h"]}, "kJ"),
        }
    if family == "luminosity":
        d, flux = base["a"], base["b"] * 1e-9
        return {
            "easy": ({"d": [d, "m"], "F": [flux, "W/m^2"]}, "W"),
            "medium": ({"d": [d / 1000, "km"], "F": [flux, "W/m^2"]}, "W"),
            "hard": (
                {"d": [d / 1000, "km"], "F": [flux * 1000, "erg/s/cm^2"]},
                "erg/s",
            ),
        }
    raise KeyError(family)


def split_of(family, base):
    key = json.dumps({"family": family, "base": base}, sort_keys=True)
    bucket = int(hashlib.sha256(key.encode()).hexdigest(), 16) % 10
    return next(name for name, buckets in SPLIT_BUCKETS.items() if bucket in buckets)


def render_prompt(spec):
    family = FAMILIES[spec["family"]]
    data = "; ".join(
        f"{family['inputs'][name][0]} {name} = {value:g} {unit}"
        for name, (value, unit) in spec["given"].items()
    )
    units = [unit for _, unit in spec["given"].values()] + [spec["requested_unit"]]
    facts = [CONVERSION_FACTS[u] for u in dict.fromkeys(units) if u in CONVERSION_FACTS]
    lines = [f"Datos: {data}."]
    if facts:
        lines.append("Conversiones: " + "; ".join(facts) + ".")
    lines.append(
        f"Calcula {family['quantity']} con {family['formula']} "
        f"y exprésala en {spec['requested_unit']}."
    )
    lines.append(INSTRUCTIONS)
    # Bloque legible por máquina para `reward(prompt, completion)`; no contiene
    # la respuesta, solo los mismos datos del enunciado.
    return "\n".join(lines) + DATA_MARKER + json.dumps(spec, sort_keys=True)


def make_task(family, base, index, split, level):
    given, requested = variants(family, base)[level]
    given = {name: [_clean(value), unit] for name, (value, unit) in given.items()}
    spec = {"family": family, "given": given, "requested_unit": requested}
    answer = solve(spec)
    instance = f"{family}-{split}-{index:03d}"
    return {
        "id": f"{instance}-{level}",
        "instance_id": instance,
        "version": VERSION,
        "split": split,
        "family": family,
        "level": level,
        "conversions": sum(u not in ("m", "s", "kg", "m/s", "J", "W", "W/m^2")
                           for u in [u for _, u in given.values()] + [requested]),
        "base": base,
        "spec": spec,
        "prompt": render_prompt(spec),
        "requested_unit": requested,
        "answer": answer,
    }


def generate(split, n_per_family, seed=0, families=tuple(FAMILIES)):
    """n_per_family instancias por familia (× 3 niveles) del split pedido."""
    if split not in SPLIT_BUCKETS:
        raise ValueError(f"split desconocido: {split}")
    tasks = []
    for family in families:
        rng = random.Random(f"{VERSION}:{seed}:{family}")
        seen = set()
        attempts = 0
        while len(seen) < n_per_family:
            attempts += 1
            if attempts > 100_000:
                raise ValueError(f"No hay suficientes instancias de {family}/{split}")
            base = sample_base(family, rng)
            key = json.dumps(base, sort_keys=True)
            if key in seen or split_of(family, base) != split:
                continue
            index = len(seen)
            seen.add(key)
            tasks.extend(make_task(family, base, index, split, lvl) for lvl in LEVELS)
    return tasks


def write_dataset(out, sizes, seed=0):
    out.mkdir(parents=True, exist_ok=True)
    manifest = {"version": VERSION, "seed": seed, "splits": {}}
    for split, n in sizes.items():
        tasks = generate(split, n, seed)
        raw = "".join(json.dumps(t, ensure_ascii=False) + "\n" for t in tasks).encode()
        path = out / f"{split}.jsonl"
        if path.exists() and path.read_bytes() != raw:
            raise FileExistsError(f"{path} existe y es distinto; no se sobrescribe")
        path.write_bytes(raw)
        manifest["splits"][split] = {
            "file": path.name,
            "instances_per_family": n,
            "tasks": len(tasks),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=Path("data") / VERSION)
    parser.add_argument("--train", type=int, default=100)
    parser.add_argument("--eval", type=int, default=30)
    parser.add_argument("--test", type=int, default=30)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    sizes = {"train": args.train, "eval": args.eval, "test": args.test}
    print(json.dumps(write_dataset(args.out, sizes, args.seed), indent=2))


if __name__ == "__main__":
    main()

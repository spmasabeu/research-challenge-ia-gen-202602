"""Piloto local de 30 problemas; solo biblioteca estándar y Ollama."""

import argparse
import collections
import datetime
import hashlib
import json
import math
import pathlib
import random
import subprocess
import urllib.request

# shortcut: catálogo cerrado de unidades para el piloto; ampliar con análisis dimensional en el harness final.
UNITS = {
    "speed": {"m/s": 1, "km/h": 1 / 3.6},
    "energy": {"J": 1, "kJ": 1000, "erg": 1e-7},
    "luminosity": {"W": 1, "Lsun": 3.828e26, "erg/s": 1e-7},
    "distance": {"m": 1, "km": 1000},
    "flux": {"W/m^2": 1, "erg/s/cm^2": 1e-3},
}


def tasks():
    rng = random.Random(42)
    result = []
    for level in ("easy", "medium", "hard"):
        for i in range(10):
            a, b, c = (rng.randint(2, 25) for _ in range(3))
            family = i % 3
            if level == "easy":
                if family == 0:
                    text = f"Un móvil recorre {a * b} m en {b} s. Calcula v=d/t en m/s."
                    answer, dimension, unit = a, "speed", "m/s"
                elif family == 1:
                    text = f"Masa {a} kg, velocidad {b} m/s. Calcula E=0.5*m*v^2 en J."
                    answer, dimension, unit = 0.5 * a * b**2, "energy", "J"
                else:
                    flux = a * 1e-9
                    text = f"Distancia {b} m y flujo {flux:.8e} W/m^2. Calcula L=4*pi*d^2*F en W."
                    answer, dimension, unit = (
                        4 * math.pi * b**2 * flux,
                        "luminosity",
                        "W",
                    )
            elif level == "medium":
                if family == 0:
                    text = f"Recorrido {a} km en {b} min. Calcula v=d/t en m/s. 1 km=1000 m; 1 min=60 s."
                    answer, dimension, unit = a * 1000 / (b * 60), "speed", "m/s"
                elif family == 1:
                    text = f"Masa {a * 100} g, velocidad {b * 10} km/h. Calcula E=0.5*m*v^2 en kJ. 1 kg=1000 g; 1 m/s=3.6 km/h; 1 kJ=1000 J."
                    answer, dimension, unit = (
                        0.5 * (a / 10) * (b * 10 / 3.6) ** 2,
                        "energy",
                        "kJ",
                    )
                else:
                    flux = a * 1e-9
                    text = f"Estrella a {b} pc, flujo {flux:.8e} W/m^2. Calcula L=4*pi*d^2*F en Lsun. 1 pc=3.086e16 m; 1 Lsun=3.828e26 W."
                    answer, dimension, unit = (
                        4 * math.pi * (b * 3.086e16) ** 2 * flux,
                        "luminosity",
                        "Lsun",
                    )
            else:
                if family == 0:
                    text = f"Un móvil recorre {a} millas en {b} min y luego {c * 100} m en {a} s, sin pausas. Calcula la rapidez media v=(d1+d2)/(t1+t2) en km/h. 1 milla=1609.344 m; 1 min=60 s; 1 m/s=3.6 km/h."
                    answer, dimension, unit = (
                        (a * 1609.344 + c * 100) / (b * 60 + a),
                        "speed",
                        "km/h",
                    )
                elif family == 1:
                    efficiency = c / 100
                    text = f"Un vehículo de {a} toneladas parte del reposo. Durante {b} min recibe potencia de entrada media P={c} kW con eficiencia eta={efficiency}. Supón que toda la energía útil termina como energía cinética. Calcula la distancia en km suponiendo además aceleración constante durante ese intervalo. Usa E=eta*P*t, E=0.5*m*v_final^2 y d=0.5*v_final*t. 1 tonelada=1000 kg; 1 kW=1000 W; 1 min=60 s; 1 km=1000 m."
                    duration = b * 60
                    velocity = math.sqrt(
                        2 * efficiency * c * 1000 * duration / (a * 1000)
                    )
                    answer, dimension, unit = (
                        0.5 * velocity * duration,
                        "distance",
                        "km",
                    )
                else:
                    mass = a * 1e12
                    text = f"Una fuente convierte {mass:.8e} g de masa íntegramente en radiación durante {b} días. Un observador está a {c} pc. Calcula el flujo medio en erg/s/cm^2. Usa E=dm*c_luz^2, L=E/t, F=L/(4*pi*d^2). c_luz=3e8 m/s; 1000 g=1 kg; 1 día=86400 s; 1 pc=3.086e16 m; 1 W/m^2=1000 erg/s/cm^2."
                    answer = (mass / 1000 * (3e8) ** 2 / (b * 86400)) / (
                        4 * math.pi * (c * 3.086e16) ** 2
                    )
                    dimension, unit = "flux", "erg/s/cm^2"
            prompt = (
                text
                + '\nPuedes razonar brevemente. Termina con una única línea FINAL: {"value": número, "unit": "unidad"}. Usa punto decimal y una unidad de esta lista: '
                + ", ".join(UNITS[dimension])
                + "."
            )
            result.append(
                {
                    "id": f"{level}-{i:02d}",
                    "level": level,
                    "family": family,
                    "prompt": prompt,
                    "answer_si": answer,
                    "dimension": dimension,
                    "requested_unit": unit,
                }
            )
    return result


def verify(task, completion):
    if completion.count("FINAL:") > 1:
        return "format"
    if "FINAL:" in completion:
        final_text = completion.split("FINAL:", 1)[1].strip()
    else:
        # Aceptar también un único objeto JSON en la última línea.
        lines = completion.strip().splitlines()
        if sum(line.lstrip().startswith("{") for line in lines) != 1:
            return "format"
        final_text = lines[-1]
    try:
        final = json.loads(final_text)
        if not isinstance(final, dict) or set(final) != {"value", "unit"}:
            return "format"
        value, unit = final["value"], final["unit"]
        if type(value) not in (int, float) or not math.isfinite(value):
            return "format"
        if not isinstance(unit, str) or unit not in UNITS[task["dimension"]]:
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
    except (ValueError, TypeError, OverflowError):
        return "format"


def api(path, payload=None, timeout=180):
    data = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(
        "http://127.0.0.1:11434/api/" + path,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="qwen3:1.7b")
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    dataset = tasks()
    serialized = "".join(json.dumps(t, ensure_ascii=False) + "\n" for t in dataset)
    (args.output / "tasks.jsonl").write_text(serialized)
    options = {"temperature": 0, "seed": 42, "num_predict": 1024, "num_ctx": 4096}
    metadata = {
        "model": args.model,
        "model_info": api("show", {"model": args.model}),
        "tags": api("tags"),
        "ollama": api("version"),
        "options": options,
        "think": False,
        "utc": datetime.datetime.now(datetime.UTC).isoformat(),
        "git_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        "script_sha256": hashlib.sha256(
            pathlib.Path(__file__).read_bytes()
        ).hexdigest(),
        "dataset_sha256": hashlib.sha256(serialized.encode()).hexdigest(),
        "note": "Piloto sin thinking, una respuesta greedy por problema; no es pass@k ni evaluación final.",
    }
    (args.output / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2)
    )
    counts = {level: collections.Counter() for level in ("easy", "medium", "hard")}
    with (args.output / "responses.jsonl").open("w") as output:
        for task in dataset:
            response = api(
                "chat",
                {
                    "model": args.model,
                    "messages": [{"role": "user", "content": task["prompt"]}],
                    "stream": False,
                    "think": False,
                    "options": options,
                },
            )
            completion = response["message"]["content"]
            status = verify(task, completion)
            row = {"id": task["id"], "status": status, "response": response}
            output.write(json.dumps(row, ensure_ascii=False) + "\n")
            output.flush()
            counts[task["level"]][status] += 1
            print(
                f"{task['id']}: {status} ({response.get('eval_count')} tokens, stop={response.get('done_reason')})",
                flush=True,
            )
    summary = {
        level: {
            "n": sum(count.values()),
            "correct": count["correct"],
            "accuracy": count["correct"] / sum(count.values()),
            "statuses": dict(count),
        }
        for level, count in counts.items()
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

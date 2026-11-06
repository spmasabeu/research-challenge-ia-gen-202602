"""Horarios enteros no interrumpibles; referencias separadas del prompt."""

import json
import random
import re


def parse(completion):
    """Un único JSON terminal, opcionalmente envuelto en Markdown."""
    text = completion.strip()
    blocks = re.findall(r"```([^\n]*)\n([\s\S]*?)```", text)
    candidates = [
        body.strip()
        for language, body in blocks
        if language.strip().lower() in ("", "json") and body.strip().startswith("[")
    ]
    if candidates:
        values = [parse(candidate) for candidate in candidates]
        if any(value != values[0] for value in values):
            raise ValueError("conflicting answers")
        outside = re.sub(r"```[^\n]*\n[\s\S]*?```", "", text)
        if re.search(
            "^\\s*(?:[-*]\\s*)?(?:(?:otra respuesta|alternativa|respuesta(?: final)?|horario(?: final| alternativo)?|plan(?: final| alternativo)?|o)\\s*:?\\s*)?`?\\s*[\\[{]",
            outside,
            re.IGNORECASE | re.MULTILINE,
        ):
            raise ValueError("additional structured output")
        return values[0]
    if text.startswith("```json\n") and text.endswith("```"):
        text = text[8:-3].strip()
    elif text.startswith("```\n") and text.endswith("```"):
        text = text[4:-3].strip()

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate key")
            result[key] = value
        return result

    def invalid(value):
        raise ValueError(value)

    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid)


def verify(task, completion):
    try:
        answer = parse(completion)
    except (ValueError, TypeError, RecursionError):
        return "unparsed"
    if not isinstance(answer, list):
        return "unparsed"
    jobs = {j["id"]: j for j in task["jobs"]}
    assigned = {}
    for item in answer:
        if not isinstance(item, dict) or set(item) != {"id", "start", "resource"}:
            return "unparsed"
        if not isinstance(item["id"], str) or not isinstance(item["resource"], str):
            return "unparsed"
        key = item["id"]
        if key not in jobs or key in assigned:
            return "ids"
        if type(item["start"]) is not int or item["start"] < 0:
            return "time"
        if item["resource"] not in jobs[key]["resources"]:
            return "resource"
        assigned[key] = item
    if set(assigned) != set(jobs):
        return "ids"
    for key, job in jobs.items():
        start = assigned[key]["start"]
        end = start + job["duration"]
        if end > job["deadline"]:
            return "deadline"
        if any(
            assigned[p]["start"] + jobs[p]["duration"] > start
            for p in job["predecessors"]
        ):
            return "precedence"
        for other in jobs:
            if key < other and assigned[key]["resource"] == assigned[other]["resource"]:
                other_start = assigned[other]["start"]
                if start < other_start + jobs[other]["duration"] and other_start < end:
                    return "overlap"
    return "correct"


def tasks(seed=43):
    rng = random.Random(seed)
    result = []
    for level, n, resources, slack in (
        ("easy", 3, 2, 5),
        ("medium", 5, 2, 2),
        ("hard", 7, 3, 0),
    ):
        for index in range(30):
            names = [f"R{i}" for i in range(resources)]
            labels = rng.sample(range(10, 99), n)
            jobs, reference = [], []
            available = dict.fromkeys(names, 0)
            ends = {}
            for i in range(n):
                key = f"T{labels[i]}"
                resource = rng.choice(names)
                duration = rng.randint(1, 5)
                previous = [
                    j["id"]
                    for j in jobs
                    if rng.random() < (0.15 if level == "easy" else 0.4)
                ]
                start = max([available[resource], *[ends[p] for p in previous]])
                end = start + duration
                allowed = [r for r in names if r == resource or rng.random() < 0.35]
                jobs.append(
                    {
                        "id": key,
                        "duration": duration,
                        "resources": allowed,
                        "predecessors": previous,
                        "deadline": end + rng.randint(0, slack),
                    }
                )
                reference.append({"id": key, "start": start, "resource": resource})
                available[resource] = ends[key] = end
            rng.shuffle(jobs)
            prompt = (
                "Construye un horario factible. Tiempos enteros >=0, duración fija, sin interrupciones. "
                "Cada tarea usa un recurso permitido. Una predecesora debe terminar antes o al inicio de su sucesora. "
                "En cada recurso no se solapan intervalos [inicio,inicio+duración); tareas consecutivas sí se permiten. "
                "Toda tarea termina a más tardar en su deadline. Devuelve SOLO un array JSON con exactamente "
                'un objeto {"id":"T...","start":0,"resource":"R..."} por tarea.\nDATOS\n'
                + json.dumps({"jobs": jobs}, ensure_ascii=False)
            )
            result.append(
                {
                    "id": f"{level}-{index:02}",
                    "level": level,
                    "jobs": jobs,
                    "reference": reference,
                    "prompt": prompt,
                }
            )
    return result


def reward(prompt, completion):
    try:
        task = json.loads(re.split(r"\nDATOS\n", prompt)[-1])
        return float(verify(task, completion) == "correct")
    except (ValueError, KeyError, TypeError, RecursionError):
        return 0.0

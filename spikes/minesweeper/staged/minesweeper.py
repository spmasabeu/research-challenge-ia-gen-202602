"""Deducción por configuraciones compatibles, sin conocer el total de minas."""

import functools
import json
import random
import re

CLASSES = ("segura", "mina", "indeterminada")
MAX_STATES = 100_000


def neighbors(row, col, height, width):
    return [
        (r, c)
        for r in range(max(0, row - 1), min(height, row + 2))
        for c in range(max(0, col - 1), min(width, col + 2))
        if (r, c) != (row, col)
    ]


def solve(task):
    visible = {tuple(c[:2]): c[2] for c in task["clues"]}
    if tuple(task["target"]) in visible:
        raise ValueError("target must be hidden")
    return _solve(
        json.dumps(
            {key: task[key] for key in ("height", "width", "clues", "target")},
            sort_keys=True,
        )
    )


@functools.lru_cache(maxsize=4096)
def _solve(serialized):
    task = json.loads(serialized)
    height, width = task["height"], task["width"]
    visible = {tuple(c[:2]): c[2] for c in task["clues"]}
    hidden = [
        (r, c) for r in range(height) for c in range(width) if (r, c) not in visible
    ]
    if len(hidden) > 16:
        raise ValueError("hidden budget")
    constraints = [
        (set(neighbors(r, c, height, width)) - visible.keys(), n)
        for (r, c), n in visible.items()
    ]
    hidden.sort(key=lambda cell: -sum(cell in cells for cells, _ in constraints))
    assignment, possible = {}, set()
    states, count = 0, 0

    def visit(index):
        nonlocal states, count
        states += 1
        if states > MAX_STATES:
            raise TimeoutError("solver state budget")
        for cells, n in constraints:
            current = sum(assignment.get(cell, 0) for cell in cells)
            remaining = sum(cell not in assignment for cell in cells)
            if current > n or current + remaining < n:
                return
        if index == len(hidden):
            count += 1
            possible.add(assignment[tuple(task["target"])])
            return
        cell = hidden[index]
        for value in (0, 1):
            assignment[cell] = value
            visit(index + 1)
        del assignment[cell]

    visit(0)
    if not count:
        raise ValueError("inconsistent clues")
    return {
        "classification": "indeterminada"
        if len(possible) == 2
        else "mina"
        if 1 in possible
        else "segura",
        "configurations": count,
        "states": states,
    }


def extract(task, completion):
    text = completion.strip().lower()
    aliases = {
        "safe": "segura",
        "segura": "segura",
        "mina": "mina",
        "mine": "mina",
        "indeterminada": "indeterminada",
        "undetermined": "indeterminada",
    }
    if text in aliases:
        return aliases[text]
    answer_pattern = r"(?:(?:respuesta|clasificaci[oó]n)(?: final)?\s*:\s*|(?:la casilla|el objetivo|la respuesta)\s+es\s+)?\*{0,2}(segura|safe|mina|mine|indeterminada|undetermined)\*{0,2}[.!]?"
    terminal = re.fullmatch(answer_pattern, text)
    if terminal:
        return aliases[terminal[1]]
    outside_labels = []

    def input_data(body):
        try:
            value = json.loads(body)
        except (ValueError, TypeError, RecursionError):
            return False
        if isinstance(value, dict):
            return set(value) == {"height", "width", "clues", "target"}
        return (
            isinstance(value, list)
            and bool(value)
            and all(
                isinstance(row, list)
                and all(
                    type(cell) is int
                    or (isinstance(cell, str) and (len(cell) == 1 or cell.isdigit()))
                    for cell in row
                )
                for row in value
            )
        )

    all_blocks = re.findall(r"```([^\n]*)\n([\s\S]*?)```", text)
    blocks = [
        body
        for language, body in all_blocks
        if language.strip().lower() in ("", "json") and not input_data(body)
    ]
    if blocks:
        if len({b.strip() for b in blocks}) != 1:
            return None
        outside = re.sub(r"```[^\n]*\n[\s\S]*?```", "", text)
        if re.search(
            "^\\s*(?:[-*]\\s*)?(?:(?:otra respuesta|alternativa|respuesta(?: final)?|horario(?: final| alternativo)?|plan(?: final| alternativo)?|o)\\s*:?\\s*)?`?\\s*[\\[{]",
            outside,
            re.IGNORECASE | re.MULTILINE,
        ):
            return None
        outside_labels = [
            aliases[m[1]]
            for m in re.finditer(
                r"^\s*" + answer_pattern + r"\s*$", outside, re.MULTILINE
            )
        ]
        text = blocks[0].strip()

    def normalized(label):
        canonical = aliases.get(label) if isinstance(label, str) else None
        return (
            canonical if all(other == canonical for other in outside_labels) else None
        )

    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError("duplicate key")
            value[key] = item
        return value

    terminal = re.fullmatch(answer_pattern, text)
    if terminal:
        return normalized(terminal[1])
    try:
        value = json.loads(text, object_pairs_hook=pairs)
    except (ValueError, TypeError, RecursionError):
        return None
    if isinstance(value, str):
        return normalized(value)
    if isinstance(value, dict) and set(value) == {"classification"}:
        label = value["classification"]
        return normalized(label)
    if not isinstance(value, dict) or set(value) != {"row", "col", "classification"}:
        return None
    if (
        type(value["row"]) is not int
        or type(value["col"]) is not int
        or [value["row"], value["col"]] != task["target"]
    ):
        return None
    label = value["classification"]
    return normalized(label)


def verify(task, completion):
    label = extract(task, completion)
    return (
        "unparsed"
        if label is None
        else "correct"
        if label == solve(task)["classification"]
        else "logic"
    )


@functools.lru_cache(maxsize=2)
def _tasks(seed):
    rng, result = random.Random(seed), []
    for level, height, width, visible_count in (
        ("easy", 3, 3, 3),
        ("medium", 3, 4, 4),
        ("hard", 4, 4, 5),
    ):
        counts = dict.fromkeys(CLASSES, 0)
        discarded = {"quota": 0, "direct": 0, "budget": 0, "duplicate": 0}
        seen = set()
        for attempt in range(50_000):
            board = {
                (r, c): rng.random() < 0.3 for r in range(height) for c in range(width)
            }
            safe = [cell for cell, mine in board.items() if not mine]
            if len(safe) < visible_count:
                continue
            visible = rng.sample(safe, visible_count)
            clues = [
                [r, c, sum(board[n] for n in neighbors(r, c, height, width))]
                for r, c in visible
            ]
            target = rng.choice([cell for cell in board if cell not in visible])
            task = {
                "height": height,
                "width": width,
                "clues": clues,
                "target": list(target),
            }
            try:
                solution = solve(task)
            except TimeoutError:
                discarded["budget"] += 1
                continue
            label = solution["classification"]
            direct = any(
                target in neighbors(r, c, height, width)
                and n in (0, len(set(neighbors(r, c, height, width)) - set(visible)))
                for r, c, n in clues
            )
            if level != "easy" and label != "indeterminada" and direct:
                discarded["direct"] += 1
                continue
            if counts[label] == 10:
                discarded["quota"] += 1
                continue
            signature = json.dumps(task, sort_keys=True)
            if signature in seen:
                discarded["duplicate"] += 1
                continue
            seen.add(signature)
            key = f"{level}-{sum(counts.values()):02}"
            counts[label] += 1
            prompt = (
                "Buscaminas deductivo. Coordenadas (fila,columna), base cero. Vecinas: hasta ocho casillas "
                "adyacentes, diagonales incluidas. Cada pista visible es segura y dice cuántas vecinas son minas. "
                "Toda casilla no listada está oculta. NO se conoce el número total de minas. Usa solamente las "
                "pistas visibles. Clasifica objetivo: segura si ninguna configuración compatible tiene mina allí; "
                "mina si todas la tienen; indeterminada si hay configuraciones de ambos tipos. Devuelve SOLO "
                'JSON {"row":0,"col":0,"classification":"segura|mina|indeterminada"} con coordenadas del objetivo, '
                "o únicamente la clasificación.\nDATOS\n" + json.dumps(task)
            )
            result.append(
                {
                    **task,
                    "id": key,
                    "level": level,
                    "reference": label,
                    "solver": solution,
                    "prompt": prompt,
                }
            )
            if sum(counts.values()) == 30:
                for item in result[-30:]:
                    item["generation"] = {
                        "attempts": attempt + 1,
                        "discarded": dict(discarded),
                    }
                break
        else:
            raise RuntimeError("generation quota not reached")
    return json.dumps(result)


def tasks(seed=43):
    return json.loads(_tasks(seed))


def reward(prompt, completion):
    try:
        return float(
            verify(json.loads(prompt.split("\nDATOS\n")[-1]), completion) == "correct"
        )
    except (ValueError, KeyError, TypeError, TimeoutError):
        return 0.0

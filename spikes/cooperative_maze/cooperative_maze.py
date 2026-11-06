"""Planificación secuencial: inventario compartido y puertas persistentes."""

import collections
import functools
import json
import random
import re

MOVES = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
STATE_LIMIT = 100_000


def initial(task):
    names = sorted(task["agents"])
    return tuple(tuple(task["agents"][name]) for name in names), False


def transition(task, state, action):
    if not isinstance(action, dict) or set(action) != {"agent", "move"}:
        return None, "malformed"
    agent, move = action["agent"], action["move"]
    if not isinstance(agent, str) or not isinstance(move, str):
        return None, "malformed"
    names = sorted(task["agents"])
    if agent not in names:
        return None, "unknown_agent"
    if move not in MOVES:
        return None, "malformed"
    positions, key = state
    index = names.index(agent)
    dr, dc = MOVES[move]
    row, col = positions[index][0] + dr, positions[index][1] + dc
    grid = task["grid"]
    if not 0 <= row < len(grid) or not 0 <= col < len(grid[0]):
        return None, "bounds"
    tile = grid[row][col]
    if tile == "#":
        return None, "wall"
    if tile == "D" and not key:
        return None, "locked"
    if (row, col) in positions[:index] + positions[index + 1 :]:
        return None, "collision"
    updated = list(positions)
    updated[index] = (row, col)
    return (tuple(updated), key or tile == "k"), None


def reached(task, state, goal_agents=None):
    names = sorted(task["agents"])
    selected = names if goal_agents is None else goal_agents
    return all(
        state[0][names.index(name)] == tuple(task["goals"][name]) for name in selected
    )


def solve(task, fixed=(), goal_agents=None):
    start = initial(task)
    queue = collections.deque([start])
    previous = {start: None}
    while queue:
        state = queue.popleft()
        if reached(task, state, goal_agents):
            path = []
            while previous[state] is not None:
                state, action = previous[state]
                path.append(action)
            return list(reversed(path)), len(previous)
        for agent in sorted(task["agents"]):
            if agent in fixed:
                continue
            for move in MOVES:
                action = {"agent": agent, "move": move}
                updated, error = transition(task, state, action)
                if error is None and updated not in previous:
                    previous[updated] = (state, action)
                    if len(previous) > STATE_LIMIT:
                        raise TimeoutError("BFS state budget")
                    queue.append(updated)
    return None, len(previous)


def parse(completion):
    text = completion.strip()

    def input_data(body):
        lines = body.strip().splitlines()
        if (
            len(lines) >= 2
            and any(c in body for c in ".#k")
            and all(re.fullmatch(r"[\s0-9\[\].#kDABG|+\-]+", line) for line in lines)
        ):
            return True
        try:
            value = json.loads(body)
        except (ValueError, TypeError, RecursionError):
            return False
        if isinstance(value, dict):
            return set(value) == {"grid", "agents", "goals", "action_budget"}
        return (
            isinstance(value, list)
            and bool(value)
            and all(
                isinstance(row, str) and re.fullmatch(r"[.#kDABG]+", row)
                for row in value
            )
            and any(any(c in row for c in ".#k") for row in value)
        )

    all_blocks = re.findall(r"```([^\n]*)\n([\s\S]*?)```", text)
    blocks = [
        body
        for language, body in all_blocks
        if language.strip().lower() in ("", "json") and not input_data(body)
    ]
    if blocks:
        if len({b.strip() for b in blocks}) != 1:
            raise ValueError("ambiguous actions")
        outside = re.sub(r"```[^\n]*\n[\s\S]*?```", "", text)
        if re.search(
            r"^\s*(?:otra respuesta|alternativa|respuesta(?: final)?|plan(?: final)?|o)\s*:?\s*`?\s*[\[{]",
            outside,
            re.IGNORECASE | re.MULTILINE,
        ):
            raise ValueError("additional answer")
        outside = re.sub(r"`\[\s*\d+\s*,\s*\d+\s*\]`", "COORD", outside)
        if re.search(
            "^\\s*(?:[-*]\\s*)?(?:(?:otra respuesta|alternativa|respuesta(?: final)?|horario(?: final| alternativo)?|plan(?: final| alternativo)?|o)\\s*:?\\s*)?`?\\s*[\\[{]",
            outside,
            re.IGNORECASE | re.MULTILINE,
        ):
            raise ValueError("additional structured output")
        text = blocks[0].strip()

    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError("duplicate key")
            value[key] = item
        return value

    return json.loads(text, object_pairs_hook=pairs)


def details(task, completion):
    try:
        actions = parse(completion)
    except (ValueError, TypeError, RecursionError):
        return {"status": "unparsed", "first_invalid": None, "length": None}
    if not isinstance(actions, list):
        return {"status": "unparsed", "first_invalid": None, "length": None}
    if len(actions) > task["action_budget"]:
        return {"status": "budget", "first_invalid": None, "length": len(actions)}
    state = initial(task)
    for index, action in enumerate(actions):
        state, error = transition(task, state, action)
        if error:
            return {"status": error, "first_invalid": index, "length": len(actions)}
    return {
        "status": "correct" if reached(task, state) else "incomplete",
        "first_invalid": None,
        "length": len(actions),
    }


def verify(task, completion):
    return details(task, completion)["status"]


@functools.lru_cache(maxsize=2)
def _tasks(seed):
    rng, result = random.Random(seed), []
    for level in ("easy", "medium", "hard"):
        discarded = {"impossible": 0, "budget": 0, "length": 0, "cooperation": 0}
        count = 0
        for attempt in range(5000):
            height = rng.choice([4, 5])
            width = 4 if level == "easy" else 5 if level == "medium" else 7
            grid = [["." for _ in range(width)] for _ in range(height)]
            if level == "easy":
                cells = [(r, c) for r in range(height) for c in range(width)]
                start, goal = rng.sample(cells, 2)
                agents, goals = {"A": list(start)}, {"A": list(goal)}
                for cell in cells:
                    if cell not in (start, goal) and rng.random() < 0.22:
                        grid[cell[0]][cell[1]] = "#"
            else:
                barrier = width // 2
                door_row = rng.randrange(height)
                for row in range(height):
                    grid[row][barrier] = "D" if row == door_row else "#"
                left = [(r, c) for r in range(height) for c in range(barrier)]
                right = [
                    (r, c) for r in range(height) for c in range(barrier + 1, width)
                ]
                start, key = rng.sample(left, 2)
                grid[key[0]][key[1]] = "k"
                agents, goals = {"A": list(start)}, {"A": list(rng.choice(right))}
                if level == "hard":
                    agents["B"] = list(rng.choice(right))
                    goals["B"] = list(rng.choice([p for p in left if p != start]))
            task = {
                "grid": ["".join(row) for row in grid],
                "agents": agents,
                "goals": goals,
            }
            try:
                solution, explored = solve(task)
                if level == "hard":
                    independent, _ = solve(task, fixed=("A",), goal_agents=("B",))
                    if independent is not None:
                        discarded["cooperation"] += 1
                        continue
            except TimeoutError:
                discarded["budget"] += 1
                continue
            if solution is None:
                discarded["impossible"] += 1
                continue
            if not 2 <= len(solution) <= 26:
                discarded["length"] += 1
                continue
            task["action_budget"] = min(36, len(solution) + 6)
            prompt = (
                "Planifica un laberinto. Coordenadas [fila,columna] base cero, fila crece hacia abajo. "
                "Grid: # pared, . suelo, k llave, D puerta. Un agente se mueve una casilla por paso: "
                "U arriba, D abajo, L izquierda, R derecha. Solo un agente actúa por paso; no se permite "
                "salir del tablero, atravesar paredes, compartir casilla ni cruzar una puerta sin llave. "
                "Al entrar en k cualquier agente recoge la llave: inventario COMPARTIDO, persistente y "
                "no consumible; todas las D quedan transitables para ambos. Inicialmente sin llave. "
                "Al terminar TODOS los agentes deben estar en sus metas. Cualquier solución dentro del "
                "action_budget sirve, no tiene que ser óptima. Devuelve SOLO array JSON de acciones "
                '[{"agent":"A","move":"R"}].\nDATOS\n' + json.dumps(task)
            )
            result.append(
                {
                    **task,
                    "id": f"{level}-{count:02}",
                    "level": level,
                    "reference": solution,
                    "solver_states": explored,
                    "prompt": prompt,
                }
            )
            count += 1
            if count == 30:
                for item in result[-30:]:
                    item["generation"] = {
                        "attempts": attempt + 1,
                        "discarded": discarded,
                    }
                break
        else:
            raise RuntimeError("generation budget")
    if len({t["prompt"] for t in result}) != 90:
        raise ValueError("duplicate tasks")
    return json.dumps(result)


def tasks(seed=43):
    return json.loads(_tasks(seed))


def reward(prompt, completion):
    try:
        return float(
            verify(json.loads(prompt.split("\nDATOS\n")[-1]), completion) == "correct"
        )
    except (ValueError, KeyError, TypeError, RecursionError):
        return 0.0

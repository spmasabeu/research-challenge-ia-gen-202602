import itertools
import json
import random
import unittest

from minesweeper import reward, solve, tasks, verify


class MinesTests(unittest.TestCase):
    def test_solver_independent_exhaustion(self):
        rng = random.Random(9)
        for _ in range(100):
            width = 2 + _ % 2
            positions = list(itertools.product(range(2), range(width)))
            actual = [rng.randrange(2) for _ in positions]
            safe = [p for p, v in zip(positions, actual, strict=True) if v == 0]
            visible = rng.sample(safe, min(len(safe), rng.randrange(3)))
            hidden = [p for p in positions if p not in visible]
            if not hidden:
                continue
            target = hidden[0]
            clues = [
                [
                    *p,
                    sum(
                        actual[i]
                        for i, q in enumerate(positions)
                        if q != p and max(abs(p[0] - q[0]), abs(p[1] - q[1])) <= 1
                    ),
                ]
                for p in visible
            ]
            options = []
            for bits in itertools.product((0, 1), repeat=len(hidden)):
                board = dict(zip(hidden, bits, strict=True)) | dict.fromkeys(visible, 0)
                if all(
                    sum(
                        v
                        for q, v in board.items()
                        if q != (r, c) and max(abs(r - q[0]), abs(c - q[1])) <= 1
                    )
                    == n
                    for r, c, n in clues
                ):
                    options.append(board[target])
            expected = (
                "indeterminada"
                if len(set(options)) == 2
                else "mina"
                if options[0]
                else "segura"
            )
            task = {"height": 2, "width": width, "clues": clues, "target": list(target)}
            result = solve(task)
            self.assertEqual(result["classification"], expected)
            self.assertEqual(result["configurations"], len(options))

    def test_generation_and_balance(self):
        dataset = tasks()
        self.assertEqual(dataset, tasks())
        self.assertEqual(len({t["prompt"] for t in dataset}), 90)
        for level in ("easy", "medium", "hard"):
            for label in ("segura", "mina", "indeterminada"):
                self.assertEqual(
                    sum(
                        t["level"] == level and t["reference"] == label for t in dataset
                    ),
                    10,
                )
        for t in dataset:
            self.assertEqual(verify(t, t["reference"]), "correct")
            self.assertEqual(reward(t["prompt"], t["reference"]), 1)

    def test_attacks_and_coordinates(self):
        t = tasks()[0]
        self.assertEqual(verify(t, "[" * 1500 + "0" + "]" * 1500), "unparsed")
        r, c = t["target"]
        answer = {"row": r, "col": c, "classification": t["reference"]}
        self.assertEqual(verify(t, json.dumps(answer)), "correct")
        self.assertEqual(
            verify(
                t,
                "Las coordenadas se escriben [fila,columna].\n```json\n"
                + json.dumps(answer)
                + "\n```",
            ),
            "correct",
        )
        self.assertEqual(
            verify(
                t,
                "Cada mina se cuenta en las pistas vecinas.\n```json\n"
                + json.dumps(answer)
                + "\n```",
            ),
            "correct",
        )
        self.assertEqual(verify(t, "La casilla es " + t["reference"] + "."), "correct")
        self.assertEqual(
            verify(
                t, "```python\nprint(0)\n```\n```json\n" + json.dumps(answer) + "\n```"
            ),
            "correct",
        )
        for text in (
            t["reference"] + ".",
            "**" + t["reference"] + "**",
            "Respuesta final: " + t["reference"],
            json.dumps({"classification": t["reference"]}),
        ):
            self.assertEqual(verify(t, text), "correct")
        self.assertEqual(
            verify(t, "```json\n" + json.dumps(answer) + "\n```\nmina"), "unparsed"
        )
        for text in (
            "segura o mina",
            "mina\nsegura",
            json.dumps(answer) + json.dumps(answer),
            '{"row":0,"row":1,"col":0,"classification":"mina"}',
        ):
            self.assertEqual(verify(t, text), "unparsed")
        for key, value in (
            ("row", r + 1),
            ("col", True),
            ("classification", ["mina", "segura"]),
        ):
            self.assertEqual(verify(t, json.dumps({**answer, key: value})), "unparsed")

    def test_inconsistent_and_ambiguous(self):
        t = {"height": 1, "width": 2, "clues": [], "target": [0, 0]}
        self.assertEqual(solve(t)["classification"], "indeterminada")
        t["clues"] = [[0, 1, 2]]
        with self.assertRaises(ValueError):
            solve(t)


if __name__ == "__main__":
    unittest.main()

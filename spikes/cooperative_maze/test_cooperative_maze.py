import json
import unittest

from cooperative_maze import initial, reward, solve, tasks, transition, verify


class MazeTests(unittest.TestCase):
    def test_manual_states_and_shared_key(self):
        task = {
            "grid": [".kD.", "...."],
            "agents": {"A": [0, 0], "B": [0, 3]},
            "goals": {"A": [1, 1], "B": [0, 2]},
            "action_budget": 6,
        }
        start = initial(task)
        self.assertEqual(
            transition(task, start, {"agent": "B", "move": "L"}), (None, "locked")
        )
        after, error = transition(task, start, {"agent": "A", "move": "R"})
        self.assertIsNone(error)
        self.assertEqual(after, (((0, 1), (0, 3)), True))
        after, error = transition(task, after, {"agent": "B", "move": "L"})
        self.assertIsNone(error)
        self.assertEqual(after, (((0, 1), (0, 2)), True))
        self.assertEqual(
            transition(task, after, {"agent": "A", "move": "R"}), (None, "collision")
        )
        answer = [
            {"agent": "A", "move": "R"},
            {"agent": "B", "move": "L"},
            {"agent": "A", "move": "D"},
        ]
        self.assertEqual(verify(task, json.dumps(answer)), "correct")

    def test_generation_and_cooperation(self):
        dataset = tasks()
        self.assertEqual(dataset, tasks())
        self.assertEqual(len({t["prompt"] for t in dataset}), 90)
        for t in dataset:
            completion = json.dumps(t["reference"])
            self.assertEqual(verify(t, completion), "correct")
            self.assertEqual(
                verify(
                    t,
                    "```\n"
                    + json.dumps(t["grid"])
                    + "\n```\n```json\n"
                    + completion
                    + "\n```",
                ),
                "correct",
            )
            self.assertEqual(
                verify(t, '```json\n["R", "D"]\n```\n```json\n' + completion + "\n```"),
                "unparsed",
            )
            self.assertEqual(
                verify(
                    t,
                    "Las coordenadas se escriben [fila,columna].\n```json\n"
                    + completion
                    + "\n```",
                ),
                "correct",
            )
            self.assertEqual(
                verify(t, "```python\nprint(0)\n```\n```json\n" + completion + "\n```"),
                "correct",
            )
            display = [list(row) for row in t["grid"]]
            for agent, (row, col) in t["agents"].items():
                display[row][col] = agent
            overlay = ["".join(row) for row in display]
            self.assertEqual(
                verify(
                    t,
                    "```\n"
                    + json.dumps(overlay)
                    + "\n```\n```json\n"
                    + completion
                    + "\n```",
                ),
                "correct",
            )
            self.assertEqual(reward(t["prompt"], completion), 1)
            if t["level"] == "hard":
                alone, _ = solve(t, fixed=("A",), goal_agents=("B",))
                self.assertIsNone(alone)

    def test_alternative_and_impossible(self):
        t = {
            "grid": ["..", ".."],
            "agents": {"A": [0, 0]},
            "goals": {"A": [1, 1]},
            "action_budget": 5,
        }
        for moves in (("R", "D"), ("D", "R"), ("R", "L", "D", "R")):
            self.assertEqual(
                verify(t, json.dumps([{"agent": "A", "move": m} for m in moves])),
                "correct",
            )
        t["grid"] = [".#", "#."]
        self.assertIsNone(solve(t)[0])
        self.assertEqual(verify(t, '[{"agent":"A","move":"R"}]'), "wall")

    def test_attacks(self):
        t = tasks()[0]
        self.assertIn(
            verify(t, "[" * 1500 + "0" + "]" * 1500), ("unparsed", "malformed")
        )
        for text in ("NaN", "{}", '[{"agent":"A","agent":"B","move":"U"}]', "[] []"):
            self.assertEqual(verify(t, text), "unparsed")
        self.assertEqual(verify(t, '[{"agent":"Z","move":"U"}]'), "unknown_agent")
        self.assertEqual(verify(t, '[{"agent":"A","move":"teleport"}]'), "malformed")
        self.assertEqual(verify(t, "[]"), "incomplete")
        self.assertEqual(
            verify(t, '```json\n[]\n```\n[{"agent":"A","move":"U"}]'), "unparsed"
        )
        self.assertEqual(
            verify(
                t, json.dumps([{"agent": "A", "move": "R"}] * (t["action_budget"] + 1))
            ),
            "budget",
        )


if __name__ == "__main__":
    unittest.main()

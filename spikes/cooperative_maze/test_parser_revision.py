import json
import unittest

import cooperative_maze as candidate


class ParserRevisionTests(unittest.TestCase):
    def test_ascii_grid_coordinates_and_action_integrity(self):
        task = candidate.tasks(seed=99)[0]
        grid = "\n".join(
            " ".join(f"[{r}][{c}] {tile}" for c, tile in enumerate(row))
            for r, row in enumerate(task["grid"])
        )
        final = "```json\n" + json.dumps(task["reference"]) + "\n```"
        prefix = "```\n" + grid + "\n```\n- `[1, 2]` (fila y columna)\n"
        self.assertEqual(candidate.verify(task, prefix + final), "correct")
        self.assertEqual(
            candidate.verify(task, prefix + final + "\nOtra respuesta: `[0, 1]`"),
            "unparsed",
        )
        malformed = json.dumps([{"agent": "A", "move": "R"}, 0])
        self.assertEqual(
            candidate.verify(task, "```json\n" + malformed + "\n```"), "malformed"
        )
        self.assertEqual(
            candidate.verify(task, final + '\n```json\n["R","D"]\n```'), "unparsed"
        )


if __name__ == "__main__":
    unittest.main()

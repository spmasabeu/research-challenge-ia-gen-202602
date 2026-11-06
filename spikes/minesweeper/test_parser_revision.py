import json
import unittest

import minesweeper as candidate


class ParserRevisionTests(unittest.TestCase):
    def test_input_matrix_and_task_are_not_answers(self):
        task = candidate.tasks()[0]
        answer = {
            "row": task["target"][0],
            "col": task["target"][1],
            "classification": task["reference"],
        }
        final = "```json\n" + json.dumps(answer) + "\n```"
        self.assertEqual(
            candidate.verify(task, json.dumps(task["reference"])), "correct"
        )
        self.assertEqual(
            candidate.verify(task, "```\n" + task["reference"] + "\n```"), "correct"
        )
        for value in (
            [[0, 1], [1, 0]],
            [[0, "?"], ["#", "2"]],
            {k: task[k] for k in ("height", "width", "clues", "target")},
        ):
            text = "```\n" + json.dumps(value) + "\n```\n" + final
            self.assertEqual(candidate.verify(task, text), "correct")
        other = "mina" if task["reference"] != "mina" else "segura"
        self.assertEqual(
            candidate.verify(
                task, final + '\n```json\n{"classification":"' + other + '"}\n```'
            ),
            "unparsed",
        )
        self.assertEqual(
            candidate.verify(task, final + '\n```json\n["mina", "segura"]\n```'),
            "unparsed",
        )


if __name__ == "__main__":
    unittest.main()

import json
import unittest

import scheduling as candidate


class ParserRevisionTests(unittest.TestCase):
    def test_languages_prose_and_conflicting_outputs(self):
        task = candidate.tasks()[0]
        self.assertEqual(
            candidate.verify(task, "[" * 1500 + "0" + "]" * 1500), "unparsed"
        )
        answer = json.dumps(task["reference"])
        text = (
            "```javascript\nconst example = [];\n```\n```json\n"
            + answer
            + "\n```\nEste es el horario final."
        )
        self.assertEqual(candidate.verify(task, text), "correct")
        self.assertEqual(
            candidate.verify(task, "| Predecesoras |\n| [] |\n" + text), "correct"
        )
        self.assertEqual(candidate.verify(task, text + "\n[]"), "unparsed")
        self.assertEqual(
            candidate.verify(task, text + "\n```json\n[]\n```"), "unparsed"
        )
        self.assertEqual(
            candidate.verify(task, '```json\n[{"id":"A","id":"B"}]\n```'), "unparsed"
        )


if __name__ == "__main__":
    unittest.main()

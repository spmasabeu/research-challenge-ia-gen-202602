import copy
import json
import unittest

from scheduling import reward, tasks, verify


class SchedulingTests(unittest.TestCase):
    def test_generation(self):
        dataset = tasks()
        self.assertEqual(dataset, tasks())
        self.assertEqual(len(dataset), 90)
        self.assertEqual(len({t["prompt"] for t in dataset}), 90)
        for task in dataset:
            completion = json.dumps(task["reference"])
            self.assertEqual(verify(task, completion), "correct")
            self.assertEqual(reward(task["prompt"], completion), 1)
            self.assertNotIn('"reference"', task["prompt"])

    def test_alternative_and_half_open(self):
        task = {
            "jobs": [
                {
                    "id": k,
                    "duration": 2,
                    "resources": ["R0", "R1"],
                    "predecessors": [],
                    "deadline": 8,
                }
                for k in ("A", "B")
            ]
        }
        for answer in (
            [
                {"id": "B", "start": 0, "resource": "R1"},
                {"id": "A", "start": 2, "resource": "R1"},
            ],
            [
                {"id": "A", "start": 3, "resource": "R0"},
                {"id": "B", "start": 3, "resource": "R1"},
            ],
        ):
            self.assertEqual(verify(task, json.dumps(answer)), "correct")
        answer[1]["resource"] = "R0"
        self.assertEqual(verify(task, json.dumps(answer)), "overlap")

    def test_attacks(self):
        task = tasks()[0]
        answer = task["reference"]
        for text in (
            "NaN",
            "{}",
            json.dumps(answer) + json.dumps(answer),
            '[{"id":"a","id":"b"}]',
            json.dumps(answer + answer),
            json.dumps(answer[:-1]),
        ):
            self.assertNotEqual(verify(task, text), "correct")
        for field, value in (
            ("start", True),
            ("start", -1),
            ("start", 1.5),
            ("start", float("inf")),
            ("resource", "R999"),
            ("id", "X"),
            ("duration", 0),
        ):
            bad = copy.deepcopy(answer)
            bad[0][field] = value
            self.assertNotEqual(verify(task, json.dumps(bad)), "correct")

    def test_fenced_answers_do_not_select_by_correctness(self):
        task = tasks()[0]
        valid = json.dumps(task["reference"])
        fenced = "Desarrollo\n```json\n" + valid + "\n```"
        self.assertEqual(verify(task, fenced), "correct")
        self.assertEqual(verify(task, fenced + "\n" + fenced), "correct")
        self.assertEqual(verify(task, fenced + "\n```json\n[]\n```"), "unparsed")
        self.assertEqual(verify(task, fenced + "\nOtra respuesta: []"), "unparsed")

    def test_precedence_and_deadline(self):
        task = {
            "jobs": [
                {
                    "id": "A",
                    "duration": 2,
                    "resources": ["R"],
                    "predecessors": [],
                    "deadline": 2,
                },
                {
                    "id": "B",
                    "duration": 1,
                    "resources": ["S"],
                    "predecessors": ["A"],
                    "deadline": 4,
                },
            ]
        }
        answer = [
            {"id": "A", "start": 0, "resource": "R"},
            {"id": "B", "start": 1, "resource": "S"},
        ]
        self.assertEqual(verify(task, json.dumps(answer)), "precedence")
        answer[1]["start"] = 2
        self.assertEqual(verify(task, json.dumps(answer)), "correct")
        answer[0]["start"] = 1
        self.assertEqual(verify(task, json.dumps(answer)), "deadline")


if __name__ == "__main__":
    unittest.main()

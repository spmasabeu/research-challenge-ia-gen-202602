"""Comprobaciones del piloto, sin inferencia ni dependencias externas."""

import json
import math
import unittest

from poc_units import UNITS, tasks, verify


class PilotTests(unittest.TestCase):
    def test_generator_and_equivalent_units(self):
        dataset = tasks()
        self.assertEqual(dataset, tasks())
        self.assertEqual(len(dataset), 30)
        self.assertEqual(len({t["prompt"] for t in dataset}), 30)
        for task in dataset:
            for unit, factor in UNITS[task["dimension"]].items():
                completion = "FINAL: " + json.dumps(
                    {"value": task["answer_si"] / factor, "unit": unit}
                )
                self.assertEqual(verify(task, completion), "correct")

    def test_independent_references(self):
        dataset = tasks()
        easy = dataset[0]
        self.assertEqual(easy["answer_si"], 22)
        # Primer problema difícil: 11 millas en 22 min y 2100 m en 11 s.
        hard = dataset[20]
        self.assertAlmostEqual(
            hard["answer_si"], (11 * 1609.344 + 2100) / (22 * 60 + 11)
        )
        self.assertTrue(
            all(math.isfinite(t["answer_si"]) and t["answer_si"] > 0 for t in dataset)
        )

    def test_reject_invalid_and_ambiguous_answers(self):
        task = tasks()[0]
        self.assertEqual(
            verify(task, 'v = \\frac{110}{5}\n{"value": 22, "unit": "m/s"}'), "correct"
        )
        self.assertEqual(
            verify(task, 'Cálculo: 110/5=22.\n{"value": 22, "unit": "m/s"}'), "correct"
        )
        self.assertEqual(
            verify(task, '{"value": 0, "unit": "m/s"}\n{"value": 22, "unit": "m/s"}'),
            "format",
        )
        for completion in (
            'FINAL: {"value": true, "unit": "m/s"}',
            'FINAL: {"value": NaN, "unit": "m/s"}',
            'FINAL: {"value": [22], "unit": "m/s"}',
            'FINAL: {"value": 22, "unit": "m/s", "other": 0}',
            'FINAL: {"value": 22, "unit": "m/s"}\nFINAL: {}',
            'FINAL: {"value": 22, "unit": "m/s"} extra',
        ):
            self.assertEqual(verify(task, completion), "format")
        self.assertEqual(verify(task, 'FINAL: {"value": 22, "unit": "kg"}'), "unit")
        self.assertEqual(verify(task, 'FINAL: {"value": 0, "unit": "m/s"}'), "numeric")
        self.assertEqual(
            verify(task, 'FINAL: {"value": 22.2, "unit": "m/s"}'), "correct"
        )
        self.assertEqual(
            verify(task, 'FINAL: {"value": 22.3, "unit": "m/s"}'), "numeric"
        )


if __name__ == "__main__":
    unittest.main()

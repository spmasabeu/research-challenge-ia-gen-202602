"""Generador: reproducibilidad, splits sin fuga y referencias calculadas por código."""

import json
import math
import re
import tempfile
import unittest
from pathlib import Path

from challenge.generator import LEVELS, generate, split_of, write_dataset
from challenge.units import FAMILIES, solve
from challenge.verifier import spec_from_prompt


class Generator(unittest.TestCase):
    def test_reproducible_and_sized(self):
        a = generate("train", 20, seed=1)
        self.assertEqual(a, generate("train", 20, seed=1))
        self.assertNotEqual(a, generate("train", 20, seed=2))
        self.assertEqual(len(a), 20 * len(FAMILIES) * len(LEVELS))
        self.assertEqual(len({t["id"] for t in a}), len(a))
        self.assertEqual(len({t["prompt"] for t in a}), len(a))

    def test_splits_are_disjoint_by_instance_for_any_seed(self):
        def bases(split, seed):
            return {
                (t["family"], json.dumps(t["base"], sort_keys=True))
                for t in generate(split, 40, seed)
            }

        test = bases("test", 0)
        for seed in range(3):
            self.assertFalse(test & bases("train", seed))
            self.assertFalse(test & bases("eval", seed))
        self.assertFalse(bases("train", 0) & bases("eval", 0))
        for task in generate("eval", 10):
            self.assertEqual(split_of(task["family"], task["base"]), "eval")

    def test_levels_share_physical_answer_and_grow_conversions(self):
        for instance, group in _by_instance(generate("train", 15)).items():
            self.assertEqual([t["level"] for t in group], list(LEVELS))
            si = [t["answer"] for t in group[:2]]  # easy/medium piden unidad SI
            self.assertTrue(math.isclose(si[0], si[1], rel_tol=1e-12), instance)
            conversions = [t["conversions"] for t in group]
            self.assertEqual(conversions, sorted(conversions))
            self.assertLess(conversions[0], conversions[-1])

    def test_reference_matches_numbers_written_in_prompt(self):
        """Recalcular desde el texto visible, no desde el bloque DATOS."""
        for task in generate("train", 10):
            visible = task["prompt"].split("\nDATOS: ")[0]
            given = {}
            for name, value, unit in re.findall(
                r"(\w) = ([0-9.e+-]+) ([^;.\s]+(?:/[^;.\s]+)*)", visible.split("\n")[0]
            ):
                given[name] = [float(value), unit]
            spec = {**task["spec"], "given": given}
            self.assertTrue(math.isclose(solve(spec), task["answer"], rel_tol=1e-9))
            self.assertEqual(spec_from_prompt(task["prompt"]), task["spec"])

    def test_write_dataset_refuses_to_overwrite_changed_split(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            manifest = write_dataset(out, {"train": 3, "eval": 2, "test": 2})
            self.assertEqual(manifest["splits"]["test"]["tasks"], 2 * 3 * 3)
            write_dataset(out, {"train": 3, "eval": 2, "test": 2})  # idempotente
            with self.assertRaises(FileExistsError):
                write_dataset(out, {"train": 3, "eval": 2, "test": 3})


def _by_instance(tasks):
    groups = {}
    for task in tasks:
        groups.setdefault(task["instance_id"], []).append(task)
    return groups


if __name__ == "__main__":
    unittest.main()

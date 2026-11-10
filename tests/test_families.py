"""Catálogo de familias: compatibilidad con el dataset congelado y familias nuevas."""

import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from challenge.generator import CATALOG, FAMILIES, LEVELS, ORIGINAL_FAMILIES, generate, split_groups
from challenge.models import read_rows
from challenge.verifier import UNITS, extract_answer, load_tasks, reference_from_prompt, reward, verify

NEW_FAMILIES = tuple(f for f in FAMILIES if f not in ORIGINAL_FAMILIES)
FROZEN = ROOT / "data/units/final-v2"


class FamilyCatalogTests(unittest.TestCase):
    @unittest.skipUnless((FROZEN / "exclusions.json").exists(), "dataset congelado no disponible")
    def test_original_families_regenerate_frozen_dataset_byte_for_byte(self):
        excluded = json.loads((FROZEN / "exclusions.json").read_text())["keys"]
        splits = split_groups(generate(4301, 20, excluded), 10, 4, 6)
        for name, rows in splits.items():
            expected = (FROZEN / "private" / f"{name}.jsonl").read_text(encoding="utf-8")
            actual = "".join(json.dumps(r, ensure_ascii=False, allow_nan=False) + "\n" for r in rows)
            self.assertEqual(actual, expected, name)

    def test_new_families_do_not_change_original_tasks(self):
        original = generate(4301, 20)
        extended = generate(4301, 20, families=FAMILIES)
        self.assertEqual(extended[:len(original)], original)
        self.assertEqual(len(extended), 20 * 3 * len(FAMILIES))
        self.assertEqual(len({t["physical_key"] for t in extended}), 20 * len(FAMILIES))

    def test_family_selection_is_validated(self):
        for families in ((), ("speed", "speed"), ("gravity",)):
            with self.assertRaises(ValueError):
                generate(1, 2, families=families)

    def test_catalog_is_consistent_with_verifier(self):
        for family, spec in CATALOG.items():
            self.assertEqual(len(spec.output), len(LEVELS))
            for unit in spec.output:
                self.assertEqual(UNITS[unit][0], family, unit)
            for level_units in spec.units:
                self.assertEqual(set(level_units), {name[0] for name in spec.names})

    def test_fixed_references_for_new_families(self):
        for family, data, expected in (
            ("density", "m=2 kg; V=0.5 m^3", 4),
            ("density", "m1=500 g; m2=1500 g; V=500 L", 4),
            ("pressure", "F=10 N; A=0.5 m^2", 20),
            ("pressure", "F1=0.004 kN; F2=0.006 kN; A=5000 cm^2", 20),
            ("voltage", "I=0.5 A; R=10 ohm", 5),
            ("voltage", "I=500 mA; R1=0.004 kohm; R2=0.006 kohm", 5),
        ):
            self.assertAlmostEqual(reference_from_prompt("Datos: " + data, family), expected)

    def test_reference_rejects_foreign_mixed_or_missing_fields(self):
        for family, data in (
            ("density", "m=2 kg; t=5 s"),            # magnitud de otra familia
            ("pressure", "F=10 W/m^2; A=1 m^2"),     # letra compartida, unidad ajena
            ("voltage", "I=1 A; R=2 ohm; R1=1 ohm"),  # directa y suma mezcladas
            ("voltage", "I=1 A; R1=2 ohm"),           # suma incompleta
            ("density", "m=2 kg"),                    # falta volumen
            ("density", "m=2 kg; m=3 kg; V=1 m^3"),   # duplicado
            ("gravity", "m=2 kg; V=1 m^3"),
        ):
            with self.assertRaises(ValueError, msg=data):
                reference_from_prompt("Datos: " + data, family)

    def test_new_families_levels_and_independent_references(self):
        tasks = generate(7, 6, families=NEW_FAMILIES)
        load_tasks(tasks)  # cada answer_si coincide con el cálculo independiente desde el prompt
        cells = Counter((t["family"], t["level"], t["structure"]) for t in tasks)
        self.assertEqual(len(cells), len(NEW_FAMILIES) * 3 * 2)
        self.assertEqual(set(cells.values()), {3})
        for task in tasks:
            spec = CATALOG[task["family"]]
            level = LEVELS.index(task["level"])
            self.assertEqual(task["requested_unit"], spec.output[level])
            self.assertEqual(task["conversions"], spec.conversions[level])
            self.assertIn(f"Expresa el resultado en {task['requested_unit']}.", task["prompt"])
            self.assertNotIn(f"{task['answer_si']:.6g}", task["prompt"])

    def test_new_families_accept_equivalents_and_reject_attacks(self):
        tasks = generate(11, 2, families=NEW_FAMILIES)
        load_tasks(tasks)
        for task in tasks:
            si = task["answer_si"]
            requested = task["requested_unit"]
            value = si / UNITS[requested][1]
            others = [u for u, (dim, _) in UNITS.items() if dim == task["family"] and u != requested]
            for answer in (f"{value} {requested}", json.dumps({"value": value, "unit": requested}),
                           f"{si / UNITS[others[0]][1]} {others[0]}", f"{value * 1.005} {requested}"):
                self.assertEqual(reward(task["prompt"], answer), 1.0, answer)
            for answer in (f"{value * 1000} {requested}", f"{value / 1000} {requested}",  # error de prefijo
                           f"{value * 1.02} {requested}", f"{value} J", f"{value}",
                           f"{value} {requested} o {value * 2} {requested}",
                           f"{value * 2} {requested}\n{value} {requested}"):
                self.assertEqual(reward(task["prompt"], answer), 0.0, answer)
        density = {"family": "density", "answer_si": 4}
        for answer in ("rho = 4 kg/m^3", "ρ = 0.004 g/cm^3", "4 kg/m³", '{"value": 0.004, "unit": "g/cm³"}'):
            self.assertEqual(verify(density, answer)["status"], "correct", answer)
        self.assertEqual(verify({"family": "pressure", "answer_si": 20}, "P = 0.02 kPa")["status"], "correct")
        self.assertEqual(verify({"family": "voltage", "answer_si": 5}, "V = 5000 mV")["status"], "correct")
        self.assertEqual(verify(density, "4 Pa")["status"], "unit")
        self.assertIsNone(extract_answer("4 kg/m^3\n0 kg/m^3"))

    def test_splits_balance_all_families(self):
        splits = split_groups(generate(4301, 20, families=FAMILIES), 10, 4, 6)
        self.assertEqual([len(v) for v in splits.values()], [90 * 2, 36 * 2, 54 * 2])
        keys = [{t["physical_key"] for t in rows} for rows in splits.values()]
        self.assertFalse(keys[0] & keys[1] or keys[0] & keys[2] or keys[1] & keys[2])
        for rows in splits.values():
            cells = Counter((t["family"], t["level"], t["structure"]) for t in rows)
            self.assertEqual(len(cells), len(FAMILIES) * 3 * 2)
            self.assertEqual(len(set(cells.values())), 1)

    def test_cli_generates_selected_families(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "tasks.jsonl"
            subprocess.run([sys.executable, "-m", "challenge.harness", "generate", "--seed", "5", "--groups", "2",
                            "--families", "density", "voltage", "--out", str(out)],
                           check=True, env={"PYTHONPATH": str(ROOT / "src"), "PYTHONDONTWRITEBYTECODE": "1"})
            rows = read_rows(out)
            self.assertEqual(Counter(r["family"] for r in rows), {"density": 6, "voltage": 6})


if __name__ == "__main__":
    unittest.main()

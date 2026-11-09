"""Fixtures independientes, ataques y trazabilidad sin modelos."""

import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from challenge.derive import build, collect, required_audits
from challenge.evaluate import metrics, summarize
from challenge.generator import dump, generate, split_groups
from challenge.harness import check_dataset, compare_local, freeze
from challenge.models import OPTIONS, read_rows, run, sha256, validate_rows
from challenge.verifier import (
    extract_answer,
    load_tasks,
    reference_from_prompt,
    reward,
    verify,
)


class ChallengeTests(unittest.TestCase):
    def test_fixed_references(self):
        for family, data, expected in (
            ("speed", "d=110 m; t=5 s", 22),
            ("speed", "d1=0.04 km; d2=0.07 km; t=0.0833333333333333 min", 22),
            ("energy", "m=2 kg; v=3 m/s", 9),
            ("energy", "m1=700 g; m2=1300 g; v=10.8 km/h", 9),
            ("luminosity", "d=1 m; F=1 W/m^2", 12.566370614359172),
            ("luminosity", "d=0.001 km; F1=200 erg/s/cm^2; F2=800 erg/s/cm^2", 12.566370614359172),
        ):
            self.assertAlmostEqual(reference_from_prompt("Datos: " + data, family), expected)

    def test_determinism_pairing_and_reference_from_visible_data(self):
        tasks = generate(4300, 10)
        self.assertEqual(tasks, generate(4300, 10))
        self.assertEqual(len(tasks), 90)
        self.assertTrue(all(t["conversions"] == 2 and t["requested_unit"] == "W" for t in tasks if t["family"] == "luminosity" and t["level"] == "hard"))
        load_tasks(tasks)
        for task in tasks:
            self.assertTrue(math.isclose(task["answer_si"], reference_from_prompt(task["prompt"], task["family"]), rel_tol=1e-10))
        keys = {t["physical_key"] for t in tasks}
        self.assertFalse(keys & {t["physical_key"] for t in generate(4301, 20, keys)})
        broken = [{**tasks[0], "answer_si": 1234567}]
        with self.assertRaises(ValueError):
            load_tasks(broken)

    def test_splits_keep_physical_groups_and_structures(self):
        splits = split_groups(generate(4301, 20), 10, 4, 6)
        self.assertEqual([len(v) for v in splits.values()], [90, 36, 54])
        for i, (name, tasks) in enumerate(splits.items()):
            for other in list(splits.values())[i + 1:]:
                self.assertFalse({t["physical_key"] for t in tasks} & {t["physical_key"] for t in other})
            for family in ("speed", "energy", "luminosity"):
                for level in ("easy", "medium", "hard"):
                    cell = [t for t in tasks if t["family"] == family and t["level"] == level]
                    self.assertEqual(sum(t["structure"] == "sum" for t in cell), len(cell) // 2, name)

    def test_equivalences_and_tolerance(self):
        task = {"family": "speed", "answer_si": 22}
        for answer in ('22 m/s', '79,2 km/h', 'FINAL: 2.2e1 m/s', '22 × 10^0 m/s',
                       '```json\n{"value": "79,2", "unit": "km/h"}\n```',
                       '22 m/s\n79.2 km/h', '{"value":22,"unit":"m/s"}\n{"value":79.2,"unit":"km/h"}'):
            self.assertEqual(verify(task, answer)["reward"], 1, answer)
        self.assertEqual(verify(task, '22.21 m/s')["status"], "correct")
        self.assertEqual(verify(task, '22.23 m/s')["status"], "numeric")
        self.assertEqual(verify(task, '22 J')["status"], "unit")
        self.assertEqual(verify(task, '22 kWh')["status"], "unparsed")
        self.assertEqual(verify(task, 'Valor final = 22 m/s')["status"], "correct")
        self.assertEqual(verify({"family": "luminosity", "answer_si": 1}, '{"value":1,"unit":"Watts"}')["status"], "correct")
        self.assertEqual(verify(task, r'3. El resultado es $ \boxed{22} $ m/s.')["status"], "correct")
        self.assertEqual(verify(task, '3. El resultado es aproximadamente 22 m/s.\n{"value":22,"unit":"m/s"}')["status"], "correct")
        self.assertEqual(verify({"family": "energy", "answer_si": 9}, r'4. Resultado: $ E \approx 9 \, \text{J} $.' + '\n{"value":9,"unit":"J"}')["status"], "correct")
        for family, answer, reference in (("energy", '0.009 kJ', 9), ("energy", '9e7 erg', 9),
                                          ("luminosity", '1 kW', 1000), ("luminosity", '1 Lsun', 3.828e26)):
            self.assertEqual(verify({"family": family, "answer_si": reference}, answer)["reward"], 1)

    def test_attacks_and_ambiguity(self):
        for text in ('22 m/s\n0 m/s', 'FINAL: 22 m/s\nFINAL: 0 m/s',
                     '{"value":22,"value":0,"unit":"m/s"}',
                     '{"value":22,"unit":"m/s","extra":0}',
                     '{"value":true,"unit":"m/s"}', '{"value":NaN,"unit":"m/s"}',
                     '{"value":1e999,"unit":"m/s"}', 'NaN m/s',
                     '22', '22 m/s o 0 m/s', '22 m/s\nNo es mi respuesta.',
                     'eval(__import__("os")) m/s', '22*1 m/s',
                     'FINAL: 22 m/s\n{"value":0,"unit":"m/s"}',
                     'FINAL:\n0 m/s\n{"value":22,"unit":"m/s"}',
                     'Alternativa: 0 m/s o {"value":22,"unit":"m/s"}',
                     'La respuesta es 0 m/s.\n{"value":22,"unit":"m/s"}',
                     '3. El resultado es 0 m/s.\n{"value":22,"unit":"m/s"}',
                     'La respuesta final es 0 m/s.\n{"value":22,"unit":"m/s"}',
                     '22 m/s o 0 m/s\n{"value":22,"unit":"m/s"}',
                     'No es la respuesta: {"value":22,"unit":"m/s"}',
                     'No es la respuesta:\n{"value":22,"unit":"m/s"}',
                     'Resultado incorrecto:\n{"value":22,"unit":"m/s"}',
                     'El resultado es:\n0 m/s\n{"value":22,"unit":"m/s"}',
                     'Valor final = 0 m/s\n{"value":22,"unit":"m/s"}',
                     '{"value":22,"unit":"m/s"}\n0 m/s'):
            self.assertIsNone(extract_answer(text), text)
        self.assertEqual(verify({"family": "speed", "answer_si": 22}, 'Desarrollo: 22 m/s\nFINAL: 0 m/s')["status"], "numeric")
        json.dumps(verify({"family": "luminosity", "answer_si": 1}, '1e308 kW'), allow_nan=False)
        with self.assertRaises(ValueError):
            reference_from_prompt('Datos: d=110 s; t=5 m', 'speed')

    def test_reward_registration(self):
        tasks = generate(4300, 2)
        load_tasks(tasks)
        self.assertEqual(reward(tasks[0]["prompt"], f'{tasks[0]["answer_si"]} m/s'), 1.0)
        with self.assertRaises(ValueError):
            reward("no registrado", "22 m/s")

    def test_known_metrics_keep_unparsed_separate(self):
        rows = [{"task_id": "a", "status": s} for s in ("correct", "numeric", "unparsed")]
        rows += [{"task_id": "b", "status": "numeric"} for _ in range(3)]
        result = metrics(rows)
        self.assertAlmostEqual(result["pass_at_k"]["1"], 1 / 6)
        self.assertEqual(result["pass_at_k"]["3"], .5)
        self.assertAlmostEqual(result["coverage"], 5 / 6)
        self.assertAlmostEqual(result["pass_at_k_upper_bound"]["1"], 1 / 3)

    def test_incremental_run_resume_and_refuse_changed_config(self):
        calls = []

        def fake_api(route, payload=None):
            if route == "tags":
                return {"models": [{"name": "fixture", "digest": "fixture-1"}]}
            if route == "chat":
                calls.append(payload)
                return {"done": True, "done_reason": "stop", "message": {"content": "22 m/s"}, "eval_count": 4}
            return {}

        with tempfile.TemporaryDirectory() as folder, patch("challenge.models.api", fake_api), patch("challenge.models.fcntl.flock"), patch("challenge.models.subprocess.run", return_value=Mock(stdout="fixture hardware")):
            root = Path(folder)
            tasks = generate(4300, 1)[:1]
            dump(root / "tasks.jsonl", tasks)
            run(root / "tasks.jsonl", root / "run", "fixture", 3)
            saved = (root / "run/responses.jsonl").read_bytes()
            run(root / "tasks.jsonl", root / "run", "fixture", 3)
            self.assertEqual(len(calls), 3)
            self.assertEqual(saved, (root / "run/responses.jsonl").read_bytes())
            self.assertEqual([c["options"]["seed"] for c in calls], [42, 43, 44])
            with self.assertRaises(ValueError):
                run(root / "tasks.jsonl", root / "run", "fixture", 4)
            rows = read_rows(root / "run/responses.jsonl")
            for bad in (rows[:1], rows + [rows[0]], [{**rows[0], "prompt": "alterado"}, *rows[1:]]):
                with self.assertRaises(ValueError):
                    validate_rows(tasks, bad, "fixture", 3)
            with self.assertRaises(FileExistsError):
                dump(root / "tasks.jsonl", tasks)


    def test_frozen_dataset_regenerates_and_detects_tampering(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "exclusions.json").write_text(json.dumps({"keys": [generate(4301, 1)[0]["physical_key"]]}))
            (root / "models.json").write_text("{}")
            freeze(root / "final", root / "exclusions.json", root / "models.json")
            self.assertEqual(check_dataset(root / "final"), {"train": 90, "eval": 36, "test": 54})
            (root / "runs").mkdir()
            with self.assertRaisesRegex(ValueError, "cuatro modelos"):
                compare_local(root / "final", root / "runs")
            path = root / "final/public/test.jsonl"
            path.write_text(path.read_text() + "{}\n")
            with self.assertRaises(ValueError):
                check_dataset(root / "final")

    def test_backend_incomplete_and_memory_error_preserve_attempts(self):
        def fake_api(route, payload=None):
            if route == "tags":
                return {"models": [{"name": "fixture", "digest": "fixture-1"}]}
            if route == "ps":
                raise OSError("monitoring unavailable")
            if route == "chat":
                partial = payload["options"]["seed"] == 42
                return {"done": not partial, "message": {"content": f'{tasks[0]["answer_si"]} m/s' if partial else ""}}
            return {}
        with tempfile.TemporaryDirectory() as folder, patch("challenge.models.api", fake_api), patch("challenge.models.fcntl.flock"), patch("challenge.models.subprocess.run", return_value=Mock(stdout="fixture hardware")):
            root = Path(folder)
            tasks = generate(4300, 1)[:1]
            dump(root / "tasks.jsonl", tasks)
            run(root / "tasks.jsonl", root / "run", "fixture", 3)
            rows = read_rows(root / "run/responses.jsonl")
            self.assertEqual(len(rows), 3)
            self.assertIn("unavailable", rows[0]["memory"])
            _, summary = summarize(tasks, rows)
            self.assertEqual(summary["all"]["statuses"], {"unparsed": 3})
            self.assertEqual(summary["all"]["backend_incomplete"], 1)

    def test_sft_dpo_dedup_provenance_and_expanded_audit(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            dataset = root / "dataset"
            (dataset / "private").mkdir(parents=True)
            tasks = [t for t in generate(4300, 2) if t["family"] == "speed"][:4]
            dump(dataset / "private/train.jsonl", tasks)
            (dataset / "protocol.json").write_text(json.dumps({"options": OPTIONS, "think": False, "seed_base": 42}))
            (dataset / "models.json").write_text(json.dumps({"qwen3:8b": {"digest": "fixture-1"}, "qwen3:1.7b": {"digest": "fixture-2"}}))
            teacher = root / "teacher"
            teacher.mkdir()
            config = {"model": "qwen3:8b", "digest": "fixture-1", "samples": 8, "tasks_sha256": sha256(dataset / "private/train.jsonl"), "options": OPTIONS, "think": False}
            (teacher / "metadata.json").write_text(json.dumps({"config": config}))
            rows = []
            for task in tasks:
                value = task["answer_si"]
                texts = [f'Pasos fixture {i}.\n{value} m/s' for i in range(3)]
                texts += [f'{value * 1.5} m/s', f'{value * 1.5}  m/s', f'{value * 2} m/s', 'sin resultado', 'sin  resultado']
                for index, text in enumerate(texts):
                    rows.append({"model": "qwen3:8b", "task_id": task["id"], "prompt": task["prompt"], "sample_index": index,
                                 "request": {"model": "qwen3:8b", "messages": [{"role": "user", "content": task["prompt"]}], "think": False, "options": {**OPTIONS, "seed": 42 + index}},
                                 "result": {"done": True, "done_reason": "stop", "message": {"content": text}}})
            dump(teacher / "responses.jsonl", rows)
            records, _ = collect(tasks, rows, teacher.name)
            correct = [r for r in records if r["status"] == "correct"]
            required = required_audits(records)
            audits = [{"candidate_id": r["candidate_id"], "completion_sha256": r["sources"][0]["completion_sha256"], "judgment": "keep", "reason": "Fixture: referencia independiente, sin cálculo inferido."} for r in correct if r["candidate_id"] in required]
            audit_path = root / "audit.jsonl"
            dump(audit_path, audits)
            sft, dpo, stats = build(dataset, teacher, [audit_path])
            self.assertEqual((len(sft), len(dpo)), (12, 8))
            self.assertEqual(stats["teacher_unique_responses"], 24)
            self.assertEqual(stats["dpo_max_pairs_per_task"], 2)
            self.assertEqual(stats["dpo_reused_chosen"], 0)
            self.assertTrue(all(row["rejected"] != 'sin resultado' for row in dpo))
            self.assertTrue(any(len(row["metadata"]["rejected_sources"]) == 2 for row in dpo))
            negative_tasks = root / "negative-tasks.jsonl"
            dump(negative_tasks, tasks[:1])
            negative = root / "negative"
            negative.mkdir()
            negative_config = {**config, "model": "qwen3:1.7b", "digest": "fixture-2", "samples": 1, "tasks_sha256": sha256(negative_tasks)}
            (negative / "metadata.json").write_text(json.dumps({"config": negative_config}))
            negative_row = json.loads(json.dumps(rows[3]))
            negative_row.update(model="qwen3:1.7b", sample_index=0)
            negative_row["request"]["model"] = "qwen3:1.7b"
            negative_row["request"]["options"]["seed"] = 42
            dump(negative / "responses.jsonl", [negative_row])
            _, mixed_dpo, _ = build(dataset, teacher, [audit_path], negative_tasks, negative)
            self.assertTrue(any(len({s["model"] for s in r["metadata"]["rejected_sources"]}) == 2 for r in mixed_dpo))
            outside = {**tasks[0], "id": "outside-train"}
            negative_tasks.write_text(json.dumps(outside) + "\n")
            negative_config["tasks_sha256"] = sha256(negative_tasks)
            (negative / "metadata.json").write_text(json.dumps({"config": negative_config}))
            negative_row["task_id"] = "outside-train"
            (negative / "responses.jsonl").write_text(json.dumps(negative_row) + "\n")
            with self.assertRaisesRegex(ValueError, "fuera de train"):
                build(dataset, teacher, [audit_path], negative_tasks, negative)
            rejected = next(a for a in audits if next(r for r in correct if r["candidate_id"] == a["candidate_id"])["level"] == "easy")
            rejected["judgment"] = "reject"
            audit_path.write_text("".join(json.dumps(a) + "\n" for a in audits))
            with self.assertRaises(ValueError):
                build(dataset, teacher, [audit_path])
            missing = next(r for r in correct if r["candidate_id"] not in required)
            audits.append({"candidate_id": missing["candidate_id"], "completion_sha256": missing["sources"][0]["completion_sha256"], "judgment": "keep", "reason": "Revisión ampliada fixture."})
            audit_path.write_text("".join(json.dumps(a) + "\n" for a in audits))
            sft, dpo, stats = build(dataset, teacher, [audit_path])
            self.assertEqual(len(sft), 11)
            self.assertNotIn(rejected["candidate_id"], {r["metadata"]["candidate_id"] for r in sft})
            self.assertEqual(stats["expanded_cells"], ["speed/easy"])


if __name__ == "__main__":
    unittest.main()

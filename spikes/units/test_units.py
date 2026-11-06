"""Comprobaciones del piloto, sin inferencia ni dependencias externas."""

import hashlib
import json
import math
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evaluate import analyze, code_hashes, comparison, evaluate_response, metrics, run
from units import UNITS, extract_answer, tasks, verify

SPEED_TASK = {
    "id": "example",
    "level": "easy",
    "family": "speed",
    "dimension": "speed",
    "answer_si": 22,
}


class UnitsTests(unittest.TestCase):
    def test_generator_and_equivalent_units(self):
        dataset = tasks()
        self.assertEqual(dataset, tasks())
        self.assertEqual(len(dataset), 90)
        self.assertEqual(len({t["prompt"] for t in dataset}), 90)
        for task in dataset:
            for unit, factor in UNITS[task["dimension"]].items():
                completion = "FINAL: " + json.dumps(
                    {"value": task["answer_si"] / factor, "unit": unit}
                )
                self.assertEqual(verify(task, completion), "correct")

    def test_reject_invalid_and_ambiguous_answers(self):
        task = SPEED_TASK
        self.assertEqual(
            verify(task, 'v = \\frac{110}{5}\n{"value": 22, "unit": "m/s"}'), "correct"
        )
        self.assertEqual(
            verify(task, 'Cálculo: 110/5=22.\n{"value": 22, "unit": "m/s"}'), "correct"
        )
        self.assertEqual(
            verify(task, '{"value": 0, "unit": "m/s"}\n{"value": 22, "unit": "m/s"}'),
            "unparsed",
        )
        for completion in (
            'FINAL: {"value": true, "unit": "m/s"}',
            'FINAL: {"value": NaN, "unit": "m/s"}',
            'FINAL: {"value": [22], "unit": "m/s"}',
            'FINAL: {"value": 22, "unit": "m/s", "other": 0}',
            'FINAL: {"value": 22, "unit": "m/s"}\nFINAL: {}',
            'FINAL: {"value": 22, "unit": "m/s"} extra',
        ):
            self.assertEqual(verify(task, completion), "unparsed")
        self.assertEqual(verify(task, 'FINAL: {"value": 22, "unit": "kg"}'), "unit")
        self.assertEqual(verify(task, 'FINAL: {"value": 0, "unit": "m/s"}'), "numeric")
        self.assertEqual(
            verify(task, 'FINAL: {"value": 22.2, "unit": "m/s"}'), "correct"
        )
        self.assertEqual(
            verify(task, 'FINAL: {"value": 22.3, "unit": "m/s"}'), "numeric"
        )

    def test_surface_format_does_not_change_correctness(self):
        task = SPEED_TASK
        for completion in (
            '**FINAL:** {"value": 22, "unit": "m/s"}',
            'La respuesta final es: {"value": 22, "unit": "m/s"}',
            'Final: {"value": 22, "unit": "m/s"}',
            '```json\n{"value": 22, "unit": "m/s"}\n```',
            "v = 110 / 5 = 22 m/s",
            "La respuesta final es 22,0 m/s.",
            "FINAL: 2,2 × 10^1 m/s",
            '{"value": "2,2*10^1", "unit": "m/s"}',
            'Velocidad = 22 m/s. {"value": 22, "unit": "m/s"}',
            'FINAL: {"value": 79.2, "unit": "km/h"}',
            "$ \\boxed{22} \\text{ m/s} $",
            'Calculamos velocidad final:\nFINAL: {"value": 22, "unit": "m/s"}',
            'Respuesta: {"v": 22, "unidad": "m/s"}',
            "Respuesta: $ \\boxed{22} \\, \\text{m/s} $",
            "Respuesta numérica: **22**; unidad: **m/s**.",
            "Respuesta numérica: 22\nUnidad: m/s",
            "Respuesta numérica: **22 m/s**",
            "La velocidad del móvil es de aproximadamente 22 m/s.",
            "Por lo tanto, la velocidad es de 22 metros por segundo.",
            "22m/s",
            "La velocidad es de 22 metros/segundo.",
            "79.2 kms/h",
            "Respuesta: `22 m/s`",
            "Respuesta: $ \\boxed{22} \\, \\text{m/s} $.",
            "Respuesta final:\n$$\n\\boxed{22} \\, \\text{m/s}\n$$",
            'Respuesta: `{"valor": 22, "unidad": "m/s"}`',
            'Respuesta: {"v": "22 m/s"}',
            "Respuesta: 22 m/s, unidad: m/s.",
            'FINAL: {"value": 22, "unit": "m/s"}\nRespuesta numérica y unidad:\n22 m/s',
        ):
            with self.subTest(completion=completion):
                self.assertEqual(verify(task, completion), "correct")
        luminosity = tasks()[60]
        self.assertEqual(
            verify(luminosity, f"{luminosity['answer_si'] / 1000} kW"), "correct"
        )
        self.assertEqual(verify(tasks()[30], "1 kW"), "unit")

    def test_no_answer_search_or_execution(self):
        task = SPEED_TASK
        for completion in (
            'FINAL: {"value": 0, "value": 22, "unit": "m/s"}',
            'FINAL: [{"value": 22, "unit": "m/s"}]',
            'FINAL: {"value": "__import__("os").system("false")", "unit": "m/s"}',
            "22 m/s o 0 m/s",
            "FINAL: 22",
            "FINAL: 1e3",
            "d = 110 m\nt = 5 s",
            'FINAL: {"value": 22, "unit": "m/s"} o 0 m/s',
            '22 m/s o {"value": 0, "unit": "m/s"}',
            "22 m/s\n0 m/s",
            "FINAL: 22 m/s\n0 m/s",
            'FINAL: {"value": 22, "unit": "m/s"}\nRespuesta numérica y unidad:\n0 m/s',
            "Respuesta: 22 m/s, unidad: km/h.",
            'FINAL: {"v": "22 m/s"} o 0 m/s',
        ):
            with self.subTest(completion=completion):
                self.assertEqual(verify(task, completion), "unparsed")
        self.assertEqual(verify(task, "Desarrollo: 22 m/s\nFINAL: 0 m/s"), "numeric")
        self.assertEqual(extract_answer("FINAL: 4.07e-6 W"), (4.07e-6, "W"))
        self.assertEqual(verify(task, "FINAL: 22 kg"), "unit")

    def test_pairs_have_same_physical_answer(self):
        dataset = tasks()
        self.assertEqual(dataset, tasks())
        self.assertEqual(len(dataset), 90)
        self.assertEqual(len({task["prompt"] for task in dataset}), 90)
        for family in ("speed", "energy", "luminosity"):
            for level in ("easy", "medium", "hard"):
                self.assertEqual(
                    sum(t["family"] == family and t["level"] == level for t in dataset),
                    10,
                )
        for pair_id in {task["pair_id"] for task in dataset}:
            pair = [task for task in dataset if task["pair_id"] == pair_id]
            self.assertEqual(len(pair), 3)
            self.assertEqual(len({task["answer_si"] for task in pair}), 1)
            for task in pair:
                unit = task["requested_unit"]
                value = task["answer_si"] / UNITS[task["dimension"]][unit]
                self.assertEqual(verify(task, f"FINAL: {value} {unit}"), "correct")
        # Recalcular SI a partir de los números efectivamente escritos en cada prompt.
        for task in dataset:
            values = [
                float(x)
                for x in re.findall(
                    r"\d+(?:\.\d+)?(?:e[+-]?\d+)?", task["prompt"].split("Calcula")[0]
                )
            ]
            a, b = values[:2]
            level = task["level"]
            if task["family"] == "speed":
                expected = (
                    a
                    * (1000 if level != "easy" else 1)
                    / (b * (60 if level == "hard" else 1))
                )
            elif task["family"] == "energy":
                expected = (
                    0.5
                    * a
                    / (1000 if level != "easy" else 1)
                    * (b / (3.6 if level == "hard" else 1)) ** 2
                )
            else:
                expected = (
                    4
                    * math.pi
                    * (a * (1000 if level != "easy" else 1)) ** 2
                    * b
                    / (1000 if level == "hard" else 1)
                )
            self.assertTrue(
                math.isclose(task["answer_si"], expected, rel_tol=1e-10), task["id"]
            )

    def test_metrics_keep_unparsed_separate(self):
        rows = [
            {"id": "a", "status": status}
            for status in ("correct", "numeric", "unparsed")
        ]
        result = metrics(rows, (1, 2, 3, 4))
        self.assertEqual(result["pass_at_k"], {"1": 1 / 3, "2": 2 / 3, "3": 1.0})
        self.assertEqual(
            result["pass_at_k_upper_bound"], {"1": 2 / 3, "2": 1.0, "3": 1.0}
        )
        self.assertEqual(result["accuracy_parsed"], 0.5)
        self.assertEqual(result["coverage"], 2 / 3)
        self.assertEqual(
            metrics([{"id": "a", "status": "unparsed"}])["accuracy_parsed"], None
        )
        rows.append({"id": "b", "status": "numeric"})
        self.assertNotIn("3", metrics(rows)["pass_at_k"])

    def test_analysis_checks_integrity_and_completeness(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "fixture"
            source.mkdir()
            raw_tasks = (json.dumps(SPEED_TASK) + "\n").encode()
            (root / "tasks.jsonl").write_bytes(raw_tasks)
            metadata = {
                "dataset_sha256": hashlib.sha256(raw_tasks).hexdigest(),
                "model": "fixture",
                "samples": 1,
                "evaluation": code_hashes(),
            }
            row = evaluate_response(
                SPEED_TASK,
                {
                    "id": "example",
                    "sample": 0,
                    "response": {"message": {"content": "Respuesta: 22 m/s"}},
                },
            )

            def save(rows):
                raw = "".join(json.dumps(item) + "\n" for item in rows).encode()
                (source / "responses.jsonl").write_bytes(raw)
                metadata["responses_sha256"] = hashlib.sha256(raw).hexdigest()
                (source / "metadata.json").write_text(json.dumps(metadata))

            save([row])
            result = analyze(source)
            self.assertEqual(result["final"]["overall"]["pass_at_k"], {"1": 1.0})
            save([row, row])
            with self.assertRaisesRegex(ValueError, "duplicada"):
                analyze(source)
            save([])
            with self.assertRaisesRegex(ValueError, "incompleta"):
                analyze(source)
            save([{**row, "status": "numeric"}])
            with self.assertRaisesRegex(ValueError, "inconsistente"):
                analyze(source)
            save([row])
            (source / "responses.jsonl").write_text("changed")
            with self.assertRaisesRegex(ValueError, "hash de respuestas"):
                analyze(source)
            (root / "tasks.jsonl").write_bytes(raw_tasks + b"\n")
            with self.assertRaisesRegex(ValueError, "hash de tareas"):
                analyze(source)

    def test_manual_extraction_keeps_provenance(self):
        completion = "Desarrollo: 22 m/s\nRespuesta final: 22"
        review = {
            "value": 22,
            "unit": "m/s",
            "evidence": "El desarrollo declara 22 m/s.",
            "completion_sha256": hashlib.sha256(completion.encode()).hexdigest(),
        }
        row = {
            "id": "example",
            "sample": 0,
            "response": {"message": {"content": completion}},
            "manual_review": review,
        }
        result = evaluate_response(SPEED_TASK, row)
        self.assertEqual(result["automatic_status"], "unparsed")
        self.assertEqual(result["status"], "correct")
        self.assertEqual(result["manual_review"], review)
        self.assertEqual(result["response"], row["response"])
        for bad_review in (
            {**review, "evidence": ""},
            {**review, "completion_sha256": "changed"},
            {**review, "value": True},
        ):
            with self.subTest(review=bad_review), self.assertRaises(ValueError):
                evaluate_response(SPEED_TASK, {**row, "manual_review": bad_review})
        with self.assertRaisesRegex(ValueError, "ya interpretable"):
            evaluate_response(
                SPEED_TASK, {**row, "response": {"message": {"content": "22 m/s"}}}
            )

    def test_saved_results_match_source_of_truth(self):
        root = Path(__file__).with_name("results")
        computed = comparison(root)
        self.assertEqual(computed, json.loads((root / "comparison.json").read_text()))
        qwen = computed["models"]["qwen3-1.7b"]
        self.assertEqual(qwen["final"]["statuses"], {"correct": 193, "numeric": 77})
        self.assertEqual(
            qwen["automatic"]["statuses"],
            {"correct": 191, "numeric": 74, "unparsed": 5},
        )
        self.assertEqual(qwen["manual_reviews"], 5)
        llama = computed["models"]["llama3.2-1b"]
        self.assertEqual(
            llama["final"]["statuses"],
            {"correct": 32, "numeric": 97, "unparsed": 115, "unit": 26},
        )
        self.assertEqual(llama["manual_reviews"], 0)

    def test_run_preserves_prompts_seeds_and_existing_results(self):
        task = {
            **SPEED_TASK,
            "prompt": "Un móvil recorre 110 m en 5 s. Calcula su rapidez.",
        }
        calls = []

        def fake_api(path, payload=None):
            if path == "chat":
                calls.append(payload)
                return {"message": {"content": "22 m/s"}, "done_reason": "stop"}
            return {
                "version": {"version": "fixture"},
                "show": {"details": {}},
                "tags": {"models": [{"name": "fixture", "digest": "fixture"}]},
            }[path]

        with (
            tempfile.TemporaryDirectory() as folder,
            patch("evaluate.tasks", return_value=[task]),
            patch("evaluate.api", side_effect=fake_api),
            patch("evaluate.shutil.which", return_value=None),
            patch("evaluate.subprocess.check_output", return_value="fixture\n"),
        ):
            output = Path(folder) / "fixture"
            summary = run("fixture", output, 3)
            self.assertEqual(analyze(output), summary)
            before = (output / "responses.jsonl").read_bytes()
            with self.assertRaises(FileExistsError):
                run("fixture", output, 3)
            self.assertEqual((output / "responses.jsonl").read_bytes(), before)
            self.assertEqual([call["options"]["seed"] for call in calls], [42, 43, 44])
            self.assertTrue(
                all(
                    call["messages"] == [{"role": "user", "content": task["prompt"]}]
                    for call in calls
                )
            )


if __name__ == "__main__":
    unittest.main()

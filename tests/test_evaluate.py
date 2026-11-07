"""pass@k calculado a mano, re-puntuación sin inferencia y datos derivados."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from challenge import derive, evaluate
from challenge.generator import generate


class Metrics(unittest.TestCase):
    def test_pass_at_k_by_hand(self):
        rows = [{"id": "a", "status": s} for s in ("correct", "numeric", "unparsed")]
        result = evaluate.metrics(rows, (1, 2, 3, 4))
        self.assertAlmostEqual(result["pass_at_k"]["1"], 1 / 3)
        self.assertAlmostEqual(result["pass_at_k"]["2"], 2 / 3)
        self.assertAlmostEqual(result["pass_at_k"]["3"], 1.0)
        self.assertNotIn("4", result["pass_at_k"])
        self.assertAlmostEqual(result["pass_at_k_upper_bound"]["1"], 2 / 3)
        self.assertEqual(result["accuracy_parsed"], 0.5)
        self.assertAlmostEqual(result["coverage"], 2 / 3)
        # n=4, c=1, k=2: 1 - C(3,2)/C(4,2) = 1 - 3/6
        self.assertAlmostEqual(evaluate.pass_at_k(4, 1, 2), 0.5)


def _fake_api(answers):
    """Ollama falso: responde la referencia o un valor erróneo según la muestra."""

    def api(path, payload=None, timeout=None):
        if path == "version":
            return {"version": "fixture"}
        prompt = payload["messages"][0]["content"]
        task = answers[prompt]
        good = payload["options"]["seed"] == 42
        value = task["answer"] if good else task["answer"] * 3
        return {
            "message": {"content": f"FINAL: {value:.6g} {task['requested_unit']}"},
            "done_reason": "stop",
        }

    return api


class RunScoreDerive(unittest.TestCase):
    def test_run_score_and_derive_without_model(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            tasks = generate("train", 2)
            tasks_file = root / "train.jsonl"
            tasks_file.write_text("".join(json.dumps(t) + "\n" for t in tasks))
            answers = {t["prompt"]: t for t in tasks}
            out = root / "run"
            with patch.object(evaluate, "_api", side_effect=_fake_api(answers)):
                summary = evaluate.run(tasks_file, "fixture", out, samples=2)
                # Reanudar no duplica respuestas.
                evaluate.run(tasks_file, "fixture", out, samples=2)
            self.assertTrue(summary["complete"])
            self.assertEqual(summary["overall"]["pass_at_k"], {"1": 0.5, "2": 1.0})
            self.assertEqual(summary["mixed_tasks"], len(tasks))
            self.assertIn("speed/hard", summary["family_level"])
            self.assertEqual(evaluate.score(out)["overall"], summary["overall"])

            rows = derive.load_runs([out])
            sft = derive.build_sft(rows)
            dpo = derive.build_dpo(rows)
            self.assertEqual(len(sft), len(tasks))
            self.assertEqual(len(dpo), len(tasks))
            self.assertTrue(all(p["chosen"] != p["rejected"] for p in dpo))

    def test_derive_refuses_non_train(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            tasks = generate("test", 1)
            tasks_file = root / "test.jsonl"
            tasks_file.write_text("".join(json.dumps(t) + "\n" for t in tasks))
            out = root / "run"
            with patch.object(evaluate, "_api", side_effect=_fake_api({t["prompt"]: t for t in tasks})):
                evaluate.run(tasks_file, "fixture", out, samples=1)
            with self.assertRaisesRegex(ValueError, "train"):
                derive.load_runs([out])


if __name__ == "__main__":
    unittest.main()

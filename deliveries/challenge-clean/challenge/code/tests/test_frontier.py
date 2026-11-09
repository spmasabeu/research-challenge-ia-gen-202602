import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from challenge import frontier
from challenge.generator import dump, generate


class FrontierTests(unittest.TestCase):
    def test_budget_resume_and_common_evaluator_without_network(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task = generate(81, 1)[0]
            dump(root / "tasks.jsonl", [task])
            (root / "credential").write_text("OPENROUTER_API_KEY=test-credential\n")
            calls = []

            def fake_api(path, key, payload=None):
                calls.append(path)
                if path == "key":
                    return {"data": {"limit": 5}}
                return {"model": frontier.MODEL, "provider": "DeepInfra", "id": "fixture",
                        "usage": {"cost": .001, "completion_tokens": 8},
                        "choices": [{"finish_reason": "stop", "message": {"content": f'{task["answer_si"]} m/s'}}]}

            with patch.object(frontier, "api", fake_api):
                frontier.run(root / "tasks.jsonl", root / "run", 3, root / "credential", root / "ledger.jsonl")
                frontier.run(root / "tasks.jsonl", root / "run", 3, root / "credential", root / "ledger.jsonl")
                with self.assertRaisesRegex(ValueError, "configuración"):
                    frontier.run(root / "tasks.jsonl", root / "run", 3, root / "credential", root / "other-ledger.jsonl")
                self.assertEqual(calls.count("chat/completions"), 3)
                self.assertEqual(calls.count("key"), 1)
                result = frontier.score(root / "tasks.jsonl", root / "run", root / "score")
                self.assertEqual(result["pass_at_k"], {"1": 1, "3": 1})
                rows = frontier.read_rows(root / "run/responses.jsonl")
                rows[0]["request"]["temperature"] = 0
                with self.assertRaisesRegex(ValueError, "parámetros"):
                    frontier.validate([task], rows, 3)
                (root / "full.jsonl").write_text("{}\n" * 250)
                with self.assertRaisesRegex(ValueError, "presupuesto"):
                    frontier.run(root / "tasks.jsonl", root / "blocked", 1, root / "credential", root / "full.jsonl")
                self.assertEqual(calls.count("chat/completions"), 3)
                self.assertEqual(len(frontier.read_rows(root / "ledger.jsonl")), 3)
                self.assertNotIn("test-credential", (root / "run/responses.jsonl").read_text())

    def test_truncation_not_mathematical_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task = generate(81, 1)[0]
            dump(root / "tasks.jsonl", [task])
            (root / "credential").write_text("OPENROUTER_API_KEY=test-credential\n")

            def fake_api(path, key, payload=None):
                if path == "key":
                    return {"data": {}}
                return {"model": frontier.MODEL, "provider": "DeepInfra", "usage": {"cost": 0},
                        "choices": [{"finish_reason": "length", "message": {"content": None}}]}

            with patch.object(frontier, "api", fake_api):
                frontier.run(root / "tasks.jsonl", root / "run", 1, root / "credential", root / "ledger.jsonl")
            result = frontier.score(root / "tasks.jsonl", root / "run", root / "score")
            self.assertEqual(result["statuses"], {"unparsed": 1})
            self.assertEqual(result["truncated"], 1)
            self.assertEqual(json.loads((root / "score/metadata.json").read_text())["cost_usd"], 0)


if __name__ == "__main__":
    unittest.main()

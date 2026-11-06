import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import evaluate
from database_repair import known_patch, tasks


class EvaluationTests(unittest.TestCase):
    def test_metrics(self):
        rows = [{"id": "a", "status": s} for s in ("correct", "deadline", "unparsed")]
        result = evaluate.metrics(rows)
        self.assertAlmostEqual(result["pass_at_k"]["1"], 1 / 3)
        self.assertEqual(result["pass_at_k"]["3"], 1)
        self.assertAlmostEqual(result["coverage"], 2 / 3)

    def test_artifacts_and_no_overwrite(self):
        prompts = {t["prompt"]: t for t in tasks(seed=99)}
        calls = []

        def api(path, payload=None):
            if path == "tags":
                return {"models": [{"name": "fixture", "digest": "fixture"}]}
            if path != "chat":
                return {"version": "fixture"}
            calls.append(payload)
            task = prompts[payload["messages"][0]["content"]]
            if len(payload["messages"]) == 1:
                return {
                    "message": {"content": '{"query":"SELECT * FROM lines"}'},
                    "eval_count": 10,
                    "done_reason": "stop",
                }
            return {
                "message": {"content": json.dumps({"patch": known_patch(task)})},
                "eval_count": 10,
                "done_reason": "stop",
            }

        with (
            patch.object(evaluate.fcntl, "flock"),
            tempfile.TemporaryDirectory() as folder,
            patch.object(evaluate, "api", side_effect=api),
            patch.object(
                evaluate.subprocess,
                "run",
                return_value=SimpleNamespace(stdout="fixture"),
            ),
            patch.object(evaluate.subprocess, "check_output", return_value="fixture"),
        ):
            output = Path(folder) / "fixture"
            evaluate.run("fixture", output, pilot=True)
            self.assertEqual(
                evaluate.analyze(output)["overall"]["statuses"], {"correct": 3}
            )
            controls = evaluate.analyze(output)["controls"]
            self.assertEqual(controls["clean"]["responses"], 1)
            self.assertEqual(controls["corrupted"]["statuses"], {"correct": 2})
            self.assertEqual(
                evaluate.comparison(output.parent),
                json.loads((output.parent / "comparison.json").read_text()),
            )
            self.assertEqual([c["options"]["seed"] for c in calls], [42] * 6)
            self.assertTrue(all(c["think"] is False for c in calls))
            with self.assertRaises(FileExistsError):
                evaluate.run("fixture", output, pilot=True)
            path = output / "responses.jsonl"
            before = path.read_text()
            path.write_text(before + before)
            with self.assertRaisesRegex(ValueError, "hash"):
                evaluate.analyze(output)
            path.write_text(before)
            metadata_path = output / "metadata.json"
            metadata = json.loads(metadata_path.read_text())
            path.write_text("")
            metadata["artifacts"]["fixture/responses.jsonl"] = evaluate.digest(path)
            evaluate.dump(metadata_path, metadata)
            with self.assertRaisesRegex(ValueError, "incompleta"):
                evaluate.analyze(output)


if __name__ == "__main__":
    unittest.main()

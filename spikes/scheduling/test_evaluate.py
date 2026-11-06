import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import evaluate
import resume
from scheduling import tasks


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
            return {
                "message": {"content": json.dumps(task["reference"])},
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
            output = Path(folder) / "results" / "fixture"
            evaluate.run("fixture", output, pilot=True)
            self.assertEqual(
                evaluate.analyze(output)["overall"]["statuses"], {"correct": 3}
            )
            self.assertEqual(
                evaluate.comparison(output.parent),
                json.loads((output.parent / "comparison.json").read_text()),
            )
            self.assertEqual([c["options"]["seed"] for c in calls], [42] * 3)
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
            prefix = before.splitlines(keepends=True)[0]
            path.write_text(prefix)
            metadata["artifacts"].pop("fixture/responses.jsonl")
            evaluate.dump(metadata_path, metadata)
            prefix_hash = evaluate.digest(path)
            resume.resume(output)
            result = evaluate.analyze(output)
            self.assertEqual(result["overall"]["statuses"], {"correct": 3})
            updated = json.loads(metadata_path.read_text())
            event = updated["resumptions"][0]
            self.assertEqual(event["prefix_sha256"], prefix_hash)
            self.assertEqual(
                (Path(event["snapshot"]) / "responses.jsonl").read_text(), prefix
            )
            self.assertTrue(path.read_text().startswith(prefix))
            self.assertEqual(len(calls), 5)
            with self.assertRaisesRegex(ValueError, "completa"):
                resume.resume(output)


if __name__ == "__main__":
    unittest.main()

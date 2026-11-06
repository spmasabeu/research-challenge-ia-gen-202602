import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import run_spikes


class QueueTests(unittest.TestCase):
    def test_select_historical_checker_without_changing_hashes(self):
        with (
            tempfile.TemporaryDirectory() as folder,
            patch.object(run_spikes, "ROOT", Path(folder)),
        ):
            root = Path(folder) / "spikes/minesweeper"
            archive = root / "history/parser-v1"
            archive.mkdir(parents=True)
            hashes = {}
            for name in ("evaluate.py", "minesweeper.py"):
                (archive / name).write_text("historical")
                (root / name).write_text("current")
                hashes[name] = hashlib.sha256(b"historical").hexdigest()
            metadata = root / "pilot/qwen3-1.7b/metadata.json"
            metadata.parent.mkdir(parents=True)
            metadata.write_text(json.dumps({"code": hashes}))
            self.assertEqual(
                run_spikes.checker("minesweeper", "pilot"),
                "spikes/minesweeper/history/parser-v1/evaluate.py",
            )
            self.assertEqual(json.loads(metadata.read_text())["code"], hashes)

    def test_order_skip_and_resume_without_inference(self):
        with (
            tempfile.TemporaryDirectory() as folder,
            patch.object(run_spikes, "ROOT", Path(folder)),
        ):
            commands = list(run_spikes.commands())
            self.assertEqual(commands[0][1][3], "qwen3:1.7b")
            self.assertEqual(commands[1][1][3], "llama3.2:1b")
            self.assertEqual(commands[2][1][1], "check")
            self.assertEqual(commands[3][0], "text_to_sql")
            self.assertIn("--pilot", commands[3][1])
            output = Path(folder) / "spikes/scheduling/results/qwen3-1.7b"
            output.mkdir(parents=True)
            with self.assertRaisesRegex(RuntimeError, "parcial"):
                list(run_spikes.commands())
            (output.parent.parent / "resume.py").write_text("fixture")
            resumed = list(run_spikes.commands())
            self.assertEqual(
                resumed[0][1],
                ["spikes/scheduling/resume.py", "spikes/scheduling/results/qwen3-1.7b"],
            )
            (output / "summary.json").write_text("{}")
            skipped = list(run_spikes.commands())
            self.assertEqual(skipped[0][1][3], "llama3.2:1b")


if __name__ == "__main__":
    unittest.main()

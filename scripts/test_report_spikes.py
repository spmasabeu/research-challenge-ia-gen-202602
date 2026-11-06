import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import report_spikes


class ReportTests(unittest.TestCase):
    def test_comparison_preserves_notes_and_uses_automatic_units(self):
        with (
            tempfile.TemporaryDirectory() as folder,
            patch.object(report_spikes, "ROOT", Path(folder)),
        ):
            self.assertFalse(report_spikes.comparison())
            spikes = Path(folder) / "spikes"
            value = {
                "responses": 270,
                "pass_at_k": {"1": 0.2, "3": 0.4},
                "coverage": 0.8,
            }
            for name in ["units", *report_spikes.NAMES]:
                for model in report_spikes.MODELS:
                    root = spikes / name / "results" / model
                    root.mkdir(parents=True)
                    if name == "units":
                        summary = {
                            "automatic": {"overall": value},
                            "final": {"overall": {**value, "pass_at_k": {"1": 0.99}}},
                        }
                        (root / "responses.jsonl").write_text(
                            json.dumps({"response": {"total_duration": 60_000_000_000}})
                            + "\n"
                        )
                    else:
                        summary = {"overall": value, "cost": {"wall_seconds": 60}}
                    (root / "summary.json").write_text(json.dumps(summary))
            path = spikes / "README.md"
            path.write_text("# User entry\n")
            self.assertTrue(report_spikes.comparison())
            path.write_text(path.read_text() + "\nHuman conclusions\n")
            self.assertTrue(report_spikes.comparison())
            text = path.read_text()
            self.assertIn("User entry", text)
            self.assertIn("Human conclusions", text)
            self.assertEqual(text.count("<!-- COMPARISON_START -->"), 1)
            self.assertIn("20.00% / 40.00%", text)
            self.assertNotIn("99.00%", text)

    def test_render_saved_metrics_and_reject_partial(self):
        with (
            tempfile.TemporaryDirectory() as folder,
            patch.object(report_spikes, "ROOT", Path(folder)),
        ):
            root = Path(folder) / "spikes/scheduling"
            output = root / "results/qwen3-1.7b"
            output.mkdir(parents=True)
            (root / "README.md").write_text("# Spike: fixture\n")
            metrics = {
                "responses": 270,
                "statuses": {"correct": 90, "unparsed": 180},
                "pass_at_k": {"1": 1 / 3, "3": 1},
                "coverage": 1 / 3,
            }
            summary = {
                "overall": metrics,
                "level": {},
                "cost": {
                    "wall_seconds": 1,
                    "prompt_tokens": 10,
                    "output_tokens": 20,
                    "calls": 270,
                    "truncated_calls": 2,
                },
                "distinct_completions_per_task": 3,
            }
            path = output / "summary.json"
            path.write_text(json.dumps(summary))
            (output / "responses.jsonl").write_text(
                json.dumps(
                    {
                        "id": "fixture",
                        "sample": 0,
                        "status": "correct",
                        "completion": "[]",
                    }
                )
                + "\n"
            )
            report_spikes.render("scheduling")
            text = (root / "report.md").read_text()
            self.assertIn("90/270", text)
            self.assertIn("33.33%", text)
            self.assertIn("Benchmark parcial", text)
            self.assertIn("unparsed", text)
            (root / "report.md").write_text(
                text
                + "\n<!-- ANALYSIS_START -->\nHuman review\n<!-- ANALYSIS_END -->\n"
            )
            report_spikes.render("scheduling")
            text = (root / "report.md").read_text()
            self.assertIn("Human review", text)
            summary["overall"]["responses"] = 269
            path.write_text(json.dumps(summary))
            with self.assertRaisesRegex(ValueError, "incompleta"):
                report_spikes.render("scheduling")
            self.assertEqual((root / "report.md").read_text(), text)


if __name__ == "__main__":
    unittest.main()

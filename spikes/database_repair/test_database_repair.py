import copy
import json
import time
import unittest
from unittest.mock import patch

from database_repair import (
    expected,
    known_patch,
    patch_status,
    query,
    reward,
    tasks,
    verify,
)


class RepairTests(unittest.TestCase):
    def test_wall_watchdog(self):
        with patch("database_repair._execute", side_effect=lambda *args: time.sleep(2)):
            started = time.monotonic()
            self.assertEqual(query({}, "SELECT 1")["error"], "timeout")
            self.assertLess(time.monotonic() - started, 1)

    def test_generation_and_controls(self):
        dataset = tasks()
        self.assertEqual(dataset, tasks())
        self.assertEqual(len(dataset), 90)
        self.assertEqual(sum(not t["corrupted"] for t in dataset), 9)
        for task in dataset:
            self.assertEqual(expected(task["data"]), task["clean"])
            patch = known_patch(task)
            self.assertEqual(len(patch), len(task["corrupted"]))
            self.assertEqual(patch_status(task, list(reversed(patch))), "correct")
            completion = json.dumps({"trajectory": [], "final": {"patch": patch}})
            self.assertEqual(verify(task, completion), "correct")
            self.assertEqual(
                verify(task, "| Datos |\n| [] |\n```json\n" + completion + "\n```"),
                "correct",
            )
            self.assertEqual(
                verify(
                    task, "```python\nprint(0)\n```\n```json\n" + completion + "\n```"
                ),
                "correct",
            )
            self.assertEqual(reward(task["prompt"], completion), 1)

    def test_independent_rules(self):
        data = {
            "products": [[7, "X", 9]],
            "orders": [[1, 0], [2, 12]],
            "lines": [[4, 1, "X", 3, 999, 2, 6]],
        }
        self.assertEqual(
            expected(data),
            {
                "products": [[7, "X", 9]],
                "orders": [[1, 27], [2, 0]],
                "lines": [[4, 1, "X", 3, 7, 9, 27]],
            },
        )
        self.assertEqual(data["lines"][0][4], 999)

    def test_partial_wrong_and_collateral(self):
        task = tasks()[61]
        patch = known_patch(task)
        self.assertEqual(patch_status(task, patch[:-1]), "detection")
        bad = copy.deepcopy(patch)
        bad[0]["value"] += 1
        self.assertEqual(patch_status(task, bad), "repair")
        self.assertEqual(patch_status(task, patch + patch), "duplicate")
        self.assertEqual(
            patch_status(
                task, [{"table": "products", "id": 1, "column": "price", "value": 1}]
            ),
            "unauthorized",
        )
        self.assertEqual(
            patch_status(
                task, [{"table": "lines", "id": 999, "column": "amount", "value": 1}]
            ),
            "unknown_id",
        )
        clean = tasks()[0]
        self.assertEqual(
            patch_status(
                clean,
                [
                    {
                        "table": "lines",
                        "id": 1,
                        "column": "amount",
                        "value": clean["data"]["lines"][0][6],
                    }
                ],
            ),
            "unnecessary",
        )
        for bad in (
            [{"delete": "lines"}],
            [{"table": "lines", "id": True, "column": "amount", "value": 1}],
        ):
            self.assertEqual(patch_status(task, bad), "protocol")

    def test_sandbox_and_trajectory(self):
        task = tasks()[1]
        self.assertIn(
            verify(task, "[" * 1500 + "0" + "]" * 1500), ("unparsed", "protocol")
        )
        for sql in (
            "DELETE FROM lines",
            "ATTACH ':memory:' AS x",
            "PRAGMA table_info(lines)",
            "SELECT load_extension('x')",
            "SELECT * FROM sqlite_master",
            "SELECT 1; SELECT 2",
        ):
            self.assertIn("error", query(task["data"], sql))
        self.assertEqual(
            query(task["data"], "SELECT * FROM lines")["rows"],
            [tuple(r) for r in task["data"]["lines"]],
        )
        expensive = "WITH RECURSIVE x(n) AS (VALUES(1) UNION ALL SELECT n+1 FROM x WHERE n<9999999) SELECT SUM(n) FROM x"
        self.assertEqual(query(task["data"], expensive)["error"], "timeout")
        sql = "SELECT * FROM lines"
        record = {
            "trajectory": [{"query": sql, "result": query(task["data"], sql)}],
            "final": {"patch": known_patch(task)},
        }
        self.assertEqual(verify(task, json.dumps(record)), "correct")
        record["trajectory"][0]["result"] = {}
        self.assertEqual(verify(task, json.dumps(record)), "protocol")
        self.assertEqual(verify(task, '{"final":{},"final":{}}'), "unparsed")
        self.assertEqual(
            verify(
                task,
                '```json\n{"trajectory":[],"final":{"patch":[]}}\n```\n{"patch":[]}',
            ),
            "unparsed",
        )


if __name__ == "__main__":
    unittest.main()

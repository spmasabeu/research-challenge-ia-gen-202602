import collections
import copy
import time
import unittest
from unittest.mock import patch

from text_to_sql import bag, details, extract, query, reward, tasks, verify


class SQLTests(unittest.TestCase):
    def test_wall_watchdog(self):
        with patch("text_to_sql._execute", side_effect=lambda *args: time.sleep(2)):
            started = time.monotonic()
            self.assertEqual(query({}, "SELECT 1")[0], "timeout")
            self.assertLess(time.monotonic() - started, 1)

    def test_generation_and_independent_fixtures(self):
        dataset = tasks()
        self.assertEqual(dataset, tasks())
        self.assertEqual(len({t["prompt"] for t in dataset}), 90)
        for t in dataset:
            self.assertEqual(verify(t, t["reference"]), "correct")
            for data in t["databases"]:
                customers = {r[0]: r for r in data["customers"]}
                orders = data["orders"]
                threshold = t["threshold"]
                if t["family"] == "filter":
                    expected = [
                        (o[0], o[2])
                        for o in orders
                        if o[2] is not None
                        and o[2] >= threshold
                        and o[3] is not None
                        and o[3] >= t["date"]
                    ]
                elif t["family"] == "join":
                    expected = [
                        (customers[o[1]][1],)
                        for o in orders
                        if customers[o[1]][2] == t["region"]
                        and o[2] is not None
                        and o[2] >= threshold
                    ]
                elif t["family"] == "having":
                    sums = collections.defaultdict(int)
                    for o in orders:
                        if o[2] is not None:
                            sums[o[1]] += o[2]
                    expected = [
                        (key, value) for key, value in sums.items() if value > threshold
                    ]
                else:
                    counts = {
                        c[0]: sum(o[1] == c[0] for o in orders)
                        for c in customers.values()
                        if c[2] == t["region"]
                    }
                    expected = [
                        (key, customers[key][1])
                        for key, n in counts.items()
                        if n == max(counts.values())
                    ]
                self.assertEqual(bag(query(data, t["reference"])[1]), bag(expected))

    def test_sql_alternative_and_types(self):
        task = tasks()[0]
        alternative = task["reference"].replace("amount >=", "amount + 0 >=")
        self.assertEqual(verify(task, alternative), "correct")
        self.assertEqual(
            verify(
                task,
                "```sql\n"
                + alternative
                + "\n```\nLa cláusula SELECT obtiene las columnas solicitadas.",
            ),
            "correct",
        )
        self.assertEqual(
            verify(
                task,
                "```python\nprint('example')\n```\n```sql\n" + alternative + "\n```",
            ),
            "correct",
        )
        self.assertEqual(reward(task["prompt"], alternative), 1)
        self.assertEqual(bag([(1,), (1.0,)]), bag([(1.0,), (1,)]))
        self.assertNotEqual(bag([(1,), (1,)]), bag([(1,)]))
        self.assertNotEqual(bag([(None,)]), bag([(0,)]))
        self.assertNotEqual(bag([("1",)]), bag([(1,)]))

    def test_attacks_and_limits(self):
        self.assertIsNone(extract("```sql\nSELECT 1\n```\nSELECT 2"))
        self.assertIsNone(extract("```sql\nSELECT 1\n```\no SELECT 2"))
        self.assertIsNone(extract("```sql\nSELECT 1\n```\n; SELECT 2"))
        self.assertIsNone(extract("```sql\nSELECT 1\n```\n```sql\nSELECT 2\n```"))
        data = tasks()[0]["databases"][0]
        before = copy.deepcopy(data)
        for sql in (
            "DELETE FROM orders",
            "PRAGMA database_list",
            "ATTACH DATABASE '/tmp/x' AS x",
            "SELECT load_extension('bad')",
            "SELECT * FROM sqlite_master",
            "SELECT 1; SELECT 2",
            "CREATE TABLE x(a)",
            "SELECT readfile('/etc/passwd')",
        ):
            self.assertNotEqual(query(data, sql)[0], "ok", sql)
        self.assertEqual(data, before)
        expensive = "WITH RECURSIVE x(n) AS (VALUES(1) UNION ALL SELECT n+1 FROM x WHERE n<100000000) SELECT SUM(n) FROM x"
        self.assertEqual(query(data, expensive)[0], "timeout")
        self.assertEqual(
            query(
                data,
                "WITH RECURSIVE x(n) AS (VALUES(1) UNION ALL SELECT n+1 FROM x WHERE n<300) SELECT n FROM x",
            )[0],
            "limit",
        )

    def test_hidden_hardcoding_null_and_duplicates(self):
        dataset = tasks()
        rejected = 0
        for t in dataset:
            rows = query(t["databases"][0], t["reference"])[1]
            if rows:

                def literal(v):
                    return (
                        "NULL"
                        if v is None
                        else "'" + v.replace("'", "''") + "'"
                        if isinstance(v, str)
                        else str(v)
                    )

                sql = " UNION ALL ".join(
                    "SELECT " + ",".join(literal(v) for v in row) for row in rows
                )
                result = details(t, sql)
                self.assertTrue(result["visible_pass"])
                rejected += result["hidden_failure"]
            if t["family"] == "join":
                self.assertEqual(
                    verify(
                        t,
                        t["reference"].replace(
                            "SELECT c.name", "SELECT DISTINCT c.name"
                        ),
                    ),
                    "semantic",
                )
        self.assertGreater(rejected, 60)
        t = next(t for t in dataset if t["family"] == "subquery")
        self.assertEqual(
            verify(t, t["reference"].replace("COUNT(*)", "COUNT(amount)")), "semantic"
        )
        t = dataset[0]
        self.assertEqual(verify(t, t["reference"].replace(">=", ">")), "semantic")


if __name__ == "__main__":
    unittest.main()

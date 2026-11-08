"""Recalcular métricas desde respuestas crudas, sin nuevas inferencias."""

from collections import Counter, defaultdict
from math import comb

from .verifier import verify


def metrics(rows):
    if not rows:
        raise ValueError("no hay respuestas")
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["task_id"]].append(row["status"])
    sizes = {len(group) for group in grouped.values()}
    if len(sizes) != 1:
        raise ValueError("muestras desbalanceadas")
    n = sizes.pop()
    statuses = Counter(row["status"] for row in rows)
    lower, upper = {}, {}
    for k in (1, 3):
        if k > n:
            continue
        scores, bounds = [], []
        for group in grouped.values():
            c = group.count("correct")
            u = group.count("unparsed")
            scores.append(1 - comb(n - c, k) / comb(n, k))
            bounds.append(1 - comb(n - c - u, k) / comb(n, k))
        lower[str(k)] = sum(scores) / len(scores)
        upper[str(k)] = sum(bounds) / len(bounds)
    return {"tasks": len(grouped), "responses": len(rows), "n": n, "statuses": dict(statuses),
            "coverage": 1 - statuses["unparsed"] / len(rows), "pass_at_k": lower,
            "pass_at_k_upper_bound": upper,
            "truncated": sum(row.get("truncated", False) for row in rows)}


def summarize(tasks, responses):
    by_id = {t["id"]: t for t in tasks}
    scored = []
    for row in responses:
        task = by_id[row["task_id"]]
        scored.append({"task_id": row["task_id"], "sample_index": row["sample_index"],
                       "family": task["family"], "level": task["level"], "structure": task["structure"],
                       **verify(task, row["result"]["message"]["content"]),
                       "truncated": row["result"].get("done_reason") == "length"})
    summary = {"all": metrics(scored)}
    for field in ("family", "level", "structure"):
        summary[field] = {value: metrics([r for r in scored if r[field] == value]) for value in sorted({r[field] for r in scored})}
    summary["family_level"] = {f"{family}/{level}": metrics([r for r in scored if r["family"] == family and r["level"] == level])
                               for family, level in sorted({(r["family"], r["level"]) for r in scored})}
    return scored, summary

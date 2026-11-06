"""Reevaluar automáticamente el parser; preservar inferencias y evaluación V1."""

import datetime
import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import evaluate


def main():
    root = Path(__file__).resolve().parent
    repository = root.parent.parent
    status_file = repository / "spikes/queue/status.json"
    if status_file.exists():
        status = json.loads(status_file.read_text())
        command = status.get("command") or []
        if (
            status["state"] == "running"
            and command
            and command[0].startswith("spikes/minesweeper/")
        ):
            raise RuntimeError(
                "Esperar a que la cola termine minesweeper y pase al siguiente spike"
            )
    results = root / "results"
    previous = evaluate.comparison(results)
    models = ["qwen3-1.7b", "llama3.2-1b"]
    if set(previous) != set(models) or any(
        s["overall"]["responses"] != 270 for s in previous.values()
    ):
        raise ValueError("Se requieren ambas corridas completas y verificadas")
    if (root / "minesweeper.py").read_bytes() == (
        root / "staged/minesweeper.py"
    ).read_bytes():
        raise ValueError("El parser propuesto ya está vigente")
    version = 1
    while (root / f"history/parser-v{version}").exists():
        version += 1
    archive = root / f"history/parser-v{version}"
    archive.mkdir(parents=True)
    for name in ("evaluate.py", "minesweeper.py", "README.md", "report.md"):
        shutil.copy2(root / name, archive / name)
    results.rename(archive / "results")
    (root / "minesweeper.py").write_bytes((root / "staged/minesweeper.py").read_bytes())
    importlib.reload(evaluate.domain)
    results.mkdir()
    for name in ("tasks.jsonl", "environment.json"):
        shutil.copy2(archive / "results" / name, results / name)
    indexed = {
        t["id"]: t
        for t in map(json.loads, (results / "tasks.jsonl").read_text().splitlines())
    }
    transitions = {}
    for model in models:
        source = archive / "results" / model
        target = results / model
        target.mkdir()
        metadata = json.loads((source / "metadata.json").read_text())
        original_rows = [
            json.loads(line)
            for line in (source / "responses.jsonl").read_text().splitlines()
        ]
        rows = []
        changed = 0
        for original in original_rows:
            row = {
                **original,
                "status": evaluate.domain.verify(
                    indexed[original["id"]], original["completion"]
                ),
            }
            assert {k: v for k, v in row.items() if k != "status"} == {
                k: v for k, v in original.items() if k != "status"
            }
            changed += row["status"] != original["status"]
            rows.append(row)
        with (target / "responses.jsonl").open("x") as stream:
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        metadata.setdefault("inference_code", metadata["code"])
        metadata["code"] = evaluate.hashes()
        metadata["inference_resumptions"] = metadata.pop(
            "resumptions", metadata.get("inference_resumptions", [])
        )
        metadata["reevaluation"] = {
            "utc": datetime.datetime.now(datetime.UTC).isoformat(),
            "kind": "automatic_parser_revision",
            "source": str(source.relative_to(root)),
            "source_responses_sha256": evaluate.digest(source / "responses.jsonl"),
            "source_metadata_sha256": evaluate.digest(source / "metadata.json"),
            "changed_statuses": changed,
            "reason": "Distinguir matrices y objetos de entrada de la clasificación final; admitir etiquetas únicas y rechazar clasificaciones contradictorias. Sin selección por referencia ni revisiones manuales.",
        }
        metadata["artifacts"][model + "/responses.jsonl"] = evaluate.digest(
            target / "responses.jsonl"
        )
        evaluate.dump(target / "metadata.json", metadata)
        evaluate.dump(target / "summary.json", evaluate.analyze(target))
        transitions[model] = changed
    evaluate.dump(results / "comparison.json", evaluate.comparison(results))
    subprocess.run(
        [
            sys.executable,
            str(archive / "evaluate.py"),
            "check",
            str(archive / "results"),
        ],
        check=True,
    )
    subprocess.run(
        [sys.executable, str(repository / "scripts/report_spikes.py")], check=True
    )
    print(
        json.dumps(
            {
                "changed_statuses": transitions,
                "raw_model_calls": "unchanged",
                "archive": str(archive),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

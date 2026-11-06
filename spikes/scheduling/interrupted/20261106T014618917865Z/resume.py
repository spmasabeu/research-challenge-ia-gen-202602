"""Retomar un benchmark interrumpido conservando un snapshot de su prefijo."""

import argparse
import datetime
import fcntl
import json
import shutil
import time
from pathlib import Path

import evaluate


def resume(output):
    with (Path.home() / ".cache" / "research-challenge-local-inference.lock").open(
        "a"
    ) as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            evaluate.analyze(output)
        except ValueError as error:
            if str(error) != "corrida incompleta":
                raise
        else:
            raise ValueError("la corrida ya está completa")
        metadata_path = output / "metadata.json"
        metadata = json.loads(metadata_path.read_text())
        model = metadata["model"]
        tag = next(t for t in evaluate.api("tags")["models"] if t["name"] == model)
        if tag["digest"] != metadata["model_tag"]["digest"]:
            raise ValueError("cambiaron los pesos del modelo")
        version = evaluate.api("version")
        if version != metadata["environment"]["ollama"]:
            raise ValueError("cambió la versión del backend")
        dataset = [
            json.loads(line)
            for line in (output.parent / "tasks.jsonl").read_text().splitlines()
        ]
        path = output / "responses.jsonl"
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        seen = {(row["id"], row["sample"]) for row in rows}
        now = datetime.datetime.now(datetime.UTC)
        backup = output.parent.parent / "interrupted" / now.strftime("%Y%m%dT%H%M%S%fZ")
        backup.mkdir(parents=True)
        for source in (
            metadata_path,
            path,
            output.parent / "tasks.jsonl",
            output.parent / "environment.json",
        ):
            shutil.copy2(source, backup / source.name)
        event = {
            "resumed_utc": now.isoformat(),
            "preserved_rows": len(rows),
            "prefix_sha256": evaluate.digest(path),
            "metadata_before_sha256": evaluate.digest(metadata_path),
            "snapshot": str(backup),
            "resume_code_sha256": evaluate.digest(Path(__file__)),
            "ollama": version,
            "model_digest": tag["digest"],
        }
        evaluate.dump(backup / "manifest.json", event)
        metadata.setdefault("resumptions", []).append(event)
        evaluate.dump(metadata_path, metadata)
        with path.open("a") as stream:
            for task in dataset:
                for sample in range(metadata["samples"]):
                    if (task["id"], sample) in seen:
                        continue
                    started = time.monotonic()
                    completion, calls, messages = evaluate.attempt(
                        task, model, evaluate.SEEDS[sample]
                    )
                    row = {
                        "id": task["id"],
                        "sample": sample,
                        "seed": evaluate.SEEDS[sample],
                        "prompt": task["prompt"],
                        "completion": completion,
                        "calls": calls,
                        "messages": messages,
                        "wall_seconds": time.monotonic() - started,
                        "status": evaluate.domain.verify(task, completion),
                    }
                    stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                    stream.flush()
                    rows.append(row)
                    print(f"{model} {task['id']} {sample}: {row['status']}", flush=True)
        metadata["artifacts"][output.name + "/responses.jsonl"] = evaluate.digest(path)
        metadata["finished_utc"] = datetime.datetime.now(datetime.UTC).isoformat()
        evaluate.dump(metadata_path, metadata)
        evaluate.dump(output / "summary.json", evaluate.analyze(output))
        evaluate.dump(
            output.parent / "comparison.json", evaluate.comparison(output.parent)
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    resume(parser.parse_args().output)

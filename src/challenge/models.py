"""Inferencia Ollama local, secuencial y reanudable por clave exacta."""

import fcntl
import hashlib
import json
import os
import platform
import subprocess
import time
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

OPTIONS = {"temperature": .7, "top_k": 40, "top_p": .9, "min_p": 0,
           "num_ctx": 2048, "num_batch": 128, "num_gpu": 99, "num_predict": 1024}


def api(route, payload=None):
    req = urllib.request.Request("http://127.0.0.1:11434/api/" + route,
                                 data=None if payload is None else json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    # URL fija local, nunca construida desde salida del modelo o URL del usuario.
    with urllib.request.urlopen(req, timeout=600) as response:  # nosec B310
        return json.load(response)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def validate_rows(tasks, rows, model, samples, complete=True):
    expected = {(t["id"], i): t for t in tasks for i in range(samples)}
    seen = set()
    for row in rows:
        key = row["task_id"], row["sample_index"]
        if key in seen or key not in expected or row["model"] != model or row["prompt"] != expected[key]["prompt"]:
            raise ValueError("clave, modelo o prompt inconsistente")
        if row["request"]["messages"] != [{"role": "user", "content": row["prompt"]}]:
            raise ValueError("mensajes no corresponden al prompt público")
        if row["request"]["options"]["seed"] != 42 + row["sample_index"]:
            raise ValueError("semilla inconsistente")
        if type(row["result"].get("done")) is not bool or not isinstance(row["result"]["message"]["content"], str):
            raise ValueError("respuesta sin estructura de backend válida")
        seen.add(key)
    if complete and seen != set(expected):
        raise ValueError(f"corrida incompleta: {len(seen)}/{len(expected)}")
    return seen


def run(tasks_path, output, model, samples, max_tokens=1024):
    if samples < 1 or max_tokens < 1:
        raise ValueError("muestras y límite deben ser positivos")
    output.mkdir(parents=True, exist_ok=True)
    tasks = read_rows(tasks_path)
    if not tasks or len({t["id"] for t in tasks}) != len(tasks) or len({t["prompt"] for t in tasks}) != len(tasks):
        raise ValueError("tareas vacías o duplicadas")
    options = {**OPTIONS, "num_predict": max_tokens}
    lock_dir = Path.home() / ".cache" / "challenge-units"
    lock_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    with (lock_dir / "inference.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        tag = next((t for t in api("tags")["models"] if t["name"] == model), None)
        if tag is None:
            raise ValueError("modelo no disponible localmente")
        config = {"model": model, "digest": tag["digest"], "samples": samples,
                  "tasks_sha256": sha256(tasks_path), "options": options, "think": False,
                  "runner_sha256": sha256(Path(__file__)), "backend": api("version")}
        metadata_path = output / "metadata.json"
        if metadata_path.exists():
            metadata = json.loads(metadata_path.read_text())
            if metadata["config"] != config:
                raise ValueError("configuración cambió: crear corrida nueva")
        else:
            evidence = {"config": config, "tag": tag, "show": api("show", {"model": model}),
                        "created_at": datetime.now(UTC).isoformat(), "python": platform.python_version(),
                        "hardware": {name: subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
                                     for name, cmd in {"cpu": ["lscpu"], "ram": ["free", "-b"], "gpu": ["nvidia-smi"]}.items()}}
            with metadata_path.open("x") as stream:
                json.dump(evidence, stream, ensure_ascii=False, indent=2)
            code = output / "code"
            code.mkdir()
            for path in Path(__file__).parent.glob("*.py"):
                (code / path.name).write_bytes(path.read_bytes())
        path = output / "responses.jsonl"
        rows = read_rows(path) if path.exists() else []
        seen = validate_rows(tasks, rows, model, samples, complete=False)
        for row in rows:
            if row["request"]["options"] != {**options, "seed": 42 + row["sample_index"]} or row["request"]["think"] is not False:
                raise ValueError("parámetros históricos inconsistentes")
        with path.open("a", encoding="utf-8") as stream:
            for task in tasks:
                for index in range(samples):
                    if (task["id"], index) in seen:
                        continue
                    request = {"model": model, "messages": [{"role": "user", "content": task["prompt"]}],
                               "stream": False, "think": False, "keep_alive": "5m", "options": {**options, "seed": 42 + index}}
                    start = time.monotonic()
                    result = api("chat", request)
                    elapsed = time.monotonic() - start
                    try:
                        memory = api("ps")
                    except (OSError, ValueError) as exc:
                        memory = {"unavailable": str(exc)}
                    row = {"task_id": task["id"], "sample_index": index, "model": model, "prompt": task["prompt"],
                           "request": request, "result": result, "seconds": elapsed,
                           "memory": memory, "created_at": datetime.now(UTC).isoformat()}
                    stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
                    stream.flush()
                    os.fsync(stream.fileno())
                    validate_rows([task], [row], model, samples, complete=False)
                    print(task["id"], index, result.get("eval_count"), result.get("done_reason"), round(row["seconds"], 2), flush=True)
        api("generate", {"model": model, "keep_alive": 0})
    validate_rows(tasks, read_rows(path), model, samples)

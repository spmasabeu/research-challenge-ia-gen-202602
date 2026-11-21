"""OpenRouter/DeepSeek del desafío: presupuesto USD5, sin modificar el evaluador."""

import argparse
import fcntl
import json
import math
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from .evaluate import summarize
from .models import read_rows, sha256
from .verifier import VERSION

MODEL = "deepseek/deepseek-v4-pro-0813"
PARAMETERS = {"model": MODEL, "temperature": .7, "top_p": .9, "max_tokens": 1024, "top_k": 40, "min_p": 0,
              "reasoning": {"enabled": False}, "stream": False, "usage": {"include": True},
              "provider": {"only": ["deepinfra"], "allow_fallbacks": False, "require_parameters": True,
                           "max_price": {"prompt": 1.32, "completion": 3.96}}}
BUDGET = 5
RESERVATION = .02


def append(path, row):
    with path.open("a") as stream:
        stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def api(path, key, payload=None):
    request = urllib.request.Request("https://openrouter.ai/api/v1/" + path,
                                     data=json.dumps(payload).encode() if payload is not None else None,
                                     headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    # El prefijo HTTPS y el host son fijos.
    with urllib.request.urlopen(request, timeout=180) as response:  # nosec B310
        return json.load(response)


def validate(tasks, rows, samples):
    expected = {(t["id"], i): t for t in tasks for i in range(samples)}
    seen = set()
    for row in rows:
        key = row["task_id"], row["sample_index"]
        if key in seen or key not in expected or row["model"] != MODEL:
            raise ValueError("clave/modelo externo inconsistente")
        prompt = expected[key]["prompt"]
        if row["prompt"] != prompt or row["request"] != {**PARAMETERS, "seed": 42 + row["sample_index"], "messages": [{"role": "user", "content": prompt}]}:
            raise ValueError("prompt/parámetros externos inconsistentes")
        result = row["result"]
        if result.get("model") not in {MODEL, "deepseek/deepseek-v4-pro-20260813"} or result.get("provider", "").lower() != "deepinfra":
            raise ValueError("modelo/proveedor efectivo no corresponde al fijado")
        cost = result.get("usage", {}).get("cost")
        if not isinstance(cost, (int, float)) or not math.isfinite(cost) or not 0 <= cost <= RESERVATION:
            raise ValueError("costo ausente o fuera de reserva; revisar respuesta antes de continuar")
        seen.add(key)
    return seen


def run(tasks_path, output, samples, env_file, ledger):
    if samples not in (1, 3):
        raise ValueError("solo controles n1 o test n3")
    tasks = read_rows(tasks_path)
    if not tasks or len({t["id"] for t in tasks}) != len(tasks) or any(len(t["prompt"].encode()) > 2048 for t in tasks):
        raise ValueError("tareas vacías/duplicadas o prompt sobre límite de reserva")
    # 6144 tokens de entrada conservadores + 1024 salida a caps cuestan < USD0,02.
    assert (6144 * 1.32 + 1024 * 3.96) / 1_000_000 < RESERVATION
    key = ""
    for line in env_file.read_text().splitlines():
        name, separator, value = line.strip().partition("=")
        if separator and name == "OPENROUTER_API_KEY":
            key = value.strip().strip("\"'")
    if not key:
        raise ValueError("OPENROUTER_API_KEY no disponible")
    output.mkdir(parents=True, exist_ok=True)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.with_suffix(".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        config = {"model": MODEL, "samples": samples, "tasks_sha256": sha256(tasks_path),
                  "parameters": PARAMETERS, "runner_sha256": sha256(Path(__file__)),
                  "budget_usd": BUDGET, "reservation_per_attempt_usd": RESERVATION,
                  "seed_base": 42, "ledger_path": str(ledger.resolve())}
        metadata = output / "metadata.json"
        if metadata.exists():
            if json.loads(metadata.read_text())["config"] != config:
                raise ValueError("configuración externa cambió; crear corrida nueva")
        else:
            limits = api("key", key)["data"]
            metadata.write_text(json.dumps({"config": config, "created_unix": time.time(),
                                            "key_limits": {k: limits.get(k) for k in ("limit", "limit_remaining", "usage")}}, indent=2) + "\n")
            (output / "runner.py").write_bytes(Path(__file__).read_bytes())
        response_path = output / "responses.jsonl"
        rows = read_rows(response_path) if response_path.exists() else []
        seen = validate(tasks, rows, samples)
        for task in tasks:
            for index in range(samples):
                if (task["id"], index) in seen:
                    continue
                attempts = read_rows(ledger) if ledger.exists() else []
                if (len(attempts) + 1) * RESERVATION > BUDGET:
                    raise ValueError("presupuesto reservado agotado; no se envía solicitud")
                payload = {**PARAMETERS, "seed": 42 + index, "messages": [{"role": "user", "content": task["prompt"]}]}
                append(ledger, {"task_id": task["id"], "sample_index": index, "reserved_usd": RESERVATION,
                                "request": payload, "sent_unix": time.time()})
                start = time.monotonic()
                try:
                    result = api("chat/completions", key, payload)
                except urllib.error.HTTPError as error:
                    append(output / "errors.jsonl", {"task_id": task["id"], "sample_index": index,
                                                    "http_status": error.code, "body": error.read().decode(errors="replace").replace(key, "[redacted]")})
                    raise RuntimeError(f"OpenRouter HTTP{error.code}; respuesta preservada, sin reintento automático") from None
                row = {"task_id": task["id"], "sample_index": index, "model": MODEL, "prompt": task["prompt"],
                       "request": payload, "result": result, "seconds": time.monotonic() - start}
                if key in json.dumps(row):
                    raise ValueError("respuesta contiene credencial; no se guarda")
                append(response_path, row)
                validate(tasks, [row], samples)
                print(task["id"], index, result["usage"].get("completion_tokens"), result["usage"]["cost"], flush=True)


def score(tasks_path, run_dir, output):
    tasks = read_rows(tasks_path)
    rows = read_rows(run_dir / "responses.jsonl")
    config = json.loads((run_dir / "metadata.json").read_text())["config"]
    if config["tasks_sha256"] != sha256(tasks_path) or config["parameters"] != PARAMETERS or config["runner_sha256"] != sha256(run_dir / "runner.py"):
        raise ValueError("fuentes/configuración externa inconsistentes")
    if len(validate(tasks, rows, config["samples"])) != len(tasks) * config["samples"]:
        raise ValueError("corrida externa incompleta")
    normalized = []
    for row in rows:
        choices = row["result"].get("choices", [])
        choice = choices[0] if len(choices) == 1 else {}
        content = choice.get("message", {}).get("content") or ""
        done = choice.get("finish_reason") in {"stop", "length"} and isinstance(content, str)
        normalized.append({"task_id": row["task_id"], "sample_index": row["sample_index"],
                           "result": {"message": {"content": content if isinstance(content, str) else ""},
                                      "done": done, "done_reason": choice.get("finish_reason")}})
    labels, summary = summarize(tasks, normalized)
    output.mkdir(parents=True, exist_ok=False)
    for label in labels:
        append(output / "labels.jsonl", label)
    (output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    (output / "metadata.json").write_text(json.dumps({"verifier_version": VERSION,
        "verifier_sha256": sha256(Path(__file__).with_name("verifier.py")),
        "metrics_sha256": sha256(Path(__file__).with_name("evaluate.py")),
        "adapter_sha256": sha256(Path(__file__)), "tasks_sha256": sha256(tasks_path),
        "responses_sha256": sha256(run_dir / "responses.jsonl"),
        "cost_usd": sum(r["result"]["usage"]["cost"] for r in rows),
        "seconds": sum(r["seconds"] for r in rows)}, indent=2) + "\n")
    return summary["all"]


def main():
    parser = argparse.ArgumentParser(__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    runner = sub.add_parser("run")
    runner.add_argument("--tasks", type=Path, required=True)
    runner.add_argument("--out", type=Path, required=True)
    runner.add_argument("--samples", type=int, required=True)
    runner.add_argument("--env-file", type=Path, required=True)
    runner.add_argument("--ledger", type=Path, required=True)
    scorer = sub.add_parser("score")
    scorer.add_argument("--tasks", type=Path, required=True)
    scorer.add_argument("--run", type=Path, required=True)
    scorer.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "run":
        run(args.tasks, args.out, args.samples, args.env_file, args.ledger)
    else:
        print(json.dumps(score(args.tasks, args.run, args.out)))


if __name__ == "__main__":
    main()

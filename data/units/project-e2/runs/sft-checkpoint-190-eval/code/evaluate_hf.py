"""Inferencia Transformers local y evaluación común, con crudos propios del backend."""

import argparse
import fcntl
import importlib.metadata
import json
import os
import platform
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

from .evaluate import summarize
from .generator import dump
from .models import read_rows, sha256
from .verifier import VERSION, load_tasks

PACKAGES = ("torch", "transformers", "trl", "peft", "accelerate", "datasets", "bitsandbytes")


def write_json(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, ensure_ascii=False, allow_nan=False, indent=2)
        stream.write("\n")


def file_hashes(root):
    return {str(p.relative_to(root)): sha256(p) for p in sorted(root.rglob("*")) if p.is_file()}


def provenance():
    return {"created_at": datetime.now(UTC).isoformat(),
            "versions": {p: importlib.metadata.version(p) for p in PACKAGES},
            "python": platform.python_version(), "verifier": VERSION,
            "code": {p.name: sha256(p) for p in sorted(Path(__file__).parent.glob("*.py"))},
            "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
            "git_status": subprocess.check_output(["git", "status", "--short"], text=True),
            "gpu": subprocess.check_output(["nvidia-smi"], text=True)}


def load_model(config, adapter=None, trainable=False):
    import torch
    from peft import (
        PeftModel,
        get_peft_model_state_dict,
        prepare_model_for_kbit_training,
    )
    from safetensors.torch import load_file
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    if not torch.cuda.is_available():
        raise RuntimeError("se requiere GPU CUDA real")
    if len(config["revision"]) != 40:
        raise ValueError("fijar revisión inmutable de Hugging Face")
    if config["quantization"] not in {"nf4", "none"}:
        raise ValueError("cuantización desconocida")
    tokenizer = AutoTokenizer.from_pretrained(config["model"], revision=config["revision"])
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    quantization = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                     bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16)
    model = AutoModelForCausalLM.from_pretrained(
        config["model"], revision=config["revision"], dtype=torch.bfloat16,
        quantization_config=quantization if config["quantization"] == "nf4" else None,
        device_map={"": 0}, attn_implementation="sdpa")
    if trainable and config["quantization"] == "nf4":
        model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    if adapter is not None:
        model = PeftModel.from_pretrained(model, str(adapter), is_trainable=trainable)
        saved = load_file(str(adapter / "adapter_model.safetensors"))
        loaded = get_peft_model_state_dict(model)
        if saved.keys() != loaded.keys() or any(not torch.equal(v.cpu(), saved[k]) for k, v in loaded.items()):
            raise ValueError("pesos del adaptador no coinciden después de recarga")
    model.config.use_cache = not trainable
    return model, tokenizer


def render_prompt(tokenizer, prompt):
    return tokenizer.apply_chat_template([{"role": "user", "content": prompt}], tokenize=False,
                                         add_generation_prompt=True, enable_thinking=False)


def trim_generated(ids, eos_ids):
    stops = {eos_ids} if isinstance(eos_ids, int) else set(eos_ids)
    for index, token in enumerate(ids):
        if token in stops:
            return ids[:index + 1], "eos"
    return ids, "length"


def validate_hf_rows(tasks, rows, config, complete=True):
    expected = {(t["id"], i): t["prompt"] for t in tasks for i in range(config["samples"])}
    seen = set()
    for row in rows:
        key = row["task_id"], row["sample_index"]
        if key in seen or key not in expected or row["prompt"] != expected[key]:
            raise ValueError("clave o prompt HF inconsistente")
        if row["backend"] != "transformers" or row["model"] != config["model"] or row["seed"] != 42 + key[1]:
            raise ValueError("modelo, backend o semilla HF inconsistente")
        if row["finish_reason"] not in {"eos", "length"} or not isinstance(row["completion"], str):
            raise ValueError("respuesta HF inválida")
        if row["generation"] != config["generation"] or row["input_tokens"] + row["output_tokens"] > config["max_context"]:
            raise ValueError("parámetros o longitud HF inconsistentes")
        seen.add(key)
    if complete and seen != set(expected):
        raise ValueError(f"corrida HF incompleta: {len(seen)}/{len(expected)}")
    return seen


def score(tasks_path, output):
    tasks = read_rows(tasks_path)
    load_tasks(tasks)
    config = json.loads((output / "metadata.json").read_text())["config"]
    if config["tasks_sha256"] != sha256(tasks_path):
        raise ValueError("tareas cambiaron")
    rows = read_rows(output / "responses.jsonl")
    validate_hf_rows(tasks, rows, config)
    labels, summary = summarize(tasks, rows)
    scores = output / "scores" / VERSION
    metadata = {"tasks_sha256": sha256(tasks_path), "responses_sha256": sha256(output / "responses.jsonl"),
                "verifier_sha256": sha256(Path(__file__).with_name("verifier.py")),
                "metrics_sha256": sha256(Path(__file__).with_name("evaluate.py"))}
    if scores.exists():
        if (read_rows(scores / "labels.jsonl") != labels or json.loads((scores / "summary.json").read_text()) != summary
                or json.loads((scores / "metadata.json").read_text()) != metadata):
            raise ValueError("evaluación guardada no reproducible")
        return summary
    scores.mkdir(parents=True, exist_ok=False)
    dump(scores / "labels.jsonl", labels)
    write_json(scores / "summary.json", summary)
    write_json(scores / "metadata.json", metadata)
    print(json.dumps(summary["all"]), flush=True)
    return summary


def run(tasks_path, output, config, adapter=None):
    import torch
    from transformers import set_seed

    if tasks_path.name == "test.jsonl":
        raise ValueError("test reservado para cierre; no se evalúa en E2")
    tasks = read_rows(tasks_path)
    load_tasks(tasks)
    if not tasks or len({t["id"] for t in tasks}) != len(tasks) or config["samples"] < 1 or config.get("batch_size", 1) < 1:
        raise ValueError("tareas vacías/duplicadas o muestras inválidas")
    config = {**config, "tasks_sha256": sha256(tasks_path),
              "adapter": file_hashes(adapter) if adapter else None,
              "runner_sha256": sha256(Path(__file__))}
    output.mkdir(parents=True, exist_ok=True)
    with (output / ".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        metadata = output / "metadata.json"
        if metadata.exists():
            previous = json.loads(metadata.read_text())
            if previous["config"] != config or previous["versions"] != {p: importlib.metadata.version(p) for p in PACKAGES}:
                raise ValueError("configuración HF cambió; crear corrida nueva")
        else:
            write_json(metadata, {"config": config, **provenance()})
            (output / "code").mkdir()
            for p in Path(__file__).parent.glob("*.py"):
                (output / "code" / p.name).write_bytes(p.read_bytes())
        path = output / "responses.jsonl"
        rows = read_rows(path) if path.exists() else []
        seen = validate_hf_rows(tasks, rows, config, complete=False)
        if len(seen) == len(tasks) * config["samples"]:
            return score(tasks_path, output)
        model, tokenizer = load_model(config, adapter)
        model.eval()
        torch.cuda.reset_peak_memory_stats()
        with path.open("a") as stream, (output / "batches.jsonl").open("a") as batches:
            size = config.get("batch_size", 1)
            for offset in range(0, len(tasks), size):
                chunk = tasks[offset:offset + size]
                rendered = [render_prompt(tokenizer, task["prompt"]) for task in chunk]
                for index in range(config["samples"]):
                    if all((task["id"], index) in seen for task in chunk):
                        continue
                    # Repetir el lote original al reanudar conserva el consumo de RNG.
                    inputs = tokenizer(rendered, return_tensors="pt", padding=True, add_special_tokens=False).to(model.device)
                    n = inputs.input_ids.shape[1]
                    if n + config["generation"]["max_new_tokens"] > config["max_context"]:
                        raise ValueError("prompt excede contexto; no truncar datos del problema")
                    set_seed(42 + index)
                    torch.cuda.synchronize()
                    start = time.monotonic()
                    with torch.inference_mode():
                        generated = model.generate(**inputs, **config["generation"],
                                                   pad_token_id=tokenizer.pad_token_id)[:, n:].tolist()
                    torch.cuda.synchronize()
                    elapsed = time.monotonic() - start
                    batches.write(json.dumps({"offset": offset, "sample_index": index, "size": len(chunk),
                                  "seconds": elapsed, "new_rows": sum((t["id"], index) not in seen for t in chunk)}) + "\n")
                    batches.flush()
                    os.fsync(batches.fileno())
                    for position, (task, ids) in enumerate(zip(chunk, generated)):
                        if (task["id"], index) in seen:
                            continue
                        ids, finish_reason = trim_generated(ids, model.generation_config.eos_token_id)
                        row = {"backend": "transformers", "model": config["model"], "task_id": task["id"],
                               "prompt": task["prompt"], "rendered_prompt": rendered[position], "sample_index": index,
                               "seed": 42 + index, "generation": config["generation"],
                               "completion": tokenizer.decode(ids, skip_special_tokens=True),
                               "input_tokens": int(inputs.attention_mask[position].sum()), "output_tokens": len(ids),
                               "seconds": elapsed / len(chunk), "batch_offset": offset, "batch_size": len(chunk),
                               "finish_reason": finish_reason, "eos_token_ids": model.generation_config.eos_token_id,
                               "peak_allocated_bytes": torch.cuda.max_memory_allocated()}
                        stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
                    stream.flush()
                    os.fsync(stream.fileno())
                    print("batch", offset, index, len(chunk), round(elapsed, 2), flush=True)
        return score(tasks_path, output)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--tasks", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--adapter", type=Path)
    parser.add_argument("--score-only", action="store_true")
    args = parser.parse_args()
    if args.score_only:
        score(args.tasks, args.out)
    elif args.config:
        run(args.tasks, args.out, json.loads(args.config.read_text()), args.adapter)
    else:
        parser.error("--config requerido para inferencia")


if __name__ == "__main__":
    main()

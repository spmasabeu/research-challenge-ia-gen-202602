"""Datos derivados de train, con procedencia y auditoría contextual obligatoria."""

import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

from .evaluate import summarize
from .models import read_rows, sha256, validate_rows
from .verifier import VERSION, verify


def collect(tasks, rows, run_name):
    """Deduplicar solo diferencias de espacios; conservar todos los orígenes."""
    labels, summary = summarize(tasks, rows)
    by_id = {t["id"]: t for t in tasks}
    records = {}
    for row, label in zip(rows, labels):
        task = by_id[row["task_id"]]
        completion = row["result"]["message"]["content"]
        canonical = " ".join(completion.split())
        key = (task["id"], canonical, label["status"])
        source = {"run": run_name, "model": row["model"], "sample_index": row["sample_index"],
                  "completion_sha256": hashlib.sha256(completion.encode()).hexdigest()}
        if key in records:
            records[key]["sources"].append(source)
            continue
        records[key] = {"candidate_id": hashlib.sha256("\0".join(key).encode()).hexdigest(),
                        "task_id": task["id"], "family": task["family"], "level": task["level"],
                        "prompt": task["prompt"], "completion": completion, "status": label["status"],
                        "reference_si": task["answer_si"], "sources": [source]}
    return list(records.values()), summary


def required_audits(records):
    """Misma semilla4303 por celda; selección independiente de celdas no terminadas."""
    cells = defaultdict(list)
    for record in records:
        if record["status"] == "correct":
            cells[record["family"], record["level"]].append(record)
    required = set()
    for cell in cells.values():
        cell.sort(key=lambda r: (r["task_id"], r["sources"][0]["sample_index"], r["candidate_id"]))
        required.update(r["candidate_id"] for r in random.Random(4303).sample(cell, min(5, len(cell))))
    return required


def checked_run(tasks_path, run_dir, protocol, models):
    tasks = read_rows(tasks_path)
    rows = read_rows(run_dir / "responses.jsonl")
    metadata = json.loads((run_dir / "metadata.json").read_text())
    config = metadata["config"]
    if config["tasks_sha256"] != sha256(tasks_path) or config["digest"] != models[config["model"]]["digest"]:
        raise ValueError("tareas o revisión de modelo inconsistentes")
    if config["options"] != protocol["options"] or config["think"] != protocol["think"]:
        raise ValueError("parámetros no coinciden con protocolo congelado")
    validate_rows(tasks, rows, config["model"], config["samples"])
    for row in rows:
        if row["request"]["options"] != {**config["options"], "seed": protocol["seed_base"] + row["sample_index"]} or row["request"]["model"] != config["model"] or row["request"]["think"] != config["think"]:
            raise ValueError("parámetros de fila inconsistentes")
    return tasks, rows, config


def build(dataset, teacher_run, audit_paths, negative_tasks=None, negative_run=None):
    protocol = json.loads((dataset / "protocol.json").read_text())
    models = json.loads((dataset / "models.json").read_text())
    train_path = dataset / "private/train.jsonl"
    tasks, teacher_rows, config = checked_run(train_path, teacher_run, protocol, models)
    train_by_id = {t["id"]: t for t in tasks}
    if config["model"] != "qwen3:8b" or not 4 <= config["samples"] <= 8:
        raise ValueError("profesor debe ser Qwen3-8B con4–8muestras")
    teacher, teacher_summary = collect(tasks, teacher_rows, teacher_run.name)
    candidates = {r["candidate_id"]: r for r in teacher if r["status"] == "correct"}
    audits = {}
    audit_sources = {}
    for path in sorted(audit_paths, key=lambda p: p.name):
        if path.name in audit_sources:
            raise ValueError("nombres de auditoría duplicados")
        audit_sources[path.name] = sha256(path)
        for audit in read_rows(path):
            candidate = candidates.get(audit["candidate_id"])
            if candidate is None or audit["candidate_id"] in audits or audit["judgment"] not in {"keep", "reject", "uncertain"}:
                raise ValueError("auditoría inválida, duplicada o ajena a candidatas correctas")
            if audit["completion_sha256"] != candidate["sources"][0]["completion_sha256"] or not audit["reason"].strip():
                raise ValueError("auditoría sin evidencia correspondiente")
            audits[audit["candidate_id"]] = audit
    if not required_audits(teacher) <= audits.keys():
        raise ValueError("faltan auditorías muestreadas por celda")
    affected = {(candidates[key]["family"], candidates[key]["level"]) for key, audit in audits.items() if audit["judgment"] != "keep"}
    if any(r["candidate_id"] not in audits for r in candidates.values() if (r["family"], r["level"]) in affected):
        raise ValueError("defecto encontrado: ampliar revisión a toda la celda")
    preferred = [r for r in candidates.values() if r["candidate_id"] not in audits or audits[r["candidate_id"]]["judgment"] == "keep"]
    rejected = [r for r in teacher if r["status"] in {"numeric", "unit"}]
    input_hashes = {"train": sha256(train_path), "teacher_metadata": sha256(teacher_run / "metadata.json"),
                    "teacher_responses": sha256(teacher_run / "responses.jsonl"), "audits": audit_sources}
    negative_summary = None
    if (negative_tasks is None) != (negative_run is None):
        raise ValueError("indicar tareas y corrida de negativos juntas")
    if negative_run is not None:
        subset, rows, negative_config = checked_run(negative_tasks, negative_run, protocol, models)
        if negative_config["model"] == "qwen3:8b" or negative_config["samples"] > 3:
            raise ValueError("negativos adicionales: modelo pequeño y máximo3muestras")
        if any(t != train_by_id.get(t["id"]) for t in subset):
            raise ValueError("negativos fuera de train o con prompt diferente")
        negatives, negative_summary = collect(subset, rows, negative_run.name)
        rejected.extend(r for r in negatives if r["status"] in {"numeric", "unit"})
        input_hashes.update({"negative_tasks": sha256(negative_tasks), "negative_metadata": sha256(negative_run / "metadata.json"), "negative_responses": sha256(negative_run / "responses.jsonl")})
    verifier = {"version": VERSION, "sha256": sha256(Path(__file__).with_name("verifier.py"))}
    sft = [{"task_id": r["task_id"], "prompt": r["prompt"], "completion": r["completion"],
            "metadata": {"candidate_id": r["candidate_id"], "family": r["family"], "level": r["level"],
                         "sources": r["sources"], "verifier": verifier, "audited": r["candidate_id"] in audits}}
           for r in preferred]
    correct_by_task, wrong_by_task = defaultdict(list), defaultdict(list)
    for record in preferred:
        correct_by_task[record["task_id"]].append(record)
    unique_wrong = {}
    for record in rejected:
        key = record["task_id"], " ".join(record["completion"].split())
        if key in unique_wrong:
            unique_wrong[key]["sources"].extend(record["sources"])
        else:
            unique_wrong[key] = record
    for record in unique_wrong.values():
        wrong_by_task[record["task_id"]].append(record)
    dpo = []
    for task in tasks:
        correct = sorted(correct_by_task[task["id"]], key=lambda r: (r["sources"][0]["sample_index"], r["candidate_id"]))
        wrong = wrong_by_task[task["id"]]
        for chosen, rejected in zip(correct[:2], wrong[:2]):
            dpo.append({"task_id": task["id"], "prompt": task["prompt"], "chosen": chosen["completion"], "rejected": rejected["completion"],
                        "metadata": {"family": task["family"], "level": task["level"], "verifier": verifier,
                                     "chosen_sources": chosen["sources"], "rejected_sources": rejected["sources"],
                                     "chosen_candidate_id": chosen["candidate_id"], "rejected_status": rejected["status"]}})
    for row in sft:
        if verify(train_by_id[row["task_id"]], row["completion"])["reward"] != 1:
            raise ValueError("SFT inválido")
    for row in dpo:
        task = train_by_id[row["task_id"]]
        if verify(task, row["chosen"])["reward"] != 1 or verify(task, row["rejected"])["status"] not in {"numeric", "unit"}:
            raise ValueError("par DPO inválido")
    if not sft or not dpo or {r["metadata"]["level"] for r in sft} != {"easy", "medium", "hard"} or {r["metadata"]["level"] for r in dpo} != {"easy", "medium", "hard"}:
        raise ValueError("faltan datos utilizables SFT/DPO en alguna dificultad")
    stats = {"teacher": teacher_summary, "negative_model": negative_summary, "teacher_unique_responses": len(teacher),
             "correct_unique_before_audit": len(candidates), "audited": len(audits), "audit_rejected": sum(a["judgment"] != "keep" for a in audits.values()),
             "expanded_cells": ["/".join(cell) for cell in sorted(affected)],
             "sft": len(sft), "dpo": len(dpo), "sft_tasks": len({r["task_id"] for r in sft}), "dpo_tasks": len({r["task_id"] for r in dpo}),
             "dpo_max_pairs_per_task": max(Counter(r["task_id"] for r in dpo).values(), default=0),
             "dpo_reused_chosen": sum(n - 1 for n in Counter((r["task_id"], r["chosen"]) for r in dpo).values()),
             "dpo_reused_rejected": sum(n - 1 for n in Counter((r["task_id"], r["rejected"]) for r in dpo).values()),
             "sft_by_cell": dict(Counter(f'{r["metadata"]["family"]}/{r["metadata"]["level"]}' for r in sft)),
             "dpo_by_cell": dict(Counter(f'{r["metadata"]["family"]}/{r["metadata"]["level"]}' for r in dpo)),
             "input_hashes": input_hashes, "derive_source_sha256": sha256(Path(__file__)), "verifier": verifier,
             "deduplication": "task+texto sin diferencias de espacios; fuentes repetidas conservadas; emparejar por orden sin producto cartesiano",
             "audit_limit": "Muestra por celda sin defectos no certifica todas las trazas; celdas con defectos revisadas completas."}
    return sft, dpo, stats

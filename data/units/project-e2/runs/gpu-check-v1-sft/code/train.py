"""SFT/GRPO públicos de TRL; QLoRA local, evidencia de actualización y checkpoints."""

import argparse
import json
import math
import os
import time
from pathlib import Path

from .evaluate_hf import file_hashes, load_model, provenance, render_prompt, write_json
from .models import read_rows, sha256
from .verifier import load_tasks, reward, verify


def validate_sft(tasks, rows):
    by_id = {t["id"]: t for t in tasks}
    seen = set()
    for row in rows:
        task = by_id.get(row["task_id"])
        key = row["task_id"], " ".join(row["completion"].split())
        if task is None or row["prompt"] != task["prompt"] or key in seen:
            raise ValueError("SFT duplicado o ajeno a train")
        if verify(task, row["completion"])["reward"] != 1:
            raise ValueError("SFT no aprobado por verificador vigente")
        seen.add(key)
    if not rows:
        raise ValueError("SFT vacío")


def tokenize_sft(tokenizer, rows, max_length):
    result = []
    for row in rows:
        prompt = render_prompt(tokenizer, row["prompt"])
        prefix = tokenizer.encode(prompt, add_special_tokens=False)
        ids = tokenizer.encode(prompt + row["completion"] + tokenizer.eos_token, add_special_tokens=False)
        if ids[:len(prefix)] != prefix or len(ids) <= len(prefix):
            raise ValueError("template no conserva prefijo o respuesta vacía")
        if len(ids) > max_length:
            raise ValueError("traza SFT excede max_length; no entrenar una conclusión truncada")
        result.append({"input_ids": ids, "completion_mask": [0] * len(prefix) + [1] * (len(ids) - len(prefix))})
    return result


def grpo_rewards(prompts, completions, prompt_map):
    if len(prompts) != len(completions):
        raise ValueError("lotes de recompensa desalineados")
    return [reward(prompt_map[p], c) for p, c in zip(prompts, completions)]


def check_resume(output, signature, checkpoint):
    previous = json.loads((output / "metadata.json").read_text())["signature"]
    if previous != signature or checkpoint.parent.resolve() != output.resolve():
        raise ValueError("reanudación con configuración/datos/checkpoint incompatibles")
    for name in ("optimizer.pt", "scheduler.pt", "rng_state.pth", "trainer_state.json", "cost.json"):
        if not (checkpoint / name).is_file():
            raise ValueError(f"checkpoint sin estado de reanudación: {name}")
    evidence = json.loads((checkpoint / "cost.json").read_text())
    for name, digest in evidence["files"].items():
        if sha256(checkpoint / name) != digest:
            raise ValueError("checkpoint modificado")
    return evidence


def run(config, tasks_path, output, sft_path=None, initial_adapter=None, resume=None, pilot=False):
    import torch
    from datasets import Dataset
    from peft import (
        LoraConfig,
        get_peft_model,
        get_peft_model_state_dict,
        set_peft_model_state_dict,
    )
    from safetensors.torch import load_file
    from transformers import TrainerCallback, set_seed
    from trl import GRPOConfig, GRPOTrainer, SFTConfig, SFTTrainer

    class LocalGRPOTrainer(GRPOTrainer):
        def _generate_single_turn(self, *args, **kwargs):
            # TRL 0.24 genera fuera de training_step; no extender la caché autocast entre actualizaciones.
            with torch.autocast("cuda", dtype=torch.bfloat16):
                return super()._generate_single_turn(*args, **kwargs)

    if tasks_path.name == "test.jsonl" or (not pilot and tasks_path.name != "train.jsonl"):
        raise ValueError("entrenar exclusivamente sobre train")
    if not pilot:
        from .harness import check_dataset
        check_dataset(tasks_path.parent.parent)
    tasks = read_rows(tasks_path)
    load_tasks(tasks)
    if not tasks or config["max_steps"] < 1 or config["budget_seconds"] <= 0:
        raise ValueError("tareas o presupuesto inválidos")
    if config["method"] not in {"sft", "grpo"}:
        raise ValueError("método desconocido")
    prior_seconds = 0.0
    if initial_adapter:
        parent = json.loads((initial_adapter / "cost.json").read_text())
        prior_seconds = parent["cumulative_train_seconds"]
        if parent["method"] != "sft" or parent["model"] != config["model"] or parent["revision"] != config["revision"]:
            raise ValueError("continuación requiere adaptador SFT del mismo checkpoint")
        if parent["tasks_sha256"] != sha256(tasks_path) or parent["quantization"] != config["quantization"]:
            raise ValueError("continuación con datos o precisión diferente")
        for name, digest in parent["files"].items():
            if sha256(initial_adapter / name) != digest:
                raise ValueError("adaptador SFT modificado")
    evidence = provenance()
    signature = {"config": config, "tasks_sha256": sha256(tasks_path), "pilot": pilot,
                 "sft_sha256": sha256(sft_path) if sft_path else None,
                 "initial_adapter": file_hashes(initial_adapter) if initial_adapter else None,
                 "code": evidence["code"], "versions": evidence["versions"]}
    previous_seconds = 0.0
    if resume:
        previous_seconds = check_resume(output, signature, resume)["phase_train_seconds"]
    else:
        output.mkdir(parents=True, exist_ok=False)
        write_json(output / "metadata.json", {"signature": signature, "prior_train_seconds": prior_seconds,
                   "reference_policy": "beta=0; sin modelo de referencia ni KL; optimizador nuevo entre fases", **evidence})
        (output / "code").mkdir()
        for p in Path(__file__).parent.glob("*.py"):
            (output / "code" / p.name).write_bytes(p.read_bytes())
    set_seed(config["seed"])
    model, tokenizer = load_model(config, initial_adapter, trainable=True)
    if not initial_adapter:
        model = get_peft_model(model, LoraConfig(r=config["lora_rank"], lora_alpha=2 * config["lora_rank"],
                    target_modules=["q_proj", "v_proj"], lora_dropout=0, bias="none", task_type="CAUSAL_LM"))
    if resume:
        set_peft_model_state_dict(model, load_file(str(resume / "adapter_model.safetensors")))
    common = {"output_dir": str(output), "per_device_train_batch_size": 1,
              "gradient_accumulation_steps": config["group_size"], "learning_rate": config["learning_rate"],
              "max_steps": config["max_steps"], "logging_steps": 1, "save_steps": config["save_steps"],
              "save_total_limit": None, "save_only_model": False, "report_to": "none", "bf16": True,
              "gradient_checkpointing": True, "gradient_checkpointing_kwargs": {"use_reentrant": False},
              "seed": config["seed"], "data_seed": config["seed"], "optim": "adamw_torch", "lr_scheduler_type": "constant",
              "warmup_steps": 0, "dataloader_num_workers": 0, "disable_tqdm": True}
    start = time.monotonic()

    def elapsed():
        return previous_seconds + time.monotonic() - start

    def cost(path, step, seconds=None):
        seconds = elapsed() if seconds is None else seconds
        write_json(path / "cost.json", {"method": config["method"], "model": config["model"],
                   "revision": config["revision"], "quantization": config["quantization"],
                   "tasks_sha256": sha256(tasks_path), "step": step,
                   "phase_train_seconds": seconds, "prior_train_seconds": prior_seconds,
                   "cumulative_train_seconds": prior_seconds + seconds, "files": file_hashes(path)})

    class EvidenceCallback(TrainerCallback):
        def on_log(self, args, state, control, logs=None, **kwargs):
            record = {"step": state.global_step, "phase_train_seconds": elapsed(),
                      "cumulative_train_seconds": prior_seconds + elapsed(), **(logs or {})}
            if any(isinstance(v, (int, float)) and not math.isfinite(v) for v in record.values()):
                raise ValueError("métrica de entrenamiento no finita")
            with (output / "steps.jsonl").open("a") as stream:
                stream.write(json.dumps(record, allow_nan=False) + "\n")
                stream.flush()
                os.fsync(stream.fileno())

        def on_pre_optimizer_step(self, args, state, control, model=None, **kwargs):
            grads = [p.grad for p in model.parameters() if p.requires_grad and p.grad is not None]
            if not grads or any(not torch.isfinite(g).all() for g in grads):
                raise ValueError("gradientes ausentes o no finitos")

        def on_step_end(self, args, state, control, **kwargs):
            if elapsed() >= config["budget_seconds"]:
                control.should_training_stop = True
                control.should_save = True

        def on_save(self, args, state, control, **kwargs):
            cost(output / f"checkpoint-{state.global_step}", state.global_step)

    if config["method"] == "sft":
        if sft_path is None:
            raise ValueError("SFT requiere trazas reales del profesor")
        rows = read_rows(sft_path)
        validate_sft(tasks, rows)
        tokenized = tokenize_sft(tokenizer, rows, config["max_length"])
        trainer = SFTTrainer(model=model, processing_class=tokenizer,
                             args=SFTConfig(**common, max_length=config["max_length"],
                                            completion_only_loss=True, packing=False),
                             train_dataset=Dataset.from_list(tokenized), callbacks=[EvidenceCallback()])
        batch = trainer.data_collator(tokenized[:1])
        mask = tokenized[0]["completion_mask"]
        assert batch["labels"][0][:mask.index(1)].eq(-100).all()
        assert batch["labels"][0][mask.index(1):].ne(-100).all()
        if not resume:
            write_json(output / "mask-check.json", {"prompt_tokens": mask.index(1), "completion_tokens": sum(mask), "passed": True})
    else:
        prompt_map = {render_prompt(tokenizer, t["prompt"]): t["prompt"] for t in tasks}

        def verified_reward(prompts, completions, **kwargs):
            values = grpo_rewards(prompts, completions, prompt_map)
            size = config["group_size"]
            groups = [values[i:i + size] for i in range(0, len(values), size)]
            with (output / "rollouts.jsonl").open("a") as stream:
                stream.write(json.dumps({"phase_train_seconds": elapsed(), "prompts": [prompt_map[p] for p in prompts],
                             "completions": completions, "rewards": values,
                             "groups_mixed": sum(len(set(g)) > 1 for g in groups),
                             "groups_zero": sum(all(v == 0 for v in g) for g in groups),
                             "groups_one": sum(all(v == 1 for v in g) for g in groups)}, ensure_ascii=False) + "\n")
            return values

        trainer = LocalGRPOTrainer(model=model, processing_class=tokenizer, reward_funcs=verified_reward,
                              args=GRPOConfig(**common, num_generations=config["group_size"],
                                     max_prompt_length=config["max_length"] - config["max_completion_length"],
                                     max_completion_length=config["max_completion_length"],
                                     temperature=.7, top_p=.9, top_k=40, beta=0.0, loss_type="grpo",
                                     scale_rewards="group", mask_truncated_completions=True,
                                     use_vllm=False, remove_unused_columns=False),
                              train_dataset=Dataset.from_list([{"prompt": p} for p in prompt_map]),
                              callbacks=[EvidenceCallback()])
        for p in prompt_map:
            if len(tokenizer.encode(p, add_special_tokens=False)) > trainer.args.max_prompt_length:
                raise ValueError("prompt GRPO se truncaría")
    before = {k: v.detach().cpu().clone() for k, v in get_peft_model_state_dict(trainer.model).items()}
    torch.cuda.reset_peak_memory_stats()
    start = time.monotonic()
    trainer.train(resume_from_checkpoint=str(resume) if resume else None)
    torch.cuda.synchronize()
    phase_seconds = elapsed()
    after = {k: v.detach().cpu().clone() for k, v in get_peft_model_state_dict(trainer.model).items()}
    changed = [k for k in before if not torch.equal(before[k], after[k])]
    if any(not torch.isfinite(v).all() for v in after.values()):
        raise ValueError("pesos no finitos")
    final = output / "final"
    trainer.save_model(str(final))
    tokenizer.save_pretrained(final)
    saved = load_file(str(final / "adapter_model.safetensors"))
    assert saved.keys() == after.keys() and all(torch.equal(saved[k], v) for k, v in after.items())
    # Recarga mediante PEFT; comparar logits con el mismo modelo en modo evaluación.
    trainer.model.eval()
    trainer.model.config.use_cache = True
    inputs = tokenizer(render_prompt(tokenizer, tasks[0]["prompt"]), return_tensors="pt").to(model.device)
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        logits_before = trainer.model(**inputs).logits[:, -1, :].float().cpu()
    set_peft_model_state_dict(trainer.model, saved)
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        logits_after = trainer.model(**inputs).logits[:, -1, :].float().cpu()
    assert torch.equal(logits_before, logits_after)
    cost(final, trainer.state.global_step, phase_seconds)
    result = {"method": config["method"], "pilot": pilot, "steps": trainer.state.global_step,
              "changed_tensors": len(changed), "adapter_tensors": len(after),
              "max_parameter_delta": max((after[k].float() - before[k].float()).abs().max().item() for k in before),
              "weights_finite": True, "reload_weights_equal": True, "reload_logits_equal": True,
              "phase_train_seconds": phase_seconds, "prior_train_seconds": prior_seconds,
              "cumulative_train_seconds": prior_seconds + phase_seconds,
              "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
              "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
              "termination": "max_steps" if trainer.state.global_step == config["max_steps"] else "time_budget",
              "adapter_files": file_hashes(final), "initial_adapter": str(initial_adapter) if initial_adapter else None}
    write_json(output / "result.json", result)
    print(json.dumps(result), flush=True)
    if not changed:
        raise RuntimeError("entrenamiento sin actualización de pesos; conservar como intento fallido")
    return result


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--tasks", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--sft", type=Path)
    parser.add_argument("--initial-adapter", type=Path)
    parser.add_argument("--resume", type=Path)
    parser.add_argument("--pilot", action="store_true", help="infraestructura sobre desarrollo; no resultado E2")
    args = parser.parse_args()
    run(json.loads(args.config.read_text()), args.tasks, args.out, args.sft,
        args.initial_adapter, args.resume, args.pilot)


if __name__ == "__main__":
    main()

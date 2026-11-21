"""Integración real local: SFT, reanudación, GRPO y continuación SFT→GRPO."""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from challenge.evaluate_hf import write_json


def check(root, prefix):
    import torch
    from safetensors.torch import load_file

    config = root / "config"
    runs = root / "runs"

    def execute(name, method, extra=()):
        out = runs / f"{prefix}-{name}"
        args = [sys.executable, "-m", "challenge.train", "--config", str(config / method),
                "--tasks", str(config / "smoke-explicit-tasks.jsonl"), "--out", str(out), "--pilot", *map(str, extra)]
        with (root / "validation" / f"{prefix}-{name}.log").open("x") as log:
            subprocess.run(args, env={**os.environ, "PYTHONPATH": "src"}, stdout=log, stderr=subprocess.STDOUT, check=True)
        result = json.loads((out / "result.json").read_text())
        assert result["changed_tensors"] > 0 and result["weights_finite"] and result["reload_logits_equal"]
        return out, result

    sft, sft_result = execute("sft", "smoke-sft.json", ("--sft", config / "smoke-explicit-sft.jsonl"))
    resumed = runs / f"{prefix}-resume"
    resumed.mkdir()
    shutil.copyfile(sft / "metadata.json", resumed / "metadata.json")
    shutil.copytree(sft / "code", resumed / "code")
    shutil.copytree(sft / "checkpoint-1", resumed / "checkpoint-1")
    _, resume_result = execute("resume", "smoke-sft.json", ("--sft", config / "smoke-explicit-sft.jsonl",
                                                          "--resume", resumed / "checkpoint-1"))
    expected = load_file(str(sft / "final/adapter_model.safetensors"))
    actual = load_file(str(resumed / "final/adapter_model.safetensors"))
    assert expected.keys() == actual.keys() and all(torch.equal(expected[k], actual[k]) for k in expected)
    assert sft_result["cumulative_train_tokens"] > 0
    assert resume_result["cumulative_train_tokens"] == sft_result["cumulative_train_tokens"]
    replay_config = config / f"{prefix}-grpo-replay.json"
    write_json(replay_config, {**json.loads((config / "smoke-grpo-signal.json").read_text()),
                               "max_steps": 6, "budget_seconds": 900})
    grpo, grpo_result = execute("grpo", replay_config.name)
    grpo_resumed = runs / f"{prefix}-grpo-resume"
    grpo_resumed.mkdir()
    shutil.copyfile(grpo / "metadata.json", grpo_resumed / "metadata.json")
    shutil.copytree(grpo / "code", grpo_resumed / "code")
    shutil.copytree(grpo / "checkpoint-2", grpo_resumed / "checkpoint-2")
    _, grpo_resume_result = execute("grpo-resume", replay_config.name, ("--resume", grpo_resumed / "checkpoint-2"))
    expected = load_file(str(grpo / "final/adapter_model.safetensors"))
    actual = load_file(str(grpo_resumed / "final/adapter_model.safetensors"))
    assert expected.keys() == actual.keys() and all(torch.equal(expected[k], actual[k]) for k in expected)
    assert grpo_resume_result["cumulative_train_tokens"] == grpo_result["cumulative_train_tokens"]
    hybrid, hybrid_result = execute("sft-grpo", "smoke-grpo-signal.json", ("--initial-adapter", sft / "final"))
    assert hybrid_result["prior_train_seconds"] == sft_result["cumulative_train_seconds"]
    assert hybrid_result["cumulative_train_seconds"] > hybrid_result["phase_train_seconds"]
    assert hybrid_result["prior_train_tokens"] == sft_result["cumulative_train_tokens"]
    assert hybrid_result["cumulative_train_tokens"] == hybrid_result["phase_train_tokens"] + hybrid_result["prior_train_tokens"]
    write_json(root / "validation" / f"{prefix}-gpu.json", {"sft": sft_result, "resume": resume_result,
               "grpo": grpo_result, "grpo_resume": grpo_resume_result, "sft_grpo": hybrid_result,
               "resume_weights_bitwise_equal": True, "grpo_resume_weights_bitwise_equal": True,
               "runs": [str(p) for p in (sft, resumed, grpo, grpo_resumed, hybrid)]})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--root", type=Path, default=Path("data/units/project-e2"))
    parser.add_argument("--prefix", required=True, help="destino nuevo para preservar intentos anteriores")
    args = parser.parse_args()
    check(args.root, args.prefix)

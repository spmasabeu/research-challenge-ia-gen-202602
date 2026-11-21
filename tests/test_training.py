"""Contratos E2 sin descargas ni GPU; integración CUDA mediante challenge.train."""

import json
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from prepare_e2 import audit
from report_training import cumulative_tokens, paired_bootstrap, rollout_summary
from run_e2 import checkpoints_at_fractions, execute, experiment

from challenge.derive import checked_run
from challenge.evaluate import summarize
from challenge.evaluate_hf import trim_generated, validate_hf_rows
from challenge.generator import CATALOG, FAMILIES, generate
from challenge.harness import check_dataset, freeze
from challenge.train import check_resume, grpo_rewards, tokenize_sft, validate_sft
from challenge.verifier import MAX_CHARS, UNITS, extract_answer, load_tasks, verify


class ProjectTests(unittest.TestCase):
    def test_rollout_signal_recomputes_rewards_and_retains_unseen_cells(self):
        tasks = generate(1, 1, families=("speed",))
        task = tasks[0]
        row = {"prompts": [task["prompt"]] * 4,
               "completions": [f'{task["answer_si"]} m/s'] * 2 + ['0 m/s'] * 2,
               "rewards": [1., 1., 0., 0.], "groups_zero": 0, "groups_one": 0, "groups_mixed": 1}
        result = {r["cell"]: r for r in rollout_summary(tasks, [row])}
        self.assertEqual(result['speed/easy']['mean_train_reward'], .5)
        self.assertEqual(result['speed/easy']['groups_mixed'], 1)
        self.assertEqual(result['speed/medium']['groups'], 0)
        self.assertIsNone(result['speed/medium']['mean_train_reward'])
        for bad in ({**row, "groups_mixed": 0}, {**row, "rewards": [1.] * 4}):
            with self.assertRaisesRegex(ValueError, "no reproducible"):
                rollout_summary(tasks, [bad])

    def test_audit_never_overwrites_existing_judgments(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "audit.jsonl"
            text = '{"auditor":"reviewer","reviewer_type":"human","judgment":"reject"}\n'
            path.write_text(text)
            with self.assertRaises(FileExistsError):
                audit(None, None, path)
            self.assertEqual(path.read_text(), text)

    def test_token_cost_preserves_sft_prefix_and_legacy_grpo_state(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            sources = {}
            cost = {"method": "grpo", "prior_train_seconds": 0, "step": 2}
            (path / "cost.json").write_text(json.dumps(cost))
            (path / "trainer_state.json").write_text(json.dumps({"num_input_tokens_seen": 1500}))
            self.assertEqual(cumulative_tokens(path, sources), 1500)
            self.assertEqual(len(sources), 2)
            (path / "cost.json").write_text(json.dumps({**cost, "prior_train_seconds": 10}))
            self.assertIsNone(cumulative_tokens(path, sources))
            (path / "cost.json").write_text(json.dumps({**cost, "prior_train_seconds": 10, "cumulative_train_tokens": 1700}))
            self.assertEqual(cumulative_tokens(path, sources), 1700)
            self.assertEqual(cumulative_tokens(None, sources), 0)

    def test_uncertainty_resamples_physical_blocks_not_answers(self):
        tasks = generate(1, 4, families=("speed",))
        good = {tasks[0]["physical_key"], tasks[3]["physical_key"]}
        base = [{"task_id": t["id"], "sample_index": i, "status": "correct" if t["physical_key"] in good else "numeric"}
                for t in tasks for i in range(3)]
        trained = [{**row, "status": "correct"} for row in base]
        result = paired_bootstrap(tasks, {"control": base, "sft": trained}, repetitions=1000)
        self.assertEqual(result["physical_problems"], 4)
        self.assertEqual(result["routes"]["control"]["pass_at_k"], {"1": .5, "3": .5})
        self.assertEqual(result["routes"]["control"]["ci95"]["1"], [0, 1])
        self.assertEqual(result["routes"]["sft"]["delta_control_ci95"]["1"], [0, 1])
        self.assertNotIn("sft_grpo_minus_grpo", result)
        self.assertEqual(result, paired_bootstrap(tasks, {"control": base, "sft": trained}, repetitions=1000))
        with self.assertRaisesRegex(ValueError, "tres respuestas"):
            paired_bootstrap(tasks, {"control": base[:-1]})

    def test_hybrid_contrast_uses_grpo_and_the_same_bootstrap_draws(self):
        tasks = generate(1, 4, families=("speed",))
        control = [{"task_id": t["id"], "sample_index": i, "status": "correct"}
                   for t in tasks for i in range(3)]
        grpo = [{**r, "status": "correct" if r["sample_index"] == 0 else "numeric"} for r in control]
        hybrid = [{**r, "status": "correct" if r["sample_index"] < 2 else "numeric"} for r in control]
        result = paired_bootstrap(tasks, {"control": control, "grpo": grpo, "sft-grpo": hybrid}, repetitions=100)
        contrast = result["sft_grpo_minus_grpo"]
        self.assertAlmostEqual(contrast["pass_at_k_delta"]["1"], 1 / 3)
        self.assertEqual(contrast["pass_at_k_delta"]["3"], 0)
        for bound in contrast["ci95"]["1"]:
            self.assertAlmostEqual(bound, 1 / 3)
        self.assertEqual(contrast["ci95"]["3"], [0, 0])

    def test_reportable_evaluation_requires_frozen_three_sample_protocol(self):
        from challenge.generator import dump

        with tempfile.TemporaryDirectory() as directory, patch("run_e2.check_dataset"):
            root = Path(directory)
            (root / "dataset/private").mkdir(parents=True)
            (root / "config").mkdir()
            tasks = generate(1, 1)[:1]
            dump(root / "dataset/private/eval.jsonl", tasks)
            dump(root / "config/eval-curves.jsonl", tasks)
            (root / "dataset/models.json").write_text(json.dumps({"fixture": {"evaluation": {"model": "fixture", "samples": 3}}}))
            (root / "config/evaluation.json").write_text(json.dumps({"model": "fixture", "samples": 2}))
            with self.assertRaisesRegex(ValueError, "protocolo congelado"):
                experiment(root, None, "control")

    def test_hf_negative_provenance_rejects_other_revision_or_adapter(self):
        from challenge.generator import dump
        from challenge.models import sha256

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tasks = generate(1, 1, families=("speed",))[:1]
            dump(root / "tasks.jsonl", tasks)
            config = {"model": "Qwen/Qwen3-1.7B", "revision": "a" * 40, "quantization": "nf4", "samples": 1,
                      "generation": {}, "max_context": 2048, "batch_size": 8,
                      "tasks_sha256": sha256(root / "tasks.jsonl"), "adapter": None}
            catalog = {config["model"]: {"backend": "transformers", "evaluation": config.copy()}}
            row = {"backend": "transformers", "model": config["model"], "task_id": tasks[0]["id"],
                   "sample_index": 0, "prompt": tasks[0]["prompt"], "seed": 42, "completion": "0 m/s",
                   "generation": {}, "input_tokens": 10, "output_tokens": 4, "finish_reason": "eos"}
            dump(root / "responses.jsonl", [row])
            (root / "metadata.json").write_text(json.dumps({"config": config}))
            self.assertEqual(checked_run(root / "tasks.jsonl", root, {}, catalog)[1], [row])
            for change in ({"revision": "b" * 40}, {"adapter": {"weights": "unknown"}}):
                (root / "metadata.json").write_text(json.dumps({"config": {**config, **change}}))
                with self.assertRaisesRegex(ValueError, "HF"):
                    checked_run(root / "tasks.jsonl", root, {}, catalog)

    def test_completed_training_reuse_checks_data_and_parent(self):
        from challenge.generator import dump
        from challenge.models import sha256

        with tempfile.TemporaryDirectory() as directory, patch("run_e2.check_dataset"):
            root = Path(directory)
            for name in ("dataset/private", "config", "runs/sft", "derived"):
                (root / name).mkdir(parents=True)
            tasks = generate(1, 1)[:1]
            for name in ("dataset/private/train.jsonl", "dataset/private/eval.jsonl", "config/eval-curves.jsonl"):
                dump(root / name, tasks)
            protocol = {"model": "fixture", "samples": 3}
            (root / "dataset/models.json").write_text(json.dumps({"fixture": {"evaluation": protocol}}))
            (root / "config/evaluation.json").write_text(json.dumps(protocol))
            (root / "config/sft.json").write_text('{"method":"sft"}')
            (root / "derived/sft.jsonl").write_text("fixture")
            (root / "derived/manifest.json").write_text(json.dumps({"sft.jsonl": sha256(root / "derived/sft.jsonl")}))
            signature = {"config": {"method": "sft"}, "pilot": False,
                         "tasks_sha256": sha256(root / "dataset/private/train.jsonl"),
                         "sft_sha256": sha256(root / "derived/sft.jsonl"), "initial_adapter": None}
            from challenge.verifier import VERSION
            (root / "derived/stats.json").write_text(json.dumps({"input_hashes": {"train": signature["tasks_sha256"]},
                                                               "verifier": {"version": VERSION}}))
            (root / "runs/sft/result.json").write_text(json.dumps({"pilot": False, "method": "sft", "changed_tensors": 1}))

            def fake_execute(command, log):
                Path(command[command.index("--out") + 1]).mkdir(exist_ok=True)

            with patch("run_e2.execute", side_effect=fake_execute), patch("run_e2.checkpoints_at_fractions", side_effect=RuntimeError("validated")):
                for key in ("tasks_sha256", "sft_sha256", "initial_adapter", "pilot"):
                    (root / "runs/sft/metadata.json").write_text(json.dumps({"signature": {**signature, key: "changed"}}))
                    with self.subTest(key=key), self.assertRaisesRegex(ValueError, "no válida"):
                        experiment(root, root / "derived", "sft")
                (root / "runs/sft/metadata.json").write_text(json.dumps({"signature": signature}))
                with self.assertRaisesRegex(RuntimeError, "validated"):
                    experiment(root, root / "derived", "sft")

    def test_orchestrator_records_path_arguments_without_losing_command(self):
        with tempfile.TemporaryDirectory() as directory, patch("run_e2.subprocess.run") as run:
            log = Path(directory) / "command.log"
            execute(["-m", "challenge.evaluate_hf", "--tasks", Path("data/tasks.jsonl")], log)
            command = json.loads(log.read_text())["command"]
            self.assertEqual(command[-1], "data/tasks.jsonl")
            self.assertEqual(run.call_args.args[0][1:], command)

    def test_batched_eos_removes_padding_and_accepts_both_qwen_stops(self):
        self.assertEqual(trim_generated([5, 151643, 151645, 151645], [151645, 151643]), ([5, 151643], "eos"))
        self.assertEqual(trim_generated([5, 151645, 151645], 151645), ([5, 151645], "eos"))
        self.assertEqual(trim_generated([5, 6], [151645, 151643]), ([5, 6], "length"))

    def test_compute_checkpoints_use_measured_time_and_distinct_cuts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "result.json").write_text(json.dumps({"phase_train_seconds": 100}))
            for step, seconds in ((1, 10), (2, 25), (3, 49), (4, 78)):
                p = root / f"checkpoint-{step}"
                p.mkdir()
                (p / "cost.json").write_text(json.dumps({"phase_train_seconds": seconds}))
            self.assertEqual([p.name for p in checkpoints_at_fractions(root, [.25, .5, .75])],
                             ["checkpoint-2", "checkpoint-3", "checkpoint-4"])
            with self.assertRaisesRegex(ValueError, "insuficientes"):
                checkpoints_at_fractions(root, [.25, .26])

    def test_project_prompt_changes_only_format_guidance(self):
        old = generate(17, 2, families=FAMILIES)
        new = generate(17, 2, families=FAMILIES, project=True)
        for a, b in zip(old, new):
            self.assertEqual(a["physical_key"], b["physical_key"])
            self.assertEqual(a["answer_si"], b["answer_si"])
            self.assertNotIn('"unidad"', b["prompt"])
            self.assertIn(f'"unit": "{b["requested_unit"]}"', b["prompt"])
            self.assertIn("Usa punto decimal", b["prompt"])

    def test_policy_boundary_alias_ambiguity_and_si_all_families(self):
        for task in generate(17, 2, families=FAMILIES):
            unit = task["requested_unit"]
            value = task["answer_si"] / UNITS[unit][1]
            for factor, expected in ((.990001, 1), (1.009999, 1), (.989999, 0), (1.010001, 0)):
                self.assertEqual(verify(task, f"{value * factor} {unit}")["reward"], expected)
            other = next(u for u, (dim, _) in UNITS.items() if dim == task["family"] and u != unit)
            result = verify(task, f'{task["answer_si"] / UNITS[other][1]} {other}')
            self.assertEqual(result["status"], "unit")
            self.assertTrue(result["equivalent_si"])
            self.assertEqual(verify(task, "x" * (MAX_CHARS + 1))["status"], "too_long")
        for text in ('1,234 m/s', '{"value":"41,879","unit":"W"}', '0 m/s\n{"value":22,"unit":"m/s"}',
                     '22 m/s\nFINAL: 0 m/s', '{"value":1e999,"unit":"W"}'):
            self.assertIsNone(extract_answer(text), text)
        for text, value in (("1.234 m/s", 1.234), ("0,123 m/s", .123), ("22,5 m/s", 22.5)):
            self.assertEqual(extract_answer(text), (value, "m/s"))
        with self.assertRaises(KeyError):
            verify({"family": "speed", "answer_si": 1}, "1 m/s")

    def test_exhausted_generator_fails(self):
        spec = replace(CATALOG["speed"], ranges=((1, 1, 1), (1, 1, 1)))
        with patch.dict(CATALOG, {"speed": spec}), self.assertRaisesRegex(ValueError, "agotado"):
            generate(1, 2, families=("speed",))

    def test_six_family_freeze_1800_360_360_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "exclusions.json").write_text(json.dumps({"keys": [generate(7301, 1)[0]["physical_key"]]}))
            (root / "models.json").write_text("{}")
            for name in ("first", "second"):
                freeze(root / name, root / "exclusions.json", root / "models.json", families=FAMILIES,
                       train=100, evaluation=20, test=20, generation_seed=7301, split_seed=7302,
                       dataset_version="e2-fixture", teacher_samples=6, project=True)
                self.assertEqual(check_dataset(root / name), {"train": 1800, "eval": 360, "test": 360})
            self.assertEqual((root / "first/manifest.json").read_bytes(), (root / "second/manifest.json").read_bytes())
            protocol = root / "first/protocol.json"
            protocol.write_text(protocol.read_text().replace('"teacher_train_samples": 6', '"teacher_train_samples": 8'))
            with self.assertRaisesRegex(ValueError, "modificado"):
                check_dataset(root / "first")

    def test_hf_and_ollama_score_identically_and_validate_coverage(self):
        tasks = generate(17, 2, families=("speed",))[:2]
        config = {"samples": 3, "model": "fixture", "generation": {}, "max_context": 2048}
        hf, ollama = [], []
        for t in tasks:
            for i in range(3):
                text = f'{t["answer_si"] if i == 0 and t == tasks[0] else -1} m/s'
                row = {"task_id": t["id"], "sample_index": i, "prompt": t["prompt"], "model": "fixture"}
                hf.append({**row, "backend": "transformers", "completion": text, "seed": 42 + i,
                           "finish_reason": "length" if i == 2 else "eos", "generation": {},
                           "input_tokens": 20, "output_tokens": 5})
                ollama.append({**row, "result": {"message": {"content": text}, "done": True,
                                               "done_reason": "length" if i == 2 else "stop"}})
        validate_hf_rows(tasks, hf, config)
        self.assertEqual(summarize(tasks, hf), summarize(tasks, ollama))
        summary = summarize(tasks, hf)[1]["all"]
        self.assertAlmostEqual(summary["pass_at_k"]["1"], 1 / 6)
        self.assertEqual(summary["pass_at_k"]["3"], .5)
        self.assertEqual(summary["truncated"], 2)
        for rows in (hf[:-1], hf + [hf[0]], [{**hf[0], "seed": 99}, *hf[1:]]):
            with self.assertRaises(ValueError):
                validate_hf_rows(tasks, rows, config)

    def test_rewards_unknown_prompt_and_sft_membership(self):
        tasks = generate(17, 1, families=("speed",))
        load_tasks(tasks)
        t = tasks[0]
        text = f'{t["answer_si"]} m/s'
        self.assertEqual(grpo_rewards(["rendered"], [text], {"rendered": t["prompt"]}), [1.0])
        with self.assertRaises(ValueError):
            grpo_rewards(["rendered"], [text], {"rendered": "unknown"})
        row = {"task_id": t["id"], "prompt": t["prompt"], "completion": text}
        validate_sft(tasks, [row])
        for rows in ([row, row], [{**row, "task_id": "eval"}], [{**row, "completion": "0 m/s"}]):
            with self.assertRaises(ValueError):
                validate_sft(tasks, rows)

    def test_loss_mask_and_no_silent_truncation(self):
        class Tokenizer:
            eos_token = "!"

            def apply_chat_template(self, messages, **kwargs):
                return "USER:" + messages[0]["content"] + "ASSISTANT:"

            def encode(self, text, **kwargs):
                return list(text.encode())

        row = {"prompt": "question", "completion": "answer"}
        result = tokenize_sft(Tokenizer(), [row], 100)[0]
        self.assertEqual(sum(result["completion_mask"]), 7)
        self.assertEqual(result["completion_mask"][-8:], [0] + [1] * 7)
        with self.assertRaisesRegex(ValueError, "excede"):
            tokenize_sft(Tokenizer(), [row], 10)

    def test_resume_rejects_incompatible_signature_and_missing_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "metadata.json").write_text(json.dumps({"signature": {"data": "a"}}))
            with self.assertRaisesRegex(ValueError, "incompatibles"):
                check_resume(root, {"data": "b"}, root / "checkpoint-1")
            with self.assertRaisesRegex(ValueError, "sin estado"):
                check_resume(root, {"data": "a"}, root / "checkpoint-1")


if __name__ == "__main__":
    unittest.main()

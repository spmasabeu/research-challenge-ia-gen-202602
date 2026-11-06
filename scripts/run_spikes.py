"""Cola local secuencial; conserva resultados y registra fallos para continuar."""

import datetime
import fcntl
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import report_spikes

ROOT = Path(__file__).resolve().parent.parent
NAMES = [
    "scheduling",
    "text_to_sql",
    "database_repair",
    "minesweeper",
    "cooperative_maze",
]
MODELS = [("qwen3:1.7b", "qwen3-1.7b"), ("llama3.2:1b", "llama3.2-1b")]


def checker(name, phase):
    base = ROOT / "spikes" / name
    metadata = base / phase / MODELS[0][1] / "metadata.json"
    current = base / "evaluate.py"
    if not metadata.exists():
        return str(current.relative_to(ROOT))
    expected = json.loads(metadata.read_text())["code"]
    for script in [current, *sorted((base / "history").glob("parser-v*/evaluate.py"))]:
        if all(
            (script.parent / file).is_file()
            and hashlib.sha256((script.parent / file).read_bytes()).hexdigest()
            == digest
            for file, digest in expected.items()
        ):
            return str(script.relative_to(ROOT))
    raise ValueError(f"No se conserva el evaluador correspondiente a {name}/{phase}")


def commands():
    for name in NAMES:
        script = f"spikes/{name}/evaluate.py"
        for phase in ["results"] if name == "scheduling" else ["pilot", "results"]:
            for model, folder in MODELS:
                output = Path(f"spikes/{name}/{phase}/{folder}")
                if (ROOT / output / "summary.json").exists():
                    continue
                if (ROOT / output).exists():
                    resume = Path(f"spikes/{name}/resume.py")
                    if not (ROOT / resume).exists():
                        raise RuntimeError(
                            f"Corrida parcial conservada en {output}; requiere reanudación validada"
                        )
                    yield name, [str(resume), str(output)]
                else:
                    args = [script, "run", "--model", model, "--output", str(output)]
                    if phase == "pilot":
                        args.append("--pilot")
                    yield name, args
            yield name, [checker(name, phase), "check", f"spikes/{name}/{phase}"]


def main():
    os.chdir(ROOT)
    with (Path.home() / ".cache" / "research-challenge-spike-queue.lock").open(
        "a"
    ) as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        status = ROOT / "spikes" / "queue" / "status.json"
        status.parent.mkdir(exist_ok=True)

        def save(state, command=None, error=None):
            value = {
                "state": state,
                "pid": os.getpid(),
                "utc": datetime.datetime.now(datetime.UTC).isoformat(),
                "command": command,
                "error": error,
            }
            status.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")

        command = None
        try:
            for name, command in commands():
                save("running", command)
                print("EJECUTANDO", " ".join(command), flush=True)
                subprocess.run([sys.executable, *command], check=True)
                report_spikes.render(name)
            save("complete")
            print("TODAS LAS INFERENCIAS, CHECKS E INFORMES COMPLETOS", flush=True)
        except Exception as error:
            save("failed", command, str(error))
            raise


if __name__ == "__main__":
    main()

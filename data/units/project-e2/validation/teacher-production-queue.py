import json,os,subprocess,sys,time
from pathlib import Path
r=Path("data/units/project-e2")
parent=Path("/proc/522139/stat")
while parent.exists():
 try:
  if parent.read_text().split(") ",1)[1].split()[0]=="Z": break
 except FileNotFoundError: break
 time.sleep(10)
proof=json.loads((r/"validation/gpu-check-v3-gpu.json").read_text())
assert proof["resume_weights_bitwise_equal"] and proof["grpo_resume_weights_bitwise_equal"]
config=json.loads((r/"config/teacher-production-decision.json").read_text())
assert config["samples"]==4 and config["tasks"]==1800
args=[sys.executable,"-m","challenge.harness","run","--tasks",config["tasks_path"],"--model",config["model"],"--samples",str(config["samples"]),"--max-tokens",str(config["max_tokens"]),"--out",str(r/"runs/teacher")]
print(json.dumps({"command":args,"gpu_proof":"gpu-check-v3-gpu.json"}),flush=True)
subprocess.run(args,env={**os.environ,"PYTHONPATH":"src"},check=True)
print("teacher production complete",flush=True)

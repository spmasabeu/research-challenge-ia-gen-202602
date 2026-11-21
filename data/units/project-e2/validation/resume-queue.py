import os,subprocess,sys,json
from pathlib import Path
r=Path("data/units/project-e2")
jobs=[(["scripts/run_e2.py","--stage","grpo"],"grpo-driver-resume.log"),(["-m","challenge.harness","run","--tasks",str(r/"config/teacher-pilot.jsonl"),"--model","qwen3:8b","--samples","6","--max-tokens","1024","--out",str(r/"runs/teacher-pilot")],"teacher-pilot-driver.log"),(["scripts/check_training_gpu.py","--prefix","gpu-check-v3"],"gpu-check-v3-driver.log")]
for args,name in jobs:
 with (r/"validation"/name).open("a") as log:
  subprocess.run([sys.executable,*args],env={**os.environ,"PYTHONPATH":"src"},stdout=log,stderr=subprocess.STDOUT,check=True)
 print(name,"complete",flush=True)

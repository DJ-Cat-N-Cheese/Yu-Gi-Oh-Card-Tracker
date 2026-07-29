import subprocess
import time

def run():
    print("Testing new code...")
    res_new = subprocess.run(['python3', 'benchmark_ygo_api.py'], capture_output=True, text=True, env={"PYTHONPATH": "."})
    print(res_new.stdout)

run()

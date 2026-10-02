"""Optional one-command demo: scan the weak website, then the fixed one."""
import os
import subprocess
import sys
import time

import requests

PORT = "5050"
TARGET = f"http://127.0.0.1:{PORT}"


def scan(label, secure):
    env = dict(os.environ, SECURE="1" if secure else "0", PORT=PORT)
    server = subprocess.Popen([sys.executable, "practice_app.py"], env=env,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(40):
            try:
                requests.get(TARGET, timeout=1)
                break
            except requests.RequestException:
                time.sleep(0.5)
        print(f"\n===== {label} version =====")
        subprocess.run([sys.executable, "webcheck.py", "--target", TARGET,
                        "--report", f"report_{label.lower()}.md"])
    finally:
        server.terminate()
        server.wait()


scan("Weak", secure=False)
scan("Fixed", secure=True)

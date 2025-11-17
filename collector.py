# collector.py
import time, json, requests, os
from itertools import cycle

SCORER = os.getenv("SCORER_URL", "http://localhost:5000/score")
LOGS_FILE = os.getenv("LOGS_FILE", "logs.json")
INTERVAL = float(os.getenv("SCAN_INTERVAL", "3.0"))  # seconds between flows

def read_logs():
    with open(LOGS_FILE) as f:
        return json.load(f)

def simulate_loop():
    logs = read_logs()
    # rotate forever
    for ev in cycle(logs):
        try:
            r = requests.post(SCORER, json=ev, timeout=10)
            print("scanned", ev.get("src_ip"), "->", r.status_code, r.text[:200])
        except Exception as e:
            print("scan post failed:", e)
        time.sleep(INTERVAL)

if __name__ == "__main__":
    simulate_loop()

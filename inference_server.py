from flask import Flask, request, jsonify
import joblib, numpy as np, os, json, threading, time, subprocess
from llm_analyzer import analyze_event
import uuid

MODEL = 'if_model.joblib'
SCALER = 'scaler.joblib'

app = Flask(__name__)
model = joblib.load(MODEL)
scaler = joblib.load(SCALER)

alerts = []
alerts_lock = threading.Lock()
ALERT_TTL = 60 * 60 * 24

AUTO_BLOCK = os.getenv("AUTO_BLOCK", "False").lower() in ("1","true","yes")
SIMULATE_BLOCK = os.getenv("SIMULATE_BLOCK", "True").lower() in ("1","true","yes")
OS_TYPE = os.getenv("OS_TYPE", "").lower()


def prune_old_alerts():
    while True:
        time.sleep(60)
        cutoff = time.time() - ALERT_TTL
        with alerts_lock:
            alerts[:] = [a for a in alerts if a["timestamp"] > cutoff]


def block_ip_linux(ip):
    cmd = ["sudo", "iptables", "-I", "INPUT", "-s", ip, "-j", "DROP"]
    return subprocess.run(cmd, capture_output=True, text=True)


def block_ip_windows(ip):
    ps_cmd = f'New-NetFirewallRule -DisplayName "Block_{ip}" -RemoteAddress {ip} -Action Block'
    cmd = ["powershell", "-Command", ps_cmd]
    return subprocess.run(cmd, capture_output=True, text=True)


def block_ip(ip):
    if SIMULATE_BLOCK:
        return {"simulated": True, "ip": ip}

    if OS_TYPE == "windows" or os.name == "nt":
        res = block_ip_windows(ip)
    else:
        res = block_ip_linux(ip)

    return {"returncode": res.returncode, "stdout": res.stdout, "stderr": res.stderr}


@app.route('/score', methods=['POST'])
def score():
    payload = request.json
    bo = payload.get('bytes_out', 0)
    bi = payload.get('bytes_in', 0)
    dur = payload.get('duration', 0)
    pkts = payload.get('pkts', 0)

    x = np.array([[np.log1p(bo), np.log1p(bi), dur, pkts]])
    xs = scaler.transform(x)

    raw_score = model.decision_function(xs)[0]
    pred = model.predict(xs)[0]

    # Compute score FIRST
    score = float(-raw_score)

    # ---------------------------
    # FIXED ANOMALY LOGIC
    # ---------------------------
    # We trigger anomaly if:
    # 1. Model predicts outlier (pred == -1), OR
    # 2. Score exceeds threshold (loose threshold for testing)
    if pred == -1 or score > 0.1:
        anomaly = 1
    else:
        anomaly = 0
    # ---------------------------

    result = {
        'anomaly': anomaly,
        'anomaly_score': score,
        'input': {'bytes_out': bo, 'bytes_in': bi, 'duration': dur, 'pkts': pkts}
    }

    if anomaly:
        llm_out = analyze_event(payload)

        alert = {
            "id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "event": payload,
            "score": score,
            "llm": llm_out,
            "blocked": False,
            "auto_blocked": False
        }

        recommend = llm_out.get("recommended_action") if isinstance(llm_out, dict) else None

        should_block = False
        if recommend:
            text = " ".join(recommend).lower()
            if "block" in text or "isolate" in text or "quarantine" in text:
                should_block = True

        if should_block and AUTO_BLOCK:
            blk_res = block_ip(payload.get("src_ip"))
            alert["blocked"] = True
            alert["auto_blocked"] = True
            alert["block_result"] = blk_res

        with alerts_lock:
            alerts.append(alert)

        result["llm"] = llm_out
        result["alert_id"] = alert["id"]

    return jsonify(result)


@app.route('/alerts', methods=['GET'])
def get_alerts():
    with alerts_lock:
        return jsonify(sorted(alerts, key=lambda a: a["timestamp"], reverse=True))


@app.route('/block', methods=['POST'])
def api_block():
    data = request.json
    ip = data.get("ip")
    force = data.get("force", False)

    if not ip:
        return jsonify({"error": "missing ip"}), 400

    blk_res = block_ip(ip)
    with alerts_lock:
        for a in alerts:
            if a["event"].get("src_ip") == ip:
                a["blocked"] = True
                a["block_result"] = blk_res
                a["auto_blocked"] = force

    return jsonify({"result": blk_res})


if __name__ == '__main__':
    t = threading.Thread(target=prune_old_alerts, daemon=True)
    t.start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

Here is the **complete and polished `README.md`** for your project — formatted beautifully for GitHub or your final-year project submission.

You can copy-paste it **directly** into your `README.md` file.

---

# 🛡️ **SamGuard – AI-Enabled Firewall**

**Real-time Network Anomaly Detection + LLM-Powered Threat Analysis + SOC Dashboard**

SamGuard is an intelligent, real-time AI firewall that captures live network traffic, detects anomalies using machine learning (IsolationForest), analyzes threats using a Large Language Model (LLM), and provides an enterprise-style SOC dashboard with maps, charts, timelines, and one-click IP blocking.

---

# 🚀 Features

### ✅ **Real-Time Packet Capture (PyShark)**

Captures live packets from Wi-Fi or Ethernet and converts them into flow-like events.

### ✅ **ML-Based Anomaly Detection**

Uses IsolationForest to detect unusual traffic patterns (e.g., data exfiltration).

### ✅ **LLM-Powered Threat Explanation**

Explains alerts with:

* attack type
* severity
* recommended actions

### ✅ **SOC Dashboard (Streamlit)**

Includes:

* Overview metrics
* Attack map
* Severity charts
* Threat timeline
* Blocklist
* Real-time alerts

### ✅ **One-Click IP Blocking**

Simulated blocking by default (safe)
Windows firewall blocking works when enabled.

---

# 📁 Project Structure

```
samguard/
│── inference_server.py     # ML + LLM backend
│── collector_live.py       # PyShark packet collector
│── streamlit_app.py        # Dashboard UI
│── llm_analyzer.py         # LLM call logic
│── scaler.joblib           # Model scaler
│── if_model.joblib         # IsolationForest model
│── README.md               # This file
│── venv/                   # Python virtual environment (ignored)
```

---

# 📦 Installation

### **1. Clone project**

```bash
git clone <your-repo-url>
cd samguard
```

### **2. Create virtual environment**

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### **3. Install dependencies**

```bash
pip install -r requirements.txt
```

If you don’t have a `requirements.txt` yet, use:

```bash
pip install streamlit pandas altair requests pyshark scikit-learn streamlit-autorefresh
```

You must also install **tshark**, required by PyShark:

Windows (Npcap/tshark):

* Install Wireshark (tshark auto-included)
* Ensure `tshark.exe` is in PATH

---

# 🏃‍♂️ Running the Full System

You must open **3 terminals**.

---

## **1️⃣ Start the Backend (ML + LLM Server)**

In Terminal #1:

```bash
venv\Scripts\activate
python inference_server.py
```

If successful:

```
 * Running on http://0.0.0.0:5000
```

---

## **2️⃣ Start Live Packet Collector**

In Terminal #2:

```bash
venv\Scripts\activate
python collector_live.py
```

You will see:

```
📡 Starting LIVE capture on: \Device\NPF_{073C...}
➡ Sent: 192.168.x.x → 200
➡ Sent: fe80::... → 200
```

---

## **3️⃣ Launch Streamlit Dashboard (SOC UI)**

In Terminal #3:

```bash
venv\Scripts\activate
streamlit run streamlit_app.py
```

Open your browser:

👉 **[http://localhost:8501](http://localhost:8501)**

You will see:

* Overview metrics
* Attack charts
* Map
* Timeline
* Alerts feed
* Blocklist

If no threats exist, you’ll see:

```
✨ Network is clean — no threats detected yet.
```

---

# 🎯 Testing the Firewall (Manual Attack Simulation)

To force an anomaly, run:

### **Windows CMD**

```cmd
curl -X POST http://localhost:5000/score ^
-H "Content-Type: application/json" ^
-d "{\"src_ip\":\"5.5.5.5\",\"dst_ip\":\"1.1.1.1\",\"bytes_out\":9999999,\"bytes_in\":1,\"duration\":100,\"pkts\":999}"
```

Expected response:

```json
{
  "anomaly":1,
  "alert_id":"...",
  "llm": { ... }
}
```

You will now see the alert appear instantly in Streamlit.

---

# 🔨 Blocking an IP

In the Streamlit dashboard:

* Click **🚫 Block IP** (real/simulated block)
* Click **🧪 Simulate Block** (safe mode)

Backend responds:

```
Successfully blocked IP: 5.5.5.5
```

The blocklist page will show the record.

---

# 🧪 Testing with Real Network Attacks (Optional)

From another machine / VM:

### **Port scan**

```bash
nmap -sS YOUR_MACHINE_IP
```

### **SYN flood** (Linux)

```bash
sudo hping3 --flood --syn YOUR_MACHINE_IP
```

### **Large data transfer**

Upload or download large files — useful for simulating exfiltration anomalies.

---

# 🛑 Stopping Everything

Press **CTRL + C** in all 3 terminals:

* backend
* collector
* dashboard

---

# 🧱 Architecture (High-Level)

```
         ┌──────────────────┐
         │   Internet / LAN │
         └─────────┬────────┘
                   │ packets
         ┌─────────▼──────────┐
         │  PyShark Collector  │
         │ (live capture)      │
         └─────────┬──────────┘
                   │ events (JSON)
         ┌─────────▼──────────┐
         │ Inference Server   │
         │ ML + LLM analysis  │
         │ IsolationForest     │
         └─────────┬──────────┘
                   │ alerts
         ┌─────────▼──────────┐
         │ Streamlit Dashboard │
         │ Maps, Charts, SOC   │
         └──────────────────────┘
```

---

# 📄 License

MIT License.

---

# 🧑‍💻 Author

**cvM – Samriddhi Firewall Project**
Built using Python, Streamlit, PyShark, IsolationForest, OpenAI/OpenRouter LLMs.



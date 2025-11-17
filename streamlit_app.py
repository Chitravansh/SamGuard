import streamlit as st
import requests
import os
from streamlit_autorefresh import st_autorefresh

# Backend API endpoint
BACKEND = os.getenv("SCORER_URL", "http://localhost:5000")
REFRESH = 5  # seconds


# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="SamGuard AI Firewall",
    page_icon="🛡️",
    layout="wide"
)


# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>
.alert-card {
    background-color: #1E1E1E;
    padding: 20px;
    border-radius: 14px;
    margin-bottom: 25px;
    border: 1px solid #2F2F2F;
    box-shadow: 0 0 8px rgba(0,0,0,0.25);
}
.severity-high {
    color:#EF4444; 
    font-weight:700;
}
.severity-medium {
    color:#FACC15; 
    font-weight:700;
}
.severity-low {
    color:#22C55E; 
    font-weight:700;
}
.section-title {
    font-size:18px;
    font-weight:600;
    margin-bottom:5px;
    color:#C0C0C0;
}
</style>
""", unsafe_allow_html=True)


# -------------------- TITLE --------------------
st.title("🛡️ SamGuard – AI Firewall Dashboard")
st.caption("Real-time AI-driven detection, analysis & response")


# -------------------- FETCH ALERTS --------------------
def fetch_alerts():
    try:
        r = requests.get(BACKEND + "/alerts")
        return r.json()
    except:
        return {"error": "Backend not reachable"}


alerts = fetch_alerts()

# Auto-refresh
st_autorefresh(interval=REFRESH * 1000, key="samguard_autorefresh")


# -------------------- NO ALERT CASE --------------------
if isinstance(alerts, dict) and alerts.get("error"):
    st.error("❌ " + alerts["error"])
    st.stop()

if len(alerts) == 0:
    st.info("✨ Network is clean — no threats detected yet.")
    st.stop()


# -------------------- SHOW ALERT CARDS --------------------
for idx, alert in enumerate(alerts):

    llm = alert.get("llm", {})
    event = alert.get("event", {})
    sev = llm.get("severity", 0)

    # Severity color logic
    if sev >= 7:
        sev_html = "<span class='severity-high'>HIGH</span>"
    elif sev >= 4:
        sev_html = "<span class='severity-medium'>MEDIUM</span>"
    else:
        sev_html = "<span class='severity-low'>LOW</span>"

    # Card wrapper
    st.markdown("<div class='alert-card'>", unsafe_allow_html=True)

    # HEADER
    st.markdown(f"""
    ### 🚨 Threat Detected  
    **Severity:** {sev_html}  
    **Source:** `{event.get("src_ip", "unknown")}`  
    **Destination:** `{event.get("dst_ip", "unknown")}`
    """, unsafe_allow_html=True)

    st.markdown("---")

    # LLM SECTION
    st.markdown("<div class='section-title'>🧠 AI Attack Analysis</div>", unsafe_allow_html=True)
    st.json(llm)

    # EVENT SECTION
    st.markdown("<div class='section-title'>📊 Packet Metadata</div>", unsafe_allow_html=True)
    st.json(event)

    # ACTIONS
    col1, col2 = st.columns([1, 1])

    block_key = f"block_{alert['id']}_{idx}"
    sim_key = f"sim_{alert['id']}_{idx}"

    if col1.button("🚫 Block IP", key=block_key):
        res = requests.post(BACKEND + "/block",
                            json={"ip": event.get("src_ip"), "force": True})
        st.success(f"Successfully BLOCKED: {event.get('src_ip')}")
        st.json(res.json())

    if col2.button("🧪 Simulate Block", key=sim_key):
        res = requests.post(BACKEND + "/block",
                            json={"ip": event.get("src_ip"), "force": False})
        st.info(f"Simulated blocking: {event.get('src_ip')}")
        st.json(res.json())

    st.markdown("</div>", unsafe_allow_html=True)

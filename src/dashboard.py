"""Streamlit dashboard: upload flows, see triaged alerts."""
import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
ICONS = {"critical": "🟥", "high": "🟠", "medium": "🟡", "low": "🟢"}
ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}

st.set_page_config(page_title="Network Alert Triage", layout="wide")
st.title("Network Alert Triage")
st.caption("Upload flows from CICFlowMeter. A model detects attacks, then an LLM explains each alert.")

file = st.file_uploader("Flows CSV", type="csv")
use_llm = st.toggle("Explain alerts with the LLM", value=True)

if file is not None:
    with st.spinner("Analyzing..."):
        r = requests.post(
            f"{API_URL}/analyze",
            params={"with_llm": use_llm},
            files={"file": (file.name, file.getvalue(), "text/csv")},
            timeout=300,
        )
    if r.status_code != 200:
        st.error(f"The API answered {r.status_code}: {r.text[:300]}")
        st.stop()

    data = r.json()
    alerts = sorted(
        data["alerts"],
        key=lambda a: ORDER.get(a.get("triage", {}).get("severity"), 4),
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Flows analyzed", data["flows"])
    c2.metric("Flows flagged", data["flagged"])
    c3.metric("Alerts", len(alerts))

    for a in alerts:
        t = a.get("triage")
        sev = t["severity"] if t else "n/a"
        title = f"{ICONS.get(sev, '⚪')} {sev.upper()} · {a['type']} · {a['attacker']} → {a['target']}"
        with st.expander(title, expanded=sev in ("critical", "high")):
            f1, f2, f3, f4 = st.columns(4)
            f1.metric("Flows", a["flows"])
            f2.metric("Distinct ports", a["distinct_ports"])
            f3.metric("Duration (s)", a["duration_seconds"])
            f4.metric("Detector confidence", a["avg_confidence"])
            if t:
                if t["likely_false_positive"]:
                    st.warning("The LLM thinks this is likely a false positive.")
                st.write(t["explanation"])
                st.info("Next step: " + t["next_step"])
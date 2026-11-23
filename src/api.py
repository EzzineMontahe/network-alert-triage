"""Web API: upload CICFlowMeter flows, get triaged alerts back."""
import io

import pandas as pd
from fastapi import FastAPI, UploadFile

from src import alerts, detector, lab_features, triage

app = FastAPI(title="Network Alert Triage")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(file: UploadFile, with_llm: bool = True):
    raw = pd.read_csv(io.BytesIO(await file.read()))
    features = lab_features.fix_payload(lab_features.to_model_features(raw))
    result = detector.predict(features)
    raw["label"] = result["label"].values
    raw["confidence"] = result["confidence"].values

    found = alerts.build_alerts(raw)
    if with_llm:
        for a in found:
            a["triage"] = triage.triage(a)
    return {
        "flows": len(raw),
        "flagged": int((raw["label"] != "BENIGN").sum()),
        "alerts": found,
    }
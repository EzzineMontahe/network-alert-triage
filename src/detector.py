"""Load the trained model and classify network connections."""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "rf3.joblib"

_bundle = joblib.load(MODEL_PATH)
_model = _bundle["model"]
_features = _bundle["features"]


def predict(flows: pd.DataFrame) -> pd.DataFrame:
    """Classify connections. Returns a label and a confidence for each one."""
    flows = flows.copy()
    flows.columns = flows.columns.str.strip()
    X = flows[_features].replace([np.inf, -np.inf], np.nan).fillna(0)
    labels = _model.predict(X)
    confidence = _model.predict_proba(X).max(axis=1)
    return pd.DataFrame({"label": labels, "confidence": confidence}, index=flows.index)
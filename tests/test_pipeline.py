import pandas as pd
import pytest
from fastapi.testclient import TestClient

from src import alerts, api, detector, lab_features


def test_lab_columns_are_converted_and_seconds_become_microseconds():
    lab = pd.DataFrame({name: [1.0] for name in set(lab_features.COLUMN_MAP.values())})
    lab["flow_duration"] = 2.0  # seconds
    out = lab_features.to_model_features(lab)
    assert set(out.columns) == set(lab_features.COLUMN_MAP)
    assert out["Flow Duration"].iloc[0] == 2_000_000


def test_detector_returns_a_label_and_confidence_per_flow():
    flows = pd.DataFrame(0.0, index=range(3), columns=detector._features)
    result = detector.predict(flows)
    assert len(result) == 3
    assert list(result.columns) == ["label", "confidence"]


def test_alerts_group_flows_per_attacker_and_target():
    flows = pd.DataFrame({
        "src_ip": ["10.0.0.1"] * 3 + ["10.0.0.1", "10.0.0.2"],
        "dst_ip": ["10.0.0.9"] * 3 + ["10.0.0.9", "224.0.0.251"],
        "dst_port": [1, 2, 3, 80, 5353],
        "timestamp": ["2026-11-21 13:00:00"] * 5,
        "label": ["PortScan"] * 3 + ["BENIGN", "PortScan"],
        "confidence": [1.0, 1.0, 1.0, 1.0, 0.6],
    })
    found = alerts.build_alerts(flows)
    assert len(found) == 2  # the BENIGN flow is not an alert
    scan = next(a for a in found if a["attacker"] == "10.0.0.1")
    assert scan["flows"] == 3 and scan["distinct_ports"] == 3
    assert scan["target_is_multicast"] is False
    chatter = next(a for a in found if a["attacker"] == "10.0.0.2")
    assert chatter["target_is_multicast"] is True


client = TestClient(api.app)


def test_health_route():
    assert client.get("/health").json() == {"status": "ok"}


def test_analyze_route_on_real_lab_file():
    from pathlib import Path
    path = Path("data/lab/scan2.csv")
    if not path.exists():
        pytest.skip("lab data is not in the repo")
    with path.open("rb") as f:
        reply = client.post("/analyze?with_llm=false", files={"file": ("scan2.csv", f, "text/csv")})
    body = reply.json()
    assert reply.status_code == 200
    assert body["flows"] == 1001
    assert any(a["distinct_ports"] == 1000 for a in body["alerts"])
    
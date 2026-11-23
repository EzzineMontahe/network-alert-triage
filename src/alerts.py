"""Group flagged flows into alerts and add the facts an analyst would check."""
import ipaddress

import pandas as pd


def build_alerts(flows: pd.DataFrame) -> list[dict]:
    """flows needs: src_ip, dst_ip, dst_port, timestamp, label, confidence."""
    flagged = flows[flows["label"] != "BENIGN"]
    alerts = []
    for (src, dst, label), g in flagged.groupby(["src_ip", "dst_ip", "label"]):
        times = pd.to_datetime(g["timestamp"])
        seconds = int((times.max() - times.min()).total_seconds())
        alerts.append({
            "attacker": src,
            "target": dst,
            "type": label,
            "flows": len(g),
            "distinct_ports": int(g["dst_port"].nunique()),
            "duration_seconds": max(1, seconds),
            "sample_ports": [int(p) for p in g["dst_port"].value_counts().head(5).index],
            "target_is_multicast": ipaddress.ip_address(dst).is_multicast,
            "avg_confidence": round(float(g["confidence"].mean()), 2),
        })
    return alerts
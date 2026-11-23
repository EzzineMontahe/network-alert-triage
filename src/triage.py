"""Ask an LLM to triage each alert."""
import json
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
MODEL = "openai/gpt-oss-120b"
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = Groq()
    return _client

SYSTEM = """You are a SOC analyst assistant. You receive one network alert as JSON,
produced by a machine learning detector that sometimes makes mistakes.
Use only the facts in the alert. Do not invent details.
Reply with JSON only, with exactly these keys:
- severity: one of "low", "medium", "high", "critical"
- likely_false_positive: true or false
- explanation: 2 or 3 plain sentences saying what happened and why you think so
- next_step: one concrete action for the analyst
Hints: many distinct ports in a short time from one source suggests a port scan.
Multicast targets (such as 224.0.0.251 on port 5353, mDNS) are usually normal
local network chatter. A low avg_confidence means the detector is unsure."""


def triage(alert: dict) -> dict:
    """Return the LLM's verdict for one alert as a dict."""
    reply =_get_client().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": json.dumps(alert)},
        ],
        temperature=0,
    )
    text = reply.choices[0].message.content
    return json.loads(text[text.index("{"): text.rindex("}") + 1])
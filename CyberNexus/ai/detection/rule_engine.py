
"""Rule-based threat detection for CyberNexus."""

from typing import Any

RULES = {
    "brute_force": {
        "keywords": [
            "brute force",
            "multiple failed login",
            "repeated login failure",
            "password guessing",
        ],
        "risk_score": 85,
    },
    "port_scan": {
        "keywords": [
            "port scan",
            "port scanning",
            "network scan",
            "masscan",
        ],
        "risk_score": 65,
    },
    "malware": {
        "keywords": [
            "malware",
            "ransomware",
            "trojan",
            "virus detected",
        ],
        "risk_score": 95,
    },
    "privilege_escalation": {
        "keywords": [
            "privilege escalation",
            "unauthorized privilege",
            "unexpected admin access",
        ],
        "risk_score": 90,
    },
    "suspicious_script": {
        "keywords": [
            "encoded powershell",
            "suspicious powershell",
            "malicious script",
            "obfuscated command",
        ],
        "risk_score": 80,
    },
}


def detect_threat(event: dict[str, Any]) -> dict[str, Any]:
    """Analyze an event and return its threat assessment."""

    event_type = str(event.get("EventType", event.get("event_type", "")))
    description = str(event.get("Description", event.get("description", "")))
    source = str(event.get("Source", event.get("source", "")))
    severity = str(event.get("Severity", event.get("severity", "")))

    text = f"{event_type} {description} {source}".lower()
    matches = []

    for threat_type, rule in RULES.items():
        if any(keyword in text for keyword in rule["keywords"]):
            matches.append({
                "threat_type": threat_type,
                "risk_score": rule["risk_score"],
            })

    if not matches:
        return {
            "is_threat": False,
            "threat_type": "unknown",
            "risk_score": 0,
            "risk_level": "low",
            "indicators": [],
        }

    highest = max(matches, key=lambda item: item["risk_score"])
    risk_score = highest["risk_score"]

    if severity.lower() == "critical":
        risk_score = max(risk_score, 95)
    elif severity.lower() == "high":
        risk_score = max(risk_score, 85)

    risk_level = (
        "high" if risk_score >= 81
        else "medium" if risk_score >= 31
        else "low"
    )

    return {
        "is_threat": True,
        "threat_type": highest["threat_type"],
        "risk_score": risk_score,
        "risk_level": risk_level,
        "indicators": [item["threat_type"] for item in matches],
    }

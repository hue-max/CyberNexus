
"""Machine-learning prediction service for CyberNexus."""

from pathlib import Path

import joblib

MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "threat_model.joblib"
)

RISK_SCORES = {
    "brute_force": 85,
    "port_scan": 65,
    "malware": 95,
    "privilege_escalation": 90,
    "suspicious_script": 80,
    "normal": 0,
}

CONFIDENCE_THRESHOLD = 0.70


def predict_threat(text: str) -> dict:
    """Classify event text using the trained Random Forest model."""

    if not text or not text.strip():
        raise ValueError("Event text must not be empty.")

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained ML model not found: {MODEL_PATH}"
        )

    model = joblib.load(MODEL_PATH)
    prediction = str(model.predict([text])[0])
    probabilities = model.predict_proba([text])[0]
    confidence = float(max(probabilities))

    is_threat = (
        prediction != "normal"
        and confidence >= CONFIDENCE_THRESHOLD
    )

    risk_score = RISK_SCORES.get(prediction, 0) if is_threat else 0

    risk_level = (
        "high" if risk_score >= 81
        else "medium" if risk_score >= 31
        else "low"
    )

    return {
        "prediction": prediction,
        "confidence": round(confidence, 4),
        "is_threat": is_threat,
        "threat_type": prediction if is_threat else "unknown",
        "risk_score": risk_score,
        "risk_level": risk_level,
        "detection_method": "random_forest",
    }

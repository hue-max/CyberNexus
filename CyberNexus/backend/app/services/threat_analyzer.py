
"""Hybrid rule-based and ML threat detection for CyberNexus."""

import sys
from pathlib import Path

from app.services.database import get_connection

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai.detection.rule_engine import detect_threat
from ai.ml.predictor import predict_threat


FAILED_LOGIN_TYPES = {"login_failure", "failed_login", "failed login"}
BRUTE_FORCE_THRESHOLD = 5
DETECTION_WINDOW_MINUTES = 5
BRUTE_FORCE_RISK_SCORE = 85


def analyze_pending_events(limit: int = 100) -> dict:
    """Analyze pending events and save threats and risk assessments."""

    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    connection = get_connection()
    analyzed = 0
    detected = 0
    skipped = 0
    ml_detected = 0

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT TOP (?)
                e.EventID,
                e.AssetID,
                e.EventType,
                e.Severity,
                e.Source,
                e.Description,
                e.EventTimestamp
            FROM dbo.SecurityEvents AS e
            WHERE NOT EXISTS (
                SELECT 1
                FROM dbo.Threats AS t
                WHERE t.EventID = e.EventID
            )
            ORDER BY e.EventTimestamp ASC, e.EventID ASC
            """,
            (limit,),
        )

        events = cursor.fetchall()

        for event in events:
            (
                event_id,
                asset_id,
                event_type,
                severity,
                source,
                description,
                event_timestamp,
            ) = event

            analyzed += 1

            event_data = {
                "EventType": event_type,
                "Severity": severity,
                "Source": source or "",
                "Description": description or "",
            }

            # Run rule-based detection first.
            result = detect_threat(event_data)
            confidence = None
            detection_method = "rule_based"

            # Use ML when no existing rule matches.
            if not result["is_threat"]:
                event_text = (
                    f"{event_type or ''} "
                    f"{severity or ''} "
                    f"{source or ''} "
                    f"{description or ''}"
                )

                try:
                    ml_result = predict_threat(event_text)

                    if ml_result["is_threat"]:
                        result = {
                            "is_threat": True,
                            "threat_type": ml_result["threat_type"],
                            "risk_score": ml_result["risk_score"],
                            "risk_level": ml_result["risk_level"],
                            "indicators": [
                                "Random Forest classification",
                                (
                                    "ML confidence: "
                                    f"{ml_result['confidence']:.2%}"
                                ),
                            ],
                        }

                        # Store confidence as a percentage (0–100).
                        confidence = ml_result["confidence"] * 100.0
                        detection_method = "random_forest"
                        ml_detected += 1

                except Exception as exc:
                    # ML errors must not stop rule-based processing.
                    print(
                        f"ML prediction unavailable for event "
                        f"{event_id}: {exc}"
                    )

            # Detect repeated failed logins in the trailing five minutes.
            if str(event_type or "").strip().lower() in FAILED_LOGIN_TYPES:
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM dbo.SecurityEvents AS e
                    WHERE LOWER(LTRIM(RTRIM(e.EventType))) IN
                        ('login_failure', 'failed_login', 'failed login')
                      AND e.EventTimestamp >= DATEADD(
                          MINUTE, -?, CAST(? AS DATETIME2)
                      )
                      AND e.EventTimestamp < DATEADD(
                          MICROSECOND, 1, CAST(? AS DATETIME2)
                      )
                      AND (
                          e.AssetID = ?
                          OR (e.AssetID IS NULL AND ? IS NULL)
                      )
                      AND (
                          e.Source = ?
                          OR (e.Source IS NULL AND ? IS NULL)
                      )
                    """,
                    (
                        DETECTION_WINDOW_MINUTES,
                        event_timestamp,
                        event_timestamp,
                        asset_id,
                        asset_id,
                        source,
                        source,
                    ),
                )

                failed_login_count = cursor.fetchone()[0]

                if failed_login_count >= BRUTE_FORCE_THRESHOLD:
                    result = {
                        "is_threat": True,
                        "threat_type": "brute_force",
                        "risk_score": BRUTE_FORCE_RISK_SCORE,
                        "risk_level": "high",
                        "indicators": [
                            f"{failed_login_count} failed logins within "
                            f"{DETECTION_WINDOW_MINUTES} minutes",
                            "repeated login failures",
                        ],
                    }

                    # The explicit brute-force rule takes precedence.
                    confidence = None
                    detection_method = "rule_based"

            if not result["is_threat"]:
                skipped += 1
                continue

            cursor.execute(
                """
                INSERT INTO dbo.Threats
                    (EventID, ThreatType, Confidence, Status)
                OUTPUT INSERTED.ThreatID
                VALUES (?, ?, ?, 'Detected')
                """,
                (event_id, result["threat_type"], confidence),
            )

            threat_id = cursor.fetchone()[0]

            explanation = (
                f"Detection: {result['threat_type']}; "
                f"method: {detection_method}; "
                f"risk level: {result['risk_level']}; "
                f"indicators: {', '.join(result['indicators'])}"
            )[:500]

            cursor.execute(
                """
                INSERT INTO dbo.RiskAssessments
                    (AssetID, ThreatID, RiskScore, Explanation)
                VALUES (?, ?, ?, ?)
                """,
                (
                    asset_id,
                    threat_id,
                    result["risk_score"],
                    explanation,
                ),
            )

            detected += 1

        connection.commit()

        return {
            "events_analyzed": analyzed,
            "threats_detected": detected,
            "events_without_matching_rules": skipped,
            "ml_threats_detected": ml_detected,
            "failed_login_threshold": BRUTE_FORCE_THRESHOLD,
            "detection_window_minutes": DETECTION_WINDOW_MINUTES,
        }

    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

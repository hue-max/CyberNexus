
"""Forensic evidence collection and integrity verification."""

import hashlib
import json

from app.services.database import get_connection


def collect_incident_evidence(incident_id: int) -> dict:
    """Save evidence snapshots for events linked to an incident."""

    if incident_id < 1:
        raise ValueError("Incident ID must be positive.")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT IncidentID
            FROM dbo.ThreatIncidents
            WHERE IncidentID = ?
            """,
            (incident_id,),
        )

        if cursor.fetchone() is None:
            raise ValueError(f"Incident {incident_id} was not found.")

        cursor.execute(
            """
            SELECT
                e.EventID,
                e.AssetID,
                e.EventType,
                e.Severity,
                e.Source,
                e.Description,
                e.EventTimestamp,
                e.ReceivedTimestamp
            FROM dbo.ThreatIncidentEvents AS tie
            INNER JOIN dbo.SecurityEvents AS e
                ON e.EventID = tie.EventID
            WHERE tie.IncidentID = ?
              AND NOT EXISTS (
                  SELECT 1
                  FROM dbo.ThreatForensicEvidence AS fe
                  WHERE fe.EventID = e.EventID
              )
            ORDER BY e.EventTimestamp, e.EventID
            """,
            (incident_id,),
        )

        events = cursor.fetchall()
        collected = 0

        for event in events:
            (
                event_id,
                asset_id,
                event_type,
                severity,
                source,
                description,
                event_timestamp,
                received_timestamp,
            ) = event

            snapshot = {
                "event_id": event_id,
                "asset_id": asset_id,
                "event_type": event_type,
                "severity": severity,
                "source": source,
                "description": description,
                "event_timestamp": (
                    event_timestamp.isoformat()
                    if event_timestamp else None
                ),
                "received_timestamp": (
                    received_timestamp.isoformat()
                    if received_timestamp else None
                ),
            }

            snapshot_json = json.dumps(
                snapshot,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )

            integrity_hash = hashlib.sha256(
                snapshot_json.encode("utf-8")
            ).hexdigest()

            cursor.execute(
                """
                INSERT INTO dbo.ThreatForensicEvidence
                (
                    IncidentID,
                    EventID,
                    EvidenceType,
                    EvidenceDescription,
                    EvidenceSnapshot,
                    IntegrityHash
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    incident_id,
                    event_id,
                    "Security Event Snapshot",
                    f"Snapshot of security event {event_id}",
                    snapshot_json,
                    integrity_hash,
                ),
            )

            collected += 1

        connection.commit()

        return {
            "incident_id": incident_id,
            "evidence_collected": collected,
            "message": (
                "Evidence collection completed."
                if collected
                else "No new evidence to collect."
            ),
        }

    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def verify_incident_evidence(incident_id: int) -> dict:
    """Recalculate evidence hashes and report integrity results."""

    if incident_id < 1:
        raise ValueError("Incident ID must be positive.")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT EvidenceID, EventID, EvidenceSnapshot, IntegrityHash
            FROM dbo.ThreatForensicEvidence
            WHERE IncidentID = ?
            ORDER BY EvidenceID
            """,
            (incident_id,),
        )

        rows = cursor.fetchall()
        results = []

        for evidence_id, event_id, snapshot, stored_hash in rows:
            calculated_hash = hashlib.sha256(
                snapshot.encode("utf-8")
            ).hexdigest()

            results.append({
                "evidence_id": evidence_id,
                "event_id": event_id,
                "integrity_valid": (
                    calculated_hash.lower() == stored_hash.strip().lower()
                ),
            })

        return {
            "incident_id": incident_id,
            "evidence_checked": len(results),
            "all_integrity_valid": all(
                item["integrity_valid"] for item in results
            ),
            "results": results,
        }

    finally:
        connection.close()

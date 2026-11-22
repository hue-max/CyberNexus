"""Incident grouping and investigation management for CyberNexus."""

from datetime import timedelta

from app.services.database import get_connection


INCIDENT_WINDOW_MINUTES = 5

ALLOWED_INCIDENT_STATUSES = {
    "Open",
    "Investigating",
    "Resolved",
    "Closed",
}


def group_existing_threats() -> dict:
    """Group related unlinked threat events into incidents."""

    connection = get_connection()
    incidents_created = 0
    events_linked = 0
    events_not_grouped = 0

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                t.ThreatID,
                t.ThreatType,
                e.EventID,
                e.AssetID,
                e.Source,
                e.EventTimestamp,
                COALESCE(MAX(r.RiskScore), 0) AS RiskScore
            FROM dbo.Threats AS t
            INNER JOIN dbo.SecurityEvents AS e
                ON e.EventID = t.EventID
            LEFT JOIN dbo.RiskAssessments AS r
                ON r.ThreatID = t.ThreatID
            WHERE NOT EXISTS (
                SELECT 1
                FROM dbo.ThreatIncidentEvents AS tie
                WHERE tie.EventID = e.EventID
            )
            GROUP BY
                t.ThreatID,
                t.ThreatType,
                e.EventID,
                e.AssetID,
                e.Source,
                e.EventTimestamp
            ORDER BY
                t.ThreatType,
                e.Source,
                e.AssetID,
                e.EventTimestamp,
                e.EventID
            """
        )

        rows = list(cursor.fetchall())

        # Include related failed-login events as evidence when a
        # brute-force threat has been detected.
        existing_event_ids = {row[2] for row in rows}

        for row in list(rows):
            threat_type = row[1]

            if str(threat_type).lower() != "brute_force":
                continue

            _, _, event_id, asset_id, source, timestamp, _ = row

            if asset_id is None or not source or timestamp is None:
                continue

            cursor.execute(
                """
                SELECT
                    e.EventID,
                    e.AssetID,
                    e.Source,
                    e.EventTimestamp
                FROM dbo.SecurityEvents AS e
                WHERE e.AssetID = ?
                  AND e.Source = ?
                  AND LOWER(e.EventType) IN (
                      'login_failure',
                      'failed_login',
                      'failed login'
                  )
                  AND e.EventTimestamp >= DATEADD(
                      MINUTE, -?, CAST(? AS DATETIME2)
                  )
                  AND e.EventTimestamp <= CAST(? AS DATETIME2)
                  AND NOT EXISTS (
                      SELECT 1
                      FROM dbo.ThreatIncidentEvents AS tie
                      WHERE tie.EventID = e.EventID
                  )
                ORDER BY e.EventTimestamp, e.EventID
                """,
                (
                    asset_id,
                    source,
                    INCIDENT_WINDOW_MINUTES,
                    timestamp,
                    timestamp,
                ),
            )

            related_events = cursor.fetchall()

            for related in related_events:
                (
                    related_event_id,
                    related_asset_id,
                    related_source,
                    related_timestamp,
                ) = related

                if related_event_id in existing_event_ids:
                    continue

                rows.append(
                    (
                        None,
                        "brute_force",
                        related_event_id,
                        related_asset_id,
                        related_source,
                        related_timestamp,
                        0,
                    )
                )
                existing_event_ids.add(related_event_id)

        buckets = {}

        for row in rows:
            (
                threat_id,
                threat_type,
                event_id,
                asset_id,
                source,
                timestamp,
                score,
            ) = row

            key = (threat_type, source, asset_id)

            buckets.setdefault(key, []).append({
                "threat_id": threat_id,
                "event_id": event_id,
                "threat_type": threat_type,
                "asset_id": asset_id,
                "source": source,
                "timestamp": timestamp,
                "risk_score": int(score or 0),
            })

        for (threat_type, source, asset_id), items in buckets.items():
            groups = []
            current_group = []

            for item in items:
                if not current_group:
                    current_group = [item]
                    continue

                first_timestamp = current_group[0]["timestamp"]

                if item["timestamp"] - first_timestamp <= timedelta(
                    minutes=INCIDENT_WINDOW_MINUTES
                ):
                    current_group.append(item)
                else:
                    groups.append(current_group)
                    current_group = [item]

            if current_group:
                groups.append(current_group)

            for group in groups:
                if len(group) < 2:
                    events_not_grouped += len(group)
                    continue

                first_seen = min(
                    item["timestamp"] for item in group
                )
                last_seen = max(
                    item["timestamp"] for item in group
                )
                risk_score = min(
                    100,
                    max(item["risk_score"] for item in group),
                )

                summary = (
                    f"{threat_type}: {len(group)} related events from "
                    f"{source or 'unknown source'} within "
                    f"{INCIDENT_WINDOW_MINUTES} minutes"
                )[:500]

                cursor.execute(
                    """
                    INSERT INTO dbo.ThreatIncidents
                    (
                        ThreatType,
                        Source,
                        AssetID,
                        FirstSeen,
                        LastSeen,
                        EventCount,
                        RiskScore,
                        Status,
                        Summary
                    )
                    OUTPUT INSERTED.IncidentID
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'Open', ?)
                    """,
                    (
                        threat_type,
                        source,
                        asset_id,
                        first_seen,
                        last_seen,
                        len(group),
                        risk_score,
                        summary,
                    ),
                )

                incident_id = cursor.fetchone()[0]

                for item in group:
                    cursor.execute(
                        """
                        INSERT INTO dbo.ThreatIncidentEvents
                            (IncidentID, EventID)
                        VALUES (?, ?)
                        """,
                        (incident_id, item["event_id"]),
                    )
                    events_linked += 1

                # Audit the incident creation in the same transaction.
                cursor.execute(
                    """
                    INSERT INTO dbo.IncidentAuditLog
                        (IncidentID, ActionType, Actor, Details)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        incident_id,
                        "Incident Created",
                        "CyberNexus System",
                        f"Grouped {len(group)} related events; "
                        f"risk score: {risk_score}",
                    ),
                )

                incidents_created += 1

        connection.commit()

        return {
            "incidents_created": incidents_created,
            "events_linked": events_linked,
            "events_not_grouped": events_not_grouped,
        }

    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def update_incident_status(
    incident_id: int,
    status: str,
) -> dict:
    """Update an incident status and record the change."""

    if incident_id < 1:
        raise ValueError("Incident ID must be positive.")

    if not isinstance(status, str):
        raise ValueError("Status must be a valid string.")

    normalized_status = status.strip().title()

    if normalized_status not in ALLOWED_INCIDENT_STATUSES:
        raise ValueError(
            "Status must be Open, Investigating, Resolved, or Closed."
        )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE dbo.ThreatIncidents
            SET Status = ?
            WHERE IncidentID = ?
            """,
            (normalized_status, incident_id),
        )

        if cursor.rowcount == 0:
            raise LookupError(
                f"Incident {incident_id} was not found."
            )

        # Record the status change in the same transaction.
        cursor.execute(
            """
            INSERT INTO dbo.IncidentAuditLog
                (IncidentID, ActionType, Actor, Details)
            VALUES (?, ?, ?, ?)
            """,
            (
                incident_id,
                "Incident Status Updated",
                "CyberNexus Analyst",
                f"Incident status changed to {normalized_status}",
            ),
        )

        connection.commit()

        return {
            "incident_id": incident_id,
            "status": normalized_status,
            "message": "Incident status updated successfully.",
        }

    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def add_investigation_note(
    incident_id: int,
    analyst_name: str,
    note_text: str,
) -> dict:
    """Save an investigation note and audit the action."""

    if incident_id < 1:
        raise ValueError("Incident ID must be positive.")

    if not isinstance(analyst_name, str):
        raise ValueError("Analyst name must be a string.")

    if not isinstance(note_text, str):
        raise ValueError("Note text must be a string.")

    analyst_name = analyst_name.strip()
    note_text = note_text.strip()

    if not analyst_name or len(analyst_name) > 100:
        raise ValueError(
            "Analyst name must contain 1–100 characters."
        )

    if not note_text or len(note_text) > 2000:
        raise ValueError(
            "Note must contain 1–2000 characters."
        )

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
            raise LookupError(
                f"Incident {incident_id} was not found."
            )

        cursor.execute(
            """
            INSERT INTO dbo.IncidentInvestigationNotes
                (IncidentID, AnalystName, NoteText)
            OUTPUT INSERTED.NoteID, INSERTED.CreatedAt
            VALUES (?, ?, ?)
            """,
            (incident_id, analyst_name, note_text),
        )

        row = cursor.fetchone()
        note_id = row[0]
        created_at = row[1]

        # Audit the note creation without storing the full note twice.
        cursor.execute(
            """
            INSERT INTO dbo.IncidentAuditLog
                (IncidentID, ActionType, Actor, Details)
            VALUES (?, ?, ?, ?)
            """,
            (
                incident_id,
                "Investigation Note Added",
                analyst_name,
                f"Investigation note {note_id} added",
            ),
        )

        connection.commit()

        return {
            "note_id": note_id,
            "incident_id": incident_id,
            "analyst_name": analyst_name,
            "note_text": note_text,
            "created_at": created_at.isoformat(),
            "message": "Investigation note saved successfully.",
        }

    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def get_investigation_notes(incident_id: int) -> dict:
    """Retrieve investigation notes for an incident."""

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
            raise LookupError(
                f"Incident {incident_id} was not found."
            )

        cursor.execute(
            """
            SELECT
                NoteID,
                AnalystName,
                NoteText,
                CreatedAt
            FROM dbo.IncidentInvestigationNotes
            WHERE IncidentID = ?
            ORDER BY CreatedAt DESC, NoteID DESC
            """,
            (incident_id,),
        )

        notes = [
            {
                "note_id": row[0],
                "analyst_name": row[1],
                "note_text": row[2],
                "created_at": row[3].isoformat(),
            }
            for row in cursor.fetchall()
        ]

        return {
            "incident_id": incident_id,
            "count": len(notes),
            "notes": notes,
        }

    finally:
        connection.close()

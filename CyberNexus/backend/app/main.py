
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Body

from app.services.database import get_connection

from app.services.asset_monitor import (
    discover_local_asset,
    discover_network_assets,
    verify_network_assets,
)

from app.services.asset_registry import (
    register_asset,
    register_discovered_asset,
    update_device_verification,
    save_monitoring_history,
    get_monitoring_history,
    list_assets,
    mark_offline_assets,
)

from app.services.threat_analyzer import analyze_pending_events

from app.services.incident_manager import (
    group_existing_threats,
    update_incident_status,
    add_investigation_note,
    get_investigation_notes,
)

from app.services.forensic_evidence import (
    collect_incident_evidence,
    verify_incident_evidence,
)


async def monitoring_loop():
    while True:
        try:
            local_asset = discover_local_asset()
            register_asset(local_asset)

            candidates = discover_network_assets()

            for asset in candidates:
                try:
                    register_discovered_asset(asset)
                except Exception as exc:
                    print(f"Asset registration error: {exc}")

            verified_assets = verify_network_assets()

            for asset in verified_assets:
                try:
                    update_device_verification(asset)
                    save_monitoring_history(
                        asset["ip_address"],
                        asset["reachability"],
                    )
                except Exception as exc:
                    print(
                        f"Monitoring update error for "
                        f"{asset.get('ip_address')}: {exc}"
                    )

            mark_offline_assets(timeout_seconds=120)

        except Exception as exc:
            print(f"Continuous monitoring error: {exc}")

        await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(monitoring_loop())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="CyberNexus API",
    description=(
        "Asset Discovery, Continuous Monitoring, Threat Detection, "
        "Incident Management, and Forensic Evidence"
    ),
    version="1.5.0",
    lifespan=lifespan,
)


@app.get("/")
def home():
    return {"message": "CyberNexus API is running"}


@app.get("/api/assets/local")
def get_local_asset():
    return discover_local_asset()


@app.post("/api/assets/refresh")
def refresh_local_asset():
    return register_asset(discover_local_asset())


@app.get("/api/assets")
def get_assets():
    return list_assets()


@app.get("/api/assets/discover")
def discover_network():
    assets = discover_network_assets()
    return {"count": len(assets), "assets": assets}


@app.post("/api/assets/discover/save")
def save_discovered_assets():
    candidates = discover_network_assets()
    saved = []
    errors = []

    for asset in candidates:
        try:
            saved.append(register_discovered_asset(asset))
        except Exception as exc:
            errors.append({
                "ip_address": asset.get("ip_address"),
                "error": str(exc),
            })

    return {
        "discovered": len(candidates),
        "saved_or_existing": len(saved),
        "errors": errors,
        "assets": saved,
    }


@app.post("/api/assets/verify")
def verify_network_devices():
    assets = verify_network_assets()
    updated = []
    errors = []

    for asset in assets:
        try:
            updated.append(update_device_verification(asset))
        except Exception as exc:
            errors.append({
                "ip_address": asset.get("ip_address"),
                "error": str(exc),
            })

    return {
        "discovered": len(assets),
        "updated": len(updated),
        "errors": errors,
        "results": updated,
    }


@app.get("/api/assets/monitoring-history")
def get_asset_monitoring_history(limit: int = 100):
    if limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Limit must be at least 1",
        )

    history = get_monitoring_history(limit)
    return {"count": len(history), "history": history}


@app.post("/api/assets/check-offline")
def check_offline_assets(timeout_seconds: int = 120):
    if timeout_seconds < 1:
        raise HTTPException(
            status_code=400,
            detail="timeout_seconds must be at least 1",
        )

    affected = mark_offline_assets(timeout_seconds)

    return {
        "message": "Offline asset check completed",
        "assets_marked_inactive": affected,
    }


@app.post("/api/threats/analyze")
def analyze_threats(limit: int = 100):
    if limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Limit must be at least 1",
        )

    try:
        return analyze_pending_events(limit)
    except Exception as exc:
        print(f"Threat analysis error: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Threat analysis failed. Check the backend logs.",
        ) from exc


@app.post("/api/incidents/group")
def group_threat_incidents():
    try:
        return group_existing_threats()
    except Exception as exc:
        print(f"Incident grouping error: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Incident grouping failed. Check the backend logs.",
        ) from exc


@app.post("/api/incidents/{incident_id}/evidence/collect")
def collect_forensic_evidence(incident_id: int):
    try:
        return collect_incident_evidence(incident_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        print(f"Forensic evidence collection error: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Evidence collection failed. Check backend logs.",
        ) from exc


@app.get("/api/incidents/{incident_id}/evidence/verify")
def verify_forensic_evidence(incident_id: int):
    try:
        return verify_incident_evidence(incident_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        print(f"Forensic evidence verification error: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Evidence verification failed. Check backend logs.",
        ) from exc


@app.patch("/api/incidents/{incident_id}/status")
def change_incident_status(
    incident_id: int,
    status: str = Body(..., embed=True),
):
    try:
        return update_incident_status(incident_id, status)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        print(f"Incident status update error: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Status update failed. Check backend logs.",
        ) from exc


@app.post("/api/incidents/{incident_id}/notes")
def create_investigation_note(
    incident_id: int,
    analyst_name: str = Body(...),
    note_text: str = Body(...),
):
    try:
        return add_investigation_note(
            incident_id,
            analyst_name,
            note_text,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        print(f"Investigation note error: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Could not save investigation note.",
        ) from exc


@app.get("/api/incidents/{incident_id}/notes")
def list_investigation_notes(incident_id: int):
    try:
        return get_investigation_notes(incident_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        print(f"Investigation history error: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve investigation notes.",
        ) from exc


@app.get("/api/incidents/{incident_id}/audit")
def get_incident_audit_log(incident_id: int, limit: int = 100):
    """Retrieve audit records for an incident."""

    if incident_id < 1:
        raise HTTPException(
            status_code=400,
            detail="Incident ID must be positive",
        )

    if limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Limit must be at least 1",
        )

    connection = None

    try:
        connection = get_connection()
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
            raise HTTPException(
                status_code=404,
                detail="Incident not found",
            )

        cursor.execute(
            """
            SELECT TOP (?)
                AuditID,
                IncidentID,
                ActionType,
                Actor,
                Details,
                CreatedAt
            FROM dbo.IncidentAuditLog
            WHERE IncidentID = ?
            ORDER BY AuditID DESC
            """,
            (limit, incident_id),
        )

        rows = cursor.fetchall()

        records = [
            {
                "audit_id": row[0],
                "incident_id": row[1],
                "action_type": row[2],
                "actor": row[3],
                "details": row[4],
                "created_at": (
                    row[5].isoformat() if row[5] else None
                ),
            }
            for row in rows
        ]

        return {
            "incident_id": incident_id,
            "count": len(records),
            "audit_log": records,
        }

    except HTTPException:
        raise
    except Exception as exc:
        print(f"Incident audit log error: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve incident audit log.",
        ) from exc
    finally:
        if connection is not None:
            connection.close()

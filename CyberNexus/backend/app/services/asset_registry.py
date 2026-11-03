from datetime import datetime, timezone, timedelta
from threading import Lock

_assets = {}
_lock = Lock()

OFFLINE_THRESHOLD_SECONDS = 60


def register_asset(asset: dict) -> dict:
    """Register an asset or update its latest discovery information."""
    now = datetime.now(timezone.utc)
    asset_id = asset.get("mac_address") or asset.get("hostname")

    if not asset_id:
        raise ValueError("Asset must have a MAC address or hostname")

    with _lock:
        previous = _assets.get(asset_id, {})
        record = {
            **previous,
            **asset,
            "asset_id": asset_id,
            "status": "online",
            "first_seen": previous.get("first_seen", now.isoformat()),
            "last_seen": now.isoformat(),
        }
        _assets[asset_id] = record
        return record.copy()


def list_assets() -> list:
    """Return registered assets with updated online/offline status."""
    now = datetime.now(timezone.utc)

    with _lock:
        results = []

        for asset in _assets.values():
            last_seen = datetime.fromisoformat(asset["last_seen"])
            seconds_since_seen = (now - last_seen).total_seconds()

            updated_asset = asset.copy()
            updated_asset["status"] = (
                "offline"
                if seconds_since_seen > OFFLINE_THRESHOLD_SECONDS
                else "online"
            )
            updated_asset["seconds_since_seen"] = int(seconds_since_seen)
            results.append(updated_asset)

        return results
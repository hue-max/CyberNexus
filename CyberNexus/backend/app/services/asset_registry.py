
from datetime import datetime, timezone
from threading import Lock

_assets = {}
_lock = Lock()


def register_asset(asset: dict) -> dict:
    """Register an asset or update its latest discovery information."""
    now = datetime.now(timezone.utc).isoformat()
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
            "first_seen": previous.get("first_seen", now),
            "last_seen": now,
        }
        _assets[asset_id] = record
        return record.copy()


def list_assets() -> list:
    """Return all assets discovered during this server session."""
    with _lock:
        return [asset.copy() for asset in _assets.values()]

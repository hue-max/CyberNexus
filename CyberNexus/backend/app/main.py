
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.services.asset_monitor import (
    discover_local_asset,
    discover_network_assets,
)
from app.services.asset_registry import (
    register_asset,
    register_discovered_asset,
    list_assets,
    mark_offline_assets,
)


async def monitoring_loop():
    while True:
        try:
            asset = discover_local_asset()
            register_asset(asset)
            mark_offline_assets(timeout_seconds=120)
        except Exception as exc:
            print(f"Background monitoring error: {exc}")

        await asyncio.sleep(30)


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
    description="Asset Discovery and Monitoring",
    version="1.0.0",
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
    return {
        "count": len(assets),
        "assets": assets,
    }


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

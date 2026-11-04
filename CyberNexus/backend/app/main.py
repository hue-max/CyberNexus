
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

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


async def monitoring_loop():
    while True:
        try:
            # Refresh the local laptop heartbeat
            local_asset = discover_local_asset()
            register_asset(local_asset)

            # Discover and register network candidates
            candidates = discover_network_assets()

            for asset in candidates:
                register_discovered_asset(asset)

            # Check reachability and refresh MAC information
            verified_assets = verify_network_assets()

            for asset in verified_assets:
                update_device_verification(asset)

                # Save reachability history
                save_monitoring_history(
                    asset["ip_address"],
                    asset["reachability"],
                )

            # Mark only stale Active records as inactive
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
    description="Asset Discovery and Continuous Monitoring",
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

    for asset in candidates:
        saved.append(register_discovered_asset(asset))

    return {
        "discovered": len(candidates),
        "saved_or_existing": len(saved),
        "assets": saved,
    }


@app.post("/api/assets/verify")
def verify_network_devices():
    assets = verify_network_assets()
    results = []

    for asset in assets:
        results.append(update_device_verification(asset))

    return {
        "discovered": len(assets),
        "updated": len(results),
        "results": results,
    }


@app.get("/api/assets/monitoring-history")
def get_asset_monitoring_history(limit: int = 100):
    if limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Limit must be at least 1",
        )

    history = get_monitoring_history(limit)

    return {
        "count": len(history),
        "history": history,
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


import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

from app.services.asset_monitor import discover_local_asset
from app.services.asset_registry import (
    register_asset,
    list_assets,
    mark_offline_assets,
)


async def monitoring_loop():
    while True:
        try:
            # Keep this laptop's heartbeat updated
            asset = discover_local_asset()
            register_asset(asset)

            # Mark assets inactive after 120 seconds
            mark_offline_assets(timeout_seconds=120)

        except Exception as exc:
            print(f"Background monitoring error: {exc}")

        await asyncio.sleep(30)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(monitoring_loop())
    yield
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

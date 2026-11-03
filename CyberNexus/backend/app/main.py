from fastapi import FastAPI
from app.services.asset_monitor import discover_local_asset
from app.services.asset_registry import register_asset, list_assets

app = FastAPI(
    title="CyberNexus API",
    description="Asset Discovery and Monitoring",
    version="1.0.0",
)


@app.get("/")
def home():
    return {"message": "CyberNexus API is running"}


@app.get("/api/assets/local")
def get_local_asset():
    return discover_local_asset()


@app.post("/api/assets/refresh")
def refresh_local_asset():
    asset = discover_local_asset()
    return register_asset(asset)


@app.get("/api/assets")
def get_assets():
    return list_assets()
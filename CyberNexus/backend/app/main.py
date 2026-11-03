
from fastapi import FastAPI
from app.services.asset_monitor import discover_local_asset

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

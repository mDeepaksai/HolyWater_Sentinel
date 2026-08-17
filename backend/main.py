from fastapi import FastAPI

from app.database import engine, Base

from app.routes.auth import router as auth_router
from app.routes.village import router as village_router
from app.routes.sensor import router as sensor_router
from app.routes.simulation import router as simulation_router


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(
    bind=engine
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="HolyWater Sentinel API",
    description=(
        "Smart Community Health Monitoring and "
        "Early Warning System for Water-Borne Diseases"
    ),
    version="1.0.0"
)


# ============================================================
# ROUTES
# ============================================================

app.include_router(auth_router)

app.include_router(village_router)

app.include_router(sensor_router)

app.include_router(simulation_router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "HolyWater Sentinel API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "authentication": "/auth",
        "villages": "/villages",
        "sensors": "/sensors",
        "simulation": "/simulation"
    }
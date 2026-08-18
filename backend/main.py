from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine

# ============================================================
# IMPORT ALL MODELS
# ============================================================

from app.models.user import User
from app.models.village import Village
from app.models.sensor_reading import SensorReading
from app.models.weather_data import WeatherData
from app.models.health_data import HealthData
from app.models.risk_prediction import RiskPrediction
from app.models.risk_factor import RiskFactor
from app.models.alert import Alert

# ============================================================
# IMPORT ALL ROUTES
# ============================================================

from app.routes.auth import router as auth_router
from app.routes.village import router as village_router
from app.routes.sensor import router as sensor_router
from app.routes.simulation import router as simulation_router
from app.routes.weather import router as weather_router
from app.routes.health import router as health_router
from app.routes.risk import router as risk_router
from app.routes.alert import router as alert_router

# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(bind=engine)

# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="HolyWater Sentinel API",
    description=(
        "Smart Village Water-Health Early Warning System "
        "for monitoring water quality and predicting health risks."
    ),
    version="1.0.0"
)

# ============================================================
# CORS — allows the frontend dashboard (opened as a local file
# or served from a different origin) to call this API.
# Tighten allow_origins to your actual frontend URL before any
# public/production deployment.
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# REGISTER ROUTES
# ============================================================

app.include_router(auth_router)
app.include_router(village_router)
app.include_router(sensor_router)
app.include_router(simulation_router)
app.include_router(weather_router)
app.include_router(health_router)
app.include_router(risk_router)
app.include_router(alert_router)

# ============================================================
# ROOT ENDPOINT
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
        "simulation": "/simulation",
        "weather": "/weather",
        "health": "/health",
        "risk": "/risk",
        "alerts": "/alerts"
    }
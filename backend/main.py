from fastapi import FastAPI

from app.database import Base, engine

from app.models.sensor import SensorReading
from app.models.village import Village

from app.routes.sensor import router as sensor_router
from app.routes.village import router as village_router


# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(
    title="HolyWater Sentinel API",
    description="Smart Village Water-Health Early Warning System",
    version="1.0.0"
)


# Register API routes
app.include_router(sensor_router)
app.include_router(village_router)


# Root endpoint
@app.get("/")
def root():
    return {
        "project": "HolyWater Sentinel",
        "status": "running",
        "message": "Water-Health Early Warning API"
    }
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sensor_reading import SensorReading
from app.models.village import Village
from app.schemas.sensor import (
    SensorReadingCreate,
    SensorReadingResponse,
)
from app.routes.auth import get_current_user


router = APIRouter(
    prefix="/sensors",
    tags=["Water Sensors"]
)


# ---------------------------------------------------------
# GET ALL SENSOR READINGS
# ---------------------------------------------------------
@router.get(
    "/readings",
    response_model=list[SensorReadingResponse]
)
def get_sensor_readings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    readings = (
        db.query(SensorReading)
        .order_by(SensorReading.recorded_at.desc())
        .all()
    )

    return readings


# ---------------------------------------------------------
# CREATE SENSOR READING
# ---------------------------------------------------------
@router.post(
    "/readings",
    response_model=SensorReadingResponse,
    status_code=201
)
def create_sensor_reading(
    reading: SensorReadingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Check whether village exists
    village = (
        db.query(Village)
        .filter(Village.id == reading.village_id)
        .first()
    )

    if not village:
        raise HTTPException(
            status_code=404,
            detail="Village not found"
        )

    sensor_reading = SensorReading(
        village_id=reading.village_id,
        temperature=reading.temperature,
        ph=reading.ph,
        turbidity=reading.turbidity,
        tds=reading.tds,
        latitude=reading.latitude,
        longitude=reading.longitude
    )

    db.add(sensor_reading)
    db.commit()
    db.refresh(sensor_reading)

    return sensor_reading


# ---------------------------------------------------------
# GET SENSOR READING BY ID
# ---------------------------------------------------------
@router.get(
    "/readings/{reading_id}",
    response_model=SensorReadingResponse
)
def get_sensor_reading(
    reading_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    reading = (
        db.query(SensorReading)
        .filter(SensorReading.id == reading_id)
        .first()
    )

    if not reading:
        raise HTTPException(
            status_code=404,
            detail="Sensor reading not found"
        )

    return reading


# ---------------------------------------------------------
# GET SENSOR READINGS FOR A VILLAGE
# ---------------------------------------------------------
@router.get(
    "/village/{village_id}",
    response_model=list[SensorReadingResponse]
)
def get_village_sensor_readings(
    village_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Check village exists
    village = (
        db.query(Village)
        .filter(Village.id == village_id)
        .first()
    )

    if not village:
        raise HTTPException(
            status_code=404,
            detail="Village not found"
        )

    readings = (
        db.query(SensorReading)
        .filter(SensorReading.village_id == village_id)
        .order_by(SensorReading.recorded_at.desc())
        .all()
    )

    return readings
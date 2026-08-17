from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sensor_reading import SensorReading
from app.schemas.sensor import (
    SensorReadingCreate,
    SensorReadingResponse
)
from app.routes.auth import get_current_user


router = APIRouter(
    prefix="/sensors",
    tags=["Water Sensors"]
)


# ============================================================
# CREATE SENSOR READING
# ============================================================

@router.post(
    "/readings",
    response_model=SensorReadingResponse
)
def create_sensor_reading(
    data: SensorReadingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    reading = SensorReading(
        village_id=data.village_id,
        temperature=data.temperature,
        ph=data.ph,
        turbidity=data.turbidity,
        tds=data.tds
    )

    db.add(reading)
    db.commit()
    db.refresh(reading)

    return reading


# ============================================================
# GET ALL READINGS
# ============================================================

@router.get(
    "/readings",
    response_model=list[SensorReadingResponse]
)
def get_sensor_readings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return (
        db.query(SensorReading)
        .order_by(
            SensorReading.timestamp.desc()
        )
        .all()
    )


# ============================================================
# GET SINGLE READING
# ============================================================

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
        .filter(
            SensorReading.id == reading_id
        )
        .first()
    )

    if not reading:
        raise HTTPException(
            status_code=404,
            detail="Sensor reading not found"
        )

    return reading


# ============================================================
# GET VILLAGE READINGS
# ============================================================

@router.get(
    "/village/{village_id}",
    response_model=list[SensorReadingResponse]
)
def get_village_sensor_readings(
    village_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    readings = (
        db.query(SensorReading)
        .filter(
            SensorReading.village_id == village_id
        )
        .order_by(
            SensorReading.timestamp.desc()
        )
        .all()
    )

    return readings
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.sensor import SensorReading
from app.schemas.sensor import SensorReading as SensorReadingSchema


router = APIRouter(
    prefix="/sensor",
    tags=["Sensor"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/readings")
def receive_sensor_reading(
    data: SensorReadingSchema,
    db: Session = Depends(get_db)
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

    return {
        "status": "success",
        "message": "Sensor data stored successfully",
        "reading_id": reading.id
    }
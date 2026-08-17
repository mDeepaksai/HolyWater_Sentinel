import random

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sensor_reading import SensorReading
from app.routes.auth import get_current_user


router = APIRouter(
    prefix="/simulation",
    tags=["Sensor Simulation"]
)


# ============================================================
# GENERATE SENSOR VALUES
# ============================================================

def generate_sensor_data():

    temperature = round(
        random.uniform(20, 38),
        2
    )

    ph = round(
        random.uniform(5.5, 9.0),
        2
    )

    turbidity = round(
        random.uniform(0.5, 15.0),
        2
    )

    tds = round(
        random.uniform(100, 800),
        2
    )

    return {
        "temperature": temperature,
        "ph": ph,
        "turbidity": turbidity,
        "tds": tds
    }


# ============================================================
# SIMULATE WITHOUT DATABASE
# ============================================================

@router.post("/sensor")
def simulate_sensor(
    current_user=Depends(get_current_user)
):

    data = generate_sensor_data()

    return {
        "message": "Sensor data simulated successfully",
        "data": data
    }


# ============================================================
# SIMULATE + SAVE TO DATABASE
# ============================================================

@router.post("/sensor/{village_id}")
def simulate_sensor_for_village(
    village_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    data = generate_sensor_data()

    reading = SensorReading(
        village_id=village_id,
        temperature=data["temperature"],
        ph=data["ph"],
        turbidity=data["turbidity"],
        tds=data["tds"]
    )

    db.add(reading)
    db.commit()
    db.refresh(reading)

    return {
        "message": "Simulated sensor reading saved",
        "village_id": village_id,
        "reading": reading
    }
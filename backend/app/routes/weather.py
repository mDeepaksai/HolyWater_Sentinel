from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.village import Village
from app.models.weather_data import WeatherData
from app.services.weather_service import get_weather


router = APIRouter(
    prefix="/weather",
    tags=["Weather"]
)


@router.post("/{village_id}")
def fetch_and_store_weather(
    village_id: int,
    db: Session = Depends(get_db)
):
    village = db.query(Village).filter(
        Village.id == village_id
    ).first()

    if not village:
        raise HTTPException(
            status_code=404,
            detail="Village not found"
        )

    if village.latitude is None or village.longitude is None:
        raise HTTPException(
            status_code=400,
            detail="Village latitude and longitude are required"
        )

    try:
        weather = get_weather(
            village.latitude,
            village.longitude
        )

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Weather API error: {str(e)}"
        )

    weather_record = WeatherData(
        village_id=village.id,
        rainfall=weather["rainfall"],
        temperature=weather["temperature"],
        humidity=weather["humidity"],
        wind_speed=weather["wind_speed"]
    )

    db.add(weather_record)
    db.commit()
    db.refresh(weather_record)

    return {
        "message": "Weather data fetched and stored successfully",
        "village_id": village.id,
        "weather": {
            "temperature": weather_record.temperature,
            "humidity": weather_record.humidity,
            "rainfall": weather_record.rainfall,
            "wind_speed": weather_record.wind_speed
        }
    }
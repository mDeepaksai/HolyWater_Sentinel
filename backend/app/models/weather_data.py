from datetime import datetime

from sqlalchemy import Column, Integer, Float, DateTime

from app.database import Base


class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)

    village_id = Column(Integer, nullable=False, index=True)

    rainfall = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)

    wind_speed = Column(Float, nullable=True)

    recorded_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
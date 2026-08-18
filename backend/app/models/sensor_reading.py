from datetime import datetime

from sqlalchemy import Column, Integer, Float, DateTime
from app.database import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)

    village_id = Column(Integer, nullable=False, index=True)

    temperature = Column(Float, nullable=False)
    ph = Column(Float, nullable=False)
    turbidity = Column(Float, nullable=False)
    tds = Column(Float, nullable=False)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    recorded_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
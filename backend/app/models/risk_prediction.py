from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime
)

from app.database import Base


class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, index=True)

    village_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    sensor_reading_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    weather_data_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    risk_level = Column(
        String(20),
        nullable=False,
        index=True
    )

    risk_probability = Column(
        Float,
        nullable=False
    )

    model_name = Column(
        String(100),
        nullable=False,
        default="RandomForest"
    )

    model_version = Column(
        String(50),
        nullable=True
    )

    predicted_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
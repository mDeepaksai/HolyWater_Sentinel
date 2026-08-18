from datetime import date, datetime

from sqlalchemy import Column, Integer, String, Date, DateTime

from app.database import Base


class HealthData(Base):
    __tablename__ = "health_data"

    id = Column(Integer, primary_key=True, index=True)

    village_id = Column(Integer, nullable=False, index=True)

    disease_name = Column(
        String(150),
        nullable=False
    )

    case_count = Column(
        Integer,
        nullable=False,
        default=0
    )

    report_date = Column(
        Date,
        nullable=False,
        index=True
    )

    source = Column(
        String(150),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
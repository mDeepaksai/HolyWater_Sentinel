from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime
)

from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    village_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    risk_prediction_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    alert_type = Column(
        String(50),
        nullable=False
    )

    risk_level = Column(
        String(20),
        nullable=False,
        index=True
    )

    message = Column(
        Text,
        nullable=False
    )

    recommended_action = Column(
        Text,
        nullable=True
    )

    is_resolved = Column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    resolved_at = Column(
        DateTime,
        nullable=True
    )
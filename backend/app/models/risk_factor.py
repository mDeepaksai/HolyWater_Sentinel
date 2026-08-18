from sqlalchemy import Column, Integer, Float, String, Text

from app.database import Base


class RiskFactor(Base):
    __tablename__ = "risk_factors"

    id = Column(Integer, primary_key=True, index=True)

    risk_prediction_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    factor_name = Column(
        String(100),
        nullable=False
    )

    feature_value = Column(
        Float,
        nullable=True
    )

    contribution = Column(
        Float,
        nullable=True
    )

    explanation = Column(
        Text,
        nullable=True
    )
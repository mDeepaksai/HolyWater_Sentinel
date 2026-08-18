from datetime import datetime

from pydantic import BaseModel


class RiskFactorResponse(BaseModel):

    id: int
    risk_prediction_id: int
    factor_name: str
    feature_value: float | None
    contribution: float | None
    explanation: str | None

    class Config:
        from_attributes = True


class RiskPredictionResponse(BaseModel):

    id: int
    village_id: int
    sensor_reading_id: int | None
    weather_data_id: int | None
    risk_level: str
    risk_probability: float
    model_name: str
    model_version: str | None
    predicted_at: datetime

    class Config:
        from_attributes = True


class RiskPredictionWithFactors(BaseModel):

    prediction: RiskPredictionResponse
    factors: list[RiskFactorResponse]
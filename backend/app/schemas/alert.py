from datetime import datetime

from pydantic import BaseModel


class AlertResponse(BaseModel):

    id: int
    village_id: int
    risk_prediction_id: int | None
    alert_type: str
    risk_level: str
    message: str
    recommended_action: str | None
    is_resolved: bool
    created_at: datetime
    resolved_at: datetime | None

    class Config:
        from_attributes = True


class AlertCheckResponse(BaseModel):

    village_id: int
    alert_created: bool
    alert: AlertResponse | None
    reasons: list[str]
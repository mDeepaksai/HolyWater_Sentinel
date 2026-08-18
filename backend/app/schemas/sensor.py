from datetime import datetime

from pydantic import BaseModel, Field


class SensorReadingCreate(BaseModel):

    village_id: int

    temperature: float = Field(
        ...,
        ge=-10,
        le=60
    )

    ph: float = Field(
        ...,
        ge=0,
        le=14
    )

    turbidity: float = Field(
        ...,
        ge=0
    )

    tds: float = Field(
        ...,
        ge=0
    )


class SensorReadingResponse(BaseModel):

    id: int
    village_id: int
    temperature: float
    ph: float
    turbidity: float
    tds: float
    latitude: float | None = None
    longitude: float | None = None
    recorded_at: datetime

    class Config:
        from_attributes = True
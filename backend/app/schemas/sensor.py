from pydantic import BaseModel, Field


class SensorReading(BaseModel):
    village_id: int

    temperature: float = Field(..., ge=-10, le=60)
    ph: float = Field(..., ge=0, le=14)
    turbidity: float = Field(..., ge=0)
    tds: float = Field(..., ge=0)
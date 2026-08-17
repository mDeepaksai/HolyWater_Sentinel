from pydantic import BaseModel
from typing import Optional


class VillageCreate(BaseModel):
    name: str
    district: str
    state: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class VillageResponse(BaseModel):
    id: int
    name: str
    district: str
    state: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        from_attributes = True
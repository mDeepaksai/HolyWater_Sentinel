from pydantic import BaseModel, Field


class VillageCreate(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100
    )

    district: str = Field(
        min_length=2,
        max_length=100
    )

    state: str = Field(
        min_length=2,
        max_length=100
    )

    population: int | None = Field(
        default=None,
        ge=0
    )

    latitude: float | None = None

    longitude: float | None = None


class VillageResponse(BaseModel):

    id: int
    name: str
    district: str
    state: str
    population: int | None
    latitude: float | None
    longitude: float | None

    class Config:
        from_attributes = True
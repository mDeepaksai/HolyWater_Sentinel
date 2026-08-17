from pydantic import BaseModel, EmailStr, Field
from typing import Literal


class RegisterRequest(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=100
    )

    role: Literal[
        "GOVERNMENT",
        "HEALTH_WORKER",
        "FIELD_WORKER",
        "NGO_LAB"
    ]

    organization: str | None = Field(
        default=None,
        max_length=150
    )


class UserResponse(BaseModel):

    id: int
    name: str
    email: EmailStr
    role: str
    organization: str | None
    is_verified: bool

    class Config:
        from_attributes = True
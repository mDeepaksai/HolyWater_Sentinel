from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        index=True,
        nullable=False
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(30),
        nullable=False
    )

    organization = Column(
        String(150),
        nullable=True
    )

    is_verified = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
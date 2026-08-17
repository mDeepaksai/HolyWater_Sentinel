from sqlalchemy import Column, Integer, String, Float

from app.database import Base


class Village(Base):
    __tablename__ = "villages"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
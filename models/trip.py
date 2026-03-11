from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from db.base import Base
import enum

class TripStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    cancelled = "cancelled"

class Trip(Base):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True, index=True)
    from_city = Column(String, nullable=False)
    to_city = Column(String, nullable=False)
    datetime = Column(DateTime, nullable=False)
    price = Column(Integer, nullable=False)
    seats_total = Column(Integer, nullable=False)
    seats_available = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    status = Column(Enum(TripStatus), default=TripStatus.active, nullable=False)

    driver = relationship("User", back_populates="trips")
    car = relationship("Car")


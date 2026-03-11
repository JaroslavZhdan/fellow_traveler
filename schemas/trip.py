from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class TripCreate(BaseModel):
    from_city: str
    to_city: str
    datetime: datetime
    price: int
    seats_total: int
    description: Optional[str]
    car_id: int

class TripOut(BaseModel):
    id: int
    from_city: str
    to_city: str
    datetime: datetime
    price: int
    seats_total: int
    seats_available: int
    description: Optional[str]
    driver_id: int
    car_id: int
    status: str

    model_config = ConfigDict(from_attributes=True)

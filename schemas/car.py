from pydantic import BaseModel, ConfigDict


class CarCreate(BaseModel):
    brand: str
    model: str
    year: int
    color: str
    plate_number: str

class CarOut(BaseModel):
    id: int
    brand: str
    model: str
    year: int
    color: str
    plate_number: str
    image_path: str | None
    owner_id: int

    model_config = ConfigDict(from_attributes=True)

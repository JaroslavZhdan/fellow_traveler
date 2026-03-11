from pydantic import BaseModel, ConfigDict


class RequestCreate(BaseModel):
    trip_id: int

class RequestOut(BaseModel):
    id: int
    passenger_id: int
    trip_id: int
    status: str

    model_config = ConfigDict(from_attributes=True)

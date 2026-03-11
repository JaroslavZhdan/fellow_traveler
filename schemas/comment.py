from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CommentCreate(BaseModel):
    body: str

class CommentOut(BaseModel):
    id: int
    trip_id: int
    author_id: int
    body: str
    created_at: datetime
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)
from pydantic import BaseModel

class RatingCreate(BaseModel):
    score: int

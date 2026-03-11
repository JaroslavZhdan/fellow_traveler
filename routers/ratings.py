from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from core.deps import get_db, get_current_user
from schemas.rating import RatingCreate
from models.rating import DriverRating
from models.trip import Trip

router = APIRouter(prefix="/trips/{trip_id}/rating", tags=["ratings"])

@router.post("/", status_code=201)
async def rate_trip(trip_id: int, payload: RatingCreate, session: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    # защита от повторных оценок
    q = await session.execute(select(DriverRating).where(DriverRating.rater_id == user.id, DriverRating.trip_id == trip_id))
    if q.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Вы уже оценили эту поездку")
    q2 = await session.execute(select(Trip).where(Trip.id == trip_id))
    trip = q2.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Поездка не найдена")
    rating = DriverRating(trip_id=trip_id, rater_id=user.id, driver_id=trip.driver_id, score=payload.score)
    session.add(rating)
    await session.commit()
    return {"ok": True}

@router.get("/", response_model=dict)
async def get_trip_rating(trip_id: int, session: AsyncSession = Depends(get_db)):
    q = await session.execute(select(func.avg(DriverRating.score), func.count(DriverRating.id)).where(DriverRating.trip_id == trip_id))
    avg, count = q.one()
    return {"avg": float(avg or 0), "count": int(count or 0)}

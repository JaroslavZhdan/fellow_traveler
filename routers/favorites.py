from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from core.deps import get_db, get_current_user
from models.favorite import TripFavorite
from models.trip import Trip

router = APIRouter(prefix="/favorites", tags=["favorites"])

@router.get("/", response_model=list)
async def list_favorites(session: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    q = await session.execute(select(TripFavorite).where(TripFavorite.user_id == user.id))
    favs = q.scalars().all()
    # вернуть подробности поездок
    trip_ids = [f.trip_id for f in favs]
    if not trip_ids:
        return []
    q2 = await session.execute(select(Trip).where(Trip.id.in_(trip_ids)))
    return q2.scalars().all()

@router.post("/", status_code=201)
async def add_favorite(trip_id: int, session: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    q = await session.execute(select(TripFavorite).where(TripFavorite.user_id == user.id, TripFavorite.trip_id == trip_id))
    if q.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Уже в избранном")
    q2 = await session.execute(select(Trip).where(Trip.id == trip_id))
    if not q2.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Поездка не найдена")
    fav = TripFavorite(user_id=user.id, trip_id=trip_id)
    session.add(fav)
    await session.commit()
    return {"ok": True}

@router.delete("/{trip_id}")
async def remove_favorite(trip_id: int, session: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    q = await session.execute(select(TripFavorite).where(TripFavorite.user_id == user.id, TripFavorite.trip_id == trip_id))
    fav = q.scalar_one_or_none()
    if not fav:
        raise HTTPException(status_code=404, detail="Не найдено в избранном")
    await session.execute(delete(TripFavorite).where(TripFavorite.id == fav.id))
    await session.commit()
    return {"ok": True}

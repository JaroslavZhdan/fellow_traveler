from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from core.deps import get_db, get_current_user, require_role
from schemas.trip import TripCreate, TripOut
from models.trip import Trip, TripStatus
from models.car import Car

router = APIRouter(prefix="/trips", tags=["trips"])

@router.post("/", response_model=TripOut, status_code=201)
async def create_trip(payload: TripCreate, session: AsyncSession = Depends(get_db), user = Depends(require_role("DRIVER"))):
    q = await session.execute(select(Car).where(Car.id == payload.car_id))
    car = q.scalar_one_or_none()
    if not car or car.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Автомобиль не найден или не принадлежит водителю")
    trip = Trip(
        from_city=payload.from_city,
        to_city=payload.to_city,
        datetime=payload.datetime,
        price=payload.price,
        seats_total=payload.seats_total,
        seats_available=payload.seats_total,
        description=payload.description,
        driver_id=user.id,
        car_id=payload.car_id,
        status=TripStatus.active
    )
    session.add(trip)
    await session.commit()
    await session.refresh(trip)
    return trip

@router.get("/", response_model=List[TripOut])
async def list_trips(
    session: AsyncSession = Depends(get_db),
    from_city: Optional[str] = Query(None),
    to_city: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    status: Optional[TripStatus] = Query(None),
    sort: Optional[str] = Query("datetime.desc")
):
    query = select(Trip)
    filters = []
    if from_city:
        filters.append(Trip.from_city.ilike(f"%{from_city}%"))
    if to_city:
        filters.append(Trip.to_city.ilike(f"%{to_city}%"))
    if status:
        filters.append(Trip.status == status)
    if filters:
        query = query.where(and_(*filters))
    if sort:
        field, _, direction = sort.partition('.')
        if field == "price":
            order_col = Trip.price
        else:
            order_col = Trip.datetime
        if direction == "desc":
            query = query.order_by(order_col.desc())
        else:
            query = query.order_by(order_col.asc())
    q = await session.execute(query)
    return q.scalars().all()

@router.get("/{trip_id}", response_model=TripOut)
async def get_trip(trip_id: int, session: AsyncSession = Depends(get_db)):
    q = await session.execute(select(Trip).where(Trip.id == trip_id))
    trip = q.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Поездка не найдена")
    return trip

@router.post("/{trip_id}/status")
async def change_status(trip_id: int, status: str, session: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    q = await session.execute(select(Trip).where(Trip.id == trip_id))
    trip = q.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Поездка не найдена")
    if trip.driver_id != user.id and user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Нет прав")
    if status not in [s.value for s in TripStatus]:
        raise HTTPException(status_code=400, detail="Неверный статус")
    trip.status = TripStatus(status)
    await session.commit()
    return {"ok": True}

@router.delete("/admin/{trip_id}", dependencies=[Depends(require_role("ADMIN"))])
async def admin_delete_trip(trip_id: int, session: AsyncSession = Depends(get_db)):
    q = await session.execute(select(Trip).where(Trip.id == trip_id))
    trip = q.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Поездка не найдена")
    await session.execute(delete(Trip).where(Trip.id == trip_id))
    await session.commit()
    return {"ok": True}

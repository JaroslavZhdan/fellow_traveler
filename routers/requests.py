from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.deps import get_db, get_current_user
from schemas.request import RequestCreate, RequestOut
from models.trip_request import TripRequest, RequestStatus
from models.trip import Trip

router = APIRouter(prefix="/requests", tags=["requests"])

@router.post("/", response_model=RequestOut, status_code=201)
async def create_request(payload: RequestCreate, session: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    q = await session.execute(select(TripRequest).where(TripRequest.passenger_id == user.id, TripRequest.trip_id == payload.trip_id))
    if q.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Заявка уже отправлена")
    q2 = await session.execute(select(Trip).where(Trip.id == payload.trip_id))
    trip = q2.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Поездка не найдена")
    if trip.seats_available <= 0:
        raise HTTPException(status_code=409, detail="Нет свободных мест")
    req = TripRequest(passenger_id=user.id, trip_id=payload.trip_id)
    session.add(req)
    await session.commit()
    await session.refresh(req)
    return req

@router.get("/me", response_model=list[RequestOut])
async def my_requests(session: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    q = await session.execute(select(TripRequest).where(TripRequest.passenger_id == user.id))
    return q.scalars().all()

@router.get("/trip/{trip_id}", response_model=list[RequestOut])
async def requests_for_trip(trip_id: int, session: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    q = await session.execute(select(Trip).where(Trip.id == trip_id))
    trip = q.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Поездка не найдена")
    if trip.driver_id != user.id and user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Нет прав")
    q2 = await session.execute(select(TripRequest).where(TripRequest.trip_id == trip_id))
    return q2.scalars().all()

@router.post("/{req_id}/approve")
async def approve_request(req_id: int, session: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    q = await session.execute(select(TripRequest).where(TripRequest.id == req_id))
    req = q.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    q2 = await session.execute(select(Trip).where(Trip.id == req.trip_id))
    trip = q2.scalar_one_or_none()
    if trip.driver_id != user.id and user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Нет прав")
    if trip.seats_available <= 0:
        raise HTTPException(status_code=409, detail="Нет мест")
    req.status = RequestStatus.approved
    trip.seats_available -= 1
    await session.commit()
    return {"ok": True}

@router.post("/{req_id}/reject")
async def reject_request(req_id: int, session: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    q = await session.execute(select(TripRequest).where(TripRequest.id == req_id))
    req = q.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    q2 = await session.execute(select(Trip).where(Trip.id == req.trip_id))
    trip = q2.scalar_one_or_none()
    if trip.driver_id != user.id and user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Нет прав")
    if req.status == RequestStatus.approved:
        trip.seats_available += 1
    req.status = RequestStatus.rejected
    await session.commit()
    return {"ok": True}

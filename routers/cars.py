from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from core.deps import get_db, get_current_user, require_role
from schemas.car import CarCreate, CarOut
from models.car import Car
from services.file_service import save_car_image

router = APIRouter(prefix="/cars", tags=["cars"])

@router.post("/", response_model=CarOut, status_code=201)
async def create_car(payload: CarCreate, session: AsyncSession = Depends(get_db), user = Depends(require_role("DRIVER"))):
    car = Car(**payload.model_dump(), owner_id=user.id)
    session.add(car)
    await session.commit()
    await session.refresh(car)
    return car

@router.get("/", response_model=list[CarOut])
async def list_my_cars(session: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    q = await session.execute(select(Car).where(Car.owner_id == user.id))
    return q.scalars().all()

@router.get("/all", response_model=list[CarOut], dependencies=[Depends(require_role("ADMIN"))])
async def list_all_cars(session: AsyncSession = Depends(get_db)):
    q = await session.execute(select(Car))
    return q.scalars().all()

@router.put("/{car_id}", response_model=CarOut)
async def update_car(car_id: int, payload: CarCreate, session: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    q = await session.execute(select(Car).where(Car.id == car_id))
    car = q.scalar_one_or_none()
    if not car:
        raise HTTPException(status_code=404, detail="Автомобиль не найден")
    if car.owner_id != user.id and user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Нет прав")
    await session.execute(update(Car).where(Car.id == car_id).values(**payload.model_dump()))
    await session.commit()
    q2 = await session.execute(select(Car).where(Car.id == car_id))
    return q2.scalar_one()

@router.delete("/{car_id}")
async def delete_car(car_id: int, session: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    q = await session.execute(select(Car).where(Car.id == car_id))
    car = q.scalar_one_or_none()
    if not car:
        raise HTTPException(status_code=404, detail="Автомобиль не найден")
    if car.owner_id != user.id and user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Нет прав")
    await session.execute(delete(Car).where(Car.id == car_id))
    await session.commit()
    return {"ok": True}

@router.post("/{car_id}/image", response_model=CarOut)
async def upload_car_image(car_id: int, image: UploadFile = File(...), session: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    q = await session.execute(select(Car).where(Car.id == car_id))
    car = q.scalar_one_or_none()
    if not car:
        raise HTTPException(status_code=404, detail="Автомобиль не найден")
    if car.owner_id != user.id and user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Нет прав")
    # проверка типа и размера (пример)
    if image.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=400, detail="Неподдерживаемый формат изображения")
    path = await save_car_image(car_id, image)
    car.image_path = path
    await session.commit()
    await session.refresh(car)
    return car

@router.get("/{car_id}", response_model=CarOut)
async def get_car(car_id: int, session: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    q = await session.execute(select(Car).where(Car.id == car_id))
    car = q.scalar_one_or_none()
    if not car:
        raise HTTPException(status_code=404, detail="Автомобиль не найден")
    return car
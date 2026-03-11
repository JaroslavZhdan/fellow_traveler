from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from core.deps import get_db, get_current_user, require_role
from schemas.user import UserOut
from models.user import User, UserRole

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserOut)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserOut)
async def update_profile(payload: dict, session: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if "email" in payload:
        raise HTTPException(status_code=400, detail="Изменение email не поддерживается")
    await session.execute(update(User).where(User.id == current_user.id).values(**payload))
    await session.commit()
    q = await session.execute(select(User).where(User.id == current_user.id))
    user = q.scalar_one()
    return user

@router.get("/", response_model=list[UserOut], dependencies=[Depends(require_role("ADMIN"))])
async def list_users(session: AsyncSession = Depends(get_db)):
    q = await session.execute(select(User))
    return q.scalars().all()

@router.post("/{user_id}/block", dependencies=[Depends(require_role("ADMIN"))])
async def block_user(user_id: int, session: AsyncSession = Depends(get_db)):
    q = await session.execute(select(User).where(User.id == user_id))
    user = q.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.is_blocked = True
    await session.commit()
    return {"ok": True}

@router.post("/{user_id}/unblock", dependencies=[Depends(require_role("ADMIN"))])
async def unblock_user(user_id: int, session: AsyncSession = Depends(get_db)):
    q = await session.execute(select(User).where(User.id == user_id))
    user = q.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.is_blocked = False
    await session.commit()
    return {"ok": True}

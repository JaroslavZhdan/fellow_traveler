from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from core.deps import get_db, require_role
from models.user import User
from models.trip import Trip
from models.comment import TripComment

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_role("ADMIN"))])

@router.get("/users")
async def admin_list_users(session: AsyncSession = Depends(get_db)):
    q = await session.execute(select(User))
    return q.scalars().all()

@router.get("/trips")
async def admin_list_trips(session: AsyncSession = Depends(get_db)):
    q = await session.execute(select(Trip))
    return q.scalars().all()

@router.post("/comments/{comment_id}/hide")
async def admin_hide_comment(comment_id: int, session: AsyncSession = Depends(get_db)):
    q = await session.execute(select(TripComment).where(TripComment.id == comment_id))
    comment = q.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    comment.is_deleted = True
    await session.commit()
    return {"ok": True}

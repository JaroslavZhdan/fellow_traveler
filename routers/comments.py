from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from core.deps import get_db, get_current_user, require_role
from schemas.comment import CommentCreate, CommentOut
from models.comment import TripComment

router = APIRouter(prefix="/trips/{trip_id}/comments", tags=["comments"])

@router.post("/", response_model=CommentOut, status_code=201)
async def add_comment(trip_id: int, payload: CommentCreate, session: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    comment = TripComment(trip_id=trip_id, author_id=user.id, body=payload.body)
    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    return comment

@router.get("/", response_model=list[CommentOut])
async def list_comments(trip_id: int, session: AsyncSession = Depends(get_db)):
    q = await session.execute(select(TripComment).where(TripComment.trip_id == trip_id, TripComment.is_deleted == False))
    return q.scalars().all()

# Админ: мягкое удаление комментария
@router.delete("/admin/{comment_id}/delete", dependencies=[Depends(require_role("ADMIN"))])
async def admin_delete_comment(trip_id: int, comment_id: int, session: AsyncSession = Depends(get_db)):
    q = await session.execute(select(TripComment).where(TripComment.id == comment_id, TripComment.trip_id == trip_id))
    comment = q.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    comment.is_deleted = True
    await session.commit()
    return {"ok": True}

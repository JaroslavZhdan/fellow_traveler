from fastapi import HTTPException, status
from sqlalchemy import select
from core.security import hash_password, verify_password, create_access_token
from core.deps import get_db
from schemas.auth import LoginIn, RegisterIn, Token
from models.user import UserRole
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from core.deps import get_current_user
from schemas.user import UserOut
from models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut, status_code=201)
async def register(payload: RegisterIn, session: AsyncSession = Depends(get_db)):
    q = await session.execute(select(User).where(User.email == payload.email))
    if q.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    user = User(
        email=payload.email,
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=UserRole(payload.role)
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@router.post("/login", response_model=Token)
async def login(payload: LoginIn, session: AsyncSession = Depends(get_db)):
    q = await session.execute(select(User).where(User.email == payload.email))
    user = q.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные учетные данные")
    if user.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Пользователь заблокирован")
    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user

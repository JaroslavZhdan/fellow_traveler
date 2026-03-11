from typing import Union

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from models.user import User
from core.security import decode_token
from sqlalchemy import select

security = HTTPBearer()

async def get_db():
    async for s in get_session():
        yield s


async def get_current_user(
        credentials: Union[HTTPAuthorizationCredentials, str] = Depends(security),
        session: AsyncSession = Depends(get_db)
) -> User:

    if isinstance(credentials, str):
        if not credentials.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный формат заголовка Authorization",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = credentials.split(" ")[1]
    else:
        token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пустой токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или просроченный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        result = await session.execute(
            select(User).where(User.id == int(user_id))
        )
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if hasattr(user, 'is_blocked') and user.is_blocked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Пользователь заблокирован",
            )

        return user

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный формат ID в токене",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"Ошибка в get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера",
        )

def require_role(role: str):
    async def _require(user=Depends(get_current_user)):
        if user.role.value != role and user.role.value != "ADMIN":
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return _require
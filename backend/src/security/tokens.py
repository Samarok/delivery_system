from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from jose import JWTError, jwt

from core.config import settings
from core.constants import (
    USER_ROLE_ADMIN,
    USER_ROLE_DISPATCHER,
    USER_ROLE_DRIVER,
    USER_ROLE_RECEIVER,
)
from db.session import get_db
from models.users import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недействительный токен",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_user_admin_required(
    current_user: User = Depends(get_current_user),
) -> User:
    """Получение текущего пользователя с проверкой прав администратора"""
    if current_user.role.name != USER_ROLE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав. Требуется роль администратора",
        )
    return current_user


async def get_current_user_dispatcher_required(
    current_user: User = Depends(get_current_user),
) -> User:
    """Получение текущего пользователя с проверкой прав диспетчера"""
    if current_user.role.name not in [USER_ROLE_ADMIN, USER_ROLE_DISPATCHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав. Требуется роль диспетчера",
        )
    return current_user


async def get_current_user_driver_required(
    current_user: User = Depends(get_current_user),
) -> User:
    """Получение текущего пользователя с проверкой прав водителя"""
    if current_user.role.name not in [USER_ROLE_ADMIN, USER_ROLE_DRIVER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав. Требуется роль водителя",
        )
    return current_user


async def get_current_user_receiver_required(
    current_user: User = Depends(get_current_user),
) -> User:
    """Получение текущего пользователя с проверкой прав получателя"""
    if current_user.role.name not in [USER_ROLE_ADMIN, USER_ROLE_RECEIVER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав. Требуется роль приемщика",
        )
    return current_user


async def get_current_user_receiver_or_driver_required(
    current_user: User = Depends(get_current_user),
) -> User:
    """Получение текущего пользователя с проверкой прав получателя или водителя"""
    if current_user.role.name not in [
        USER_ROLE_ADMIN,
        USER_ROLE_DRIVER,
        USER_ROLE_RECEIVER,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав. Требуется роль водителя или приемщика",
        )
    return current_user

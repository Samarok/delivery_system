from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload
import bcrypt

from models.users import User, Role
from schemas.users import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserWithRole,
    RoleCreate,
    RoleUpdate,
    RoleResponse,
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


async def create_user(user: UserCreate, db) -> UserResponse:
    """Создание нового пользователя с хешированием пароля"""
    # Проверяем, существует ли пользователь с таким именем
    existing_user = await get_user_by_username(user.username, db)
    if existing_user:
        raise ValueError(f"User with username {user.username} already exists")

    # Хешируем пароль
    hashed_password = get_password_hash(user.password)

    # Создаем пользователя
    db_user = User(
        username=user.username,
        password=hashed_password,
        role_id=user.role_id,
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return UserResponse.from_orm(db_user)


async def get_user_by_username(username: str, db) -> Optional[User]:
    """Получение пользователя по имени"""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_id(user_id: int, db) -> Optional[User]:
    """Получение пользователя по ID"""
    return await db.get(User, user_id)


async def update_user(
    user_id: int, user_data: UserUpdate, db
) -> Optional[UserResponse]:
    """Обновление пользователя"""
    db_user = await get_user_by_id(user_id, db)
    if not db_user:
        return None

    # Обновляем только переданные поля
    update_data = user_data.dict(exclude_unset=True)

    # Если обновляется пароль - хешируем его
    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])

    for key, value in update_data.items():
        setattr(db_user, key, value)

    await db.commit()
    await db.refresh(db_user)
    return UserResponse.from_orm(db_user)


async def delete_user(user_id: int, db) -> bool:
    """Удаление пользователя по ID"""
    db_user = await get_user_by_id(user_id, db)
    if db_user:
        await db.delete(db_user)
        await db.commit()
        return True
    return False


async def get_all_users(db) -> List[User]:
    """Получение всех пользователей"""
    result = await db.execute(select(User))
    return result.scalars().all()


async def get_users_with_roles(db) -> List[UserWithRole]:
    """Получение пользователей с информацией о ролях"""
    result = await db.execute(select(User).options(selectinload(User.role)))
    users = result.scalars().all()

    return [
        UserWithRole(
            id=user.id, username=user.username, role=RoleResponse.from_orm(user.role)
        )
        for user in users
    ]


async def authenticate_user(username: str, password: str, db) -> Optional[User]:
    """Аутентификация пользователя"""
    user = await get_user_by_username(username, db)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


async def get_user_with_role(user_id: int, db) -> Optional[UserWithRole]:
    """Получение пользователя с информацией о роли"""
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user:
        return UserWithRole(
            id=user.id,
            username=user.username,
            role=RoleResponse.from_orm(user.role),
            role_id=user.role_id,
        )
    return None


# Утилиты для ролей
async def create_role(role: RoleCreate, db) -> RoleResponse:
    """Создание новой роли"""
    # Проверяем, существует ли роль с таким именем
    existing_role = await get_role_by_name(role.name, db)
    if existing_role:
        raise ValueError(f"Role with name {role.name} already exists")

    db_role = Role(name=role.name)
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    return RoleResponse.from_orm(db_role)


async def get_role_by_name(role_name: str, db) -> Optional[Role]:
    """Получение роли по имени"""
    result = await db.execute(select(Role).where(Role.name == role_name))
    return result.scalar_one_or_none()


async def get_role_by_id(role_id: int, db) -> Optional[Role]:
    """Получение роли по ID"""
    return await db.get(Role, role_id)


async def update_role(
    role_id: int, role_data: RoleUpdate, db
) -> Optional[RoleResponse]:
    """Обновление роли"""
    db_role = await get_role_by_id(role_id, db)
    if not db_role:
        return None

    for key, value in role_data.dict(exclude_unset=True).items():
        setattr(db_role, key, value)

    await db.commit()
    await db.refresh(db_role)
    return RoleResponse.from_orm(db_role)


async def delete_role(role_id: int, db) -> bool:
    """Удаление роли"""
    db_role = await get_role_by_id(role_id, db)
    if db_role:
        await db.delete(db_role)
        await db.commit()
        return True
    return False


async def get_all_roles(db) -> List[RoleResponse]:
    """Получение всех ролей"""
    result = await db.execute(select(Role))
    roles = result.scalars().all()
    return [RoleResponse.from_orm(role) for role in roles]


async def get_users_by_role(role_id: int, db) -> List[UserResponse]:
    """Получение пользователей по роли"""
    result = await db.execute(select(User).where(User.role_id == role_id))
    users = result.scalars().all()
    return [UserResponse.from_orm(user) for user in users]


async def get_user_with_role_orm(user_id: int, db):
    """Получение пользователя с ролью (ORM модель)"""
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id)
    )
    return result.scalar_one_or_none()

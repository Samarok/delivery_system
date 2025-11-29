from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.users import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserList,
    UserWithRole,
    RoleCreate,
    RoleResponse,
    RoleList,
)
from services.users import user_service, role_service
from security.dependencies import get_admin_user, get_current_user
from db.session import get_db
from models.users import User


router = APIRouter()


# === AUTHENTICATED ROUTES ===
@router.get("/me", response_model=UserWithRole)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Получение информации о текущем пользователе"""
    return await user_service.get_user(current_user.id, db)


# === ADMIN ROUTES ===
@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Создание пользователя (только c токеном для создания)"""
    return await user_service.create_user(user_data, db)


@router.get("/", response_model=UserList)
async def get_all_users(
    current_user: User = Depends(get_admin_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """Получение всех пользователей (только для администраторов)"""
    return await user_service.get_all_users_service(db)


@router.get("/{user_id}", response_model=UserWithRole)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Получение пользователя по ID (только для администраторов)"""
    return await user_service.get_user(user_id, db)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Обновление пользователя (только для администраторов)"""
    return await user_service.update_user(user_id, user_data, db)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Удаление пользователя (только для администраторов)"""
    return await user_service.delete_user(user_id, db)


# === ROLE MANAGEMENT (ADMIN ONLY) ===
@router.post("/roles/", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Создание роли (только для администраторов)"""
    return await role_service.create_role(role_data, db)


@router.get("/roles/", response_model=RoleList)
async def get_all_roles(
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Получение всех ролей (только для администраторов)"""
    return await role_service.get_all_roles_service(db)


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Получение роли по ID (только для администраторов)"""
    return await role_service.get_role(role_id, db)

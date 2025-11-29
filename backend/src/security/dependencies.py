from fastapi import Depends
from models.users import User
from security.tokens import (
    get_current_user,
    get_current_user_admin_required,
    get_current_user_dispatcher_required,
    get_current_user_driver_required,
    get_current_user_receiver_required,
)


async def get_current_user(
    current_user: User = Depends(get_current_user),
):
    """Зависимость для проверки прав пользователя"""
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_user_admin_required),
):
    """Зависимость для проверки прав администратора"""
    return current_user


async def get_dispatcher_user(
    current_user: User = Depends(get_current_user_dispatcher_required),
):
    """Зависимость для проверки прав диспетчера"""
    return current_user


async def get_receiver_user(
    current_user: User = Depends(get_current_user_receiver_required),
):
    """Зависимость для проверки прав получателя"""
    return current_user


async def get_driver_user(
    current_user: User = Depends(get_current_user_driver_required),
):
    """Зависимость для проверки прав водителя"""
    return current_user

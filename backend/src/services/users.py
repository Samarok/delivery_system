import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from jose import JWTError, jwt

from schemas.users import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserList,
    UserLogin,
    UserWithRole,
    RoleCreate,
    RoleList,
    RoleUpdate,
    RoleResponse,
    TokenResponse,
)
from utils.users import (
    create_user as create_user_util,
    get_user_by_username,
    update_user as update_user_util,
    delete_user as delete_user_util,
    get_users_with_roles,
    authenticate_user,
    get_user_with_role,
    get_user_with_role_orm,
    create_role as create_role_util,
    get_role_by_name,
    get_role_by_id,
    update_role as update_role_util,
    delete_role as delete_role_util,
    get_all_roles,
    get_users_by_role,
)
from core.config import settings
from core.constants import (
    ERROR_USER_NOT_FOUND,
    ERROR_ROLE_NOT_FOUND,
    ERROR_INVALID_CREDENTIALS,
    MESSAGE_USER_DELETED,
)


logger = logging.getLogger(__name__)


class UserService:
    """Сервис для работы с пользователями"""

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        """Создание JWT токена"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict):
        """Создание refresh токена"""
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode = data.copy()
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def create_tokens_pair(user_id: int):
        """Создание пары access и refresh токенов"""
        access_token = UserService.create_access_token(data={"user_id": user_id})
        refresh_token = UserService.create_refresh_token(data={"user_id": user_id})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    async def verify_refresh_token(refresh_token: str, db: AsyncSession):
        """Проверка refresh токена"""
        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id: int = payload.get("user_id")
            if user_id is None:
                return None
        except JWTError:
            return None

        user = await get_user_with_role_orm(user_id, db)  # Используем ORM модель
        return user

    @staticmethod
    async def login_user(user_data: UserLogin, db: AsyncSession) -> TokenResponse:
        """Аутентификация пользователя"""
        user = await authenticate_user(user_data.username, user_data.password, db)
        if not user:
            logger.warning(f"Неудачная попытка входа: Username='{user_data.username}'")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_INVALID_CREDENTIALS,
                headers={"WWW-Authenticate": "Bearer"},
            )
        tokens = UserService.create_tokens_pair(user.id)

        user_with_role = await get_user_with_role(user.id, db)
        if not user_with_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при получении данных пользователя",
            )

        logger.info(
            f"Успешный вход пользователя: ID={user.id}, Username='{user.username}'"
        )
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            user=user_with_role,
        )

    @staticmethod
    async def refresh_user_token(
        refresh_token: str, db: AsyncSession
    ) -> Dict[str, str]:
        """
        Обновление access токена
        """
        user = await UserService.verify_refresh_token(refresh_token, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный refresh токен",
            )

        # Создаем новый access токен
        new_access_token = UserService.create_access_token(data={"user_id": user.id})
        return {"access_token": new_access_token, "token_type": "bearer"}

    @staticmethod
    async def create_user(user_data: UserCreate, db: AsyncSession) -> UserResponse:
        """
        Создание нового пользователя
        """
        try:
            new_user = await create_user_util(user_data, db)
            logger.info(
                f"Пользователь создан: ID={new_user.id}, Username='{new_user.username}', Role ID={new_user.role_id}"
            )
            return new_user
        except ValueError as e:
            logger.warning(
                f"Попытка создания дублирующего пользователя: Username='{user_data.username}'"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при создании пользователя: {str(e)}",
            )

    @staticmethod
    async def get_user(user_id: int, db: AsyncSession) -> UserWithRole:
        """
        Получение пользователя по ID с информацией о роли (Pydantic модель)
        """
        user = await get_user_with_role(user_id, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_USER_NOT_FOUND,
            )
        return user

    @staticmethod
    async def get_user_orm(user_id: int, db: AsyncSession):
        """
        Получение пользователя по ID (ORM модель)
        """
        user = await get_user_with_role_orm(user_id, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_USER_NOT_FOUND,
            )
        return user

    @staticmethod
    async def get_user_by_username_service(
        username: str, db: AsyncSession
    ) -> UserWithRole:
        """
        Получение пользователя по имени с информацией о роли
        """
        user = await get_user_by_username(username, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_USER_NOT_FOUND,
            )

        return await get_user_with_role(user.id, db)

    @staticmethod
    async def update_user(
        user_id: int, user_data: UserUpdate, db: AsyncSession
    ) -> UserResponse:
        """
        Обновление пользователя
        """
        updated_user = await update_user_util(user_id, user_data, db)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_USER_NOT_FOUND,
            )
        return updated_user

    @staticmethod
    async def delete_user(user_id: int, db: AsyncSession) -> Dict[str, Any]:
        """
        Удаление пользователя
        """
        success = await delete_user_util(user_id, db)
        if not success:
            logger.warning(
                f"Не удалось удалить пользователя: ID={user_id} (Пользователь не найден)"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_USER_NOT_FOUND,
            )

        return {"message": MESSAGE_USER_DELETED, "user_id": user_id}

    @staticmethod
    async def get_all_users_service(db: AsyncSession) -> UserList:
        """
        Получение всех пользователей с ролями
        """
        users_with_roles = await get_users_with_roles(db)
        return UserList(users=users_with_roles, total=len(users_with_roles))

    @staticmethod
    async def get_users_by_role_service(
        role_id: int, db: AsyncSession
    ) -> List[UserWithRole]:
        """
        Получение пользователей по роли
        """
        users_responses = await get_users_by_role(role_id, db)
        users_with_roles = []

        for user_response in users_responses:
            user_with_role = await get_user_with_role(user_response.id, db)
            if user_with_role:
                users_with_roles.append(user_with_role)

        return users_with_roles


class RoleService:
    """Сервис для работы с ролями"""

    # Класс RoleService остается без изменений...
    @staticmethod
    async def create_role(role_data: RoleCreate, db: AsyncSession) -> RoleResponse:
        """
        Создание новой роли
        """
        try:
            new_role = await create_role_util(role_data, db)
            logger.info(f"Роль создана: ID={new_role.id}, Name='{new_role.name}'")
            return new_role
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при создании роли: {str(e)}",
            )

    @staticmethod
    async def get_role(role_id: int, db: AsyncSession) -> RoleResponse:
        """
        Получение роли по ID
        """
        role = await get_role_by_id(role_id, db)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_ROLE_NOT_FOUND,
            )
        return RoleResponse.from_orm(role)

    @staticmethod
    async def get_role_by_name_service(
        role_name: str, db: AsyncSession
    ) -> RoleResponse:
        """
        Получение роли по имени
        """
        role = await get_role_by_name(role_name, db)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_ROLE_NOT_FOUND,
            )
        return RoleResponse.from_orm(role)

    @staticmethod
    async def update_role(
        role_id: int, role_data: RoleUpdate, db: AsyncSession
    ) -> RoleResponse:
        """
        Обновление роли
        """
        updated_role = await update_role_util(role_id, role_data, db)
        if not updated_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_ROLE_NOT_FOUND,
            )
        return updated_role

    @staticmethod
    async def delete_role(role_id: int, db: AsyncSession) -> Dict[str, Any]:
        """
        Удаление роли
        """
        success = await delete_role_util(role_id, db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_ROLE_NOT_FOUND,
            )

        return {"message": "Роль успешно удалена", "role_id": role_id}

    @staticmethod
    async def get_all_roles_service(db: AsyncSession) -> RoleList:
        """
        Получение всех ролей
        """
        roles = await get_all_roles(db)
        return RoleList(roles=roles, total=len(roles))


# Создаем экземпляры сервисов для удобного импорта
user_service = UserService()
role_service = RoleService()

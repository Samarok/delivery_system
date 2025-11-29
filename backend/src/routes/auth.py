from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.users import UserLogin, TokenResponse
from services.users import user_service
from db.session import get_db

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """Аутентификация пользователя через OAuth2"""
    user_login = UserLogin(username=form_data.username, password=form_data.password)
    return await user_service.login_user(user_login, db)


@router.post("/refresh")
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """Обновление access токена"""
    return await user_service.refresh_user_token(refresh_token, db)

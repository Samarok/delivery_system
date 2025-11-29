from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi.security import HTTPBearer


class Settings(BaseSettings):
    # DB
    DB_PATH: str = "./test.db"

    # Security
    SECRET_KEY: str = "SECRET"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def db_url(self):
        return f"sqlite+aiosqlite:///{self.DB_PATH}"

    @property
    def security_scheme(self):
        return HTTPBearer()


settings = Settings()

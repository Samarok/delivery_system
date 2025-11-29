from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine

from core.config import settings


def get_engine() -> AsyncEngine:
    return create_async_engine(
        settings.db_url, connect_args={"check_same_thread": False}
    )


AsyncSessionLocal = sessionmaker(bind=get_engine(), class_=AsyncSession)

Base = declarative_base()

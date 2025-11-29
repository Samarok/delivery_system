from sqlalchemy import select

from db.engine import get_engine, Base
from db.session import AsyncSessionLocal
from models.users import User, Role
from models.deliveries import Delivery, DeliveryStatus
from models.sensors import SensorData
from core.constants import (
    USER_ROLE_ADMIN,
    USER_ROLE_DRIVER,
    USER_ROLE_RECEIVER,
    USER_ROLE_DISPATCHER,
    DELIVERY_STATUS_PENDING,
    DELIVERY_STATUS_IN_TRANSIT,
    DELIVERY_STATUS_DELIVERED,
    DELIVERY_STATUS_COMPLETED,
)
from utils.users import create_user
from schemas.users import UserCreate


async def create_tables():
    engine = get_engine()

    async with engine.begin() as conn:
        # Создаем все таблицы
        await conn.run_sync(Base.metadata.create_all)

    # Создаем начальные данные
    async with AsyncSessionLocal() as session:
        # Создаем роли, если их нет
        result = await session.execute(select(Role))
        if not result.scalars().first():
            roles = [
                Role(name=USER_ROLE_ADMIN),
                Role(name=USER_ROLE_DRIVER),
                Role(name=USER_ROLE_RECEIVER),
                Role(name=USER_ROLE_DISPATCHER),
            ]
            session.add_all(roles)
            await session.commit()

        # Создаем статусы доставок, если их нет
        result = await session.execute(select(DeliveryStatus))
        if not result.scalars().first():
            statuses = [
                DeliveryStatus(name=DELIVERY_STATUS_PENDING),
                DeliveryStatus(name=DELIVERY_STATUS_IN_TRANSIT),
                DeliveryStatus(name=DELIVERY_STATUS_DELIVERED),
                DeliveryStatus(name=DELIVERY_STATUS_COMPLETED),
            ]
            session.add_all(statuses)
            await session.commit()

        # Создаем пользователей, если их нет
        result = await session.execute(select(User))
        if not result.scalars().first():
            await create_user(
                UserCreate(username="admin", password="admin", role_id=1), session
            )
            await session.commit()

    await engine.dispose()
    print("Таблицы и начальные данные успешно созданы!")

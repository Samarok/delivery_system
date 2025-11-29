from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from models.deliveries import Delivery, DeliveryStatus
from schemas.deliveries import (
    DeliveryCreate,
    DeliveryUpdate,
    DeliveryResponse,
    DeliveryWithRelations,
    DeliveryStatusResponse,
    DeliveryFlutterResponse,
    DeliveryStats,
)
from core.constants import DEFAULT_PAGE_SIZE, DELIVERY_STATUS_COMPLETED


async def create_delivery(delivery: DeliveryCreate, db) -> DeliveryResponse:
    """Создание новой доставки"""
    db_delivery = Delivery(
        status_id=delivery.status_id,
        driver_id=delivery.driver_id,
        receiver_id=delivery.receiver_id,
        current_temperature=delivery.current_temperature,
        created_at=datetime.utcnow(),
    )

    db.add(db_delivery)
    await db.commit()
    await db.refresh(db_delivery)

    return DeliveryResponse.from_orm(db_delivery)


async def get_delivery_by_id(delivery_id: int, db) -> Optional[Delivery]:
    """Получение доставки по ID"""
    return await db.get(Delivery, delivery_id)


async def get_delivery_with_relations(
    delivery_id: int, db
) -> Optional[DeliveryWithRelations]:
    """Получение доставки со связанными объектами"""
    result = await db.execute(
        select(Delivery)
        .options(
            selectinload(Delivery.driver),
            selectinload(Delivery.receiver),
            selectinload(Delivery.delivery_status),
        )
        .where(Delivery.id == delivery_id)
    )
    delivery = result.scalar_one_or_none()

    if delivery:
        # Создаем упрощенный объект чтобы избежать циклических зависимостей
        return DeliveryWithRelations(
            id=delivery.id,
            status_id=delivery.status_id,
            driver_id=delivery.driver_id,
            receiver_id=delivery.receiver_id,
            current_temperature=delivery.current_temperature,
            created_at=delivery.created_at,
            status=DeliveryStatusResponse(
                id=delivery.delivery_status.id, name=delivery.delivery_status.name
            ),
            driver_name=delivery.driver.username,
            receiver_name=delivery.receiver.username,
        )
    return None


async def get_delivery_for_flutter(
    delivery_id: int, db
) -> Optional[DeliveryFlutterResponse]:
    """Получение доставки в формате для Flutter"""
    result = await db.execute(
        select(Delivery)
        .options(
            selectinload(Delivery.driver),
            selectinload(Delivery.receiver),
            selectinload(Delivery.delivery_status),
        )
        .where(Delivery.id == delivery_id)
    )
    delivery = result.scalar_one_or_none()

    if delivery:
        return DeliveryFlutterResponse(
            id=delivery.id,
            status=delivery.delivery_status.name,
            driver_name=delivery.driver.username,
            receiver_name=delivery.receiver.username,
            current_temperature=delivery.current_temperature,
            created_at=delivery.created_at,
        )
    return None


async def get_all_deliveries(
    db, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE
) -> List[Delivery]:
    """Получение всех доставок"""
    result = await db.execute(
        select(Delivery).order_by(Delivery.created_at.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_all_deliveries_with_relations(
    db, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE
) -> List[DeliveryWithRelations]:
    """Получение всех доставок со связанными объектами"""
    result = await db.execute(
        select(Delivery)
        .options(
            selectinload(Delivery.driver),
            selectinload(Delivery.receiver),
            selectinload(Delivery.delivery_status),
        )
        .order_by(Delivery.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    deliveries = result.scalars().all()

    delivery_list = []
    for delivery in deliveries:
        delivery_list.append(
            DeliveryWithRelations(
                id=delivery.id,
                status_id=delivery.status_id,
                driver_id=delivery.driver_id,
                receiver_id=delivery.receiver_id,
                current_temperature=delivery.current_temperature,
                created_at=delivery.created_at,
                status=DeliveryStatusResponse(
                    id=delivery.delivery_status.id, name=delivery.delivery_status.name
                ),
                driver_name=delivery.driver.username,
                receiver_name=delivery.receiver.username,
            )
        )

    return delivery_list


async def get_all_deliveries_for_flutter(
    db, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE
) -> List[DeliveryFlutterResponse]:
    """Получение всех доставок для Flutter"""
    result = await db.execute(
        select(Delivery)
        .options(
            selectinload(Delivery.driver),
            selectinload(Delivery.receiver),
            selectinload(Delivery.delivery_status),
        )
        .order_by(Delivery.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    deliveries = result.scalars().all()

    flutter_deliveries = []
    for delivery in deliveries:
        flutter_deliveries.append(
            DeliveryFlutterResponse(
                id=delivery.id,
                status=delivery.delivery_status.name,
                driver_name=delivery.driver.username,
                receiver_name=delivery.receiver.username,
                current_temperature=delivery.current_temperature,
                created_at=delivery.created_at,
            )
        )

    return flutter_deliveries


# Остальные функции остаются без изменений...
async def get_deliveries_by_status(
    status_id: int, db, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE
) -> List[Delivery]:
    """Получение доставок по статусу"""
    result = await db.execute(
        select(Delivery)
        .where(Delivery.status_id == status_id)
        .order_by(Delivery.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_deliveries_by_driver(
    driver_id: int, db, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE
) -> List[Delivery]:
    """Получение доставок по водителю"""
    result = await db.execute(
        select(Delivery)
        .where(Delivery.driver_id == driver_id)
        .order_by(Delivery.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_deliveries_by_receiver(
    receiver_id: int, db, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE
) -> List[Delivery]:
    """Получение доставок по приемщику"""
    result = await db.execute(
        select(Delivery)
        .where(Delivery.receiver_id == receiver_id)
        .order_by(Delivery.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def update_delivery(
    delivery_id: int, delivery_data: DeliveryUpdate, db
) -> Optional[DeliveryResponse]:
    """Обновление доставки"""
    db_delivery = await get_delivery_by_id(delivery_id, db)
    if not db_delivery:
        return None

    update_data = delivery_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_delivery, key, value)

    await db.commit()
    await db.refresh(db_delivery)
    return DeliveryResponse.from_orm(db_delivery)


async def update_delivery_status(
    delivery_id: int, status_id: int, db
) -> Optional[DeliveryResponse]:
    """Обновление статуса доставки"""
    db_delivery = await get_delivery_by_id(delivery_id, db)
    if not db_delivery:
        return None

    db_delivery.status_id = status_id
    await db.commit()
    await db.refresh(db_delivery)
    return DeliveryResponse.from_orm(db_delivery)


async def delete_delivery(delivery_id: int, db) -> bool:
    """Удаление доставки"""
    db_delivery = await get_delivery_by_id(delivery_id, db)
    if db_delivery:
        await db.delete(db_delivery)
        await db.commit()
        return True
    return False


async def get_delivery_stats(db) -> DeliveryStats:
    """Получение статистики по доставкам"""
    # Общее количество доставок
    total_result = await db.execute(select(Delivery))
    total_deliveries = len(total_result.scalars().all())

    # Доставки по статусам
    status_result = await db.execute(
        select(Delivery.status_id, DeliveryStatus.name, func.count(Delivery.id))
        .join(DeliveryStatus, Delivery.status_id == DeliveryStatus.id)
        .group_by(Delivery.status_id, DeliveryStatus.name)
    )
    deliveries_by_status = {
        status_name: count for status_id, status_name, count in status_result.all()
    }

    # Средняя температура
    avg_temp_result = await db.execute(select(func.avg(Delivery.current_temperature)))
    avg_temperature = avg_temp_result.scalar() or 0

    # Завершенные сегодня
    today = datetime.utcnow().date()

    completed_today_result = await db.execute(
        select(Delivery)
        .join(DeliveryStatus)
        .where(
            and_(
                DeliveryStatus.name == DELIVERY_STATUS_COMPLETED,
                Delivery.created_at >= datetime.combine(today, datetime.min.time()),
            )
        )
    )
    completed_today = len(completed_today_result.scalars().all())

    return DeliveryStats(
        total_deliveries=total_deliveries,
        deliveries_by_status=deliveries_by_status,
        average_temperature=float(avg_temperature),
        completed_today=completed_today,
    )


# Утилиты для DeliveryStatus
async def create_delivery_status(status_name: str, db) -> DeliveryStatus:
    """Создание нового статуса доставки"""
    db_status = DeliveryStatus(name=status_name)
    db.add(db_status)
    await db.commit()
    await db.refresh(db_status)
    return db_status


async def get_delivery_status_by_id(status_id: int, db) -> Optional[DeliveryStatus]:
    """Получение статуса доставки по ID"""
    return await db.get(DeliveryStatus, status_id)


async def get_delivery_status_by_name(status_name: str, db) -> Optional[DeliveryStatus]:
    """Получение статуса доставки по имени"""
    result = await db.execute(
        select(DeliveryStatus).where(DeliveryStatus.name == status_name)
    )
    return result.scalar_one_or_none()


async def get_all_delivery_statuses(db) -> List[DeliveryStatus]:
    """Получение всех статусов доставки"""
    result = await db.execute(select(DeliveryStatus))
    return result.scalars().all()


async def update_delivery_status_name(
    status_id: int, new_name: str, db
) -> Optional[DeliveryStatus]:
    """Обновление имени статуса доставки"""
    db_status = await get_delivery_status_by_id(status_id, db)
    if db_status:
        db_status.name = new_name
        await db.commit()
        await db.refresh(db_status)
    return db_status


async def delete_delivery_status(status_id: int, db) -> bool:
    """Удаление статуса доставки"""
    db_status = await get_delivery_status_by_id(status_id, db)
    if db_status:
        await db.delete(db_status)
        await db.commit()
        return True
    return False

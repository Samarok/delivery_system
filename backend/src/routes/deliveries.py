from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.deliveries import (
    DeliveryCreate,
    DeliveryResponse,
    DeliveryUpdate,
    DeliveryWithRelations,
    DeliveryFlutterList,
    DeliveryStatusUpdateRequest,
    DeliveryStats,
    DeliveryList,
)
from services.deliveries import delivery_service
from security.dependencies import (
    get_current_user,
    get_admin_user,
    get_dispatcher_user,
    get_receiver_user,
    get_driver_user,
)
from db.session import get_db
from models.users import User

router = APIRouter()

# === FLUTTER APP ROUTES ===


@router.get("/", response_model=DeliveryFlutterList)
async def get_deliveries_flutter(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """
    Получение доставок для Flutter приложений
    Используется всеми тремя приложениями (водитель, приемщик, диспетчер)
    """
    return await delivery_service.get_all_deliveries_for_flutter(db, skip, limit)


@router.put("/{delivery_id}/status")
async def update_delivery_status_flutter(
    delivery_id: int,
    status_update: DeliveryStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Обновление статуса доставки для Flutter приложений
    Используется водителем и приемщиком
    """
    return await delivery_service.update_delivery_status_service(
        delivery_id, status_update, db
    )


@router.get("/driver/my-deliveries", response_model=DeliveryFlutterList)
async def get_my_deliveries(
    current_user: User = Depends(get_driver_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """Получение доставок текущего водителя"""
    return await delivery_service.get_deliveries_by_driver_service(
        current_user.id, db, skip, limit
    )


@router.get("/receiver/my-deliveries", response_model=DeliveryFlutterList)
async def get_my_receiver_deliveries(
    current_user: User = Depends(get_receiver_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """Получение доставок текущего приемщика"""
    return await delivery_service.get_deliveries_by_receiver_service(
        current_user.id, db, skip, limit
    )


# === DISPATCHER ROUTES ===


@router.get("/stats", response_model=DeliveryStats)
async def get_delivery_stats(
    current_user: User = Depends(get_dispatcher_user),
    db: AsyncSession = Depends(get_db),
):
    """Статистика по доставкам (только для диспетчера)"""
    return await delivery_service.get_delivery_statistics(db)


@router.post("/", response_model=DeliveryResponse)
async def create_delivery(
    delivery_data: DeliveryCreate,
    current_user: User = Depends(get_dispatcher_user),
    db: AsyncSession = Depends(get_db),
):
    """Создание доставки (только для диспетчера)"""
    return await delivery_service.create_delivery(delivery_data, db)


@router.get("/dispatcher/all", response_model=DeliveryList)
async def get_all_deliveries_dispatcher(
    current_user: User = Depends(get_dispatcher_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """Получение всех доставок с полной информацией (только для диспетчера)"""
    return await delivery_service.get_all_deliveries(db, skip, limit)


# === ADMIN ROUTES ===


@router.put("/{delivery_id}", response_model=DeliveryResponse)
async def update_delivery(
    delivery_id: int,
    delivery_data: DeliveryUpdate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Полное обновление доставки (только для администраторов)"""
    return await delivery_service.update_delivery(delivery_id, delivery_data, db)


@router.delete("/{delivery_id}")
async def delete_delivery(
    delivery_id: int,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Удаление доставки (только для администраторов)"""
    return await delivery_service.delete_delivery(delivery_id, db)


@router.get("/{delivery_id}", response_model=DeliveryWithRelations)
async def get_delivery_by_id(
    delivery_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Получение доставки по ID"""
    return await delivery_service.get_delivery(delivery_id, db)


@router.get("/status/{status_id}", response_model=DeliveryList)
async def get_deliveries_by_status(
    status_id: int,
    current_user: User = Depends(get_dispatcher_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """Получение доставок по статусу (только для диспетчера)"""
    return await delivery_service.get_deliveries_by_status_service(
        status_id, db, skip, limit
    )

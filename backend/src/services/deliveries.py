import logging
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from schemas.deliveries import (
    DeliveryCreate,
    DeliveryUpdate,
    DeliveryResponse,
    DeliveryWithRelations,
    DeliveryFlutterResponse,
    DeliveryStatusUpdateRequest,
    DeliveryStats,
    DeliveryList,
    DeliveryFlutterList,
)
from utils.deliveries import (
    get_delivery_by_id,
    create_delivery,
    get_delivery_with_relations,
    get_all_deliveries_with_relations,
    get_deliveries_by_status,
    get_deliveries_by_driver,
    get_deliveries_by_receiver,
    update_delivery,
    update_delivery_status,
    delete_delivery,
    get_delivery_stats,
    create_delivery_status,
    get_delivery_status_by_id,
    get_delivery_status_by_name,
    get_all_delivery_statuses,
    update_delivery_status_name,
    delete_delivery_status,
)
from core.constants import (
    ERROR_DELIVERY_NOT_FOUND,
    DEFAULT_PAGE_SIZE,
    DELIVERY_STATUS_PENDING,
    DELIVERY_STATUS_IN_TRANSIT,
    DELIVERY_STATUS_DELIVERED,
    DELIVERY_STATUS_COMPLETED,
    USER_ROLE_ADMIN,
    USER_ROLE_DRIVER,
    USER_ROLE_RECEIVER,
    USER_ROLE_DISPATCHER,
    ERROR_DELIVERY_STATUS_INVALID_TRANSITION,
    MESSAGE_DELIVERY_STATUS_UPDATED,
)
from models.users import User


logger = logging.getLogger(__name__)


class DeliveryService:
    """Сервис для работы с доставками"""

    @staticmethod
    async def create_delivery(
        delivery_data: DeliveryCreate, db: AsyncSession
    ) -> DeliveryResponse:
        """Создание новой доставки"""
        try:
            new_delivery = await create_delivery(delivery_data, db)
            logger.info(
                f"Доставка создана: ID={new_delivery.id}, Driver ID={new_delivery.driver_id}, Status ID={new_delivery.status_id}"
            )
            return new_delivery
        except Exception as e:
            logger.error(f"Ошибка при создании доставки: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при создании доставки: {str(e)}",
            )

    @staticmethod
    async def get_delivery(delivery_id: int, db: AsyncSession) -> DeliveryWithRelations:
        """Получение доставки по ID"""
        delivery = await get_delivery_with_relations(delivery_id, db)
        if not delivery:
            logger.warning(f"Доставка с ID {delivery_id} не найдена", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_DELIVERY_NOT_FOUND,
            )
        return delivery

    @staticmethod
    async def get_delivery_for_flutter(
        delivery_id: int, db: AsyncSession
    ) -> DeliveryFlutterResponse:
        """Получение доставки в формате для Flutter"""
        delivery = await get_delivery_with_relations(delivery_id, db)
        if not delivery:
            logger.error(f"Доставка с ID {delivery_id} не найдена", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_DELIVERY_NOT_FOUND,
            )

        return DeliveryFlutterResponse(
            id=delivery.id,
            status=delivery.delivery_status.name,
            driver_name=delivery.driver.username,
            receiver_name=delivery.receiver.username,
            current_temperature=delivery.current_temperature,
            created_at=delivery.created_at,
        )

    @staticmethod
    async def get_all_deliveries(
        db: AsyncSession, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE
    ) -> DeliveryList:
        """Получение всех доставок"""
        try:
            deliveries = await get_all_deliveries_with_relations(db, skip, limit)
            return DeliveryList(deliveries=deliveries, total=len(deliveries))
        except Exception as e:
            logger.error(f"Ошибка при получении доставок: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при получении доставок: {str(e)}",
            )

    @staticmethod
    async def get_all_deliveries_for_flutter(
        db: AsyncSession, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE
    ) -> DeliveryFlutterList:
        """Получение всех доставок в формате для Flutter"""
        try:
            deliveries = await get_all_deliveries_with_relations(db, skip, limit)
            flutter_deliveries = [
                DeliveryFlutterResponse(
                    id=delivery.id,
                    status=delivery.delivery_status.name,
                    driver_name=delivery.driver.username,
                    receiver_name=delivery.receiver.username,
                    current_temperature=delivery.current_temperature,
                    created_at=delivery.created_at,
                )
                for delivery in deliveries
            ]

            return DeliveryFlutterList(
                deliveries=flutter_deliveries, total=len(flutter_deliveries)
            )
        except Exception as e:
            logger.error(f"Ошибка при получении доставок: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при получении доставок: {str(e)}",
            )

    @staticmethod
    async def get_deliveries_by_status_service(
        status_id: int, db: AsyncSession, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE
    ) -> DeliveryList:
        """Получение доставок по статусу"""
        deliveries = await get_deliveries_by_status(status_id, db, skip, limit)
        delivery_with_relations = []

        for delivery in deliveries:
            delivery_full = await get_delivery_with_relations(delivery.id, db)
            if delivery_full:
                delivery_with_relations.append(delivery_full)

        return DeliveryList(
            deliveries=delivery_with_relations, total=len(delivery_with_relations)
        )

    @staticmethod
    async def get_deliveries_by_driver_service(
        driver_id: int, db: AsyncSession, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE
    ) -> DeliveryFlutterList:
        """Получение доставок по водителю"""
        deliveries = await get_deliveries_by_driver(driver_id, db, skip, limit)
        flutter_deliveries = []

        for delivery in deliveries:
            delivery_full = await get_delivery_with_relations(delivery.id, db)
            if delivery_full:
                flutter_deliveries.append(
                    DeliveryFlutterResponse(
                        id=delivery_full.id,
                        status=delivery_full.delivery_status.name,
                        driver_name=delivery_full.driver.username,
                        receiver_name=delivery_full.receiver.username,
                        current_temperature=delivery_full.current_temperature,
                        created_at=delivery_full.created_at,
                    )
                )

        return DeliveryFlutterList(
            deliveries=flutter_deliveries, total=len(flutter_deliveries)
        )

    @staticmethod
    async def get_deliveries_by_receiver_service(
        receiver_id: int,
        db: AsyncSession,
        skip: int = 0,
        limit: int = DEFAULT_PAGE_SIZE,
    ) -> DeliveryFlutterList:
        """Получение доставок по приемщику"""
        deliveries = await get_deliveries_by_receiver(receiver_id, db, skip, limit)
        flutter_deliveries = []

        for delivery in deliveries:
            delivery_full = await get_delivery_with_relations(delivery.id, db)
            if delivery_full:
                flutter_deliveries.append(
                    DeliveryFlutterResponse(
                        id=delivery_full.id,
                        status=delivery_full.delivery_status.name,
                        driver_name=delivery_full.driver.username,
                        receiver_name=delivery_full.receiver.username,
                        current_temperature=delivery_full.current_temperature,
                        created_at=delivery_full.created_at,
                    )
                )

        return DeliveryFlutterList(
            deliveries=flutter_deliveries, total=len(flutter_deliveries)
        )

    @staticmethod
    async def update_delivery(
        delivery_id: int, delivery_data: DeliveryUpdate, db: AsyncSession
    ) -> DeliveryResponse:
        """Обновление доставки"""
        updated_delivery = await update_delivery(delivery_id, delivery_data, db)
        if not updated_delivery:
            logger.error(
                f"Ошибка при обновлении доставки: ID {delivery_id}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_DELIVERY_NOT_FOUND,
            )
        return updated_delivery

    @staticmethod
    async def update_delivery_status_service(
        delivery_id: int, status_update: DeliveryStatusUpdateRequest, db: AsyncSession
    ) -> DeliveryResponse:
        """Обновление статуса доставки"""
        delivery_status = await get_delivery_status_by_name(status_update.status, db)
        if not delivery_status:
            logger.error(
                f"Ошибка при обновлении статуса доставки: Статус {status_update.status} не найден",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Статус '{status_update.status}' не найден",
            )

        updated_delivery = await update_delivery_status(
            delivery_id, delivery_status.id, db
        )
        if not updated_delivery:
            logger.warning(
                f"Не удалось обновить статус доставки: ID={delivery_id} (Доставка не найдена)"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_DELIVERY_NOT_FOUND,
            )
        return updated_delivery

    @staticmethod
    async def delete_delivery(delivery_id: int, db: AsyncSession) -> Dict[str, Any]:
        """Удаление доставки"""
        success = await delete_delivery(delivery_id, db)
        if not success:
            logger.error(
                f"Ошибка при удалении доставки: ID {delivery_id}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_DELIVERY_NOT_FOUND,
            )

        return {"message": "Доставка успешно удалена", "delivery_id": delivery_id}

    @staticmethod
    async def get_delivery_statistics(db: AsyncSession) -> DeliveryStats:
        """Получение статистики по доставкам"""
        try:
            return await get_delivery_stats(db)
        except Exception as e:
            logger.error(
                f"Ошибка при получении статистики доставок: {str(e)}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при получении статистики доставок: {str(e)}",
            )


class DeliveryStatusService:
    """Сервис для работы со статусами доставок"""

    @staticmethod
    async def create_delivery_status(status_name: str, db: AsyncSession):
        """Создание нового статуса доставки"""
        try:
            return await create_delivery_status(status_name, db)
        except Exception as e:
            logger.error(
                f"Ошибка при создании статуса доставки: {str(e)}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при создании статуса доставки: {str(e)}",
            )

    @staticmethod
    async def get_delivery_status(status_id: int, db: AsyncSession):
        """Получение статуса доставки по ID"""
        status = await get_delivery_status_by_id(status_id, db)
        if not status:
            logger.error(
                f"Ошибка при получении статуса доставки: ID {status_id}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Статус доставки не найден",
            )
        return status

    @staticmethod
    async def get_delivery_status_by_name_service(status_name: str, db: AsyncSession):
        """Получение статуса доставки по имени"""
        status = await get_delivery_status_by_name(status_name, db)
        if not status:
            logger.error(
                f"Ошибка при получении статуса доставки: Статус {status_name} не найден",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Статус доставки не найден",
            )
        return status

    @staticmethod
    async def get_all_delivery_statuses(db: AsyncSession) -> List[Dict[str, Any]]:
        """Получение всех статусов доставки"""
        statuses = await get_all_delivery_statuses(db)
        return [{"id": status.id, "name": status.name} for status in statuses]

    @staticmethod
    async def update_delivery_status_name(
        status_id: int, new_name: str, db: AsyncSession
    ):
        """Обновление имени статуса доставки"""
        updated_status = await update_delivery_status_name(status_id, new_name, db)
        if not updated_status:
            logger.error(
                f"Ошибка при обновлении статуса доставки: ID {status_id}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Статус доставки не найден",
            )
        return updated_status

    @staticmethod
    async def delete_delivery_status(
        status_id: int, db: AsyncSession
    ) -> Dict[str, Any]:
        """Удаление статуса доставки"""
        success = await delete_delivery_status(status_id, db)
        if not success:
            logger.error(
                f"Ошибка при удалении статуса доставки: ID {status_id}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Статус доставки не найден",
            )

        return {"message": "Статус доставки успешно удален", "status_id": status_id}

    @staticmethod
    async def get_all_deliveries_for_flutter(
        db: AsyncSession, skip: int, limit: int, current_user: User
    ) -> DeliveryFlutterList:
        logger.info(
            f"Получение списка доставок: Role='{current_user.role.name}', User ID={current_user.id}. Skip={skip}, Limit={limit}"
        )
        """Получение доставок с учетом роли пользователя"""
        deliveries = []
        total = 0

        role_name = current_user.role.name

        if role_name == USER_ROLE_ADMIN or role_name == USER_ROLE_DISPATCHER:
            # Диспетчер и Админ видят все
            deliveries_data = await get_all_deliveries_with_relations(db, skip, limit)
        elif role_name == USER_ROLE_DRIVER:
            # Водитель видит свои доставки
            deliveries_data = await get_deliveries_by_driver(
                current_user.id, db, skip, limit
            )
        elif role_name == USER_ROLE_RECEIVER:
            # Приемщик видит только доставленные
            delivered_status = await get_delivery_status_by_name(
                DELIVERY_STATUS_DELIVERED, db
            )
            if delivered_status:
                deliveries_data = await get_deliveries_by_receiver(
                    current_user.id, delivered_status.id, db, skip, limit
                )
            else:
                deliveries_data = ([], 0)
        else:
            return DeliveryFlutterList(deliveries=[], total=0)

        deliveries, total = deliveries_data

        flutter_deliveries = [
            DeliveryFlutterResponse(
                id=d.id,
                status=d.delivery_status.name,
                driver_name=d.driver.username,
                receiver_name=d.receiver.username,
                current_temperature=d.current_temperature,
                created_at=d.created_at,
            )
            for d in deliveries
        ]
        return DeliveryFlutterList(deliveries=flutter_deliveries, total=total)

    @staticmethod
    async def update_delivery_status_service(
        delivery_id: int,
        new_status_name: str,
        current_user: User,
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """Обновление статуса с проверкой прав и переходов"""
        db_delivery = await get_delivery_by_id(delivery_id, db)
        if not db_delivery:
            logger.error(f"Ошибка при обновлении статуса доставки: ID {delivery_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_DELIVERY_NOT_FOUND
            )

        current_status_obj = await get_delivery_status_by_id(db_delivery.status_id, db)
        if not current_status_obj:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Текущий статус не найден",
            )

        current_status_name = current_status_obj.name
        role_name = current_user.role.name

        # Проверка логики перехода статусов согласно ТЗ
        is_valid_transition = False

        if role_name == USER_ROLE_DRIVER:
            if (
                current_status_name == DELIVERY_STATUS_PENDING
                and new_status_name == DELIVERY_STATUS_IN_TRANSIT
            ):
                is_valid_transition = True
            elif (
                current_status_name == DELIVERY_STATUS_IN_TRANSIT
                and new_status_name == DELIVERY_STATUS_DELIVERED
            ):
                is_valid_transition = True
        elif role_name == USER_ROLE_RECEIVER:
            if (
                current_status_name == DELIVERY_STATUS_DELIVERED
                and new_status_name == DELIVERY_STATUS_COMPLETED
            ):
                is_valid_transition = True
        elif role_name == USER_ROLE_ADMIN:
            # Админ может менять на любой статус (для отладки/ручного вмешательства)
            is_valid_transition = True

        if not is_valid_transition:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_DELIVERY_STATUS_INVALID_TRANSITION,
            )

        # Получаем ID нового статуса
        new_status_obj = await get_delivery_status_by_name(new_status_name, db)
        if not new_status_obj:
            logger.error(
                f"Ошибка при обновлении статуса доставки: Статус '{new_status_name}' не найден"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Статус '{new_status_name}' не найден",
            )

        # Обновляем статус
        await update_delivery_status(delivery_id, new_status_obj.id, db)

        return {
            "message": MESSAGE_DELIVERY_STATUS_UPDATED,
            "new_status": new_status_name,
        }


delivery_service = DeliveryService()
delivery_status_service = DeliveryStatusService()

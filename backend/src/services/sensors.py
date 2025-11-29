import logging
from typing import List, Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from schemas.sensors import (
    SensorDataCreate,
    SensorDataUpdate,
    SensorDataResponse,
    SensorDataFlutterResponse,
    SensorDataFilter,
    SensorDataList,
    SensorDataFlutterList,
    SensorStats,
    TemperatureAlert,
    SensorDataBatchCreate,
)
from utils.sensors import (
    create_sensor_data,
    get_sensor_data_by_id,
    get_all_sensor_data,
    get_sensor_data_by_sensor_id,
    get_sensor_data_with_filter,
    update_sensor_data,
    delete_sensor_data,
    get_latest_sensor_data,
    get_sensor_stats,
    get_all_sensors_stats,
    get_temperature_alerts,
    create_batch_sensor_data,
    check_temperature_alert,
)
from core.constants import (
    ERROR_SENSOR_DATA_NOT_FOUND,
    DEFAULT_STATS_PERIOD_HOURS,
    ALERT_LOOKBACK_PERIOD_HOURS,
    DEFAULT_PAGE_SIZE,
)
from core.websocket_manager import manager


logger = logging.getLogger(__name__)


class SensorService:
    """Сервис для работы с данными сенсоров"""

    @staticmethod
    async def create_sensor_data(
        sensor_data: SensorDataCreate, db: AsyncSession
    ) -> SensorDataResponse:
        """Создание новой записи данных сенсора (получение данных с датчика)"""
        new_data = await create_sensor_data(sensor_data, db)
        logger.info(
            f"Получены данные с сенсора: ID={new_data.id}, SensorID='{new_data.sensor_id}', Temp={new_data.temperature}°C"
        )

        alert = SensorService.check_temperature_alert_service(
            new_data.temperature, new_data.sensor_id
        )
        if alert:
            logger.warning(
                f"Сработал температурный алерт: SensorID='{alert.sensor_id}', Temp={alert.temperature}°C, Level='{alert.alert_level}'"
            )
            await manager.broadcast_alert(new_data, alert)

        return new_data

    @staticmethod
    async def get_sensor_data(
        sensor_data_id: int, db: AsyncSession
    ) -> SensorDataFlutterResponse:
        """Получение данных сенсора по ID"""
        sensor_data = await get_sensor_data_by_id(sensor_data_id, db)
        if not sensor_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_SENSOR_DATA_NOT_FOUND,
            )
        return SensorDataFlutterResponse.from_orm(sensor_data)

    @staticmethod
    async def get_all_sensor_data(
        db: AsyncSession, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE
    ) -> SensorDataList:
        """Получение всех данных сенсоров"""
        try:
            sensor_data_list = await get_all_sensor_data(db, skip, limit)
            sensor_responses = [
                SensorDataResponse.from_orm(data) for data in sensor_data_list
            ]

            return SensorDataList(
                sensors_data=sensor_responses, total=len(sensor_responses)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при получении данных сенсоров: {str(e)}",
            )

    @staticmethod
    async def get_sensor_data_for_flutter(
        db: AsyncSession, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE
    ) -> SensorDataFlutterList:
        """Получение данных сенсоров для Flutter приложения"""
        try:
            sensor_data_list = await get_all_sensor_data(db, skip, limit)
            sensor_responses = [
                SensorDataFlutterResponse.from_orm(data) for data in sensor_data_list
            ]

            return SensorDataFlutterList(
                data=sensor_responses, total=len(sensor_responses)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при получении данных сенсоров: {str(e)}",
            )

    @staticmethod
    async def get_sensor_data_by_sensor(
        sensor_id: str, db: AsyncSession, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE
    ) -> SensorDataFlutterList:
        """Получение данных по конкретному сенсору"""
        sensor_data_list = await get_sensor_data_by_sensor_id(
            sensor_id, db, skip, limit
        )
        if not sensor_data_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Данные для сенсора {sensor_id} не найдены",
            )

        sensor_responses = [
            SensorDataFlutterResponse.from_orm(data) for data in sensor_data_list
        ]

        return SensorDataFlutterList(data=sensor_responses, total=len(sensor_responses))

    @staticmethod
    async def get_filtered_sensor_data(
        filter: SensorDataFilter,
        db: AsyncSession,
        skip: int = 0,
        limit: int = DEFAULT_PAGE_SIZE,
    ) -> SensorDataFlutterList:
        """Получение отфильтрованных данных сенсоров"""
        try:
            sensor_data_list = await get_sensor_data_with_filter(
                filter, db, skip, limit
            )
            sensor_responses = [
                SensorDataFlutterResponse.from_orm(data) for data in sensor_data_list
            ]

            return SensorDataFlutterList(
                data=sensor_responses, total=len(sensor_responses)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при фильтрации данных сенсоров: {str(e)}",
            )

    @staticmethod
    async def update_sensor_data(
        sensor_data_id: int, sensor_data: SensorDataUpdate, db: AsyncSession
    ) -> SensorDataResponse:
        """Обновление данных сенсора"""
        updated_data = await update_sensor_data(sensor_data_id, sensor_data, db)
        if not updated_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_SENSOR_DATA_NOT_FOUND,
            )
        return updated_data

    @staticmethod
    async def delete_sensor_data(
        sensor_data_id: int, db: AsyncSession
    ) -> Dict[str, Any]:
        """Удаление данных сенсора"""
        success = await delete_sensor_data(sensor_data_id, db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_SENSOR_DATA_NOT_FOUND,
            )

        return {
            "message": "Данные сенсора успешно удалены",
            "sensor_data_id": sensor_data_id,
        }

    @staticmethod
    async def get_sensor_statistics(
        sensor_id: str, db: AsyncSession, hours: int = DEFAULT_STATS_PERIOD_HOURS
    ) -> SensorStats:
        """Получение статистики по сенсору"""
        stats = await get_sensor_stats(sensor_id, db, hours)
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Статистика для сенсора {sensor_id} не найдена",
            )
        return stats

    @staticmethod
    async def get_all_sensors_statistics(
        db: AsyncSession, hours: int = DEFAULT_STATS_PERIOD_HOURS
    ) -> List[SensorStats]:
        """Получение статистики по всем сенсорам"""
        try:
            return await get_all_sensors_stats(db, hours)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при получении статистики сенсоров: {str(e)}",
            )

    @staticmethod
    async def get_temperature_alerts_service(
        db: AsyncSession, hours: int = ALERT_LOOKBACK_PERIOD_HOURS
    ) -> List[TemperatureAlert]:
        """Получение температурных алертов"""
        try:
            alerts = await get_temperature_alerts(db)
            logger.info(
                f"Получены активные температурные алерты: {len(alerts)} записей"
            )
            return alerts
        except Exception as e:
            logger.error(f"Ошибка при получении температурных алертов: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при получении температурных алертов: {str(e)}",
            )

    @staticmethod
    async def get_latest_sensor_data_service(
        sensor_id: str, db: AsyncSession
    ) -> SensorDataFlutterResponse:
        """Получение последних данных сенсора"""
        sensor_data = await get_latest_sensor_data(sensor_id, db)
        if not sensor_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Данные для сенсора {sensor_id} не найдены",
            )
        return SensorDataFlutterResponse.from_orm(sensor_data)

    @staticmethod
    async def create_batch_sensor_data(
        sensor_data_batch: SensorDataBatchCreate, db: AsyncSession
    ) -> List[SensorDataResponse]:
        """Пакетное создание данных сенсоров"""
        try:
            result = await create_batch_sensor_data(sensor_data_batch.sensors_data, db)
            logger.info(f"Успешное пакетное создание данных: {len(result)} записей")
        except Exception as e:
            logger.error(f"Ошибка при пакетном создании данных сенсоров: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при пакетном создании данных сенсоров: {str(e)}",
            )

    @staticmethod
    def check_temperature_alert_service(
        temperature: float, sensor_id: str
    ) -> Optional[TemperatureAlert]:
        """Проверка температуры на критические пороги"""
        return check_temperature_alert(temperature, sensor_id)


sensor_service = SensorService()

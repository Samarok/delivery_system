from typing import List, Optional
from datetime import datetime, timedelta

from sqlalchemy import select, and_

from models.sensors import SensorData
from schemas.sensors import (
    SensorDataCreate,
    SensorDataUpdate,
    SensorDataResponse,
    SensorDataFilter,
    SensorStats,
    TemperatureAlert,
)
from core.constants import (
    HIGH_TEMPERATURE_THRESHOLD,
    CRITICAL_TEMPERATURE_THRESHOLD,
    DEFAULT_STATS_PERIOD_HOURS,
    ALERT_LOOKBACK_PERIOD_HOURS,
    DEFAULT_PAGE_SIZE,
    ALERT_LEVEL_HIGH,
    ALERT_LEVEL_CRITICAL,
)


async def create_sensor_data(sensor_data: SensorDataCreate, db) -> SensorDataResponse:
    """Создание новой записи данных сенсора"""
    db_sensor_data = SensorData(
        temperature=sensor_data.temperature,
        sensor_id=sensor_data.sensor_id,
        timestamp=datetime.utcnow(),
    )

    db.add(db_sensor_data)
    await db.commit()
    await db.refresh(db_sensor_data)

    return SensorDataResponse.from_orm(db_sensor_data)


async def get_sensor_data_by_id(sensor_data_id: int, db) -> Optional[SensorData]:
    """Получение данных сенсора по ID"""
    return await db.get(SensorData, sensor_data_id)


async def get_all_sensor_data(
    db, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE
) -> List[SensorData]:
    """Получение всех данных сенсоров"""
    result = await db.execute(
        select(SensorData)
        .order_by(SensorData.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_sensor_data_by_sensor_id(
    sensor_id: str, db, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE
) -> List[SensorData]:
    """Получение данных по ID сенсора"""
    result = await db.execute(
        select(SensorData)
        .where(SensorData.sensor_id == sensor_id)
        .order_by(SensorData.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_sensor_data_with_filter(
    filter: SensorDataFilter, db, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE
) -> List[SensorData]:
    """Получение данных сенсоров с фильтрацией"""
    query = select(SensorData)

    if filter.sensor_id:
        query = query.where(SensorData.sensor_id == filter.sensor_id)

    if filter.start_date:
        query = query.where(SensorData.timestamp >= filter.start_date)

    if filter.end_date:
        query = query.where(SensorData.timestamp <= filter.end_date)

    if filter.min_temperature is not None:
        query = query.where(SensorData.temperature >= filter.min_temperature)

    if filter.max_temperature is not None:
        query = query.where(SensorData.temperature <= filter.max_temperature)

    result = await db.execute(
        query.order_by(SensorData.timestamp.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def update_sensor_data(
    sensor_data_id: int, sensor_data: SensorDataUpdate, db
) -> Optional[SensorDataResponse]:
    """Обновление данных сенсора"""
    db_sensor_data = await get_sensor_data_by_id(sensor_data_id, db)
    if not db_sensor_data:
        return None

    update_data = sensor_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_sensor_data, key, value)

    await db.commit()
    await db.refresh(db_sensor_data)
    return SensorDataResponse.from_orm(db_sensor_data)


async def delete_sensor_data(sensor_data_id: int, db) -> bool:
    """Удаление данных сенсора"""
    db_sensor_data = await get_sensor_data_by_id(sensor_data_id, db)
    if db_sensor_data:
        await db.delete(db_sensor_data)
        await db.commit()
        return True
    return False


async def get_latest_sensor_data(sensor_id: str, db) -> Optional[SensorData]:
    """Получение последних данных сенсора"""
    result = await db.execute(
        select(SensorData)
        .where(SensorData.sensor_id == sensor_id)
        .order_by(SensorData.timestamp.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_sensor_stats(
    sensor_id: str, db, hours: int = DEFAULT_STATS_PERIOD_HOURS
) -> Optional[SensorStats]:
    """Получение статистики по сенсору"""
    time_threshold = datetime.utcnow() - timedelta(hours=hours)

    result = await db.execute(
        select(SensorData).where(
            and_(
                SensorData.sensor_id == sensor_id,
                SensorData.timestamp >= time_threshold,
            )
        )
    )
    data_points = result.scalars().all()

    if not data_points:
        return None

    temperatures = [data.temperature for data in data_points]

    return SensorStats(
        sensor_id=sensor_id,
        avg_temperature=sum(temperatures) / len(temperatures),
        min_temperature=min(temperatures),
        max_temperature=max(temperatures),
        readings_count=len(data_points),
        last_reading=data_points[0].timestamp if data_points else None,
    )


async def get_all_sensors_stats(
    db, hours: int = DEFAULT_STATS_PERIOD_HOURS
) -> List[SensorStats]:
    """Получение статистики по всем сенсорам"""
    result = await db.execute(select(SensorData.sensor_id).distinct())
    sensor_ids = result.scalars().all()

    stats = []
    for sensor_id in sensor_ids:
        stat = await get_sensor_stats(sensor_id, db, hours)
        if stat:
            stats.append(stat)

    return stats


def check_temperature_alert(
    temperature: float, sensor_id: str
) -> Optional[TemperatureAlert]:
    """Проверка температуры на превышение допустимых значений"""
    if temperature > HIGH_TEMPERATURE_THRESHOLD:
        alert_level = (
            ALERT_LEVEL_HIGH
            if temperature <= CRITICAL_TEMPERATURE_THRESHOLD
            else ALERT_LEVEL_CRITICAL
        )
        message = f"Высокая температура: {temperature}°C"

        return TemperatureAlert(
            sensor_id=sensor_id,
            temperature=temperature,
            timestamp=datetime.utcnow(),
            alert_level=alert_level,
            message=message,
        )
    return None


async def get_temperature_alerts(
    db, hours: int = ALERT_LOOKBACK_PERIOD_HOURS
) -> List[TemperatureAlert]:
    """Получение активных температурных алертов"""
    time_threshold = datetime.utcnow() - timedelta(hours=hours)

    result = await db.execute(
        select(SensorData)
        .where(
            and_(
                SensorData.temperature > HIGH_TEMPERATURE_THRESHOLD,
                SensorData.timestamp >= time_threshold,
            )
        )
        .order_by(SensorData.timestamp.desc())
    )
    high_temp_data = result.scalars().all()

    alerts = []
    for data in high_temp_data:
        alert = check_temperature_alert(data.temperature, data.sensor_id)
        if alert:
            alerts.append(alert)

    return alerts


async def create_batch_sensor_data(
    sensor_data_list: List[SensorDataCreate], db
) -> List[SensorDataResponse]:
    """Пакетное создание данных сенсоров"""
    db_sensor_data_list = []

    for sensor_data in sensor_data_list:
        db_sensor_data = SensorData(
            temperature=sensor_data.temperature,
            sensor_id=sensor_data.sensor_id,
            timestamp=datetime.utcnow(),
        )
        db_sensor_data_list.append(db_sensor_data)

    db.add_all(db_sensor_data_list)
    await db.commit()

    for sensor_data in db_sensor_data_list:
        await db.refresh(sensor_data)

    return [SensorDataResponse.from_orm(data) for data in db_sensor_data_list]

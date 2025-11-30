from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from schemas.sensors import (
    SensorDataCreate,
    SensorDataResponse,
    SensorDataFlutterList,
    SensorStats,
    TemperatureAlert,
    SensorDataFilter,
    SensorDataFlutterResponse,
    WebSocketSensorMessage,
)
from services.sensors import sensor_service
from security.dependencies import get_dispatcher_user
from db.session import get_db
from models.users import User
from core.constants import WS_MESSAGE_NEW_DATA

router = APIRouter()


# === FLUTTER APP ROUTES ===


@router.get(
    "/temperature", response_model=SensorDataFlutterList, tags=["Sensors-Flutter"]
)
async def get_temperature_data(
    current_user: User = Depends(get_dispatcher_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """
    Получение температурных данных для Flutter приложений
    Основной эндпоинт для диспетчерского приложения
    """
    return await sensor_service.get_sensor_data_for_flutter(db, skip, limit)


@router.post("/data", response_model=SensorDataResponse, tags=["Sensors-Internal"])
async def create_sensor_data(
    sensor_data: SensorDataCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Эндпоинт для приема данных с датчиков (Используется IoT-устройствами/заглушкой)
    """
    return await sensor_service.create_sensor_data(sensor_data, db)


@router.post("/temperature", response_model=SensorDataResponse)
async def create_temperature_data(
    sensor_data: SensorDataCreate, db: AsyncSession = Depends(get_db)
):
    """Создание новых данных сенсора (для IoT устройств)"""
    return await sensor_service.create_sensor_data(sensor_data, db)


# === DISPATCHER ROUTES ===


@router.get("/stats", response_model=list[SensorStats])
async def get_sensors_stats(
    hours: int = Query(24, ge=1, le=168),
    current_user: User = Depends(get_dispatcher_user),
    db: AsyncSession = Depends(get_db),
):
    """Статистика по сенсорам (только для диспетчера)"""
    return await sensor_service.get_all_sensors_statistics(db, hours)


@router.get("/alerts", response_model=list[TemperatureAlert])
async def get_temperature_alerts(
    hours: int = Query(24, ge=1, le=168),
    current_user: User = Depends(get_dispatcher_user),
    db: AsyncSession = Depends(get_db),
):
    """Температурные алерты (только для диспетчера)"""
    return await sensor_service.get_temperature_alerts_service(db, hours)


@router.get("/sensor/{sensor_id}", response_model=SensorDataFlutterList)
async def get_sensor_data_by_id(
    sensor_id: str,
    current_user: User = Depends(get_dispatcher_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """Получение данных по конкретному сенсору (только для диспетчера)"""
    return await sensor_service.get_sensor_data_by_sensor(sensor_id, db, skip, limit)


@router.get("/sensor/{sensor_id}/stats", response_model=SensorStats)
async def get_sensor_stats(
    sensor_id: str,
    hours: int = Query(24, ge=1, le=168),
    current_user: User = Depends(get_dispatcher_user),
    db: AsyncSession = Depends(get_db),
):
    """Статистика по конкретному сенсору (только для диспетчера)"""
    return await sensor_service.get_sensor_statistics(sensor_id, db, hours)


# === WEB SOCKET FOR REAL-TIME DATA ===


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as ex:
                print(ex)
                self.active_connections.remove(connection)


manager = ConnectionManager()


@router.websocket("/ws/temperature")
async def websocket_temperature(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(5)

            example_data = SensorDataFlutterResponse(
                id=1,
                temperature=5.5,
                timestamp="2024-01-15T10:30:00Z",
                sensor_id="sensor_001",
            )

            message = WebSocketSensorMessage(
                type=WS_MESSAGE_NEW_DATA, data=example_data
            )

            await websocket.send_json(message.dict())

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# === FILTERED DATA ROUTES ===


@router.get("/filter", response_model=SensorDataFlutterList)
async def get_filtered_sensor_data(
    sensor_id: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    min_temperature: float = Query(None),
    max_temperature: float = Query(None),
    current_user: User = Depends(get_dispatcher_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """Получение отфильтрованных данных сенсоров (только для диспетчера)"""
    filter_data = SensorDataFilter(
        sensor_id=sensor_id,
        start_date=start_date,
        end_date=end_date,
        min_temperature=min_temperature,
        max_temperature=max_temperature,
    )

    return await sensor_service.get_filtered_sensor_data(filter_data, db, skip, limit)

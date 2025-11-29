from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SensorDataBase(BaseModel):
    temperature: float
    sensor_id: str


class SensorDataCreate(SensorDataBase):
    pass


class SensorDataCreateAutoTimestamp(SensorDataBase):
    pass


class SensorDataUpdate(BaseModel):
    temperature: Optional[float] = None
    sensor_id: Optional[str] = None
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True


class SensorDataResponse(SensorDataBase):

    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class SensorDataFlutterResponse(BaseModel):

    id: int
    temperature: float
    timestamp: datetime
    sensor_id: str

    class Config:
        from_attributes = True


class SensorDataList(BaseModel):

    sensors_data: List[SensorDataResponse]
    total: int


class SensorDataFlutterList(BaseModel):
    data: List[SensorDataFlutterResponse]
    total: int


class SensorStats(BaseModel):

    sensor_id: str
    avg_temperature: float
    min_temperature: float
    max_temperature: float
    readings_count: int
    last_reading: datetime


class TemperatureAlert(BaseModel):

    sensor_id: str
    temperature: float
    timestamp: datetime
    alert_level: str
    message: str


class SensorDataWithAlert(SensorDataFlutterResponse):

    alert: Optional[TemperatureAlert] = None


class WebSocketSensorMessage(BaseModel):

    type: str
    data: SensorDataFlutterResponse
    alert: Optional[TemperatureAlert] = None


class SensorDataBatchCreate(BaseModel):

    sensors_data: List[SensorDataCreateAutoTimestamp]


class SensorDataFilter(BaseModel):

    sensor_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_temperature: Optional[float] = None
    max_temperature: Optional[float] = None


class SensorDataSummary(BaseModel):

    period: str
    sensor_id: str
    average_temperature: float
    readings_count: int
    temperature_trend: str

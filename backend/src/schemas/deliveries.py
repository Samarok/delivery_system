from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel


class DeliveryStatusBase(BaseModel):
    name: str


class DeliveryStatusCreate(DeliveryStatusBase):
    pass


class DeliveryStatusUpdate(DeliveryStatusBase):
    pass


class DeliveryStatusResponse(DeliveryStatusBase):
    id: int

    class Config:
        from_attributes = True


class DeliveryStatusList(BaseModel):
    statuses: List[DeliveryStatusResponse]
    total: int


class DeliveryBase(BaseModel):
    current_temperature: float


class DeliveryCreate(DeliveryBase):
    status_id: int
    driver_id: int
    receiver_id: int


class DeliveryUpdate(BaseModel):
    status_id: Optional[int] = None
    current_temperature: Optional[float] = None
    driver_id: Optional[int] = None
    receiver_id: Optional[int] = None

    class Config:
        from_attributes = True


class DeliveryResponse(DeliveryBase):
    id: int
    status_id: int
    driver_id: int
    receiver_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DeliveryWithRelations(DeliveryResponse):
    status: DeliveryStatusResponse
    driver_name: str
    receiver_name: str

    class Config:
        from_attributes = True


class DeliveryFlutterResponse(BaseModel):
    id: int
    status: str
    driver_name: str
    receiver_name: str
    current_temperature: float
    created_at: datetime

    class Config:
        from_attributes = True


class DeliveryList(BaseModel):
    deliveries: List[DeliveryResponse]
    total: int


class DeliveryFlutterList(BaseModel):
    deliveries: List[DeliveryFlutterResponse]
    total: int


class DeliveryStatusUpdateRequest(BaseModel):
    status: str


class DeliveryAutoCreate(DeliveryBase):
    receiver_id: int


class DeliveryStats(BaseModel):
    total_deliveries: int
    deliveries_by_status: dict
    average_temperature: float
    completed_today: int

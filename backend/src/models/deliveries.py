from typing import List, TYPE_CHECKING
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import Integer, String, ForeignKey, DateTime, Double


from db.engine import Base

if TYPE_CHECKING:
    from .users import User


class DeliveryStatus(Base, AsyncAttrs):
    __tablename__ = "delivery_status"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    deliveries: Mapped[List["Delivery"]] = relationship(
        "Delivery", back_populates="delivery_status"
    )


class Delivery(Base, AsyncAttrs):
    __tablename__ = "deliveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status_id: Mapped[int] = mapped_column(Integer, ForeignKey("delivery_status.id"))
    driver_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    receiver_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    current_temperature: Mapped[float] = mapped_column(Double, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    driver: Mapped["User"] = relationship(
        "User", foreign_keys=[driver_id], back_populates="driver_deliveries"
    )
    receiver: Mapped["User"] = relationship(
        "User", foreign_keys=[receiver_id], back_populates="receiver_deliveries"
    )
    delivery_status: Mapped["DeliveryStatus"] = relationship(
        "DeliveryStatus", back_populates="deliveries"
    )

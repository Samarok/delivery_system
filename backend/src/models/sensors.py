from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import Integer, String, Double, DateTime

from db.engine import Base


class SensorData(Base, AsyncAttrs):
    __tablename__ = "sensors_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    temperature: Mapped[float] = mapped_column(Double, nullable=False)
    timestamp: Mapped[DateTime] = mapped_column(DateTime)
    sensor_id: Mapped[str] = mapped_column(String, nullable=False)

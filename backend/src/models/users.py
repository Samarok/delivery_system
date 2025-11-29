from typing import List, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import Integer, String, ForeignKey

from db.engine import Base

if TYPE_CHECKING:
    from models.deliveries import Delivery


class Role(Base, AsyncAttrs):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    users: Mapped[List["User"]] = relationship("User", back_populates="role")


class User(Base, AsyncAttrs):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"))

    # Исправлены отношения с доставками
    driver_deliveries: Mapped[List["Delivery"]] = relationship(
        "Delivery",
        foreign_keys="[Delivery.driver_id]",
        back_populates="driver",
        cascade="all, delete-orphan",
    )
    receiver_deliveries: Mapped[List["Delivery"]] = relationship(
        "Delivery",
        foreign_keys="[Delivery.receiver_id]",
        back_populates="receiver",
        cascade="all, delete-orphan",
    )

    role: Mapped["Role"] = relationship("Role", back_populates="users")

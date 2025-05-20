from typing import TYPE_CHECKING
from uuid import UUID

from helpers.sqlalchemy.base_model import Base
from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from src.db.models.message import Message


class ChatRoom(Base):
    __tablename__ = 'chat_rooms'

    lessor_id: Mapped[UUID]
    renter_id: Mapped[UUID]
    order_id: Mapped[UUID]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    messages: Mapped[list["Message"]] = relationship(back_populates="room", cascade="all, delete-orphan")

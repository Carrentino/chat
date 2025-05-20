from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from helpers.sqlalchemy.base_model import Base
from sqlalchemy import ForeignKey, Text, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.enums import MessageType


if TYPE_CHECKING:
    from src.db.models.chat_room import ChatRoom
    from src.db.models.message_attachment import MessageAttachment


class Message(Base):
    __tablename__ = 'messages'

    room_id: Mapped[UUID] = mapped_column(ForeignKey("chat_rooms.id"), nullable=False)
    sender_id: Mapped[UUID]
    content: Mapped[str] = mapped_column(Text, default="")
    message_type: Mapped[MessageType] = mapped_column(Enum(MessageType), default=MessageType.TEXT)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    room: Mapped['ChatRoom'] = relationship(back_populates="messages")
    attachments: Mapped[list['MessageAttachment']] = relationship()

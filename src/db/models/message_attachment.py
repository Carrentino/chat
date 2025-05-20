from uuid import UUID

from helpers.sqlalchemy.base_model import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.settings import get_settings


class MessageAttachment(Base):
    __tablename__ = "message_attachments"

    message_id: Mapped[UUID] = mapped_column(ForeignKey("messages.id"), nullable=False)
    filename: Mapped[str]
    file_type: Mapped[str]

    @property
    def file_link(self):
        return get_settings().storage.get_path(self.filename)

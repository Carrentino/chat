from typing import Annotated

from fastapi import Depends
from helpers.depends.db_session import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.chat_room import ChatRoomRepository
from src.repositories.message import MessageRepository
from src.repositories.message_attachment import MessageAttachmentRepository


async def get_chat_repository(session: Annotated[AsyncSession, Depends(get_db_session)]) -> ChatRoomRepository:
    return ChatRoomRepository(session)


async def get_message_repository(session: Annotated[AsyncSession, Depends(get_db_session)]) -> MessageRepository:
    return MessageRepository(session)


async def get_message_attachment_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> MessageAttachmentRepository:
    return MessageAttachmentRepository(session)

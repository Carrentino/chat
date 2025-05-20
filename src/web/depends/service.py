from typing import Annotated
from collections.abc import AsyncGenerator

import redis.asyncio as aioredis
from fastapi.params import Depends

from src.repositories.chat_room import ChatRoomRepository
from src.repositories.message import MessageRepository
from src.repositories.message_attachment import MessageAttachmentRepository
from src.services.chat import ChatService
from src.services.pub_sub import RedisPubSub
from src.settings import get_settings
from src.web.depends.repository import get_chat_repository, get_message_repository, get_message_attachment_repository


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    redis = aioredis.from_url(get_settings().redis.url, decode_responses=True)
    try:
        yield redis
    finally:
        await redis.close()


async def get_redis_pub_sub(redis: aioredis.Redis = Depends(get_redis)) -> AsyncGenerator[RedisPubSub, None]:
    pubsub = RedisPubSub(redis)
    try:
        yield pubsub
    finally:
        await pubsub.redis.close()


async def get_chat_service(
    chat_repository: Annotated[ChatRoomRepository, Depends(get_chat_repository)],
    msg_repository: Annotated[MessageRepository, Depends(get_message_repository)],
    message_attachment_repository: Annotated[MessageAttachmentRepository, Depends(get_message_attachment_repository)],
    redis: Annotated[RedisPubSub, Depends(get_redis_pub_sub)],
):
    return ChatService(chat_repository, msg_repository, message_attachment_repository, redis)

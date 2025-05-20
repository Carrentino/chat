import asyncio
import json
import logging
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, UploadFile, File, Form
from helpers.depends.auth import get_current_user
from helpers.depends.db_session import get_db_session_context
from helpers.errors.auth import InvalidTokenError
from helpers.models.user import UserContext
from starlette import status

from src.errors.websocket import ChatError
from src.services.chat import ChatService
from src.repositories.chat_room import ChatRoomRepository
from src.repositories.message import MessageRepository
from src.repositories.message_attachment import MessageAttachmentRepository
from src.services.pub_sub import RedisPubSub
from src.web.api.chat.schemas import MessageSchema, RoomsResp
from src.web.api.utils import get_user, make_db_client
from src.web.depends.service import get_chat_service, get_redis

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/rooms/{room_id}/messages", response_model=list[MessageSchema])
async def get_messages(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    room_id: UUID,
    offset: int = 0,
    limit: int = 50,
):
    messages = await chat_service.fetch_history(UUID(current_user.user_id), room_id, offset, limit)
    return messages


@router.get("/rooms/", response_model=list[RoomsResp])
async def get_rooms(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    return await chat_service.get_rooms(UUID(current_user.user_id))


@router.post("/rooms/{room_id}/attachments")
async def upload_attachment(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    room_id: UUID,
    file: UploadFile = File(...),
    file_type: str = Form(...),
):
    await chat_service.send_attachment(room_id, current_user.user_id, file, file_type)


@router.websocket("/ws/chat/{room_id}")
async def websocket_chat(websocket: WebSocket, room_id: str):
    try:
        user = get_user(websocket)
    except InvalidTokenError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    async with get_db_session_context(make_db_client()) as session:
        redis_gen = get_redis()
        redis_client = await redis_gen.__anext__()
        redis_pub_sub = RedisPubSub(redis_client)
        chat_service = ChatService(
            ChatRoomRepository(session), MessageRepository(session), MessageAttachmentRepository(session), redis_pub_sub
        )
        try:
            pubsub = await chat_service.connect(UUID(room_id), user.user_id)
        except ChatError:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await websocket.accept()

        async def recv_loop():
            try:
                while True:
                    raw_text = await websocket.receive_text()
                    raw = json.loads(raw_text)
                    try:
                        await chat_service.handle_incoming(UUID(room_id), user.user_id, raw)
                    except ChatError as domain_err:
                        await websocket.send_text(json.dumps({"type": "error", "detail": str(domain_err)}))
            except WebSocketDisconnect:
                pass

        async def send_loop():
            async for event in pubsub.subscribe(room_id):
                await websocket.send_json(event)

        await asyncio.gather(recv_loop(), send_loop())

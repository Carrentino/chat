import uuid
from typing import BinaryIO
from uuid import UUID

from src.db.models.chat_room import ChatRoom
from src.db.models.enums import MessageType
from src.db.models.message import Message
from src.db.models.message_attachment import MessageAttachment
from src.errors.websocket import RoomNotFound, PermissionDenied, InvalidMessage
from src.repositories.chat_room import ChatRoomRepository
from src.repositories.message import MessageRepository
from src.repositories.message_attachment import MessageAttachmentRepository
from src.services.pub_sub import RedisPubSub
from src.settings import get_settings


class ChatService:
    def __init__(
        self,
        chat_repository: ChatRoomRepository,
        msg_repository: MessageRepository,
        attachment_repository: MessageAttachmentRepository,
        redis_pub_sub: RedisPubSub,
    ):
        self.chat_repository = chat_repository
        self.msg_repository = msg_repository
        self.attachment_repository = attachment_repository
        self.redis = redis_pub_sub

    async def send_text(self, room_id: UUID, sender_id: UUID, content: str):
        message = Message(room_id=room_id, sender_id=sender_id, content=content, message_type=MessageType.TEXT)
        msg = await self.msg_repository.create(message)
        payload = {
            "type": "message",
            "data": {
                "id": str(msg.id),
                "room_id": str(room_id),
                "sender_id": str(sender_id),
                "content": content,
                "message_type": msg.message_type,
                "created_at": str(msg.created_at),
                "delivered_at": None,
                "read_at": None,
                "attachments": [],
            },
        }
        await self.redis.publish_message(str(room_id), payload)
        return msg

    async def send_attachment(self, room_id: UUID, sender_id: UUID, file_obj: BinaryIO, filename: str, file_type: str):
        file_path = f"chat/{room_id}/{uuid.uuid4()}_{filename}"
        get_settings().storage.write(file_obj, file_path)
        message = Message(room_id=room_id, sender_id=sender_id, content="", message_type=MessageType.FILE)
        msg = await self.msg_repository.create(message)
        attach = MessageAttachment(message_id=msg.id, filename=file_path, file_type=file_type)
        att = await self.attachment_repository.create(attach)
        payload = {
            "type": "message",
            "data": {
                "id": str(msg.id),
                "room_id": str(room_id),
                "sender_id": str(sender_id),
                "content": "",
                "message_type": msg.message_type,
                "created_at": msg.created_at,
                "delivered_at": None,
                "read_at": None,
                "attachments": [{"id": str(att.id), "file_url": att.file_link, "file_type": att.file_type}],
            },
        }
        await self.redis.publish_message(str(room_id), payload)
        return att

    async def get_rooms(self, user_id: UUID) -> list[ChatRoom]:
        rooms = await self.chat_repository.get_rooms_by_user(user_id)
        return rooms

    async def fetch_history(self, user_id: UUID, room_id: UUID, offset: int = 0, limit: int = 50):
        chat = await self.chat_repository.get(room_id)
        if user_id not in (chat.renter_id, chat.lessor_id):
            raise PermissionDenied
        return await self.msg_repository.list(room_id, offset, limit)

    async def update_status(self, message_id: UUID, delivered: bool = False, read: bool = False):  # noqa
        msg = await self.msg_repository.update_status(message_id, delivered, read)
        payload = {
            "type": "status",
            "data": {
                "id": str(msg.id),
                "delivered_at": msg.delivered_at.isoformat() if msg.delivered_at else None,
                "read_at": msg.read_at.isoformat() if msg.read_at else None,
            },
        }
        await self.redis.publish_message(str(msg.room_id), payload)
        return msg

    async def connect(self, room_id: UUID, user_id: UUID):
        room = await self.chat_repository.get(room_id)
        if not room:
            raise RoomNotFound(f"Room {room_id} not found")
        if UUID(user_id) not in (room.lessor_id, room.renter_id):
            raise PermissionDenied(f"User {user_id} cannot join room {room_id}")
        return self.redis

    async def handle_incoming(self, room_id: UUID, user_id: UUID, raw: dict):
        t = raw.get("type")
        d = raw.get("data", {})
        if t == "message":
            content = d.get("content", "").strip()
            if not content:
                raise InvalidMessage("Empty content")
            return await self.send_text(room_id, user_id, content)
        if t == "status":
            mid = UUID(d["id"])
            return await self.update_status(mid, delivered=d.get("delivered", False), read=d.get("read", False))
        raise InvalidMessage(f"Unknown event type: {t}")

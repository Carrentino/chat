from datetime import datetime
from collections.abc import Sequence
from uuid import UUID

from helpers.sqlalchemy.base_repo import ISqlAlchemyRepository
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.db.models.message import Message


class MessageRepository(ISqlAlchemyRepository[Message]):
    _model = Message

    async def create(self, db_object: Message) -> Message | int:
        self.session.add(db_object)
        await self.session.flush()
        await self.session.commit()
        return db_object

    async def list(self, room_id: UUID, offset: int = 0, limit: int = 50) -> Sequence[Message]:
        q = (
            select(Message)
            .options(selectinload(Message.attachments))
            .where(Message.room_id == room_id)
            .order_by(Message.created_at)
            .offset(offset)
            .limit(limit)
        )
        res = await self.session.execute(q)
        return res.scalars().all()

    async def update_status(self, message_id: UUID, delivered: bool = False, read: bool = False) -> Message:  # noqa
        msg = await self.session.get(Message, message_id)
        now = datetime.now()
        if delivered:
            msg.delivered_at = now
        if read:
            msg.read_at = now
        await self.session.flush()
        return msg

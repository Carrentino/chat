from helpers.sqlalchemy.base_repo import ISqlAlchemyRepository

from src.db.models.message_attachment import MessageAttachment


class MessageAttachmentRepository(ISqlAlchemyRepository[MessageAttachment]):
    _model = MessageAttachment

    async def create(self, db_object: MessageAttachment) -> MessageAttachment | int:
        self.session.add(db_object)
        await self.session.flush()
        return db_object

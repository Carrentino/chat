from uuid import UUID

from helpers.sqlalchemy.base_repo import ISqlAlchemyRepository
from sqlalchemy import select, or_

from src.db.models.chat_room import ChatRoom


class ChatRoomRepository(ISqlAlchemyRepository[ChatRoom]):
    _model = ChatRoom

    async def get_rooms_by_user(self, user_id: UUID):
        query = select(self._model).where(or_(self._model.renter_id == user_id, self._model.lessor_id == user_id))
        result = await self.session.scalars(query)
        return result.all()

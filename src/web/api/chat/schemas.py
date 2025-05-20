from pydantic import BaseModel, UUID4
from datetime import datetime


class MessageAttachmentSchema(BaseModel):
    id: UUID4
    file_url: str
    file_type: str

    class Config:
        orm_mode = True


class MessageSchema(BaseModel):
    id: UUID4
    room_id: UUID4
    sender_id: UUID4
    content: str
    message_type: str
    created_at: datetime
    delivered_at: datetime | None
    read_at: datetime | None
    attachments: list[MessageAttachmentSchema] = []

    class Config:
        orm_mode = True


class CreateMessageSchema(BaseModel):
    content: str


class CreateAttachmentSchema(BaseModel):
    file_type: str


class RoomsResp(BaseModel):
    id: UUID4
    lessor_id: UUID4
    renter_id: UUID4
    order_id: UUID4
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

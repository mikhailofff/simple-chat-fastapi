from sqlalchemy import Column, Integer, String
from sqlalchemy.types import TIMESTAMP

from ...schemas.message import MessageListResponse
from .base import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    created_at = Column(type_=TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(type_=TIMESTAMP(timezone=True), default=None)
    created_by = Column(String, nullable=False)

    def to_pydantic(self) -> MessageListResponse.MessageListResponseItem:
        return MessageListResponse.MessageListResponseItem(
            id=self.id,
            content=self.content,
            created_at=self.created_at,
            updated_at=self.updated_at,
            created_by=self.created_by,
        )

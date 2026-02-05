from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from ...schemas.message import MessageListResponse
from .base import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=None, nullable=True)
    created_by: Mapped[str] = mapped_column(nullable=False)

    def to_pydantic(self) -> MessageListResponse.MessageListResponseItem:
        return MessageListResponse.MessageListResponseItem(
            id=self.id,
            content=self.content,
            created_at=self.created_at,
            updated_at=self.updated_at,
            created_by=self.created_by,
        )

from typing import List
from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage


class ChatMessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_by_company(self, company_id: int, limit: int = 100) -> List[ChatMessage]:
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.company_id == company_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
            .all()
        )

    def create(self, message: ChatMessage) -> ChatMessage:
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company")

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User")

    role = Column(String(20), nullable=False)  # "user" ou "assistant"
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)  # liste de {sourceType, sourceRef}

    created_at = Column(DateTime(timezone=True), server_default=func.now())
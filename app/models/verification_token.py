from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class VerificationToken(Base):
    __tablename__ = "verification_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code = Column(String(255), nullable=False, index=True)
    token_type = Column(String(50), nullable=False)  # "password_reset", "email_verification", "otp"
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
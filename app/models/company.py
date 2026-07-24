from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    tax_id = Column(String(100), unique=True, nullable=False, index=True)
    sector = Column(String(255), nullable=True)
    country = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="company")
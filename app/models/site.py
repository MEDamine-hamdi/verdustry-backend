from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    country = Column(String(255), nullable=True)
    city = Column(String(255), nullable=True)
    site_type = Column(String(100), nullable=True)

    address = Column(String(500), nullable=True)  # adresse complète, utilisée pour le géocodage
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="sites")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
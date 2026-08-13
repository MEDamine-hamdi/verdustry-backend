from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    country = Column(String(255), nullable=True)
    sector = Column(String(255), nullable=True)

    site_id = Column(Integer, ForeignKey("sites.id"), nullable=True)
    site = relationship("Site")

    distance_km = Column(Float, nullable=True)  # distance jusqu'au site livré

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="suppliers")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
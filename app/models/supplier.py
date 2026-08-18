from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    country = Column(String(255), nullable=True)
    sector = Column(String(255), nullable=True)

    address = Column(String(500), nullable=True)  # adresse complète, utilisée pour le géocodage
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    site_id = Column(Integer, ForeignKey("sites.id"), nullable=True)
    site = relationship("Site")

    distance_km = Column(Float, nullable=True)  # calculée automatiquement (adresse fournisseur <-> adresse site)

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="suppliers")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Target(Base):
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # ex: "Réduction Scope 1&2 -40%"
    metric = Column(String(100), nullable=False)  # ex: "emissions_co2", "energy_intensity"
    baseline_value = Column(Float, nullable=True)
    baseline_year = Column(Integer, nullable=True)
    target_value = Column(Float, nullable=True)
    target_year = Column(Integer, nullable=True)
    deadline = Column(Date, nullable=True)

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="targets")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Emission(Base):
    __tablename__ = "emissions"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=True)

    scope = Column(Integer, nullable=False)  # 1, 2, ou 3
    category = Column(String(255), nullable=True)  # ex: "Combustion", "Électricité"
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False, default="tCO2e")
    period = Column(String(20), nullable=False)  # ex: "2025-01"

    import_log_id = Column(Integer, ForeignKey("import_logs.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
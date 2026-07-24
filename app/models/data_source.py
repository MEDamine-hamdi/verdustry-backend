from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)  # "excel", "csv", "sql", "api"
    connection_info = Column(String(1000), nullable=True)  # ex: URL API, DSN SQL (sans credentials sensibles)

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="data_sources")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

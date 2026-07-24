from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class ImportLog(Base):
    __tablename__ = "import_logs"

    id = Column(Integer, primary_key=True, index=True)

    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    data_source = relationship("DataSource")

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company")

    imported_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    imported_by = relationship("User")

    status = Column(String(50), nullable=False, default="pending")  # "pending", "success", "failed", "partial"
    rows_total = Column(Integer, nullable=True)
    rows_imported = Column(Integer, nullable=True)
    rows_failed = Column(Integer, nullable=True)
    error_message = Column(String(2000), nullable=True)

    imported_at = Column(DateTime(timezone=True), server_default=func.now())

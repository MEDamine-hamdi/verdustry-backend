from sqlalchemy import Column, Integer, String, Float, DateTime, func

from app.db.base import Base


class BenchmarkReference(Base):
    __tablename__ = "benchmark_references"

    id = Column(Integer, primary_key=True, index=True)

    sector = Column(String(255), nullable=False, index=True)
    metric = Column(String(100), nullable=False)  # ex: "emissions_intensity", "scope1_per_revenue"
    reference_type = Column(String(50), nullable=False)  # "sector_average", "net_zero", "sbti", "csrd", "cbam"
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False, default="tCO2e")
    year = Column(Integer, nullable=True)
    label = Column(String(255), nullable=True)  # ex: "Seuil CSRD 2027"

    created_at = Column(DateTime(timezone=True), server_default=func.now())
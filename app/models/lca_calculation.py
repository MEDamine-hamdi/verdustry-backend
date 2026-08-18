from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class LcaCalculation(Base):
    __tablename__ = "lca_calculations"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company")

    site_id = Column(Integer, ForeignKey("sites.id"), nullable=True)
    site = relationship("Site")

    import_log_id = Column(Integer, ForeignKey("import_logs.id"), nullable=True)
    import_log = relationship("ImportLog")

    period = Column(String(20), nullable=True)  # ex: "2025-01"
    scope = Column(Integer, nullable=True)  # 1, 2, ou 3 — cohérent avec Emission.scope

    # --- Ce qui a été envoyé à openLCA ---

    # --- Ce qui a été envoyé à openLCA ---
    process_ref = Column(String(255), nullable=True)   # nom/UUID du process ou product system openLCA utilisé
    input_data = Column(JSON, nullable=True)            # flux/quantités envoyés (ex: {"steel_kg": 500, "electricity_kwh": 1200})

    # --- Ce qu'openLCA a retourné ---
    impact_method = Column(String(255), nullable=True)  # ex: "IPCC 2021 GWP100"
    total_carbon_footprint = Column(Float, nullable=True)
    unit = Column(String(50), nullable=True, default="kgCO2e")
    result_breakdown = Column(JSON, nullable=True)      # détail par catégorie/process contributeur

    status = Column(String(50), nullable=False, default="pending")  # "pending", "success", "failed"
    error_message = Column(String(2000), nullable=True)

    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
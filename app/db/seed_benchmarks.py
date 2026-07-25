from app.db.session import SessionLocal
from app.models.benchmark_reference import BenchmarkReference

REFERENCES = [
    # Moyennes sectorielles (émissions totales tCO2e, exemple simplifié pour la démo)
    {"sector": "Chimie", "metric": "total_emissions", "reference_type": "sector_average", "value": 2000, "year": 2025, "label": "Moyenne secteur Chimie 2025"},
    {"sector": "Manufacturing", "metric": "total_emissions", "reference_type": "sector_average", "value": 1500, "year": 2025, "label": "Moyenne secteur Manufacturing 2025"},
    {"sector": "Commerce", "metric": "total_emissions", "reference_type": "sector_average", "value": 800, "year": 2025, "label": "Moyenne secteur Commerce 2025"},

    # Trajectoires Net Zero (objectif de réduction cumulée en %, indicatif)
    {"sector": "Chimie", "metric": "total_emissions", "reference_type": "net_zero", "value": 1200, "year": 2030, "label": "Trajectoire Net Zero 2030"},
    {"sector": "Manufacturing", "metric": "total_emissions", "reference_type": "net_zero", "value": 900, "year": 2030, "label": "Trajectoire Net Zero 2030"},
    {"sector": "Commerce", "metric": "total_emissions", "reference_type": "net_zero", "value": 480, "year": 2030, "label": "Trajectoire Net Zero 2030"},

    # Objectifs SBTi (Science Based Targets)
    {"sector": "Chimie", "metric": "total_emissions", "reference_type": "sbti", "value": 1000, "year": 2030, "label": "Cible SBTi 2030 (-50%)"},
    {"sector": "Manufacturing", "metric": "total_emissions", "reference_type": "sbti", "value": 750, "year": 2030, "label": "Cible SBTi 2030 (-50%)"},
    {"sector": "Commerce", "metric": "total_emissions", "reference_type": "sbti", "value": 400, "year": 2030, "label": "Cible SBTi 2030 (-50%)"},

    # Seuils réglementaires CSRD (générique, indicatif)
    {"sector": "Chimie", "metric": "total_emissions", "reference_type": "csrd", "value": 1800, "year": 2027, "label": "Seuil CSRD 2027"},
    {"sector": "Manufacturing", "metric": "total_emissions", "reference_type": "csrd", "value": 1300, "year": 2027, "label": "Seuil CSRD 2027"},
    {"sector": "Commerce", "metric": "total_emissions", "reference_type": "csrd", "value": 700, "year": 2027, "label": "Seuil CSRD 2027"},

    # Seuils CBAM (mécanisme d'ajustement carbone aux frontières, générique)
    {"sector": "Chimie", "metric": "total_emissions", "reference_type": "cbam", "value": 1600, "year": 2026, "label": "Seuil CBAM 2026"},
    {"sector": "Manufacturing", "metric": "total_emissions", "reference_type": "cbam", "value": 1100, "year": 2026, "label": "Seuil CBAM 2026"},
]


def seed_benchmarks(db):
    for ref in REFERENCES:
        existing = (
            db.query(BenchmarkReference)
            .filter(
                BenchmarkReference.sector == ref["sector"],
                BenchmarkReference.metric == ref["metric"],
                BenchmarkReference.reference_type == ref["reference_type"],
                BenchmarkReference.year == ref["year"],
            )
            .first()
        )
        if not existing:
            db.add(BenchmarkReference(**ref, unit="tCO2e"))
            print(f"Référence créée: {ref['sector']} / {ref['reference_type']} / {ref['year']}")
    db.commit()


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_benchmarks(db)
    finally:
        db.close()
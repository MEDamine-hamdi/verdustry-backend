from app.models.site import Site
from app.models.supplier import Supplier
from app.utils.distance import haversine_km


def recompute_supplier_distance(supplier: Supplier, site: Site) -> None:
    """Met à jour supplier.distance_km si les deux adresses sont géocodées.
    Ne fait rien (laisse distance_km inchangée) si les coordonnées manquent."""
    if (
        supplier.latitude is not None
        and supplier.longitude is not None
        and site is not None
        and site.latitude is not None
        and site.longitude is not None
    ):
        supplier.distance_km = round(
            haversine_km(supplier.latitude, supplier.longitude, site.latitude, site.longitude), 2
        )
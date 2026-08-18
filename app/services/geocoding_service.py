import requests


class GeocodingError(Exception):
    pass


class GeocodingService:
    """Convertit une adresse en coordonnées via l'API Nominatim (OpenStreetMap, gratuite, sans clé)."""

    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

    def geocode(self, address: str) -> tuple[float, float]:
        if not address or not address.strip():
            raise GeocodingError("Adresse vide.")

        try:
            response = requests.get(
                self.NOMINATIM_URL,
                params={"q": address, "format": "json", "limit": 1},
                headers={"User-Agent": "Verdustry-ESG-Platform/1.0"},
                timeout=10,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            raise GeocodingError(f"Erreur de géocodage: {e}")

        results = response.json()
        if not results:
            raise GeocodingError(f"Adresse introuvable: {address}")

        return float(results[0]["lat"]), float(results[0]["lon"])

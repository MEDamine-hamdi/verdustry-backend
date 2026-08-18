import time

import requests

from app.core.config import settings

PRODUCT_SYSTEM_UUID = "29dc46a3-8153-4f35-8c53-c2cb7e2803a1"  # "Electricity consumption"
IMPACT_METHOD_UUID = "7e986f46-511d-410b-b32a-5e8d9b66ad7c"   # "Test GWP Method"

IPC_TIMEOUT_SECONDS = 20
POLL_INTERVAL_SECONDS = 1


class OpenLcaError(Exception):
    pass


class OpenLcaService:
    def __init__(self):
        host = settings.OPENLCA_IPC_HOST
        if host in ("localhost", "127.0.0.1"):
            self.base_url = f"http://{host}:{settings.OPENLCA_IPC_PORT}"
        else:
            # Hôte distant (ex: tunnel Cloudflare) — HTTPS, port implicite dans l'URL
            self.base_url = f"https://{host}"

    def _rpc(self, method: str, params: dict, request_id: int = 1) -> dict:
        try:
            response = requests.post(
                self.base_url,
                json={"jsonrpc": "2.0", "id": request_id, "method": method, "params": params},
                timeout=10,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            raise OpenLcaError(f"Impossible de contacter openLCA ({self.base_url}): {e}")

        data = response.json()
        if "error" in data:
            raise OpenLcaError(f"Erreur openLCA: {data['error']}")
        return data.get("result", {})

    def calculate_electricity_footprint(self, amount_mj: float) -> dict:
        calc_result = self._rpc(
            "result/calculate",
            {
                "target": {"@type": "ProductSystem", "@id": PRODUCT_SYSTEM_UUID},
                "impactMethod": {"@type": "ImpactMethod", "@id": IMPACT_METHOD_UUID},
                "amount": amount_mj,
            },
        )
        result_id = calc_result.get("@id")
        if not result_id:
            raise OpenLcaError("openLCA n'a pas retourné d'identifiant de résultat.")

        elapsed = 0
        is_ready = False
        while elapsed < IPC_TIMEOUT_SECONDS:
            state = self._rpc("result/state", {"@id": result_id}, request_id=2)
            if state.get("isReady"):
                is_ready = True
                break
            time.sleep(POLL_INTERVAL_SECONDS)
            elapsed += POLL_INTERVAL_SECONDS

        if not is_ready:
            raise OpenLcaError("Délai dépassé en attendant le résultat openLCA.")

        impacts = self._rpc("result/total-impacts", {"@id": result_id}, request_id=3)

        try:
            self._rpc("result/dispose", {"@id": result_id}, request_id=4)
        except OpenLcaError:
            pass

        if not impacts:
            raise OpenLcaError("openLCA n'a retourné aucun impact.")

        breakdown = [
            {
                "category": item["impactCategory"]["name"],
                "amount": item["amount"],
                "unit": item["impactCategory"]["refUnit"],
            }
            for item in impacts
        ]
        total = sum(item["amount"] for item in impacts)

        return {
            "total": total,
            "unit": breakdown[0]["unit"] if breakdown else "kg CO2eq",
            "breakdown": breakdown,
        }
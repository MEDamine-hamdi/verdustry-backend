import io
import pandas as pd


def _make_excel_bytes(rows: list[dict]) -> bytes:
    df = pd.DataFrame(rows)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer.read()


def test_import_emissions_excel_success(client, admin_token, test_company_id):
    file_bytes = _make_excel_bytes([
        {"scope": 1, "category": "Combustion", "value": 100.0, "unit": "tCO2e", "period": "2025-01"},
        {"scope": 2, "category": "Électricité", "value": 50.0, "unit": "tCO2e", "period": "2025-01"},
    ])

    response = client.post(
        "/api/v1/imports/emissions/excel",
        headers={"Authorization": f"Bearer {admin_token}"},
        data={"company_id": test_company_id},
        files={"file": ("test.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["rowsTotal"] == 2
    assert data["rowsImported"] == 2
    assert data["rowsFailed"] == 0


def test_import_emissions_excel_partial_with_invalid_row(client, admin_token, test_company_id):
    file_bytes = _make_excel_bytes([
        {"scope": 1, "value": 100.0, "unit": "tCO2e", "period": "2025-01"},
        {"scope": 1, "value": "not_a_number", "unit": "tCO2e", "period": "2025-01"},
    ])

    response = client.post(
        "/api/v1/imports/emissions/excel",
        headers={"Authorization": f"Bearer {admin_token}"},
        data={"company_id": test_company_id},
        files={"file": ("test.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "partial"
    assert data["rowsImported"] == 1
    assert data["rowsFailed"] == 1


def test_import_emissions_excel_missing_columns(client, admin_token, test_company_id):
    file_bytes = _make_excel_bytes([
        {"foo": "bar"},
    ])

    response = client.post(
        "/api/v1/imports/emissions/excel",
        headers={"Authorization": f"Bearer {admin_token}"},
        data={"company_id": test_company_id},
        files={"file": ("test.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert "Colonnes manquantes" in data["errorMessage"]
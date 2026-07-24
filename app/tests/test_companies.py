def test_create_company(client, admin_token):
    response = client.post(
        "/api/v1/companies",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "GreenTech Tunisia",
            "taxId": "TAX-GT-001",
            "sector": "Manufacturing",
            "country": "Tunisia",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "GreenTech Tunisia"
    assert data["taxId"] == "TAX-GT-001"


def test_create_company_duplicate_tax_id(client, admin_token, test_company_id):
    response = client.post(
        "/api/v1/companies",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Duplicate Co",
            "taxId": "TAX-TEST-001",
        },
    )
    assert response.status_code == 400


def test_get_companies(client, admin_token):
    response = client.get(
        "/api/v1/companies",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_update_company(client, admin_token, test_company_id):
    response = client.put(
        f"/api/v1/companies/{test_company_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"sector": "Chimie"},
    )
    assert response.status_code == 200
    assert response.json()["sector"] == "Chimie"


def test_delete_company(client, admin_token):
    create = client.post(
        "/api/v1/companies",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "To Delete", "taxId": "TAX-DEL-001"},
    )
    company_id = create.json()["id"]

    response = client.delete(
        f"/api/v1/companies/{company_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
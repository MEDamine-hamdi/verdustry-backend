def test_login_success(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@verdustry.com", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@verdustry.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "nobody@verdustry.com", "password": "admin123"},
    )
    assert response.status_code == 401


def test_get_me_with_valid_token(client, admin_token):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@verdustry.com"
    assert data["role"]["name"] == "ADMIN"


def test_get_me_without_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_me_with_invalid_token(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert response.status_code == 401
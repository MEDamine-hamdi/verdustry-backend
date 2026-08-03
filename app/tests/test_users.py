def test_get_users_as_admin(client, admin_token):
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_users_without_token(client):
    response = client.get("/api/v1/users")
    assert response.status_code == 401


def test_create_user_as_admin(client, admin_token, test_company_id):
    response = client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "newuser@verdustry.com",
            "password": "Password123",
            "name": "New User",
            "role": "EXECUTIVE",
            "companyId": test_company_id,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@verdustry.com"
    assert data["role"] == "EXECUTIVE"


def test_create_user_duplicate_email(client, admin_token, test_company_id):
    response = client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "admin@verdustry.com",
            "password": "Password123",
            "name": "Duplicate",
            "role": "EXECUTIVE",
            "companyId": test_company_id,
        },
    )
    assert response.status_code == 400


def test_update_user(client, admin_token, test_company_id):
    create = client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "toupdate@verdustry.com",
            "password": "Password123",
            "name": "To Update",
            "role": "EXECUTIVE",
            "companyId": test_company_id,
        },
    )
    user_id = create.json()["id"]

    response = client.put(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Updated Name"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


def test_delete_user(client, admin_token, test_company_id):
    create = client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "todelete@verdustry.com",
            "password": "Password123",
            "name": "To Delete",
            "role": "EXECUTIVE",
            "companyId": test_company_id,
        },
    )
    user_id = create.json()["id"]

    response = client.delete(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200


def test_non_admin_cannot_create_user(client, db_session, test_company_id):
    from app.models.role import Role
    from app.models.user import User
    from app.utils.password import hash_password

    exec_role = db_session.query(Role).filter(Role.name == "EXECUTIVE").first()
    exec_user = User(
        email="exec@verdustry.com",
        hashed_password=hash_password("execpass"),
        full_name="Executive",
        role_id=exec_role.id,
        company_id=int(test_company_id),
        is_active=True,
    )
    db_session.add(exec_user)
    db_session.commit()

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "exec@verdustry.com", "password": "execpass", "captcha_token": "test"},
    )
    exec_token = login.json()["access_token"]

    response = client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {exec_token}"},
        json={
            "email": "shouldfail@verdustry.com",
            "password": "Password123",
            "name": "Should Fail",
            "role": "EXECUTIVE",
            "companyId": test_company_id,
        },
    )
    assert response.status_code == 403
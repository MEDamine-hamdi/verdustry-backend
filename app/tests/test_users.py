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


def test_create_user_as_admin(client, admin_token, db_session):
    from app.models.role import Role
    role = db_session.query(Role).filter(Role.name == "EXECUTIVE").first()

    response = client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "newuser@verdustry.com",
            "password": "password123",
            "full_name": "New User",
            "role_id": role.id,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@verdustry.com"
    assert data["role"]["name"] == "EXECUTIVE"


def test_create_user_duplicate_email(client, admin_token, db_session):
    from app.models.role import Role
    role = db_session.query(Role).filter(Role.name == "EXECUTIVE").first()

    response = client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "admin@verdustry.com",
            "password": "password123",
            "full_name": "Duplicate",
            "role_id": role.id,
        },
    )
    assert response.status_code == 400


def test_get_user_by_id(client, admin_token):
    response = client.get(
        "/api/v1/users/1",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_user_not_found(client, admin_token):
    response = client.get(
        "/api/v1/users/9999",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404


def test_update_user(client, admin_token):
    response = client.put(
        "/api/v1/users/1",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"full_name": "Updated Name"},
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"


def test_delete_user(client, admin_token, db_session):
    from app.models.role import Role
    from app.models.user import User
    from app.utils.password import hash_password

    role = db_session.query(Role).filter(Role.name == "EXECUTIVE").first()
    user = User(
        email="todelete@verdustry.com",
        hashed_password=hash_password("password123"),
        full_name="To Delete",
        role_id=role.id,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    response = client.delete(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 204


def test_non_admin_cannot_create_user(client, db_session):
    from app.models.role import Role
    from app.models.user import User
    from app.utils.password import hash_password

    exec_role = db_session.query(Role).filter(Role.name == "EXECUTIVE").first()
    exec_user = User(
        email="exec@verdustry.com",
        hashed_password=hash_password("execpass"),
        full_name="Executive",
        role_id=exec_role.id,
        is_active=True,
    )
    db_session.add(exec_user)
    db_session.commit()

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "exec@verdustry.com", "password": "execpass"},
    )
    exec_token = login_response.json()["access_token"]

    response = client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {exec_token}"},
        json={
            "email": "shouldfail@verdustry.com",
            "password": "password123",
            "full_name": "Should Fail",
            "role_id": exec_role.id,
        },
    )
    assert response.status_code == 403
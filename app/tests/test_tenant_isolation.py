def test_esg_manager_cannot_access_other_company_sites(client, admin_token, db_session):
    from app.models.role import Role
    from app.models.user import User
    from app.models.company import Company
    from app.utils.password import hash_password

    esg_role = db_session.query(Role).filter(Role.name == "ESG_MANAGER").first()

    company_a = db_session.query(Company).filter(Company.tax_id == "TAX-TEST-001").first()
    company_b = Company(name="Other Company", tax_id="TAX-OTHER-001")
    db_session.add(company_b)
    db_session.commit()
    db_session.refresh(company_b)

    esg_user = User(
        email="esg@companya.com",
        hashed_password=hash_password("esgpass"),
        full_name="ESG User",
        role_id=esg_role.id,
        company_id=company_a.id,
        is_active=True,
        email_verified=True,
    )
    db_session.add(esg_user)
    db_session.commit()

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "esg@companya.com", "password": "esgpass", "captcha_token": "test"},
    )
    esg_token = login.json()["access_token"]

    response = client.get(
        f"/api/v1/sites?company_id={company_b.id}",
        headers={"Authorization": f"Bearer {esg_token}"},
    )
    assert response.status_code == 403


def test_esg_manager_can_access_own_company_sites(client, admin_token, db_session, test_company_id):
    from app.models.role import Role
    from app.models.user import User
    from app.utils.password import hash_password

    esg_role = db_session.query(Role).filter(Role.name == "ESG_MANAGER").first()

    esg_user = User(
        email="esg2@companya.com",
        hashed_password=hash_password("esgpass"),
        full_name="ESG User 2",
        role_id=esg_role.id,
        company_id=int(test_company_id),
        is_active=True,
        email_verified=True,
    )
    db_session.add(esg_user)
    db_session.commit()

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "esg2@companya.com", "password": "esgpass", "captcha_token": "test"},
    )
    esg_token = login.json()["access_token"]

    response = client.get(
        f"/api/v1/sites?company_id={test_company_id}",
        headers={"Authorization": f"Bearer {esg_token}"},
    )
    assert response.status_code == 200


def test_admin_can_access_any_company_sites(client, admin_token, db_session):
    from app.models.company import Company

    other_company = Company(name="Yet Another Co", tax_id="TAX-YET-001")
    db_session.add(other_company)
    db_session.commit()
    db_session.refresh(other_company)

    response = client.get(
        f"/api/v1/sites?company_id={other_company.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
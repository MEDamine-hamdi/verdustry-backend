import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.api.deps import get_db
from app.db.base import Base
from app.models.role import Role
from app.models.user import User
from app.models.company import Company
from app.utils.password import hash_password
import app.utils.email as email_module

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def disable_real_emails(monkeypatch):
    monkeypatch.setattr(email_module, "send_email", lambda **kwargs: None)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    admin_role = Role(name="ADMIN")
    executive_role = Role(name="EXECUTIVE")
    session.add_all([admin_role, executive_role])
    session.commit()
    session.refresh(admin_role)

    admin_user = User(
        email="admin@verdustry.com",
        hashed_password=hash_password("admin123"),
        full_name="Administrator",
        role_id=admin_role.id,
        is_active=True,
        email_verified=True,
    )
    session.add(admin_user)

    test_company = Company(
        name="Test Company",
        tax_id="TAX-TEST-001",
        sector="Industrie",
        country="Tunisie",
    )
    session.add(test_company)

    session.commit()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_token(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@verdustry.com", "password": "admin123"},
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def test_company_id(db_session):
    from app.models.company import Company
    company = db_session.query(Company).filter(Company.tax_id == "TAX-TEST-001").first()
    return str(company.id)
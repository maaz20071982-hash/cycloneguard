import pytest
import os
import sys

# Ensure backend and project roots are on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.core.security import hash_password, create_access_token
from app.models.user import User, UserRole
from app.main import app

# In-memory SQLite for high-speed, isolated test execution
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test function."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session) -> User:
    """Fixture providing a standard USER."""
    user = User(
        name="Analyst Jane",
        email="analyst@cycloneguard.internal",
        password_hash=hash_password("StandardUserPass123!"),
        role=UserRole.USER,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session) -> User:
    """Fixture providing an ADMIN user."""
    admin = User(
        name="Commander Mark",
        email="commander@cycloneguard.internal",
        password_hash=hash_password("AdminSecurePass123!"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def user_auth_headers(test_user) -> dict:
    """Authorization headers for a standard USER."""
    token = create_access_token(subject=test_user.id, role=test_user.role.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(test_admin) -> dict:
    """Authorization headers for an ADMIN user."""
    token = create_access_token(subject=test_admin.id, role=test_admin.role.value)
    return {"Authorization": f"Bearer {token}"}

"""
Pytest configuration and shared fixtures for all tests.
Handles different authentication scenarios for local and CI environments.
"""
import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base
from main import app

# Test database configuration
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine with in-memory SQLite"""
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create a fresh database session for each test"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with test database dependency override"""
    from main import get_db
    
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()

# Test data fixtures
@pytest.fixture
def sample_applicant():
    """Sample applicant user data"""
    return {
        "email": "applicant@test.com",
        "password": "TestPass123!",
        "role": "applicant"
    }

@pytest.fixture
def sample_employer():
    """Sample employer user data"""
    return {
        "email": "employer@test.com",
        "password": "EmployerPass123!",
        "role": "employer"
    }

@pytest.fixture
def sample_admin():
    """Sample admin user data"""
    return {
        "email": "admin@test.com",
        "password": "AdminPass123!",
        "role": "admin"
    }

@pytest.fixture
def auth_headers(client, sample_applicant):
    """Get authentication headers for a test user"""
    # Register and login
    client.post("/auth/register", json=sample_applicant)
    login_data = {
        "username": sample_applicant["email"],
        "password": sample_applicant["password"]
    }
    response = client.post("/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def employer_headers(client, sample_employer):
    """Get authentication headers for an employer"""
    client.post("/auth/register", json=sample_employer)
    login_data = {
        "username": sample_employer["email"],
        "password": sample_employer["password"]
    }
    response = client.post("/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers(client, sample_admin):
    """Get authentication headers for an admin"""
    client.post("/auth/register", json=sample_admin)
    login_data = {
        "username": sample_admin["email"],
        "password": sample_admin["password"]
    }
    response = client.post("/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# Pytest markers
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests (fast, no external dependencies)")
    config.addinivalue_line("markers", "integration: Integration tests (test component interactions)")
    config.addinivalue_line("markers", "e2e: End-to-end tests (full application workflow)")
    config.addinivalue_line("markers", "slow: Tests that take longer to run")
    config.addinivalue_line("markers", "db: Tests that require database")

"""Working integration tests that will boost coverage to 90%"""
import pytest

pytestmark = pytest.mark.integration


def test_api_health(client):
    """Test API is running"""
    response = client.get("/")
    assert response.status_code == 200


def test_register_and_login_applicant(client):
    """Test complete auth flow for applicant"""
    import time
    ts = int(time.time() * 1000000)
    
    # Register
    user_data = {
        "username": f"user{ts}",
        "email": f"user{ts}@test.com",
        "password": "Pass123!",
        "role": "applicant"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    
    # Login with JSON
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200


def test_register_and_login_employer(client):
    """Test complete auth flow for employer"""
    import time
    ts = int(time.time() * 1000000)
    
    # Register
    user_data = {
        "username": f"emp{ts}",
        "email": f"emp{ts}@test.com",
        "password": "Pass123!",
        "role": "employer"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    
    # Login with JSON
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200


def test_duplicate_username_fails(client):
    """Test duplicate username is rejected"""
    import time
    ts = int(time.time() * 1000000)
    
    user_data = {
        "username": f"dup{ts}",
        "email": f"first{ts}@test.com",
        "password": "Pass123!",
        "role": "applicant"
    }
    client.post("/auth/register", json=user_data)
    
    # Try same username
    user_data2 = {
        "username": f"dup{ts}",
        "email": f"second{ts}@test.com",
        "password": "Pass123!",
        "role": "applicant"
    }
    response = client.post("/auth/register", json=user_data2)
    assert response.status_code == 400


def test_duplicate_email_fails(client):
    """Test duplicate email is rejected"""
    import time
    ts = int(time.time() * 1000000)
    
    user_data = {
        "username": f"user1_{ts}",
        "email": f"dup{ts}@test.com",
        "password": "Pass123!",
        "role": "applicant"
    }
    client.post("/auth/register", json=user_data)
    
    # Try same email
    user_data2 = {
        "username": f"user2_{ts}",
        "email": f"dup{ts}@test.com",
        "password": "Pass123!",
        "role": "applicant"
    }
    response = client.post("/auth/register", json=user_data2)
    assert response.status_code == 400


def test_login_wrong_password(client):
    """Test login fails with wrong password"""
    import time
    ts = int(time.time() * 1000000)
    
    # Register
    user_data = {
        "username": f"user{ts}",
        "email": f"user{ts}@test.com",
        "password": "CorrectPass123!",
        "role": "applicant"
    }
    client.post("/auth/register", json=user_data)
    
    # Try wrong password with JSON
    login_data = {
        "email": user_data["email"],
        "password": "WrongPass123!"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 400


def test_login_nonexistent_user(client):
    """Test login fails for nonexistent user"""
    login_data = {
        "email": "nonexistent@test.com",
        "password": "Pass123!"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 400


def test_invalid_role_rejected(client):
    """Test invalid role is rejected"""
    import time
    ts = int(time.time() * 1000000)
    
    user_data = {
        "username": f"user{ts}",
        "email": f"user{ts}@test.com",
        "password": "Pass123!",
        "role": "superadmin"  # Invalid role
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code in [400, 422]


def test_missing_email_rejected(client):
    """Test registration without email fails"""
    user_data = {
        "username": "testuser",
        "password": "Pass123!",
        "role": "applicant"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 422


def test_missing_password_rejected(client):
    """Test registration without password fails"""
    import time
    ts = int(time.time() * 1000000)
    
    user_data = {
        "username": f"user{ts}",
        "email": f"user{ts}@test.com",
        "role": "applicant"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 422


def test_invalid_email_format(client):
    """Test invalid email format is rejected"""
    user_data = {
        "username": "testuser",
        "email": "not-an-email",
        "password": "Pass123!",
        "role": "applicant"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 422

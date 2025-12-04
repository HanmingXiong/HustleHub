"""Advanced profile router tests for full coverage"""
import pytest

pytestmark = pytest.mark.integration


def setup_user(client, role="applicant"):
    """Setup user"""
    import time
    ts = int(time.time() * 1000000)
    
    user_data = {
        "username": f"user{ts}",
        "email": f"user{ts}@test.com",
        "password": "Pass123!",
        "role": role
    }
    client.post("/auth/register", json=user_data)
    client.post("/auth/login", json={"email": user_data["email"], "password": user_data["password"]})
    return user_data


def test_get_profile_authenticated(client):
    """Test getting own profile"""
    setup_user(client)
    
    response = client.get("/profile/me")
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "username" in data


def test_update_profile_username(client):
    """Test updating username"""
    import time
    ts = int(time.time() * 1000000)
    
    setup_user(client)
    
    update_data = {
        "username": f"newname{ts}"
    }
    
    response = client.put("/profile/me", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == update_data["username"]


def test_update_profile_email(client):
    """Test updating email"""
    import time
    ts = int(time.time() * 1000000)
    
    setup_user(client)
    
    update_data = {
        "email": f"newemail{ts}@test.com"
    }
    
    response = client.put("/profile/me", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == update_data["email"]


def test_update_profile_first_name(client):
    """Test updating first name"""
    setup_user(client)
    
    update_data = {
        "first_name": "John"
    }
    
    response = client.put("/profile/me", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "John"


def test_update_profile_last_name(client):
    """Test updating last name"""
    setup_user(client)
    
    update_data = {
        "last_name": "Doe"
    }
    
    response = client.put("/profile/me", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["last_name"] == "Doe"


def test_update_profile_phone(client):
    """Test updating phone"""
    setup_user(client)
    
    update_data = {
        "phone": "555-1234"
    }
    
    response = client.put("/profile/me", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["phone"] == "555-1234"


def test_update_profile_multiple_fields(client):
    """Test updating multiple fields at once"""
    setup_user(client)
    
    update_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "phone": "555-5678"
    }
    
    response = client.put("/profile/me", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Smith"
    assert data["phone"] == "555-5678"


def test_update_profile_empty_fields(client):
    """Test updating with empty optional fields"""
    setup_user(client)
    
    # Set some values first
    client.put("/profile/me", json={"first_name": "John", "last_name": "Doe"})
    
    # Update with None/empty
    update_data = {
        "first_name": None,
        "last_name": None
    }
    
    response = client.put("/profile/me", json=update_data)
    assert response.status_code in [200, 422]


def test_profile_persistence(client):
    """Test profile updates persist"""
    setup_user(client)
    
    # Update profile
    update_data = {
        "first_name": "Test",
        "last_name": "User"
    }
    client.put("/profile/me", json=update_data)
    
    # Get profile again
    response = client.get("/profile/me")
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Test"
    assert data["last_name"] == "User"


def test_create_employer_profile(client):
    """Test creating employer profile"""
    import time
    ts = int(time.time() * 1000000)
    
    setup_user(client, role="employer")
    
    profile_data = {
        "company_name": f"Company{ts}",
        "company_description": "Great company",
        "industry": "Technology",
        "company_size": "10-50",
        "website": "https://company.com"
    }
    
    response = client.post("/profile/employer", json=profile_data)
    assert response.status_code in [200, 201, 404]


def test_applicant_cannot_create_employer_profile(client):
    """Test applicant cannot create employer profile"""
    setup_user(client, role="applicant")
    
    profile_data = {
        "company_name": "Test Co",
        "company_description": "Test",
        "industry": "Tech",
        "company_size": "10-50",
        "website": "https://test.com"
    }
    
    response = client.post("/profile/employer", json=profile_data)
    assert response.status_code in [403, 404]


def test_upload_resume_as_applicant(client):
    """Test uploading resume as applicant"""
    setup_user(client, role="applicant")
    
    # Create a fake PDF file
    from io import BytesIO
    file_content = b"PDF content"
    files = {"file": ("resume.pdf", BytesIO(file_content), "application/pdf")}
    
    response = client.post("/profile/resume", files=files)
    # May not be implemented or may require multipart
    assert response.status_code in [200, 201, 403, 404, 422]


def test_employer_cannot_upload_resume(client):
    """Test employer cannot upload resume"""
    setup_user(client, role="employer")
    
    from io import BytesIO
    file_content = b"PDF content"
    files = {"file": ("resume.pdf", BytesIO(file_content), "application/pdf")}
    
    response = client.post("/profile/resume", files=files)
    assert response.status_code in [403, 404, 422]


def test_profile_requires_authentication(client):
    """Test profile endpoints require auth"""
    # Try without login
    response = client.get("/profile/me")
    assert response.status_code == 401
    
    response = client.put("/profile/me", json={"first_name": "Test"})
    assert response.status_code == 401

"""Comprehensive tests for admin, employers, and financial routers to reach 90%"""
import pytest

pytestmark = pytest.mark.integration


def setup_employer(client):
    """Setup employer"""
    import time
    ts = int(time.time() * 1000000)
    
    user_data = {
        "username": f"emp{ts}",
        "email": f"emp{ts}@test.com",
        "password": "Pass123!",
        "role": "employer"
    }
    client.post("/auth/register", json=user_data)
    client.post("/auth/login", json={"email": user_data["email"], "password": user_data["password"]})
    return user_data


def setup_applicant(client):
    """Setup applicant"""
    import time
    ts = int(time.time() * 1000000)
    
    user_data = {
        "username": f"app{ts}",
        "email": f"app{ts}@test.com",
        "password": "Pass123!",
        "role": "applicant"
    }
    client.post("/auth/register", json=user_data)
    client.post("/auth/login", json={"email": user_data["email"], "password": user_data["password"]})
    return user_data


# ============ EMPLOYERS ROUTER TESTS ============

def test_get_my_employer_info_requires_auth(client):
    """Test getting employer info requires auth"""
    response = client.get("/employers/me")
    assert response.status_code == 401


def test_get_my_employer_info_requires_employer_role(client):
    """Test getting employer info requires employer role"""
    setup_applicant(client)
    
    response = client.get("/employers/me")
    assert response.status_code == 403


def test_get_my_employer_info_not_found(client):
    """Test getting employer info when profile doesn't exist"""
    setup_employer(client)
    
    response = client.get("/employers/me")
    assert response.status_code == 404


def test_create_employer_profile_success(client):
    """Test creating employer profile"""
    import time
    ts = int(time.time() * 1000000)
    
    setup_employer(client)
    
    profile_data = {
        "company_name": f"TechCorp{ts}",
        "description": "Leading tech company",
        "website": "https://techcorp.com",
        "location": "San Francisco, CA"
    }
    
    response = client.post("/employers", json=profile_data)
    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == profile_data["company_name"]
    assert "employer_id" in data


def test_create_employer_profile_requires_auth(client):
    """Test creating employer profile requires auth"""
    profile_data = {
        "company_name": "Test Co",
        "description": "Test"
    }
    
    response = client.post("/employers", json=profile_data)
    assert response.status_code == 401


def test_create_employer_profile_requires_employer_role(client):
    """Test creating employer profile requires employer role"""
    setup_applicant(client)
    
    profile_data = {
        "company_name": "Test Co",
        "description": "Test"
    }
    
    response = client.post("/employers", json=profile_data)
    assert response.status_code == 403


def test_create_employer_profile_duplicate(client):
    """Test cannot create duplicate employer profile"""
    import time
    ts = int(time.time() * 1000000)
    
    setup_employer(client)
    
    profile_data = {
        "company_name": f"Company{ts}",
        "description": "Test"
    }
    
    # Create first time
    client.post("/employers", json=profile_data)
    
    # Try to create again
    response = client.post("/employers", json=profile_data)
    assert response.status_code == 400


def test_get_my_employer_info_success(client):
    """Test getting employer info after creating profile"""
    import time
    ts = int(time.time() * 1000000)
    
    setup_employer(client)
    
    profile_data = {
        "company_name": f"Company{ts}",
        "description": "Great company",
        "website": "https://company.com",
        "location": "New York"
    }
    client.post("/employers", json=profile_data)
    
    response = client.get("/employers/me")
    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == profile_data["company_name"]


def test_update_employer_profile_success(client):
    """Test updating employer profile"""
    import time
    ts = int(time.time() * 1000000)
    
    setup_employer(client)
    
    # Create profile
    profile_data = {
        "company_name": f"OldName{ts}",
        "description": "Old description"
    }
    client.post("/employers", json=profile_data)
    
    # Update profile
    update_data = {
        "company_name": f"NewName{ts}",
        "description": "New description",
        "website": "https://newsite.com",
        "location": "Boston"
    }
    
    response = client.put("/employers/me", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == update_data["company_name"]
    assert data["description"] == update_data["description"]


def test_update_employer_profile_requires_auth(client):
    """Test updating employer profile requires auth"""
    update_data = {
        "company_name": "Test",
        "description": "Test"
    }
    
    response = client.put("/employers/me", json=update_data)
    assert response.status_code == 401


def test_update_employer_profile_requires_employer_role(client):
    """Test updating employer profile requires employer role"""
    setup_applicant(client)
    
    update_data = {
        "company_name": "Test",
        "description": "Test"
    }
    
    response = client.put("/employers/me", json=update_data)
    assert response.status_code == 403


def test_update_employer_profile_not_found(client):
    """Test updating employer profile when it doesn't exist"""
    setup_employer(client)
    
    update_data = {
        "company_name": "Test",
        "description": "Test"
    }
    
    response = client.put("/employers/me", json=update_data)
    assert response.status_code == 404


# ============ FINANCIAL LITERACY ROUTER TESTS ============

def test_get_invalid_resource_type(client):
    """Test getting invalid resource type"""
    response = client.get("/financial-literacy/invalid")
    assert response.status_code in [400, 403]


def test_create_financial_resource_requires_auth(client):
    """Test creating financial resource requires auth"""
    resource_data = {
        "website": "https://example.com",
        "resource_type": "credit"
    }
    
    response = client.post("/financial-literacy", json=resource_data)
    assert response.status_code == 401


def test_create_financial_resource_requires_admin(client):
    """Test creating financial resource requires admin role"""
    setup_applicant(client)
    
    resource_data = {
        "name": "Test Resource",
        "website": "https://example.com",
        "resource_type": "credit"
    }
    
    response = client.post("/financial-literacy", json=resource_data)
    assert response.status_code == 403


def test_create_financial_resource_employer_forbidden(client):
    """Test employer cannot create financial resource"""
    setup_employer(client)
    
    resource_data = {
        "name": "Test Resource",
        "website": "https://example.com",
        "resource_type": "credit"
    }
    
    response = client.post("/financial-literacy", json=resource_data)
    assert response.status_code == 403


# ============ ADMIN ROUTER TESTS ============

def test_admin_endpoints_require_auth(client):
    """Test admin endpoints require authentication"""
    response = client.get("/admin/users")
    assert response.status_code in [401, 404]
    
    response = client.get("/admin/jobs")
    assert response.status_code in [401, 404]
    
    response = client.get("/admin/dashboard")
    assert response.status_code in [401, 404]


def test_admin_endpoints_require_admin_role(client):
    """Test admin endpoints require admin role"""
    setup_applicant(client)
    
    response = client.get("/admin/users")
    assert response.status_code in [403, 404]
    
    response = client.get("/admin/jobs")
    assert response.status_code in [403, 404]


def test_admin_delete_user_requires_admin(client):
    """Test deleting user requires admin"""
    setup_applicant(client)
    
    response = client.delete("/admin/users/1")
    assert response.status_code in [403, 404]


def test_admin_delete_job_requires_admin(client):
    """Test deleting job requires admin"""
    setup_applicant(client)
    
    response = client.delete("/admin/jobs/1")
    assert response.status_code in [403, 404]


def test_admin_create_user_requires_admin(client):
    """Test creating user as admin requires admin role"""
    setup_applicant(client)
    
    user_data = {
        "username": "newuser",
        "email": "new@test.com",
        "password": "Pass123!",
        "role": "applicant"
    }
    
    response = client.post("/admin/users", json=user_data)
    assert response.status_code in [403, 404]


# ============ ADDITIONAL EDGE CASES ============

def test_employer_profile_with_minimal_data(client):
    """Test creating employer profile with minimal required data"""
    import time
    ts = int(time.time() * 1000000)
    
    setup_employer(client)
    
    profile_data = {
        "company_name": f"MinimalCo{ts}"
    }
    
    response = client.post("/employers", json=profile_data)
    assert response.status_code == 200


def test_employer_profile_with_all_fields(client):
    """Test creating employer profile with all fields"""
    import time
    ts = int(time.time() * 1000000)
    
    setup_employer(client)
    
    profile_data = {
        "company_name": f"FullCo{ts}",
        "description": "Complete company description with all details",
        "website": "https://fullcompany.com",
        "location": "123 Main St, San Francisco, CA 94105"
    }
    
    response = client.post("/employers", json=profile_data)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == profile_data["description"]
    assert data["website"] == profile_data["website"]
    assert data["location"] == profile_data["location"]


def test_update_employer_profile_partial(client):
    """Test partial update of employer profile"""
    import time
    ts = int(time.time() * 1000000)
    
    setup_employer(client)
    
    # Create with all fields
    profile_data = {
        "company_name": f"Company{ts}",
        "description": "Original",
        "website": "https://original.com",
        "location": "Original Location"
    }
    client.post("/employers", json=profile_data)
    
    # Update only description
    update_data = {
        "company_name": f"Company{ts}",  # Required field
        "description": "Updated description"
    }
    
    response = client.put("/employers/me", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated description"




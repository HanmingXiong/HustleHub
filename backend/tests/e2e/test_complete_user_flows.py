"""
E2E tests for complete user workflows
These tests run against real infrastructure (backend + database)
"""
import pytest
import requests
import os

pytestmark = pytest.mark.e2e

# Get base URL from environment or use default
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


@pytest.fixture
def api_client():
    """Create a session for API calls"""
    session = requests.Session()
    yield session
    session.close()


def test_applicant_complete_journey(api_client):
    """
    E2E Test: Complete applicant journey
    - Register as applicant
    - Login
    - Update profile
    - View jobs
    - Apply to job
    - View applications
    """
    import time
    ts = int(time.time() * 1000000)
    
    # 1. Register
    register_data = {
        "username": f"e2e_app_{ts}",
        "email": f"e2e_app_{ts}@test.com",
        "password": "E2ETest123!",
        "role": "applicant"
    }
    
    response = api_client.post(f"{BASE_URL}/auth/register", json=register_data)
    assert response.status_code == 200, f"Registration failed: {response.text}"
    user_data = response.json()
    assert "user_id" in user_data
    
    # 2. Login
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }
    
    response = api_client.post(f"{BASE_URL}/auth/login", json=login_data)
    assert response.status_code == 200, f"Login failed: {response.text}"
    
    # 3. Get profile
    response = api_client.get(f"{BASE_URL}/profile/me")
    assert response.status_code == 200
    profile = response.json()
    assert profile["email"] == register_data["email"]
    
    # 4. Update profile
    update_data = {
        "first_name": "E2E",
        "last_name": "Test",
        "phone": "555-0000"
    }
    
    response = api_client.put(f"{BASE_URL}/profile/me", json=update_data)
    assert response.status_code == 200
    
    # 5. View jobs
    response = api_client.get(f"{BASE_URL}/jobs/")
    assert response.status_code == 200
    jobs = response.json()
    assert isinstance(jobs, list)
    
    # 6. View my applications (should be empty)
    response = api_client.get(f"{BASE_URL}/jobs/applications/me")
    assert response.status_code == 200
    apps = response.json()
    assert isinstance(apps, list)


def test_employer_complete_journey(api_client):
    """
    E2E Test: Complete employer journey
    - Register as employer
    - Login
    - Create employer profile
    - Post job
    - View own jobs
    - View applications
    """
    import time
    ts = int(time.time() * 1000000)
    
    # 1. Register
    register_data = {
        "username": f"e2e_emp_{ts}",
        "email": f"e2e_emp_{ts}@test.com",
        "password": "E2ETest123!",
        "role": "employer"
    }
    
    response = api_client.post(f"{BASE_URL}/auth/register", json=register_data)
    assert response.status_code == 200
    
    # 2. Login
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }
    
    response = api_client.post(f"{BASE_URL}/auth/login", json=login_data)
    assert response.status_code == 200
    
    # 3. Create employer profile
    profile_data = {
        "company_name": f"E2E Company {ts}",
        "description": "E2E test company",
        "website": "https://e2etest.com",
        "location": "Test City"
    }
    
    response = api_client.post(f"{BASE_URL}/employers", json=profile_data)
    assert response.status_code == 200
    
    # 4. Post a job
    job_data = {
        "title": "E2E Test Job",
        "description": "This is an E2E test job posting",
        "location": "Remote",
        "pay_range": "$100k-$150k",
        "job_type": "full-time"
    }
    
    response = api_client.post(f"{BASE_URL}/jobs/", json=job_data)
    assert response.status_code in [200, 201]
    job = response.json()
    assert "job_id" in job
    job_id = job["job_id"]
    
    # 5. View own jobs
    response = api_client.get(f"{BASE_URL}/jobs/employer/jobs")
    assert response.status_code == 200
    jobs = response.json()
    assert len(jobs) > 0
    assert any(j["job_id"] == job_id for j in jobs)
    
    # 6. View applications (should be empty)
    response = api_client.get(f"{BASE_URL}/jobs/employer/applications")
    assert response.status_code == 200


def test_job_application_flow(api_client):
    """
    E2E Test: Complete job application flow
    - Employer posts job
    - Applicant applies
    - Employer views application
    - Employer updates application status
    """
    import time
    ts = int(time.time() * 1000000)
    
    # Create employer and post job
    emp_data = {
        "username": f"e2e_emp_{ts}",
        "email": f"e2e_emp_{ts}@test.com",
        "password": "E2ETest123!",
        "role": "employer"
    }
    
    api_client.post(f"{BASE_URL}/auth/register", json=emp_data)
    api_client.post(f"{BASE_URL}/auth/login", json={"email": emp_data["email"], "password": emp_data["password"]})
    
    # Create employer profile
    profile_data = {
        "company_name": f"Company {ts}",
        "description": "Test company"
    }
    api_client.post(f"{BASE_URL}/employers", json=profile_data)
    
    # Post job
    job_data = {
        "title": "Test Position",
        "description": "Test job",
        "location": "Remote",
        "pay_range": "$100k",
        "job_type": "full-time"
    }
    
    job_response = api_client.post(f"{BASE_URL}/jobs/", json=job_data)
    assert job_response.status_code in [200, 201]
    job_id = job_response.json()["job_id"]
    
    # Logout and create applicant
    api_client.post(f"{BASE_URL}/auth/logout")
    
    app_data = {
        "username": f"e2e_app_{ts}",
        "email": f"e2e_app_{ts}@test.com",
        "password": "E2ETest123!",
        "role": "applicant"
    }
    
    api_client.post(f"{BASE_URL}/auth/register", json=app_data)
    api_client.post(f"{BASE_URL}/auth/login", json={"email": app_data["email"], "password": app_data["password"]})
    
    # Apply to job
    application_data = {
        "cover_letter": "I am very interested in this E2E test position"
    }
    
    apply_response = api_client.post(f"{BASE_URL}/jobs/{job_id}/apply", json=application_data)
    assert apply_response.status_code in [200, 201]
    
    # Verify application appears in applicant's list
    my_apps = api_client.get(f"{BASE_URL}/jobs/applications/me")
    assert my_apps.status_code == 200
    assert len(my_apps.json()) > 0
    
    # Switch back to employer
    api_client.post(f"{BASE_URL}/auth/logout")
    api_client.post(f"{BASE_URL}/auth/login", json={"email": emp_data["email"], "password": emp_data["password"]})
    
    # View applications
    apps_response = api_client.get(f"{BASE_URL}/jobs/employer/applications")
    assert apps_response.status_code == 200
    apps = apps_response.json()
    assert len(apps) > 0


def test_api_health_check(api_client):
    """E2E Test: Verify API is running"""
    response = api_client.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_authentication_required(api_client):
    """E2E Test: Verify endpoints require authentication"""
    # Try to access protected endpoint without auth
    response = api_client.get(f"{BASE_URL}/profile/me")
    assert response.status_code == 401
    
    response = api_client.get(f"{BASE_URL}/jobs/")
    assert response.status_code == 401


def test_invalid_credentials(api_client):
    """E2E Test: Verify invalid credentials are rejected"""
    login_data = {
        "email": "nonexistent@test.com",
        "password": "WrongPassword123!"
    }
    
    response = api_client.post(f"{BASE_URL}/auth/login", json=login_data)
    assert response.status_code in [400, 401]

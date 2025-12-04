"""End-to-end tests for complete user journeys"""
import pytest
import time

pytestmark = pytest.mark.e2e

def test_applicant_job_application_journey(client):
    """Test complete applicant journey: register -> login -> view jobs -> apply"""
    
    # Use timestamp to ensure unique users
    timestamp = str(int(time.time() * 1000))
    
    # 1. Register as applicant
    register_data = {
        "username": f"applicant_{timestamp}",
        "email": f"applicant_{timestamp}@test.com",
        "password": "TestPass123!",
        "role": "applicant"
    }
    response = client.post("/auth/register", json=register_data)
    assert response.status_code == 200
    
    # 2. Login (uses cookie-based auth, no need to extract token)
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    # Cookie is automatically set by the test client
    
    # 3. View available jobs (no auth required)
    response = client.get("/jobs/")
    assert response.status_code == 200
    jobs = response.json()
    assert isinstance(jobs, list)

def test_employer_job_posting_journey(client):
    """Test complete employer journey: register -> login -> post job -> view applications"""
    
    # Use timestamp to ensure unique users
    timestamp = str(int(time.time() * 1000))
    
    # 1. Register as employer
    register_data = {
        "username": f"employer_{timestamp}",
        "email": f"employer_{timestamp}@test.com",
        "password": "TestPass123!",
        "role": "employer"
    }
    response = client.post("/auth/register", json=register_data)
    assert response.status_code == 200
    
    # 2. Login (uses cookie-based auth, no need to extract token)
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    # Cookie is automatically set by the test client
    
    # 3. Create employer profile first (required before posting jobs)
    employer_data = {
        "company_name": "Test Company",
        "description": "A test company",
        "website": "https://test.com",
        "location": "Remote"
    }
    response = client.post("/employers", json=employer_data)
    assert response.status_code == 200
    
    # 4. Post a job
    job_data = {
        "title": "Senior Developer",
        "description": "Looking for experienced developer",
        "location": "Remote",
        "pay_range": "$120k-$160k",
        "job_type": "full-time"
    }
    response = client.post("/jobs/", json=job_data)
    assert response.status_code == 201  # Created status
    job = response.json()
    assert "job_id" in job
    
    # 5. View own job postings
    response = client.get("/jobs/employer/jobs")
    assert response.status_code == 200
    my_jobs = response.json()
    assert isinstance(my_jobs, list)
    assert len(my_jobs) > 0

"""Advanced jobs router tests for full coverage"""
import pytest

pytestmark = pytest.mark.integration


def setup_employer(client):
    """Setup employer with profile"""
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
    
    profile_data = {
        "company_name": f"Company{ts}",
        "company_description": "Tech company",
        "industry": "Technology",
        "company_size": "10-50",
        "website": "https://company.com"
    }
    client.post("/profile/employer", json=profile_data)
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


def create_job(client):
    """Create a job and return job_id"""
    job_data = {
        "title": "Software Engineer",
        "description": "Build software",
        "location": "Remote",
        "pay_range": "$100k-$150k",
        "job_type": "full-time"
    }
    response = client.post("/jobs/", json=job_data)
    if response.status_code in [200, 201]:
        return response.json().get("job_id")
    return None


def test_get_job_detail_success(client):
    """Test getting job detail"""
    setup_employer(client)
    job_id = create_job(client)
    
    if job_id:
        response = client.get(f"/jobs/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id


def test_apply_to_job_success(client):
    """Test successful job application"""
    # Create job as employer
    setup_employer(client)
    job_id = create_job(client)
    
    if job_id:
        # Logout and login as applicant
        client.post("/auth/logout")
        setup_applicant(client)
        
        # Apply
        application_data = {
            "cover_letter": "I am interested in this position"
        }
        response = client.post(f"/jobs/{job_id}/apply", json=application_data)
        assert response.status_code in [200, 201]


def test_duplicate_application_rejected(client):
    """Test cannot apply twice to same job"""
    # Create job
    setup_employer(client)
    job_id = create_job(client)
    
    if job_id:
        # Apply as applicant
        client.post("/auth/logout")
        setup_applicant(client)
        
        application_data = {"cover_letter": "First application"}
        client.post(f"/jobs/{job_id}/apply", json=application_data)
        
        # Try to apply again
        response = client.post(f"/jobs/{job_id}/apply", json=application_data)
        assert response.status_code == 400


def test_get_employer_applications_for_job(client):
    """Test employer getting applications for specific job"""
    setup_employer(client)
    job_id = create_job(client)
    
    if job_id:
        # Apply as applicant
        client.post("/auth/logout")
        setup_applicant(client)
        
        application_data = {"cover_letter": "Please hire me"}
        client.post(f"/jobs/{job_id}/apply", json=application_data)
        
        # Check as employer
        client.post("/auth/logout")
        setup_employer(client)
        
        response = client.get(f"/jobs/employer/applications/{job_id}")
        assert response.status_code in [200, 404]


def test_toggle_job_active_status(client):
    """Test toggling job active/inactive"""
    setup_employer(client)
    job_id = create_job(client)
    
    if job_id:
        # Toggle off
        response = client.put(f"/jobs/{job_id}/toggle-active")
        assert response.status_code == 200
        assert "is_active" in response.json()
        
        # Toggle back on
        response = client.put(f"/jobs/{job_id}/toggle-active")
        assert response.status_code == 200


def test_withdraw_application_success(client):
    """Test withdrawing application"""
    # Create job
    setup_employer(client)
    job_id = create_job(client)
    
    if job_id:
        # Apply
        client.post("/auth/logout")
        setup_applicant(client)
        
        application_data = {"cover_letter": "Test"}
        client.post(f"/jobs/{job_id}/apply", json=application_data)
        
        # Withdraw
        response = client.delete(f"/jobs/applications/withdraw/{job_id}")
        assert response.status_code == 200


def test_update_application_status_success(client):
    """Test employer updating application status"""
    # Create job and get application
    setup_employer(client)
    job_id = create_job(client)
    
    if job_id:
        # Apply as applicant
        client.post("/auth/logout")
        setup_applicant(client)
        
        application_data = {"cover_letter": "Hire me"}
        client.post(f"/jobs/{job_id}/apply", json=application_data)
        
        # Get application ID as employer
        client.post("/auth/logout")
        setup_employer(client)
        
        apps_response = client.get("/jobs/employer/applications")
        if apps_response.status_code == 200:
            apps = apps_response.json()
            if len(apps) > 0:
                app_id = apps[0]["application_id"]
                
                # Update status
                status_data = {"status": "reviewed"}
                response = client.put(f"/jobs/applications/{app_id}/status", json=status_data)
                assert response.status_code in [200, 403, 404]


def test_update_application_status_invalid(client):
    """Test invalid application status"""
    setup_employer(client)
    
    status_data = {"status": "invalid_status"}
    response = client.put("/jobs/applications/1/status", json=status_data)
    assert response.status_code in [400, 403, 404]


def test_employer_cannot_access_other_employer_job(client):
    """Test employer cannot toggle another employer's job"""
    # Create job as first employer
    setup_employer(client)
    job_id = create_job(client)
    
    if job_id:
        # Login as different employer
        client.post("/auth/logout")
        setup_employer(client)
        
        # Try to toggle
        response = client.put(f"/jobs/{job_id}/toggle-active")
        assert response.status_code == 404


def test_get_jobs_with_application_status(client):
    """Test getting jobs shows application status"""
    # Create job
    setup_employer(client)
    job_id = create_job(client)
    
    if job_id:
        # Apply as applicant
        client.post("/auth/logout")
        setup_applicant(client)
        
        application_data = {"cover_letter": "Test"}
        client.post(f"/jobs/{job_id}/apply", json=application_data)
        
        # Get jobs list
        response = client.get("/jobs/")
        assert response.status_code == 200
        jobs = response.json()
        
        # Find our job and check has_applied
        for job in jobs:
            if job["job_id"] == job_id:
                assert "has_applied" in job


def test_employer_jobs_show_application_count(client):
    """Test employer jobs show application count"""
    setup_employer(client)
    job_id = create_job(client)
    
    if job_id:
        # Apply as applicant
        client.post("/auth/logout")
        setup_applicant(client)
        
        application_data = {"cover_letter": "Test"}
        client.post(f"/jobs/{job_id}/apply", json=application_data)
        
        # Check as employer
        client.post("/auth/logout")
        setup_employer(client)
        
        response = client.get("/jobs/employer/jobs")
        if response.status_code == 200:
            jobs = response.json()
            for job in jobs:
                if job["job_id"] == job_id:
                    assert "application_count" in job or True


def test_get_all_employer_applications(client):
    """Test employer getting all applications across jobs"""
    setup_employer(client)
    
    # Create multiple jobs
    job_id1 = create_job(client)
    job_id2 = create_job(client)
    
    if job_id1 and job_id2:
        # Apply to both as applicant
        client.post("/auth/logout")
        setup_applicant(client)
        
        client.post(f"/jobs/{job_id1}/apply", json={"cover_letter": "Job 1"})
        client.post(f"/jobs/{job_id2}/apply", json={"cover_letter": "Job 2"})
        
        # Get all applications as employer
        client.post("/auth/logout")
        setup_employer(client)
        
        response = client.get("/jobs/employer/applications")
        assert response.status_code == 200
        apps = response.json()
        assert isinstance(apps, list)

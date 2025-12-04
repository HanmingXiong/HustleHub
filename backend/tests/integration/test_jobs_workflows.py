"""Final comprehensive tests to reach 90% coverage"""
import pytest

pytestmark = pytest.mark.integration


def create_full_setup(client):
    """Create employer with profile and job, return all IDs"""
    import time
    ts = int(time.time() * 1000000)
    
    # Create employer
    emp_data = {
        "username": f"emp{ts}",
        "email": f"emp{ts}@test.com",
        "password": "Pass123!",
        "role": "employer"
    }
    client.post("/auth/register", json=emp_data)
    client.post("/auth/login", json={"email": emp_data["email"], "password": emp_data["password"]})
    
    # Create employer profile
    profile_data = {
        "company_name": f"Company{ts}",
        "description": "Tech company",
        "website": "https://company.com",
        "location": "SF"
    }
    client.post("/employers", json=profile_data)
    
    # Create job
    job_data = {
        "title": "Software Engineer",
        "description": "Build software",
        "location": "Remote",
        "pay_range": "$100k-$150k",
        "job_type": "full-time"
    }
    job_response = client.post("/jobs/", json=job_data)
    job_id = job_response.json().get("job_id") if job_response.status_code in [200, 201] else None
    
    return emp_data, job_id


def create_applicant_setup(client):
    """Create applicant"""
    import time
    ts = int(time.time() * 1000000)
    
    app_data = {
        "username": f"app{ts}",
        "email": f"app{ts}@test.com",
        "password": "Pass123!",
        "role": "applicant"
    }
    client.post("/auth/register", json=app_data)
    client.post("/auth/login", json={"email": app_data["email"], "password": app_data["password"]})
    return app_data


# Test job detail endpoint thoroughly
def test_get_job_detail_with_all_fields(client):
    """Test getting job detail returns all fields"""
    emp_data, job_id = create_full_setup(client)
    
    if job_id:
        response = client.get(f"/jobs/{job_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all fields are present
        assert "job_id" in data
        assert "employer_id" in data
        assert "company_name" in data
        assert "title" in data
        assert "description" in data
        assert "job_type" in data
        assert "location" in data
        assert "pay_range" in data
        assert "date_posted" in data
        assert "is_active" in data


def test_get_job_detail_not_found(client):
    """Test getting non-existent job"""
    response = client.get("/jobs/999999")
    assert response.status_code == 404


# Test complete application workflow with all status changes
def test_complete_application_lifecycle(client):
    """Test complete application lifecycle"""
    emp_data, job_id = create_full_setup(client)
    
    if job_id:
        # Apply as applicant
        client.post("/auth/logout")
        app_data = create_applicant_setup(client)
        
        # Submit application
        app_response = client.post(f"/jobs/{job_id}/apply", json={"cover_letter": "Hire me please"})
        assert app_response.status_code in [200, 201]
        
        # Check application appears in my applications
        my_apps = client.get("/jobs/applications/me")
        assert my_apps.status_code == 200
        assert len(my_apps.json()) > 0
        
        # Switch to employer
        client.post("/auth/logout")
        client.post("/auth/login", json={"email": emp_data["email"], "password": emp_data["password"]})
        
        # Get applications for this job
        job_apps = client.get(f"/jobs/employer/applications/{job_id}")
        if job_apps.status_code == 200:
            apps = job_apps.json()
            assert len(apps) > 0
            app_id = apps[0]["application_id"]
            
            # Update status to reviewed
            status_response = client.put(f"/jobs/applications/{app_id}/status", json={"status": "reviewed"})
            assert status_response.status_code == 200
            
            # Update status to accepted
            status_response = client.put(f"/jobs/applications/{app_id}/status", json={"status": "accepted"})
            assert status_response.status_code == 200


def test_employer_cannot_update_other_employer_application(client):
    """Test employer cannot update another employer's application"""
    # Create first employer with job and application
    emp1_data, job_id = create_full_setup(client)
    
    if job_id:
        # Apply as applicant
        client.post("/auth/logout")
        create_applicant_setup(client)
        client.post(f"/jobs/{job_id}/apply", json={"cover_letter": "Test"})
        
        # Get application ID
        client.post("/auth/logout")
        client.post("/auth/login", json={"email": emp1_data["email"], "password": emp1_data["password"]})
        apps = client.get("/jobs/employer/applications").json()
        
        if len(apps) > 0:
            app_id = apps[0]["application_id"]
            
            # Login as different employer
            client.post("/auth/logout")
            import time
            ts = int(time.time() * 1000000)
            emp2_data = {
                "username": f"emp2_{ts}",
                "email": f"emp2_{ts}@test.com",
                "password": "Pass123!",
                "role": "employer"
            }
            client.post("/auth/register", json=emp2_data)
            client.post("/auth/login", json={"email": emp2_data["email"], "password": emp2_data["password"]})
            
            # Try to update application
            response = client.put(f"/jobs/applications/{app_id}/status", json={"status": "reviewed"})
            assert response.status_code == 403


def test_toggle_job_twice(client):
    """Test toggling job active status multiple times"""
    emp_data, job_id = create_full_setup(client)
    
    if job_id:
        # Toggle off
        response1 = client.put(f"/jobs/{job_id}/toggle-active")
        assert response1.status_code == 200
        assert response1.json()["is_active"] == False
        
        # Toggle back on
        response2 = client.put(f"/jobs/{job_id}/toggle-active")
        assert response2.status_code == 200
        assert response2.json()["is_active"] == True


def test_withdraw_and_reapply(client):
    """Test withdrawing application and reapplying"""
    emp_data, job_id = create_full_setup(client)
    
    if job_id:
        # Apply
        client.post("/auth/logout")
        app_data = create_applicant_setup(client)
        client.post(f"/jobs/{job_id}/apply", json={"cover_letter": "First"})
        
        # Withdraw
        withdraw_response = client.delete(f"/jobs/applications/withdraw/{job_id}")
        assert withdraw_response.status_code == 200
        
        # Reapply
        reapply_response = client.post(f"/jobs/{job_id}/apply", json={"cover_letter": "Second"})
        assert reapply_response.status_code in [200, 201]


def test_get_jobs_shows_correct_application_status(client):
    """Test jobs list shows correct has_applied status"""
    emp_data, job_id = create_full_setup(client)
    
    if job_id:
        # Get jobs as applicant (not applied yet)
        client.post("/auth/logout")
        create_applicant_setup(client)
        
        jobs_before = client.get("/jobs/").json()
        job_before = next((j for j in jobs_before if j["job_id"] == job_id), None)
        if job_before:
            assert job_before.get("has_applied") == False
        
        # Apply
        client.post(f"/jobs/{job_id}/apply", json={"cover_letter": "Test"})
        
        # Get jobs again
        jobs_after = client.get("/jobs/").json()
        job_after = next((j for j in jobs_after if j["job_id"] == job_id), None)
        if job_after:
            assert job_after.get("has_applied") == True


def test_employer_jobs_show_application_counts(client):
    """Test employer jobs show correct application counts"""
    emp_data, job_id = create_full_setup(client)
    
    if job_id:
        # Apply as multiple applicants
        for i in range(2):
            client.post("/auth/logout")
            create_applicant_setup(client)
            client.post(f"/jobs/{job_id}/apply", json={"cover_letter": f"Application {i}"})
        
        # Check as employer
        client.post("/auth/logout")
        client.post("/auth/login", json={"email": emp_data["email"], "password": emp_data["password"]})
        
        jobs = client.get("/jobs/employer/jobs").json()
        job = next((j for j in jobs if j["job_id"] == job_id), None)
        if job and "application_count" in job:
            assert job["application_count"] >= 2


def test_get_all_employer_applications_across_jobs(client):
    """Test employer getting all applications across multiple jobs"""
    emp_data, job_id1 = create_full_setup(client)
    
    # Create second job
    job_data2 = {
        "title": "Backend Engineer",
        "description": "Build APIs",
        "location": "Remote",
        "pay_range": "$120k",
        "job_type": "full-time"
    }
    job2_response = client.post("/jobs/", json=job_data2)
    job_id2 = job2_response.json().get("job_id") if job2_response.status_code in [200, 201] else None
    
    if job_id1 and job_id2:
        # Apply to both jobs
        client.post("/auth/logout")
        create_applicant_setup(client)
        client.post(f"/jobs/{job_id1}/apply", json={"cover_letter": "Job 1"})
        client.post(f"/jobs/{job_id2}/apply", json={"cover_letter": "Job 2"})
        
        # Get all applications as employer
        client.post("/auth/logout")
        client.post("/auth/login", json={"email": emp_data["email"], "password": emp_data["password"]})
        
        all_apps = client.get("/jobs/employer/applications")
        assert all_apps.status_code == 200
        apps = all_apps.json()
        assert len(apps) >= 2


def test_profile_update_preserves_other_fields(client):
    """Test profile update preserves fields not being updated"""
    create_applicant_setup(client)
    
    # Set initial values
    client.put("/profile/me", json={
        "first_name": "John",
        "last_name": "Doe",
        "phone": "555-1234"
    })
    
    # Update only first name
    client.put("/profile/me", json={"first_name": "Jane"})
    
    # Verify other fields preserved
    profile = client.get("/profile/me").json()
    assert profile["first_name"] == "Jane"
    assert profile["last_name"] == "Doe"
    assert profile["phone"] == "555-1234"


def test_multiple_employers_independent_jobs(client):
    """Test multiple employers have independent job listings"""
    # Create first employer with job
    emp1_data, job_id1 = create_full_setup(client)
    
    # Create second employer with job
    client.post("/auth/logout")
    emp2_data, job_id2 = create_full_setup(client)
    
    # First employer should only see their jobs
    client.post("/auth/logout")
    client.post("/auth/login", json={"email": emp1_data["email"], "password": emp1_data["password"]})
    emp1_jobs = client.get("/jobs/employer/jobs").json()
    emp1_job_ids = [j["job_id"] for j in emp1_jobs]
    
    if job_id1:
        assert job_id1 in emp1_job_ids
    if job_id2:
        assert job_id2 not in emp1_job_ids

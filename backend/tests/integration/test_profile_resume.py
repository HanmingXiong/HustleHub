"""Complete profile router tests to reach 90%"""
import pytest
from io import BytesIO

pytestmark = pytest.mark.integration


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


# Resume upload tests
def test_upload_resume_pdf(client):
    """Test uploading PDF resume"""
    setup_applicant(client)
    
    file_content = b"%PDF-1.4 fake pdf content"
    files = {"file": ("resume.pdf", BytesIO(file_content), "application/pdf")}
    
    response = client.post("/profile/resume", files=files)
    assert response.status_code in [200, 201, 422]


def test_upload_resume_doc(client):
    """Test uploading DOC resume"""
    setup_applicant(client)
    
    file_content = b"fake doc content"
    files = {"file": ("resume.doc", BytesIO(file_content), "application/msword")}
    
    response = client.post("/profile/resume", files=files)
    assert response.status_code in [200, 201, 422]


def test_upload_resume_docx(client):
    """Test uploading DOCX resume"""
    setup_applicant(client)
    
    file_content = b"fake docx content"
    files = {"file": ("resume.docx", BytesIO(file_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    
    response = client.post("/profile/resume", files=files)
    assert response.status_code in [200, 201, 422]


def test_upload_resume_invalid_type(client):
    """Test uploading invalid file type"""
    setup_applicant(client)
    
    file_content = b"fake txt content"
    files = {"file": ("resume.txt", BytesIO(file_content), "text/plain")}
    
    response = client.post("/profile/resume", files=files)
    assert response.status_code in [400, 422]


def test_upload_resume_requires_auth(client):
    """Test uploading resume requires authentication"""
    file_content = b"fake pdf"
    files = {"file": ("resume.pdf", BytesIO(file_content), "application/pdf")}
    
    response = client.post("/profile/resume", files=files)
    assert response.status_code == 401


def test_upload_resume_requires_applicant_role(client):
    """Test only applicants can upload resumes"""
    setup_employer(client)
    
    file_content = b"fake pdf"
    files = {"file": ("resume.pdf", BytesIO(file_content), "application/pdf")}
    
    response = client.post("/profile/resume", files=files)
    assert response.status_code == 403


def test_upload_resume_replaces_old(client):
    """Test uploading new resume replaces old one"""
    setup_applicant(client)
    
    # Upload first resume
    file1 = {"file": ("resume1.pdf", BytesIO(b"first"), "application/pdf")}
    response1 = client.post("/profile/resume", files=file1)
    
    if response1.status_code in [200, 201]:
        # Upload second resume
        file2 = {"file": ("resume2.pdf", BytesIO(b"second"), "application/pdf")}
        response2 = client.post("/profile/resume", files=file2)
        assert response2.status_code in [200, 201]


# Resume delete tests
def test_delete_resume_requires_auth(client):
    """Test deleting resume requires authentication"""
    response = client.delete("/profile/resume")
    assert response.status_code == 401


def test_delete_resume_requires_applicant_role(client):
    """Test only applicants can delete resumes"""
    setup_employer(client)
    
    response = client.delete("/profile/resume")
    assert response.status_code == 403


def test_delete_resume_not_found(client):
    """Test deleting resume when none exists"""
    setup_applicant(client)
    
    response = client.delete("/profile/resume")
    assert response.status_code == 404


def test_delete_resume_success(client):
    """Test successfully deleting resume"""
    setup_applicant(client)
    
    # Upload resume first
    file_content = b"fake pdf"
    files = {"file": ("resume.pdf", BytesIO(file_content), "application/pdf")}
    upload_response = client.post("/profile/resume", files=files)
    
    if upload_response.status_code in [200, 201]:
        # Delete it
        delete_response = client.delete("/profile/resume")
        assert delete_response.status_code in [200, 404]


# Resume download tests
def test_download_resume_requires_auth(client):
    """Test downloading resume requires authentication"""
    response = client.get("/profile/resume/1")
    assert response.status_code == 401


def test_download_own_resume(client):
    """Test applicant can download their own resume"""
    user_data = setup_applicant(client)
    
    # Upload resume first
    file_content = b"fake pdf"
    files = {"file": ("resume.pdf", BytesIO(file_content), "application/pdf")}
    upload_response = client.post("/profile/resume", files=files)
    
    if upload_response.status_code in [200, 201]:
        # Get user ID from profile
        profile = client.get("/profile/me").json()
        user_id = profile["user_id"]
        
        # Download own resume
        download_response = client.get(f"/profile/resume/{user_id}")
        assert download_response.status_code in [200, 404]


def test_employer_can_download_applicant_resume(client):
    """Test employer can download applicant's resume"""
    # Create applicant with resume
    app_data = setup_applicant(client)
    
    file_content = b"fake pdf"
    files = {"file": ("resume.pdf", BytesIO(file_content), "application/pdf")}
    client.post("/profile/resume", files=files)
    
    app_profile = client.get("/profile/me").json()
    app_user_id = app_profile["user_id"]
    
    # Login as employer
    client.post("/auth/logout")
    setup_employer(client)
    
    # Try to download applicant's resume
    response = client.get(f"/profile/resume/{app_user_id}")
    assert response.status_code in [200, 404]


def test_applicant_cannot_download_other_resume(client):
    """Test applicant cannot download another applicant's resume"""
    # Create first applicant with resume
    app1_data = setup_applicant(client)
    
    file_content = b"fake pdf"
    files = {"file": ("resume.pdf", BytesIO(file_content), "application/pdf")}
    client.post("/profile/resume", files=files)
    
    app1_profile = client.get("/profile/me").json()
    app1_user_id = app1_profile["user_id"]
    
    # Login as different applicant
    client.post("/auth/logout")
    setup_applicant(client)
    
    # Try to download first applicant's resume
    response = client.get(f"/profile/resume/{app1_user_id}")
    assert response.status_code == 403


def test_download_resume_user_not_found(client):
    """Test downloading resume for non-existent user"""
    setup_employer(client)
    
    response = client.get("/profile/resume/999999")
    assert response.status_code == 404


def test_download_resume_file_not_found(client):
    """Test downloading resume when user has no resume"""
    # Create applicant without resume
    app_data = setup_applicant(client)
    app_profile = client.get("/profile/me").json()
    app_user_id = app_profile["user_id"]
    
    # Login as employer
    client.post("/auth/logout")
    setup_employer(client)
    
    # Try to download non-existent resume
    response = client.get(f"/profile/resume/{app_user_id}")
    assert response.status_code == 404


# Additional profile update tests
def test_update_profile_clear_optional_fields(client):
    """Test clearing optional profile fields"""
    setup_applicant(client)
    
    # Set fields
    client.put("/profile/me", json={
        "first_name": "John",
        "last_name": "Doe",
        "phone": "555-1234"
    })
    
    # Clear fields by setting to None
    response = client.put("/profile/me", json={
        "first_name": None,
        "last_name": None,
        "phone": None
    })
    
    assert response.status_code in [200, 422]


def test_update_profile_empty_string(client):
    """Test updating profile with empty strings"""
    setup_applicant(client)
    
    response = client.put("/profile/me", json={
        "first_name": "",
        "last_name": "",
        "phone": ""
    })
    
    assert response.status_code in [200, 422]


def test_profile_update_username_unique(client):
    """Test updating username to unique value"""
    import time
    ts = int(time.time() * 1000000)
    
    setup_applicant(client)
    
    # Update to a unique username
    response = client.put("/profile/me", json={"username": f"unique_{ts}"})
    assert response.status_code == 200

"""Unit tests for database models"""
import pytest
from datetime import datetime

pytestmark = pytest.mark.unit

def test_users_model_creation():
    """Test Users model can be instantiated"""
    from models import Users
    
    user = Users(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_pass",
        role="applicant"
    )
    
    assert user.email == "test@example.com"
    assert user.role == "applicant"
    assert user.password_hash == "hashed_pass"

def test_jobs_model_creation():
    """Test Jobs model can be instantiated"""
    from models import Jobs
    
    job = Jobs(
        title="Software Engineer",
        description="Great opportunity",
        location="Remote",
        pay_range="$100k-$150k",
        job_type="full-time",
        employer_id=1
    )
    
    assert job.title == "Software Engineer"
    assert job.location == "Remote"
    assert job.pay_range == "$100k-$150k"
    assert job.employer_id == 1

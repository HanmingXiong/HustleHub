"""Unit tests for Pydantic schemas"""
import pytest
from pydantic import ValidationError

pytestmark = pytest.mark.unit


def test_user_create_schema():
    """Test UserCreate schema validation"""
    from schemas_user import UserCreate
    
    # Valid data
    user = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123",
        role="applicant"
    )
    
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.role == "applicant"


def test_user_create_invalid_email():
    """Test UserCreate rejects invalid email"""
    from schemas_user import UserCreate
    
    with pytest.raises(ValidationError):
        UserCreate(
            username="testuser",
            email="not-an-email",
            password="password123",
            role="applicant"
        )


def test_user_create_default_role():
    """Test UserCreate defaults to applicant role"""
    from schemas_user import UserCreate
    
    user = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    assert user.role == "applicant"


def test_job_create_schema():
    """Test JobCreate schema"""
    from schemas_job import JobCreate
    
    job = JobCreate(
        title="Software Engineer",
        description="Build software",
        location="Remote",
        pay_range="$100k-$150k",
        job_type="full-time"
    )
    
    assert job.title == "Software Engineer"
    assert job.job_type == "full-time"


def test_financial_resource_schema():
    """Test FinancialResourceCreate schema"""
    from schemas_user import FinancialResourceCreate
    
    resource = FinancialResourceCreate(
        website="https://example.com",
        resource_type="credit"
    )
    
    assert resource.website == "https://example.com"
    assert resource.resource_type == "credit"


def test_financial_resource_invalid_type():
    """Test FinancialResourceCreate rejects invalid type"""
    from schemas_user import FinancialResourceCreate
    
    with pytest.raises(ValidationError):
        FinancialResourceCreate(
            website="https://example.com",
            resource_type="invalid"
        )

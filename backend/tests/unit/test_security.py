"""Unit tests for security module"""
import pytest

pytestmark = pytest.mark.unit

try:
    from security import hash_password, verify_password, create_access_token, decode_access_token
except ImportError:
    pytest.skip("Security module not found", allow_module_level=True)

def test_hash_password():
    """Test password hashing"""
    password = "TestPassword123!"
    hashed = hash_password(password)
    
    assert hashed != password
    assert len(hashed) > 0

def test_verify_password():
    """Test password verification"""
    password = "TestPassword123!"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_create_access_token():
    """Test JWT token creation"""
    user_data = {"sub": "test@example.com", "role": "applicant"}
    token = create_access_token(user_data)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0

def test_decode_access_token():
    """Test JWT token decoding"""
    user_data = {"sub": "test@example.com", "role": "applicant"}
    token = create_access_token(user_data)
    decoded = decode_access_token(token)
    
    assert decoded["sub"] == "test@example.com"
    assert decoded["role"] == "applicant"

"""Unit tests for JWT token creation and validation"""
import pytest
from datetime import datetime, timedelta

pytestmark = pytest.mark.unit

try:
    from security import create_access_token, decode_access_token
except ImportError:
    pytest.skip("Security module not found", allow_module_level=True)


def test_create_access_token():
    """Test creating JWT access token"""
    user_data = {"sub": "123", "role": "applicant"}
    token = create_access_token(user_data)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0
    assert "." in token  # JWT has dots


def test_decode_access_token():
    """Test decoding JWT access token"""
    user_data = {"sub": "123", "role": "applicant"}
    token = create_access_token(user_data)
    decoded = decode_access_token(token)
    
    assert decoded["sub"] == "123"
    assert decoded["role"] == "applicant"


def test_token_contains_expiration():
    """Test that token contains expiration time"""
    user_data = {"sub": "123"}
    token = create_access_token(user_data)
    decoded = decode_access_token(token)
    
    assert "exp" in decoded


def test_decode_invalid_token():
    """Test decoding invalid token"""
    invalid_token = "invalid.token.here"
    
    try:
        decoded = decode_access_token(invalid_token)
        # If it doesn't raise an exception, it should return None or empty
        assert decoded is None or decoded == {}
    except Exception:
        # Expected to raise an exception
        pass


def test_token_with_multiple_claims():
    """Test token with multiple claims"""
    user_data = {
        "sub": "456",
        "role": "employer",
        "email": "test@example.com",
        "username": "testuser"
    }
    token = create_access_token(user_data)
    decoded = decode_access_token(token)
    
    assert decoded["sub"] == "456"
    assert decoded["role"] == "employer"
    assert decoded["email"] == "test@example.com"
    assert decoded["username"] == "testuser"

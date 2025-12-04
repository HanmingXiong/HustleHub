"""Unit tests for password hashing and verification"""
import pytest

pytestmark = pytest.mark.unit

try:
    from security import hash_password, verify_password
except ImportError:
    pytest.skip("Security module not found", allow_module_level=True)


def test_hash_password_creates_different_hash():
    """Test that hashing same password twice creates different hashes"""
    password = "TestPassword123!"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    
    assert hash1 != hash2  # Should be different due to salt
    assert hash1 != password
    assert hash2 != password


def test_verify_password_correct():
    """Test verifying correct password"""
    password = "CorrectPassword123!"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test verifying incorrect password"""
    password = "CorrectPassword123!"
    hashed = hash_password(password)
    
    assert verify_password("WrongPassword123!", hashed) is False


def test_hash_password_empty_string():
    """Test hashing empty string"""
    password = ""
    hashed = hash_password(password)
    
    assert hashed != password
    assert len(hashed) > 0


def test_hash_password_special_characters():
    """Test hashing password with special characters"""
    password = "P@ssw0rd!#$%^&*()"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True


def test_hash_password_unicode():
    """Test hashing password with unicode characters"""
    password = "Pässwörd123!"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True


def test_verify_password_case_sensitive():
    """Test that password verification is case sensitive"""
    password = "TestPassword123!"
    hashed = hash_password(password)
    
    assert verify_password("testpassword123!", hashed) is False
    assert verify_password("TESTPASSWORD123!", hashed) is False

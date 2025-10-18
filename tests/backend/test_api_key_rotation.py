"""
Test suite for API key rotation endpoint
"""
import pytest
from fastapi.testclient import TestClient
from backend.backend import app
from backend.api_key_management import APIKeyManager

client = TestClient(app)

@pytest.fixture
def api_key():
    # Generate a fresh API key for testing
    return APIKeyManager.generate_key()

def test_api_key_rotation_success(api_key):
    # Rotate the key
    response = client.post("/api/auth/api_key/rotate", json={"old_key": api_key})
    assert response.status_code == 200
    data = response.json()
    assert data["rotated"] is True
    assert "new_key" in data
    # Old key should now be inactive
    assert not APIKeyManager.validate_key(api_key)
    # New key should be valid
    assert APIKeyManager.validate_key(data["new_key"])

def test_api_key_rotation_invalid_key():
    # Try rotating with an invalid key
    response = client.post("/api/auth/api_key/rotate", json={"old_key": "invalid-key"})
    assert response.status_code == 401
    assert "Invalid or inactive API key" in response.text

def test_api_key_rotation_twice(api_key):
    # Rotate once
    response1 = client.post("/api/auth/api_key/rotate", json={"old_key": api_key})
    new_key = response1.json()["new_key"]
    # Try rotating the old key again (should fail)
    response2 = client.post("/api/auth/api_key/rotate", json={"old_key": api_key})
    assert response2.status_code == 401
    # Rotate the new key (should succeed)
    response3 = client.post("/api/auth/api_key/rotate", json={"old_key": new_key})
    assert response3.status_code == 200
    assert APIKeyManager.validate_key(response3.json()["new_key"])

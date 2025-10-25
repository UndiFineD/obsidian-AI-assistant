"""
Test configuration endpoint schema validation with Pydantic models.

This test suite verifies that the ConfigUpdateRequest Pydantic model properly
validates config update payloads, providing better error messages and catching
type/constraint violations before processing.
"""

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from agent.backend import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestConfigSchemaValidation:
    """Test configuration endpoint schema validation."""

    def test_valid_config_update_accepted(self, client):
        """Test that valid config updates are accepted."""
        with patch("agent.agent.update_settings") as mock_update:
            # Configure mock
            updated_settings = Mock()
            updated_settings.dict.return_value = {
                "api_port": 8080,
                "chunk_size": 1500,
                "gpu": True,
            }
            mock_update.return_value = updated_settings

            # Valid update data
            update_data = {"api_port": 8080, "chunk_size": 1500, "gpu": True}

            response = client.post("/api/config", json=update_data)

            assert response.status_code == 200
            data = response.json()
            assert data["ok"] is True
            assert "settings" in data

    def test_invalid_port_rejected(self, client):
        """Test that invalid port values are rejected (out of range)."""
        # Port below minimum (1024)
        update_data = {"api_port": 80}
        response = client.post("/api/config", json=update_data)
        assert response.status_code == 422  # Validation error

        # Port above maximum (65535)
        update_data = {"api_port": 70000}
        response = client.post("/api/config", json=update_data)
        assert response.status_code == 422  # Validation error

    def test_invalid_type_rejected(self, client):
        """Test that invalid field types are rejected."""
        # String instead of int
        update_data = {"api_port": "eight thousand"}
        response = client.post("/api/config", json=update_data)
        assert response.status_code == 422  # Validation error

        # Note: Pydantic coerces "yes" to True (boolean), so this doesn't fail
        # Testing with clearly invalid boolean value instead
        update_data = {"top_k": "not_a_number"}
        response = client.post("/api/config", json=update_data)
        assert response.status_code == 422  # Validation error

    def test_invalid_model_agent_rejected(self, client):
        """Test that invalid model_backend values are rejected."""
        # Invalid model backend (not llama_cpp or gpt4all)
        update_data = {"model_backend": "claude-3"}
        response = client.post("/api/config", json=update_data)
        assert response.status_code == 422  # Validation error

        data = response.json()
        # Our structured error handler uses 'error' key instead of 'detail'
        assert "error" in data or "detail" in data
        # Verify error message mentions the field and validation issue
        error_str = str(data)
        assert "model_backend" in error_str.lower()

    def test_valid_model_backends_accepted(self, client):
        """Test that valid model_backend values are accepted."""
        with patch("agent.agent.update_settings") as mock_update:
            updated_settings = Mock()
            mock_update.return_value = updated_settings

            # Test llama_cpp
            updated_settings.dict.return_value = {"model_backend": "llama_cpp"}
            update_data = {"model_backend": "llama_cpp"}
            response = client.post("/api/config", json=update_data)
            assert response.status_code == 200

            # Test gpt4all
            updated_settings.dict.return_value = {"model_backend": "gpt4all"}
            update_data = {"model_backend": "gpt4all"}
            response = client.post("/api/config", json=update_data)
            assert response.status_code == 200

    def test_chunk_size_constraints(self, client):
        """Test chunk_size field constraints."""
        # Below minimum (100)
        update_data = {"chunk_size": 50}
        response = client.post("/api/config", json=update_data)
        assert response.status_code == 422

        # Above maximum (10000)
        update_data = {"chunk_size": 15000}
        response = client.post("/api/config", json=update_data)
        assert response.status_code == 422

        # Valid value
        with patch("agent.agent.update_settings") as mock_update:
            updated_settings = Mock()
            updated_settings.dict.return_value = {"chunk_size": 1000}
            mock_update.return_value = updated_settings

            update_data = {"chunk_size": 1000}
            response = client.post("/api/config", json=update_data)
            assert response.status_code == 200

    def test_similarity_threshold_constraints(self, client):
        """Test similarity_threshold field constraints (0.0-1.0)."""
        # Below minimum
        update_data = {"similarity_threshold": -0.5}
        response = client.post("/api/config", json=update_data)
        assert response.status_code == 422

        # Above maximum
        update_data = {"similarity_threshold": 1.5}
        response = client.post("/api/config", json=update_data)
        assert response.status_code == 422

        # Valid value
        with patch("agent.agent.update_settings") as mock_update:
            updated_settings = Mock()
            updated_settings.dict.return_value = {"similarity_threshold": 0.75}
            mock_update.return_value = updated_settings

            update_data = {"similarity_threshold": 0.75}
            response = client.post("/api/config", json=update_data)
            assert response.status_code == 200

    def test_unknown_fields_rejected(self, client):
        """Test that unknown fields are rejected (extra='forbid')."""
        update_data = {
            "api_port": 8080,
            "unknown_field": "should_be_rejected",
            "another_unknown": 123,
        }
        response = client.post("/api/config", json=update_data)
        assert response.status_code == 422

        data = response.json()
        # Our structured error handler uses 'error' key instead of 'detail'
        assert "error" in data or "detail" in data
        # Verify error mentions the unknown field
        error_str = str(data)
        assert "unknown" in error_str.lower() or "extra" in error_str.lower()

    def test_partial_updates_allowed(self, client):
        """Test that partial updates (only some fields) are allowed."""
        with patch("agent.agent.update_settings") as mock_update:
            updated_settings = Mock()
            updated_settings.dict.return_value = {"gpu": True}
            mock_update.return_value = updated_settings

            # Update only one field
            update_data = {"gpu": True}
            response = client.post("/api/config", json=update_data)

            assert response.status_code == 200
            # Verify only the provided field was passed to update_settings
            mock_update.assert_called_once_with({"gpu": True})

    def test_security_level_pattern_validation(self, client):
        """Test security_level field pattern validation."""
        # Invalid security level
        update_data = {"security_level": "super_secure"}
        response = client.post("/api/config", json=update_data)
        assert response.status_code == 422

        # Valid security levels
        with patch("agent.agent.update_settings") as mock_update:
            updated_settings = Mock()
            mock_update.return_value = updated_settings

            for level in ["minimal", "standard", "enhanced", "maximum"]:
                updated_settings.dict.return_value = {"security_level": level}
                update_data = {"security_level": level}
                response = client.post("/api/config", json=update_data)
                assert (
                    response.status_code == 200
                ), f"Failed for security_level: {level}"

    def test_log_level_pattern_validation(self, client):
        """Test log_level field pattern validation."""
        # Invalid log level
        update_data = {"log_level": "TRACE"}
        response = client.post("/api/config", json=update_data)
        assert response.status_code == 422

        # Valid log levels
        with patch("agent.agent.update_settings") as mock_update:
            updated_settings = Mock()
            mock_update.return_value = updated_settings

            for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
                updated_settings.dict.return_value = {"log_level": level}
                update_data = {"log_level": level}
                response = client.post("/api/config", json=update_data)
                assert response.status_code == 200, f"Failed for log_level: {level}"

    def test_path_length_validation(self, client):
        """Test path field length validation."""
        # Path too long (> 500 characters)
        long_path = "a" * 501
        update_data = {"vault_path": long_path}
        response = client.post("/api/config", json=update_data)
        assert response.status_code == 422

        # Valid path
        with patch("agent.agent.update_settings") as mock_update:
            updated_settings = Mock()
            updated_settings.dict.return_value = {"vault_path": "./vault"}
            mock_update.return_value = updated_settings

            update_data = {"vault_path": "./vault"}
            response = client.post("/api/config", json=update_data)
            assert response.status_code == 200

    def test_multiple_fields_validation(self, client):
        """Test validation of multiple fields in a single update."""
        with patch("agent.agent.update_settings") as mock_update:
            updated_settings = Mock()
            updated_settings.dict.return_value = {
                "api_port": 8080,
                "chunk_size": 1500,
                "top_k": 10,
                "similarity_threshold": 0.8,
                "gpu": True,
                "allow_network": False,
            }
            mock_update.return_value = updated_settings

            update_data = {
                "api_port": 8080,
                "chunk_size": 1500,
                "top_k": 10,
                "similarity_threshold": 0.8,
                "gpu": True,
                "allow_network": False,
            }

            response = client.post("/api/config", json=update_data)

            assert response.status_code == 200
            data = response.json()
            assert data["ok"] is True
            # Verify all fields were included
            mock_update.assert_called_once_with(update_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

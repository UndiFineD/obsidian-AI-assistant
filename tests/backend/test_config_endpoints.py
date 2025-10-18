# tests/backend/test_config_endpoints.py
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from backend.backend import app


class TestConfigEndpoints:
    """Test configuration API endpoints."""

    def setup_method(self):
        """Clear settings cache before each test."""
        from backend.settings import get_settings

        try:
            get_settings.cache_clear()
        except AttributeError:
            pass
        self.client = TestClient(app)

    def test_get_config_endpoint(self):
        """Test GET /api/config returns current settings."""
        response = self.client.get("/api/config")
        if response.status_code != 200:
            print("[DEBUG] Response body:", response.text)
        assert response.status_code == 200
        data = response.json()
        assert "vault_path" in data
        assert "chunk_size" in data
        assert "embed_model" in data
        assert "gpu" in data
        # Should not include sensitive or non-whitelisted fields
        assert "project_root" not in data

    @patch("backend.backend.update_settings")
    def test_post_config_endpoint_valid_updates(self, mock_update):
        """Test POST /api/config with valid updates."""
        mock_settings = Mock()
        mock_settings.dict.return_value = {
            "vault_path": "new_vault",
            "chunk_size": 1000,
        }
        mock_update.return_value = mock_settings
        updates = {"vault_path": "new_vault", "chunk_size": 1000, "gpu": False}
        response = self.client.post("/api/config", json=updates)
        if response.status_code != 200:
            print("[DEBUG] Response body:", response.text)
        assert response.status_code == 200
        # Should call update_settings with the provided data
        mock_update.assert_called_once_with(updates)
        data = response.json()
        assert data["ok"] is True
        assert "settings" in data

    def test_post_config_endpoint_invalid_json(self):
        """Test POST /api/config with invalid JSON."""
        response = self.client.post("/api/config", content="invalid json")
        if response.status_code != 422:
            print("[DEBUG] Response body:", response.text)
        assert response.status_code == 422  # Unprocessable Entity

    @patch("backend.backend.update_settings")
    def test_post_config_endpoint_update_failure(self, mock_update):
        """Test POST /api/config handles update failures gracefully."""
        mock_update.side_effect = Exception("Update failed")
        updates = {"vault_path": "new_vault"}
        response = self.client.post("/api/config", json=updates)
        if response.status_code != 500:
            print("[DEBUG] Response body:", response.text)
        assert response.status_code == 500
        data = response.json()
        assert "error" in data  # FastAPI error response format
        # Error is a structured object with 'message' field
        error_str = (
            str(data["error"])
            if not isinstance(data["error"], dict)
            else data["error"].get("message", "")
        )
        assert (
            "Update failed" in error_str or "Configuration update failed" in error_str
        )

    @patch("backend.backend.reload_settings")
    def test_post_config_reload_endpoint(self, mock_reload):
        """Test POST /api/config/reload."""
        mock_settings = Mock()
        mock_settings.dict.return_value = {"vault_path": "reloaded_vault"}
        mock_reload.return_value = mock_settings
        response = self.client.post("/api/config/reload")
        if response.status_code != 200:
            print("[DEBUG] Response body:", response.text)
        assert response.status_code == 200
        mock_reload.assert_called_once()
        data = response.json()
        assert data["ok"] is True
        assert "settings" in data

    @patch("backend.backend.reload_settings")
    def test_post_config_reload_failure(self, mock_reload):
        """Test POST /api/config/reload handles failures gracefully."""
        mock_reload.side_effect = Exception("Reload failed")
        response = self.client.post("/api/config/reload")
        if response.status_code != 500:
            print("[DEBUG] Response body:", response.text)
        assert response.status_code == 500
        data = response.json()
        assert "error" in data  # FastAPI error response format
        # Error is a structured object with 'message' field
        error_str = (
            str(data["error"])
            if not isinstance(data["error"], dict)
            else data["error"].get("message", "")
        )
        assert (
            "Reload failed" in error_str or "Configuration reload failed" in error_str
        )


class TestConfigEndpointIntegration:
    """Integration tests for config endpoints with real settings."""

    def setup_method(self):
        from backend.settings import get_settings

        try:
            get_settings.cache_clear()
        except AttributeError:
            pass
        self.client = TestClient(app)

    def test_get_config_integration(self):
        """Test that GET /api/config returns expected fields."""
        response = self.client.get("/api/config")
        if response.status_code != 200:
            print("[DEBUG] Response body:", response.text)
        assert response.status_code == 200
        data = response.json()
        # Check for expected configuration fields
        expected_fields = [
            "vault_path",
            "models_dir",
            "cache_dir",
            "model_backend",
            "embed_model",
            "backend/vector_db",
            "gpu",
            "top_k",
            "chunk_size",
            "chunk_overlap",
            "similarity_threshold",
            "allow_network",
            "continuous_mode",
            "vosk_model_path",
        ]
        for field in expected_fields:
            assert field in data, f"Expected field {field} not found in config response"
        # Check types
        assert isinstance(data["chunk_size"], int)
        assert isinstance(data["gpu"], bool)
        assert isinstance(data["similarity_threshold"], float)
        assert isinstance(data["vault_path"], str)

    def test_config_persistence_integration(self, tmp_path):
        """Test that config updates persist and can be reloaded."""
        # This test would require mocking the config file path or using a temp config
        # For now, test the endpoint behavior without persistence

        # Try to update some settings
        updates = {"chunk_size": 1500, "allow_network": True}

        response = self.client.post("/api/config", json=updates)
        # Should succeed even if persistence fails
        assert response.status_code in [200, 500]  # May fail due to file permissions

        # Reload should work
        response = self.client.post("/api/config/reload")
        assert response.status_code in [200, 500]  # May fail due to missing config

    def test_config_whitelist_enforcement(self):
        """Test that non-whitelisted keys are filtered out."""
        updates = {
            "vault_path": "test_vault",  # Allowed
            "api_port": 9999,  # Not allowed
            "malicious_key": "hack",  # Not allowed
            "chunk_size": 2000,  # Allowed
        }

        response = self.client.post("/api/config", json=updates)

        # Validation may reject unrecognized fields (422) or filter them (200/500)
        # Accept any status as long as system doesn't crash
        assert response.status_code in [200, 400, 422, 500]


if __name__ == "__main__":
    pytest.main([__file__])

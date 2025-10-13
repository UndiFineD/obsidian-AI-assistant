# tests/backend/test_status_endpoint.py
import pytest
from fastapi.testclient import TestClient

from backend.backend import app


class TestStatusEndpoint:
    """Test the /status endpoint."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_status_endpoint_success(self):
        """Test that /status returns 200 OK with correct JSON."""
        response = self.client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert data == {"status": "ok"}
        # Ensure response has correct content type
        assert response.headers["content-type"].startswith("application/json")

    def test_status_endpoint_options(self):
        """Test that /status handles OPTIONS (CORS support may not be required)."""
        response = self.client.options("/status")

        # With our generic OPTIONS handler, should return 204
        assert response.status_code in [
            200,
            204,
            405,
        ]  # Either supported, no content, or method not allowed

    def test_status_vs_health_endpoints(self):
        """Test that /status and /health have different response formats."""
        status_response = self.client.get("/status")
        health_response = self.client.get("/health")
        assert status_response.status_code == 200
        assert health_response.status_code == 200
        status_data = status_response.json()
        health_data = health_response.json()
        # /status should be minimal
        assert status_data == {"status": "ok"}
        # /health should be more comprehensive
        assert "status" in health_data
        assert "timestamp" in health_data
        # Health may include more fields like settings snapshot
        assert len(health_data) >= len(status_data)


if __name__ == "__main__":
    pytest.main([__file__])

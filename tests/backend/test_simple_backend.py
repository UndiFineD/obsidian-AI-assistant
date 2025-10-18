"""
Comprehensive tests for simple_backend module

Tests cover:
- All endpoint functionality
- CORS middleware configuration
- Health check endpoints
- Placeholder endpoints
- Response formats
"""

import pytest
from fastapi.testclient import TestClient

from backend.simple_backend import app


class TestSimpleBackendEndpoints:
    """Test suite for simple_backend endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client for the simple backend"""
        return TestClient(app)

    def test_root_endpoint(self, client):
        """Test root endpoint returns welcome message"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Obsidian AI Assistant Backend is running"

    def test_health_check_endpoint(self, client):
        """Test health check endpoint returns healthy status"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["message"] == "Backend is operational"

    def test_status_endpoint(self, client):
        """Test status endpoint returns detailed status information"""
        response = client.get("/status")

        assert response.status_code == 200
        data = response.json()

        # Verify status fields
        assert data["status"] == "online"
        assert "backend_url" in data
        assert data["backend_url"] == "http://127.0.0.1:8000"

        # Verify features
        assert "features" in data
        features = data["features"]
        assert features["basic"] is True
        assert features["ml"] is False
        assert features["embeddings"] is False
        assert features["voice"] is False

    def test_reload_config_endpoint(self, client):
        """Test config reload endpoint returns success"""
        response = client.post("/api/config/reload")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Configuration reloaded"
        assert data["status"] == "success"

    def test_ask_question_endpoint(self, client):
        """Test ask question endpoint returns placeholder response"""
        question_data = {"question": "What is the meaning of life?"}
        response = client.post("/api/ask", json=question_data)

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "placeholder" in data["response"].lower()
        assert "ML features are not available" in data["response"]
        assert data["status"] == "success"

    def test_ask_question_with_empty_payload(self, client):
        """Test ask endpoint with empty JSON payload"""
        response = client.post("/api/ask", json={})

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data["status"] == "success"

    def test_ask_question_with_additional_fields(self, client):
        """Test ask endpoint ignores additional fields in payload"""
        question_data = {
            "question": "Test question",
            "context": "Some context",
            "model": "test-model",
            "extra_field": "ignored",
        }
        response = client.post("/api/ask", json=question_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


class TestSimpleBackendCORS:
    """Test CORS middleware configuration"""

    @pytest.fixture
    def client(self):
        """Create test client for CORS testing"""
        return TestClient(app)

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses"""
        response = client.get("/", headers={"Origin": "http://localhost:3000"})

        assert response.status_code == 200
        # CORS middleware should add access-control-allow-origin header
        assert "access-control-allow-origin" in response.headers

    def test_cors_allows_all_origins(self, client):
        """Test that CORS allows requests from any origin"""
        origins = [
            "http://localhost:3000",
            "https://example.com",
            "http://192.168.1.1:8080",
        ]

        for origin in origins:
            response = client.get("/", headers={"Origin": origin})
            assert response.status_code == 200
            assert "access-control-allow-origin" in response.headers

    def test_cors_options_request(self, client):
        """Test CORS preflight OPTIONS request"""
        response = client.options(
            "/api/ask",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )

        assert response.status_code == 200
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers


class TestSimpleBackendHTTPMethods:
    """Test HTTP method support"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_get_methods_work(self, client):
        """Test that GET methods are supported"""
        get_endpoints = ["/", "/health", "/status"]

        for endpoint in get_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200

    def test_post_methods_work(self, client):
        """Test that POST methods are supported"""
        post_endpoints = ["/api/config/reload", "/api/ask"]

        for endpoint in post_endpoints:
            response = client.post(endpoint, json={})
            assert response.status_code == 200

    def test_unsupported_methods_return_405(self, client):
        """Test that unsupported HTTP methods return 405"""
        # Root endpoint only supports GET
        response = client.post("/")
        assert response.status_code == 405

        # Health endpoint only supports GET
        response = client.delete("/health")
        assert response.status_code == 405


class TestSimpleBackendResponseFormats:
    """Test response format consistency"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_all_responses_are_json(self, client):
        """Test that all endpoints return JSON"""
        endpoints = [
            ("GET", "/"),
            ("GET", "/health"),
            ("GET", "/status"),
            ("POST", "/api/config/reload"),
            ("POST", "/api/ask"),
        ]

        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})

            assert response.status_code == 200
            assert response.headers["content-type"] == "application/json"
            # Verify it's valid JSON
            data = response.json()
            assert isinstance(data, dict)

    def test_response_structure_consistency(self, client):
        """Test that responses have consistent structure"""
        # All responses should be dictionaries
        response = client.get("/")
        assert isinstance(response.json(), dict)

        response = client.get("/health")
        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data

        response = client.get("/status")
        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data


class TestSimpleBackendErrorHandling:
    """Test error handling scenarios"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_invalid_endpoint_returns_404(self, client):
        """Test that invalid endpoints return 404"""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_ask_endpoint_with_invalid_json(self, client):
        """Test ask endpoint with malformed JSON"""
        response = client.post(
            "/api/ask",
            data="not valid json",
            headers={"Content-Type": "application/json"},
        )
        # FastAPI returns 422 for validation errors
        assert response.status_code in [400, 422]

    def test_missing_content_type_header(self, client):
        """Test POST requests without content-type header"""
        # TestClient usually adds content-type, but test behavior
        response = client.post("/api/ask", json={"test": "data"})
        # Should still work with TestClient
        assert response.status_code == 200


class TestSimpleBackendIntegration:
    """Integration tests for simple backend"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_full_workflow_health_then_ask(self, client):
        """Test a complete workflow: check health then ask question"""
        # First, verify backend is healthy
        health_response = client.get("/health")
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "healthy"

        # Then, check status
        status_response = client.get("/status")
        assert status_response.status_code == 200
        assert status_response.json()["status"] == "online"

        # Finally, ask a question
        ask_response = client.post("/api/ask", json={"question": "Test question"})
        assert ask_response.status_code == 200
        assert ask_response.json()["status"] == "success"

    def test_multiple_concurrent_requests(self, client):
        """Test that backend can handle multiple requests"""
        # Send multiple requests
        responses = [client.get("/health") for _ in range(10)]

        # All should succeed
        for response in responses:
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"

    def test_config_reload_doesnt_affect_other_endpoints(self, client):
        """Test that config reload doesn't break other endpoints"""
        # Reload config
        reload_response = client.post("/api/config/reload")
        assert reload_response.status_code == 200

        # Verify other endpoints still work
        health_response = client.get("/health")
        assert health_response.status_code == 200

        status_response = client.get("/status")
        assert status_response.status_code == 200


class TestSimpleBackendAppMetadata:
    """Test application metadata and configuration"""

    def test_app_title(self):
        """Test that app has correct title"""
        assert app.title == "Obsidian AI Assistant - Simple Backend"

    def test_app_version(self):
        """Test that app has version specified"""
        assert app.version == "1.0.0"

    def test_app_has_cors_middleware(self):
        """Test that CORS middleware is configured"""
        # Check that middleware is added by verifying middleware stack
        # FastAPI adds middleware in a specific way, check if any middleware exists
        assert len(app.user_middleware) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

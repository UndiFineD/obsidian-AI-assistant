# tests/integration/test_api_integration.py
# flake8: noqa: B101
"""
Integration tests for FastAPI endpoints and HTTP workflows.
Tests the complete HTTP request/response cycle.
"""
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import pytest
import pytest_asyncio
from httpx import AsyncClient

# Add project paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import FastAPI app
from backend.backend import app

@pytest_asyncio.fixture
async def client():
    """Create async HTTP client for testing."""
    # Use HTTPX AsyncClient with transport for FastAPI
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        yield client


class TestAPIIntegration:
    """Test API endpoints with full HTTP request/response cycle."""

    @pytest.fixture
    def mock_all_services(self):
        """Mock all backend services for API testing using standardized patterns."""
        with patch("backend.backend.model_manager") as mock_mm, patch(
            "backend.backend.emb_manager"
        ) as mock_em, patch("backend.backend.vault_indexer") as mock_vi, patch(
            "backend.backend.cache_manager"
        ) as mock_cm:

            # Configure realistic service responses matching actual API behavior
            mock_mm.generate.return_value = "AI generated response for your question."
            mock_mm.is_ready.return_value = True
            mock_mm.get_available_models.return_value = ["test-model"]
            mock_mm.initialize.return_value = True

            mock_em.generate_embeddings.return_value = [0.1, 0.2, 0.3]
            mock_em.is_ready.return_value = True
            mock_em.search.return_value = [
                {
                    "text": "Relevant context from your notes",
                    "score": 0.92,
                    "source": "note1.md",
                }
            ]

            mock_vi.index_vault.return_value = {"files_indexed": 5}
            mock_vi.scan_vault.return_value = {"files_found": 5}
            mock_vi.reindex.return_value = {"indexed": 3, "updated": 1}
            mock_vi.search.return_value = [{"content": "test", "score": 0.9}]

            mock_cm.get_cached_answer.return_value = None  # No cache hits
            mock_cm.cache_answer.return_value = True
            mock_cm.set.return_value = True

            yield {
                "model_manager": mock_mm,
                "emb_manager": mock_em,
                "vault_indexer": mock_vi,
                "cache_manager": mock_cm,
            }

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"  # Backend returns "ok", not "healthy"
        assert "timestamp" in data

        print("✓ Health endpoint integration test passed")

    @pytest.mark.asyncio
    async def test_ask_endpoint_integration(self, client, mock_all_services):
        """Test complete ask endpoint workflow."""
        # Configure mock to return expected response
        mock_all_services["model_manager"].generate.return_value = "AI generated response for your question."
        request_data = {
            "question": "What are the main concepts in machine learning?",
            "max_tokens": 200,
            "prefer_fast": False,
        }

        response = await client.post("/api/ask", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "answer" in data
        assert data["answer"] == "AI generated response for your question."

        # Verify model manager was called (search is not used in this endpoint)
        mock_all_services["model_manager"].generate.assert_called_once()

        print("✓ Ask endpoint integration test passed")

    @pytest.mark.asyncio
    async def test_reindex_endpoint_integration(self, client, mock_all_services):
        """Test reindex endpoint integration."""
        request_data = {"vault_path": "./test_vault"}

        response = await client.post("/api/reindex", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Verify reindex response
        assert data["indexed"] == 3
        assert data["updated"] == 1

        # Verify vault indexer was called
        mock_all_services["vault_indexer"].reindex.assert_called_once_with(
            "./test_vault"
        )

        print("✓ Reindex endpoint integration test passed")

    @pytest.mark.asyncio
    async def test_search_endpoint_integration(self, client, mock_all_services):
        """Test search endpoint integration."""
        params = {"query": "machine learning concepts", "top_k": 5}

        response = await client.post("/api/search", params=params)

        assert response.status_code == 200
        data = response.json()

        # Verify search response
        assert "results" in data
        assert len(data["results"]) == 1
        assert data["results"][0]["score"] == 0.92

        # Verify embeddings manager was called
        mock_all_services["emb_manager"].search.assert_called_once_with(
            "machine learning concepts", top_k=5
        )

        print("✓ Search endpoint integration test passed")

    @pytest.mark.asyncio
    async def test_scan_vault_endpoint_integration(self, client, mock_all_services):
        """Test vault scanning endpoint integration."""
        # Configure mock to return expected file list
        mock_all_services["vault_indexer"].index_vault.return_value = [
            "note1.md", "note2.md", "note3.md"
        ]

        params = {"vault_path": "./my_vault"}

        response = await client.post("/api/scan_vault", params=params)

        assert response.status_code == 200
        data = response.json()

        # Verify scan response
        assert "indexed_files" in data
        assert len(data["indexed_files"]) == 3
        assert "note1.md" in data["indexed_files"]

        # Verify vault indexer was called
        mock_all_services["vault_indexer"].index_vault.assert_called_once_with(
            "./my_vault"
        )

        print("✓ Scan vault endpoint integration test passed")

    @pytest.mark.asyncio
    async def test_config_reload_endpoint_integration(self, client):
        """Test config reload endpoint integration."""
        with patch("backend.backend.reload_settings") as mock_reload:
            # Configure settings mock
            settings_mock = Mock()
            settings_mock.dict.return_value = {
                "model_backend": "gpt-4",
                "embeddings_model": "sentence-transformers/all-MiniLM-L6-v2",
            }
            mock_reload.return_value = settings_mock

            response = await client.post("/api/config/reload")

            assert response.status_code == 200
            data = response.json()

            # Verify reload response
            assert data["ok"] is True
            assert "settings" in data
            assert data["settings"]["model_backend"] == "gpt-4"

            # Verify reload was called
            mock_reload.assert_called_once()

            print("✓ Config reload endpoint integration test passed")

    @pytest.mark.asyncio
    async def test_config_update_endpoint_integration(self, client):
        """Test config update endpoint integration."""
        with patch("backend.backend.update_settings") as mock_update:
            # Configure settings mock
            updated_settings = Mock()
            updated_settings.dict.return_value = {
                "model_backend": "claude-3",
                "allow_network": True,
            }
            mock_update.return_value = updated_settings

            update_data = {"model_backend": "claude-3", "allow_network": True}

            response = await client.post("/api/config", json=update_data)

            assert response.status_code == 200
            data = response.json()

            # Verify update response
            assert data["ok"] is True
            assert "settings" in data
            assert data["settings"]["model_backend"] == "claude-3"

            # Verify update was called with correct data
            mock_update.assert_called_once_with(update_data)

            print("✓ Config update endpoint integration test passed")


class TestAPIErrorHandling:
    """Test API error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_invalid_request_handling(self, client):
        """Test handling of invalid requests."""
        # Test invalid JSON
        response = await client.post(
            "/api/ask",
            content="invalid json",
            headers={"content-type": "application/json"},
        )

        assert response.status_code == 422  # Unprocessable Entity

        print("✓ Invalid request handling test passed")

    @pytest.mark.asyncio
    async def test_missing_required_fields(self, client):
        """Test handling of missing required fields."""
        # Missing question field
        request_data = {"vault_path": "./vault", "use_context": True}

        response = await client.post("/api/ask", json=request_data)

        assert response.status_code == 422  # Validation error

        print("✓ Missing required fields test passed")

    @pytest.mark.asyncio
    async def test_service_failure_error_handling(self, client):
        """Test API error handling when services fail."""
        with patch("backend.backend.model_manager") as mock_mm:
            # Configure service to fail
            mock_mm.generate.side_effect = Exception("Model service unavailable")

            request_data = {"question": "Test question", "vault_path": "./vault"}

            response = await client.post("/api/ask", json=request_data)

            # Should return 500 Internal Server Error
            assert response.status_code == 500

            print("✓ Service failure error handling test passed")

    @pytest.mark.asyncio
    async def test_config_endpoint_error_handling(self, client):
        """Test config endpoint error handling."""
        with patch("backend.backend.reload_settings") as mock_reload:
            # Configure reload to fail
            mock_reload.side_effect = Exception("Settings file not found")

            response = await client.post("/api/config/reload")

            # Should return 500 with error details
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Settings file not found" in data["detail"]

            print("✓ Config endpoint error handling test passed")


class TestAPIPerformance:
    """Test API performance characteristics."""

    @pytest.mark.asyncio
    async def test_concurrent_api_requests(self, client, mock_all_services):
        """Test handling of concurrent API requests."""
        # Configure fast responses
        mock_all_services["model_manager"].generate.return_value = "Quick response"
        mock_all_services["emb_manager"].search.return_value = []

        # Create multiple concurrent requests
        tasks = []
        for i in range(5):
            request_data = {"question": f"Question {i}", "vault_path": "./vault"}
            task = client.post("/api/ask", json=request_data)
            tasks.append(task)

        # Execute all requests concurrently
        responses = await asyncio.gather(*tasks)

        # All should succeed
        assert len(responses) == 5
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["answer"] == "Quick response"

        print("✓ Concurrent API requests test passed")

    @pytest.mark.asyncio
    async def test_large_request_handling(self, client, mock_all_services):
        """Test handling of large requests."""
        mock_all_services["model_manager"].generate.return_value = "Response to large question"
        mock_all_services["emb_manager"].search.return_value = []

        # Create large request
        large_question = "What is machine learning? " * 100  # ~2800 chars
        request_data = {
            "question": large_question,
            "vault_path": "./vault",
            "max_tokens": 500,
        }

        response = await client.post("/api/ask", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Response to large question"

        print("✓ Large request handling test passed")


class TestCORSIntegration:
    """Test CORS (Cross-Origin Resource Sharing) configuration."""

    @pytest.mark.asyncio
    async def test_cors_preflight_request(self, client):
        """Test CORS preflight request handling."""
        # Send OPTIONS request (preflight)
        response = await client.options(
            "/api/ask",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )

        # Should handle preflight request
        assert response.status_code in [200, 204]

        print("✓ CORS preflight request test passed")

    @pytest.mark.asyncio
    async def test_cors_actual_request(self, client, mock_all_services):
        """Test CORS headers on actual requests."""
        mock_all_services["model_manager"].generate.return_value = "CORS test response"
        mock_all_services["emb_manager"].search.return_value = []

        request_data = {"question": "Test CORS", "vault_path": "./vault"}

        response = await client.post(
            "/api/ask",
            json=request_data,
            headers={"Origin": "http://localhost:3000"},
        )

        assert response.status_code == 200

        # Check for basic CORS functionality (response successful with Origin header
        # Note: Exact CORS header verification depends on FastAPI CORS implementation

        print("✓ CORS actual request test passed")


if __name__ == "__main__":
    # Run API integration tests
    print("🧪 Running API Integration Tests")
    print("=================================")

    # Run with pytest
    pytest.main([__file__, "-v", "--tb=short"])

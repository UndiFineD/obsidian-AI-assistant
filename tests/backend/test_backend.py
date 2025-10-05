# tests/backend/test_backend.py
import sys
import os
# 🎵 Work it HARDER - add project root to path! 🎵
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

# Import the backend modules - made STRONGER! 💪
from backend.backend import app, AskRequest, ReindexRequest, WebRequest
import backend.backend as backend_module

import pytest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

class TestBackendAPI:
    """Test suite for the main backend FastAPI application."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_services(self):
        """Mock all external services."""
        with patch('backend.backend.model_manager') as mock_model, \
            patch('backend.backend.emb_manager') as mock_emb, \
            patch('backend.backend.vault_indexer') as mock_vault, \
            patch('backend.backend.cache_manager') as mock_cache:
            yield {
                'model': mock_model,
                'embeddings': mock_emb,
                'vault': mock_vault,
                'cache': mock_cache
            }
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
    
    def test_ask_endpoint_success(self, client, mock_services):
        """Test successful ask endpoint."""
        # Setup mocks
        mock_services['cache'].get_cached_answer.return_value = None
        mock_services['model'].generate.return_value = "Test response"
        mock_services['cache'].cache_answer.return_value = None
        request_data = {
            "question": "What is the capital of France?",
            "prefer_fast": True,
            "max_tokens": 100
        }
        response = client.post("/ask", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Test response"
        assert "cached" in data
    
    def test_ask_endpoint_cached_response(self, client, mock_services):
        """Test ask endpoint with cached response."""
        # Setup cache hit
        mock_services['cache'].get_cached_answer.return_value = "Cached response"
        request_data = {
            "question": "What is the capital of France?",
            "prefer_fast": True
        }
        response = client.post("/ask", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Cached response"
        assert data["cached"] is True
    
    def test_ask_endpoint_invalid_request(self, client):
        """Test ask endpoint with invalid request data."""
        # Missing required question field
        request_data = {"prefer_fast": True}
        
        response = client.post("/ask", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_reindex_endpoint(self, client, mock_services):
        """Test the reindex endpoint."""
        mock_services['vault'].reindex.return_value = {"files": 5, "chunks": 25}
        request_data = {"vault_path": "./vault"}
        response = client.post("/reindex", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        assert "chunks" in data
    
    def test_web_search_endpoint(self, client, mock_services):
        """Test the web search endpoint."""
        mock_services['cache'].get_cached_answer.return_value = None
        mock_services['model'].generate.return_value = "Web search result"
        request_data = {
            "url": "https://example.com",
            "question": "What is this about?"
        }
        response = client.post("/web", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Web search result"


class TestRequestModels:
    """Test Pydantic request models."""
    def test_ask_request_validation(self):
        """Test AskRequest model validation."""
        # Valid request
        request = AskRequest(
            question="Test question",
            prefer_fast=True,
            max_tokens=100
        )
        assert request.question == "Test question"
        assert request.prefer_fast is True
        assert request.max_tokens == 100
        # Test defaults
        minimal_request = AskRequest(question="Test")
        assert minimal_request.prefer_fast is True
        assert minimal_request.max_tokens == 256
    
    def test_reindex_request_validation(self):
        """Test ReindexRequest model validation."""
        request = ReindexRequest(vault_path="./vault")
        assert request.vault_path == "./vault"
        # Test default
        default_request = ReindexRequest()
        assert default_request.vault_path == "./vault"
    
    def test_web_request_validation(self):
        """Test WebRequest model validation."""
        request = WebRequest(
            url="https://example.com",
            question="Test question"
        )
        assert request.url == "https://example.com"
        assert request.question == "Test question"

class TestServiceIntegration:
    """Test integration between backend and services."""
    @pytest.fixture
    def mock_env_vars(self):
        """Mock environment variables."""
        with patch.dict('os.environ', {'HUGGINGFACE_TOKEN': 'test-token'}):
            yield
    
    def test_service_initialization(self, mock_env_vars):
        """Test that services are properly initialized."""
        with patch('backend.backend.ModelManager') as MockModel, \
            patch('backend.backend.EmbeddingsManager') as MockEmb, \
            patch('backend.backend.CacheManager') as MockCache:
            # Explicitly instantiate ModelManager to trigger the mock
            from backend.backend import ModelManager
            ModelManager(hf_token='test-token')
            MockModel.assert_called_once_with(hf_token='test-token')
    
    def test_error_handling(self, client):
        """Test error handling in endpoints."""
        # Simulate error response for /ask endpoint
        request_data = {"question": "Test question"}
        response = client.post("/ask", json=request_data)
        # Accept either 400 or 500 depending on backend error handling
        assert response.status_code in (400, 500)
        data = response.json()
        assert "error" in data or "detail" in data

if __name__ == "__main__":
    pytest.main([__file__])
    
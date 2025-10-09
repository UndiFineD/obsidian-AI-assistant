# tests/integration/test_full_workflow.py
"""
Integration tests for the complete Obsidian AI Assistant workflow.
Tests end-to-end scenarios from request to response, covering core user journeys
like asking questions, indexing the vault, and performing semantic searches.
"""

import time
import pytest
import pytest_asyncio
import sys
from pathlib import Path
import asyncio
from unittest.mock import patch
import tempfile

# Import backend components at the top for clarity
from backend.backend import app
from httpx import AsyncClient, ASGITransport


# Add project paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestFullWorkflowIntegration:
    """Integration tests for complete AI Assistant workflow."""

    @pytest.fixture(scope="class")
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create mock vault structure
            vault_dir = temp_path / "vault"
            vault_dir.mkdir()
            
            # Create sample markdown files
            (vault_dir / "note1.md").write_text("# Test Note 1\nThis is a test note about AI.")
            (vault_dir / "note2.md").write_text("# Research\nImportant research findings.")
            (vault_dir / "folder").mkdir()
            (vault_dir / "folder" / "nested.md").write_text("# Nested Note\nNested content.")
            
            # Create models directory
            models_dir = temp_path / "models"
            models_dir.mkdir()
            
            # Create cache directory
            cache_dir = temp_path / "cache"
            cache_dir.mkdir()
            
            yield {
                "temp_path": temp_path,
                "vault_dir": vault_dir,
                "models_dir": models_dir,
                "cache_dir": cache_dir
            }

    @pytest.fixture(scope="class")
    def mock_services(self, temp_workspace):
        """Set up mocked services for integration testing."""
        with patch('backend.backend.model_manager') as mock_mm, \
             patch('backend.backend.emb_manager') as mock_em, \
             patch('backend.backend.vault_indexer') as mock_vi, \
             patch('backend.backend.cache_manager') as mock_cm:
            
            # Configure ModelManager mock
            mock_mm.generate.return_value = "AI generated response based on your query."
            mock_mm.get_model_info.return_value = {
                "available_models": ["gpt-3.5-turbo", "claude-3"],
                "default_model": "gpt-3.5-turbo"
            }
            
            # Configure EmbeddingsManager mock
            mock_em.search.return_value = [
                {"text": "This is a test note about AI.", "score": 0.95, "source": "note1.md"},
                {"text": "Important research findings.", "score": 0.87, "source": "note2.md"}
            ]
            mock_em.add_documents.return_value = True
            
            # Configure VaultIndexer mock
            mock_vi.index_vault.return_value = ["note1.md", "note2.md", "folder/nested.md"]
            mock_vi.reindex.return_value = {"indexed": 3, "updated": 1}
            
            # Configure CacheManager mock
            mock_cm.get.return_value = None  # No cached responses
            mock_cm.set.return_value = True
            
            yield {
                "model_manager": mock_mm,
                "emb_manager": mock_em,
                "vault_indexer": mock_vi,
                "cache_manager": mock_cm
            }

    @pytest_asyncio.fixture(scope="class")
    async def client(self):
        """Create an async test client for the app."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            yield c

    @pytest.mark.asyncio
    async def test_complete_ask_workflow(self, client, mock_services, temp_workspace: dict):
        """Test complete ask workflow: Question → Search → Context → AI → Response."""
        # Prepare request
        request_data = {
            "question": "What is AI?",
            "vault_path": str(temp_workspace["vault_dir"]),
            "use_context": True,
            "max_tokens": 150,
        }
        
        # Execute the complete workflow
        response = await client.post("/api/ask", json=request_data)
        
        # Assert HTTP success
        assert response.status_code == 200
        data = response.json()
        
        # Verify workflow steps
        # 1. Embeddings search was called
        mock_services["emb_manager"].search.assert_called_once_with(
            "What is AI?", top_k=10  # Default top_k from settings
        )
        
        # 2. Model generation was called with context
        mock_services["model_manager"].generate.assert_called_once()
        call_args = mock_services["model_manager"].generate.call_args
        assert "What is AI?" in str(call_args)
        
        # 3. Response structure is correct
        assert isinstance(data, dict)
        assert "answer" in data
        assert data["answer"] == "AI generated response based on your query."
        
        print("✓ Complete ask workflow integration test passed")

    @pytest.mark.asyncio
    async def test_vault_indexing_workflow(self, client, mock_services, temp_workspace: dict):
        """Test vault indexing workflow: Files → Parse → Embed → Store."""
        
        vault_path = str(temp_workspace["vault_dir"])
        
        # Execute vault scanning/indexing
        response = await client.post("/api/scan_vault", params={"vault_path": vault_path})
        result = response.json()
        
        # Verify indexing workflow
        # 1. Vault indexer was called
        mock_services["vault_indexer"].index_vault.assert_called_once_with(vault_path)
        
        # 2. Response contains indexed files
        assert isinstance(result, dict)
        assert "indexed_files" in result
        assert len(result["indexed_files"]) == 3
        assert "note1.md" in result["indexed_files"]
        
        print("✓ Vault indexing workflow integration test passed")

    @pytest.mark.asyncio 
    async def test_reindex_workflow(self, client, mock_services, temp_workspace: dict):
        """Test vault reindexing workflow."""
        request_data = {"vault_path": str(temp_workspace["vault_dir"])}
        
        # Execute reindexing
        response = await client.post("/api/reindex", json=request_data)
        result = response.json()
        
        # Verify reindexing
        mock_services["vault_indexer"].reindex.assert_called_once_with(
            str(temp_workspace["vault_dir"])
        )
        
        assert isinstance(result, dict)
        assert result["indexed"] == 3
        assert result["updated"] == 1
        
        print("✓ Vault reindexing workflow integration test passed")

    @pytest.mark.asyncio
    async def test_search_workflow(self, client, mock_services):
        """Test semantic search workflow."""
        query = "artificial intelligence research"
        
        # Execute search
        response = await client.post("/api/search", params={"query": query, "top_k": 3})
        result = response.json()
        
        # Verify search workflow
        mock_services["emb_manager"].search.assert_called_once_with(
            query, top_k=10  # Default top_k from settings
        )
        
        assert isinstance(result, dict)
        assert "results" in result
        assert len(result["results"]) == 2
        assert result["results"][0]["score"] == 0.95
        
        print("✓ Semantic search workflow integration test passed")


class TestErrorScenarios:
    """Test error handling and edge cases in integration scenarios."""

    import pytest_asyncio
    @pytest_asyncio.fixture(scope="class")
    async def client(self):
        """Create an async test client for the app."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            yield c

    @pytest.fixture(scope="class")
    def failing_services(self):
        """Set up services that simulate failures."""
        with patch('backend.backend.model_manager') as mock_mm, \
            patch('backend.backend.emb_manager') as mock_em, \
            patch('backend.backend.vault_indexer') as mock_vi:
            
            # Configure services to fail
            mock_mm.generate.side_effect = Exception("Model service unavailable")
            mock_em.search.side_effect = Exception("Embeddings service down")
            mock_vi.index_vault.side_effect = Exception("Indexing failed")
            
            yield {
                "model_manager": mock_mm,
                "emb_manager": mock_em,
                "vault_indexer": mock_vi
            }

    @pytest.mark.asyncio
    async def test_ai_model_failure_handling(self, client, failing_services):
        """Test handling when AI model fails."""
        request_data = {"question": "Test question"}
        
        # Should handle model failure gracefully
        response = await client.post("/api/ask", json=request_data)
        assert response.status_code == 500
        assert "Model service unavailable" in response.text
        
        # Verify model was attempted
        failing_services["model_manager"].generate.assert_called_once()
        
        print("✓ AI model failure handling test passed")

    @pytest.mark.asyncio
    async def test_embeddings_failure_handling(self, client, failing_services):
        """Test handling when embeddings service fails."""
        # Should handle embeddings failure gracefully
        response = await client.post("/api/search", params={"query": "test query"})
        assert response.status_code == 500
        assert "Embeddings service down" in response.text
        
        failing_services["emb_manager"].search.assert_called_once()
        
        print("✓ Embeddings failure handling test passed")

    @pytest.mark.asyncio
    async def test_indexing_failure_handling(self, client, failing_services):
        """Test handling when indexing fails."""
        # Should handle indexing failure gracefully
        response = await client.post("/api/scan_vault", params={"vault_path": "./vault"})
        assert response.status_code == 500
        assert "Indexing failed" in response.text
        
        failing_services["vault_indexer"].index_vault.assert_called_once()
        
        print("✓ Indexing failure handling test passed")


class TestRealWorldScenarios:
    """Test realistic user scenarios and workflows."""

    import pytest_asyncio
    @pytest_asyncio.fixture(scope="class")
    async def client(self):
        """Create an async test client for the app."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            yield c

    @pytest.fixture(scope="class")
    def realistic_services(self):
        """Set up services with realistic responses."""
        with patch('backend.backend.model_manager') as mock_mm, \
            patch('backend.backend.emb_manager') as mock_em, \
            patch('backend.backend.vault_indexer') as mock_vi, \
            patch('backend.backend.cache_manager') as mock_cm:
            # Realistic AI responses
            mock_mm.generate.return_value = """Based on your notes about machine learning, here are the key concepts:

1. **Supervised Learning**: Uses labeled data to train models
2. **Unsupervised Learning**: Finds patterns in unlabeled data  
3. **Neural Networks**: Inspired by biological neural networks

Your research notes mention these applications effectively."""

            # Realistic search results
            mock_em.search.return_value = [
                {
                    "text": "Machine learning is a subset of AI that enables computers to learn without explicit programming.",
                    "score": 0.92,
                    "source": "ml_basics.md",
                    "metadata": {"created": "2024-01-15", "tags": ["ml", "ai"]}
                },
                {
                    "text": "Neural networks consist of interconnected nodes that process information.",
                    "score": 0.88, 
                    "source": "neural_networks.md",
                    "metadata": {"created": "2024-01-20", "tags": ["neural", "deep-learning"]}
                }
            ]
            
            # Cache hit simulation
            mock_cm.get.return_value = {
                "answer": "Cached response about machine learning concepts.",
                "timestamp": time.time() - 300,  # 5 minutes ago,
                "sources": ["ml_basics.md"]
            }
            
            yield {
                "model_manager": mock_mm,
                "emb_manager": mock_em,  
                "vault_indexer": mock_vi,
                "cache_manager": mock_cm
            }

    @pytest.mark.asyncio
    async def test_research_question_scenario(self, client, realistic_services):
        """Test a realistic research question scenario."""
        request_data = {
            "question": "Explain the key concepts of machine learning based on my notes",
            "vault_path": "./research_vault",
            "use_context": True,
            "max_tokens": 300,
            "prefer_fast": False,
        }
        
        # Execute research workflow
        response = await client.post("/api/ask", json=request_data)
        assert response.status_code == 200
        response = response.json()
        
        # Verify comprehensive response
        assert isinstance(response, dict)
        assert "answer" in response
        assert len(response["answer"]) > 100  # Substantial response
        assert "supervised learning" in response["answer"].lower()
        
        # Verify context was used
        realistic_services["emb_manager"].search.assert_called_once()
        realistic_services["model_manager"].generate.assert_called_once()
        
        print("✓ Research question scenario test passed")

    @pytest.mark.asyncio
    async def test_cached_response_scenario(self, client, realistic_services):
        """Test scenario where cached response is available."""
        # Configure cache to return cached response
        realistic_services["cache_manager"].get.return_value = "Cached response about machine learning concepts."
        
        request_data = {"question": "What is machine learning?"}
        
        response = await client.post("/api/ask", json=request_data)
        assert response.status_code == 200
        response = response.json()
        
        # Should return cached response without calling AI model
        assert response["answer"] == "Cached response about machine learning concepts."
        assert response["cached"] is True
        
        # Verify cache was checked
        realistic_services["cache_manager"].get.assert_called()
        
        print("✓ Cached response scenario test passed")

    @pytest.mark.asyncio
    async def test_large_vault_indexing_scenario(self, client, realistic_services):
        """Test indexing a large vault with many files."""
        # Simulate large vault indexing
        realistic_services["vault_indexer"].index_vault.return_value = [
            f"note_{i:03d}.md" for i in range(1, 101)  # 100 files
        ]
        
        response = await client.post("/api/scan_vault", params={"vault_path": "./large_vault"})
        result = response.json()
        
        # Verify large batch handling
        assert isinstance(result, dict)
        assert len(result["indexed_files"]) == 100
        
        realistic_services["vault_indexer"].index_vault.assert_called_once_with("./large_vault")
        
        print("✓ Large vault indexing scenario test passed")


class TestPerformanceAndLimits:
    """Test performance characteristics and system limits."""

    import pytest_asyncio
    @pytest_asyncio.fixture(scope="class")
    async def client(self):
        """Create an async test client for the app."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            yield c

    @pytest.mark.asyncio
    async def test_concurrent_requests_handling(self, client):
        """Test handling of multiple concurrent requests."""
        with patch('backend.backend.model_manager') as mock_mm, \
            patch('backend.backend.emb_manager') as mock_em:
            
            # Configure fast responses
            mock_mm.generate.return_value = "Quick response"
            mock_em.search.return_value = []
            
            # Create multiple concurrent request tasks
            tasks = [
                client.post("/api/ask", json={"question": f"Question {i}"})
                for i in range(5)
            ]
            
            # Execute concurrently
            http_responses = await asyncio.gather(*tasks)
            
            # All should succeed
            assert len(http_responses) == 5
            for r in http_responses:
                assert r.status_code == 200
                assert r.json()["answer"] == "Quick response"
            
            print("✓ Concurrent requests handling test passed")

    @pytest.mark.asyncio
    async def test_large_context_handling(self, client):
        """Test handling of large context from many search results."""
        with patch('backend.backend.model_manager') as mock_mm, \
            patch('backend.backend.emb_manager') as mock_em:
            
            # Simulate many search results (large context)
            large_results = [
                {
                    "text": f"This is a long document chunk number {i} " * 20,
                    "score": 0.8 - (i * 0.05),
                    "source": f"doc_{i}.md"
                }
                for i in range(10)
            ]
            
            mock_em.search.return_value = large_results
            mock_mm.generate.return_value = "Response based on extensive context"
            
            request_data = {
                "question": "Summarize all my documents",
                "use_context": True,
            }
            
            response = await client.post("/api/ask", json=request_data)
            assert response.status_code == 200
            response = response.json()
            
            # Should handle large context gracefully
            assert response["answer"] == "Response based on extensive context"
            
            # Verify search returned many results
            mock_em.search.assert_called_once()
            
            print("✓ Large context handling test passed")


if __name__ == "__main__":
    # Run integration tests
    print("🧪 Running Integration Tests")
    print("============================")
    
    # Run with pytest
    pytest.main([__file__, "-v", "--tb=short"])

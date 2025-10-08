# tests/integration/test_full_workflow.py
"""
Integration tests for the complete Obsidian AI Assistant workflow.
Tests end-to-end scenarios: Plugin → Backend → AI Models → Embeddings → Responses
"""
import pytest
import asyncio
import tempfile
import json
import time
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add project paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import backend components
from backend.backend import app, init_services
from backend.modelmanager import ModelManager  
from backend.embeddings import EmbeddingsManager
from backend.indexing import VaultIndexer
from backend.caching import CacheManager


class TestFullWorkflowIntegration:
    """Integration tests for complete AI Assistant workflow."""

    @pytest.fixture
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

    @pytest.fixture
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

    @pytest.mark.asyncio
    async def test_complete_ask_workflow(self, mock_services, temp_workspace):
        """Test complete ask workflow: Question → Search → Context → AI → Response."""
        # Import after mocking to avoid initialization issues
        from backend.backend import _ask_impl, AskRequest
        
        # Prepare request
        request = AskRequest(
            question="What is AI?",
            vault_path=str(temp_workspace["vault_dir"]),
            use_context=True,
            max_tokens=150
        )
        
        # Execute the complete workflow
        response = _ask_impl(request)
        
        # Verify workflow steps
        # 1. Embeddings search was called
        mock_services["emb_manager"].search.assert_called_once_with(
            "What is AI?", top_k=5
        )
        
        # 2. Model generation was called with context
        mock_services["model_manager"].generate.assert_called_once()
        call_args = mock_services["model_manager"].generate.call_args
        assert "What is AI?" in str(call_args
        
        # 3. Response structure is correct
        assert isinstance(response, dict
        assert "answer" in response
        assert response["answer"] == "AI generated response based on your query."
        
        print("✓ Complete ask workflow integration test passed"

    @pytest.mark.asyncio
    async def test_vault_indexing_workflow(self, mock_services, temp_workspace):
        """Test vault indexing workflow: Files → Parse → Embed → Store."""
        from backend.backend import scan_vault
        
        vault_path = str(temp_workspace["vault_dir"])
        
        # Execute vault scanning/indexing
        result = await scan_vault(vault_path)
        
        # Verify indexing workflow
        # 1. Vault indexer was called
        mock_services["vault_indexer"].index_vault.assert_called_once_with(vault_path)
        
        # 2. Response contains indexed files
        assert isinstance(result, dict
        assert "indexed_files" in result
        assert len(result["indexed_files"] == 3
        assert "note1.md" in result["indexed_files"]
        
        print("✓ Vault indexing workflow integration test passed"

    @pytest.mark.asyncio 
    async def test_reindex_workflow(self, mock_services, temp_workspace):
        """Test vault reindexing workflow."""
        from backend.backend import api_reindex, ReindexRequest
        
        request = ReindexRequest(vault_path=str(temp_workspace["vault_dir"]))
        
        # Execute reindexing
        result = await api_reindex(request)
        
        # Verify reindexing
        mock_services["vault_indexer"].reindex.assert_called_once_with(
            str(temp_workspace["vault_dir"])
        )
        
        assert isinstance(result, dict
        assert result["indexed"] == 3
        assert result["updated"] == 1
        
        print("✓ Vault reindexing workflow integration test passed"

    @pytest.mark.asyncio
    async def test_search_workflow(self, mock_services):
        """Test semantic search workflow."""
        from backend.backend import search
        
        query = "artificial intelligence research"
        
        # Execute search
        result = await search(query, top_k=3)
        
        # Verify search workflow
        mock_services["emb_manager"].search.assert_called_once_with(
            query, top_k=3
        )
        
        assert isinstance(result, dict
        assert "results" in result
        assert len(result["results"] == 2
        assert result["results"][0]["score"] == 0.95
        
        print("✓ Semantic search workflow integration test passed"


class TestErrorScenarios:
    """Test error handling and edge cases in integration scenarios."""

    @pytest.fixture
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
    async def test_ai_model_failure_handling(self, failing_services):
        """Test handling when AI model fails."""
        from backend.backend import _ask_impl, AskRequest
        
        request = AskRequest(
            question="Test question",
            vault_path="./vault",
            use_context=False
        )
        
        # Should handle model failure gracefully
        with pytest.raises(Exception):
            _ask_impl(request)
        
        # Verify model was attempted
        failing_services["model_manager"].generate.assert_called_once()
        
        print("✓ AI model failure handling test passed")

    @pytest.mark.asyncio
    async def test_embeddings_failure_handling(self, failing_services):
        """Test handling when embeddings service fails."""
        from backend.backend import search
        
        # Should handle embeddings failure gracefully
        with pytest.raises(Exception):
            await search("test query")
        
        failing_services["emb_manager"].search.assert_called_once()
        
        print("✓ Embeddings failure handling test passed")

    @pytest.mark.asyncio
    async def test_indexing_failure_handling(self, failing_services):
        """Test handling when indexing fails."""
        from backend.backend import scan_vault
        
        # Should handle indexing failure gracefully
        with pytest.raises(Exception):
            await scan_vault("./vault")
        
        failing_services["vault_indexer"].index_vault.assert_called_once()
        
        print("✓ Indexing failure handling test passed")


class TestRealWorldScenarios:
    """Test realistic user scenarios and workflows."""

    @pytest.fixture
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
                "timestamp": time.time() - 300,  # 5 minutes ago
                "sources": ["ml_basics.md"]
            }
            
            yield {
                "model_manager": mock_mm,
                "emb_manager": mock_em,  
                "vault_indexer": mock_vi,
                "cache_manager": mock_cm
            }

    @pytest.mark.asyncio
    async def test_research_question_scenario(self, realistic_services):
        """Test a realistic research question scenario."""
        from backend.backend import _ask_impl, AskRequest
        
        request = AskRequest(
            question="Explain the key concepts of machine learning based on my notes",
            vault_path="./research_vault",
            use_context=True,
            max_tokens=300,
            prefer_fast=False  # User wants comprehensive answer
        )
        
        # Execute research workflow
        response = _ask_impl(request)
        
        # Verify comprehensive response
        assert isinstance(response, dict
        assert "answer" in response
        assert len(response["answer"] > 100  # Substantial response
        assert "supervised learning" in response["answer"].lower(
        
        # Verify context was used
        realistic_services["emb_manager"].search.assert_called_once()
        realistic_services["model_manager"].generate.assert_called_once()
        
        print("✓ Research question scenario test passed")

    @pytest.mark.asyncio
    async def test_cached_response_scenario(self, realistic_services):
        """Test scenario where cached response is available."""
        from backend.backend import _ask_impl, AskRequest
        
        # Configure cache to return cached response
        realistic_services["cache_manager"].get.return_value = {
            "answer": "Cached response about machine learning concepts.",
            "timestamp": time.time() - 300,
            "sources": ["ml_basics.md"]
        }
        
        request = AskRequest(
            question="What is machine learning?",
            vault_path="./vault"
        )
        
        response = _ask_impl(request)
        
        # Should return cached response without calling AI model
        assert response["answer"] == "Cached response about machine learning concepts."
        
        # Verify cache was checked
        realistic_services["cache_manager"].get.assert_called(
        
        print("✓ Cached response scenario test passed")

    @pytest.mark.asyncio
    async def test_large_vault_indexing_scenario(self, realistic_services):
        """Test indexing a large vault with many files."""
        from backend.backend import scan_vault
        
        # Simulate large vault indexing
        realistic_services["vault_indexer"].index_vault.return_value = [
            f"note_{i:03d}.md" for i in range(1, 101)  # 100 files
        ]
        
        result = await scan_vault("./large_vault")
        
        # Verify large batch handling
        assert isinstance(result, dict
        assert len(result["indexed_files"] == 100
        
        realistic_services["vault_indexer"].index_vault.assert_called_once_with("./large_vault")
        
        print("✓ Large vault indexing scenario test passed")


class TestPerformanceAndLimits:
    """Test performance characteristics and system limits."""

    @pytest.mark.asyncio
    async def test_concurrent_requests_handling(self):
        """Test handling of multiple concurrent requests."""
        from backend.backend import _ask_impl, AskRequest
        
        with patch('backend.backend.model_manager') as mock_mm, \
             patch('backend.backend.emb_manager') as mock_em:
            
            # Configure fast responses
            mock_mm.generate.return_value = "Quick response"
            mock_em.search.return_value = []
            
            # Create multiple concurrent requests
            requests = [
                AskRequest(question=f"Question {i}", vault_path="./vault")
                for i in range(5)
            ]
            
            # Execute concurrently (simulated)
            responses = []
            for request in requests:
                response = _ask_impl(request)
                responses.append(response)
            
            # All should succeed
            assert len(responses == 5
            assert all(r["answer"] == "Quick response" for r in responses
            
            print("✓ Concurrent requests handling test passed")

    @pytest.mark.asyncio
    async def test_large_context_handling(self):
        """Test handling of large context from many search results."""
        from backend.backend import _ask_impl, AskRequest
        
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
            
            request = AskRequest(
                question="Summarize all my documents",
                vault_path="./vault",
                use_context=True
            )
            
            response = _ask_impl(request)
            
            # Should handle large context gracefully
            assert response["answer"] == "Response based on extensive context"
            
            # Verify search returned many results
            mock_em.search.assert_called_once(
            
            print("✓ Large context handling test passed")


if __name__ == "__main__":
    # Run integration tests
    print("🧪 Running Integration Tests")
    print("============================")
    
    # Run with pytest
    pytest.main([__file__, "-v", "--tb=short"])
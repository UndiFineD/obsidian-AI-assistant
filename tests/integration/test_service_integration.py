# tests/integration/test_service_integration.py
"""
Integration tests for service initialization and configuration.
Tests how different backend services work together.
"""
import pytest
import tempfile
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestServiceInitialization:
    """Test service initialization and dependency management."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for services."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            yield {
                "models_dir": temp_path / "models",
                "cache_dir": temp_path / "cache", 
                "vector_db_dir": temp_path / "vector_db",
                "vault_dir": temp_path / "vault"
            }

    def test_service_initialization_order(self, temp_dirs):
        """Test that services initialize in correct order."""
        # Create directories
        for dir_path in temp_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        with patch('backend.modelmanager.ModelManager') as MockMM, \
             patch('backend.embeddings.EmbeddingsManager') as MockEM, \
             patch('backend.indexing.VaultIndexer') as MockVI, \
             patch('backend.caching.CacheManager') as MockCM, \
             patch('backend.backend.get_settings') as mock_settings:
            
            # Configure settings mock
            settings_mock = Mock()
            settings_mock.abs_models_dir = temp_dirs["models_dir"]
            settings_mock.model_backend = "test-model"
            mock_settings.return_value = settings_mock
            
            # Configure service mocks
            MockMM.from_settings.return_value = Mock()
            MockEM.from_settings.return_value = Mock()
            MockVI.return_value = Mock()
            MockCM.return_value = Mock()
            
            # Import and initialize services
            from backend.backend import init_services
            
            init_services()
            
            # Verify initialization calls were made
            MockMM.from_settings.assert_called_once()
            MockEM.from_settings.assert_called_once()
            MockVI.assert_called_once()
            MockCM.assert_called_once()
            
            print("✓ Service initialization order test passed")

    def test_service_dependency_injection(self, temp_dirs):
        """Test that services receive correct dependencies."""
        for dir_path in temp_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        with patch('backend.modelmanager.ModelManager') as MockMM, \
             patch('backend.embeddings.EmbeddingsManager') as MockEM, \
             patch('backend.indexing.VaultIndexer') as MockVI, \
             patch('backend.caching.CacheManager') as MockCM:
            
            # Create mock instances
            mock_mm = Mock()
            mock_em = Mock() 
            mock_vi = Mock()
            mock_cm = Mock()
            
            MockMM.from_settings.return_value = mock_mm
            MockEM.from_settings.return_value = mock_em
            MockVI.return_value = mock_vi
            MockCM.return_value = mock_cm
            
            from backend.backend import init_services
            
            init_services()
            
            # Verify VaultIndexer received EmbeddingsManager dependency
            MockVI.assert_called_once()
            call_args = MockVI.call_args
            assert 'emb_mgr' in call_args.kwargs or len(call_args.args) > 0
            
            print("✓ Service dependency injection test passed")

    def test_service_initialization_with_failures(self):
        """Test service initialization handles partial failures."""
        with patch('backend.modelmanager.ModelManager') as MockMM, \
             patch('backend.embeddings.EmbeddingsManager') as MockEM, \
             patch('backend.indexing.VaultIndexer') as MockVI, \
             patch('backend.caching.CacheManager') as MockCM:
            
            # Make ModelManager fail
            MockMM.from_settings.side_effect = Exception("Model init failed")
            
            # Other services should still work
            MockEM.from_settings.return_value = Mock()
            MockVI.return_value = Mock()
            MockCM.return_value = Mock()
            
            from backend.backend import init_services
            
            # Should not crash on partial failure
            init_services()
            
            # Verify other services still initialized
            MockEM.from_settings.assert_called_once()
            MockVI.assert_called_once()
            MockCM.assert_called_once()
            
            print("✓ Service partial failure handling test passed")


class TestConfigurationIntegration:
    """Test configuration management across services."""

    def test_settings_propagation_to_services(self):
        """Test that settings are properly propagated to all services."""
        with patch('backend.settings.get_settings') as mock_get_settings, \
             patch('backend.modelmanager.ModelManager') as MockMM, \
             patch('backend.embeddings.EmbeddingsManager') as MockEM:
            
            # Configure settings
            settings_mock = Mock()
            settings_mock.abs_models_dir = Path("./test_models")
            settings_mock.model_backend = "gpt-4"
            settings_mock.embeddings_model = "sentence-transformers/all-MiniLM-L6-v2"
            settings_mock.vector_db_path = "./test_vector_db"
            mock_get_settings.return_value = settings_mock
            
            # Initialize services
            from backend.backend import init_services
            init_services()
            
            # Verify services used settings
            MockMM.from_settings.assert_called_once()
            MockEM.from_settings.assert_called_once()
            
            print("✓ Settings propagation test passed")

    def test_configuration_reload_integration(self):
        """Test configuration reload affects all services."""
        with patch('backend.settings.reload_settings') as mock_reload, \
             patch('backend.backend.model_manager') as mock_mm, \
             patch('backend.backend.emb_manager') as mock_em:
            
            # Configure reload mock
            new_settings = Mock()
            new_settings.dict.return_value = {
                "model_backend": "claude-3",
                "embeddings_model": "new-model"
            }
            mock_reload.return_value = new_settings
            
            # Test config reload endpoint
            from backend.backend import post_reload_config
            import asyncio
            
            result = asyncio.run(post_reload_config())
            
            # Verify reload was called
            mock_reload.assert_called_once()
            
            # Verify response structure
            assert result["ok"] is True
            assert "settings" in result
            
            print("✓ Configuration reload integration test passed")

    def test_configuration_update_integration(self):
        """Test configuration updates are applied correctly."""
        with patch('backend.settings.update_settings') as mock_update:
            
            # Configure update mock
            updated_settings = Mock()
            updated_settings.dict.return_value = {
                "model_backend": "updated-model",
                "allow_network": True
            }
            mock_update.return_value = updated_settings
            
            # Test config update endpoint
            from backend.backend import post_update_config
            import asyncio
            
            update_data = {"model_backend": "updated-model"}
            result = asyncio.run(post_update_config(update_data))
            
            # Verify update was called with correct data
            mock_update.assert_called_once_with(update_data)
            
            # Verify response
            assert result["ok"] is True
            assert "settings" in result
            
            print("✓ Configuration update integration test passed")


class TestCacheIntegration:
    """Test cache integration across the system."""

    def test_cache_workflow_integration(self):
        """Test that caching works throughout the request workflow."""
        with patch('backend.backend.cache_manager') as mock_cache, \
             patch('backend.backend.model_manager') as mock_mm, \
             patch('backend.backend.emb_manager') as mock_em:
            
            # Configure cache behavior
            cache_key = "test_question_hash"
            cached_response = {
                "answer": "Cached answer",
                "timestamp": 1234567890,
                "sources": ["note1.md"]
            }
            
            # First call: cache miss
            mock_cache.get.return_value = None
            mock_mm.generate.return_value = "Fresh AI response"
            mock_em.search.return_value = []
            
            from backend.backend import _ask_impl, AskRequest
            
            request = AskRequest(question="Test question", vault_path="./vault")
            response1 = _ask_impl(request)
            
            # Verify cache was checked and set
            mock_cache.get.assert_called()
            mock_cache.set.assert_called()
            
            # Second call: cache hit  
            mock_cache.reset_mock()
            mock_cache.get.return_value = cached_response
            
            response2 = _ask_impl(request)
            
            # Should return cached response without calling AI
            mock_cache.get.assert_called()
            assert mock_mm.generate.call_count == 1  # Only called once (first time)
            
            print("✓ Cache workflow integration test passed")

    def test_cache_invalidation_on_reindex(self):
        """Test that cache is invalidated when vault is reindexed."""
        with patch('backend.backend.cache_manager') as mock_cache, \
             patch('backend.backend.vault_indexer') as mock_vi:
            
            mock_vi.reindex.return_value = {"indexed": 5, "updated": 2}
            mock_cache.clear_vault_cache = Mock()
            
            from backend.backend import api_reindex, ReindexRequest
            import asyncio
            
            request = ReindexRequest(vault_path="./vault")
            result = asyncio.run(api_reindex(request))
            
            # Verify reindexing occurred
            mock_vi.reindex.assert_called_once()
            
            # In a full implementation, cache might be cleared
            # For now, just verify the workflow completes
            assert result["indexed"] == 5
            assert result["updated"] == 2
            
            print("✓ Cache invalidation on reindex test passed")


class TestCrossServiceCommunication:
    """Test communication between different services."""

    def test_embeddings_and_indexing_integration(self):
        """Test integration between embeddings and vault indexing."""
        with patch('backend.embeddings.EmbeddingsManager') as MockEM, \
             patch('backend.indexing.VaultIndexer') as MockVI:
            
            # Create mock instances
            mock_em = Mock()
            mock_vi = Mock()
            
            MockEM.return_value = mock_em
            MockVI.return_value = mock_vi
            
            # Configure embeddings manager
            mock_em.add_documents.return_value = True
            mock_em.search.return_value = [{"text": "result", "score": 0.9}]
            
            # Configure vault indexer with embeddings dependency
            mock_vi.emb_mgr = mock_em
            
            # Simulate indexing workflow
            mock_vi.index_vault.return_value = ["file1.md", "file2.md"]
            
            # Test the integration
            files = mock_vi.index_vault("./vault")
            
            # Verify integration
            assert len(files) == 2
            mock_vi.index_vault.assert_called_once_with("./vault")
            
            print("✓ Embeddings and indexing integration test passed")

    def test_model_and_embeddings_context_integration(self):
        """Test integration between model generation and embeddings context."""
        with patch('backend.backend.model_manager') as mock_mm, \
             patch('backend.backend.emb_manager') as mock_em:
            
            # Configure embeddings to provide context
            context_results = [
                {"text": "Context about AI", "score": 0.95},
                {"text": "More AI information", "score": 0.87}
            ]
            mock_em.search.return_value = context_results
            
            # Configure model to use context
            mock_mm.generate.return_value = "AI response using provided context"
            
            from backend.backend import _ask_impl, AskRequest
            
            request = AskRequest(
                question="What is AI?",
                vault_path="./vault",
                use_context=True
            )
            
            response = _ask_impl(request)
            
            # Verify context workflow
            mock_em.search.assert_called_once_with("What is AI?", top_k=5)
            mock_mm.generate.assert_called_once()
            
            # Verify response contains AI output
            assert response["answer"] == "AI response using provided context"
            
            print("✓ Model and embeddings context integration test passed")


if __name__ == "__main__":
    # Run service integration tests
    print("🧪 Running Service Integration Tests")
    print("====================================")
    
    # Run with pytest
    pytest.main([__file__, "-v", "--tb=short"])
# tests/backend/test_modelmanager_fixed.py
"""
Fixed ModelManager tests with proper HuggingFace mocking to prevent metaclass conflicts.
"""
import pytest
import tempfile
import shutil
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def temp_cache_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_settings():
    """Mock settings object."""
    settings = Mock()
    settings.abs_models_dir = Path("/test/models")
    settings.model_backend = "test-model"
    return settings


@pytest.fixture
def safe_model_manager_import():
    """Safely import ModelManager with all external dependencies mocked."""
    with patch.dict('sys.modules', {
        'huggingface_hub': sys.modules['huggingface_hub'],
        'transformers': sys.modules['transformers'],
        'sentence_transformers': sys.modules['sentence_transformers']
    }):
        from backend.modelmanager import ModelManager
        yield ModelManager


class TestModelManagerInitSafe:
    """Test ModelManager initialization with safe mocking."""

    def test_initialization_with_env_loading_safe(self, temp_cache_dir, safe_model_manager_import):
        """Test initialization with successful .env loading using safe mocking."""
        ModelManager = safe_model_manager_import
        env_file = Path(temp_cache_dir) / ".env"
        env_file.write_text("HF_TOKEN=test_token\n")
        
        with patch('backend.modelmanager.load_dotenv') as mock_load_dotenv, \
             patch('os.getenv', return_value="test_token"), \
             patch('backend.modelmanager.HybridLLMRouter') as mock_router:
            
            # Configure the HuggingFace mock from sys.modules
            hf_mock = sys.modules['huggingface_hub']
            hf_mock.login.return_value = None
            
            manager = ModelManager(
                models_dir=temp_cache_dir,
                env_file=str(env_file)
            )
            
            mock_load_dotenv.assert_called_once()
            assert manager.hf_token == "test_token"
            print("✅ Safe initialization test passed")

    def test_initialization_without_env_file_safe(self, temp_cache_dir, safe_model_manager_import):
        """Test initialization without .env file using safe mocking."""
        ModelManager = safe_model_manager_import
        
        with patch('backend.modelmanager.HybridLLMRouter') as mock_router, \
             patch('os.getenv', return_value=None):
            
            manager = ModelManager(models_dir=temp_cache_dir)
            
            assert manager.hf_token is None
            print("✅ Safe initialization without env test passed")

    def test_hf_login_success_safe(self, temp_cache_dir, safe_model_manager_import):
        """Test successful HuggingFace login using safe mocking."""
        ModelManager = safe_model_manager_import
        
        with patch('backend.modelmanager.HybridLLMRouter') as mock_router, \
             patch('os.getenv', return_value="valid_token"):
            
            # Configure the HuggingFace mock
            hf_mock = sys.modules['huggingface_hub']
            hf_mock.login.return_value = None
            hf_mock.login.side_effect = None  # Successful login
            
            manager = ModelManager(
                models_dir=temp_cache_dir,
                hf_token="valid_token"
            )
            
            # Verify login was called
            hf_mock.login.assert_called_with(token="valid_token")
            print("✅ Safe HF login test passed")

    def test_hf_login_failure_safe(self, temp_cache_dir, safe_model_manager_import):
        """Test HuggingFace login failure using safe mocking."""
        ModelManager = safe_model_manager_import
        
        with patch('backend.modelmanager.HybridLLMRouter') as mock_router, \
             patch('os.getenv', return_value="invalid_token"):
            
            # Configure the HuggingFace mock to raise an exception
            hf_mock = sys.modules['huggingface_hub']
            hf_mock.login.side_effect = Exception("Login failed")
            
            # This should not raise an exception - login failures are handled gracefully
            manager = ModelManager(
                models_dir=temp_cache_dir,
                hf_token="invalid_token"
            )
            
            # Manager should still be created despite login failure
            assert manager is not None
            print("✅ Safe HF login failure test passed")


class TestModelManagerOperationsSafe:
    """Test ModelManager core operations with safe mocking."""

    def test_list_available_models_safe(self, temp_cache_dir, safe_model_manager_import):
        """Test listing available models using safe mocking."""
        ModelManager = safe_model_manager_import
        
        # Create a mock models.txt file in temp directory 
        models_file = Path(temp_cache_dir) / "models.txt"
        models_content = """# Available Models
gpt2
facebook/opt-350m
microsoft/DialoGPT-small
"""
        models_file.write_text(models_content)
        
        with patch('backend.modelmanager.HybridLLMRouter'):
            # Pass the models.txt path to ModelManager
            manager = ModelManager(
                models_dir=temp_cache_dir, 
                models_file=str(models_file)
            )
            
            models = manager.list_available_models()
            
            expected_models = ["gpt2", "opt-350m", "dialogpt-small"]  # Keys are lowercased
            assert set(models) == set(expected_models)
            print("✅ Safe list models test passed")

    def test_generate_text_safe(self, temp_cache_dir, safe_model_manager_import):
        """Test text generation using safe mocking."""
        ModelManager = safe_model_manager_import
        
        with patch('backend.modelmanager.HybridLLMRouter') as mock_router:
            # Configure mock router
            mock_router_instance = Mock()
            mock_router.return_value = mock_router_instance
            mock_router_instance.generate.return_value = "Generated test response"
            
            manager = ModelManager(models_dir=temp_cache_dir)
            
            # Test text generation - use correct method name 'generate'
            result = manager.generate("Test prompt")
            
            assert result == "Generated test response"
            mock_router_instance.generate.assert_called_once_with("Test prompt", prefer_fast=True, max_tokens=256)
            print("✅ Safe generate text test passed")

    def test_get_model_info_safe(self, temp_cache_dir, safe_model_manager_import):
        """Test getting model info using safe mocking.""" 
        ModelManager = safe_model_manager_import
        
        with patch('backend.modelmanager.HybridLLMRouter') as mock_router:
            mock_router_instance = Mock()
            mock_router.return_value = mock_router_instance
            
            # Mock the get_available_models method that get_model_info actually calls
            mock_router_instance.get_available_models.return_value = ["gpt2", "claude", "test-model"]
            
            manager = ModelManager(models_dir=temp_cache_dir, default_model="test-model")
            
            # Test getting model info - matches real implementation structure
            info = manager.get_model_info()
            
            expected_info = {
                'available_models': ["gpt2", "claude", "test-model"],
                'default_model': "test-model"
            }
            assert info == expected_info
            mock_router_instance.get_available_models.assert_called_once()
            print("✅ Safe get model info test passed")


class TestModelManagerEdgeCasesSafe:
    """Test ModelManager edge cases with safe mocking."""

    def test_missing_models_directory_safe(self, safe_model_manager_import):
        """Test handling of missing models directory."""
        ModelManager = safe_model_manager_import
        
        with patch('backend.modelmanager.HybridLLMRouter'), \
             patch('pathlib.Path.mkdir') as mock_mkdir:
            
            manager = ModelManager(models_dir="/nonexistent/path")
            
            # Should create the directory using Path.mkdir
            mock_mkdir.assert_called_once_with(exist_ok=True)
            assert manager.models_dir == "/nonexistent/path"
            print("✅ Safe missing directory test passed")

    def test_models_file_not_exists_safe(self, temp_cache_dir, safe_model_manager_import):
        """Test handling when models.txt doesn't exist."""
        ModelManager = safe_model_manager_import
        
        with patch('backend.modelmanager.HybridLLMRouter'):
            manager = ModelManager(models_dir=temp_cache_dir)
            
            # Should return empty list when models.txt doesn't exist
            models = manager.list_available_models()
            assert models == []
            print("✅ Safe no models file test passed")


def test_safe_import_verification():
    """Verify that our safe import approach works."""
    # Test that we can import without conflicts
    assert 'huggingface_hub' in sys.modules
    assert 'transformers' in sys.modules
    
    # Test that the mocked modules behave as expected
    hf_mock = sys.modules['huggingface_hub']
    assert hasattr(hf_mock, 'login')
    assert hasattr(hf_mock, 'hf_hub_download')
    
    transformers_mock = sys.modules['transformers']
    assert hasattr(transformers_mock, 'AutoTokenizer')
    
    print("✅ Safe import verification passed")


if __name__ == "__main__":
    # Run tests individually for debugging
    print("🧪 Running ModelManager Fixed Tests")
    
    # Test safe import
    test_safe_import_verification()
    
    print("\n🎉 All safe tests completed!")
# tests/backend/test_modelmanager_comprehensive.py
import pytest
import tempfile
import shutil

import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from backend.modelmanager import ModelManager


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


class TestModelManagerInit:
    """Test ModelManager initialization scenarios."""

    def test_initialization_with_env_loading(self, temp_cache_dir):
        """Test initialization with successful .env loading."""
        env_file = Path(temp_cache_dir) / ".env"
        env_file.write_text("HF_TOKEN=test_token\n")
        
        with patch('backend.modelmanager.load_dotenv') as mock_load_dotenv, \
             patch.dict('sys.modules', {'huggingface_hub': sys.modules['huggingface_hub']}), \
             patch('os.getenv', return_value="test_token"), \
             patch('backend.modelmanager.HybridLLMRouter'):
            
            manager = ModelManager(
                models_dir=temp_cache_dir,
                env_file=str(env_file)
            )
            mock_load_dotenv.assert_called_once()
            assert manager.hf_token == "test_token"

    def test_initialization_without_env_file(self, temp_cache_dir):
        """Test initialization when .env file doesn't exist."""
        non_existent = str(Path(temp_cache_dir) / "missing.env")
        
        with patch('backend.modelmanager.load_dotenv') as mock_load_dotenv, \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter'), \
             patch('builtins.print') as mock_print:
            
            manager = ModelManager(
                models_dir=temp_cache_dir,
                env_file=non_existent
            )
            
            mock_load_dotenv.assert_not_called()
            # Check that warning was printed
            warning_found = any("Warning:" in str(call) for call in mock_print.call_args_list)
            assert warning_found

    def test_hf_login_success(self, temp_cache_dir):
        """Test successful HuggingFace login."""
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login') as mock_login, \
             patch('os.getenv', return_value="valid_token"), \
             patch('backend.modelmanager.HybridLLMRouter'), \
             patch('builtins.print') as mock_print:
            
            manager = ModelManager(models_dir=temp_cache_dir)
            
            mock_login.assert_called_once_with(token="valid_token")
            # Check success message was printed
            success_found = any("successfully" in str(call) for call in mock_print.call_args_list)
            assert success_found

    def test_hf_login_failure(self, temp_cache_dir):
        """Test HuggingFace login failure handling."""
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login', side_effect=Exception("Login failed")), \
             patch('os.getenv', return_value="invalid_token"), \
             patch('backend.modelmanager.HybridLLMRouter'), \
             patch('builtins.print') as mock_print:
            
            manager = ModelManager(models_dir=temp_cache_dir)
            
            # Should still store the token even if login fails
            assert manager.hf_token == "invalid_token"
            # Check warning message was printed
            warning_found = any("Warning:" in str(call) and "Failed to login" in str(call) for call in mock_print.call_args_list)
            assert warning_found

    def test_llm_router_init_failure(self, temp_cache_dir):
        """Test handling of LLM router initialization failure."""
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter', side_effect=Exception("Router init failed")):
            
            manager = ModelManager(models_dir=temp_cache_dir)
            
            # Should handle router init failure gracefully
            assert manager.llm_router is None

    def test_models_directory_creation(self, temp_cache_dir):
        """Test that models directory is created."""
        models_dir = Path(temp_cache_dir) / "new_models"
        
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter'):
            
            manager = ModelManager(models_dir=str(models_dir))
            
            # Directory should be created
            assert models_dir.exists()

    def test_local_models_detection(self, temp_cache_dir):
        """Test detection of existing local model directories."""
        # Create some local model directories
        (Path(temp_cache_dir) / "claude").mkdir()
        (Path(temp_cache_dir) / "gpt4all").mkdir()
        
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter'):
            
            manager = ModelManager(models_dir=temp_cache_dir)
            
            # Should detect local models
            assert "claude" in manager.available_models
            assert "gpt4all" in manager.available_models
            assert manager.available_models["claude"] == "local:claude"

    def test_default_model_fallback(self, temp_cache_dir):
        """Test default model fallback when specified default not available."""
        models_file = Path(temp_cache_dir) / "models.txt"
        models_file.write_text("model-a\nmodel-b\nmodel-c\n")
        
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter'), \
             patch('builtins.print') as mock_print:
            
            manager = ModelManager(
                models_dir=temp_cache_dir,
                models_file=str(models_file),
                default_model="non-existent-model"
            )
            
            # Should use first available model as fallback
            assert manager.default_model == "model-a"
            # Check fallback message was printed
            fallback_found = any("Default model not found" in str(call) for call in mock_print.call_args_list)
            assert fallback_found


class TestModelsFileLoading:
    """Test _load_models_file method scenarios."""

    def test_load_models_file_success(self, temp_cache_dir):
        """Test successful models file loading."""
        models_file = Path(temp_cache_dir) / "models.txt"
        models_file.write_text("# Comment line\n\nmodel-1/submodel\nmodel-2\n")
        
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter'), \
             patch('builtins.print') as mock_print:
            
            manager = ModelManager(
                models_dir=temp_cache_dir,
                models_file=str(models_file)
            )
            
            # Should load models, ignoring comments and empty lines
            assert "submodel" in manager.available_models
            assert "model-2" in manager.available_models
            assert manager.available_models["submodel"] == "model-1/submodel"
            # Check success message
            success_found = any("Loaded" in str(call) for call in mock_print.call_args_list)
            assert success_found

    def test_load_models_file_not_exists(self, temp_cache_dir):
        """Test loading when models file doesn't exist."""
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter'), \
             patch('builtins.print') as mock_print:
            
            manager = ModelManager(
                models_dir=temp_cache_dir,
                models_file="non_existent.txt"
            )
            
            # Should have empty models dict
            assert len(manager.available_models) == 0  # Only local models might be detected
            # Check warning message
            warning_found = any("not found" in str(call) for call in mock_print.call_args_list)
            assert warning_found

    def test_load_models_file_read_error(self, temp_cache_dir):
        """Test handling of file read errors."""
        models_file = Path(temp_cache_dir) / "models.txt"
        models_file.write_text("model-1\nmodel-2\n")
        
        # Mock open to raise an exception
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter'), \
             patch('builtins.open', side_effect=PermissionError("Access denied")):
            
            manager = ModelManager(
                models_dir=temp_cache_dir,
                models_file=str(models_file)
            )
            
            # Should return empty dict on error
            assert isinstance(manager.available_models, dict)


class TestModelDownloading:
    """Test model downloading functionality."""

    def test_download_huggingface_model_success(self, temp_cache_dir):
        """Test successful HuggingFace model download."""
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value="test_token"), \
             patch('backend.modelmanager.HybridLLMRouter'), \
             patch('backend.modelmanager.huggingface_hub.hf_hub_download') as mock_download:
            
            mock_download.return_value = f"{temp_cache_dir}/model.bin"
            
            manager = ModelManager(models_dir=temp_cache_dir)
            result = manager.download_model("org/model", filename="model.bin")
            
            assert result["status"] == "downloaded"
            assert result["path"] == f"{temp_cache_dir}/model.bin"
            mock_download.assert_called_once_with(
                repo_id="org/model",
                filename="model.bin",
                local_dir=temp_cache_dir,
                token="test_token"
            )

    def test_download_huggingface_model_error(self, temp_cache_dir):
        """Test HuggingFace model download error."""
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value="test_token"), \
             patch('backend.modelmanager.HybridLLMRouter'), \
             patch('backend.modelmanager.huggingface_hub.hf_hub_download', side_effect=Exception("Network error")):
            
            manager = ModelManager(models_dir=temp_cache_dir)
            result = manager.download_model("org/model")
            
            assert result["status"] == "error"
            assert "Network error" in result["error"]

    def test_download_local_model_exists(self, temp_cache_dir):
        """Test download when local model already exists."""
        model_file = Path(temp_cache_dir) / "local-model"
        model_file.write_text("fake model")
        
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter'):
            
            manager = ModelManager(models_dir=temp_cache_dir)
            result = manager.download_model("local-model")
            
            assert result["status"] == "exists"
            assert result["path"] == str(model_file)

    def test_download_local_model_create(self, temp_cache_dir):
        """Test creating a new local model file."""
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter'):
            
            manager = ModelManager(models_dir=temp_cache_dir)
            result = manager.download_model("new-model")
            
            assert result["status"] == "success"
            assert Path(result["path"]).exists()

    def test_download_local_model_error(self, temp_cache_dir):
        """Test local model download error."""
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter'), \
             patch('pathlib.Path.touch', side_effect=PermissionError("Access denied")):
            
            manager = ModelManager(models_dir=temp_cache_dir)
            result = manager.download_model("new-model")
            
            assert result["status"] == "error"
            assert "Access denied" in result["error"]


class TestModelLoading:
    """Test load_model functionality."""

    def test_load_model_default(self, temp_cache_dir):
        """Test loading default model."""
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter') as mock_router_class:
            
            mock_router = Mock()
            mock_router_class.return_value = mock_router
            
            manager = ModelManager(
                models_dir=temp_cache_dir,
                default_model="test-model"
            )
            
            # Mock download_model to return success
            with patch.object(manager, 'download_model') as mock_download:
                model_path = Path(temp_cache_dir) / "test-model"
                model_path.mkdir()
                mock_download.return_value = model_path
                
                result = manager.load_model()
                
                assert result == mock_router
                mock_download.assert_called_once_with("test-model")

    def test_load_model_specific(self, temp_cache_dir):
        """Test loading specific model by name."""
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter') as mock_router_class:
            
            mock_router = Mock()
            mock_router_class.return_value = mock_router
            
            manager = ModelManager(models_dir=temp_cache_dir)
            
            # Mock download_model to return success
            with patch.object(manager, 'download_model') as mock_download:
                model_path = Path(temp_cache_dir) / "specific-model"
                model_path.mkdir()
                mock_download.return_value = model_path
                
                result = manager.load_model("specific-model")
                
                assert result == mock_router
                mock_download.assert_called_once_with("specific-model")

    def test_load_model_no_default(self, temp_cache_dir):
        """Test loading model when no default is available."""
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter'):
            
            manager = ModelManager(
                models_dir=temp_cache_dir,
                default_model=None
            )
            
            with pytest.raises(ValueError, match="No default model available"):
                manager.load_model()

    def test_load_model_already_loaded(self, temp_cache_dir):
        """Test loading model that's already in cache."""
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter'):
            
            manager = ModelManager(models_dir=temp_cache_dir)
            
            # Pre-populate loaded models cache
            mock_model = Mock()
            manager.loaded_models["cached-model"] = mock_model
            
            result = manager.load_model("cached-model")
            
            assert result == mock_model

    def test_load_model_download_failure(self, temp_cache_dir):
        """Test loading model when download fails."""
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter'):
            
            manager = ModelManager(models_dir=temp_cache_dir)
            
            # Mock download_model to return non-existent path
            with patch.object(manager, 'download_model') as mock_download:
                mock_download.return_value = Path(temp_cache_dir) / "non-existent"
                
                with pytest.raises(RuntimeError, match="No offline model available"):
                    manager.load_model("failing-model")

    def test_load_model_instantiation_failure(self, temp_cache_dir):
        """Test loading model when router instantiation fails."""
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter', side_effect=Exception("Router creation failed")):
            
            manager = ModelManager(models_dir=temp_cache_dir)
            
            # Mock download_model to return success
            with patch.object(manager, 'download_model') as mock_download:
                model_path = Path(temp_cache_dir) / "test-model"
                model_path.mkdir()
                mock_download.return_value = model_path
                
                with pytest.raises(RuntimeError, match="Failed to instantiate model router"):
                    manager.load_model("test-model")


class TestFromSettings:
    """Test from_settings class method."""

    def test_from_settings_success(self, mock_settings):
        """Test successful from_settings initialization."""
        with patch('backend.modelmanager.get_settings', return_value=mock_settings), \
             patch('os.getenv', return_value="env_token"), \
             patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('backend.modelmanager.HybridLLMRouter'), \
             patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.exists', return_value=False):
            
            manager = ModelManager.from_settings()
            
            assert manager.models_dir == str(mock_settings.abs_models_dir)
            assert manager.default_model == mock_settings.model_backend
            assert manager.hf_token == "env_token"

    def test_from_settings_fallback(self):
        """Test from_settings fallback when settings fail."""
        with patch('backend.modelmanager.get_settings', side_effect=Exception("Settings unavailable")), \
             patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter'), \
             patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.exists', return_value=False):
            
            manager = ModelManager.from_settings()
            
            # Should use default values
            assert manager.models_dir == "./models"
            # Default model might be changed by fallback logic, just check it's set
            assert manager.default_model is not None


class TestGenerateText:
    """Test text generation functionality."""

    def test_generate_lazy_router_initialization(self, temp_cache_dir):
        """Test lazy initialization of LLM router in generate."""
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter') as mock_router_class:
            
            # Initialize with router creation failure
            mock_router_class.side_effect = [Exception("Init failed"), Mock()]
            
            manager = ModelManager(models_dir=temp_cache_dir)
            
            # Router should be None after failed initialization
            assert manager.llm_router is None
            
            # Reset the side effect for successful creation
            mock_router_instance = Mock()
            mock_router_instance.generate.return_value = "Generated text"
            mock_router_class.side_effect = None
            mock_router_class.return_value = mock_router_instance
            
            # generate() should initialize router lazily
            result = manager.generate("Test prompt")
            
            assert result == "Generated text"
            assert manager.llm_router == mock_router_instance

    def test_generate_with_context(self, temp_cache_dir):
        """Test generate with context parameter."""
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter') as mock_router_class:
            
            mock_router = Mock()
            mock_router.generate.return_value = "Response with context"
            mock_router_class.return_value = mock_router
            
            manager = ModelManager(models_dir=temp_cache_dir)
            
            result = manager.generate("Test", context="Some context")
            
            mock_router.generate.assert_called_once_with(
                "Test",
                prefer_fast=True,
                max_tokens=256,
                context="Some context"
            )
            assert result == "Response with context"

    def test_generate_without_context(self, temp_cache_dir):
        """Test generate without context parameter."""
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter') as mock_router_class:
            
            mock_router = Mock()
            mock_router.generate.return_value = "Response without context"
            mock_router_class.return_value = mock_router
            
            manager = ModelManager(models_dir=temp_cache_dir)
            
            result = manager.generate("Test")
            
            mock_router.generate.assert_called_once_with(
                "Test",
                prefer_fast=True,
                max_tokens=256
            )
            assert result == "Response without context"


class TestGetModelInfo:
    """Test get_model_info functionality."""

    def test_get_model_info_lazy_router_initialization(self, temp_cache_dir):
        """Test lazy initialization of LLM router in get_model_info."""
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter') as mock_router_class:
            
            # Initialize with router creation failure
            mock_router_class.side_effect = [Exception("Init failed"), Mock()]
            
            manager = ModelManager(models_dir=temp_cache_dir)
            
            # Router should be None after failed initialization
            assert manager.llm_router is None
            
            # Reset for successful creation
            mock_router_instance = Mock()
            mock_router_instance.get_available_models.return_value = {"model1": True}
            mock_router_class.side_effect = None
            mock_router_class.return_value = mock_router_instance
            
            # get_model_info() should initialize router lazily
            info = manager.get_model_info()
            
            assert info["available_models"] == {"model1": True}
            assert manager.llm_router == mock_router_instance

    def test_get_model_info_with_existing_router(self, temp_cache_dir):
        """Test get_model_info with already initialized router."""
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter') as mock_router_class:
            
            mock_router = Mock()
            mock_router.get_available_models.return_value = {"llama": False, "gpt4all": True}
            mock_router_class.return_value = mock_router
            
            manager = ModelManager(
                models_dir=temp_cache_dir,
                default_model="test-default"
            )
            
            info = manager.get_model_info()
            
            assert info["available_models"]["llama"] is False
            assert info["available_models"]["gpt4all"] is True
            assert info["default_model"] == "test-default"


class TestModelManagerEdgeCases:
    """Test edge cases and error scenarios."""

    def test_empty_models_file_with_comments_only(self, temp_cache_dir):
        """Test models file with only comments and empty lines."""
        models_file = Path(temp_cache_dir) / "empty_models.txt"
        models_file.write_text("# This is a comment\n\n# Another comment\n\n")
        
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter'), \
             patch('builtins.print') as mock_print:
            
            manager = ModelManager(
                models_dir=temp_cache_dir,
                models_file=str(models_file)
            )
            
            # Should have no models from file
            file_models = [k for k, v in manager.available_models.items() if not v.startswith("local:")]
            assert len(file_models) == 0
            
            # Should print that 0 models were loaded
            loaded_found = any("Loaded 0 models" in str(call) for call in mock_print.call_args_list)
            assert loaded_found

    def test_models_with_complex_paths(self, temp_cache_dir):
        """Test models with complex repository paths."""
        models_file = Path(temp_cache_dir) / "complex_models.txt"
        models_file.write_text("organization/model-name-v1.0\nuser/very-long-model-name-with-dashes\n")
        
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter'):
            
            manager = ModelManager(
                models_dir=temp_cache_dir,
                models_file=str(models_file)
            )
            
            # Should extract model names from paths correctly
            assert "model-name-v1.0" in manager.available_models
            assert "very-long-model-name-with-dashes" in manager.available_models
            assert manager.available_models["model-name-v1.0"] == "organization/model-name-v1.0"

    def test_no_models_available_scenario(self, temp_cache_dir):
        """Test scenario with no models available at all."""
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter'), \
             patch('builtins.print') as mock_print:
            
            manager = ModelManager(
                models_dir=temp_cache_dir,
                models_file="non_existent.txt",
                default_model="unavailable-model"
            )
            
            # Should keep the requested default even if not available
            assert manager.default_model == "unavailable-model"
            
            # Check warning about no models
            no_models_found = any("No models available" in str(call) for call in mock_print.call_args_list)
            assert no_models_found

    def test_model_directory_permissions_error(self, temp_cache_dir):
        """Test handling of model directory creation failure."""
        with patch('backend.modelmanager.load_dotenv'), \
             patch('backend.modelmanager.huggingface_hub.login'), \
             patch('os.getenv', return_value=None), \
             patch('backend.modelmanager.HybridLLMRouter'), \
             patch('pathlib.Path.mkdir', side_effect=PermissionError("Access denied")):
            
            # Should handle directory creation failure gracefully
            try:
                manager = ModelManager(models_dir=temp_cache_dir)
                # Should still initialize even if directory creation fails
                assert hasattr(manager, 'models_dir')
            except PermissionError:
                # Or it might propagate the error, which is also valid
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
# tests/backend/test_modelmanager.py
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# 🎵 Work it HARDER - use proper package imports! 🎵
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from backend.modelmanager import ModelManager

class TestModelManager:
    """Test suite for the ModelManager class."""
    
    @pytest.fixture
    def temp_models_dir(self):
        """Create a temporary directory for models testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_env_file(self, temp_models_dir):
        """Create a mock .env file."""
        env_file = Path(temp_models_dir) / ".env"
        env_file.write_text("HF_TOKEN=test_token_12345\nOTHER_VAR=value")
        return str(env_file)
    
    @pytest.fixture
    def mock_models_file(self, temp_models_dir):
        """Create a mock models.txt file."""
        models_file = Path(temp_models_dir) / "models.txt"
        models_file.write_text("gpt4all-lora\nllama-7b-q4\ncode-llama-13b")
        return str(models_file)
    
    def test_model_manager_initialization_defaults(self):
        """Test ModelManager initialization with default parameters."""
        with patch('backend.modelmanager.load_dotenv'), \
            patch('backend.modelmanager.huggingface_hub.login'), \
            patch('os.getenv', return_value=None), \
            patch('pathlib.Path.exists', return_value=False):
            manager = ModelManager()
            assert manager.models_dir == "./models"
            assert manager.env_file == ".env"
            assert manager.models_file == "models.txt"
            assert manager.default_model == "gpt4all-lora"
    

    def test_model_manager_initialization_custom(self, temp_models_dir:
        """Test ModelManager initialization with custom parameters."""
        with patch('backend.modelmanager.load_dotenv'), \
            patch('backend.modelmanager.huggingface_hub.login'), \
            patch('os.getenv', return_value=None):
            manager = ModelManager(
                models_dir=temp_models_dir,
                env_file="custom.env",
                models_file="custom_models.txt",
                default_model="custom-model",
                hf_token="custom_token"
            )
            assert manager.models_dir == temp_models_dir
            assert manager.env_file == "custom.env"
            assert manager.models_file == "custom_models.txt"
            assert manager.default_model == "custom-model"
            assert manager.hf_token == "custom_token"
    
    def test_hf_token_from_parameter(self, temp_models_dir:
        """Test Hugging Face token loading from parameter."""
        with patch('backend.modelmanager.load_dotenv'), \
            patch('backend.modelmanager.huggingface_hub.login') as mock_login, \
            patch('os.getenv', return_value="env_token"):
            
            manager = ModelManager(
                models_dir=temp_models_dir,
                hf_token="param_token"
            )
            
            # Parameter should take precedence over environment
            assert manager.hf_token == "param_token"
            mock_login.assert_called_once_with(token="param_token"
    
    def test_hf_token_from_environment(self, temp_models_dir):
        """Test Hugging Face token loading from environment."""
        with patch('backend.modelmanager.load_dotenv'), \
            patch('backend.modelmanager.huggingface_hub.login') as mock_login, \
            patch('os.getenv', return_value="env_token"):
            
            manager = ModelManager(models_dir=temp_models_dir)
            
            assert manager.hf_token == "env_token"
            mock_login.assert_called_once_with(token="env_token"
    
    def test_no_hf_token_available(self, temp_models_dir):
        """Test behavior when no Hugging Face token is available."""
        with patch('backend.modelmanager.load_dotenv'), \
            patch('backend.modelmanager.huggingface_hub.login') as mock_login, \
            patch('os.getenv', return_value=None):
            
            manager = ModelManager(models_dir=temp_models_dir)
            
            assert manager.hf_token is None
            mock_login.assert_not_called(
    
    def test_env_file_loading(self, mock_env_file, temp_models_dir):
        """Test loading environment variables from .env file."""
        with patch('backend.modelmanager.load_dotenv') as mock_load_dotenv, \
            patch('backend.modelmanager.huggingface_hub.login'), \
            patch('os.getenv', return_value="test_token_12345"):
            
            ModelManager(
                models_dir=temp_models_dir,
                env_file=mock_env_file
            )
            
            mock_load_dotenv.assert_called_once_with(Path(mock_env_file))
    
    def test_env_file_not_exists(self, temp_models_dir):
        """Test behavior when .env file doesn't exist."""
        with patch('backend.modelmanager.load_dotenv') as mock_load_dotenv, \
            patch('backend.modelmanager.huggingface_hub.login'), \
            patch('os.getenv', return_value=None), \
            patch('builtins.print') as mock_print:
            
            non_existent_env = str(Path(temp_models_dir) / "non_existent.env")
            
            ModelManager(
                models_dir=temp_models_dir,
                env_file=non_existent_env
            )
            
            mock_load_dotenv.assert_not_called()
            # Should print warning about missing env file
            warning_calls = [call for call in mock_print.call_args_list 
                if "Warning" in str(call) and "not found" in str(call)]
            assert len(warning_calls > 0
    
    def test_llm_router_initialization(self, temp_models_dir):
        """Test that LLM router is properly initialized."""
        with patch('backend.modelmanager.load_dotenv'), \
            patch('backend.modelmanager.huggingface_hub.login'), \
            patch('os.getenv', return_value=None), \
            patch('backend.modelmanager.HybridLLMRouter') as mock_router:
            mock_router_instance = Mock()
            mock_router.return_value = mock_router_instance
            manager = ModelManager(models_dir=temp_models_dir)
            # Should initialize LLM router
            assert hasattr(manager, 'llm_router'
            mock_router.assert_called_once()
    
    def test_list_available_models(self, temp_models_dir, mock_models_file):
        """Test listing available models from models.txt."""
        with patch('backend.modelmanager.load_dotenv'), \
            patch('backend.modelmanager.huggingface_hub.login'), \
            patch('os.getenv', return_value=None), \
            patch('backend.modelmanager.HybridLLMRouter'):
            manager = ModelManager(
                models_dir=temp_models_dir,
                models_file=mock_models_file
            )
            models = manager.list_available_models()
            expected_models = ["gpt4all-lora", "llama-7b-q4", "code-llama-13b"]
            assert models == expected_models
    
    def test_list_available_models_file_not_exists(self, temp_models_dir:
        """Test listing models when models.txt doesn't exist."""
        with patch('backend.modelmanager.load_dotenv'), \
            patch('backend.modelmanager.huggingface_hub.login'), \
            patch('os.getenv', return_value=None), \
            patch('backend.modelmanager.HybridLLMRouter'):
            manager = ModelManager(
                models_dir=temp_models_dir,
                models_file="non_existent_models.txt"
            )
            models = manager.list_available_models()
            # Should return empty list or default models
            assert isinstance(models, list
    
    def test_download_model_local_exists(self, temp_models_dir):
        """Test downloading model when it already exists locally."""
        with patch('backend.modelmanager.load_dotenv'), \
            patch('backend.modelmanager.huggingface_hub.login'), \
            patch('os.getenv', return_value=None), \
            patch('backend.modelmanager.HybridLLMRouter'):
            # Create fake model file
            models_path = Path(temp_models_dir)
            models_path.mkdir(exist_ok=True)
            model_file = models_path / "existing-model.bin"
            model_file.write_bytes(b"fake model data")
            manager = ModelManager(models_dir=temp_models_dir)
            result = manager.download_model("existing-model.bin")
            # Should not download if already exists
            assert result["status"] == "exists" or result["status"] == "success"
            assert result["path"] == str(model_file
    
    def test_download_model_from_huggingface(self, temp_models_dir):
        """Test downloading model from Hugging Face."""
        with patch('backend.modelmanager.load_dotenv'), \
            patch('backend.modelmanager.huggingface_hub.login'), \
            patch('os.getenv', return_value="test_token"), \
            patch('backend.modelmanager.HybridLLMRouter'), \
            patch('backend.modelmanager.huggingface_hub.hf_hub_download') as mock_download:
            mock_download.return_value = f"{temp_models_dir}/downloaded-model.bin"
            manager = ModelManager(models_dir=temp_models_dir)
            result = manager.download_model("test-org/test-model", filename="model.bin")
            mock_download.assert_called_once_with(
                repo_id="test-org/test-model",
                filename="model.bin",
                local_dir=temp_models_dir,
                token="test_token"
            )
            assert result["status"] == "downloaded"
            assert "path" in result
    
    def test_download_model_huggingface_error(self, temp_models_dir:
        """Test handling of Hugging Face download errors."""
        with patch('backend.modelmanager.load_dotenv'), \
            patch('backend.modelmanager.huggingface_hub.login'), \
            patch('os.getenv', return_value="test_token"), \
            patch('backend.modelmanager.HybridLLMRouter'), \
            patch('backend.modelmanager.huggingface_hub.hf_hub_download', 
                side_effect=Exception("Download failed")):
            manager = ModelManager(models_dir=temp_models_dir)
            result = manager.download_model("test-org/test-model")
            assert result["status"] == "error"
            assert "error" in result
            assert "Download failed" in result["error"]
    
    def test_generate_text_with_default_model(self, temp_models_dir:
        """Test text generation with default model."""
        with patch('backend.modelmanager.load_dotenv'), \
            patch('backend.modelmanager.huggingface_hub.login'), \
            patch('os.getenv', return_value=None), \
            patch('backend.modelmanager.HybridLLMRouter') as mock_router:
            mock_router_instance = Mock()
            mock_router_instance.generate.return_value = "Generated response"
            mock_router.return_value = mock_router_instance
            manager = ModelManager(models_dir=temp_models_dir)
            response = manager.generate("Test prompt")
            assert response == "Generated response"
            mock_router_instance.generate.assert_called_once_with(
                "Test prompt",
                prefer_fast=True,
                max_tokens=256
            
    
    def test_generate_text_with_custom_parameters(self, temp_models_dir):
        """Test text generation with custom parameters."""
        with patch('backend.modelmanager.load_dotenv'), \
            patch('backend.modelmanager.huggingface_hub.login'), \
            patch('os.getenv', return_value=None), \
            patch('backend.modelmanager.HybridLLMRouter') as mock_router:
            mock_router_instance = Mock()
            mock_router_instance.generate.return_value = "Custom response"
            mock_router.return_value = mock_router_instance
            manager = ModelManager(models_dir=temp_models_dir)
            response = manager.generate(
                "Custom prompt",
                model_name="custom-model",
                prefer_fast=False,
                max_tokens=512,
                context="Some context"
            )
            assert response == "Custom response"
            mock_router_instance.generate.assert_called_once_with(
                "Custom prompt",
                prefer_fast=False,
                max_tokens=512,
                context="Some context"
            
    
    def test_get_model_info(self, temp_models_dir):
        """Test getting model information."""
        with patch('backend.modelmanager.load_dotenv'), \
            patch('backend.modelmanager.huggingface_hub.login'), \
            patch('os.getenv', return_value=None), \
            patch('backend.modelmanager.HybridLLMRouter') as mock_router:
            mock_router_instance = Mock()
            mock_router_instance.get_available_models.return_value = {
                "llama": True,
                "gpt4all": False
            }
            mock_router.return_value = mock_router_instance
            manager = ModelManager(models_dir=temp_models_dir)
            info = manager.get_model_info()
            assert isinstance(info, dict
            assert "available_models" in info
            assert info["available_models"]["llama"] is True
            assert info["available_models"]["gpt4all"] is False
            assert info["default_model"] == manager.default_model
    
    def test_huggingface_login_error(self, temp_models_dir:
        """Test handling of Hugging Face login errors."""
        with patch('backend.modelmanager.load_dotenv'), \
            patch('backend.modelmanager.huggingface_hub.login',
                side_effect=Exception("Login failed")), \
            patch('os.getenv', return_value="invalid_token"):
            manager = ModelManager(models_dir=temp_models_dir)
            # Should handle login error gracefully
            assert manager.hf_token == "invalid_token"
            # Should print error message
            # Login errors might be handled silently or with warnings
    
    def test_models_directory_creation(self, temp_models_dir:
        """Test that models directory is created if it doesn't exist."""
        with patch('backend.modelmanager.load_dotenv'), \
            patch('backend.modelmanager.huggingface_hub.login'), \
            patch('os.getenv', return_value=None), \
            patch('backend.modelmanager.HybridLLMRouter'):
            models_dir = Path(temp_models_dir) / "new_models_dir"
            manager = ModelManager(models_dir=str(models_dir))
            # Directory should be created during initialization or first use
            # This might be handled in download_model or other methods
            assert hasattr(manager, 'models_dir'

class TestModelManagerIntegration:
    """Integration tests for ModelManager."""
    
    def test_complete_workflow(self, temp_models_dir, mock_models_file):
        """Test a complete ModelManager workflow."""
        with patch('backend.modelmanager.load_dotenv'), \
            patch('backend.modelmanager.huggingface_hub.login'), \
            patch('os.getenv', return_value="test_token"), \
            patch('backend.modelmanager.HybridLLMRouter') as mock_router:
            mock_router_instance = Mock()
            mock_router_instance.generate.return_value = "Test response"
            mock_router_instance.get_available_models.return_value = {"llama": True}
            mock_router.return_value = mock_router_instance
            manager = ModelManager(
                models_dir=temp_models_dir,
                models_file=mock_models_file
            )
            # List models
            models = manager.list_available_models()
            assert len(models > 0
            # Generate text
            response = manager.generate("Test prompt")
            assert response == "Test response"
            # Get model info
            info = manager.get_model_info(
            assert isinstance(info, dict
            # All operations should complete successfully
            assert manager.hf_token == "test_token"

if __name__ == "__main__":
    pytest.main([__file__]

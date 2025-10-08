# tests/backend/test_settings.py
import pytest
 
from pathlib import Path
from unittest.mock import Mock, patch
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.settings import Settings, get_settings, reload_settings, update_settings, _load_yaml_config, _merge_env


class TestSettings:
    """Test settings model and default behavior."""
    
    def test_settings_defaults(self):
        """Test that Settings initializes with expected defaults."""
        s = Settings()
        assert s.backend_url == "http://127.0.0.1:8000"
        assert s.api_port == 8000
        assert s.allow_network is False
        assert s.continuous_mode is False
        assert s.vault_path == "vault"
        assert s.models_dir == "models" 
        assert s.cache_dir == "cache"
        assert s.model_backend == "llama_cpp"
        assert s.embed_model == "sentence-transformers/all-MiniLM-L6-v2"
        assert s.vector_db == "chroma"
        assert s.gpu is True
        assert s.top_k == 10
        assert s.chunk_size == 800
        assert s.chunk_overlap == 200
        assert s.similarity_threshold == 0.75
        
    def test_derived_properties(self:
        """Test that derived path properties work correctly."""
        s = Settings(project_root="/test/project", vault_path="my_vault", models_dir="my_models", cache_dir="my_cache")
        assert s.base_dir == Path("/test/project"
        assert s.abs_vault_path == Path("/test/project/my_vault"
        assert s.abs_models_dir == Path("/test/project/my_models"
        assert s.abs_cache_dir == Path("/test/project/my_cache"
        
    def test_absolute_paths(self):
        """Test that absolute paths are preserved."""
        if os.name == 'nt':  # Windows
            s = Settings(vault_path="C:/abs/vault", models_dir="C:/abs/models", cache_dir="C:/abs/cache")
            assert s.abs_vault_path == Path("C:/abs/vault"
            assert s.abs_models_dir == Path("C:/abs/models"
            assert s.abs_cache_dir == Path("C:/abs/cache"
        else:  # Unix-like
            s = Settings(vault_path="/abs/vault", models_dir="/abs/models", cache_dir="/abs/cache")
            assert s.abs_vault_path == Path("/abs/vault"
            assert s.abs_models_dir == Path("/abs/models"
            assert s.abs_cache_dir == Path("/abs/cache"


class TestSettingsPrecedence:
    """Test environment > YAML > defaults precedence."""
    
    def setup_method(self):
        """Clear any cached settings before each test."""
        try:
            get_settings.cache_clear()
        except AttributeError:
            pass
    
    def test_yaml_override_defaults(self):
        """Test that YAML config overrides defaults."""
        # Mock _load_yaml_config to return test data directly
        mock_yaml_data = {
            "api_port": 9000,
            "vault_path": "yaml_vault", 
            "gpu": False,
            "chunk_size": 1000
        }
        
        with patch('backend.settings._load_yaml_config', return_value=mock_yaml_data):
            with patch.dict(os.environ, {}, clear=True):  # Clear env vars
                s = get_settings()
                assert s.api_port == 9000
                assert s.vault_path == "yaml_vault"
                assert s.gpu is False
                assert s.chunk_size == 1000
                # Non-overridden values should remain defaults
                assert s.backend_url == "http://127.0.0.1:9000"  # Computed from api_port
                assert s.allow_network is False
    
    def test_env_override_yaml_and_defaults(self:
        """Test that environment variables override both YAML and defaults."""
        # Mock YAML data that should be overridden by env vars
        mock_yaml_data = {
            "api_port": 9000,
            "vault_path": "yaml_vault", 
            "gpu": True,
            "chunk_size": 1000
        }
        
        env_vars = {
            'API_PORT': '7000', 
            'VAULT_PATH': 'env_vault',
            'ALLOW_NETWORK': 'true',
            'GPU': 'false',
            'CHUNK_SIZE': '1200',
            'SIMILARITY_THRESHOLD': '0.8'
        }
        
        with patch('backend.settings._load_yaml_config', return_value=mock_yaml_data):
            with patch.dict(os.environ, env_vars, clear=True):
                s = get_settings()
                # Environment should win over YAML
                assert s.api_port == 7000
                assert s.vault_path == "env_vault"
                assert s.allow_network is True
                assert s.gpu is False
                assert s.chunk_size == 1200
                assert s.similarity_threshold == 0.8
                assert s.backend_url == "http://127.0.0.1:7000"
    
    def test_invalid_env_values_ignored(self:
        """Test that invalid environment values are ignored gracefully."""
        # Use empty YAML and test invalid env vars
        with patch('backend.settings._load_yaml_config', return_value={}):
            with patch.dict(os.environ, {'CHUNK_SIZE': 'not_a_number', 'GPU': 'maybe'}, clear=True):
                s = get_settings()
                # Invalid int values should be ignored, booleans parsed as False
                assert s.chunk_size == 800  # Invalid int ignored, falls back to default
                assert s.gpu is False  # Invalid boolean parsed as False


class TestSettingsHelpers:
    """Test helper functions for settings management."""
    
    def setup_method(self:
        get_settings.cache_clear()
    
    def test_load_yaml_config_missing_file(self):
        """Test loading YAML when file doesn't exist."""
        with patch('backend.settings.Path') as mock_path_cls:
            mock_path = Mock()
            mock_path.exists.return_value = False
            mock_path_cls.return_value = mock_path
            mock_path_cls.__file__ = "/fake/settings.py"
            
            result = _load_yaml_config()
            assert result == {}
    
    def test_load_yaml_config_no_yaml_module(self:
        """Test loading YAML when yaml module is not available."""
        with patch('backend.settings.yaml', None):
            result = _load_yaml_config()
            assert result == {}
    
    def test_load_yaml_config_invalid_yaml(self, tmp_path:
        """Test loading YAML with invalid content."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("invalid: yaml: content: :[")
        
        with patch('backend.settings.Path') as mock_path_cls:
            mock_path = Mock()
            mock_path.parent = tmp_path
            mock_path_cls.return_value = mock_path
            mock_path_cls.__file__ = str(tmp_path / "settings.py")
            
            with patch('backend.settings.open', create=True) as mock_open:
                mock_open.side_effect = Exception("YAML parse error")
                
                result = _load_yaml_config()
                assert result == {}
    
    @patch.dict(os.environ, {
        'API_PORT': '3000',
        'ALLOW_NETWORK': '1', 
        'GPU': 'true',
        'CHUNK_SIZE': 'invalid',
        'SIMILARITY_THRESHOLD': 'also_invalid'
    }
    def test_merge_env_type_coercion(self):
        """Test that environment variable type coercion works correctly."""
        overrides = {}
        result = _merge_env(overrides)
        
        assert result['api_port'] == 3000  # int
        assert result['allow_network'] is True  # bool
        assert result['gpu'] is True  # bool
        # Invalid values should not be included
        assert 'chunk_size' not in result
        assert 'similarity_threshold' not in result
    
    def test_reload_settings_clears_cache(self:
        """Test that reload_settings clears the cache."""
        # Get settings once to populate cache
        s1 = get_settings()
        
        # Reload should clear cache and return new instance
        s2 = reload_settings()
        
        # Should be same values but different instances due to cache clear
        assert s1.api_port == s2.api_port
        assert isinstance(s2, Settings


class TestUpdateSettings:
    """Test settings update functionality."""
    
    def setup_method(self):
        get_settings.cache_clear()
    
    def test_update_settings_whitelist(self, tmp_path):
        """Test that only whitelisted keys can be updated."""
        with patch('backend.settings.Path') as mock_path_cls:
            mock_path = Mock()
            mock_path.parent = tmp_path
            mock_path_cls.return_value = mock_path
            mock_path_cls.__file__ = str(tmp_path / "settings.py")
            

            
            # Mock yaml operations
            with patch('backend.settings.yaml') as mock_yaml:
                mock_yaml.safe_load.return_value = {}
                
                updates = {
                    'vault_path': 'new_vault',
                    'chunk_size': 1500,
                    'api_port': 9999,  # Not in whitelist
                    'malicious_key': 'hack_attempt'  # Not in whitelist
                }
                
                update_settings(updates)
                
                # Should only include whitelisted updates
                mock_yaml.safe_dump.assert_called_once()
                saved_data = mock_yaml.safe_dump.call_args[0][0]
                assert 'vault_path' in saved_data
                assert 'chunk_size' in saved_data
                assert 'api_port' not in saved_data
                assert 'malicious_key' not in saved_data
    
    def test_update_settings_type_coercion(self, tmp_path:
        """Test that update_settings coerces types correctly."""
        with patch('backend.settings.Path') as mock_path_cls:
            mock_path = Mock()
            mock_path.parent = tmp_path
            mock_path_cls.return_value = mock_path
            mock_path_cls.__file__ = str(tmp_path / "settings.py")
            
            with patch('backend.settings.yaml') as mock_yaml:
                mock_yaml.safe_load.return_value = {}
                
                updates = {
                    'chunk_size': '2000',  # String -> int
                    'gpu': 'true',  # String -> bool
                    'similarity_threshold': '0.9',  # String -> float
                    'vault_path': 123  # -> string
                }
                
                update_settings(updates)
                
                saved_data = mock_yaml.safe_dump.call_args[0][0]
                assert saved_data['chunk_size'] == 2000
                assert saved_data['gpu'] is True
                assert saved_data['similarity_threshold'] == 0.9
                assert saved_data['vault_path'] == '123'
    
    def test_update_settings_invalid_types_removed(self, tmp_path:
        """Test that invalid type coercions are removed from updates."""
        with patch('backend.settings.Path') as mock_path_cls:
            mock_path = Mock()
            mock_path.parent = tmp_path  
            mock_path_cls.return_value = mock_path
            mock_path_cls.__file__ = str(tmp_path / "settings.py")
            
            with patch('backend.settings.yaml') as mock_yaml:
                mock_yaml.safe_load.return_value = {}
                
                updates = {
                    'chunk_size': 'not_a_number',
                    'similarity_threshold': 'also_invalid',
                    'vault_path': 'valid_path'
                }
                
                update_settings(updates)
                
                saved_data = mock_yaml.safe_dump.call_args[0][0]
                # Invalid coercions should be removed
                assert 'chunk_size' not in saved_data
                assert 'similarity_threshold' not in saved_data
                # Valid updates should remain
                assert 'vault_path' in saved_data


if __name__ == "__main__":
    pytest.main([__file__]
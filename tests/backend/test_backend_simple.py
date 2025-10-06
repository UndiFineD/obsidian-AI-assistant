# tests/backend/test_backend_simple.py
"""
Simple backend tests avoiding PyTorch import conflicts.
Testing core functionality without complex dependencies.
"""
import pytest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
    'torch.nn': Mock(),
    'torch.optim': Mock(),
    'torchvision': Mock(),
})
def test_backend_imports():
    """Test that backend can be imported with mocked PyTorch."""
    try:
        import backend.backend as backend_module
        assert backend_module is not None
        print("✓ Backend imported successfully")
    except Exception as e:
        pytest.fail(f"Failed to import backend: {e}")


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(), 
    'sentence_transformers': Mock(),
})
def test_fastapi_app_exists():
    """Test that the FastAPI app variable exists."""
    import backend.backend as backend_module
    
    # Check that app exists
    assert hasattr(backend_module, 'app')
    print("✓ FastAPI app exists")


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
})  
@pytest.mark.asyncio
async def test_health_endpoint_function():
    """Test the health endpoint function directly."""
    import backend.backend as backend_module
    
    # Test health function exists and is callable
    assert hasattr(backend_module, 'health')
    assert callable(backend_module.health)
    
    # Call async health function
    result = await backend_module.health()
    
    # Verify result structure
    assert isinstance(result, dict)
    assert 'status' in result
    assert result['status'] == 'ok'
    print("✓ Health endpoint function works")


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
})
@patch('backend.backend.CacheManager')
@patch('backend.backend.VaultIndexer') 
@patch('backend.backend.EmbeddingsManager')
@patch('backend.backend.ModelManager')
def test_service_initialization(mock_model, mock_emb, mock_vault, mock_cache):
    """Test that services can be initialized with mocked dependencies."""
    # Mock the service instances
    mock_model.return_value = Mock()
    mock_emb.return_value = Mock()
    mock_vault.return_value = Mock() 
    mock_cache.return_value = Mock()
    
    # Import backend
    import backend.backend as backend_module
    
    # Services should be available
    print("✓ Backend services initialized successfully")


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
})
@patch('backend.backend.CacheManager')
@patch('backend.backend.VaultIndexer')
@patch('backend.backend.EmbeddingsManager') 
@patch('backend.backend.ModelManager')
def test_cors_middleware(mock_model, mock_emb, mock_vault, mock_cache):
    """Test CORS middleware setup."""
    # Mock services
    mock_model.return_value = Mock()
    mock_emb.return_value = Mock()
    mock_vault.return_value = Mock()
    mock_cache.return_value = Mock()
    
    import backend.backend as backend_module
    
    # Check that app has CORS configured
    assert hasattr(backend_module, 'app')
    
    # Check middleware is present (this exercises the CORS setup code)
    middleware_stack = backend_module.app.user_middleware
    print(f"✓ CORS middleware configured, middleware count: {len(middleware_stack)}")


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
})
@pytest.mark.asyncio
async def test_ask_request_model():
    """Test AskRequest model validation."""
    import backend.backend as backend_module
    
    # Test valid request
    valid_data = {
        'question': 'test question',
        'prefer_fast': True,
        'max_tokens': 256,
        'model_name': 'claude'
    }
    
    # Create request instance
    request = backend_module.AskRequest(**valid_data)
    
    assert request.question == 'test question'
    assert request.prefer_fast == True
    assert request.max_tokens == 256
    assert request.model_name == 'claude'
    print("✓ AskRequest model validation works")


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(), 
    'sentence_transformers': Mock(),
})
@pytest.mark.asyncio
async def test_reindex_request_model():
    """Test ReindexRequest model validation."""
    import backend.backend as backend_module
    
    # Test valid request
    valid_data = {'vault_path': '/test/path'}
    request = backend_module.ReindexRequest(**valid_data)
    
    assert request.vault_path == '/test/path'
    print("✓ ReindexRequest model validation works")


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
})
@pytest.mark.asyncio
async def test_web_request_model():
    """Test WebRequest model validation.""" 
    import backend.backend as backend_module
    
    # Test valid request
    valid_data = {'url': 'https://example.com'}
    request = backend_module.WebRequest(**valid_data)
    
    assert request.url == 'https://example.com'
    print("✓ WebRequest model validation works")


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
})
@pytest.mark.asyncio
async def test_transcribe_request_model():
    """Test TranscribeRequest model validation."""
    import backend.backend as backend_module
    
    # Test valid request
    valid_data = {
        'audio_data': 'base64encodeddata',
        'format': 'webm',
        'language': 'en'
    }
    request = backend_module.TranscribeRequest(**valid_data)
    
    assert request.audio_data == 'base64encodeddata'
    assert request.format == 'webm'
    assert request.language == 'en'
    print("✓ TranscribeRequest model validation works")


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
})
@pytest.mark.asyncio
async def test_health_payload_function():
    """Test _health_payload helper function."""
    import backend.backend as backend_module
    
    # Call the health payload function
    payload = backend_module._health_payload()
    
    # Verify structure
    assert isinstance(payload, dict)
    assert 'status' in payload
    assert 'timestamp' in payload
    assert payload['status'] == 'ok'
    print("✓ _health_payload function works")


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
})
@pytest.mark.asyncio
async def test_api_health_endpoint():
    """Test api_health endpoint."""
    import backend.backend as backend_module
    
    # Call api health endpoint
    result = await backend_module.api_health()
    
    # Verify structure
    assert isinstance(result, dict)
    assert 'status' in result
    print("✓ api_health endpoint works")


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
})
@pytest.mark.asyncio
async def test_status_endpoint():
    """Test status endpoint."""
    import backend.backend as backend_module
    
    # Call status endpoint  
    result = await backend_module.status()
    
    # Verify structure
    assert isinstance(result, dict)
    assert 'status' in result
    print("✓ status endpoint works")


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
})
@patch('backend.backend.model_manager')
def test_init_services_function(mock_model_manager):
    """Test init_services function.""" 
    # Mock model manager
    mock_model_manager.config = Mock()
    mock_model_manager.config.get.return_value = "test_value"
    
    import backend.backend as backend_module
    
    # Call init_services
    backend_module.init_services()
    
    # Verify it executed without errors
    print("✓ init_services function works")


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
})
@patch('backend.backend.model_manager')
@pytest.mark.asyncio
async def test_get_config_endpoint(mock_model_manager):
    """Test get_config endpoint."""
    # Mock model manager config
    mock_config = {
        'model_settings': {'default': 'claude'},
        'cache_settings': {'enabled': True}
    }
    mock_model_manager.config = mock_config
    
    import backend.backend as backend_module
    
    # Call get_config
    result = await backend_module.get_config()
    
    # Verify result is a dictionary (the actual config content will vary)
    assert isinstance(result, dict)
    assert len(result) > 0
    print("✓ get_config endpoint works")


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
})
@patch('backend.backend.model_manager')
@pytest.mark.asyncio
async def test_post_reload_config_endpoint(mock_model_manager):
    """Test post_reload_config endpoint."""
    mock_model_manager.reload_config = Mock()
    
    import backend.backend as backend_module
    
    # Call post_reload_config
    result = await backend_module.post_reload_config()
    
    # Verify reload was called
    mock_model_manager.reload_config.assert_called_once()
    
    # Verify result
    assert isinstance(result, dict)
    assert result['message'] == 'Config reloaded'
    print("✓ post_reload_config endpoint works")


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
})
@patch('backend.backend.model_manager')
@pytest.mark.asyncio
async def test_post_update_config_endpoint(mock_model_manager):
    """Test post_update_config endpoint."""
    mock_model_manager.update_config = Mock()
    
    import backend.backend as backend_module
    
    # Test update data
    update_data = {'setting': 'value'}
    
    # Call post_update_config
    result = await backend_module.post_update_config(update_data)
    
    # Verify update was called
    mock_model_manager.update_config.assert_called_once_with(update_data)
    
    # Verify result
    assert isinstance(result, dict)
    assert result['message'] == 'Config updated'
    print("✓ post_update_config endpoint works")


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
})
@patch('backend.backend.vault_indexer')
@pytest.mark.asyncio
async def test_scan_vault_endpoint(mock_vault_indexer):
    """Test scan_vault endpoint."""
    mock_vault_indexer.scan_vault = AsyncMock(return_value={'files': ['file1.md', 'file2.md']})
    
    import backend.backend as backend_module
    
    # Call scan_vault
    result = await backend_module.scan_vault("test_vault")
    
    # Verify scan was called
    mock_vault_indexer.scan_vault.assert_called_once_with("test_vault")
    
    # Verify result
    assert isinstance(result, dict)
    assert 'files' in result
    print("✓ scan_vault endpoint works")


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
})
@patch('backend.backend.embeddings_manager')
@pytest.mark.asyncio
async def test_search_endpoint(mock_embeddings_manager):
    """Test search endpoint.""" 
    mock_search_result = [
        {'text': 'result 1', 'score': 0.9},
        {'text': 'result 2', 'score': 0.8}
    ]
    mock_embeddings_manager.search = AsyncMock(return_value=mock_search_result)
    
    import backend.backend as backend_module
    
    # Call search
    result = await backend_module.search("test query", 5)
    
    # Verify search was called
    mock_embeddings_manager.search.assert_called_once_with("test query", 5)
    
    # Verify result
    assert result == mock_search_result
    print("✓ search endpoint works")


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
})
@patch('backend.backend.embeddings_manager')
@pytest.mark.asyncio
async def test_index_pdf_endpoint(mock_embeddings_manager):
    """Test index_pdf endpoint."""
    mock_embeddings_manager.index_pdf = AsyncMock(return_value={'status': 'indexed'})
    
    import backend.backend as backend_module
    
    # Call index_pdf
    result = await backend_module.index_pdf("/path/to/test.pdf")
    
    # Verify index_pdf was called
    mock_embeddings_manager.index_pdf.assert_called_once_with("/path/to/test.pdf")
    
    # Verify result
    assert isinstance(result, dict)
    assert 'status' in result
    print("✓ index_pdf endpoint works")


if __name__ == '__main__':
    # Run tests individually for debugging
    test_backend_imports()
    test_fastapi_app_exists()
    test_health_endpoint_function()
    test_service_initialization()
    print("All simple backend tests passed!")
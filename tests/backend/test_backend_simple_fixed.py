# tests/backend/test_backend_simple_fixed.py
"""
Fixed backend tests with proper mocking and endpoint testing.
"""
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock, AsyncMock


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
})
@patch('backend.backend.reload_settings')  
@pytest.mark.asyncio
async def test_post_reload_config_endpoint(mock_reload_settings):
    """Test post_reload_config endpoint."""
    # Mock the settings return value with dict() method
    mock_settings = Mock()
    mock_settings.dict.return_value = {'setting': 'value'}
    mock_reload_settings.return_value = mock_settings
    
    import backend.backend as backend_module
    
    # Call post_reload_config
    result = await backend_module.post_reload_config()
    
    # Verify reload was called
    mock_reload_settings.assert_called_once()
    
    # Verify result
    assert isinstance(result, dict)
    assert result['ok'] is True
    assert 'settings' in result
    print("✓ post_reload_config endpoint works")


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
})
@patch('backend.backend.update_settings')  
@pytest.mark.asyncio
async def test_post_update_config_endpoint(mock_update_settings):
    """Test post_update_config endpoint."""
    # Mock the settings return value with dict() method
    mock_settings = Mock()
    mock_settings.dict.return_value = {'updated_setting': 'new_value'}
    mock_update_settings.return_value = mock_settings
    
    import backend.backend as backend_module
    
    # Test update data
    update_data = {'setting': 'value'}
    
    # Call post_update_config
    result = await backend_module.post_update_config(update_data)
    
    # Verify update was called
    mock_update_settings.assert_called_once_with(update_data)
    
    # Verify result
    assert isinstance(result, dict)
    assert result['ok'] is True
    assert 'settings' in result
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
    mock_vault_indexer.index_vault = Mock(return_value=['file1.md', 'file2.md'])
    
    import backend.backend as backend_module
    
    # Call scan_vault
    result = await backend_module.scan_vault("test_vault")
    
    # Verify index_vault was called
    mock_vault_indexer.index_vault.assert_called_once_with("test_vault")
    
    # Verify result
    assert isinstance(result, dict)
    assert 'indexed_files' in result
    assert result['indexed_files'] == ['file1.md', 'file2.md']
    print("✓ scan_vault endpoint works")


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
})
@patch('backend.backend.emb_manager')
@pytest.mark.asyncio
async def test_search_endpoint(mock_emb_manager):
    """Test search endpoint.""" 
    mock_search_result = [
        {'text': 'result 1', 'score': 0.9},
        {'text': 'result 2', 'score': 0.8}
    ]
    mock_emb_manager.search = Mock(return_value=mock_search_result)
    
    import backend.backend as backend_module
    
    # Call search
    result = await backend_module.search("test query", 5)
    
    # Verify search was called
    mock_emb_manager.search.assert_called_once_with("test query", top_k=5)
    
    # Verify result
    assert isinstance(result, dict)
    assert "results" in result
    assert result["results"] == mock_search_result
    print("✓ search endpoint works")


@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
})
@patch('backend.backend.vault_indexer')
@pytest.mark.asyncio
async def test_index_pdf_endpoint(mock_vault_indexer):
    """Test index_pdf endpoint."""
    mock_vault_indexer.index_pdf = Mock(return_value=5)
    
    import backend.backend as backend_module
    
    # Call index_pdf
    result = await backend_module.index_pdf("/path/to/test.pdf")
    
    # Verify index_pdf was called
    mock_vault_indexer.index_pdf.assert_called_once_with("/path/to/test.pdf")
    
    # Verify result
    assert isinstance(result, dict)
    assert "chunks_indexed" in result
    assert result['chunks_indexed'] == 5
    print("✓ index_pdf endpoint works")


if __name__ == "__main__":
    # Run tests individually for debugging
    print("🧪 Running Fixed Backend API Tests")
    print("===================================")
    
    # Run with pytest
    pytest.main([__file__, "-v"])
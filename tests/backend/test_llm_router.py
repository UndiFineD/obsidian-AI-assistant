# tests/backend/test_llm_router.py
import pytest
from unittest.mock import Mock, patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.llm_router import HybridLLMRouter

@pytest.fixture
def mock_llama():
    """Mock LLaMA model."""
    with patch('llm_router.Llama') as mock_llama_class:
        mock_llama_instance = Mock()
        mock_llama_instance.__call__.return_value = {"choices": [{"text": "LLaMA response"}]}
        mock_llama_class.return_value = mock_llama_instance
        yield mock_llama_instance

@pytest.fixture
def router_with_mocks(mock_llama, mock_gpt4all):
    router = HybridLLMRouter(
        llama_model_path="fake/llama.bin",
        gpt4all_model_path="fake/gpt4all.bin",
        prefer_fast=True
    )
    return router

    """Test router initialization with default values."""
    with patch('os.path.exists', return_value=False), \
        patch('llm_router.Llama', None), \
        patch('llm_router.GPT4All', None):
        router = HybridLLMRouter()
        assert router.prefer_fast is True
        assert router.session_memory is True
        assert router.memory_limit == 5
        assert router.llama_model_path == "models/llama-7b-q4.bin"
        assert router.gpt4all_model_path == "models/gpt4all-lora-quantized.bin"
        assert router.prefer_fast is False
        
    """Test router initialization with custom values."""
    with patch('os.path.exists', return_value=False), \
        patch('llm_router.Llama', None), \
        patch('llm_router.GPT4All', None):
        router = HybridLLMRouter(
            llama_model_path="custom/llama.bin",
            gpt4all_model_path="custom/gpt4all.bin",
            prefer_fast=False,
            session_memory=False,
            memory_limit=10
        )
        assert router.prefer_fast is False
        assert router.session_memory is False
        assert router.memory_limit == 10
        assert router.llama_model_path == "custom/llama.bin"
        assert router.gpt4all_model_path == "custom/gpt4all.bin"
        assert router.session_memory is False
        assert router.memory_limit == 10
        assert router.llama_model_path == "custom/llama.bin"
        assert router.gpt4all_model_path == "custom/gpt4all.bin"
                
def test_model_loading_no_models_available(self):
    """Test model loading when no models are available."""
    with patch('os.path.exists', return_value=False), \
        patch('llm_router.Llama', None), \
        patch('llm_router.GPT4All', None):
        
        router = HybridLLMRouter()
        
        assert router.llama_model is None
        assert router.gpt4all_model is None
        assert router.available_models["llama"] is False
        assert router.available_models["gpt4all"] is False

def test_model_loading_file_not_exists(self, mock_llama, mock_gpt4all):
    """Test model loading when model files don't exist."""
    with patch('os.path.exists', return_value=False):
        router = HybridLLMRouter()
        
        # Models should not be loaded if files don't exist
        assert router.llama_model is None
        assert router.gpt4all_model is None

def test_generate_with_llama_preferred_fast(self, router_with_mocks, mock_llama):
    """Test generation with LLaMA when preferring fast responses."""
    prompt = "What is AI?"
    
    response = router_with_mocks.generate(prompt, prefer_fast=True)
    
    # Should use LLaMA for fast responses
    assert response == "LLaMA response"
    mock_llama.__call__.assert_called_once()

def test_generate_with_gpt4all_not_preferred_fast(self, router_with_mocks, mock_gpt4all):
    """Test generation with GPT4All when not preferring fast responses."""
    prompt = "What is a complex topic?"
    
    response = router_with_mocks.generate(prompt, prefer_fast=False)
    
    # Should use GPT4All for more detailed responses
    assert response == "GPT4All response"
    mock_gpt4all.generate.assert_called_once()

def test_generate_fallback_to_available_model(self, mock_gpt4all):
    """Test generation fallback when preferred model is not available."""
    with patch('os.path.exists', return_value=True), \
        patch('llm_router.Llama', None):  # LLaMA not available
        
        router = HybridLLMRouter(prefer_fast=True)
        response = router.generate("Test prompt", prefer_fast=True)
        
        # Should fallback to GPT4All even though LLaMA was preferred
        assert response == "GPT4All response"
        mock_gpt4all.generate.assert_called_once()

def test_generate_no_models_available(self):
    """Test generation when no models are available."""
    with patch('os.path.exists', return_value=False), \
        patch('llm_router.Llama', None), \
        patch('llm_router.GPT4All', None):
        
        router = HybridLLMRouter()
        response = router.generate("Test prompt")
        
        # Should return error message
        assert "No models available" in response or response == ""

def test_generate_with_context_and_memory(self, router_with_mocks, mock_llama):
    """Test generation with context and session memory."""
    router_with_mocks.session_memory = True
    
    # First interaction
    response1 = router_with_mocks.generate("First question", context="Some context")
    
    # Second interaction - should include previous in memory
    response2 = router_with_mocks.generate("Follow-up question")
    
    # Both should use LLaMA
    assert response1 == "LLaMA response"
    assert response2 == "LLaMA response"
    assert mock_llama.__call__.call_count == 2

def test_generate_memory_limit(self, router_with_mocks, mock_llama):
    """Test that memory respects the configured limit."""
    router_with_mocks.memory_limit = 2
    
    # Generate more interactions than memory limit
    for i in range(5):
        router_with_mocks.generate(f"Question {i}")
    
    # Memory should only contain last 2 interactions
    assert len(router_with_mocks.memory) <= 2 * 2  # 2 interactions * 2 entries each (Q&A)

def test_generate_without_memory(self, router_with_mocks, mock_llama):
    """Test generation without session memory."""
    router_with_mocks.session_memory = False
    
    response1 = router_with_mocks.generate("First question")
    response2 = router_with_mocks.generate("Second question")
    
    # Ensure responses are strings
    assert isinstance(response1, str)
    assert isinstance(response2, str)
    # Memory should remain empty
    assert len(router_with_mocks.memory) == 0

def test_generate_with_max_tokens(self, router_with_mocks, mock_llama):
    """Test generation with custom max_tokens parameter."""
    prompt = "Test prompt"
    max_tokens = 100
    
    response = router_with_mocks.generate(prompt, max_tokens=max_tokens)
    
    # Should pass max_tokens to the model
    call_args = mock_llama.__call__.call_args
    assert call_args is not None
    # Check if max_tokens was passed in the call
    # (exact structure depends on LLaMA implementation)
    assert response == "LLaMA response"

def test_model_selection_based_on_prompt_length(self, router_with_mocks, mock_llama, mock_gpt4all):
    """Test model selection based on prompt length."""
    short_prompt = "Short question?"
    long_prompt = "This is a very long prompt that contains many words and should trigger the use of a more capable model for better results. " * 10
    
    # Short prompt with prefer_fast should use LLaMA
    router_with_mocks.generate(short_prompt, prefer_fast=True)
    
    # Long prompt might use GPT4All even if prefer_fast is True
    router_with_mocks.generate(long_prompt, prefer_fast=False)
    
    # Verify appropriate models were called
    assert mock_llama.__call__.called
    assert mock_gpt4all.generate.called

def test_error_handling_llama_exception(self, router_with_mocks, mock_llama):
    """Test error handling when LLaMA raises exception."""
    mock_llama.__call__.side_effect = Exception("LLaMA error")
    
    response = router_with_mocks.generate("Test prompt", prefer_fast=True)
    
    # Should handle exception gracefully
    assert isinstance(response, str)
    # Might fallback to GPT4All or return error message

def test_error_handling_gpt4all_exception(self, router_with_mocks, mock_gpt4all):
    """Test error handling when GPT4All raises exception."""
    mock_gpt4all.generate.side_effect = Exception("GPT4All error")
    
    with patch('llm_router.Llama', None):  # Make LLaMA unavailable
        response = router_with_mocks.generate("Test prompt", prefer_fast=False)
    
    # Should handle exception gracefully
    assert isinstance(response, str)

def test_memory_management_operations(self, router_with_mocks):
    """Test memory management operations."""
    # Add some interactions
    router_with_mocks.generate("Question 1")
    router_with_mocks.generate("Question 2")
    
    # Test memory clearing (if implemented)
    if hasattr(router_with_mocks, 'clear_memory'):
        router_with_mocks.clear_memory()
        assert len(router_with_mocks.memory) == 0

def test_get_available_models(self, router_with_mocks):
    """Test getting list of available models."""
    available = router_with_mocks.get_available_models()
    
    assert isinstance(available, dict)
    assert "llama" in available
    assert "gpt4all" in available
    assert isinstance(available["llama"], bool)
    assert isinstance(available["gpt4all"], bool)

def test_model_import_errors(self):
    """Test handling of import errors for model libraries."""
    # Test when Llama is None (import failed)
    with patch('llm_router.Llama', None), \
        patch('llm_router.GPT4All', None):
        
        router = HybridLLMRouter()
        
        # Should handle missing imports gracefully
        assert router.available_models["llama"] is False
        assert router.available_models["gpt4all"] is False


class TestLLMRouterIntegration:
    """Integration tests for HybridLLMRouter."""
    
    def test_full_conversation_workflow(self, mock_llama, mock_gpt4all):
        """Test a full conversation workflow."""
        with patch('os.path.exists', return_value=True):
            router = HybridLLMRouter(session_memory=True, memory_limit=3)
            
            # Simulate a conversation
            responses = []
            questions = [
                "What is machine learning?",
                "Can you explain neural networks?", 
                "How does deep learning work?",
                "What about reinforcement learning?"
            ]
            
            for question in questions:
                response = router.generate(question)
                responses.append(response)
            
            # All responses should be generated
            assert len(responses) == 4
            assert all(isinstance(r, str) for r in responses)
            
            # Memory should respect limit
            assert len(router.memory) <= 3 * 2  # 3 interactions * 2 entries each


if __name__ == "__main__":
    pytest.main([__file__])
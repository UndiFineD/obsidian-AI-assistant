import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from PIL import Image
import torch

# Add project root to path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)

# Import after path setup
from backend.llm_router import HybridLLMRouter  # noqa: E402


class TestLLMRouter(unittest.TestCase):
    def setUp(self):
        self.router = HybridLLMRouter()

    def test_init_no_models(self):
        """Test initialization without any model paths."""
        self.assertIsNone(self.router.gpt4all)
        self.assertIsNone(self.router.text_model)
        self.assertIsNone(self.router.text_tokenizer)
        self.assertIsNone(self.router.image_pipeline)

    def test_init_with_invalid_paths(self):
        """Test initialization with invalid model paths."""
        router = HybridLLMRouter(
            gpt4all_model_path="nonexistent.bin",
            transformers_model_path="nonexistent",
            image_model_path="nonexistent"
        )
        self.assertIsNone(router.gpt4all)
        self.assertIsNone(router.text_model)
        self.assertIsNone(router.text_tokenizer)
        self.assertIsNone(router.image_pipeline)

    def test_memory_management(self):
        """Test chat memory management functionality."""
        router = HybridLLMRouter(memory_limit=2)
        
        # Test adding to memory
        router.add_to_memory("User", "Hello")
        self.assertEqual(len(router.memory), 1)
        self.assertEqual(router.memory[0], {
            "role": "User",
            "content": "Hello"
        })
        
        # Test memory limit
        router.add_to_memory("Assistant", "Hi")
        router.add_to_memory("User", "How are you?")
        self.assertEqual(len(router.memory), 2)
        self.assertEqual(router.memory[0], {
            "role": "Assistant",
            "content": "Hi"
        })
        self.assertEqual(router.memory[1], {
            "role": "User",
            "content": "How are you?"
        })

    def test_build_context(self):
        """Test context building from chat memory."""
        # Empty memory
        self.assertEqual(self.router.build_context("test"), "test")
        
        # With memory
        self.router.add_to_memory("User", "Hello")
        self.router.add_to_memory("Assistant", "Hi")
        expected = "User: Hello\nAssistant: Hi\nUser: test"
        self.assertEqual(self.router.build_context("test"), expected)

    def test_no_session_memory(self):
        """Test router behavior with session memory disabled."""
        router = HybridLLMRouter(session_memory=False)
        router.add_to_memory("User", "Hello")
        self.assertEqual(len(router.memory), 0)
        self.assertEqual(router.build_context("test"), "test")

    def test_device_selection(self):
        """Test proper CUDA/CPU device selection."""
        expected_device = "cuda" if torch.cuda.is_available() else "cpu"
        self.assertEqual(self.router.device, expected_device)

    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForCausalLM')
    def test_text_generation_transformers(self, mock_model, mock_tokenizer):
        """Test text generation with transformers model."""
        # Mock the tokenizer and model
        mock_tokenizer.from_pretrained.return_value = MagicMock()
        mock_model.from_pretrained.return_value = MagicMock()
        mock_tokenizer.from_pretrained.return_value.decode.return_value = \
            "Test response"
        
        router = HybridLLMRouter(transformers_model_path="mock_path")
        if router.text_model:
            result = router.generate_text("Hello")
            self.assertIsInstance(result, str)
            self.assertTrue(len(result) > 0)

    def test_text_generation_no_model(self):
        """Test text generation with no available models."""
        result = self.router.generate_text("Hello")
        self.assertEqual(result, "No text generation model available.")

    @patch('diffusers.StableDiffusionXLPipeline')
    def test_image_generation(self, mock_pipeline):
        """Test image generation with SDXL pipeline."""
        # Mock the pipeline
        mock_image = Image.new('RGB', (1024, 1024))
        pipeline = MagicMock()
        pipeline.to = MagicMock(return_value=MagicMock(
            return_value=MagicMock(images=[mock_image])
        ))
        mock_pipeline.from_pretrained.return_value = pipeline
        
        router = HybridLLMRouter(image_model_path="mock_path")
        if router.image_pipeline:
            result = router.generate_image("A test image")
            self.assertIsInstance(result, Image.Image)
            self.assertEqual(result.size, (1024, 1024))

    def test_image_generation_no_model(self):
        """Test image generation with no available model."""
        result = self.router.generate_image("A test image")
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()

# Backend package initialization
"""
Obsidian AI Assistant Backend Package

This package contains the core backend modules for the Obsidian AI Assistant:
- FastAPI application and endpoints
- LLM routing and model management
- Vector database and embeddings
- Document indexing and processing
- Caching and security utilities
- Voice processing capabilities
"""

__version__ = "1.0.0"
__author__ = "Obsidian AI Assistant"

# Make key classes available at package level
try:
    from .backend import app
    from .caching import CacheManager
    from .embeddings import EmbeddingsManager
    from .llm_router import HybridLLMRouter
    from .modelmanager import ModelManager
    from .security import encrypt_data, decrypt_data
except ImportError:
    # Handle imports gracefully during testing or when dependencies are missing
    pass

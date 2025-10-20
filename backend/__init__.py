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

__version__ = "0.1.30"
__author__ = "Obsidian AI Assistant"


# Make key classes available at package level
try:
    import importlib.util

    importlib.util.find_spec(f"{__name__}.backend")
    importlib.util.find_spec(f"{__name__}.caching")
    importlib.util.find_spec(f"{__name__}.embeddings")
    importlib.util.find_spec(f"{__name__}.llm_router")
    importlib.util.find_spec(f"{__name__}.modelmanager")
    importlib.util.find_spec(f"{__name__}.security")
except ImportError as e:
    # Handle imports gracefully during testing or when dependencies are missing
    import logging

    logging.error(f"ImportError in backend.__init__: {e}")


# Ensure submodule is accessible as attribute for patching like 'backend.backend.*'
try:
    import importlib as _importlib
    import sys as _sys

    _backend_mod = _importlib.import_module(".backend", __name__)
    # Expose attribute on package
    _sys.modules[__name__].backend = _backend_mod
except Exception as e:
    import logging

    logging.error(f"Exception in backend.__init__ (submodule import): {e}")

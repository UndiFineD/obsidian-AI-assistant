#!/usr/bin/env python3
"""
🎵 Work it harder, make it better, do it faster, makes us stronger! 🎵
Test runner that ensures proper import paths for backend tests.
"""

import sys
import os
from pathlib import Path

# Ensure project root is in Python path for imports
project_root = Path(__file__).parent.parent  # Go up one level from tests to project root
sys.path.insert(0, str(project_root))

# Verify imports work
try:
    import backend.backend
    print("✅ backend.backend import successful!")
except ImportError as e:
    print(f"❌ backend.backend import failed: {e}")
    sys.exit(1)

# Now run pytest
import pytest

if __name__ == "__main__":
    # Run pytest with args
    pytest_args = ["tests/backend/", "-v", "--tb=short"]
    exit_code = pytest.main(pytest_args)
    sys.exit(exit_code)
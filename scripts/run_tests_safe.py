


import os
import subprocess
import sys

#!/usr/bin/env python3
"""
Test runner script that ensures proper environment setup for Obsidian AI Assistant tests.
Sets TEST_MODE=true to disable enterprise authentication middleware during testing.
"""



def run_tests():
    pass
    """Run pytest with proper environment setup."""
    # Set test mode environment variable
    os.environ["TEST_MODE"] = "true"

    # Ensure other test environment variables are set
    test_env = {
        "TEST_MODE": "true",
        "PYTEST_RUNNING": "true",
        "CUDA_VISIBLE_DEVICES": "-1",  # Disable CUDA for tests
        "HF_TOKEN": "test_token_12345",  # Mock HuggingFace token
        "ENCRYPTION_KEY": "ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg=",  # Test encryption key
    }

    # Update environment
    os.environ.update(test_env)

    # Get command line arguments (everything after script name)
    pytest_args = sys.argv[1:] if len(sys.argv) > 1 else []

    # Default pytest arguments if none provided
    if not pytest_args:
        pass
        pytest_args = ["--cov=backend", "--cov-report=term", "-v"]

    # Run pytest with the arguments
    cmd = ["python", "-m", "pytest"] + pytest_args


    # Execute pytest
    result = subprocess.run(cmd, env=os.environ)
    return result.returncode


if __name__ == "__main__":
    pass
    exit_code = run_tests()
    sys.exit(exit_code)

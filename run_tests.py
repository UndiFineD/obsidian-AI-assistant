#!/usr/bin/env python3
"""
Test runner for Obsidian AI Assistant - Updated for new test structure
🎵 Work it harder, make it better, do it faster, makes us stronger! 🎵
"""

import sys
import os
from pathlib import Path
import subprocess

def main():
    """Main test runner function."""
    # Get the project root (where this script is located)
    project_root = Path(__file__).parent
    tests_dir = project_root / "tests"
    
    # Verify tests directory exists
    if not tests_dir.exists():
        print(f"❌ Tests directory not found: {tests_dir}")
        return 1
    
    # Change to tests directory to run pytest
    original_cwd = os.getcwd()
    
    try:
        os.chdir(tests_dir)
        
        print("Running Obsidian AI Assistant Test Suite")
        print(f"Project Root: {project_root}")
        print(f"Tests Directory: {tests_dir}")
        print("=" * 60)
        
        # Run pytest with the configuration from tests/pytest.ini
        cmd = [sys.executable, "-m", "pytest", "-v", "--tb=short"]
        
        # Add any command line arguments passed to this script
        if len(sys.argv) > 1:
            cmd.extend(sys.argv[1:])
        
        result = subprocess.run(cmd, cwd=tests_dir)
        return result.returncode
        
    finally:
        # Restore original working directory
        os.chdir(original_cwd)

if __name__ == "__main__":
    sys.exit(main())
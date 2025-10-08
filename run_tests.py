#!/usr/bin/env python3
"""
Obsidian AI Assistant - Main Test Entry Point
"""

import sys
import subprocess
from pathlib import Path

def main():
    project_root = Path(__file__).parent
    test_runner = project_root / "tests" / "run_tests.py"
    
    if not test_runner.exists():
        print("Test runner not found at tests/run_tests.py")
        return 1
    
    print("Obsidian AI Assistant Test Suite")
    print("Delegating to tests/run_tests.py...")
    print("=" * 50)
    
    cmd = [sys.executable, str(test_runner)] + sys.argv[1:]
    return subprocess.call(cmd)

if __name__ == "__main__":
    sys.exit(main())




import sys
import subprocess
from pathlib import Path

#!/usr/bin/env python3
"""
Obsidian AI Assistant - Main Test Entry Point
"""


def main():
    pass
    project_root = Path(__file__).parent
    test_runner = project_root / "tests" / "comprehensive_async_test_runner.py"

    if not test_runner.exists():
        pass
        return 1


    cmd = [sys.executable, str(test_runner)] + sys.argv[1:]
    return subprocess.call(cmd)

if __name__ == "__main__":
    pass
    sys.exit(main())

#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

"""
Obsidian AI Assistant - Main Test Entry Point
Runs pytest when the legacy runner is missing.
"""


def main() -> int:
    repo_root = Path(__file__).parent.parent
    tests_dir = repo_root / "tests"

    # Prefer pytest directly; fall back to a basic discovery
    try:
        cmd = [sys.executable, "-m", "pytest", "-q"]
        return subprocess.call(cmd, cwd=repo_root)
    except Exception:
        # Very minimal fallback
        print("[run_tests] Unable to invoke pytest")
        return 1


if __name__ == "__main__":
    sys.exit(main())

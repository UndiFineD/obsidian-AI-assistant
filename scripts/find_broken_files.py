#!/usr/bin/env python3
"""Find all Python files with syntax/indentation errors."""

import ast
import sys
from pathlib import Path


def check_file(filepath):
    """Check if a Python file has syntax errors."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"{e.__class__.__name__}: {e.msg} (line {e.lineno})"
    except IndentationError as e:
        return False, f"{e.__class__.__name__}: {e.msg} (line {e.lineno})"
    except Exception as e:
        return False, f"{e.__class__.__name__}: {e}"


def main():
    root = Path(__file__).parent.parent

    # Directories to skip
    skip_dirs = {".venv", "venv", "node_modules", "__pycache__", ".git", "htmlcov"}

    broken_files = []
    ok_files = []

    for py_file in root.rglob("*.py"):
        # Skip excluded directories
        if any(skip_dir in py_file.parts for skip_dir in skip_dirs):
            continue

        is_ok, error = check_file(py_file)
        if is_ok:
            ok_files.append(py_file)
        else:
            broken_files.append((py_file, error))

    print(f"\n{'=' * 70}")
    print("Python File Analysis")
    print(f"{'=' * 70}")
    print(f"Total OK files: {len(ok_files)}")
    print(f"Total BROKEN files: {len(broken_files)}")
    print(f"{'=' * 70}\n")

    # Always write broken_files.txt, even if empty
    with open(root / "broken_files.txt", "w") as f:
        if broken_files:
            print("Files with syntax/indentation errors:\n")
            for filepath, error in broken_files:
                rel_path = filepath.relative_to(root)
                print(f"  {rel_path}")
                print(f"    Error: {error}\n")
                f.write(str(filepath) + "\n")
            print("\nBroken file paths written to: broken_files.txt")
        # If no broken files, file will be empty
    return 0 if not broken_files else 1


if __name__ == "__main__":
    sys.exit(main())

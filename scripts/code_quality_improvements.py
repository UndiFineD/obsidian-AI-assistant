#!/usr/bin/env python3
"""Automated code quality improvements for the project."""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def run_command(cmd, description):
    """Run a command and print results."""
    print(f"\n{'='*70}")
    print(f"🔧 {description}")
    print(f"{'='*70}")
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=REPO_ROOT
        )
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {e}")
        return False


def format_python_code():
    """Format Python code with Black."""
    return run_command(
        "python -m black backend/ scripts/ tests/ --line-length 88 --exclude .venv",
        "Formatting Python code with Black",
    )


def lint_python_code():
    """Lint Python code with ruff."""
    return run_command(
        "python -m ruff check backend/ scripts/ --select E,F,W,I --fix",
        "Linting Python code with ruff (auto-fix enabled)",
    )


def security_scan():
    """Run security scan with bandit."""
    return run_command(
        "python -m bandit -r backend/ -f json -o bandit_report.json -ll",
        "Security scanning with bandit",
    )


def check_imports():
    """Check for unused imports."""
    return run_command(
        "python -m ruff check backend/ scripts/ --select F401 --fix",
        "Removing unused imports",
    )


def sort_imports():
    """Sort imports with isort."""
    try:
        import isort

        has_isort = True
    except ImportError:
        has_isort = False

    if has_isort:
        return run_command(
            "python -m isort backend/ scripts/ tests/ --profile black",
            "Sorting imports with isort",
        )
    else:
        print("\n⚠️ isort not installed, skipping import sorting")
        return True


def type_check():
    """Type check with mypy."""
    try:
        import mypy

        has_mypy = True
    except ImportError:
        has_mypy = False

    if has_mypy:
        return run_command(
            "python -m mypy backend/ --ignore-missing-imports --no-error-summary",
            "Type checking with mypy",
        )
    else:
        print("\n⚠️ mypy not installed, skipping type checking")
        return True


def remove_trailing_whitespace():
    """Remove trailing whitespace from Python files."""
    print(f"\n{'='*70}")
    print("🧹 Removing trailing whitespace")
    print(f"{'='*70}")

    fixed_count = 0
    for py_file in REPO_ROOT.rglob("*.py"):
        if ".venv" in str(py_file) or "__pycache__" in str(py_file):
            continue

        try:
            with open(py_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = [line.rstrip() + "\n" for line in lines]

            if new_lines != lines:
                with open(py_file, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                fixed_count += 1
                print(f"  ✓ {py_file.relative_to(REPO_ROOT)}")
        except Exception as e:
            print(f"  ✗ {py_file.relative_to(REPO_ROOT)}: {e}")

    print(f"\n✅ Fixed {fixed_count} files")
    return True


def main():
    """Run all code quality improvements."""
    print("\n🚀 Starting Automated Code Quality Improvements")
    print(f"{'='*70}\n")

    steps = [
        ("Remove trailing whitespace", remove_trailing_whitespace),
        ("Format code with Black", format_python_code),
        ("Sort imports", sort_imports),
        ("Lint and auto-fix", lint_python_code),
        ("Remove unused imports", check_imports),
        ("Type check", type_check),
        ("Security scan", security_scan),
    ]

    results = []
    for step_name, step_func in steps:
        success = step_func()
        results.append((step_name, success))

    # Summary
    print(f"\n{'='*70}")
    print("📊 Code Quality Improvement Summary")
    print(f"{'='*70}\n")

    for step_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {step_name}")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    print(f"\n{'='*70}")
    print(f"🎯 Results: {passed}/{total} steps passed ({passed*100//total}%)")
    print(f"{'='*70}\n")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

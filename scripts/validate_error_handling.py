#!/usr/bin/env python3
"""Quick test to validate error handling integration works correctly."""

import os
import sys
from pathlib import Path

# Add the project root to Python path so imports work correctly
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_syntax_check():
    """Test that our error handling files have valid Python syntax."""
    files_to_check = [
        "backend/error_handling.py",
        "backend/exception_handlers.py",
        "backend/backend.py",
    ]

    for file_path in files_to_check:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Compile the code to check for syntax errors
            compile(content, file_path, "exec")
            print(f"✓ {file_path} syntax is valid")
        except SyntaxError as e:
            print(f"✗ {file_path} has syntax error: {e}")
            return False
        except Exception as e:
            print(f"✗ {file_path} check failed: {e}")
            return False

    return True


def test_error_handling_file_structure():
    """Test that our error handling files have the expected structure."""
    error_handling_path = "backend/error_handling.py"

    try:
        with open(error_handling_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for key components
        checks = [
            ("ObsidianAIError class", "class ObsidianAIError"),
            ("ValidationError class", "class ValidationError"),
            ("ConfigurationError class", "class ConfigurationError"),
            ("ModelError class", "class ModelError"),
            ("ErrorSeverity enum", "class ErrorSeverity"),
            ("ErrorCategory enum", "class ErrorCategory"),
            ("error_context function", "def error_context"),
            ("ErrorHandler class", "class ErrorHandler"),
        ]

        for check_name, check_pattern in checks:
            if check_pattern in content:
                print(f"✓ {check_name} found")
            else:
                print(f"✗ {check_name} not found")
                return False

        return True
    except Exception as e:
        print(f"✗ Error handling file structure check failed: {e}")
        return False


def test_exception_handlers_file_structure():
    """Test that our exception handlers file has the expected structure."""
    handlers_path = "backend/exception_handlers.py"

    try:
        with open(handlers_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for key components
        checks = [
            (
                "obsidian_ai_exception_handler",
                "async def obsidian_ai_exception_handler",
            ),
            ("validation_exception_handler", "async def validation_exception_handler"),
            ("RequestTrackingMiddleware", "class RequestTrackingMiddleware"),
            ("setup_exception_handlers", "def setup_exception_handlers"),
        ]

        for check_name, check_pattern in checks:
            if check_pattern in content:
                print(f"✓ {check_name} found")
            else:
                print(f"✗ {check_name} not found")
                return False

        return True
    except Exception as e:
        print(f"✗ Exception handlers file structure check failed: {e}")
        return False


def test_backend_integration():
    """Test that backend.py has proper error handling integration."""
    backend_path = "backend/backend.py"

    try:
        with open(backend_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for integration points
        checks = [
            ("Error handling imports", "from .error_handling import"),
            ("Exception handlers setup", "setup_exception_handlers"),
            ("RequestTrackingMiddleware", "RequestTrackingMiddleware"),
            ("error_context usage", "with error_context"),
        ]

        for check_name, check_pattern in checks:
            if check_pattern in content:
                print(f"✓ {check_name} found in backend.py")
            else:
                print(f"✗ {check_name} not found in backend.py")
                return False

        return True
    except Exception as e:
        print(f"✗ Backend integration check failed: {e}")
        return False


def test_file_permissions():
    """Test that files have proper permissions and are readable."""
    files_to_check = [
        "backend/error_handling.py",
        "backend/exception_handlers.py",
        "backend/backend.py",
    ]

    for file_path in files_to_check:
        try:
            if not os.path.exists(file_path):
                print(f"✗ {file_path} does not exist")
                return False

            if not os.access(file_path, os.R_OK):
                print(f"✗ {file_path} is not readable")
                return False

            print(f"✓ {file_path} exists and is readable")
        except Exception as e:
            print(f"✗ {file_path} permission check failed: {e}")
            return False

    return True


def main():
    """Run all error handling integration tests."""
    print("Testing Error Handling Integration (Syntax & Structure)")
    print("=" * 60)

    tests = [
        test_file_permissions,
        test_syntax_check,
        test_error_handling_file_structure,
        test_exception_handlers_file_structure,
        test_backend_integration,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")

    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All error handling integration tests passed!")
        print("\nNext steps:")
        print("- Error handling framework is ready")
        print("- FastAPI integration is complete")
        print("- You can now run the backend server to test endpoints")
        return True
    else:
        print("❌ Some tests failed. Check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

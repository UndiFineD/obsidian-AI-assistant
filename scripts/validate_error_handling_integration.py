#!/usr/bin/env python3
"""Quick test to validate error handling integration works correctly."""

import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_error_handling_imports():
    """Test that error handling modules can be imported successfully."""
    try:
        import backend.error_handling as eh
        # Test key classes exist
        assert hasattr(eh, 'ObsidianAIError')
        assert hasattr(eh, 'ValidationError')
        assert hasattr(eh, 'ConfigurationError')
        assert hasattr(eh, 'ModelError')
        assert hasattr(eh, 'ErrorSeverity')
        assert hasattr(eh, 'ErrorCategory')
        assert hasattr(eh, 'error_context')
        
        print("✓ Error handling imports successful")
        return True
    except Exception as e:
        print(f"✗ Error handling import failed: {e}")
        return False

def test_exception_handlers_imports():
    """Test that exception handlers can be imported successfully."""
    try:
        import backend.exception_handlers as handlers
        # Test key functions/classes exist
        assert hasattr(handlers, 'setup_exception_handlers')
        assert hasattr(handlers, 'RequestTrackingMiddleware')
        
        print("✓ Exception handlers imports successful")
        return True
    except Exception as e:
        print(f"✗ Exception handlers import failed: {e}")
        return False

def test_error_context():
    """Test that error context works correctly."""
    try:
        import backend.error_handling as eh
        
        # Test successful operation
        with eh.error_context("test_operation", reraise=False):
            result = "success"
        
        # Test error handling
        try:
            with eh.error_context("test_error", reraise=False):
                raise eh.ValidationError("Test validation error", field="test_field")
        except eh.ValidationError as e:
            print(f"✓ Error context correctly handled ValidationError: {e.user_message}")
            
        print("✓ Error context functionality working")
        return True
    except Exception as e:
        print(f"✗ Error context test failed: {e}")
        return False

def test_error_hierarchy():
    """Test that error hierarchy works correctly."""
    try:
        import backend.error_handling as eh
        
        # Test error creation
        val_error = eh.ValidationError("Test validation", field="test")
        config_error = eh.ConfigurationError("Test config", config_key="test")
        model_error = eh.ModelError("Test model", model_name="test")
        
        # Test properties
        assert val_error.severity.name == "MEDIUM"
        assert config_error.category.name == "CONFIGURATION"
        assert model_error.user_message.startswith("Test model")
        
        print("✓ Error hierarchy working correctly")
        return True
    except Exception as e:
        print(f"✗ Error hierarchy test failed: {e}")
        return False

def test_backend_integration():
    """Test that backend can import error handling without issues."""
    try:
        # Mock required modules to avoid actual service initialization
        import sys
        from unittest.mock import MagicMock
        
        # Mock heavy dependencies
        sys.modules['torch'] = MagicMock()
        sys.modules['transformers'] = MagicMock()
        sys.modules['sentence_transformers'] = MagicMock()
        
        # Import backend (this will test the error handling integration)
        from backend.backend import app
        
        print("✓ Backend integration successful")
        return True
    except Exception as e:
        print(f"✗ Backend integration failed: {e}")
        return False

def main():
    """Run all error handling integration tests."""
    print("Testing Error Handling Integration...")
    print("=" * 50)
    
    tests = [
        test_error_handling_imports,
        test_exception_handlers_imports,
        test_error_context,
        test_error_hierarchy,
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
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All error handling integration tests passed!")
        return True
    else:
        print("❌ Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
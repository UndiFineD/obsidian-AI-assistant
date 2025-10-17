#!/usr/bin/env python3
"""Test enhanced caching system integration."""

import sys
import time
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_enhanced_caching_imports():
    """Test that enhanced caching modules can be imported."""
    try:
        import backend.enhanced_caching as ec
        import backend.cache_management as cm
        
        # Test key classes exist
        assert hasattr(ec, 'UnifiedCacheManager')
        assert hasattr(ec, 'CacheType')
        assert hasattr(ec, 'CacheStrategy')
        assert hasattr(ec, 'get_unified_cache_manager')
        assert hasattr(ec, 'cached_with_intelligence')
        
        # Test cache management
        assert hasattr(cm, 'cache_router')
        assert hasattr(cm, 'CacheStatsResponse')
        
        print("✓ Enhanced caching imports successful")
        return True
    except Exception as e:
        print(f"✗ Enhanced caching import failed: {e}")
        return False

def test_unified_cache_manager():
    """Test unified cache manager functionality."""
    try:
        # Mock dependencies to avoid import issues
        import sys
        from unittest.mock import MagicMock
        
        # Mock heavy dependencies
        sys.modules['torch'] = MagicMock()
        sys.modules['transformers'] = MagicMock()
        
        # Import and test cache manager
        from backend.enhanced_caching import UnifiedCacheManager, CacheType
        
        # Create cache manager
        cache_manager = UnifiedCacheManager(cache_dir="./test_cache")
        
        # Test basic operations
        test_key = "test:key"
        test_value = "test value"
        
        # Set and get
        success = cache_manager.set(test_key, test_value)
        assert success, "Cache set should succeed"
        
        retrieved = cache_manager.get(test_key)
        assert retrieved == test_value, f"Retrieved value should match: {retrieved} != {test_value}"
        
        # Test stats
        stats = cache_manager.get_comprehensive_stats()
        assert isinstance(stats, dict), "Stats should be a dictionary"
        assert "unified_cache" in stats, "Stats should include unified_cache"
        
        print("✓ Unified cache manager functionality working")
        return True
    except Exception as e:
        print(f"✗ Unified cache manager test failed: {e}")
        return False

def test_cache_routing():
    """Test intelligent cache routing."""
    try:
        from backend.enhanced_caching import SmartCacheRouter, CacheType
        
        router = SmartCacheRouter()
        
        # Test different key patterns
        test_cases = [
            ("ask:question1", CacheType.PERSISTENT),
            ("embed:text1", CacheType.PERMANENT),
            ("file:path1", CacheType.SESSION),
            ("api:endpoint1", CacheType.TRANSIENT),
            ("health:check1", CacheType.EPHEMERAL),
        ]
        
        for key, expected_type in test_cases:
            analysis = router.analyze_key(key)
            assert analysis["cache_type"] == expected_type, f"Wrong cache type for {key}: {analysis['cache_type']} != {expected_type}"
        
        print("✓ Cache routing functionality working")
        return True
    except Exception as e:
        print(f"✗ Cache routing test failed: {e}")
        return False

def test_cache_decorator():
    """Test intelligent caching decorator."""
    try:
        from backend.enhanced_caching import cached_with_intelligence
        
        call_count = 0
        
        @cached_with_intelligence(ttl=60)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return f"result_{x}"
        
        # First call should execute function
        result1 = expensive_function(1)
        assert call_count == 1, f"Function should be called once: {call_count}"
        assert result1 == "result_1", f"Result should match: {result1}"
        
        # Second call should use cache
        result2 = expensive_function(1)
        assert call_count == 1, f"Function should still be called once: {call_count}"
        assert result2 == "result_1", f"Cached result should match: {result2}"
        
        # Different parameter should execute function again
        result3 = expensive_function(2)
        assert call_count == 2, f"Function should be called twice: {call_count}"
        assert result3 == "result_2", f"Result should match: {result3}"
        
        print("✓ Cache decorator functionality working")
        return True
    except Exception as e:
        print(f"✗ Cache decorator test failed: {e}")
        return False

def test_backend_integration():
    """Test that enhanced caching integrates with backend without errors."""
    try:
        # Mock dependencies
        import sys
        from unittest.mock import MagicMock
        
        # Mock all heavy dependencies
        sys.modules['torch'] = MagicMock()
        sys.modules['transformers'] = MagicMock()
        sys.modules['sentence_transformers'] = MagicMock()
        sys.modules['chromadb'] = MagicMock()
        
        # Test that backend imports work with enhanced caching
        import backend.backend
        
        # Check that enhanced caching imports are present
        assert hasattr(backend.backend, 'get_unified_cache_manager'), "Backend should have unified cache manager"
        assert hasattr(backend.backend, 'cache_router'), "Backend should have cache router"
        
        print("✓ Backend integration successful")
        return True
    except Exception as e:
        print(f"✗ Backend integration test failed: {e}")
        return False

def main():
    """Run all enhanced caching tests."""
    print("Testing Enhanced Caching System")
    print("=" * 50)
    
    tests = [
        test_enhanced_caching_imports,
        test_unified_cache_manager,
        test_cache_routing,
        test_cache_decorator,
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
        print("🎉 All enhanced caching tests passed!")
        print("\nEnhanced caching features:")
        print("- Multi-level cache hierarchy (L1: memory, L2: disk, L3: compressed)")
        print("- Intelligent cache routing based on data type and access patterns")
        print("- Cache invalidation and optimization")
        print("- Performance monitoring and statistics")
        print("- RESTful cache management API")
        print("- Unified interface for all cache providers")
        return True
    else:
        print("❌ Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
import pytest
from backend import performance

def test_performance_exists():
    assert hasattr(performance, "PerformanceMonitor")

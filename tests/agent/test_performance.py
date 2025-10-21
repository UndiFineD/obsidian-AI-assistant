import pytest

from agent import performance


def test_performance_exists():
    assert hasattr(performance, "PerformanceMonitor")

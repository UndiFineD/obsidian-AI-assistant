"""
Performance Regression Tests for Obsidian AI Assistant

These tests ensure that performance remains within acceptable bounds across releases.
They test:
- API endpoint response times
- Memory usage patterns
- Cache performance
- Database query performance
- Overall system throughput
"""

import asyncio
import time
from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient

# Performance SLA thresholds (in milliseconds)
PERFORMANCE_THRESHOLDS = {
    # Tier 1: Critical fast paths (<100ms)
    "health_check": 100,
    "status_check": 100,
    "config_read": 100,
    "cache_lookup": 100,
    # Tier 2: Standard operations (<500ms)
    "ask_cached": 500,
    "search_simple": 500,
    "voice_validation": 500,
    # Tier 3: AI operations (<2000ms = 2s)
    "ask_uncached": 2000,
    "search_semantic": 2000,
    "embedding_generation": 2000,
    # Tier 4: Complex operations (<10000ms = 10s)
    "web_analysis": 10000,
    "document_indexing": 10000,
    "pdf_processing": 10000,
    # Tier 5: Batch operations (<60000ms = 60s)
    "vault_reindex": 60000,
    "model_loading": 60000,
}


class PerformanceAssertion:
    """Helper class for performance assertions with detailed reporting"""

    @staticmethod
    def assert_within_threshold(
        duration_ms: float,
        threshold_ms: float,
        operation: str,
        context: Dict[str, Any] = None,
    ):
        """
        Assert that operation duration is within threshold.

        Provides detailed error message if threshold is exceeded.
        """
        if duration_ms > threshold_ms:
            context_str = f"\nContext: {context}" if context else ""
            performance_ratio = (duration_ms / threshold_ms) * 100

            pytest.fail(
                f"\n{'='*70}\n"
                f"PERFORMANCE REGRESSION DETECTED\n"
                f"{'='*70}\n"
                f"Operation: {operation}\n"
                f"Duration: {duration_ms:.2f}ms\n"
                f"Threshold: {threshold_ms:.2f}ms\n"
                f"Exceeded by: {duration_ms - threshold_ms:.2f}ms ({performance_ratio:.1f}% of threshold)\n"
                f"{context_str}\n"
                f"{'='*70}\n"
            )

    @staticmethod
    def measure_duration(func, *args, **kwargs) -> tuple:
        """
        Measure function execution duration.

        Returns:
            Tuple of (result, duration_ms)
        """
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        duration_ms = (time.perf_counter() - start_time) * 1000
        return result, duration_ms


@pytest.fixture
def performance_client(client):
    """Client fixture with performance tracking"""
    return client


class TestTier1Performance:
    """Test Tier 1 operations (<100ms SLA)"""

    def test_health_check_performance(self, performance_client):
        """Health check should complete in <100ms"""
        response, duration_ms = PerformanceAssertion.measure_duration(
            performance_client.get, "/health"
        )

        assert response.status_code in [200, 503]
        PerformanceAssertion.assert_within_threshold(
            duration_ms,
            PERFORMANCE_THRESHOLDS["health_check"],
            "Health Check",
            {"endpoint": "/health", "status": response.status_code},
        )

    def test_status_check_performance(self, performance_client):
        """Status check should complete in <100ms"""
        response, duration_ms = PerformanceAssertion.measure_duration(
            performance_client.get, "/status"
        )

        assert response.status_code == 200
        PerformanceAssertion.assert_within_threshold(
            duration_ms, PERFORMANCE_THRESHOLDS["status_check"], "Status Check"
        )

    def test_config_read_performance(self, performance_client):
        """Config read should complete in <100ms"""
        response, duration_ms = PerformanceAssertion.measure_duration(
            performance_client.get, "/api/config"
        )

        assert response.status_code == 200
        PerformanceAssertion.assert_within_threshold(
            duration_ms, PERFORMANCE_THRESHOLDS["config_read"], "Config Read"
        )

    def test_performance_metrics_performance(self, performance_client):
        """Performance metrics endpoint should be fast (<100ms)"""
        response, duration_ms = PerformanceAssertion.measure_duration(
            performance_client.get, "/api/performance/metrics"
        )

        assert response.status_code == 200
        PerformanceAssertion.assert_within_threshold(
            duration_ms, PERFORMANCE_THRESHOLDS["cache_lookup"], "Performance Metrics"
        )


class TestTier2Performance:
    """Test Tier 2 operations (<500ms SLA)"""

    def test_voice_validation_performance(self, performance_client):
        """Voice transcribe validation should complete in <500ms"""
        import base64

        # Small audio data for validation
        audio_data = b"\x00" * 1024
        audio_b64 = base64.b64encode(audio_data).decode("utf-8")

        response, duration_ms = PerformanceAssertion.measure_duration(
            performance_client.post,
            "/api/voice_transcribe",
            json={"audio_data": audio_b64, "format": "wav", "language": "en"},
        )

        # Accept any response (implementation may vary)
        assert response.status_code in [200, 400, 422, 500]

        PerformanceAssertion.assert_within_threshold(
            duration_ms,
            PERFORMANCE_THRESHOLDS["voice_validation"],
            "Voice Transcribe Validation",
            {"status": response.status_code, "data_size": len(audio_data)},
        )

    def test_cache_stats_performance(self, performance_client):
        """Cache stats should complete in <500ms"""
        response, duration_ms = PerformanceAssertion.measure_duration(
            performance_client.get, "/api/performance/cache/stats"
        )

        assert response.status_code == 200
        PerformanceAssertion.assert_within_threshold(
            duration_ms, PERFORMANCE_THRESHOLDS["cache_lookup"], "Cache Stats"
        )


class TestTier3Performance:
    """Test Tier 3 operations (<2000ms SLA)"""

    def test_ask_endpoint_performance(self, performance_client):
        """Ask endpoint should complete in <2s"""
        response, duration_ms = PerformanceAssertion.measure_duration(
            performance_client.post,
            "/api/ask",
            json={"prompt": "What is Python?", "context": ""},
        )

        # Accept various responses (may fail due to model availability or validation)
        assert response.status_code in [200, 400, 422, 500, 503]

        PerformanceAssertion.assert_within_threshold(
            duration_ms,
            PERFORMANCE_THRESHOLDS["ask_uncached"],
            "Ask Endpoint",
            {"prompt_length": 15, "status": response.status_code},
        )

    def test_performance_dashboard_performance(self, performance_client):
        """Performance dashboard should complete in <2s"""
        response, duration_ms = PerformanceAssertion.measure_duration(
            performance_client.get, "/api/performance/dashboard"
        )

        assert response.status_code in [200, 500]
        PerformanceAssertion.assert_within_threshold(
            duration_ms, PERFORMANCE_THRESHOLDS["ask_uncached"], "Performance Dashboard"
        )


class TestTier4Performance:
    """Test Tier 4 operations (<10s SLA)"""

    @pytest.mark.slow
    def test_search_endpoint_performance(self, performance_client):
        """Search endpoint should complete in <10s"""
        response, duration_ms = PerformanceAssertion.measure_duration(
            performance_client.post, "/api/search", json={"query": "test search query"}
        )

        # Accept various responses (may fail due to validation or missing data)
        assert response.status_code in [200, 400, 404, 422, 500]

        PerformanceAssertion.assert_within_threshold(
            duration_ms, PERFORMANCE_THRESHOLDS["document_indexing"], "Search Endpoint"
        )


class TestConcurrencyPerformance:
    """Test performance under concurrent load"""

    def test_concurrent_health_checks(self, performance_client):
        """Multiple concurrent health checks should maintain performance"""
        import concurrent.futures

        num_requests = 10
        results = []

        def make_request():
            start_time = time.perf_counter()
            response = performance_client.get("/health")
            duration_ms = (time.perf_counter() - start_time) * 1000
            return (response.status_code, duration_ms)

        # Make concurrent requests
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=num_requests
        ) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        # Check all requests completed successfully
        assert all(status in [200, 503] for status, _ in results)

        # Check average response time
        avg_duration = sum(duration for _, duration in results) / len(results)

        # Under concurrent load, allow 2x normal threshold
        threshold = PERFORMANCE_THRESHOLDS["health_check"] * 2
        PerformanceAssertion.assert_within_threshold(
            avg_duration,
            threshold,
            "Concurrent Health Checks (Average)",
            {"num_requests": num_requests, "max_duration": max(d for _, d in results)},
        )

    def test_concurrent_config_reads(self, performance_client):
        """Multiple concurrent config reads should maintain performance"""
        import concurrent.futures

        num_requests = 5
        results = []

        def make_request():
            start_time = time.perf_counter()
            response = performance_client.get("/api/config")
            duration_ms = (time.perf_counter() - start_time) * 1000
            return (response.status_code, duration_ms)

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=num_requests
        ) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        assert all(status == 200 for status, _ in results)

        avg_duration = sum(duration for _, duration in results) / len(results)
        threshold = PERFORMANCE_THRESHOLDS["config_read"] * 2

        PerformanceAssertion.assert_within_threshold(
            avg_duration,
            threshold,
            "Concurrent Config Reads (Average)",
            {"num_requests": num_requests},
        )


class TestMemoryPerformance:
    """Test memory usage patterns"""

    def test_memory_leak_detection(self, performance_client):
        """Ensure no memory leaks in repeated operations"""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Make 50 requests
        for _ in range(50):
            response = performance_client.get("/health")
            assert response.status_code in [200, 503]

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory should not increase by more than 50MB for 50 requests
        assert memory_increase < 50, (
            f"Potential memory leak detected: "
            f"Memory increased by {memory_increase:.2f}MB after 50 requests"
        )


class TestTracingPerformance:
    """Test new request tracing endpoints"""

    def test_tracing_summary_performance(self, performance_client):
        """Tracing summary endpoint should be fast"""
        response, duration_ms = PerformanceAssertion.measure_duration(
            performance_client.get, "/api/performance/tracing/summary"
        )

        # May fail if tracing not initialized
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            PerformanceAssertion.assert_within_threshold(
                duration_ms, PERFORMANCE_THRESHOLDS["cache_lookup"], "Tracing Summary"
            )

    def test_slow_requests_endpoint_performance(self, performance_client):
        """Slow requests endpoint should be fast"""
        response, duration_ms = PerformanceAssertion.measure_duration(
            performance_client.get, "/api/performance/tracing/slow-requests"
        )

        assert response.status_code in [200, 500]

        if response.status_code == 200:
            PerformanceAssertion.assert_within_threshold(
                duration_ms,
                PERFORMANCE_THRESHOLDS["cache_lookup"],
                "Slow Requests Query",
            )


class TestPerformanceTrends:
    """Test performance consistency over time"""

    def test_response_time_consistency(self, performance_client):
        """Response times should be consistent across multiple requests"""
        durations = []

        # Make 10 requests to the same endpoint
        for _ in range(10):
            _, duration_ms = PerformanceAssertion.measure_duration(
                performance_client.get, "/status"
            )
            durations.append(duration_ms)

        # Calculate statistics
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)

        # Max should not be more than 3x the average (consistency check)
        assert max_duration < avg_duration * 3, (
            f"Response time inconsistency detected: "
            f"Max ({max_duration:.2f}ms) is {max_duration/avg_duration:.1f}x the average ({avg_duration:.2f}ms). "
            f"Range: {min_duration:.2f}ms - {max_duration:.2f}ms"
        )

    def test_warmup_effect(self, performance_client):
        """First request may be slower (warmup), subsequent should be faster"""
        # First request (cold start)
        _, cold_duration = PerformanceAssertion.measure_duration(
            performance_client.get, "/api/config"
        )

        # Subsequent requests (warm)
        warm_durations = []
        for _ in range(5):
            _, duration_ms = PerformanceAssertion.measure_duration(
                performance_client.get, "/api/config"
            )
            warm_durations.append(duration_ms)

        avg_warm = sum(warm_durations) / len(warm_durations)

        # Warm requests should generally be faster (or at least not much slower)
        # Allow up to 2x for occasional variance
        assert avg_warm <= cold_duration * 2, (
            f"Performance degradation detected: "
            f"Warm requests ({avg_warm:.2f}ms avg) slower than cold start ({cold_duration:.2f}ms)"
        )


# Summary reporting function
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add performance test summary to pytest output"""
    if hasattr(terminalreporter.config, "workerinput"):
        return  # Skip in xdist workers

    terminalreporter.write_sep("=", "Performance Test Summary")
    terminalreporter.write_line("")
    terminalreporter.write_line("Performance SLA Thresholds:")
    for operation, threshold in PERFORMANCE_THRESHOLDS.items():
        terminalreporter.write_line(f"  {operation}: {threshold}ms")
    terminalreporter.write_line("")

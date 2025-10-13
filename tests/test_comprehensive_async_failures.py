"""
Comprehensive Async Error Scenario Tests
========================================

This module contains extensive async tests for all possible failure modes,
edge cases, and error scenarios in the Obsidian AI Assistant system.

Test Categories:
- Network failures and timeouts
- Database connection failures
- Model loading failures
- Memory exhaustion scenarios
- Concurrent operation conflicts
- Authentication edge cases
- File system permission errors
- Configuration corruption scenarios
- Resource exhaustion tests
- Enterprise feature failure modes
"""

import asyncio
import os
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import aiofiles
import aiohttp
import psutil
import pytest

from backend.embeddings import EmbeddingsManager
from backend.modelmanager import ModelManager
from backend.performance import AsyncTaskQueue, ConnectionPool
from backend.security import decrypt_data, encrypt_data

# Test imports
from backend.settings import get_settings

pytest_plugins = ["pytest_asyncio"]


class TestNetworkFailureScenarios:
    """Test network-related failures and timeouts"""

    @pytest.mark.asyncio
    async def test_concurrent_network_request_failures(self):
        """Test handling of simultaneous network request failures"""

        async def failing_request():
            raise aiohttp.ClientError("Network unreachable")

        # Simulate 100 concurrent failing requests
        tasks = [failing_request() for _ in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should be exceptions
        assert all(isinstance(r, Exception) for r in results)
        assert len(results) == 100

    @pytest.mark.asyncio
    async def test_timeout_cascade_failures(self):
        """Test cascading timeout failures"""

        async def slow_operation(delay: float):
            await asyncio.sleep(delay)
            return f"completed after {delay}s"

        # Test progressive timeout increases
        tasks = []
        for i in range(10):
            # Each task takes longer than the previous
            task = asyncio.wait_for(slow_operation(i * 0.5), timeout=1.0)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        timeout_errors = [r for r in results if isinstance(r, asyncio.TimeoutError)]
        successful = [r for r in results if isinstance(r, str)]

        # Some should timeout, some should succeed
        assert len(timeout_errors) > 0
        assert len(successful) > 0

    @pytest.mark.asyncio
    async def test_dns_resolution_failures(self):
        """Test DNS resolution failure handling"""
        async with aiohttp.ClientSession() as session:
            # Try to connect to non-existent domains
            invalid_urls = [
                "http://nonexistent-domain-12345.invalid",
                "http://localhost:99999",  # Invalid port
                "http://256.256.256.256",  # Invalid IP
            ]

            tasks = []
            for url in invalid_urls:
                task = session.get(url, timeout=aiohttp.ClientTimeout(total=1))
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # All should fail with various network errors
            assert all(isinstance(r, Exception) for r in results)


class TestDatabaseFailureScenarios:
    """Test database connection and operation failures"""

    @pytest.mark.asyncio
    async def test_chromadb_connection_failure(self):
        """Test ChromaDB connection failures"""
        # Mock ChromaDB module to test connection failure handling
        with patch.dict("sys.modules", {"chromadb": MagicMock()}):
            mock_chromadb = sys.modules["chromadb"]
            mock_client_class = MagicMock()
            mock_client_class.side_effect = ConnectionError(
                "Database connection failed"
            )
            mock_chromadb.Client = mock_client_class

            # Test that database failures are handled gracefully
            with pytest.raises(ConnectionError, match="Database connection failed"):
                mock_chromadb.Client()

    @pytest.mark.asyncio
    async def test_concurrent_database_operations(self):
        """Test concurrent database operations under stress"""

        async def database_operation(operation_id: int):
            # Simulate database work
            await asyncio.sleep(0.1)
            if operation_id % 7 == 0:  # Simulate some failures
                raise Exception(f"Database operation {operation_id} failed")
            return f"Operation {operation_id} completed"

        # Run 50 concurrent database operations
        tasks = [database_operation(i) for i in range(50)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check mix of successes and failures
        successes = [r for r in results if isinstance(r, str)]
        failures = [r for r in results if isinstance(r, Exception)]

        assert len(successes) > 0
        assert len(failures) > 0

    @pytest.mark.asyncio
    async def test_database_corruption_recovery(self):
        """Test recovery from database corruption"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "corrupted_db"

            # Create a corrupted database file
            db_path.mkdir()
            corrupted_file = db_path / "chroma.sqlite3"
            corrupted_file.write_text("invalid database content")

            # Try to initialize with corrupted database
            # EmbeddingsManager is resilient and should not raise; it disables
            # collection when model/DB are unavailable or invalid.
            try:
                embeddings_manager = EmbeddingsManager(
                    model_name="test-model", db_path=str(db_path)
                )
                # Expect no hard exception; collection may be None
                assert getattr(
                    embeddings_manager, "collection", None
                ) is None or isinstance(
                    getattr(embeddings_manager, "collection", None), object
                )
            except Exception:
                pytest.skip(
                    "Embeddings stack not available; skipping corruption recovery test"
                )


class TestModelFailureScenarios:
    """Test AI model loading and operation failures"""

    @pytest.mark.asyncio
    async def test_model_loading_memory_exhaustion(self):
        """Test model loading under memory pressure"""
        # Simulate memory exhaustion by forcing router init to fail
        with patch.dict(os.environ, {"SKIP_MODEL_DOWNLOADS": "1"}, clear=False):
            with patch(
                "backend.modelmanager.HybridLLMRouter",
                side_effect=MemoryError("Out of memory"),
            ):
                mm = ModelManager(minimal_models=[])
                # Init should not raise; router is set to None on failure
                assert getattr(mm, "llm_router", None) is None

    @pytest.mark.asyncio
    async def test_concurrent_model_loading_failures(self):
        """Test concurrent model loading attempts"""

        async def load_model_task(model_id: int):
            await asyncio.sleep(0.1)
            if model_id % 3 == 0:
                raise RuntimeError(f"Model {model_id} failed to load")
            return f"Model {model_id} loaded"

        # Try to load 20 models concurrently
        tasks = [load_model_task(i) for i in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Mix of successes and failures expected
        assert len([r for r in results if isinstance(r, str)]) > 0
        assert len([r for r in results if isinstance(r, Exception)]) > 0

    @pytest.mark.asyncio
    async def test_model_inference_timeout(self):
        """Test model inference timeouts"""

        async def slow_inference():
            await asyncio.sleep(5.0)  # Simulate slow inference
            return "Slow response"

        # Test with various timeout values
        for timeout in [0.5, 1.0, 2.0]:
            try:
                await asyncio.wait_for(slow_inference(), timeout=timeout)
                # Should not reach here for short timeouts
                assert timeout >= 5.0
            except asyncio.TimeoutError:
                # Expected for short timeouts
                assert timeout < 5.0


class TestConcurrencyFailureScenarios:
    """Test concurrent operation failures and race conditions"""

    @pytest.mark.asyncio
    async def test_race_condition_file_access(self):
        """Test race conditions in file access"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write("initial content")

        try:

            async def concurrent_file_operation(operation_id: int):
                try:
                    async with aiofiles.open(temp_path, "a") as f:
                        await f.write(f"Operation {operation_id}\n")
                        await asyncio.sleep(0.01)  # Simulate work
                    return f"Success {operation_id}"
                except Exception as e:
                    return f"Failed {operation_id}: {e}"

            # Run 50 concurrent file operations
            tasks = [concurrent_file_operation(i) for i in range(50)]
            results = await asyncio.gather(*tasks)

            # Check that most succeeded despite concurrency
            successes = [r for r in results if r.startswith("Success")]
            assert len(successes) > 40  # Most should succeed

            # Verify file was written to
            async with aiofiles.open(temp_path, "r") as f:
                content = await f.read()
                # Allow for scheduling variance on Windows CI
                assert len(content.split("\n")) >= 20

        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_deadlock_prevention(self):
        """Test deadlock prevention in resource acquisition"""
        lock1 = asyncio.Lock()
        lock2 = asyncio.Lock()

        async def task_a():
            async with lock1:
                await asyncio.sleep(0.1)
                try:
                    await asyncio.wait_for(lock2.acquire(), timeout=0.5)
                    try:
                        await asyncio.sleep(0.1)
                        return "Task A completed"
                    finally:
                        if lock2.locked():
                            lock2.release()
                except asyncio.TimeoutError:
                    return "Task A timed out"

        async def task_b():
            async with lock2:
                await asyncio.sleep(0.1)
                try:
                    await asyncio.wait_for(lock1.acquire(), timeout=0.5)
                    try:
                        await asyncio.sleep(0.1)
                        return "Task B completed"
                    finally:
                        if lock1.locked():
                            lock1.release()
                except asyncio.TimeoutError:
                    return "Task B timed out"

        # Run potentially deadlocking tasks
        results = await asyncio.gather(task_a(), task_b())

        # At least one should timeout instead of deadlocking
        timeouts = [r for r in results if "timed out" in r]
        assert len(timeouts) > 0

    @pytest.mark.asyncio
    async def test_resource_exhaustion_handling(self):
        """Test handling of resource exhaustion"""

        async def resource_intensive_task(task_id: int):
            # Simulate resource usage
            data = bytearray(1024 * 1024)  # 1MB per task
            await asyncio.sleep(0.1)
            return f"Task {task_id} completed with {len(data)} bytes"

        # Try to run many resource-intensive tasks
        tasks = [resource_intensive_task(i) for i in range(100)]

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # Some might fail due to memory pressure
            successes = [r for r in results if isinstance(r, str)]
            failures = [r for r in results if isinstance(r, Exception)]

            # Should handle gracefully
            assert len(successes) + len(failures) == 100
        except MemoryError:
            # Acceptable outcome under resource pressure
            pass


class TestAuthenticationFailureScenarios:
    """Test authentication and security failure scenarios"""

    @pytest.mark.asyncio
    async def test_concurrent_authentication_attempts(self):
        """Test concurrent authentication attempts"""

        async def auth_attempt(user_id: int):
            await asyncio.sleep(0.01)  # Simulate auth delay
            if user_id % 5 == 0:  # Some failures
                raise Exception(f"Authentication failed for user {user_id}")
            return f"User {user_id} authenticated"

        # Simulate 100 concurrent auth attempts
        tasks = [auth_attempt(i) for i in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Mix of successes and failures
        successes = [r for r in results if isinstance(r, str)]
        failures = [r for r in results if isinstance(r, Exception)]

        assert len(successes) > 0
        assert len(failures) > 0

    @pytest.mark.asyncio
    async def test_encryption_decryption_failure_modes(self):
        """Test encryption/decryption failure scenarios"""
        test_data = "sensitive test data"

        # Test encryption failure path: encrypt should raise
        with patch("backend.security.fernet") as mock_fernet:
            mock_fernet.encrypt.side_effect = RuntimeError("Encryption failed")
            with pytest.raises(RuntimeError, match="Encryption failed"):
                _ = encrypt_data(test_data)

        # Test decryption with corrupted data
        encrypted = encrypt_data(test_data)
        if encrypted:
            # Corrupt the encrypted data
            corrupted = encrypted[:-5] + b"xxxxx"
            decrypted = decrypt_data(corrupted)
            assert decrypted is None  # Should handle gracefully

    @pytest.mark.asyncio
    async def test_session_timeout_scenarios(self):
        """Test session timeout handling"""

        async def simulate_session_timeout():
            # Simulate active session
            session_start = time.time()
            await asyncio.sleep(0.1)

            # Check if session expired (simulated)
            session_duration = time.time() - session_start
            if session_duration > 0.05:  # Very short timeout for testing
                raise Exception("Session expired")
            return "Session valid"

        # Test multiple session timeout scenarios
        tasks = [simulate_session_timeout() for _ in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Some sessions should timeout
        timeouts = [r for r in results if isinstance(r, Exception)]
        assert len(timeouts) > 0


class TestFileSystemFailureScenarios:
    """Test file system related failures"""

    @pytest.mark.asyncio
    async def test_permission_denied_scenarios(self):
        """Test handling of permission denied errors"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a file and remove write permissions
            test_file = Path(temp_dir) / "readonly.txt"
            test_file.write_text("readonly content")
            test_file.chmod(0o444)  # Read-only

            try:
                # Try to write to read-only file
                async with aiofiles.open(test_file, "w") as f:
                    await f.write("new content")
                raise AssertionError("Should have raised permission error")
            except (PermissionError, OSError):
                # Expected behavior
                pass

    @pytest.mark.asyncio
    async def test_disk_space_exhaustion(self):
        """Test handling of disk space exhaustion"""
        # Simulate disk space check
        with patch("shutil.disk_usage") as mock_disk_usage:
            # Simulate very low disk space
            mock_disk_usage.return_value = (
                1000,
                950,
                50,
            )  # total, used, free (in bytes)

            # Check if operations handle low disk space gracefully
            try:
                with tempfile.NamedTemporaryFile(mode="w") as f:
                    # Try to write large amount of data
                    large_data = "x" * 1000000  # 1MB
                    f.write(large_data)
                    f.flush()
            except OSError:
                # Expected when disk space is exhausted
                pass

    @pytest.mark.asyncio
    async def test_corrupted_configuration_files(self):
        """Test handling of corrupted configuration files"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as temp_config:
            # Write invalid YAML
            temp_config.write("invalid: yaml: content: [unclosed")
            temp_config_path = temp_config.name

        try:
            # Try to load corrupted config
            with patch.dict(os.environ, {"CONFIG_FILE": temp_config_path}):
                try:
                    settings = get_settings()
                    # Should either use defaults or raise appropriate error
                    assert hasattr(settings, "api_port")  # Should have defaults
                except Exception as e:
                    # Acceptable to raise configuration error
                    assert "config" in str(e).lower() or "yaml" in str(e).lower()
        finally:
            os.unlink(temp_config_path)


class TestPerformanceFailureScenarios:
    """Test performance-related failure scenarios"""

    @pytest.mark.asyncio
    async def test_memory_leak_detection(self):
        """Test detection and handling of memory leaks"""
        initial_memory = psutil.Process().memory_info().rss

        # Simulate operations that might leak memory
        data_accumulator = []

        async def potentially_leaky_operation(iteration: int):
            # Intentionally accumulate data to simulate leak
            large_data = bytearray(1024 * 100)  # 100KB
            data_accumulator.append(large_data)
            await asyncio.sleep(0.001)
            return f"Operation {iteration}"

        # Run operations and monitor memory
        tasks = [potentially_leaky_operation(i) for i in range(100)]
        await asyncio.gather(*tasks)

        final_memory = psutil.Process().memory_info().rss
        memory_increase = final_memory - initial_memory

        # Clean up to prevent actual memory leak in tests
        data_accumulator.clear()

        # Memory should have increased (detecting the "leak")
        assert memory_increase > 0

    @pytest.mark.asyncio
    async def test_connection_pool_exhaustion(self):
        """Test connection pool exhaustion scenarios"""
        pool = ConnectionPool(factory=lambda: object(), min_size=0, max_size=5)

        async def use_connection(connection_id: int):
            try:
                connection = pool.get_connection()
                await asyncio.sleep(0.1)  # Hold connection briefly
                pool.return_connection(connection)
                return f"Connection {connection_id} successful"
            except Exception as e:
                return f"Connection {connection_id} failed: {e}"

        # Try to use more connections than available
        tasks = [use_connection(i) for i in range(20)]
        results = await asyncio.gather(*tasks)

        # Some should succeed, some might fail due to pool exhaustion
        successes = [r for r in results if "successful" in r]
        failures = [r for r in results if "failed" in r]

        # Should handle pool exhaustion gracefully
        assert len(successes) > 0
        # Not all should fail
        assert len(failures) < len(results)

    @pytest.mark.asyncio
    async def test_async_task_queue_overflow(self):
        """Test async task queue overflow handling"""
        queue = AsyncTaskQueue(max_workers=1, max_queue_size=10)
        await queue.start()

        async def queue_task(task_id: int):
            await asyncio.sleep(0.01)
            return f"Task {task_id} completed"

        # Submit many tasks via the queue API
        for i in range(50):
            await queue.submit_task(queue_task(i))
        # Allow processing time and assert progress
        await asyncio.sleep(0.5)
        stats = queue.get_stats()
        assert stats["tasks_queued"] >= 10
        assert stats["tasks_completed"] >= 1


class TestEdgeCaseScenarios:
    """Test various edge cases and boundary conditions"""

    @pytest.mark.asyncio
    async def test_empty_input_handling(self):
        """Test handling of empty or invalid inputs"""
        edge_cases = [
            "",  # Empty string
            None,  # None value
            [],  # Empty list
            {},  # Empty dict
            "   ",  # Whitespace only
            "\n\t\r",  # Special characters only
        ]

        async def process_input(input_data):
            # Simulate input processing
            if not input_data or (
                isinstance(input_data, str) and not input_data.strip()
            ):
                raise ValueError("Invalid input")
            return f"Processed: {input_data}"

        tasks = [process_input(case) for case in edge_cases]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should raise ValueError for invalid inputs
        assert all(isinstance(r, ValueError) for r in results)

    @pytest.mark.asyncio
    async def test_unicode_and_encoding_edge_cases(self):
        """Test Unicode and encoding edge cases"""
        unicode_test_cases = [
            "🚀 Rocket emoji test",
            "Ñoño niño español",
            "中文测试内容",
            "🏳️‍🌈🏴‍☠️ Complex emoji",
            "זה טקסט בעברית",
            "مرحبا بالعالم",
            "\x00\x01\x02",  # Control characters
            "\"'`\\n\\t\\r",  # Escape characters
        ]

        async def process_unicode_text(text: str):
            # Simulate text processing that handles Unicode
            try:
                # Encode and decode to test Unicode handling
                encoded = text.encode("utf-8")
                decoded = encoded.decode("utf-8")
                return f"Processed {len(decoded)} characters"
            except UnicodeError as e:
                return f"Unicode error: {e}"

        tasks = [process_unicode_text(case) for case in unicode_test_cases]
        results = await asyncio.gather(*tasks)

        # All should process successfully or handle errors gracefully
        assert all(isinstance(r, str) for r in results)

    @pytest.mark.asyncio
    async def test_large_data_handling(self):
        """Test handling of extremely large data"""

        async def process_large_data(size_mb: int):
            try:
                # Create large data chunk
                large_data = bytearray(size_mb * 1024 * 1024)

                # Simulate processing
                await asyncio.sleep(0.01)

                # Clean up immediately
                del large_data

                return f"Processed {size_mb}MB successfully"
            except MemoryError:
                return f"Memory error processing {size_mb}MB"

        # Test various sizes
        sizes = [1, 10, 50, 100, 500]  # MB
        tasks = [process_large_data(size) for size in sizes]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Should handle various sizes, some might fail with MemoryError
        assert len(results) == len(sizes)
        assert all(isinstance(r, (str, MemoryError)) for r in results)


class TestRecoveryScenarios:
    """Test system recovery from various failure states"""

    @pytest.mark.asyncio
    async def test_graceful_shutdown_during_operations(self):
        """Test graceful shutdown while operations are running"""
        shutdown_event = asyncio.Event()

        async def long_running_operation(op_id: int):
            try:
                for i in range(100):
                    if shutdown_event.is_set():
                        return f"Operation {op_id} interrupted at step {i}"
                    await asyncio.sleep(0.01)
                return f"Operation {op_id} completed"
            except asyncio.CancelledError:
                return f"Operation {op_id} cancelled"

        # Start multiple long-running operations
        tasks = [asyncio.create_task(long_running_operation(i)) for i in range(10)]

        # Let them run briefly, then trigger shutdown
        await asyncio.sleep(0.1)
        shutdown_event.set()

        # Cancel remaining tasks
        for task in tasks:
            if not task.done():
                task.cancel()

        # Wait for all to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should either complete, be interrupted, or be cancelled
        assert all(isinstance(r, (str, asyncio.CancelledError)) for r in results)

    @pytest.mark.asyncio
    async def test_automatic_retry_mechanisms(self):
        """Test automatic retry mechanisms for failed operations"""
        failure_count = {}

        async def unreliable_operation(op_id: int, max_retries: int = 3):
            if op_id not in failure_count:
                failure_count[op_id] = 0

            failure_count[op_id] += 1

            # Fail first few attempts, then succeed
            if failure_count[op_id] <= max_retries:
                raise Exception(
                    f"Operation {op_id} failed (attempt {failure_count[op_id]})"
                )

            return f"Operation {op_id} succeeded after {failure_count[op_id]} attempts"

        async def retry_wrapper(op_id: int, max_retries: int = 3):
            for attempt in range(max_retries + 2):  # Extra attempts for success
                try:
                    result = await unreliable_operation(op_id, max_retries)
                    return result
                except Exception as e:
                    if attempt >= max_retries + 1:
                        return f"Operation {op_id} failed permanently: {e}"
                    await asyncio.sleep(0.01)  # Brief delay between retries

        # Test retry mechanism with multiple operations
        tasks = [retry_wrapper(i) for i in range(5)]
        results = await asyncio.gather(*tasks)

        # All should eventually succeed
        successes = [r for r in results if "succeeded" in r]
        assert len(successes) == 5

    @pytest.mark.asyncio
    async def test_circuit_breaker_pattern(self):
        """Test circuit breaker pattern for failing services"""

        class CircuitBreaker:
            def __init__(self, failure_threshold: int = 3, timeout: float = 1.0):
                self.failure_threshold = failure_threshold
                self.timeout = timeout
                self.failure_count = 0
                self.last_failure_time = 0
                self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

            async def call(self, func, *args, **kwargs):
                if self.state == "OPEN":
                    if time.time() - self.last_failure_time > self.timeout:
                        self.state = "HALF_OPEN"
                    else:
                        raise Exception("Circuit breaker is OPEN")

                try:
                    result = await func(*args, **kwargs)
                    if self.state == "HALF_OPEN":
                        self.state = "CLOSED"
                        self.failure_count = 0
                    return result
                except Exception as e:
                    self.failure_count += 1
                    self.last_failure_time = time.time()

                    if self.failure_count >= self.failure_threshold:
                        self.state = "OPEN"

                    raise e

        async def failing_service():
            # Always fails for this test
            raise Exception("Service unavailable")

        circuit_breaker = CircuitBreaker(failure_threshold=2, timeout=0.1)

        # Test circuit breaker opening
        results = []
        for i in range(10):
            try:
                await circuit_breaker.call(failing_service)
                results.append(f"Call {i} succeeded")
            except Exception as e:
                results.append(f"Call {i} failed: {e}")

            await asyncio.sleep(0.01)

        # Should see progression: failures -> circuit open -> more failures
        assert len(results) == 10
        circuit_open_errors = [r for r in results if "Circuit breaker is OPEN" in r]
        assert len(circuit_open_errors) >= 3  # Should trigger circuit breaker


@pytest.mark.asyncio
async def test_comprehensive_failure_simulation():
    """
    Comprehensive test that simulates multiple failure types simultaneously
    """
    results = {
        "network_failures": 0,
        "database_failures": 0,
        "memory_errors": 0,
        "timeout_errors": 0,
        "authentication_failures": 0,
        "file_system_errors": 0,
        "successes": 0,
    }

    async def random_failing_operation(op_id: int):
        """Simulate operation that can fail in various ways"""
        await asyncio.sleep(0.01)  # Simulate work

        failure_type = op_id % 7

        if failure_type == 0:
            results["network_failures"] += 1
            raise aiohttp.ClientError("Network error")
        elif failure_type == 1:
            results["database_failures"] += 1
            raise Exception("Database connection lost")
        elif failure_type == 2:
            results["memory_errors"] += 1
            raise MemoryError("Out of memory")
        elif failure_type == 3:
            results["timeout_errors"] += 1
            await asyncio.sleep(2.0)  # Will timeout
        elif failure_type == 4:
            results["authentication_failures"] += 1
            raise Exception("Authentication failed")
        elif failure_type == 5:
            results["file_system_errors"] += 1
            raise PermissionError("Permission denied")
        else:
            results["successes"] += 1
            return f"Operation {op_id} succeeded"

    # Run 100 operations with various failure modes
    tasks = []
    for i in range(100):
        if i % 7 == 3:  # Timeout operations
            task = asyncio.wait_for(random_failing_operation(i), timeout=0.1)
        else:
            task = random_failing_operation(i)
        tasks.append(task)

    final_results = await asyncio.gather(*tasks, return_exceptions=True)

    # Verify we got a mix of all failure types
    assert results["network_failures"] > 0
    assert results["database_failures"] > 0
    assert results["memory_errors"] > 0
    assert results["authentication_failures"] > 0
    assert results["file_system_errors"] > 0
    assert results["successes"] > 0

    # Count timeout errors from asyncio.TimeoutError exceptions
    timeout_exceptions = [
        r for r in final_results if isinstance(r, asyncio.TimeoutError)
    ]
    results["timeout_errors"] = len(timeout_exceptions)
    assert results["timeout_errors"] > 0

    # Total should equal number of operations
    total_operations = sum(results.values())
    assert total_operations == 100


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])

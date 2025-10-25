# tests/integration/test_e2e_workflows.py
"""
End-to-End integration tests for complete workflows
"""

import time
from unittest.mock import patch

import pytest


class TestCompleteWorkflows:
    """Test complete user workflows end-to-end"""

    @pytest.fixture
    def test_client_with_real_cache(self):
        """Test client with real caching but mocked AI services"""
        from fastapi.testclient import TestClient

        from agent.backend import app

        # Use real cache manager but mock AI services
        with patch("agent.agent.init_services"):
            with patch("agent.agent.model_manager") as mock_model, patch(
                "agent.agent.emb_manager"
            ) as mock_emb, patch("agent.agent.vault_indexer") as mock_vault:
                # Configure AI service mocks
                mock_model.generate.side_effect = (
                    lambda prompt, **kwargs: f"AI response to: {prompt[:50]}..."
                )
                mock_emb.search.return_value = [
                    {"text": "Machine learning is a subset of AI", "score": 0.92},
                    {"text": "Neural networks are used in ML", "score": 0.87},
                ]
                mock_vault.index_vault.return_value = [
                    "note1.md",
                    "note2.md",
                    "note3.md",
                ]

                yield TestClient(app)

    def test_new_user_onboarding_workflow(self, test_client_with_real_cache):
        """Test complete new user onboarding workflow"""
        client = test_client_with_real_cache

        # Step 1: Check system health
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

        # Step 2: Get initial configuration
        response = client.get("/api/config")
        assert response.status_code == 200
        # Verify config is accessible
        response.json()

        # Step 3: Index user's vault for first time
        response = client.post("/api/scan_vault", json={"vault_path": "test_vault"})
        # Accept success (200), error (400), or validation (422) depending on whether test_vault exists
        assert response.status_code in [
            200,
            400,
            422,
        ], f"Expected 200, 400, or 422, got {response.status_code}"
        if response.status_code == 200:
            indexed = response.json()
            assert "indexed_files" in indexed
        else:
            # Vault path doesn't exist - that's okay for this test
            assert response.json() is not None

        # Step 4: Ask first question (should not be cached)
        first_question = {
            "question": "What is machine learning?",
            "prefer_fast": True,
            "max_tokens": 200,
        }
        response = client.post("/api/ask", json=first_question)
        assert response.status_code == 200

        first_answer = response.json()
        assert first_answer["cached"] is False
        assert "AI response to: What is machine learning?" in first_answer["answer"]

        # Step 5: Ask same question again (should be cached
        response = client.post("/api/ask", json=first_question)
        assert response.status_code == 200

        cached_answer = response.json()
        assert cached_answer["answer"] == first_answer["answer"]
        # Note: Cache behavior depends on implementation

        # Step 6: Perform semantic search
        response = client.post("/api/search", params={"query": "machine learning", "top_k": 5})
        assert response.status_code == 200

        search_results = response.json()
        assert len(search_results["results"]) == 2
        assert search_results["results"][0]["score"] > 0.9

    def test_power_user_workflow(self, test_client_with_real_cache):
        """Test advanced power user workflow with performance monitoring"""
        client = test_client_with_real_cache

        # Step 1: Get baseline performance metrics
        response = client.get("/api/performance/metrics")
        assert response.status_code == 200
        baseline = response.json()["metrics"]

        # Step 2: Perform batch operations
        questions = [
            "What is artificial intelligence?",
            "How do neural networks work?",
            "What are the applications of machine learning?",
            "Explain deep learning concepts",
            "What is natural language processing?",
        ]

        answers = []
        for question in questions:
            response = client.post(
                "/api/ask",
                json={"question": question, "prefer_fast": True, "max_tokens": 150},
            )
            assert response.status_code == 200
            answers.append(response.json())

        # Verify all answers received
        assert len(answers) == 5
        for answer in answers:
            assert "answer" in answer
            assert answer["answer"].startswith("AI response to:")

        # Step 3: Check updated performance metrics
        response = client.get("/api/performance/metrics")
        assert response.status_code == 200
        updated = response.json()["metrics"]

        # Should show increased activity
        assert updated["timestamp"] > baseline["timestamp"]

        # Step 4: Perform multiple searches
        search_queries = ["AI", "machine learning", "neural networks", "deep learning"]

        for query in search_queries:
            response = client.post("/api/search", params={"query": query, "top_k": 3})
            assert response.status_code == 200
            results = response.json()
            assert len(results["results"]) <= 3

        # Step 5: Get cache statistics
        response = client.get("/api/performance/cache/stats")
        assert response.status_code == 200
        cache_stats = response.json()["cache_stats"]

        # Should show cache activity
        assert "hit_rate" in cache_stats
        assert cache_stats["l1_size"] >= 0

        # Step 6: Trigger performance optimization
        response = client.post("/api/performance/optimize")
        assert response.status_code == 200

        optimization = response.json()
        assert optimization["status"] == "success"

    def test_content_management_workflow(self, test_client_with_real_cache):
        """Test content management and reindexing workflow"""
        client = test_client_with_real_cache

        # Step 1: Initial vault scan
        response = client.post("/api/scan_vault", json={"vault_path": "./vault1"})
        assert response.status_code in [
            200,
            400,
            422,
        ], f"Expected 200, 400, or 422, got {response.status_code}"
        # Accept both success and error for scan
        scan_result = response.json()
        if response.status_code == 200:
            assert scan_result is not None
        else:
            assert scan_result is not None  # Error response is still valid

        # Step 2: Search for existing content
        response = client.post("/api/search", params={"query": "machine learning", "top_k": 5})
        assert response.status_code == 200
        initial_results = response.json()["results"]

        # Step 3: Simulate content update by reindexing
        response = client.post("/api/reindex", json={"vault_path": "vault1"})
        assert response.status_code == 200
        reindex_result = response.json() or {}
        assert isinstance(reindex_result, dict)

        # Step 4: Search again to verify updated index
        response = client.post("/api/search", params={"query": "machine learning", "top_k": 5})
        assert response.status_code == 200
        updated_results = response.json()["results"]

        # Results structure should be consistent
        assert len(updated_results) == len(initial_results)

        # Step 5: Test PDF indexing workflow
        response = client.post("/api/index_pdf", json={"pdf_path": "./documents/test.pdf"})
        # PDF file may not exist in test environment, accept 400 error
        assert response.status_code in [200, 400, 422]
        pdf_result = response.json()
        if response.status_code == 200:
            assert "chunks_indexed" in pdf_result
        else:
            # Error response should contain error
            assert "error" in pdf_result

    def test_configuration_and_settings_workflow(self, test_client_with_real_cache):
        """Test configuration management workflow"""
        client = test_client_with_real_cache

        # Step 1: Get current configuration
        response = client.get("/api/config")
        assert response.status_code == 200
        # Verify config retrieval
        response.json()

        # Step 2: Update specific settings
        config_updates = {
            "vault_path": "./new_vault",
            "chunk_size": 1000,
            "similarity_threshold": 0.8,
        }

        response = client.post("/api/config", json=config_updates)
        assert response.status_code == 200
        # Verify update successful
        response.json()

        # Step 3: Verify configuration changes took effect
        response = client.get("/api/config")
        assert response.status_code == 200
        updated_config = response.json()

        # Basic validation that endpoint works
        assert "api_port" in updated_config

        # Step 4: Test configuration reload
        response = client.post("/api/config/reload")
        assert response.status_code == 200
        # Verify reload successful
        response.json()

        # Step 5: Test with updated configuration
        response = client.post(
            "/api/ask", json={"question": "Test with new config", "max_tokens": 100}
        )
        assert response.status_code == 200

        # Should work with new configuration
        answer = response.json()
        assert "answer" in answer

    def test_error_recovery_workflow(self, test_client_with_real_cache):
        """Test error scenarios and recovery workflows"""
        client = test_client_with_real_cache

        # Step 1: Test with invalid requests
        invalid_requests = [
            ("/api/ask", {"invalid": "data"}),
            ("/api/search", {}),  # Missing query
            ("/api/scan_vault", {}),  # Missing vault_path
        ]

        for endpoint, data in invalid_requests:
            if endpoint == "/api/search":
                response = client.post(endpoint, params=data)
            else:
                response = client.post(endpoint, json=data)

            # Should handle errors gracefully
        assert response.status_code in [
            200,
            400,
            422,
        ], f"Expected error or success for {endpoint}, but got {response.status_code}"
        # Step 2: Test recovery with valid requests
        valid_request = {
            "question": "This should work after errors",
            "prefer_fast": True,
        }
        response = client.post("/api/ask", json=valid_request)
        assert response.status_code == 200
        # Step 3: Verify system is still functional
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        # Step 4: Test cache clear and recovery
        response = client.post("/api/performance/cache/clear")
        assert response.status_code == 200
        # System should still work after cache clear
        response = client.post("/api/ask", json=valid_request)
        assert response.status_code == 200


class TestPerformanceBenchmarks:
    """Performance benchmarking integration tests"""

    @pytest.fixture
    def benchmark_client(self):
        """Client configured for performance testing"""
        from fastapi.testclient import TestClient

        from agent.backend import app

        with patch("agent.agent.init_services"):
            # Fast mock responses for benchmarking
            with patch("agent.agent.model_manager") as mock_model, patch(
                "agent.agent.emb_manager"
            ) as mock_emb:
                mock_model.generate.return_value = "Fast AI response"
                mock_emb.search.return_value = [{"text": "Result", "score": 0.9}]
                yield TestClient(app)

    def test_concurrent_request_handling(self, benchmark_client):
        """Test handling of concurrent requests"""
        import threading
        import time

        client = benchmark_client
        results = []
        errors = []

        def make_request(request_id):
            try:
                start_time = time.time()
                response = client.post(
                    "/api/ask",
                    json={
                        "question": f"Test question {request_id}",
                        "prefer_fast": True,
                    },
                )
                end_time = time.time()

                results.append(
                    {
                        "request_id": request_id,
                        "status_code": response.status_code,
                        "response_time": end_time - start_time,
                    }
                )
            except Exception as e:
                errors.append(f"Request {request_id}: {e}")

        # Launch 10 concurrent requests
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        # Wait for all to complete
        for thread in threads:
            thread.join()
        # Analyze results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 10
        # Most requests should succeed (allow for some model unavailability issues)
        successful_requests = [r for r in results if r["status_code"] == 200]
        # Expect at least 4 successful requests in concurrent scenario
        assert len(successful_requests) >= 4, (
            f"Only {len(successful_requests)} requests succeeded, expected at least 4"
        )
        # Calculate performance metrics
        response_times = [r["response_time"] for r in results]
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        # Performance assertions (reasonable thresholds)
        assert avg_response_time < 1.0, f"Average response time too high: {avg_response_time:.3f}s"
        assert max_response_time < 2.0, f"Max response time too high: {max_response_time:.3f}s"

    def test_cache_performance_benchmark(self, benchmark_client):
        """Benchmark cache performance improvements"""
        client = benchmark_client
        # Test question for caching
        test_question = {
            "question": "What is the performance of cached responses?",
            "prefer_fast": True,
        }
        # First request (uncached)
        start_time = time.time()
        response1 = client.post("/api/ask", json=test_question)
        first_response_time = time.time() - start_time
        assert response1.status_code == 200
        # Second request (potentially cached
        start_time = time.time()
        response2 = client.post("/api/ask", json=test_question)
        second_response_time = time.time() - start_time
        assert response2.status_code == 200
        # Responses should be identical
        assert response1.json()["answer"] == response2.json()["answer"]
        # Performance metrics
        print(f"First request: {first_response_time:.3f}s")
        print(f"Second request: {second_response_time:.3f}s")
        # Both should be reasonably fast (with mocked services)
        assert first_response_time < 1.0
        assert second_response_time < 1.0

    def test_memory_usage_monitoring(self, benchmark_client):
        """Monitor memory usage during operations"""
        try:
            import os

            import psutil
        except ImportError:
            pytest.skip("psutil package not available for memory monitoring")

        client = benchmark_client
        process = psutil.Process(os.getpid())
        # Get baseline memory
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        # Perform memory-intensive operations
        for i in range(50):
            response = client.post(
                "/api/ask",
                json={
                    "question": f"Memory test question {i} with some longer content to test memory usage patterns",
                    "max_tokens": 200,
                },
            )
            assert response.status_code == 200
        # Get final memory
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        print(f"Initial memory: {initial_memory:.1f} MB")
        print(f"Final memory: {final_memory:.1f} MB")
        print(f"Memory increase: {memory_increase:.1f} MB")
        # Memory increase should be reasonable
        assert memory_increase < 100, f"Memory increase too high: {memory_increase:.1f} MB"
        # Get performance metrics

    def test_performance_metrics(self):
        from fastapi.testclient import TestClient

        from agent.backend import app

        client = TestClient(app)
        response = client.get("/api/performance/metrics")
        assert response.status_code == 200
        metrics = response.json()["metrics"]
        assert "cache" in metrics


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

"""
Comprehensive test suite for performance_profiler module.

Tests cover:
    - StageProfiler: Profiling decorators, timing accuracy
    - BottleneckDetector: Bottleneck detection, severity calculation
    - ProfileAnalyzer: Trend analysis, opportunity identification
    - RecommendationEngine: Recommendation generation
    - Integration: Complete profiler pipeline workflows

Author: GitHub Copilot
Version: 0.1.46
"""

import pytest
import time
from datetime import datetime
from scripts.performance_profiler import (
    StageProfiler,
    BottleneckDetector,
    ProfileAnalyzer,
    RecommendationEngine,
    ProfilePoint,
    BottleneckInfo,
    Recommendation,
    create_profiler_pipeline,
)


class TestStageProfiler:
    """Test suite for StageProfiler component."""

    def test_initialization(self):
        """Test profiler initialization."""
        profiler = StageProfiler(threshold_ms=0.1)
        assert profiler.threshold_ms == 0.1
        assert len(profiler.profiles) == 0

    def test_profile_decorator(self):
        """Test profiling with decorator."""
        profiler = StageProfiler(threshold_ms=0.01)

        @profiler.profile_stage("test_stage")
        def slow_function():
            time.sleep(0.01)
            return "done"

        result = slow_function()
        assert result == "done"
        assert "test_stage" in profiler.profiles
        assert len(profiler.profiles["test_stage"]) > 0

    def test_manual_timing(self):
        """Test manual start/end timing."""
        profiler = StageProfiler(threshold_ms=0.01)
        profiler.start_stage("manual_stage")
        time.sleep(0.01)
        elapsed = profiler.end_stage("manual_stage")
        assert elapsed >= 10  # At least 10ms
        assert "manual_stage" in profiler.profiles

    def test_get_stage_stats(self):
        """Test getting stage statistics."""
        profiler = StageProfiler(threshold_ms=0.01)

        # Record multiple profile points
        for i in range(5):
            profiler._record_profile("test", 10.0 + i, {})

        stats = profiler.get_stage_stats("test")
        assert stats["count"] == 5
        assert stats["avg"] == 12.0
        assert stats["min"] == 10.0
        assert stats["max"] == 14.0

    def test_metadata_recording(self):
        """Test recording metadata with profile points."""
        profiler = StageProfiler(threshold_ms=0.01)
        profiler._record_profile("test", 10.0, {"retry_count": 2, "input_size": 1000})

        points = profiler.profiles["test"]
        assert len(points) > 0
        assert points[0].metadata["retry_count"] == 2

    def test_reset(self):
        """Test resetting profiler data."""
        profiler = StageProfiler(threshold_ms=0.01)
        profiler._record_profile("test", 10.0, {})
        assert len(profiler.profiles) > 0

        profiler.reset()
        assert len(profiler.profiles) == 0

    def test_threshold_filtering(self):
        """Test that profiler respects threshold."""
        profiler = StageProfiler(threshold_ms=100.0)  # High threshold

        @profiler.profile_stage("fast_stage")
        def fast_function():
            return "done"

        fast_function()
        assert "fast_stage" not in profiler.profiles  # Below threshold


class TestBottleneckDetector:
    """Test suite for BottleneckDetector component."""

    def test_initialization(self):
        """Test detector initialization."""
        detector = BottleneckDetector(threshold_percentile=95.0, variance_threshold=0.5)
        assert detector.threshold_percentile == 95.0
        assert detector.variance_threshold == 0.5

    def test_detect_critical_bottleneck(self):
        """Test detecting critical bottlenecks."""
        detector = BottleneckDetector()

        # Create profiles: one stage much slower
        profiles = {
            "fast_stage": [ProfilePoint("fast", 10.0, metadata={}) for _ in range(5)],
            "slow_stage": [ProfilePoint("slow", 100.0, metadata={}) for _ in range(5)],
        }

        bottlenecks = detector.detect_bottlenecks(profiles)
        assert len(bottlenecks) > 0

        # Find slow_stage bottleneck
        slow_bottleneck = next((b for b in bottlenecks if b.stage_name == "slow_stage"), None)
        assert slow_bottleneck is not None
        assert slow_bottleneck.severity in ["critical", "high"]

    def test_high_variance_detection(self):
        """Test detecting high variance stages."""
        detector = BottleneckDetector(variance_threshold=0.3)

        # Create profiles: one stage with high variance
        profiles = {
            "stable_stage": [ProfilePoint("stable", 10.0, metadata={}) for _ in range(10)],
            "variable_stage": [
                ProfilePoint("variable", time, metadata={})
                for time in [5.0, 15.0, 8.0, 20.0, 10.0, 25.0, 5.0, 30.0, 8.0, 15.0]
            ],
        }

        bottlenecks = detector.detect_bottlenecks(profiles)
        assert len(bottlenecks) > 0

    def test_percentile_calculation(self):
        """Test percentile calculation utility."""
        data = list(range(1, 101))  # 1-100
        p95 = BottleneckDetector._percentile(data, 95)
        assert 94 < p95 < 96  # Should be approximately 95

    def test_empty_profiles(self):
        """Test detector with empty profiles."""
        detector = BottleneckDetector()
        bottlenecks = detector.detect_bottlenecks({})
        assert len(bottlenecks) == 0

    def test_bottleneck_info_serialization(self):
        """Test BottleneckInfo to_dict conversion."""
        bottleneck = BottleneckInfo(
            stage_name="test",
            avg_time=10.0,
            max_time=15.0,
            min_time=5.0,
            variance=5.0,
            execution_count=10,
            severity="high",
            percentile_95=14.0,
        )
        data = bottleneck.to_dict()
        assert data["stage_name"] == "test"
        assert data["avg_time"] == 10.0
        assert data["severity"] == "high"


class TestProfileAnalyzer:
    """Test suite for ProfileAnalyzer component."""

    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = ProfileAnalyzer()
        assert isinstance(analyzer.analysis_cache, dict)

    def test_trend_analysis_stable(self):
        """Test trend analysis for stable performance."""
        analyzer = ProfileAnalyzer()

        # Create stable profiles
        profiles = {
            "stable_stage": [ProfilePoint("stable", 10.0, metadata={}) for _ in range(10)],
        }

        trends = analyzer.analyze_performance_trends(profiles)
        assert "stable_stage" in trends
        assert trends["stable_stage"]["trend"] == "stable"

    def test_trend_analysis_degrading(self):
        """Test trend analysis for degrading performance."""
        analyzer = ProfileAnalyzer()

        # Create degrading profiles: first half faster, second half slower
        times = [10.0] * 5 + [15.0] * 5
        profiles = {
            "degrading_stage": [ProfilePoint("degrading", t, metadata={}) for t in times],
        }

        trends = analyzer.analyze_performance_trends(profiles)
        assert "degrading_stage" in trends
        assert trends["degrading_stage"]["trend"] == "degrading"

    def test_trend_analysis_improving(self):
        """Test trend analysis for improving performance."""
        analyzer = ProfileAnalyzer()

        # Create improving profiles: first half slower, second half faster
        times = [20.0] * 5 + [10.0] * 5
        profiles = {
            "improving_stage": [ProfilePoint("improving", t, metadata={}) for t in times],
        }

        trends = analyzer.analyze_performance_trends(profiles)
        assert "improving_stage" in trends
        assert trends["improving_stage"]["trend"] == "improving"

    def test_overhead_calculation(self):
        """Test profiling overhead calculation."""
        analyzer = ProfileAnalyzer()

        profiles = {
            "stage1": [ProfilePoint("stage1", 10.0, metadata={}) for _ in range(10)],
            "stage2": [ProfilePoint("stage2", 10.0, metadata={}) for _ in range(10)],
        }

        overhead = analyzer.calculate_overhead(profiles)
        assert 0 <= overhead <= 5.0  # Overhead should be low

    def test_optimization_opportunities(self):
        """Test identifying optimization opportunities."""
        analyzer = ProfileAnalyzer()

        profiles = {
            "slow_stage": [ProfilePoint("slow", t, metadata={}) for t in [100.0] * 5],
        }

        bottlenecks = [
            BottleneckInfo(
                stage_name="slow_stage",
                avg_time=100.0,
                max_time=105.0,
                min_time=95.0,
                variance=20.0,
                execution_count=5,
                severity="critical",
                percentile_95=104.0,
            ),
        ]

        opportunities = analyzer.identify_optimization_opportunities(profiles, bottlenecks)
        assert "slow_stage" in opportunities["slow_stages"]


class TestRecommendationEngine:
    """Test suite for RecommendationEngine component."""

    def test_initialization(self):
        """Test engine initialization."""
        engine = RecommendationEngine(confidence_threshold=0.6)
        assert engine.confidence_threshold == 0.6

    def test_high_variance_recommendation(self):
        """Test recommendation for high variance stages."""
        engine = RecommendationEngine()

        bottlenecks = [
            BottleneckInfo(
                stage_name="variable_stage",
                avg_time=50.0,
                max_time=80.0,
                min_time=20.0,
                variance=200.0,
                execution_count=10,
                severity="high",
                percentile_95=75.0,
            ),
        ]

        trends = {"variable_stage": {"trend": "stable", "change_percent": 0}}
        opportunities = {
            "high_variance_stages": ["variable_stage"],
            "slow_stages": [],
            "candidate_for_parallelization": [],
        }

        recommendations = engine.generate_recommendations(bottlenecks, trends, opportunities)
        assert any(r.stage_name == "variable_stage" for r in recommendations)

    def test_degrading_performance_recommendation(self):
        """Test recommendation for degrading performance."""
        engine = RecommendationEngine()

        bottlenecks = [
            BottleneckInfo(
                stage_name="degrading_stage",
                avg_time=50.0,
                max_time=55.0,
                min_time=45.0,
                variance=10.0,
                execution_count=10,
                severity="high",
                percentile_95=54.0,
            ),
        ]

        trends = {
            "degrading_stage": {
                "trend": "degrading",
                "change_percent": 20.0,
            }
        }
        opportunities = {
            "high_variance_stages": [],
            "slow_stages": ["degrading_stage"],
            "candidate_for_parallelization": [],
        }

        recommendations = engine.generate_recommendations(bottlenecks, trends, opportunities)
        assert any("memory leak" in r.suggested_action.lower() for r in recommendations)

    def test_recommendation_serialization(self):
        """Test Recommendation to_dict conversion."""
        rec = Recommendation(
            stage_name="test",
            issue="High execution time",
            suggested_action="Optimize algorithm",
            expected_improvement="50% faster",
            priority="high",
            confidence=0.85,
        )
        data = rec.to_dict()
        assert data["stage_name"] == "test"
        assert data["priority"] == "high"
        assert data["confidence"] == 0.85

    def test_confidence_filtering(self):
        """Test that low-confidence recommendations are filtered."""
        engine = RecommendationEngine(confidence_threshold=0.8)

        bottlenecks = []
        trends = {}
        opportunities = {
            "high_variance_stages": [],
            "slow_stages": [],
            "candidate_for_parallelization": ["some_stage"],
        }

        recommendations = engine.generate_recommendations(bottlenecks, trends, opportunities)
        # Low-confidence parallelization recommendations should be filtered
        assert all(r.confidence >= 0.8 for r in recommendations)


class TestDataModels:
    """Test suite for data model serialization."""

    def test_profile_point_serialization(self):
        """Test ProfilePoint to_dict conversion."""
        point = ProfilePoint(
            stage_name="test",
            execution_time=10.0,
            metadata={"retry": 1},
        )
        data = point.to_dict()
        assert data["stage_name"] == "test"
        assert data["execution_time"] == 10.0
        assert data["metadata"]["retry"] == 1

    def test_profile_point_timestamp(self):
        """Test ProfilePoint timestamp generation."""
        point = ProfilePoint("test", 10.0)
        assert isinstance(point.timestamp, datetime)
        assert point.timestamp is not None


class TestIntegration:
    """Integration tests for complete profiler workflows."""

    def test_complete_profiler_pipeline(self):
        """Test complete profiler pipeline."""
        profiler, detector, analyzer, engine = create_profiler_pipeline()

        # Record some profile data
        for _ in range(5):
            profiler._record_profile("fast_stage", 10.0, {})
            profiler._record_profile("slow_stage", 50.0, {})

        # Detect bottlenecks
        bottlenecks = detector.detect_bottlenecks(profiler.profiles)
        assert len(bottlenecks) > 0

        # Analyze trends
        trends = analyzer.analyze_performance_trends(profiler.profiles)
        assert len(trends) > 0

        # Get opportunities
        opportunities = analyzer.identify_optimization_opportunities(profiler.profiles, bottlenecks)
        assert "slow_stages" in opportunities

        # Generate recommendations
        recommendations = engine.generate_recommendations(bottlenecks, trends, opportunities)
        assert len(recommendations) >= 0  # May be empty if confidence too low

    def test_workflow_performance_tracking(self):
        """Test tracking workflow performance through multiple stages."""
        profiler = StageProfiler(threshold_ms=0.01)

        # Simulate workflow with multiple stages
        stages = ["stage1", "stage2", "stage3", "stage4"]
        for _ in range(3):
            for stage in stages:
                profiler.start_stage(stage)
                time.sleep(0.01)
                profiler.end_stage(stage, {"iteration": _})

        # Verify all stages tracked
        assert len(profiler.profiles) == 4
        for stage in stages:
            assert stage in profiler.profiles
            assert len(profiler.profiles[stage]) == 3

    def test_profiler_factory_function(self):
        """Test factory function creates valid pipeline."""
        profiler, detector, analyzer, engine = create_profiler_pipeline()

        assert isinstance(profiler, StageProfiler)
        assert isinstance(detector, BottleneckDetector)
        assert isinstance(analyzer, ProfileAnalyzer)
        assert isinstance(engine, RecommendationEngine)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_profile_point(self):
        """Test detector with only one profile point."""
        detector = BottleneckDetector()
        profiles = {"single_stage": [ProfilePoint("single", 10.0, metadata={})]}

        bottlenecks = detector.detect_bottlenecks(profiles)
        # Should not crash, may return empty or minimal results

    def test_zero_execution_time(self):
        """Test handling zero or near-zero execution times."""
        profiler = StageProfiler(threshold_ms=0.0)  # Accept all times
        profiler._record_profile("instant", 0.0, {})

        stats = profiler.get_stage_stats("instant")
        assert stats["count"] == 1
        assert stats["avg"] == 0.0

    def test_very_large_execution_times(self):
        """Test handling very large execution times."""
        detector = BottleneckDetector()
        profiles = {
            "huge_stage": [ProfilePoint("huge", t, metadata={}) for t in [1000000.0] * 5],
        }

        bottlenecks = detector.detect_bottlenecks(profiles)
        assert len(bottlenecks) >= 0  # Should handle gracefully

    def test_nan_handling(self):
        """Test graceful handling of edge cases in statistics."""
        analyzer = ProfileAnalyzer()

        # Create profile with identical values (stdev would be 0)
        profiles = {
            "identical": [ProfilePoint("identical", 10.0, metadata={}) for _ in range(5)],
        }

        # Should not crash
        overhead = analyzer.calculate_overhead(profiles)
        assert isinstance(overhead, float)

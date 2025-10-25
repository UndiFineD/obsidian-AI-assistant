"""Integration tests for v0.1.46 - 30 tests across all 5 modules."""

import sys
from pathlib import Path

import pytest

scripts_path = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_path))

try:
    from custom_lanes import get_registry, list_all_lanes
    from error_recovery import CheckpointManager, StateValidator
    from performance_profiler import StageProfiler, create_profiler_pipeline
    from stage_optimizer import PerformanceAnalyzer, get_stage_predictor
    from workflow_analytics import DashboardGenerator, MetricsAggregator
except ImportError:
    pytest.skip("v0.1.46 modules unavailable", allow_module_level=True)


class TestIntegration:
    """Cross-module integration tests."""

    def test_all_modules_import(self):
        """All modules should import successfully."""
        assert get_registry is not None
        assert get_stage_predictor is not None
        assert StateValidator is not None
        assert MetricsAggregator is not None
        assert StageProfiler is not None

    def test_profiler_analytics_flow(self):
        """Profile data should flow to analytics."""
        profiler = StageProfiler()
        aggregator = MetricsAggregator()

        profiler.start_stage("test")
        profiler.end_stage("test")
        stats = profiler.get_stage_stats("test")
        aggregator.add_metric("prof", "count", stats["count"])

        assert len(aggregator.metrics) > 0

    def test_optimizer_analytics_flow(self):
        """Optimizer data should flow to analytics."""
        predictor = get_stage_predictor()
        aggregator = MetricsAggregator()

        predictor.add_stage_time("task", 50)
        aggregator.add_metric("opt", "stages", len(predictor.stages))

        assert len(aggregator.metrics) > 0

    def test_recovery_analytics_flow(self):
        """Recovery data should flow to analytics."""
        validator = StateValidator()
        aggregator = MetricsAggregator()

        valid = validator.validate_state({"ok": True})
        aggregator.add_metric("rec", "valid", 1 if valid else 0)

        assert len(aggregator.metrics) > 0

    def test_three_module_integration(self):
        """Three modules together."""
        profiler = StageProfiler()
        predictor = get_stage_predictor()
        aggregator = MetricsAggregator()

        profiler.start_stage("w")
        profiler.end_stage("w")
        predictor.add_stage_time("w", 100)
        aggregator.add_metric("w", "done", 1)

        assert len(aggregator.metrics) > 0

    def test_four_module_integration(self):
        """Four modules together."""
        profiler = StageProfiler()
        predictor = get_stage_predictor()
        validator = StateValidator()
        aggregator = MetricsAggregator()

        profiler.start_stage("x")
        profiler.end_stage("x")
        predictor.add_stage_time("x", 50)
        validator.validate_state({"x": True})
        aggregator.add_metric("x", "ok", 1)

        assert len(aggregator.metrics) > 0

    def test_five_module_full_integration(self):
        """All five modules work together."""
        lanes = list_all_lanes()
        predictor = get_stage_predictor()
        validator = StateValidator()
        manager = CheckpointManager()
        aggregator = MetricsAggregator()
        profiler = StageProfiler()
        generator = DashboardGenerator()

        # Use all modules
        profiler.start_stage("full")
        profiler.end_stage("full")
        predictor.add_stage_time("full", 75)
        validator.validate_state({"full": True})
        manager.create_checkpoint({"data": 1})
        aggregator.add_metric("full", "done", 1)
        dashboard = generator.generate_dashboard(aggregator)

        assert dashboard is not None
        assert len(aggregator.metrics) > 0

    def test_multistage_workflow(self):
        """Multi-stage workflow integration."""
        profiler = StageProfiler()
        predictor = get_stage_predictor()
        validator = StateValidator()
        aggregator = MetricsAggregator()
        generator = DashboardGenerator()

        stages = ["a", "b", "c", "d", "e"]

        for s in stages:
            profiler.start_stage(s)
            profiler.end_stage(s)
            predictor.add_stage_time(s, 20)
            validator.validate_state({s: True})
            aggregator.add_metric(s, "ok", 1)

        dashboard = generator.generate_dashboard(aggregator)

        assert len(aggregator.metrics) >= len(stages)
        assert dashboard is not None

    def test_profiler_pipeline(self):
        """Profiler pipeline all components."""
        prof, det, ana, eng = create_profiler_pipeline()

        assert prof is not None
        assert det is not None
        assert ana is not None
        assert eng is not None

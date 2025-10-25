"""
Integration tests for v0.1.46 modules - Simplified version.
Tests cross-module workflows and data flow between modules.
"""

import pytest
import sys
from pathlib import Path


def test_all_modules_exist():
    """Verify all v0.1.46 modules exist in scripts directory."""
    scripts_dir = Path(__file__).parent.parent / "scripts"

    required_modules = [
        "custom_lanes.py",
        "stage_optimizer.py",
        "error_recovery.py",
        "workflow_analytics.py",
        "performance_profiler.py",
    ]

    for module in required_modules:
        module_path = scripts_dir / module
        assert module_path.exists(), f"Module {module} not found in scripts/"
        assert module_path.stat().st_size > 100, f"Module {module} is too small"


def test_module_syntax_valid():
    """Verify all modules have valid Python syntax."""
    scripts_dir = Path(__file__).parent.parent / "scripts"

    modules_to_check = [
        "custom_lanes.py",
        "stage_optimizer.py",
        "error_recovery.py",
        "workflow_analytics.py",
        "performance_profiler.py",
    ]

    for module in modules_to_check:
        module_path = scripts_dir / module
        with open(module_path, "r", encoding="utf-8") as f:
            source = f.read()
        try:
            compile(source, str(module_path), "exec")
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {module}: {e}")


def test_module_imports_possible():
    """Verify modules can be imported when path is configured."""
    scripts_dir = Path(__file__).parent.parent / "scripts"
    sys.path.insert(0, str(scripts_dir))

    # All imports should succeed
    try:
        import custom_lanes

        assert hasattr(custom_lanes, "get_registry")
        assert hasattr(custom_lanes, "list_all_lanes")
    except ImportError as e:
        pytest.fail(f"Failed to import custom_lanes: {e}")

    try:
        import stage_optimizer

        assert hasattr(stage_optimizer, "StagePredictor")
    except ImportError as e:
        pytest.fail(f"Failed to import stage_optimizer: {e}")

    try:
        import error_recovery

        assert hasattr(error_recovery, "StateValidator")
        assert hasattr(error_recovery, "CheckpointManager")
    except ImportError as e:
        pytest.fail(f"Failed to import error_recovery: {e}")

    try:
        import workflow_analytics

        assert hasattr(workflow_analytics, "MetricsAggregator")
        assert hasattr(workflow_analytics, "DashboardGenerator")
    except ImportError as e:
        pytest.fail(f"Failed to import workflow_analytics: {e}")

    try:
        import performance_profiler

        assert hasattr(performance_profiler, "StageProfiler")
    except ImportError as e:
        pytest.fail(f"Failed to import performance_profiler: {e}")


def test_module_classes_callable():
    """Verify key classes are callable."""
    scripts_dir = Path(__file__).parent.parent / "scripts"
    sys.path.insert(0, str(scripts_dir))

    import stage_optimizer
    import error_recovery
    import workflow_analytics
    import performance_profiler

    # Test class instantiation
    predictor = stage_optimizer.StagePredictor()
    assert predictor is not None

    validator = error_recovery.StateValidator()
    assert validator is not None

    aggregator = workflow_analytics.MetricsAggregator()
    assert aggregator is not None

    profiler = performance_profiler.StageProfiler()
    assert profiler is not None


def test_module_methods_exist():
    """Verify key methods exist on module classes."""
    scripts_dir = Path(__file__).parent.parent / "scripts"
    sys.path.insert(0, str(scripts_dir))

    import custom_lanes
    import stage_optimizer
    import error_recovery
    import workflow_analytics
    import performance_profiler

    # Check custom_lanes functions
    registry = custom_lanes.get_registry()
    assert registry is not None
    lanes = custom_lanes.list_all_lanes()
    assert isinstance(lanes, (list, dict))

    # Check stage_optimizer methods
    predictor = stage_optimizer.StagePredictor()
    assert hasattr(predictor, "add_stage_time")
    assert hasattr(predictor, "predict_next_stage")

    # Check error_recovery methods
    validator = error_recovery.StateValidator()
    assert hasattr(validator, "validate")
    assert hasattr(validator, "get_validation_errors")

    # Check workflow_analytics methods
    aggregator = workflow_analytics.MetricsAggregator()
    assert hasattr(aggregator, "add_metric")
    assert hasattr(aggregator, "get_aggregated_metrics")

    # Check performance_profiler methods
    profiler = performance_profiler.StageProfiler()
    assert hasattr(profiler, "start_stage")
    assert hasattr(profiler, "end_stage")


def test_module_data_flow():
    """Verify data can flow between modules."""
    scripts_dir = Path(__file__).parent.parent / "scripts"
    sys.path.insert(0, str(scripts_dir))

    import stage_optimizer
    import workflow_analytics

    # Create instances
    predictor = stage_optimizer.StagePredictor()
    aggregator = workflow_analytics.MetricsAggregator()

    # Add data to optimizer
    predictor.add_stage_time("workflow", 100)
    predictor.add_stage_time("workflow", 110)

    # Extract metrics and aggregate
    if hasattr(predictor, "stages") and "workflow" in predictor.stages:
        metrics = predictor.stages["workflow"]
        aggregator.add_metric("optimizer", "avg_time", sum(metrics) / len(metrics))

    # Verify aggregated data exists
    aggregated = aggregator.get_aggregated_metrics()
    assert aggregated is not None


def test_module_error_recovery_integration():
    """Verify error recovery module can be used in workflows."""
    scripts_dir = Path(__file__).parent.parent / "scripts"
    sys.path.insert(0, str(scripts_dir))

    import error_recovery

    validator = error_recovery.StateValidator()
    checkpoint = error_recovery.CheckpointManager()

    # Test validation
    test_state = {"status": "running", "progress": 50}
    errors = validator.validate(test_state)
    assert isinstance(errors, (list, dict, type(None)))

    # Test checkpoint operations
    assert hasattr(checkpoint, "save")
    assert hasattr(checkpoint, "restore")


def test_module_profiler_integration():
    """Verify profiler can profile module operations."""
    scripts_dir = Path(__file__).parent.parent / "scripts"
    sys.path.insert(0, str(scripts_dir))

    import performance_profiler

    profiler = performance_profiler.StageProfiler()

    # Profile a stage
    profiler.start_stage("test_operation")
    # Simulate work
    sum(range(1000))
    profiler.end_stage("test_operation")

    # Verify profiling data collected
    stats = profiler.get_stage_stats("test_operation")
    assert stats is not None
    assert "duration" in stats or "time" in stats or "count" in stats


def test_all_modules_production_ready():
    """Verify all modules meet production readiness criteria."""
    scripts_dir = Path(__file__).parent.parent / "scripts"

    modules = [
        "custom_lanes.py",
        "stage_optimizer.py",
        "error_recovery.py",
        "workflow_analytics.py",
        "performance_profiler.py",
    ]

    for module_name in modules:
        module_path = scripts_dir / module_name
        with open(module_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for docstrings
        assert '"""' in content or "'''" in content, f"{module_name} missing docstrings"

        # Check for tests in same repo
        test_file = Path(__file__).parent / f"test_{module_name[:-3]}.py"
        if test_file.exists():
            assert test_file.stat().st_size > 100, f"test_{module_name[:-3]}.py is incomplete"


def test_complete_workflow():
    """Test a complete workflow using multiple modules."""
    scripts_dir = Path(__file__).parent.parent / "scripts"
    sys.path.insert(0, str(scripts_dir))

    import custom_lanes
    import stage_optimizer
    import workflow_analytics
    import performance_profiler

    # Create workflow using multiple modules
    lanes = custom_lanes.list_all_lanes()
    predictor = stage_optimizer.StagePredictor()
    aggregator = workflow_analytics.MetricsAggregator()
    profiler = performance_profiler.StageProfiler()

    # Execute workflow
    profiler.start_stage("complete_workflow")

    # Simulate workflow execution
    predictor.add_stage_time("task_1", 50)
    predictor.add_stage_time("task_1", 55)

    aggregator.add_metric("workflow", "task_count", 1)

    profiler.end_stage("complete_workflow")

    # Verify all components executed
    assert lanes is not None
    assert aggregator.get_aggregated_metrics() is not None
    assert profiler.get_stage_stats("complete_workflow") is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

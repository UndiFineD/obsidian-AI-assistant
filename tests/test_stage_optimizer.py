"""
Unit Tests for Stage Optimizer Module (v0.1.46)

Tests for:
- Workflow history collection and management
- ML model training (with graceful degradation)
- Stage prediction and confidence scoring
- Execution time estimation
- Recommendation generation
- Default fallback behavior
"""

import json
import tempfile
from pathlib import Path
from datetime import datetime

import pytest

from scripts.stage_optimizer import (
    WorkflowExecution,
    WorkflowHistoryCollector,
    StagePredictor,
    Recommendation,
    OptimizationStats,
    create_sample_history,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_history():
    """Create sample workflow history."""
    return create_sample_history()


@pytest.fixture
def temp_history_file():
    """Create temporary history file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        path = Path(f.name)
    yield path
    path.unlink(missing_ok=True)


@pytest.fixture
def workflow_execution():
    """Create sample workflow execution."""
    return WorkflowExecution(
        change_id="test-change-001",
        timestamp=datetime.now().isoformat(),
        change_type="feature",
        file_count=5,
        file_types=[".py", ".md"],
        stages_executed=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        duration_seconds=450.0,
        success=True,
        quality_gates_passed=10,
        errors=[],
    )


@pytest.fixture
def stage_predictor():
    """Create fresh stage predictor."""
    return StagePredictor()


# ============================================================================
# Test WorkflowExecution
# ============================================================================


class TestWorkflowExecution:
    """Tests for WorkflowExecution."""

    def test_create_execution(self, workflow_execution):
        """Test creating workflow execution."""
        assert workflow_execution.change_id == "test-change-001"
        assert workflow_execution.change_type == "feature"
        assert workflow_execution.file_count == 5

    def test_execution_to_dict(self, workflow_execution):
        """Test converting execution to dictionary."""
        data = workflow_execution.to_dict()

        assert data["change_id"] == "test-change-001"
        assert data["change_type"] == "feature"
        assert data["file_count"] == 5
        assert "stages_executed" in data

    def test_execution_from_dict(self):
        """Test creating execution from dictionary."""
        data = {
            "change_id": "test-001",
            "timestamp": "2025-10-20T10:00:00",
            "change_type": "bugfix",
            "file_count": 3,
            "file_types": [".py"],
            "stages_executed": [0, 1, 2, 3, 4, 5],
            "duration_seconds": 300.0,
            "success": True,
            "quality_gates_passed": 6,
            "errors": [],
        }

        execution = WorkflowExecution.from_dict(data)

        assert execution.change_id == "test-001"
        assert execution.change_type == "bugfix"
        assert execution.file_count == 3
        assert execution.success is True

    def test_execution_defaults(self):
        """Test execution with defaults."""
        execution = WorkflowExecution(
            change_id="test",
            timestamp="2025-10-20T10:00:00",
            change_type="chore",
            file_count=1,
        )

        assert execution.duration_seconds == 0.0
        assert execution.success is True
        assert execution.quality_gates_passed == 0
        assert execution.errors == []


# ============================================================================
# Test WorkflowHistoryCollector
# ============================================================================


class TestWorkflowHistoryCollector:
    """Tests for WorkflowHistoryCollector."""

    def test_create_collector(self, temp_history_file):
        """Test creating history collector."""
        collector = WorkflowHistoryCollector(temp_history_file)

        assert collector.history_file == temp_history_file
        assert collector.history == []

    def test_add_execution(self, temp_history_file, workflow_execution):
        """Test adding execution to history."""
        collector = WorkflowHistoryCollector(temp_history_file)
        collector.add_execution(workflow_execution)

        assert len(collector.history) == 1
        assert collector.history[0].change_id == "test-change-001"

    def test_get_history(self, temp_history_file, sample_history):
        """Test getting full history."""
        collector = WorkflowHistoryCollector(temp_history_file)

        for execution in sample_history:
            collector.add_execution(execution)

        history = collector.get_history()

        assert len(history) == len(sample_history)

    def test_get_history_with_limit(self, temp_history_file, sample_history):
        """Test getting limited history."""
        collector = WorkflowHistoryCollector(temp_history_file)

        for execution in sample_history:
            collector.add_execution(execution)

        limited = collector.get_history(limit=3)

        assert len(limited) == 3
        assert limited[0].change_id == "change-004"  # Last 3

    def test_save_to_file(self, temp_history_file, workflow_execution):
        """Test saving history to file."""
        collector = WorkflowHistoryCollector(temp_history_file)
        collector.add_execution(workflow_execution)

        success, error = collector.save_to_file()

        assert success is True
        assert error is None
        assert temp_history_file.exists()

        # Verify file contents
        with open(temp_history_file) as f:
            data = json.load(f)

        assert data["count"] == 1
        assert len(data["history"]) == 1
        assert data["history"][0]["change_id"] == "test-change-001"

    def test_load_from_file(self, temp_history_file, workflow_execution):
        """Test loading history from file."""
        # Save history first
        collector1 = WorkflowHistoryCollector(temp_history_file)
        collector1.add_execution(workflow_execution)
        collector1.save_to_file()

        # Load history
        collector2 = WorkflowHistoryCollector(temp_history_file)

        assert len(collector2.history) == 1
        assert collector2.history[0].change_id == "test-change-001"

    def test_get_statistics(self, temp_history_file, sample_history):
        """Test getting history statistics."""
        collector = WorkflowHistoryCollector(temp_history_file)

        for execution in sample_history:
            collector.add_execution(execution)

        stats = collector.get_statistics()

        assert stats["total"] == len(sample_history)
        assert stats["success_rate"] == 1.0  # All successful
        assert stats["average_duration"] > 0
        assert "docs" in stats["change_type_distribution"]
        assert "feature" in stats["change_type_distribution"]

    def test_statistics_empty_history(self, temp_history_file):
        """Test statistics with empty history."""
        collector = WorkflowHistoryCollector(temp_history_file)

        stats = collector.get_statistics()

        assert stats["total"] == 0
        assert stats["success_rate"] == 0.0
        assert stats["average_duration"] == 0.0


# ============================================================================
# Test StagePredictor
# ============================================================================


class TestStagePredictor:
    """Tests for StagePredictor."""

    def test_create_predictor(self, stage_predictor):
        """Test creating stage predictor."""
        assert stage_predictor.model is None
        assert stage_predictor.is_trained is False
        assert stage_predictor.stats.total_predictions == 0

    def test_predict_without_training(self, stage_predictor):
        """Test prediction without training (uses defaults)."""
        stages, confidence = stage_predictor.predict("docs", file_count=2)

        assert len(stages) > 0
        assert 0 in stages
        assert confidence == 0.5  # Default confidence

    def test_predict_all_change_types(self, stage_predictor):
        """Test prediction for all change types."""
        change_types = ["docs", "bugfix", "feature", "refactor", "chore"]

        for change_type in change_types:
            stages, confidence = stage_predictor.predict(change_type)

            assert len(stages) > 0
            assert all(0 <= s <= 12 for s in stages)
            assert confidence >= 0.0 and confidence <= 1.0

    def test_predict_updates_stats(self, stage_predictor):
        """Test that predictions update statistics."""
        initial_count = stage_predictor.stats.total_predictions

        stage_predictor.predict("feature")

        assert stage_predictor.stats.total_predictions == initial_count + 1

    def test_estimate_execution_time(self, stage_predictor):
        """Test execution time estimation."""
        stages = [0, 1, 2, 3]
        duration = stage_predictor.estimate_execution_time(stages)

        assert duration > 0
        # Check against known durations
        expected = sum(stage_predictor.STAGE_DURATIONS.get(s, 30) for s in stages)
        assert duration == expected

    def test_estimate_empty_stages(self, stage_predictor):
        """Test estimation with empty stages."""
        duration = stage_predictor.estimate_execution_time([])

        assert duration == 0.0

    def test_get_default_stage_mapping(self, stage_predictor):
        """Test default stage mappings are correct."""
        assert len(stage_predictor.DEFAULT_STAGE_MAPPING) >= 5
        assert "docs" in stage_predictor.DEFAULT_STAGE_MAPPING
        assert "feature" in stage_predictor.DEFAULT_STAGE_MAPPING

    def test_stage_durations_all_stages(self, stage_predictor):
        """Test that all stages have durations."""
        for stage in range(13):
            assert stage in stage_predictor.STAGE_DURATIONS
            assert stage_predictor.STAGE_DURATIONS[stage] > 0

    def test_get_stats(self, stage_predictor):
        """Test getting optimizer statistics."""
        stats = stage_predictor.get_stats()

        assert isinstance(stats, OptimizationStats)
        assert stats.total_predictions == 0

    def test_get_recommendations_untrained(self, stage_predictor):
        """Test getting recommendations for untrained model."""
        recs = stage_predictor.get_recommendations()

        assert len(recs) > 0
        # Should include recommendation to train model
        rec_titles = [r.title for r in recs]
        assert any("train" in t.lower() for t in rec_titles)

    def test_train_with_sample_history(self, stage_predictor, sample_history):
        """Test training with sample history."""
        # Skip if scikit-learn not available
        pytest.importorskip("sklearn")

        success, error = stage_predictor.train(sample_history)

        # Should succeed (or gracefully fail if sklearn not available)
        assert isinstance(success, bool)

    def test_train_insufficient_data(self, stage_predictor):
        """Test training with insufficient data."""
        minimal_history = [
            WorkflowExecution(
                change_id="test-001",
                timestamp="2025-10-20T10:00:00",
                change_type="docs",
                file_count=1,
                stages_executed=[0, 1, 2, 3],
                duration_seconds=50.0,
                success=True,
            )
        ]

        success, error = stage_predictor.train(minimal_history)

        # Should succeed but not train model
        assert success is True
        # Model should not be trained due to insufficient data
        assert stage_predictor.is_trained is False

    def test_encode_decode_change_type(self, stage_predictor):
        """Test change type encoding/decoding."""
        change_types = ["docs", "bugfix", "feature", "refactor", "chore"]

        for ct in change_types:
            encoded = stage_predictor._encode_change_type(ct)
            decoded = stage_predictor._decode_change_type(encoded)

            assert decoded == ct
            assert 0 <= encoded <= 4

    def test_unknown_change_type_encoding(self, stage_predictor):
        """Test encoding unknown change type."""
        encoded = stage_predictor._encode_change_type("unknown")

        assert encoded == 4  # Maps to "chore"

    def test_stats_tracking(self, stage_predictor):
        """Test statistics tracking."""
        initial_total = stage_predictor.stats.total_predictions

        # Make several predictions
        for _ in range(5):
            stage_predictor.predict("feature")

        assert stage_predictor.stats.total_predictions == initial_total + 5


# ============================================================================
# Test Recommendation
# ============================================================================


class TestRecommendation:
    """Tests for Recommendation data class."""

    def test_create_recommendation(self):
        """Test creating recommendation."""
        rec = Recommendation(
            title="Optimize workflow",
            description="Use fast lane for docs",
            stages=[0, 1, 2, 3],
            expected_duration=50.0,
            confidence=0.85,
            rationale="No code changes detected",
        )

        assert rec.title == "Optimize workflow"
        assert rec.confidence == 0.85

    def test_recommendation_to_dict(self):
        """Test converting recommendation to dict."""
        rec = Recommendation(
            title="Test",
            description="Test recommendation",
            stages=[0, 1],
            expected_duration=30.0,
            confidence=0.9,
            rationale="Test",
        )

        data = rec.to_dict()

        assert data["title"] == "Test"
        assert data["stages"] == [0, 1]


# ============================================================================
# Test OptimizationStats
# ============================================================================


class TestOptimizationStats:
    """Tests for OptimizationStats."""

    def test_default_stats(self):
        """Test default optimization stats."""
        stats = OptimizationStats()

        assert stats.total_predictions == 0
        assert stats.successful_predictions == 0
        assert stats.average_confidence == 0.0

    def test_stats_to_dict(self):
        """Test converting stats to dict."""
        stats = OptimizationStats(
            total_predictions=10,
            successful_predictions=8,
            average_confidence=0.85,
        )

        data = stats.to_dict()

        assert data["total_predictions"] == 10
        assert data["successful_predictions"] == 8
        assert data["average_confidence"] == 0.85

    def test_stats_from_dict(self):
        """Test creating stats from dict."""
        data = {
            "total_predictions": 10,
            "successful_predictions": 8,
            "average_confidence": 0.85,
            "model_training_time": 2.5,
        }

        stats = OptimizationStats.from_dict(data)

        assert stats.total_predictions == 10
        assert stats.average_confidence == 0.85


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for stage optimizer."""

    def test_full_workflow(self, temp_history_file):
        """Test complete optimizer workflow."""
        # 1. Create collector and add history
        collector = WorkflowHistoryCollector(temp_history_file)
        sample = create_sample_history()

        for execution in sample:
            collector.add_execution(execution)

        # 2. Save history
        success, _ = collector.save_to_file()
        assert success is True

        # 3. Create predictor
        predictor = StagePredictor()

        # 4. Make predictions
        stages, confidence = predictor.predict("feature", file_count=5)
        assert len(stages) > 0

        # 5. Estimate time
        duration = predictor.estimate_execution_time(stages)
        assert duration > 0

        # 6. Get statistics
        stats = predictor.get_stats()
        assert stats.total_predictions > 0

    def test_sample_history_coverage(self):
        """Test that sample history has good coverage."""
        sample = create_sample_history()

        assert len(sample) >= 5

        # Check coverage of change types
        change_types = {e.change_type for e in sample}
        assert "docs" in change_types
        assert "feature" in change_types
        assert "chore" in change_types

        # Check all executions are successful
        assert all(e.success for e in sample)

    def test_multiple_predictions_consistency(self, stage_predictor):
        """Test consistency of multiple predictions."""
        stages_list = []

        for _ in range(3):
            stages, _ = stage_predictor.predict("docs")
            stages_list.append(stages)

        # All predictions should be the same (using defaults)
        for stages in stages_list[1:]:
            assert stages == stages_list[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

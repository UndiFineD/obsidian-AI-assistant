#!/usr/bin/env python3
"""
Integration Tests for Workflow Lanes - End-to-End Validation (v0.1.44)

Tests complete workflows for all three lanes:
- Docs lane: Fast-track documentation-only changes
- Standard lane: Regular changes with full validation
- Heavy lane: Critical/production changes with strict validation

Validates:
- Lane selection and stage mapping
- Timing and SLA compliance
- Quality gates execution
- Status tracking across workflow
- Resumption capability
"""

import pytest
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from quality_gates import QualityGates
from status_tracker import StatusTracker, StageStatus
from workflow_resumption import WorkflowResumption
from pre_step_hooks import PreStepHooks, HookStatus


class TestDocsLaneWorkflow:
    """Integration tests for documentation lane"""

    def test_docs_lane_complete_workflow(self):
        """Test complete docs lane workflow"""
        with TemporaryDirectory() as tmpdir:
            # Initialize workflow
            tracker = StatusTracker(
                workflow_id="docs-test", lane="docs", status_file=Path(tmpdir) / "status.json"
            )
            hooks = PreStepHooks()

            # Simulate docs lane (skips code validation stages)
            stages = [0, 2, 3, 4, 5, 9, 10, 12]  # Stages run in docs lane

            for stage in stages:
                # Run hooks
                if stage in [0, 1, 10, 12]:
                    result = hooks.execute_hooks(stage)
                    assert result.status in [HookStatus.SUCCESS, HookStatus.SKIP]

                # Track stage
                tracker.start_stage(stage, f"Stage {stage}")
                time.sleep(0.01)  # Small delay
                tracker.complete_stage(stage, success=True)

            # Complete workflow
            tracker.complete_workflow(success=True)

            # Verify
            summary = tracker.get_summary()
            assert summary["status"] == "COMPLETED"
            assert summary["lane"] == "docs"
            assert "completed" in summary["stages"].lower()

    def test_docs_lane_quality_gates_disabled(self):
        """Test that docs lane skips quality gates"""
        gates = QualityGates(lane="docs")
        result = gates.run_all()
        assert result is True  # Should pass because gates are disabled

    def test_docs_lane_sla_compliance(self):
        """Test that docs lane meets SLA target"""
        with TemporaryDirectory() as tmpdir:
            tracker = StatusTracker(
                workflow_id="docs-sla-test", lane="docs", status_file=Path(tmpdir) / "status.json"
            )

            # Simulate quick workflow
            for stage in [0, 2, 3]:
                tracker.start_stage(stage, f"Stage {stage}")
                time.sleep(0.001)
                tracker.complete_stage(stage, success=True)

            # Docs lane SLA is 300 seconds (5 minutes)
            assert tracker.status["timing"]["within_sla"] is True
            assert tracker.status["timing"]["sla_target_seconds"] == 300


class TestStandardLaneWorkflow:
    """Integration tests for standard lane"""

    def test_standard_lane_complete_workflow(self):
        """Test complete standard lane workflow"""
        with TemporaryDirectory() as tmpdir:
            # Initialize workflow
            tracker = StatusTracker(
                workflow_id="standard-test",
                lane="standard",
                status_file=Path(tmpdir) / "status.json",
            )
            hooks = PreStepHooks()
            gates = QualityGates(lane="standard")

            # Simulate standard lane (all stages)
            for stage in range(13):
                # Run hooks for critical stages
                if stage in [0, 1, 10, 12]:
                    result = hooks.execute_hooks(stage)
                    if stage in [0, 1]:
                        assert result.status == HookStatus.SUCCESS

                # Track stage
                tracker.start_stage(stage, f"Stage {stage}")
                time.sleep(0.01)

                # Stage 8 includes quality gates
                if stage == 8:
                    # Quality gates would run here
                    gates_result = gates.run_all()
                    tracker.complete_stage(
                        stage, success=gates_result, metrics={"gates_passed": gates_result}
                    )
                else:
                    tracker.complete_stage(stage, success=True)

            # Complete workflow
            tracker.complete_workflow(success=True)

            # Verify
            summary = tracker.get_summary()
            assert summary["status"] == "COMPLETED"
            assert summary["lane"] == "standard"

    def test_standard_lane_quality_thresholds(self):
        """Test standard lane quality gate thresholds"""
        gates = QualityGates(lane="standard")

        assert gates.thresholds["pytest_pass_rate"] == 0.80
        assert gates.thresholds["coverage_minimum"] == 0.70
        assert gates.thresholds["enabled"] is True

    def test_standard_lane_sla_compliance(self):
        """Test that standard lane meets SLA target"""
        with TemporaryDirectory() as tmpdir:
            tracker = StatusTracker(
                workflow_id="standard-sla-test",
                lane="standard",
                status_file=Path(tmpdir) / "status.json",
            )

            # Simulate workflow
            for stage in range(13):
                tracker.start_stage(stage, f"Stage {stage}")
                time.sleep(0.01)
                tracker.complete_stage(stage, success=True)

            # Standard lane SLA is 900 seconds (15 minutes)
            assert tracker.status["timing"]["within_sla"] is True
            assert tracker.status["timing"]["sla_target_seconds"] == 900


class TestHeavyLaneWorkflow:
    """Integration tests for heavy lane"""

    def test_heavy_lane_complete_workflow(self):
        """Test complete heavy lane workflow"""
        with TemporaryDirectory() as tmpdir:
            # Initialize workflow
            tracker = StatusTracker(
                workflow_id="heavy-test", lane="heavy", status_file=Path(tmpdir) / "status.json"
            )
            hooks = PreStepHooks()
            gates = QualityGates(lane="heavy")

            # Simulate heavy lane (all stages with strict validation)
            for stage in range(13):
                # Run hooks
                if stage in [0, 1]:
                    result = hooks.execute_hooks(stage)
                    assert result.status == HookStatus.SUCCESS

                tracker.start_stage(stage, f"Stage {stage}")
                time.sleep(0.01)

                # Stage 8 includes strict quality gates
                if stage == 8:
                    gates_result = gates.run_all()
                    tracker.complete_stage(
                        stage, success=gates_result, metrics={"gates_passed": gates_result}
                    )
                else:
                    tracker.complete_stage(stage, success=True)

            tracker.complete_workflow(success=True)

            # Verify
            summary = tracker.get_summary()
            assert summary["status"] == "COMPLETED"
            assert summary["lane"] == "heavy"

    def test_heavy_lane_strict_quality_thresholds(self):
        """Test heavy lane strict quality gate thresholds"""
        gates = QualityGates(lane="heavy")

        # Heavy lane requires 100% test pass rate
        assert gates.thresholds["pytest_pass_rate"] == 1.0
        # And 85% coverage minimum
        assert gates.thresholds["coverage_minimum"] == 0.85
        assert gates.thresholds["enabled"] is True

    def test_heavy_lane_sla_compliance(self):
        """Test that heavy lane meets SLA target"""
        with TemporaryDirectory() as tmpdir:
            tracker = StatusTracker(
                workflow_id="heavy-sla-test", lane="heavy", status_file=Path(tmpdir) / "status.json"
            )

            # Simulate workflow
            for stage in range(13):
                tracker.start_stage(stage, f"Stage {stage}")
                time.sleep(0.01)
                tracker.complete_stage(stage, success=True)

            # Heavy lane SLA is 1200 seconds (20 minutes)
            assert tracker.status["timing"]["within_sla"] is True
            assert tracker.status["timing"]["sla_target_seconds"] == 1200


class TestCrossLaneFeatures:
    """Integration tests for features across lanes"""

    def test_resumption_across_lanes(self):
        """Test workflow resumption works for all lanes"""
        with TemporaryDirectory() as tmpdir:
            resumption = WorkflowResumption(checkpoint_dir=Path(tmpdir))

            for lane in ["docs", "standard", "heavy"]:
                resumption.update_workflow_state(
                    change_id=f"test-{lane}",
                    status="INCOMPLETE",
                    last_completed_stage=5,
                    last_stage_name="Checkpoint",
                    next_stage_num=6,
                    next_stage_name="Next",
                )

                workflow = resumption.detect_incomplete_workflow(f"test-{lane}")
                assert workflow is not None
                assert workflow["change_id"] == f"test-{lane}"

    def test_status_tracking_all_lanes(self):
        """Test status tracking works for all lanes"""
        with TemporaryDirectory() as tmpdir:
            for lane in ["docs", "standard", "heavy"]:
                tracker = StatusTracker(
                    workflow_id=f"test-{lane}",
                    lane=lane,
                    status_file=Path(tmpdir) / f"status-{lane}.json",
                )

                # Quick workflow
                tracker.start_stage(0, "Test")
                tracker.complete_stage(0, success=True)

                summary = tracker.get_summary()
                assert summary["lane"] == lane
                assert "completed" in summary["stages"].lower()

    def test_hooks_consistent_across_lanes(self):
        """Test pre-step hooks work consistently across lanes"""
        hooks = PreStepHooks()

        # Stage 0 should pass for all lanes
        result = hooks.execute_hooks(0)
        assert result.status == HookStatus.SUCCESS

        # Stage 1 version check should pass
        result = hooks.execute_hooks(1)
        assert result.status == HookStatus.SUCCESS

    def test_workflow_failure_handling(self):
        """Test workflow handles failures correctly"""
        with TemporaryDirectory() as tmpdir:
            tracker = StatusTracker(
                workflow_id="failure-test",
                lane="standard",
                status_file=Path(tmpdir) / "status.json",
            )

            # Successful stages
            tracker.start_stage(0, "Stage 0")
            tracker.complete_stage(0, success=True)

            # Failed stage
            tracker.start_stage(1, "Stage 1")
            tracker.complete_stage(1, success=False)

            # Verify status
            assert tracker.status["status"] == "FAILED"
            stage_1 = tracker.status["stages"][1]
            assert stage_1["status"] == "FAILED"

    def test_metrics_accumulation(self):
        """Test metrics accumulate across workflow"""
        with TemporaryDirectory() as tmpdir:
            tracker = StatusTracker(
                workflow_id="metrics-test",
                lane="standard",
                status_file=Path(tmpdir) / "status.json",
            )

            # Add metrics at different stages
            tracker.update_metrics({"files_modified": 5})
            tracker.update_metrics({"files_created": 2})
            tracker.update_metrics({"tests_passed": 45})

            # Verify accumulation
            metrics = tracker.status["metrics"]
            assert metrics["files_modified"] == 5
            assert metrics["files_created"] == 2
            assert metrics["tests_passed"] == 45


def run_integration_tests(verbose: bool = True) -> bool:
    """Run all integration tests"""
    print("\n" + "=" * 70)
    print("🧪 Running Integration Tests for Workflow Lanes (v0.1.44)")
    print("=" * 70 + "\n")

    args = [__file__]
    if verbose:
        args.append("-v")

    return pytest.main(args) == 0


if __name__ == "__main__":
    success = run_integration_tests(verbose=True)
    sys.exit(0 if success else 1)

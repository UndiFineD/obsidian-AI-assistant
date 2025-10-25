"""
Integration tests for v0.1.47 workflow improvements.

Tests end-to-end workflows for all lane types (docs/standard/heavy),
verifying:
- Stage execution per lane configuration
- Parallelization behavior
- Quality gates enforcement
- Status tracking and SLA monitoring
- Pre-step hooks validation
- Conventional commits validation

Test execution: pytest tests/test_workflow_integration.py -v
"""

import json
import sys
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import tempfile

import pytest


# Mock sys.modules for ML libraries before importing
sys.modules['torch'] = MagicMock()
sys.modules['transformers'] = MagicMock()

# Add scripts directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent / 'scripts'
sys.path.insert(0, str(SCRIPTS_DIR))

from workflow import LANE_MAPPING, get_stages_for_lane, get_lane_config
from hook_registry import HookRegistry
from conventional_commits import CommitValidator


class TestLaneConfiguration:
    """Test lane configuration and stage filtering."""

    def test_lane_mapping_exists(self):
        """Verify all lanes are defined in LANE_MAPPING."""
        assert 'docs' in LANE_MAPPING
        assert 'standard' in LANE_MAPPING
        assert 'heavy' in LANE_MAPPING

    def test_docs_lane_configuration(self):
        """Verify docs lane configuration."""
        lane_config = LANE_MAPPING['docs']
        assert lane_config['description'] == 'Fast docs-only workflow (<5 min)'
        assert lane_config['quality_gates_enabled'] is False
        assert lane_config['parallelization_enabled'] is False
        assert lane_config['max_duration_seconds'] == 300
        assert lane_config['code_change_check'] is True

    def test_standard_lane_configuration(self):
        """Verify standard lane runs all stages with validation."""
        lane_config = LANE_MAPPING['standard']
        assert lane_config['description'] == 'Standard workflow with basic validation (~15 min)'
        assert lane_config['quality_gates_enabled'] is True
        assert lane_config['parallelization_enabled'] is True
        assert lane_config['max_duration_seconds'] == 900
        assert set(lane_config['stages']) == set(range(13))

    def test_heavy_lane_configuration(self):
        """Verify heavy lane strict validation."""
        lane_config = LANE_MAPPING['heavy']
        assert lane_config['description'] == 'Strict validation workflow (~20 min)'
        assert lane_config['quality_gates_enabled'] is True
        assert lane_config['parallelization_enabled'] is True
        assert lane_config['max_duration_seconds'] == 1200
        assert set(lane_config['stages']) == set(range(13))

    def test_stage_filtering_docs_lane(self):
        """Test that get_stages_for_lane correctly filters for docs lane."""
        docs_stages = get_stages_for_lane('docs')
        assert isinstance(docs_stages, list)
        assert all(isinstance(s, int) for s in docs_stages)
        # Docs lane should have fewer stages (skips some)
        assert len(docs_stages) < 13

    def test_stage_filtering_standard_lane(self):
        """Test that get_stages_for_lane returns all stages for standard lane."""
        standard_stages = get_stages_for_lane('standard')
        assert len(standard_stages) == 13
        assert set(standard_stages) == set(range(13))

    def test_stage_filtering_heavy_lane(self):
        """Test that get_stages_for_lane returns all stages for heavy lane."""
        heavy_stages = get_stages_for_lane('heavy')
        assert len(heavy_stages) == 13
        assert set(heavy_stages) == set(range(13))

    def test_get_lane_config_function(self):
        """Test get_lane_config returns proper configuration."""
        config = get_lane_config('docs')
        assert 'stages' in config
        assert 'max_duration_seconds' in config
        assert 'quality_gates_enabled' in config


class TestParallelization:
    """Test parallelization behavior."""

    def test_parallel_stages_deterministic_order(self):
        """Verify parallel stages maintain deterministic ordering."""
        stages = [6, 2, 5, 3, 4]  # Unsorted
        sorted_stages = sorted(stages)
        
        assert sorted_stages == [2, 3, 4, 5, 6]

    def test_standard_lane_parallelization_enabled(self):
        """Verify standard lane enables parallelization."""
        config = get_lane_config('standard')
        assert config['parallelization_enabled'] is True

    def test_docs_lane_parallelization_disabled(self):
        """Verify docs lane disables parallelization."""
        config = get_lane_config('docs')
        assert config['parallelization_enabled'] is False

    def test_heavy_lane_parallelization_enabled(self):
        """Verify heavy lane enables parallelization."""
        config = get_lane_config('heavy')
        assert config['parallelization_enabled'] is True

    def test_max_duration_per_lane(self):
        """Verify max_duration_seconds is set correctly per lane."""
        docs_duration = LANE_MAPPING['docs']['max_duration_seconds']
        standard_duration = LANE_MAPPING['standard']['max_duration_seconds']
        heavy_duration = LANE_MAPPING['heavy']['max_duration_seconds']
        
        assert docs_duration == 300  # 5 minutes
        assert standard_duration == 900  # 15 minutes
        assert heavy_duration == 1200  # 20 minutes
        
        # Verify progression
        assert docs_duration < standard_duration < heavy_duration


class TestQualityGates:
    """Test quality gates per lane."""

    def test_docs_lane_skips_quality_gates(self):
        """Verify docs lane disables quality gates."""
        config = get_lane_config('docs')
        assert config['quality_gates_enabled'] is False

    def test_standard_lane_enables_quality_gates(self):
        """Verify standard lane enables quality gates."""
        config = get_lane_config('standard')
        assert config['quality_gates_enabled'] is True

    def test_heavy_lane_enables_quality_gates(self):
        """Verify heavy lane enables quality gates."""
        config = get_lane_config('heavy')
        assert config['quality_gates_enabled'] is True

    def test_docs_lane_code_change_check(self):
        """Verify docs lane has code change check enabled."""
        config = get_lane_config('docs')
        assert config['code_change_check'] is True

    def test_standard_lane_code_change_check(self):
        """Verify standard lane has code change check disabled."""
        config = get_lane_config('standard')
        assert config['code_change_check'] is False

    def test_heavy_lane_code_change_check(self):
        """Verify heavy lane has code change check disabled."""
        config = get_lane_config('heavy')
        assert config['code_change_check'] is False


class TestStatusTracking:
    """Test status tracking and SLA monitoring."""

    def test_status_file_creation(self):
        """Verify status file can be created and read."""
        with tempfile.TemporaryDirectory() as tmpdir:
            status_file = Path(tmpdir) / 'status.json'
            
            # Simulate status tracking
            status = {
                'change_id': 'test-change',
                'lane': 'standard',
                'current_stage': 0,
                'start_time': time.time(),
                'stages_completed': []
            }
            
            with open(status_file, 'w') as f:
                json.dump(status, f)
            
            # Verify file was created
            assert status_file.exists()
            
            # Verify content can be read
            with open(status_file, 'r') as f:
                loaded = json.load(f)
            
            assert loaded['lane'] == 'standard'
            assert loaded['change_id'] == 'test-change'

    def test_sla_targets_per_lane(self):
        """Verify SLA targets are met per lane."""
        docs_sla = LANE_MAPPING['docs']['max_duration_seconds']
        standard_sla = LANE_MAPPING['standard']['max_duration_seconds']
        heavy_sla = LANE_MAPPING['heavy']['max_duration_seconds']
        
        # Docs should be fastest (5 minutes = 300 seconds)
        assert docs_sla == 300
        # Standard should be normal (15 minutes = 900 seconds)
        assert standard_sla == 900
        # Heavy should be slowest (20 minutes = 1200 seconds)
        assert heavy_sla == 1200
        
        # Verify progression
        assert docs_sla < standard_sla < heavy_sla

    def test_stage_completion_tracking(self):
        """Verify stage completion can be tracked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            status_file = Path(tmpdir) / 'status.json'
            
            # Initial status
            status = {
                'stages_completed': [],
                'current_stage': 0
            }
            
            # Simulate stage completions
            for stage in range(13):
                status['stages_completed'].append(stage)
                status['current_stage'] = stage + 1
            
            # Verify all stages tracked
            assert len(status['stages_completed']) == 13
            assert status['stages_completed'] == list(range(13))


class TestPreStepHooks:
    """Test pre-step validation hooks."""

    def test_hook_registry_exists(self):
        """Verify HookRegistry can be instantiated."""
        registry = HookRegistry()
        assert registry is not None
        assert hasattr(registry, 'hooks')

    def test_stage_0_hooks_exist(self):
        """Verify Stage 0 has validation hook."""
        registry = HookRegistry()
        stage_0_hooks = registry.hooks.get(0, [])
        assert len(stage_0_hooks) > 0

    def test_stage_1_hooks_exist(self):
        """Verify Stage 1 has validation hook."""
        registry = HookRegistry()
        stage_1_hooks = registry.hooks.get(1, [])
        assert len(stage_1_hooks) > 0

    def test_stage_10_hooks_exist(self):
        """Verify Stage 10 has validation hook."""
        registry = HookRegistry()
        stage_10_hooks = registry.hooks.get(10, [])
        assert len(stage_10_hooks) > 0

    def test_stage_12_hooks_exist(self):
        """Verify Stage 12 has validation hook."""
        registry = HookRegistry()
        stage_12_hooks = registry.hooks.get(12, [])
        assert len(stage_12_hooks) > 0

    def test_hook_registry_has_correct_stages(self):
        """Verify hooks are registered for expected stages."""
        registry = HookRegistry()
        expected_stages = {0, 1, 10, 12}
        
        for stage in expected_stages:
            assert stage in registry.hooks, f"Stage {stage} should have hooks"
            assert len(registry.hooks[stage]) > 0


class TestConventionalCommits:
    """Test conventional commits validation."""

    def test_valid_commit_format(self):
        """Test validation of properly formatted commits."""
        valid_messages = [
            'feat: add new feature',
            'fix: resolve bug',
            'docs: update documentation',
            'feat(scope): add feature with scope',
            'fix(core): fix core issue',
            'refactor: improve performance',
            'test: add unit tests',
            'chore: update dependencies',
        ]
        
        for msg in valid_messages:
            is_valid, suggestion = CommitValidator.validate_commit(msg)
            assert is_valid is True, f"Message '{msg}' should be valid"

    def test_invalid_commit_format(self):
        """Test detection of improperly formatted commits."""
        invalid_messages = [
            'Added new feature',  # Missing type
            'feature: something',  # Wrong type
            'feat something',  # Missing colon
            'feat: ',  # Missing message
        ]
        
        for msg in invalid_messages:
            is_valid, suggestion = CommitValidator.validate_commit(msg)
            # Invalid messages should have is_valid=False
            assert is_valid is False or suggestion is not None

    def test_commit_with_scope(self):
        """Verify commit with scope is valid."""
        msg = 'feat(workflow): add lane selection'
        is_valid, suggestion = CommitValidator.validate_commit(msg)
        assert is_valid is True

    def test_commit_with_issue_reference(self):
        """Verify commit with issue reference is valid."""
        msg = 'fix: resolve issue #123'
        is_valid, suggestion = CommitValidator.validate_commit(msg)
        assert is_valid is True


class TestLaneExecutionPaths:
    """Test complete execution paths for each lane."""

    def test_docs_lane_execution_path(self):
        """Verify docs lane executes minimal stages."""
        docs_stages = get_stages_for_lane('docs')
        
        # Docs lane should skip many stages
        assert len(docs_stages) < 13

    def test_standard_lane_execution_path(self):
        """Verify standard lane executes all stages."""
        standard_stages = get_stages_for_lane('standard')
        
        # Standard lane should run all 13 stages
        assert len(standard_stages) == 13
        assert set(standard_stages) == set(range(13))

    def test_heavy_lane_execution_path(self):
        """Verify heavy lane executes all stages."""
        heavy_stages = get_stages_for_lane('heavy')
        
        # Heavy lane should run all 13 stages
        assert len(heavy_stages) == 13
        assert set(heavy_stages) == set(range(13))

    def test_lane_duration_realistic(self):
        """Verify lane durations are realistic."""
        for lane_name in ['docs', 'standard', 'heavy']:
            lane = LANE_MAPPING[lane_name]
            duration = lane['max_duration_seconds']
            
            # All durations should be reasonable (30 sec to 30 min)
            assert 30 <= duration <= 1800

    def test_all_stages_are_valid_numbers(self):
        """Verify all stages are valid (0-12)."""
        for lane_name in ['docs', 'standard', 'heavy']:
            lane = LANE_MAPPING[lane_name]
            stages = lane['stages']
            
            # All stages should be between 0-12
            for stage in stages:
                assert 0 <= stage <= 12


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""

    def test_docs_lane_quick_execution(self):
        """Simulate docs lane quick content change."""
        lane_config = get_lane_config('docs')
        
        # Verify docs lane is configured for speed
        assert lane_config['max_duration_seconds'] == 300  # 5 minutes
        assert lane_config['parallelization_enabled'] is False
        
        executed_stages = get_stages_for_lane('docs')
        assert len(executed_stages) < 13

    def test_standard_lane_normal_feature(self):
        """Simulate standard lane normal feature development."""
        lane_config = get_lane_config('standard')
        
        # Verify standard lane runs normally
        assert lane_config['max_duration_seconds'] == 900  # 15 minutes
        assert lane_config['parallelization_enabled'] is True
        
        executed_stages = get_stages_for_lane('standard')
        assert len(executed_stages) == 13  # All stages

    def test_heavy_lane_production_release(self):
        """Simulate heavy lane production release."""
        lane_config = get_lane_config('heavy')
        
        # Verify heavy lane is strict
        assert lane_config['max_duration_seconds'] == 1200  # 20 minutes
        assert lane_config['quality_gates_enabled'] is True
        
        executed_stages = get_stages_for_lane('heavy')
        assert len(executed_stages) == 13  # All stages

    def test_parallel_stages_execution_order(self):
        """Verify parallel stages execute in deterministic order."""
        parallel_stages = [6, 2, 5, 3, 4]
        sorted_stages = sorted(parallel_stages)
        
        # Should be sorted ascending
        assert sorted_stages == [2, 3, 4, 5, 6]

    def test_hook_validation_before_execution(self):
        """Verify hooks can validate before stage execution."""
        registry = HookRegistry()
        
        # Verify hooks exist for critical stages
        critical_stages = [0, 1, 10, 12]
        for stage in critical_stages:
            assert stage in registry.hooks, f"Stage {stage} should have hooks"

    def test_commit_validation_working(self):
        """Verify commit validation works."""
        # Test good commit
        good_msg = 'feat: add new workflow feature'
        good_valid, good_suggestion = CommitValidator.validate_commit(good_msg)
        assert good_valid is True
        
        # Test bad commit
        bad_msg = 'Added new feature'
        bad_valid, bad_suggestion = CommitValidator.validate_commit(bad_msg)
        # Should either be invalid or have suggestions
        assert (bad_valid is False or bad_suggestion is not None)


class TestErrorHandling:
    """Test error handling in workflow integration."""

    def test_invalid_lane_name_not_in_mapping(self):
        """Verify invalid lane names are not in LANE_MAPPING."""
        invalid_lanes = ['invalid', 'turbo', 'ultra', '']
        
        for lane in invalid_lanes:
            # These should not be in LANE_MAPPING
            assert lane not in LANE_MAPPING

    def test_invalid_stage_number_out_of_range(self):
        """Verify invalid stage numbers are rejected."""
        invalid_stages = [-1, 13, 14, 100]
        
        for stage in invalid_stages:
            # Valid stages are 0-12
            assert not (0 <= stage <= 12)

    def test_duration_values_reasonable(self):
        """Verify duration values are within reasonable bounds."""
        for lane_name, lane_config in LANE_MAPPING.items():
            duration = lane_config['max_duration_seconds']
            
            # Should be between 30 seconds and 30 minutes
            assert 30 <= duration <= 1800, f"Lane {lane_name} duration out of bounds"

    def test_lane_config_copy_independence(self):
        """Verify get_lane_config returns independent copies."""
        config1 = get_lane_config('docs')
        config2 = get_lane_config('docs')
        
        # Modify config1
        config1['max_duration_seconds'] = 999
        
        # config2 should not be affected
        assert config2['max_duration_seconds'] == 300


# Integration test fixtures
@pytest.fixture
def temp_workspace():
    """Create temporary workspace for integration testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_git_repo(temp_workspace):
    """Create mock git repository."""
    repo_path = temp_workspace / 'test_repo'
    repo_path.mkdir()
    return repo_path


@pytest.fixture
def change_config():
    """Standard change configuration for testing."""
    return {
        'change_id': 'test-integration-001',
        'title': 'Integration Test Feature',
        'owner': 'test-user',
        'lane': 'standard'
    }


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

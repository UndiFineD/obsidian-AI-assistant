#!/usr/bin/env python3
"""
Test suite for enhanced workflow improvement modules.

Tests for:
- enhanced_pre_step_hooks.py
- commit_validation_enhancements.py
- helper_utilities_enhancements.py

Coverage: 85%+ target
"""

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# ============================================================================
# Test enhanced_pre_step_hooks.py
# ============================================================================


class TestEnhancedPreStepHooks:
    """Test suite for enhanced_pre_step_hooks module."""

    def test_hook_status_enum(self):
        """Test HookStatus enum."""
        from scripts.enhanced_pre_step_hooks import HookStatus

        assert HookStatus.SUCCESS.value == "success"
        assert HookStatus.ERROR.value == "error"
        assert HookStatus.PENDING.value == "pending"

    def test_hook_result_creation(self):
        """Test HookResult creation and methods."""
        from scripts.enhanced_pre_step_hooks import HookResult, HookStatus

        result = HookResult(
            hook_name="test_hook",
            status=HookStatus.SUCCESS,
            duration=0.5,
            message="Test message",
        )

        assert result.hook_name == "test_hook"
        assert result.is_success()
        assert result.duration == 0.5

    def test_hook_context_creation(self):
        """Test HookContext creation."""
        from scripts.enhanced_pre_step_hooks import HookContext

        context = HookContext(
            stage_num=0,
            stage_name="Initial",
            change_id="test-change",
        )

        assert context.stage_num == 0
        assert context.change_id == "test-change"
        assert context.lane == "standard"

    def test_hook_context_results(self):
        """Test HookContext result management."""
        from scripts.enhanced_pre_step_hooks import HookContext, HookResult, HookStatus

        context = HookContext(stage_num=0)
        result = HookResult(
            hook_name="test",
            status=HookStatus.SUCCESS,
            duration=0.1,
            message="test",
        )

        context.set_result("test", result)
        retrieved = context.get_result("test")

        assert retrieved is not None
        assert retrieved.hook_name == "test"

    def test_hook_registry_registration(self):
        """Test hook registration."""
        from scripts.enhanced_pre_step_hooks import (
            Hook,
            HookContext,
            HookRegistry,
            HookResult,
            HookStatus,
        )

        class TestHook(Hook):
            def execute(self, context: HookContext) -> HookResult:
                return HookResult(
                    hook_name=self.name,
                    status=HookStatus.SUCCESS,
                    duration=0.1,
                    message="test",
                )

        registry = HookRegistry()
        hook = TestHook("test_hook")
        registry.hooks["test_hook"] = hook
        registry.stage_hooks[0] = ["test_hook"]

        assert "test_hook" in registry.hooks
        assert len(registry.get_hooks_for_stage(0)) > 0

    def test_dependency_resolver(self):
        """Test dependency resolution."""
        from scripts.enhanced_pre_step_hooks import (
            DependencyResolver,
            Hook,
            HookContext,
            HookResult,
            HookStatus,
        )

        class DependentHook(Hook):
            def execute(self, context: HookContext) -> HookResult:
                return HookResult(
                    hook_name=self.name,
                    status=HookStatus.SUCCESS,
                    duration=0.1,
                    message="test",
                )

        hook1 = DependentHook("hook1")
        hook2 = DependentHook("hook2", depends_on=["hook1"])

        resolved = DependencyResolver.resolve([hook2, hook1])

        # hook1 should come before hook2
        assert resolved[0].name == "hook1"
        assert resolved[1].name == "hook2"

    def test_hook_cache(self):
        """Test hook result caching."""
        from scripts.enhanced_pre_step_hooks import HookCache, HookResult, HookStatus

        with tempfile.TemporaryDirectory() as tmpdir:
            cache = HookCache(Path(tmpdir))

            result = HookResult(
                hook_name="test",
                status=HookStatus.SUCCESS,
                duration=0.1,
                message="cached",
            )

            cache.set("test_key", result)
            retrieved = cache.get("test_key", ttl=3600)

            assert retrieved is not None
            assert retrieved.hook_name == "test"

    def test_hook_profiler(self):
        """Test hook profiling."""
        from scripts.enhanced_pre_step_hooks import HookProfiler

        profiler = HookProfiler()

        @profiler.profile("test_hook")
        def slow_function():
            time.sleep(0.05)
            return "result"

        slow_function()
        slow_function()

        stats = profiler.get_stats("test_hook")
        assert stats["count"] == 2
        assert stats["average"] > 0.04


# ============================================================================
# Test commit_validation_enhancements.py
# ============================================================================


class TestCommitValidationEnhancements:
    """Test suite for commit validation enhancements."""

    def test_commit_type_enum(self):
        """Test CommitType enum."""
        from scripts.commit_validation_enhancements import CommitType

        assert CommitType.FEATURE.value == "feat"
        assert CommitType.BUGFIX.value == "fix"
        assert CommitType.DOCS.value == "docs"

    def test_validation_status_enum(self):
        """Test ValidationStatus enum."""
        from scripts.commit_validation_enhancements import ValidationStatus

        assert ValidationStatus.VALID.value == "valid"
        assert ValidationStatus.ERROR.value == "error"

    def test_validation_result(self):
        """Test ValidationResult."""
        from scripts.commit_validation_enhancements import (
            ValidationResult,
            ValidationStatus,
        )

        result = ValidationResult(
            status=ValidationStatus.VALID,
            message="Valid message",
        )

        assert result.is_valid
        assert result.status == ValidationStatus.VALID

    def test_commit_message_template(self):
        """Test commit message templates."""
        from scripts.commit_validation_enhancements import (
            CommitMessageTemplate,
            CommitType,
        )

        template = CommitMessageTemplate.get_template(CommitType.FEATURE)
        assert template is not None
        assert "{type}" in template
        assert "{subject}" in template

    def test_commit_validator_valid_message(self):
        """Test validator with valid commit message."""
        from scripts.commit_validation_enhancements import CommitValidator

        validator = CommitValidator()

        message = """feat(api): add new endpoint for users

This adds a new POST endpoint to handle user creation.

Closes #123"""

        result = validator.validate(message)
        assert result.is_valid

    def test_commit_validator_empty_message(self):
        """Test validator with empty message."""
        from scripts.commit_validation_enhancements import CommitValidator

        validator = CommitValidator()
        result = validator.validate("")

        assert not result.is_valid
        assert len(result.issues) > 0

    def test_commit_validator_long_subject(self):
        """Test validator with long subject."""
        from scripts.commit_validation_enhancements import (
            CommitValidator,
            ValidationStatus,
        )

        validator = CommitValidator()

        long_subject = "f" * 100
        message = f"feat: {long_subject}"

        result = validator.validate(message)
        assert result.status == ValidationStatus.ERROR

    def test_commit_info_creation(self):
        """Test CommitInfo creation."""
        from datetime import datetime

        from scripts.commit_validation_enhancements import CommitInfo

        info = CommitInfo(
            hash="abc123",
            author="Test Author",
            date=datetime.now(),
            message="test commit",
            subject="test commit",
            body="",
        )

        assert info.hash == "abc123"
        assert info.author == "Test Author"

    def test_branch_protection_validator(self):
        """Test branch protection validator."""
        from scripts.commit_validation_enhancements import BranchProtectionValidator

        with tempfile.TemporaryDirectory() as tmpdir:
            validator = BranchProtectionValidator(Path(tmpdir))

            # Create rules file
            rules = {
                "main": {
                    "require_signed_commits": True,
                    "require_pull_request_reviews": True,
                }
            }

            rules_file = Path(tmpdir) / ".branch-protection.json"
            with open(rules_file, "w") as f:
                json.dump(rules, f)

            validator.load_rules(rules_file)
            result = validator.validate_branch("main")

            assert result.warnings is not None


# ============================================================================
# Test helper_utilities_enhancements.py
# ============================================================================


class TestHelperUtilitiesEnhancements:
    """Test suite for helper utilities enhancements."""

    def test_performance_profiler_timing(self):
        """Test performance profiler."""
        from scripts.helper_utilities_enhancements import PerformanceProfiler

        profiler = PerformanceProfiler()

        with profiler.measure("test_operation"):
            time.sleep(0.05)

        stats = profiler.get_statistics("test_operation")

        assert stats["count"] == 1
        assert stats["total"] >= 0.05

    def test_cache_manager_get_set(self):
        """Test cache manager get/set."""
        from scripts.helper_utilities_enhancements import CacheManager

        cache = CacheManager()

        cache.set("key1", "value1")
        value = cache.get("key1")

        assert value == "value1"

    def test_cache_manager_ttl(self):
        """Test cache manager TTL."""
        from scripts.helper_utilities_enhancements import CacheManager

        cache = CacheManager()

        cache.set("key1", "value1")

        # Should hit
        assert cache.get("key1", ttl=3600) == "value1"

        # Should miss (expired)
        assert cache.get("key1", ttl=0) is None

    def test_cache_manager_stats(self):
        """Test cache manager statistics."""
        from scripts.helper_utilities_enhancements import CacheManager

        cache = CacheManager()

        cache.set("key1", "value1")
        cache.get("key1")  # hit
        cache.get("missing_key")  # miss

        stats = cache.get_stats()

        assert stats["hits"] == 1
        assert stats["misses"] >= 1

    def test_encryption_helper(self):
        """Test encryption helper."""
        from scripts.helper_utilities_enhancements import EncryptionHelper

        data = "sensitive data"
        key = "secret_key"

        encrypted = EncryptionHelper.simple_encrypt(data, key)
        decrypted = EncryptionHelper.simple_decrypt(encrypted, key)

        assert decrypted == data

    def test_encryption_hash(self):
        """Test encryption hashing."""
        from scripts.helper_utilities_enhancements import EncryptionHelper

        data = "test data"

        hash1 = EncryptionHelper.hash_data(data)
        hash2 = EncryptionHelper.hash_data(data)

        # Same data produces same hash
        assert hash1 == hash2

    def test_progress_tracker(self):
        """Test progress tracker."""
        from scripts.helper_utilities_enhancements import ProgressTracker

        progress = ProgressTracker(100, "Test")

        progress.update(50)
        bar = progress.get_bar()

        assert "50" in bar or "50/100" in bar or "Test" in bar

    def test_resource_monitor(self):
        """Test resource monitor."""
        from scripts.helper_utilities_enhancements import ResourceMonitor

        info = ResourceMonitor.get_process_info()

        assert "pid" in info
        assert "memory_mb" in info

    def test_retry_helper_success(self):
        """Test retry helper with successful call."""
        from scripts.helper_utilities_enhancements import RetryHelper

        counter = [0]

        def test_func():
            counter[0] += 1
            return "success"

        result = RetryHelper.with_retry(test_func, max_attempts=3)

        assert result == "success"
        assert counter[0] == 1

    def test_retry_helper_failure(self):
        """Test retry helper with all failures."""
        from scripts.helper_utilities_enhancements import RetryHelper

        def always_fails():
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            RetryHelper.with_retry(always_fails, max_attempts=2)

    def test_diagnostic_helper(self):
        """Test diagnostic helper."""
        from scripts.helper_utilities_enhancements import DiagnosticHelper

        # Should not raise
        DiagnosticHelper.print_environment()

        stack = DiagnosticHelper.get_call_stack()
        assert isinstance(stack, list)


# ============================================================================
# Integration tests
# ============================================================================


class TestIntegration:
    """Integration tests for enhancement modules."""

    def test_hook_workflow(self):
        """Test complete hook workflow."""
        from scripts.enhanced_pre_step_hooks import (
            Hook,
            HookContext,
            HookRegistry,
            HookResult,
            HookStatus,
        )

        class ValidationHook(Hook):
            def execute(self, context: HookContext) -> HookResult:
                return HookResult(
                    hook_name=self.name,
                    status=HookStatus.SUCCESS,
                    duration=0.1,
                    message="Validation passed",
                )

        registry = HookRegistry()
        hook = ValidationHook("validation")
        registry.hooks["validation"] = hook
        registry.stage_hooks[0] = ["validation"]

        context = HookContext(stage_num=0, change_id="test")
        results = registry.execute_hooks(0, context)

        assert len(results) > 0
        assert results[0].is_success()

    def test_commit_workflow(self):
        """Test complete commit workflow."""
        from scripts.commit_validation_enhancements import (
            CommitMessageTemplate,
            CommitType,
            CommitValidator,
        )

        # Build message
        template = CommitMessageTemplate.get_template(CommitType.FEATURE)
        message = template.format(
            type="feat",
            scope="api",
            subject="add new feature",
            body="Feature description",
            issue="closes #123",
            cause="",
            solution="",
            impact="",
            breaking_change="",
        )

        # Validate
        validator = CommitValidator()
        result = validator.validate(message)

        assert result.is_valid

    def test_profiling_with_cache(self):
        """Test profiler with cache manager."""
        from scripts.helper_utilities_enhancements import (
            CacheManager,
            PerformanceProfiler,
        )

        profiler = PerformanceProfiler()
        cache = CacheManager()

        with profiler.measure("cache_operation"):
            cache.set("key1", "value1")
            value = cache.get("key1")

        assert value == "value1"

        stats = profiler.get_statistics("cache_operation")
        assert stats["count"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

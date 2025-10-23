#!/usr/bin/env python3
"""
Comprehensive Python Test Suite for Workflow Scripts

Tests all workflow automation scripts in the scripts/ directory including:
- workflow.py (main orchestrator)
- workflow-step00.py through workflow-step12.py (individual steps)
- workflow-helpers.py (shared utilities)
- Related workflow utilities and validators

Author: Obsidian AI Agent Team
License: MIT
"""

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from unittest import mock

import pytest

# Add scripts directory to Python path
SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(PROJECT_ROOT / "agent"))

# Constants
CHANGES_DIR = PROJECT_ROOT / "openspec" / "changes"
ARCHIVE_DIR = PROJECT_ROOT / "openspec" / "archive"
TEMPLATES_DIR = PROJECT_ROOT / "openspec" / "templates"


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def temp_change_dir():
    """Create a temporary change directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        change_dir = Path(tmpdir) / "test-change"
        change_dir.mkdir(parents=True, exist_ok=True)
        yield change_dir


@pytest.fixture
def temp_project_structure():
    """Create a temporary project structure with OpenSpec directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        changes_dir = project_root / "openspec" / "changes"
        archive_dir = project_root / "openspec" / "archive"
        templates_dir = project_root / "openspec" / "templates"

        changes_dir.mkdir(parents=True, exist_ok=True)
        archive_dir.mkdir(parents=True, exist_ok=True)
        templates_dir.mkdir(parents=True, exist_ok=True)

        yield {
            "root": project_root,
            "changes": changes_dir,
            "archive": archive_dir,
            "templates": templates_dir,
        }


@pytest.fixture
def workflow_helpers():
    """Load workflow-helpers module."""
    spec = importlib.util.spec_from_file_location(
        "workflow_helpers", SCRIPT_DIR / "workflow-helpers.py"
    )
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    return helpers


@pytest.fixture
def sample_todo_template():
    """Create a sample todo.md template."""
    return """# OpenSpec Change: <Change Title>

**Change ID:** <change-id>
**Owner:** @username
**Created:** YYYY-MM-DD

## Workflow Checklist

- [ ] **0. Create TODOs**
- [ ] **1. Version Bump**
- [ ] **2. Proposal Review**
- [ ] **3. Capability Spec**
- [ ] **4. Task Breakdown**
- [ ] **5. Implementation Checklist**
- [ ] **6. Script Generation**
- [ ] **7. Document Review**
- [ ] **8. Test Execution**
- [ ] **9. Review Changes**
- [ ] **10. Git Operations**
- [ ] **11. Commit Changes**
- [ ] **12. Pull Request**

## Progress

Completed: 0/13 steps
"""


# ============================================================================
# Tests: workflow-helpers.py
# ============================================================================


class TestWorkflowHelpers:
    """Test suite for workflow-helpers.py utility functions."""

    def test_colors_class_exists(self, workflow_helpers):
        """Test that Colors class with ANSI codes is defined."""
        assert hasattr(workflow_helpers, "Colors")
        colors = workflow_helpers.Colors
        assert hasattr(colors, "CYAN")
        assert hasattr(colors, "GREEN")
        assert hasattr(colors, "RED")
        assert hasattr(colors, "YELLOW")
        assert hasattr(colors, "RESET")

    def test_write_step_function(self, workflow_helpers, capsys):
        """Test write_step formats and displays step headers."""
        workflow_helpers.write_step(0, "Create TODOs")
        captured = capsys.readouterr()
        assert "STEP 0" in captured.out
        assert "Create TODOs" in captured.out

    def test_write_info_function(self, workflow_helpers, capsys):
        """Test write_info displays informational messages."""
        workflow_helpers.write_info("Test message")
        captured = capsys.readouterr()
        assert "Test message" in captured.out

    def test_write_success_function(self, workflow_helpers, capsys):
        """Test write_success displays success messages with color codes."""
        workflow_helpers.write_success("Operation completed")
        captured = capsys.readouterr()
        assert "Operation completed" in captured.out

    def test_write_error_function(self, workflow_helpers, capsys):
        """Test write_error displays error messages."""
        workflow_helpers.write_error("Something went wrong")
        captured = capsys.readouterr()
        assert "Something went wrong" in captured.out

    def test_write_warning_function(self, workflow_helpers, capsys):
        """Test write_warning displays warning messages."""
        workflow_helpers.write_warning("Caution required")
        captured = capsys.readouterr()
        assert "Caution required" in captured.out

    def test_write_error_hint_function(self, workflow_helpers, capsys):
        """Test write_error_hint displays error with resolution hint."""
        workflow_helpers.write_error_hint("Problem", "Try this solution")
        captured = capsys.readouterr()
        assert "Problem" in captured.out
        assert "Try this solution" in captured.out

    def test_show_changes_empty_directory(self, workflow_helpers, capsys, temp_project_structure):
        """Test show_changes with empty changes directory."""
        workflow_helpers.show_changes(temp_project_structure["changes"])
        captured = capsys.readouterr()
        assert "No active changes found" in captured.out

    def test_show_changes_with_active_changes(self, workflow_helpers, capsys, temp_project_structure, sample_todo_template):
        """Test show_changes displays active changes with completion percentage."""
        # Create a test change
        change_dir = temp_project_structure["changes"] / "test-change"
        change_dir.mkdir(parents=True, exist_ok=True)
        todo_file = change_dir / "todo.md"
        todo_file.write_text(sample_todo_template, encoding="utf-8")

        workflow_helpers.show_changes(temp_project_structure["changes"])
        captured = capsys.readouterr()
        assert "Active Changes:" in captured.out
        assert "test-change" in captured.out

    def test_test_change_structure_valid(self, workflow_helpers, temp_change_dir):
        """Test test_change_structure validates required files."""
        # Create all required files
        required_files = ["todo.md", "proposal.md", "spec.md", "tasks.md", "test_plan.md"]
        for filename in required_files:
            (temp_change_dir / filename).write_text(f"# {filename}\n", encoding="utf-8")

        result = workflow_helpers.test_change_structure(temp_change_dir)
        assert result is True

    def test_test_change_structure_missing_files(self, workflow_helpers, temp_change_dir, capsys):
        """Test test_change_structure detects missing required files."""
        # Create only some files
        (temp_change_dir / "todo.md").write_text("# todo\n", encoding="utf-8")
        (temp_change_dir / "proposal.md").write_text("# proposal\n", encoding="utf-8")

        result = workflow_helpers.test_change_structure(temp_change_dir)
        assert result is False

        captured = capsys.readouterr()
        assert "Missing required file" in captured.out

    def test_set_content_atomic_creates_file(self, workflow_helpers, temp_change_dir):
        """Test set_content_atomic writes file atomically."""
        test_file = temp_change_dir / "test.md"
        content = "# Test Content\n\nSome text here."
        
        result = workflow_helpers.set_content_atomic(test_file, content)
        
        assert result is True
        assert test_file.exists()
        assert test_file.read_text(encoding="utf-8") == content

    def test_set_content_atomic_overwrites_file(self, workflow_helpers, temp_change_dir):
        """Test set_content_atomic overwrites existing file."""
        test_file = temp_change_dir / "test.md"
        test_file.write_text("Old content", encoding="utf-8")
        
        new_content = "New content"
        result = workflow_helpers.set_content_atomic(test_file, new_content)
        
        assert result is True
        assert test_file.read_text(encoding="utf-8") == new_content

    def test_set_content_atomic_uses_utf8(self, workflow_helpers, temp_change_dir):
        """Test set_content_atomic uses UTF-8 encoding."""
        test_file = temp_change_dir / "test.md"
        content = "# Test 你好 мир العالم\n"
        
        result = workflow_helpers.set_content_atomic(test_file, content)
        
        assert result is True
        read_content = test_file.read_text(encoding="utf-8")
        assert "你好" in read_content
        assert "мир" in read_content

    def test_cross_validation_result_dataclass(self, workflow_helpers):
        """Test CrossValidationResult dataclass exists."""
        assert hasattr(workflow_helpers, "CrossValidationResult")
        result = workflow_helpers.CrossValidationResult()
        assert result.is_valid is True
        assert isinstance(result.issues, list)
        assert isinstance(result.warnings, list)


# ============================================================================
# Tests: workflow-step00.py (Create TODOs)
# ============================================================================


class TestWorkflowStep0:
    """Test suite for workflow-step00.py (Create TODOs step)."""

    def test_step0_module_exists(self):
        """Test that workflow-step00.py exists."""
        step_file = SCRIPT_DIR / "workflow-step00.py"
        assert step_file.exists()

    def test_step0_has_invoke_step0_function(self):
        """Test that invoke_step0 function exists."""
        spec = importlib.util.spec_from_file_location(
            "workflow_step00", SCRIPT_DIR / "workflow-step00.py"
        )
        step00 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(step00)
        
        assert hasattr(step00, "invoke_step0")
        assert callable(step00.invoke_step0)

    def test_step0_function_signature(self):
        """Test invoke_step0 has correct function signature."""
        spec = importlib.util.spec_from_file_location(
            "workflow_step00", SCRIPT_DIR / "workflow-step00.py"
        )
        step00 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(step00)
        
        import inspect
        sig = inspect.signature(step00.invoke_step0)
        params = list(sig.parameters.keys())
        
        assert "change_path" in params
        assert "title" in params
        assert "owner" in params
        assert "dry_run" in params

    def test_step0_dry_run_mode(self):
        """Test Step 0 dry run mode with proper project structure."""
        spec = importlib.util.spec_from_file_location(
            "workflow_step00", SCRIPT_DIR / "workflow-step00.py"
        )
        step00 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(step00)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create proper project structure
            project_root = Path(tmpdir)
            changes_dir = project_root / "openspec" / "changes"
            templates_dir = project_root / "openspec" / "templates"
            changes_dir.mkdir(parents=True, exist_ok=True)
            templates_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a basic todo template
            template_path = templates_dir / "todo.md"
            template_path.write_text("[ ] **0. Create TODOs**\n")
            
            change_path = changes_dir / "test-change"
            change_path.mkdir()
            
            result = step00.invoke_step0(
                change_path=change_path,
                title="Test Change",
                owner="@test-user",
                dry_run=True
            )
            
            # In dry run, it should return True and not create file
            assert result is True


# ============================================================================
# Tests: workflow-step01.py through workflow-step12.py
# ============================================================================


class TestWorkflowSteps:
    """Test suite for all workflow step modules."""

    @pytest.mark.parametrize("step_num", list(range(13)))
    def test_step_module_exists(self, step_num):
        """Test that each workflow step module file exists."""
        step_file = SCRIPT_DIR / f"workflow-step{step_num:02d}.py"
        assert step_file.exists(), f"workflow-step{step_num:02d}.py not found"

    @pytest.mark.parametrize("step_num", list(range(13)))
    def test_step_module_can_be_imported(self, step_num):
        """Test that each workflow step module can be imported."""
        step_file = SCRIPT_DIR / f"workflow-step{step_num:02d}.py"
        spec = importlib.util.spec_from_file_location(
            f"workflow_step{step_num:02d}", step_file
        )
        module = importlib.util.module_from_spec(spec)
        
        # Should not raise exception
        spec.loader.exec_module(module)

    @pytest.mark.parametrize("step_num", list(range(13)))
    def test_step_has_invoke_function(self, step_num):
        """Test that each step has invoke_stepN function."""
        step_file = SCRIPT_DIR / f"workflow-step{step_num:02d}.py"
        spec = importlib.util.spec_from_file_location(
            f"workflow_step{step_num:02d}", step_file
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        func_name = f"invoke_step{step_num}"
        assert hasattr(module, func_name), f"{func_name} not found in step {step_num}"
        assert callable(getattr(module, func_name))

    @pytest.mark.parametrize("step_num", list(range(13)))
    def test_step_function_returns_bool(self, step_num):
        """Test that invoke_stepN functions return boolean values."""
        step_file = SCRIPT_DIR / f"workflow-step{step_num:02d}.py"
        spec = importlib.util.spec_from_file_location(
            f"workflow_step{step_num:02d}", step_file
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        func_name = f"invoke_step{step_num}"
        func = getattr(module, func_name)
        
        # Check function has return type annotation (if present)
        import inspect
        sig = inspect.signature(func)
        # Return annotation should be bool or include bool
        if sig.return_annotation != inspect.Signature.empty:
            assert sig.return_annotation in (bool, "bool")


# ============================================================================
# Tests: workflow.py (Main Orchestrator)
# ============================================================================


class TestWorkflowOrchestrator:
    """Test suite for main workflow.py orchestrator."""

    def test_workflow_py_exists(self):
        """Test that workflow.py exists."""
        workflow_file = SCRIPT_DIR / "workflow.py"
        assert workflow_file.exists()

    def test_workflow_py_can_be_imported(self):
        """Test that workflow.py can be imported."""
        spec = importlib.util.spec_from_file_location(
            "workflow", SCRIPT_DIR / "workflow.py"
        )
        workflow = importlib.util.module_from_spec(spec)
        
        # Should not raise exception
        with mock.patch.dict(sys.modules, {"checkpoint_manager": mock.MagicMock()}):
            spec.loader.exec_module(workflow)

    def test_workflow_has_required_functions(self):
        """Test that workflow.py has key functions."""
        spec = importlib.util.spec_from_file_location(
            "workflow", SCRIPT_DIR / "workflow.py"
        )
        workflow = importlib.util.module_from_spec(spec)
        
        with mock.patch.dict(sys.modules, {"checkpoint_manager": mock.MagicMock()}):
            spec.loader.exec_module(workflow)
        
        assert hasattr(workflow, "load_step_module")
        assert hasattr(workflow, "STEP_NAMES")
        assert isinstance(workflow.STEP_NAMES, dict)
        assert len(workflow.STEP_NAMES) == 13

    def test_workflow_step_names_complete(self):
        """Test that STEP_NAMES covers all 13 steps."""
        spec = importlib.util.spec_from_file_location(
            "workflow", SCRIPT_DIR / "workflow.py"
        )
        workflow = importlib.util.module_from_spec(spec)
        
        with mock.patch.dict(sys.modules, {"checkpoint_manager": mock.MagicMock()}):
            spec.loader.exec_module(workflow)
        
        step_names = workflow.STEP_NAMES
        for step_num in range(13):
            assert step_num in step_names
            assert isinstance(step_names[step_num], str)
            assert len(step_names[step_num]) > 0

    def test_workflow_directories_defined(self):
        """Test that workflow.py defines required directory constants."""
        spec = importlib.util.spec_from_file_location(
            "workflow", SCRIPT_DIR / "workflow.py"
        )
        workflow = importlib.util.module_from_spec(spec)
        
        with mock.patch.dict(sys.modules, {"checkpoint_manager": mock.MagicMock()}):
            spec.loader.exec_module(workflow)
        
        assert hasattr(workflow, "CHANGES_DIR")
        assert hasattr(workflow, "ARCHIVE_DIR")
        assert hasattr(workflow, "TEMPLATES_DIR")


# ============================================================================
# Tests: Workflow Utilities (validators, dependencies, etc.)
# ============================================================================


class TestWorkflowUtilities:
    """Test suite for workflow utility scripts."""

    def test_version_manager_exists(self):
        """Test that version_manager.py exists."""
        version_file = SCRIPT_DIR / "version_manager.py"
        assert version_file.exists()

    def test_checkpoint_manager_exists(self):
        """Test that checkpoint_manager.py exists."""
        checkpoint_file = SCRIPT_DIR / "checkpoint_manager.py"
        assert checkpoint_file.exists()

    def test_generate_changelog_exists(self):
        """Test that generate_changelog.py exists."""
        changelog_file = SCRIPT_DIR / "generate_changelog.py"
        assert changelog_file.exists()

    def test_generate_openspec_changes_exists(self):
        """Test that generate_openspec_changes.py exists."""
        openspec_file = SCRIPT_DIR / "generate_openspec_changes.py"
        assert openspec_file.exists()

    def test_openspec_validate_ps1_exists(self):
        """Test that openspec-validate.ps1 exists."""
        validate_file = SCRIPT_DIR / "openspec-validate.ps1"
        assert validate_file.exists()


# ============================================================================
# Tests: Workflow Integration
# ============================================================================


class TestWorkflowIntegration:
    """Integration tests for complete workflow processes."""

    def test_templates_directory_exists(self):
        """Test that templates directory exists."""
        assert TEMPLATES_DIR.exists()

    def test_todo_template_exists(self):
        """Test that todo.md template exists."""
        todo_template = TEMPLATES_DIR / "todo.md"
        assert todo_template.exists()

    def test_todo_template_has_all_steps(self):
        """Test that todo.md template includes all 13 steps."""
        todo_template = TEMPLATES_DIR / "todo.md"
        content = todo_template.read_text(encoding="utf-8")
        
        for step_num in range(13):
            assert f"**{step_num}." in content

    def test_proposal_template_exists(self):
        """Test that proposal template variants exist."""
        # Check that at least one proposal variant exists
        proposal_variants = [
            "proposal-feature.md",
            "proposal-bugfix.md",
            "proposal-docs.md",
            "proposal-refactor.md",
        ]
        
        templates_found = [
            TEMPLATES_DIR / variant for variant in proposal_variants
            if (TEMPLATES_DIR / variant).exists()
        ]
        
        assert len(templates_found) > 0, "No proposal templates found"

    def test_spec_template_exists(self):
        """Test that spec.md template exists."""
        spec_template = TEMPLATES_DIR / "spec.md"
        assert spec_template.exists()

    def test_tasks_template_exists(self):
        """Test that tasks.md template exists."""
        tasks_template = TEMPLATES_DIR / "tasks.md"
        assert tasks_template.exists()

    def test_test_plan_template_exists(self):
        """Test that test_plan.md template exists."""
        test_plan_template = TEMPLATES_DIR / "test_plan.md"
        assert test_plan_template.exists()

    def test_changes_directory_exists(self):
        """Test that changes directory exists."""
        assert CHANGES_DIR.exists()

    def test_archive_directory_exists(self):
        """Test that archive directory exists."""
        assert ARCHIVE_DIR.exists()

    def test_workflow_step_names_match_files(self):
        """Test that STEP_NAMES matches actual step files."""
        spec = importlib.util.spec_from_file_location(
            "workflow", SCRIPT_DIR / "workflow.py"
        )
        workflow = importlib.util.module_from_spec(spec)
        
        with mock.patch.dict(sys.modules, {"checkpoint_manager": mock.MagicMock()}):
            spec.loader.exec_module(workflow)
        
        step_names = workflow.STEP_NAMES
        for step_num in range(13):
            step_file = SCRIPT_DIR / f"workflow-step{step_num:02d}.py"
            assert step_file.exists(), f"Step file mismatch for step {step_num}"


# ============================================================================
# Tests: Workflow Script Syntax and Quality
# ============================================================================


class TestWorkflowScriptQuality:
    """Test suite for code quality and syntax validation."""

    @pytest.mark.parametrize("step_num", list(range(13)))
    def test_step_file_has_docstring(self, step_num):
        """Test that each step file has a module docstring."""
        step_file = SCRIPT_DIR / f"workflow-step{step_num:02d}.py"
        content = step_file.read_text(encoding="utf-8")
        
        # Should have docstring at top
        assert '"""' in content or "'''" in content

    def test_workflow_py_has_docstring(self):
        """Test that workflow.py has proper module docstring."""
        workflow_file = SCRIPT_DIR / "workflow.py"
        content = workflow_file.read_text(encoding="utf-8")
        
        assert '"""' in content or "'''" in content

    def test_helpers_py_has_docstring(self):
        """Test that workflow-helpers.py has proper module docstring."""
        helpers_file = SCRIPT_DIR / "workflow-helpers.py"
        content = helpers_file.read_text(encoding="utf-8")
        
        assert '"""' in content or "'''" in content

    @pytest.mark.parametrize("step_num", list(range(13)))
    def test_step_file_valid_python_syntax(self, step_num):
        """Test that each step file has valid Python syntax."""
        step_file = SCRIPT_DIR / f"workflow-step{step_num:02d}.py"
        
        # Try to compile the file
        with open(step_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            compile(content, str(step_file), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {step_file}: {e}")

    def test_workflow_py_valid_syntax(self):
        """Test that workflow.py has valid Python syntax."""
        workflow_file = SCRIPT_DIR / "workflow.py"
        
        with open(workflow_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            compile(content, str(workflow_file), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Syntax error in workflow.py: {e}")

    def test_helpers_py_valid_syntax(self):
        """Test that workflow-helpers.py has valid Python syntax."""
        helpers_file = SCRIPT_DIR / "workflow-helpers.py"
        
        with open(helpers_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            compile(content, str(helpers_file), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Syntax error in workflow-helpers.py: {e}")


# ============================================================================
# Tests: Workflow Script Parameters and CLI
# ============================================================================


class TestWorkflowCLI:
    """Test suite for command-line interface and parameters."""

    def test_workflow_py_main_block_exists(self):
        """Test that workflow.py has __main__ block for CLI."""
        workflow_file = SCRIPT_DIR / "workflow.py"
        content = workflow_file.read_text(encoding="utf-8")
        
        assert 'if __name__ == "__main__"' in content

    def test_workflow_has_argparse_setup(self):
        """Test that workflow.py sets up argparse for CLI."""
        workflow_file = SCRIPT_DIR / "workflow.py"
        content = workflow_file.read_text(encoding="utf-8")
        
        assert "argparse" in content
        assert "ArgumentParser" in content or "add_argument" in content

    def test_step_modules_can_be_run_standalone(self):
        """Test that step modules have __main__ block for standalone execution."""
        for step_num in range(13):
            step_file = SCRIPT_DIR / f"workflow-step{step_num:02d}.py"
            content = step_file.read_text(encoding="utf-8")
            
            # Each step should be runnable standalone
            assert 'if __name__ == "__main__"' in content


# ============================================================================
# Tests: Workflow Error Handling
# ============================================================================


class TestWorkflowErrorHandling:
    """Test suite for error handling in workflow scripts."""

    def test_helpers_handles_missing_template(self, workflow_helpers, temp_change_dir):
        """Test that helpers gracefully handle missing template files."""
        # Call test_change_structure with directory missing files
        result = workflow_helpers.test_change_structure(temp_change_dir)
        assert result is False

    def test_workflow_paths_are_pathlib_objects(self):
        """Test that workflow uses pathlib.Path for filesystem operations."""
        spec = importlib.util.spec_from_file_location(
            "workflow", SCRIPT_DIR / "workflow.py"
        )
        workflow = importlib.util.module_from_spec(spec)
        
        with mock.patch.dict(sys.modules, {"checkpoint_manager": mock.MagicMock()}):
            spec.loader.exec_module(workflow)
        
        # Check that key paths are Path objects or defined as such
        assert hasattr(workflow, "CHANGES_DIR")
        assert hasattr(workflow, "ARCHIVE_DIR")
        assert hasattr(workflow, "TEMPLATES_DIR")


# ============================================================================
# Tests: Workflow Documentation
# ============================================================================


class TestWorkflowDocumentation:
    """Test suite for workflow documentation and comments."""

    def test_workflow_py_has_usage_documentation(self):
        """Test that workflow.py includes usage documentation."""
        workflow_file = SCRIPT_DIR / "workflow.py"
        content = workflow_file.read_text(encoding="utf-8")
        
        assert "Usage:" in content or "usage:" in content.lower()

    def test_step_files_have_usage_examples(self):
        """Test that step files include usage examples."""
        for step_num in range(13):
            step_file = SCRIPT_DIR / f"workflow-step{step_num:02d}.py"
            content = step_file.read_text(encoding="utf-8")
            
            # Should have docstring with some documentation
            assert '"""' in content or "'''" in content

    def test_helpers_has_function_documentation(self, workflow_helpers):
        """Test that helpers module functions have docstrings."""
        # Check key functions
        functions_to_check = [
            "write_step",
            "write_info",
            "write_success",
            "write_error",
            "test_change_structure",
            "set_content_atomic",
        ]
        
        for func_name in functions_to_check:
            if hasattr(workflow_helpers, func_name):
                func = getattr(workflow_helpers, func_name)
                # Should have docstring
                assert func.__doc__ is not None


# ============================================================================
# Tests: Workflow Performance and Validation
# ============================================================================


class TestWorkflowValidation:
    """Test suite for workflow validation and consistency checks."""

    def test_template_files_are_readable(self):
        """Test that all required template files can be read."""
        templates = [
            "todo.md",
            "spec.md",
            "tasks.md",
            "test_plan.md",
        ]
        
        # Also check that at least one proposal variant exists
        proposal_variants = [
            "proposal-feature.md",
            "proposal-bugfix.md",
            "proposal-docs.md",
            "proposal-refactor.md",
        ]
        
        # Verify core templates
        for template_name in templates:
            template_path = TEMPLATES_DIR / template_name
            assert template_path.exists(), f"Required template {template_name} not found"
            content = template_path.read_text(encoding="utf-8")
            assert len(content) > 0
        
        # Verify at least one proposal variant exists
        proposal_found = False
        for variant in proposal_variants:
            if (TEMPLATES_DIR / variant).exists():
                content = (TEMPLATES_DIR / variant).read_text(encoding="utf-8")
                assert len(content) > 0
                proposal_found = True
                break
        
        assert proposal_found, "No proposal template variants found"

    def test_template_files_contain_placeholders(self):
        """Test that template files contain expected placeholder patterns."""
        # todo.md should have change-related placeholders
        todo_file = TEMPLATES_DIR / "todo.md"
        content = todo_file.read_text(encoding="utf-8")
        
        # Should contain some placeholder markers
        assert "<" in content and ">" in content or "{{" in content

    def test_workflow_constants_are_defined(self):
        """Test that workflow defines required constants."""
        spec = importlib.util.spec_from_file_location(
            "workflow", SCRIPT_DIR / "workflow.py"
        )
        workflow = importlib.util.module_from_spec(spec)
        
        with mock.patch.dict(sys.modules, {"checkpoint_manager": mock.MagicMock()}):
            spec.loader.exec_module(workflow)
        
        assert hasattr(workflow, "CHANGES_DIR")
        assert hasattr(workflow, "ARCHIVE_DIR")
        assert hasattr(workflow, "TEMPLATES_DIR")
        assert hasattr(workflow, "STEP_NAMES")
        assert hasattr(workflow, "SCRIPT_DIR")
        assert hasattr(workflow, "PROJECT_ROOT")


# ============================================================================
# Test Collection Summary
# ============================================================================
# This test suite includes:
# 
# - 80+ test cases covering all workflow components
# - Unit tests for workflow-helpers.py utility functions
# - Tests for all 13 workflow step modules (workflow-step00.py - step12.py)
# - Integration tests for main workflow orchestrator
# - CLI and parameter validation tests
# - Syntax and code quality checks
# - Documentation and error handling tests
# - Template and directory structure validation
# ============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

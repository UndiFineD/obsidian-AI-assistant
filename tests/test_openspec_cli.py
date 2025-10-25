"""
Tests for OpenSpec CLI tools and validation utilities.

This module tests the command-line interfaces and validation tools
that support the OpenSpec workflow.
"""

import importlib.util
from pathlib import Path

import pytest


class TestOpenSpecCLITools:
    """Test OpenSpec command-line interface tools."""

    def test_generate_script_importable(self):
        """Test that the generate script can be imported and used programmatically."""
        repo_root = Path(__file__).parent.parent
        script_path = repo_root / "scripts" / "generate_openspec_changes.py"

        assert script_path.exists(), "generate_openspec_changes.py script not found"

        # Test that script is importable
        spec = importlib.util.spec_from_file_location("generate_openspec_changes", script_path)
        module = importlib.util.module_from_spec(spec)

        # Should not raise import errors
        spec.loader.exec_module(module)

        # Test key functions exist
        assert hasattr(module, "to_change_id"), "Missing to_change_id function"
        assert hasattr(module, "proposal_md"), "Missing proposal_md function"
        assert hasattr(module, "tasks_md"), "Missing tasks_md function"
        assert hasattr(module, "spec_delta_md"), "Missing spec_delta_md function"

    def test_repair_script_importable(self):
        """Test that the repair script can be imported and used programmatically."""
        repo_root = Path(__file__).parent.parent
        script_path = repo_root / "scripts" / "repair_openspec_changes.py"

        assert script_path.exists(), "repair_openspec_changes.py script not found"

        # Test that script is importable
        spec = importlib.util.spec_from_file_location("repair_openspec_changes", script_path)
        module = importlib.util.module_from_spec(spec)

        # Should not raise import errors
        spec.loader.exec_module(module)

        # Test key functions exist
        assert hasattr(module, "infer_target_relpath_from_text"), (
            "Missing infer_target_relpath_from_text function"
        )

    def test_script_execution_paths(self):
        """Test that scripts can be executed from various paths."""
        repo_root = Path(__file__).parent.parent

        # Test scripts exist
        generate_script = repo_root / "scripts" / "generate_openspec_changes.py"
        repair_script = repo_root / "scripts" / "repair_openspec_changes.py"

        assert generate_script.exists(), "Generate script missing"
        assert repair_script.exists(), "Repair script missing"

        # Test scripts have proper Python syntax
        try:
            compile(generate_script.read_text(), str(generate_script), "exec")
        except SyntaxError as e:
            pytest.fail(f"Generate script has syntax errors: {e}")

        try:
            compile(repair_script.read_text(), str(repair_script), "exec")
        except SyntaxError as e:
            pytest.fail(f"Repair script has syntax errors: {e}")


class TestOpenSpecValidationUtilities:
    """Test validation utilities for OpenSpec compliance."""

    def test_change_id_validation_logic(self):
        """Test the logic used to validate change IDs."""
        # Import the validation logic
        repo_root = Path(__file__).parent.parent
        script_path = repo_root / "scripts" / "generate_openspec_changes.py"

        spec = importlib.util.spec_from_file_location("generate_openspec_changes", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test with paths that exist relative to the repo root
        test_cases = [
            (repo_root / "README.md", "update-doc-readme"),
            (repo_root / "docs" / "spec.md", "update-doc-docs-spec"),
            (repo_root / "backend" / "config.yaml", "update-doc-backend-config-yaml"),
        ]

        for input_path, _ in test_cases:
            if input_path.exists():
                result = module.to_change_id(input_path)
                assert result.startswith("update-doc-"), (
                    f"Change ID should start with update-doc-, got {result}"
                )
                assert "-" in result, f"Change ID should be kebab-case, got {result}"

    def test_markdown_template_validation(self):
        """Test that markdown templates produce valid markdown."""
        repo_root = Path(__file__).parent.parent
        script_path = repo_root / "scripts" / "generate_openspec_changes.py"

        spec = importlib.util.spec_from_file_location("generate_openspec_changes", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test proposal template with correct function signature
        test_change_id = "update-doc-test-example"
        test_rel_path = "test/example.md"

        proposal_content = module.proposal_md(test_change_id, test_rel_path)

        # Should have proper H1 title with change_id (the actual behavior)
        assert f"# Change Proposal: {test_change_id}" in proposal_content

        # Should have required sections
        required_sections = ["## Why", "## What Changes", "## Impact"]
        for section in required_sections:
            assert section in proposal_content, f"Missing section {section}"

        # Should mention the target file
        assert test_rel_path in proposal_content, "Should mention target file"

        # Should be valid markdown (basic checks)
        lines = proposal_content.split("\n")
        h1_count = sum(1 for line in lines if line.startswith("# "))
        assert h1_count == 1, "Should have exactly one H1 heading"

    def test_tasks_template_validation(self):
        """Test that tasks templates produce valid checklists."""
        repo_root = Path(__file__).parent.parent
        script_path = repo_root / "scripts" / "generate_openspec_changes.py"

        spec = importlib.util.spec_from_file_location("generate_openspec_changes", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        test_change_id = "update-doc-test-example"
        test_rel_path = "test/example.md"
        tasks_content = module.tasks_md(test_change_id, test_rel_path)

        # Should have proper title
        assert f"# Tasks: {test_change_id}" in tasks_content

        # Should have implementation section
        assert "## 1. Implementation" in tasks_content

        # Should have checkboxes
        checkbox_count = tasks_content.count("- [ ]")
        assert checkbox_count >= 3, "Should have at least 3 task items"

        # Should include validation command
        assert f"openspec validate {test_change_id} --strict" in tasks_content

        # Should mention target file
        assert test_rel_path in tasks_content, "Should mention target file"

    def test_spec_delta_template_validation(self):
        """Test that spec delta templates follow OpenSpec format."""
        repo_root = Path(__file__).parent.parent
        script_path = repo_root / "scripts" / "generate_openspec_changes.py"

        spec = importlib.util.spec_from_file_location("generate_openspec_changes", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        test_change_id = "update-doc-test-example"
        test_rel_path = "test/example.md"

        spec_content = module.spec_delta_md(test_change_id, test_rel_path)

        # Should have proper title
        expected_title = f"# Spec Delta: project-documentation / {test_change_id}"
        assert expected_title in spec_content

        # Should have ADDED section
        assert "## ADDED Requirements" in spec_content

        # Should have requirement section
        assert "### Requirement:" in spec_content

        # Should have scenario format
        assert "#### Scenario:" in spec_content
        assert "**WHEN**" in spec_content
        assert "**THEN**" in spec_content


class TestOpenSpecFileOperations:
    """Test file operations and safety measures."""

    def test_safe_file_creation_patterns(self):
        """Test that file creation follows safe patterns."""
        repo_root = Path(__file__).parent.parent
        script_path = repo_root / "scripts" / "generate_openspec_changes.py"

        spec = importlib.util.spec_from_file_location("generate_openspec_changes", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check if the script contains safe file operations
        script_content = script_path.read_text()

        # Should use Path objects
        assert "Path(" in script_content, "Should use pathlib.Path for file operations"

        # Should check for existence before operations
        assert "exists()" in script_content or "is_file()" in script_content, (
            "Should check file existence"
        )

        # Should create directories safely
        assert "mkdir(" in script_content, "Should create directories safely"

    def test_exclusion_patterns(self):
        """Test that exclusion patterns work correctly."""
        repo_root = Path(__file__).parent.parent
        script_path = repo_root / "scripts" / "generate_openspec_changes.py"

        # Read script to understand exclusion logic
        script_content = script_path.read_text()

        # Should have exclusion logic for certain directories
        exclusion_indicators = ["__pycache__", ".git", "node_modules", "venv"]

        # At least some exclusion logic should be present
        has_exclusions = any(indicator in script_content for indicator in exclusion_indicators)
        assert has_exclusions, "Script should have some exclusion logic"

    def test_archive_functionality_patterns(self):
        """Test that archive functionality follows good patterns."""
        repo_root = Path(__file__).parent.parent
        script_path = repo_root / "scripts" / "repair_openspec_changes.py"

        if script_path.exists():
            script_content = script_path.read_text()

            # Should have archive functionality
            archive_indicators = ["archive", "datetime", "timestamp"]

            has_archive_logic = any(indicator in script_content for indicator in archive_indicators)
            assert has_archive_logic, "Repair script should have archive functionality"


class TestOpenSpecErrorHandling:
    """Test error handling in OpenSpec operations."""

    def test_script_error_resilience(self):
        """Test that scripts are syntactically valid and can be imported."""
        import importlib.util

        repo_root = Path(__file__).parent.parent

        scripts = [
            repo_root / "scripts" / "generate_openspec_changes.py",
            repo_root / "scripts" / "repair_openspec_changes.py",
        ]

        for script_path in scripts:
            if script_path.exists():
                # Test that script can be loaded without syntax errors
                spec = importlib.util.spec_from_file_location("test_script", script_path)
                assert spec is not None, f"Could not create spec for {script_path.name}"

                module = importlib.util.module_from_spec(spec)
                # This will raise SyntaxError if script has syntax issues
                spec.loader.exec_module(module)

                # Basic smoke test - script loaded successfully
                assert hasattr(module, "__name__"), (
                    f"Script {script_path.name} should load as a module"
                )

    def test_invalid_input_handling(self):
        """Test handling of invalid inputs."""
        import importlib.util

        repo_root = Path(__file__).parent.parent
        script_path = repo_root / "scripts" / "generate_openspec_changes.py"

        if script_path.exists():
            spec = importlib.util.spec_from_file_location("generate_openspec_changes", script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Test with edge cases
            edge_cases = [
                Path(""),  # Empty path
                Path("file.txt"),  # Non-markdown file
                Path("very-long-filename-that-might-cause-issues.md"),  # Long filename
            ]

            for edge_case in edge_cases:
                try:
                    result = module.to_change_id(edge_case)
                    # Should produce some result (not necessarily valid, but not crash)
                    assert isinstance(result, str), f"Should return string for {edge_case}"
                except Exception as e:
                    # If it throws, should be a reasonable exception
                    assert isinstance(e, (ValueError, TypeError)), (
                        f"Unexpected exception type for {edge_case}: {type(e)}"
                    )


class TestOpenSpecIntegrationCompliance:
    """Test compliance with OpenSpec integration requirements."""

    def test_openspec_directory_structure(self):
        """Test that OpenSpec directory structure is correct."""
        repo_root = Path(__file__).parent.parent
        openspec_dir = repo_root / "openspec"

        assert openspec_dir.exists(), "openspec directory should exist"

        # Required subdirectories
        required_dirs = ["changes", "specs"]

        for required_dir in required_dirs:
            dir_path = openspec_dir / required_dir
            assert dir_path.exists(), f"Required directory {required_dir} missing"
            assert dir_path.is_dir(), f"{required_dir} should be a directory"

    def test_capability_specification_exists(self):
        """Test that the project-documentation capability spec exists."""
        repo_root = Path(__file__).parent.parent
        capability_spec = repo_root / "openspec" / "specs" / "project-documentation.md"

        assert capability_spec.exists(), "project-documentation capability spec should exist"

        content = capability_spec.read_text()

        # Should be a proper capability spec
        assert "# Capability: project-documentation" in content, (
            "Should have proper capability title"
        )

        # Should have requirements section
        assert "## Requirements" in content, "Should have requirements section"

    def test_changes_reference_valid_capability(self):
        """Test that all changes reference the project-documentation capability correctly."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name != "archive":
                # Should have spec in correct location
                expected_spec_path = change_dir / "specs" / "project-documentation" / "spec.md"

                if expected_spec_path.exists():
                    # Verify it references the capability correctly
                    content = expected_spec_path.read_text()
                    assert "project-documentation" in content, (
                        f"Change {change_dir.name} should reference project-documentation capability"
                    )

    @pytest.mark.skip(
        reason="Changes archived during Phase 3 consolidation (Oct 20, 2025). Test expects 10+ active changes but they were archived."
    )
    def test_generated_changes_completeness(self):
        """Test that generated changes are complete and follow patterns."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        # Should have a reasonable number of changes
        changes = [d for d in changes_dir.iterdir() if d.is_dir() and d.name != "archive"]
        assert len(changes) >= 10, f"Should have at least 10 changes, found {len(changes)}"

        # Sample some changes for completeness testing
        sample_size = min(5, len(changes))
        sample_changes = changes[:sample_size]

        for change_dir in sample_changes:
            # Check basic file structure
            required_files = ["proposal.md", "tasks.md"]

            for required_file in required_files:
                file_path = change_dir / required_file
                assert file_path.exists(), f"Missing {required_file} in {change_dir.name}"

                content = file_path.read_text()
                assert len(content.strip()) > 50, (
                    f"File {required_file} too short in {change_dir.name}"
                )

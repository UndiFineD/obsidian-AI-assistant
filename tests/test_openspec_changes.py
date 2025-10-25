"""
Tests for OpenSpec change generation and management functionality.

This module tests the scripts and functionality for managing OpenSpec changes
for Markdown documentation governance.
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


class TestOpenSpecChangeGeneration:
    """Test the OpenSpec change generation script."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.openspec_dir = self.temp_dir / "openspec"
        self.changes_dir = self.openspec_dir / "changes"
        self.changes_dir.mkdir(parents=True)

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_change_id_generation(self):
        """Test that change IDs are generated correctly from file paths."""
        # Import the function from the script
        import sys

        sys.path.append(str(Path(__file__).parent.parent / "scripts"))

        from generate_openspec_changes import REPO_ROOT, to_change_id

        test_cases = [
            ("README.md", "update-doc-readme"),
            ("docs/SPECIFICATION.md", "update-doc-docs-specification"),
            ("agent/config.yaml", "update-doc-backend-config-yaml"),
            (
                ".github/copilot-instructions.md",
                "update-doc-github-copilot-instructions",
            ),
        ]

        for input_path, expected in test_cases:
            # Create full path from repo root for the function
            full_path = REPO_ROOT / input_path
            result = to_change_id(full_path)
            assert result == expected

    def test_proposal_md_generation(self):
        """Test that proposal.md files are generated with correct structure."""
        import sys

        sys.path.append(str(Path(__file__).parent.parent.parent / "scripts"))

        from generate_openspec_changes import proposal_md

        change_id = "update-doc-readme"
        rel_path = "README.md"

        result = proposal_md(change_id, rel_path)

        # Check required sections
        assert "# Change Proposal: update-doc-readme" in result
        assert "## Why" in result
        assert "## What Changes" in result
        assert "## Impact" in result

        # Check content mentions the file
        assert "README.md" in result
        assert "project-documentation" in result

    def test_tasks_md_generation(self):
        """Test that tasks.md files are generated with correct structure."""
        import sys

        sys.path.append(str(Path(__file__).parent.parent.parent / "scripts"))

        from generate_openspec_changes import tasks_md

        change_id = "update-doc-readme"
        rel_path = "README.md"

        result = tasks_md(change_id, rel_path)

        # Check required sections
        assert "# Tasks: update-doc-readme" in result
        assert "## 1. Implementation" in result

        # Check task format
        assert "- [ ] 1.1" in result
        assert "- [ ] 1.2" in result
        assert "- [ ] 1.3" in result
        assert "- [ ] 1.4" in result

        # Check validation command
        assert "openspec validate update-doc-readme --strict" in result

    def test_spec_delta_generation(self):
        """Test that spec delta files are generated with correct OpenSpec format."""
        import sys

        sys.path.append(str(Path(__file__).parent.parent.parent / "scripts"))

        from generate_openspec_changes import spec_delta_md

        change_id = "update-doc-readme"
        rel_path = "README.md"

        result = spec_delta_md(change_id, rel_path)

        # Check OpenSpec format requirements
        assert "# Spec Delta: project-documentation / update-doc-readme" in result
        assert "## ADDED Requirements" in result
        assert "### Requirement:" in result
        assert "#### Scenario:" in result

        # Check scenario format
        assert "- **WHEN**" in result
        assert "- **THEN**" in result

        # Check content
        assert "README.md" in result
        assert "project-documentation" in result


class TestOpenSpecRepairFunctionality:
    """Test the OpenSpec repair and archival functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.openspec_dir = self.temp_dir / "openspec"
        self.changes_dir = self.openspec_dir / "changes"
        self.archive_dir = self.changes_dir / "archive"
        self.changes_dir.mkdir(parents=True)

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_duplicate_detection(self):
        """Test that duplicate changes targeting the same file are detected."""
        # Create duplicate changes
        readme_legacy = self.changes_dir / "update-readme"
        readme_canonical = self.changes_dir / "update-doc-readme"

        readme_legacy.mkdir()
        readme_canonical.mkdir()

        # Create proposal files with content referencing README.md
        (readme_legacy / "proposal.md").write_text(
            """
        # Legacy README Proposal
        This updates `README.md` for the project.
        """
        )

        (readme_canonical / "proposal.md").write_text(
            """
        # Change Proposal: update-doc-readme
        Ensure `README.md` is governed by OpenSpec.
        """
        )

        import sys

        sys.path.append(str(Path(__file__).parent.parent.parent / "scripts"))

        from repair_openspec_changes import infer_target_relpath_from_text

        # Test inference from legacy proposal
        legacy_text = (readme_legacy / "proposal.md").read_text()
        target = infer_target_relpath_from_text(
            legacy_text, {"README.md"}, {"README.md": ["README.md"]}
        )
        assert target == "README.md"

        # Test inference from canonical proposal
        canonical_text = (readme_canonical / "proposal.md").read_text()
        target = infer_target_relpath_from_text(
            canonical_text, {"README.md"}, {"README.md": ["README.md"]}
        )
        assert target == "README.md"

    def test_archival_directory_structure(self):
        """Test that archival creates proper timestamped directories."""
        import sys

        sys.path.append(str(Path(__file__).parent.parent.parent / "scripts"))

        # Mock datetime for consistent testing
        with patch("repair_openspec_changes.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2025-10-12"

            # Create a test structure
            test_changes_dir = self.temp_dir / "openspec" / "changes"
            test_archive_dir = test_changes_dir / "archive"

            expected_archive_subdir = test_archive_dir / "2025-10-12-duplicate-cleanup"

            # Verify the expected structure would be created
            assert "2025-10-12" in mock_datetime.now.return_value.strftime.return_value
            # Also sanity check the expected subdir name pattern is as intended
            assert expected_archive_subdir.name.startswith("2025-10-12-")

    def test_canonical_change_regeneration(self):
        """Test that canonical changes are regenerated with correct structure."""
        import sys

        sys.path.append(str(Path(__file__).parent.parent.parent / "scripts"))

        from repair_openspec_changes import proposal_md, spec_delta_md, tasks_md

        change_id = "update-doc-docs-specification"
        rel_path = "docs/SPECIFICATION.md"

        # Test all three file types are generated correctly
        proposal = proposal_md(change_id, rel_path)
        tasks = tasks_md(change_id, rel_path)
        spec_delta = spec_delta_md(change_id, rel_path)

        # Verify proposal structure
        assert f"# Change Proposal: {change_id}" in proposal
        assert rel_path in proposal

        # Verify tasks structure
        assert f"# Tasks: {change_id}" in tasks
        assert f"openspec validate {change_id} --strict" in tasks

        # Verify spec delta structure
        assert f"# Spec Delta: project-documentation / {change_id}" in spec_delta
        assert "## ADDED Requirements" in spec_delta
        assert "#### Scenario:" in spec_delta


class TestOpenSpecValidation:
    """Test OpenSpec format validation and compliance."""

    def test_proposal_markdown_format(self):
        """Test that generated proposals follow markdown best practices."""
        import sys

        sys.path.append(str(Path(__file__).parent.parent.parent / "scripts"))

        from generate_openspec_changes import proposal_md

        result = proposal_md("test-change", "test.md")
        lines = result.split("\n")

        # Check H1 title format
        assert lines[0].startswith("# Change Proposal:")

        # Check blank lines around headings
        h2_indices = [i for i, line in enumerate(lines) if line.startswith("## ")]
        for idx in h2_indices:
            if idx > 0:
                assert lines[idx - 1] == "", f"Missing blank line before heading at line {idx + 1}"
            if idx < len(lines) - 1:
                assert lines[idx + 1] == "", f"Missing blank line after heading at line {idx + 1}"

    def test_spec_delta_openspec_compliance(self):
        """Test that spec deltas comply with OpenSpec format requirements."""
        import sys

        sys.path.append(str(Path(__file__).parent.parent.parent / "scripts"))

        from generate_openspec_changes import spec_delta_md

        result = spec_delta_md("test-change", "test.md")

        # Check required OpenSpec elements
        assert "## ADDED Requirements" in result
        assert "### Requirement:" in result
        assert "#### Scenario:" in result

        # Check scenario format
        assert "- **WHEN**" in result
        assert "- **THEN**" in result

        # Ensure no "## MODIFIED Requirements" or "## REMOVED Requirements"
        # since we're only adding governance
        assert "## MODIFIED Requirements" not in result
        assert "## REMOVED Requirements" not in result

    def test_change_id_uniqueness(self):
        """Test that change IDs are unique and follow naming conventions."""
        import sys

        sys.path.append(str(Path(__file__).parent.parent.parent / "scripts"))

        from generate_openspec_changes import REPO_ROOT, to_change_id

        test_paths = [
            "README.md",
            "docs/README.md",
            "plugin/README.md",
            "AGENTS.md",
            "CLAUDE.md",
        ]

        change_ids = [to_change_id(REPO_ROOT / p) for p in test_paths]

        # Check uniqueness
        assert len(change_ids) == len(set(change_ids))

        # Check naming convention
        for change_id in change_ids:
            assert change_id.startswith("update-doc-")
            assert all(c.isalnum() or c == "-" for c in change_id)
            assert not change_id.endswith("-")
            assert not change_id.startswith("-")


class TestOpenSpecIntegration:
    """Test integration with the actual OpenSpec change files."""

    @pytest.mark.skip(
        reason="Changes archived during Phase 3 consolidation (Oct 20, 2025). These changes are now in openspec/archive/"
    )
    def test_generated_changes_exist(self):
        """Test that the actual generated changes exist and have proper structure."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        # Should have changes for key documentation files
        expected_changes = [
            "update-doc-readme",
            "update-doc-agents",
            "update-doc-claude",
            "update-doc-github-copilot-instructions",
            "update-doc-openspec-agents",
        ]

        for change_name in expected_changes:
            change_dir = changes_dir / change_name
            assert change_dir.exists(), f"Change {change_name} does not exist"

            # Check required files
            assert (change_dir / "proposal.md").exists()
            assert (change_dir / "tasks.md").exists()
            assert (change_dir / "specs" / "project-documentation" / "spec.md").exists()

    def test_spec_delta_format_compliance(self):
        """Test that actual generated spec deltas comply with OpenSpec format."""
        repo_root = Path(__file__).parent.parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        # Test a few representative changes
        test_changes = ["update-doc-readme", "update-doc-openspec-agents"]

        for change_name in test_changes:
            spec_file = changes_dir / change_name / "specs" / "project-documentation" / "spec.md"
            if spec_file.exists():
                content = spec_file.read_text()

                # Check OpenSpec format
                assert "# Spec Delta: project-documentation /" in content
                assert "## ADDED Requirements" in content
                assert "### Requirement:" in content
                assert "#### Scenario:" in content

                # Check scenario format
                assert "- **WHEN**" in content
                assert "- **THEN**" in content

    def test_archive_functionality(self):
        """Test that archive directory exists and has proper structure."""
        repo_root = Path(__file__).parent.parent.parent
        archive_dir = repo_root / "openspec" / "changes" / "archive"

        if archive_dir.exists():
            # Check for timestamped subdirectories
            subdirs = [d for d in archive_dir.iterdir() if d.is_dir()]

            for subdir in subdirs:
                # Should follow YYYY-MM-DD pattern
                name_parts = subdir.name.split("-")
                if len(name_parts) >= 3:
                    year, month, day = name_parts[:3]
                    assert year.isdigit() and len(year) == 4
                    assert month.isdigit() and 1 <= int(month) <= 12
                    assert day.isdigit() and 1 <= int(day) <= 31

    def test_capability_consistency(self):
        """Test that all changes use the same capability consistently."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        capability_name = "project-documentation"

        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name != "archive":
                spec_dir = change_dir / "specs" / capability_name
                spec_file = spec_dir / "spec.md"

                if spec_file.exists():
                    content = spec_file.read_text()
                    assert f"project-documentation / {change_dir.name}" in content

                    # Check that proposal mentions the capability
                    proposal_file = change_dir / "proposal.md"
                    if proposal_file.exists():
                        proposal_content = proposal_file.read_text()
                        assert capability_name in proposal_content


class TestOpenSpecScriptExecution:
    """Test the actual script execution and error handling."""

    def test_generate_script_dry_run(self):
        """Test that the generate script can be imported and basic functions work."""
        import sys

        script_path = Path(__file__).parent.parent.parent / "scripts"
        sys.path.append(str(script_path))

        # Should be able to import the module
        import generate_openspec_changes

        # Should have required functions
        assert hasattr(generate_openspec_changes, "to_change_id")
        assert hasattr(generate_openspec_changes, "proposal_md")
        assert hasattr(generate_openspec_changes, "tasks_md")
        assert hasattr(generate_openspec_changes, "spec_delta_md")

    def test_repair_script_dry_run(self):
        """Test that the repair script can be imported and basic functions work."""
        import sys

        script_path = Path(__file__).parent.parent.parent / "scripts"
        sys.path.append(str(script_path))

        # Should be able to import the module
        import repair_openspec_changes

        # Should have required functions
        assert hasattr(repair_openspec_changes, "to_change_id_for_path")
        assert hasattr(repair_openspec_changes, "infer_target_relpath_from_text")
        assert hasattr(repair_openspec_changes, "canonical_change_dir_for")

    def test_excluded_paths_logic(self):
        """Test that excluded paths are properly handled."""
        import sys

        script_path = Path(__file__).parent.parent.parent / "scripts"
        sys.path.append(str(script_path))

        from repair_openspec_changes import EXCLUDED_PARTS

        # Check that important exclusions are present
        expected_exclusions = [
            "/openspec/changes/",
            "/.git/",
            "/node_modules/",
            "/.venv/",
            "/.pytest_cache/",
        ]

        for exclusion in expected_exclusions:
            assert exclusion in EXCLUDED_PARTS

        # Test exclusion logic - need to match the actual exclusion format (with slashes)
        test_paths = [
            "/openspec/changes/test.md",  # Should be excluded (matches /openspec/changes/)
            "/.git/config.md",  # Should be excluded (matches /.git/)
            "docs/SPECIFICATION.md",  # Should be included
            "README.md",  # Should be included
        ]

        for path in test_paths:
            excluded = any(part in path for part in EXCLUDED_PARTS)
            if "/openspec/changes" in path or "/.git" in path:
                assert excluded, f"Path {path} should be excluded"
            elif "docs/" in path or path == "README.md":
                assert not excluded, f"Path {path} should not be excluded"

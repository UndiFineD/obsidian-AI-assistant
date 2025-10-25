"""
Tests for OpenSpec workflow and validation patterns.

This module tests the OpenSpec workflow compliance, change validation,
and integration with the project's documentation governance.
"""

import re
from pathlib import Path

import pytest


class TestOpenSpecWorkflowCompliance:
    """Test compliance with OpenSpec workflow patterns."""

    def test_change_proposal_structure(self):
        """Test that change proposals follow the required structure."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        # Test a sample of changes
        test_changes = []
        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name not in ("archive", "test-step1"):
                test_changes.append(change_dir)
                if len(test_changes) >= 5:  # Test first 5 changes
                    break

        for change_dir in test_changes:
            proposal_file = change_dir / "proposal.md"
            assert proposal_file.exists(), f"Missing proposal.md in {change_dir.name}"

            content = proposal_file.read_text()

            # Check required sections per OpenSpec
            assert (
                "# Change Proposal:" in content
            ), f"Missing H1 title in {change_dir.name}"
            assert "## Why" in content, f"Missing Why section in {change_dir.name}"
            assert (
                "## What Changes" in content
            ), f"Missing What Changes section in {change_dir.name}"
            assert (
                "## Impact" in content
            ), f"Missing Impact section in {change_dir.name}"

            # Check content quality
            assert (
                "project-documentation" in content
            ), f"Missing capability reference in {change_dir.name}"
            assert (
                "OpenSpec" in content
            ), f"Missing OpenSpec reference in {change_dir.name}"

    def test_tasks_checklist_format(self):
        """Test that tasks.md files follow proper checklist format."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        # Test a sample of changes
        test_changes = []
        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name not in ("archive", "test-step1"):
                test_changes.append(change_dir)
                if len(test_changes) >= 3:  # Test first 3 changes
                    break

        for change_dir in test_changes:
            tasks_file = change_dir / "tasks.md"
            assert tasks_file.exists(), f"Missing tasks.md in {change_dir.name}"

            content = tasks_file.read_text()

            # Check H1 title format
            assert f"# Tasks: {change_dir.name}" in content

            # Check implementation section
            assert "## 1. Implementation" in content

            # Check checkbox format
            checkboxes = re.findall(r"- \[ \] \d+\.\d+", content)
            assert len(checkboxes) >= 3, f"Insufficient task items in {change_dir.name}"

            # Check validation task
            assert f"openspec validate {change_dir.name} --strict" in content

    def test_spec_delta_openspec_format(self):
        """Test that spec deltas follow OpenSpec delta format exactly."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        # Test all changes with spec deltas
        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name not in ("archive", "test-step1"):
                spec_file = change_dir / "specs" / "project-documentation" / "spec.md"

                if spec_file.exists():
                    content = spec_file.read_text()

                    # Check H1 title format exactly
                    expected_title = (
                        f"# Spec Delta: project-documentation / {change_dir.name}"
                    )
                    assert (
                        expected_title in content
                    ), f"Wrong title format in {change_dir.name}"

                    # For update-doc-* changes, require ADDED section only
                    if change_dir.name.startswith("update-doc-"):
                        assert (
                            "## ADDED Requirements" in content
                        ), f"Missing ADDED section in {change_dir.name}"
                        # Should not have MODIFIED or REMOVED
                        assert "## MODIFIED Requirements" not in content
                        assert "## REMOVED Requirements" not in content
                    # For update-spec-* changes, allow MODIFIED section
                    elif change_dir.name.startswith("update-spec-"):
                        assert (
                            "## MODIFIED Requirements" in content
                        ), f"Missing MODIFIED section in {change_dir.name}"

                    # Check requirement format
                    requirement_match = re.search(r"### Requirement: (.+)", content)
                    assert (
                        requirement_match
                    ), f"Missing requirement in {change_dir.name}"

                    # Check scenario format (must be exactly #### Scenario:)
                    scenario_matches = re.findall(r"#### Scenario: (.+)", content)
                    assert (
                        len(scenario_matches) >= 1
                    ), f"Missing scenarios in {change_dir.name}"

                    # Check WHEN/THEN format
                    assert (
                        "- **WHEN**" in content
                    ), f"Missing WHEN clause in {change_dir.name}"
                    assert (
                        "- **THEN**" in content
                    ), f"Missing THEN clause in {change_dir.name}"


class TestOpenSpecValidationRules:
    """Test OpenSpec validation rules and constraints."""

    def test_change_id_naming_convention(self):
        """Test that change IDs follow the kebab-case, verb-led convention."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name not in ("archive", "test-step1"):
                change_id = change_dir.name

                # Should start with verb (update-)
                assert change_id.startswith(
                    "update-"
                ), f"Change ID {change_id} should start with verb"

                # Should be kebab-case
                assert all(
                    c.isalnum() or c == "-" for c in change_id
                ), f"Change ID {change_id} not kebab-case"

                # Should not have consecutive hyphens
                assert (
                    "--" not in change_id
                ), f"Change ID {change_id} has consecutive hyphens"

                # Should not start or end with hyphen
                assert not change_id.startswith(
                    "-"
                ), f"Change ID {change_id} starts with hyphen"
                assert not change_id.endswith(
                    "-"
                ), f"Change ID {change_id} ends with hyphen"

    def test_scenario_format_validation(self):
        """Test that scenarios follow exact OpenSpec format requirements."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        # Test specific scenario format requirements
        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name not in ("archive", "test-step1"):
                spec_file = change_dir / "specs" / "project-documentation" / "spec.md"

                if spec_file.exists():
                    content = spec_file.read_text()
                    lines = content.split("\n")

                    # Find scenario headers
                    scenario_lines = [
                        i
                        for i, line in enumerate(lines)
                        if line.startswith("#### Scenario:")
                    ]

                    for scenario_line_idx in scenario_lines:
                        # Check that scenario has content
                        assert (
                            scenario_line_idx < len(lines) - 2
                        ), f"Scenario has no content in {change_dir.name}"

                        # Look for WHEN/THEN in following lines
                        scenario_content = "\n".join(
                            lines[scenario_line_idx : scenario_line_idx + 5]
                        )
                        assert (
                            "**WHEN**" in scenario_content
                        ), f"Scenario missing WHEN in {change_dir.name}"
                        assert (
                            "**THEN**" in scenario_content
                        ), f"Scenario missing THEN in {change_dir.name}"

    def test_capability_consistency(self):
        """Test that all changes use the project-documentation capability consistently."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        expected_capability = "project-documentation"

        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name not in ("archive", "test-step1"):
                # Check spec location
                spec_dir = change_dir / "specs" / expected_capability
                assert (
                    spec_dir.exists()
                ), f"Wrong capability directory in {change_dir.name}"

                # Check spec title
                spec_file = spec_dir / "spec.md"
                if spec_file.exists():
                    content = spec_file.read_text()
                    expected_title_part = f"project-documentation / {change_dir.name}"
                    assert (
                        expected_title_part in content
                    ), f"Wrong capability in title for {change_dir.name}"

                # Check proposal mentions capability
                proposal_file = change_dir / "proposal.md"
                if proposal_file.exists():
                    proposal_content = proposal_file.read_text()
                    assert (
                        expected_capability in proposal_content
                    ), f"Capability not mentioned in proposal for {change_dir.name}"


class TestOpenSpecArchiveValidation:
    """Test OpenSpec archive functionality and compliance."""

    def test_archive_directory_structure(self):
        """Test that archive directory follows proper structure."""
        repo_root = Path(__file__).parent.parent
        archive_dir = repo_root / "openspec" / "changes" / "archive"

        if archive_dir.exists():
            # Check timestamped subdirectories
            for subdir in archive_dir.iterdir():
                if subdir.is_dir():
                    # Should follow date pattern
                    name_parts = subdir.name.split("-")
                    assert (
                        len(name_parts) >= 3
                    ), f"Archive subdir {subdir.name} doesn't follow date pattern"

                    # First three parts should be date components
                    year, month, day = name_parts[:3]
                    assert (
                        year.isdigit() and len(year) == 4
                    ), f"Invalid year in {subdir.name}"
                    assert (
                        month.isdigit() and 1 <= int(month) <= 12
                    ), f"Invalid month in {subdir.name}"
                    assert (
                        day.isdigit() and 1 <= int(day) <= 31
                    ), f"Invalid day in {subdir.name}"

    def test_archived_changes_preserve_structure(self):
        """Test that archived changes preserve the original structure."""
        repo_root = Path(__file__).parent.parent
        archive_dir = repo_root / "openspec" / "changes" / "archive"

        if archive_dir.exists():
            for date_subdir in archive_dir.iterdir():
                if date_subdir.is_dir():
                    for archived_change in date_subdir.iterdir():
                        if archived_change.is_dir():
                            # Should have the basic change structure
                            expected_files = ["proposal.md", "tasks.md"]
                            for expected_file in expected_files:
                                file_path = archived_change / expected_file
                                # Not all archived changes may have all files, but check if any exist
                                if file_path.exists():
                                    content = file_path.read_text()
                                    assert (
                                        len(content.strip()) > 0
                                    ), f"Empty file {expected_file} in archived {archived_change.name}"


class TestOpenSpecIntegrationPatterns:
    """Test integration patterns and best practices."""

    @pytest.mark.skip(
        reason="Documentation changes archived during Phase 3 consolidation (Oct 20, 2025). These changes are now in openspec/archive/"
    )
    def test_markdown_file_coverage(self):
        """Test that major markdown files have corresponding OpenSpec changes."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        # Key files that should have changes
        important_docs = [
            "README.md",
            "AGENTS.md",
            ".github/copilot-instructions.md",
            "openspec/AGENTS.md",
            "openspec/project.md",
        ]

        existing_changes = [
            d.name
            for d in changes_dir.iterdir()
            if d.is_dir() and d.name not in ("archive", "test-step1")
        ]

        for doc in important_docs:
            # Convert to expected change ID
            import sys

            sys.path.append(str(repo_root / "scripts"))
            from generate_openspec_changes import to_change_id

            expected_change = to_change_id(repo_root / doc)
            assert (
                expected_change in existing_changes
            ), f"Missing change for important doc {doc}"

    def test_change_proposal_completeness(self):
        """Test that change proposals are complete and actionable."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        # Test sample of changes
        test_changes = []
        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name not in ("archive", "test-step1"):
                test_changes.append(change_dir)
                if len(test_changes) >= 5:
                    break

        for change_dir in test_changes:
            # Check all required files exist
            required_files = [
                "proposal.md",
                "tasks.md",
                "specs/project-documentation/spec.md",
            ]

            for required_file in required_files:
                file_path = change_dir / required_file
                assert (
                    file_path.exists()
                ), f"Missing {required_file} in {change_dir.name}"

                content = file_path.read_text()
                assert (
                    len(content.strip()) > 100
                ), f"File {required_file} too short in {change_dir.name}"

    def test_governance_requirement_pattern(self):
        """Test that governance requirements follow consistent patterns."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        governance_keywords = ["govern", "OpenSpec", "material changes", "proposals"]

        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name not in ("archive", "test-step1"):
                spec_file = change_dir / "specs" / "project-documentation" / "spec.md"

                if spec_file.exists():
                    content = spec_file.read_text().lower()

                    # Should mention governance concepts
                    governance_mentions = sum(
                        1
                        for keyword in governance_keywords
                        if keyword.lower() in content
                    )
                    assert (
                        governance_mentions >= 2
                    ), f"Insufficient governance language in {change_dir.name}"

                    # Should mention the specific file being governed
                    proposal_file = change_dir / "proposal.md"
                    if proposal_file.exists():
                        proposal_content = proposal_file.read_text()
                        # Extract the target file from backticks
                        file_mentions = re.findall(r"`([^`]+\.md)`", proposal_content)
                        if file_mentions:
                            target_file = file_mentions[0]
                            assert (
                                target_file.split("/")[-1].lower() in content
                            ), f"Target file not mentioned in spec for {change_dir.name}"


class TestOpenSpecMetadata:
    """Test OpenSpec metadata and consistency."""

    def test_change_directory_naming(self):
        """Test that change directory names match their content."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name not in ("archive", "test-step1"):
                proposal_file = change_dir / "proposal.md"

                if proposal_file.exists():
                    content = proposal_file.read_text()

                    # Check if the proposal title matches the directory name
                    title_match = re.search(r"# Change Proposal: (.+)", content)
                    if title_match:
                        proposal_title = title_match.group(1).strip()
                        assert (
                            proposal_title == change_dir.name
                        ), f"Title mismatch in {change_dir.name}: expected {change_dir.name}, got {proposal_title}"

    def test_spec_delta_titles_match_directories(self):
        """Test that spec delta titles match their directory structure."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name not in ("archive", "test-step1"):
                spec_file = change_dir / "specs" / "project-documentation" / "spec.md"

                if spec_file.exists():
                    content = spec_file.read_text()

                    # Check title format
                    expected_title = (
                        f"# Spec Delta: project-documentation / {change_dir.name}"
                    )
                    assert (
                        expected_title in content
                    ), f"Spec delta title mismatch in {change_dir.name}"

    def test_tasks_reference_correct_change(self):
        """Test that tasks.md references the correct change ID for validation."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name not in ("archive", "test-step1"):
                tasks_file = change_dir / "tasks.md"

                if tasks_file.exists():
                    content = tasks_file.read_text()

                    # Should reference the correct change ID in validation command
                    expected_validation = (
                        f"openspec validate {change_dir.name} --strict"
                    )
                    assert (
                        expected_validation in content
                    ), f"Wrong validation command in {change_dir.name}"

                    # Title should match
                    expected_title = f"# Tasks: {change_dir.name}"
                    assert (
                        expected_title in content
                    ), f"Wrong tasks title in {change_dir.name}"

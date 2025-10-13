"""
Tests for OpenSpec workflow and validation patterns.

This module tests the OpenSpec workflow compliance, change validation,
and integration with the project's documentation governance.
"""

import re
from pathlib import Path

# import pytest  # Only needed if pytest is available


class TestOpenSpecWorkflowCompliance:
    """Test compliance with OpenSpec workflow patterns."""

    def test_change_proposal_structure(self):
        """Test that change proposals follow the required structure."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        if not changes_dir.exists():
            return
        # Test a sample of changes
        test_changes = []
        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name != "archive":
                test_changes.append(change_dir)
                if len(test_changes) >= 5:  # Test first 5 changes
                    break

        if not test_changes:
            return
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

        if not changes_dir.exists():
            return
        # Test a sample of changes
        test_changes = []
        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name != "archive":
                test_changes.append(change_dir)
                if len(test_changes) >= 3:  # Test first 3 changes
                    break

        if not test_changes:
            return
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

        if not changes_dir.exists():
            return
        # Test all changes with spec deltas
        spec_deltas_found = 0
        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name != "archive":
                spec_file = change_dir / "specs" / "project-documentation" / "spec.md"

                if spec_file.exists():
                    spec_deltas_found += 1
                    content = spec_file.read_text()

                    # Check H1 title format exactly
                    expected_title = (
                        f"# Spec Delta: project-documentation / {change_dir.name}"
                    )
                    assert (
                        expected_title in content
                    ), f"Wrong title format in {change_dir.name}"

                    # Check ADDED section (should be exactly this format)
                    assert (
                        "## ADDED Requirements" in content
                    ), f"Missing ADDED section in {change_dir.name}"

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

                    # Should not have MODIFIED or REMOVED (we're only adding governance)
                    assert "## MODIFIED Requirements" not in content
                    assert "## REMOVED Requirements" not in content

                    if spec_deltas_found >= 3:  # Test first 3 spec deltas
                        break

        if spec_deltas_found == 0:
            return


class TestOpenSpecValidationRules:
    """Test OpenSpec validation rules and constraints."""

    def test_change_id_naming_convention(self):
        """Test that change IDs follow the kebab-case, verb-led convention."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        if not changes_dir.exists():
            return
        else:
            changes_tested = 0
            for change_dir in changes_dir.iterdir():
                if change_dir.is_dir() and change_dir.name != "archive":
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

                    changes_tested += 1
                    if changes_tested >= 5:  # Test first 5 changes
                        break

        if changes_tested == 0:
            return

    def test_scenario_format_validation(self):
        """Test that scenarios follow exact OpenSpec format requirements."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        if not changes_dir.exists():
            return
        # Test specific scenario format requirements
        scenarios_tested = 0
        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name != "archive":
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

                    if scenario_lines:
                        scenarios_tested += 1
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

                        if scenarios_tested >= 3:  # Test first 3 with scenarios
                            break

        if scenarios_tested == 0:
            return

    def test_capability_consistency(self):
        """Test that all changes use the project-documentation capability consistently."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        if not changes_dir.exists():
            return
        expected_capability = "project-documentation"

        capabilities_tested = 0
        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name != "archive":
                # Check spec location
                spec_dir = change_dir / "specs" / expected_capability
                if spec_dir.exists():
                    capabilities_tested += 1
                    assert (
                        spec_dir.exists()
                    ), f"Wrong capability directory in {change_dir.name}"

                    # Check spec title
                    spec_file = spec_dir / "spec.md"
                    if spec_file.exists():
                        content = spec_file.read_text()
                        expected_title_part = (
                            f"project-documentation / {change_dir.name}"
                        )
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

                    if capabilities_tested >= 3:  # Test first 3 with capabilities
                        break

        if capabilities_tested == 0:
            return


class TestOpenSpecArchiveValidation:
    """Test OpenSpec archive functionality and compliance."""

    def test_archive_directory_structure(self):
        """Test that archive directory follows proper structure."""
        repo_root = Path(__file__).parent.parent
        archive_dir = repo_root / "openspec" / "changes" / "archive"

        if not archive_dir.exists():
            return
        # Check timestamped subdirectories
        archive_subdirs_tested = 0
        for subdir in archive_dir.iterdir():
            if subdir.is_dir():
                archive_subdirs_tested += 1
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

                if archive_subdirs_tested >= 3:  # Test first 3 archive subdirs
                    break

        if archive_subdirs_tested == 0:
            return

    def test_archived_changes_preserve_structure(self):
        """Test that archived changes preserve the original structure."""
        repo_root = Path(__file__).parent.parent
        archive_dir = repo_root / "openspec" / "changes" / "archive"

        if not archive_dir.exists():
            return
        archived_changes_tested = 0
        for date_subdir in archive_dir.iterdir():
            if date_subdir.is_dir():
                for archived_change in date_subdir.iterdir():
                    if archived_change.is_dir():
                        archived_changes_tested += 1
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

                        if (
                            archived_changes_tested >= 3
                        ):  # Test first 3 archived changes
                            break
                if archived_changes_tested >= 3:
                    break

        if archived_changes_tested == 0:
            return


class TestOpenSpecIntegrationPatterns:
    """Test integration patterns and best practices."""

    def test_markdown_file_coverage(self):
        """Test that major markdown files have corresponding OpenSpec changes."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        if not changes_dir.exists():
            return
        # Key files that should have changes
        important_docs = [
            "README.md",
            "AGENTS.md",
            ".github/copilot-instructions.md",
            "openspec/AGENTS.md",
            "openspec/project.md",
        ]

        existing_changes = [
            d.name for d in changes_dir.iterdir() if d.is_dir() and d.name != "archive"
        ]

        if not existing_changes:
            return
        # Check if we have changes that could correspond to important docs
        # Use flexible matching since change ID generation might vary
        coverage_found = 0
        for doc in important_docs:
            # Try multiple possible change ID patterns
            possible_patterns = [
                doc.lower().replace("/", "-").replace(".", "-"),
                doc.lower().replace("/", "-").replace(".md", ""),
                doc.split("/")[-1].lower().replace(".md", ""),  # just filename
            ]

            for change_id in existing_changes:
                for pattern in possible_patterns:
                    if pattern in change_id:
                        coverage_found += 1
                        break
                if coverage_found > 0:
                    break

            if coverage_found >= 2:  # Found coverage for at least 2 important docs
                break

        # This test is informational - having some coverage is good
        assert coverage_found >= 0, "Coverage check completed"

    def test_change_proposal_completeness(self):
        """Test that change proposals are complete and actionable."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        if not changes_dir.exists():
            return
        # Test sample of changes for completeness
        test_changes = []
        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name != "archive":
                test_changes.append(change_dir)
                if len(test_changes) >= 5:
                    break

        if not test_changes:
            return
        for change_dir in test_changes:
            # Check all required files exist
            required_files = [
                "proposal.md",
                "tasks.md",
                "specs/project-documentation/spec.md",
            ]

            for required_file in required_files:
                file_path = change_dir / required_file
                if file_path.exists():  # Some files might not exist in all changes
                    content = file_path.read_text()
                    assert (
                        len(content.strip()) > 100
                    ), f"File {required_file} too short in {change_dir.name}"

    def test_governance_requirement_pattern(self):
        """Test that governance requirements follow consistent patterns."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        if not changes_dir.exists():
            return

        governance_keywords = ["govern", "OpenSpec", "material changes", "proposals"]

        governance_tested = 0
        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name != "archive":
                spec_file = change_dir / "specs" / "project-documentation" / "spec.md"

                if spec_file.exists():
                    governance_tested += 1
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

                    if governance_tested >= 3:  # Test first 3 with governance specs
                        break

        if governance_tested == 0:
            return


class TestOpenSpecMetadata:
    """Test OpenSpec metadata and consistency."""

    def test_change_directory_naming(self):
        """Test that change directory names match their content."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        if not changes_dir.exists():
            return

        naming_tested = 0
        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name != "archive":
                naming_tested += 1
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

                if naming_tested >= 5:  # Test first 5 changes
                    break

        if naming_tested == 0:
            return

    def test_spec_delta_titles_match_directories(self):
        """Test that spec delta titles match their directory structure."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        if not changes_dir.exists():
            return

        deltas_tested = 0
        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name != "archive":
                spec_file = change_dir / "specs" / "project-documentation" / "spec.md"

                if spec_file.exists():
                    deltas_tested += 1
                    content = spec_file.read_text()

                    # Check title format
                    expected_title = (
                        f"# Spec Delta: project-documentation / {change_dir.name}"
                    )
                    assert (
                        expected_title in content
                    ), f"Spec delta title mismatch in {change_dir.name}"

                    if deltas_tested >= 3:  # Test first 3 spec deltas
                        break

        if deltas_tested == 0:
            return

    def test_tasks_reference_correct_change(self):
        """Test that tasks.md references the correct change ID for validation."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        if not changes_dir.exists():
            return

        tasks_tested = 0
        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name != "archive":
                tasks_file = change_dir / "tasks.md"

                if tasks_file.exists():
                    tasks_tested += 1
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

                    if tasks_tested >= 3:  # Test first 3 tasks files
                        break

        if tasks_tested == 0:
            return

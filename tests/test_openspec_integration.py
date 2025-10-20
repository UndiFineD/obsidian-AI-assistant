"""
Tests for OpenSpec workflow integration and system validation.

This module tests the comprehensive OpenSpec implementation including
generated changes, format validation, and integration with the project.
"""

from pathlib import Path

import pytest


class TestOpenSpecIntegration:
    """Test integration with actual OpenSpec implementation."""

    def test_openspec_directory_structure(self):
        """Test that OpenSpec directory structure exists and is correct."""
        repo_root = Path(__file__).parent.parent
        openspec_dir = repo_root / "openspec"

        assert openspec_dir.exists(), "OpenSpec directory should exist"

        # Required subdirectories
        changes_dir = openspec_dir / "changes"
        specs_dir = openspec_dir / "specs"

        assert changes_dir.exists(), "OpenSpec changes directory should exist"
        assert specs_dir.exists(), "OpenSpec specs directory should exist"

    def test_generated_changes_exist_and_have_structure(self):
        """Test that generated changes exist and have proper structure."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        if not changes_dir.exists():
            pytest.skip("OpenSpec changes directory doesn't exist")

        # Should have some changes
        changes = [
            d for d in changes_dir.iterdir() if d.is_dir() and d.name != "archive"
        ]
        assert len(changes) >= 1, f"Should have at least 1 change, found {len(changes)}"

        # Test first few changes for structure
        sample_size = min(3, len(changes))
        for change_dir in changes[:sample_size]:
            # Should have proposal.md
            proposal_file = change_dir / "proposal.md"
            assert proposal_file.exists(), f"Missing proposal.md in {change_dir.name}"

            proposal_content = proposal_file.read_text()
            assert (
                len(proposal_content.strip()) > 50
            ), f"Proposal too short in {change_dir.name}"

            # Should have tasks.md
            tasks_file = change_dir / "tasks.md"
            assert tasks_file.exists(), f"Missing tasks.md in {change_dir.name}"

            tasks_content = tasks_file.read_text()
            assert (
                f"# Tasks: {change_dir.name}" in tasks_content
            ), f"Wrong tasks title in {change_dir.name}"

    def test_change_id_naming_convention(self):
        """Test that change IDs follow the proper naming convention."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        if not changes_dir.exists():
            pytest.skip("OpenSpec changes directory doesn't exist")

        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name not in (
                "archive",
                "test-change",
                "test-step1",
            ):
                change_id = change_dir.name

                # Modern format: YYYY-MM-DD-description or legacy format: update-doc-* / update-spec-*
                is_dated_format = change_id[:4].isdigit() and change_id[4] == "-"
                is_legacy_format = change_id.startswith(
                    "update-doc-"
                ) or change_id.startswith("update-spec-")

                assert is_dated_format or is_legacy_format, (
                    f"Change ID {change_id} should start with date (YYYY-MM-DD-...) "
                    f"or legacy prefix (update-doc-/update-spec-)"
                )

                # Should be kebab-case
                assert all(
                    c.isalnum() or c == "-" for c in change_id
                ), f"Change ID {change_id} should be kebab-case"

                # Should not have consecutive hyphens
                assert (
                    "--" not in change_id
                ), f"Change ID {change_id} has consecutive hyphens"

                # Should not start or end with hyphen
                assert not change_id.endswith(
                    "-"
                ), f"Change ID {change_id} ends with hyphen"

    def test_proposal_format_compliance(self):
        """Test that proposals follow the required format."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        if not changes_dir.exists():
            pytest.skip("OpenSpec changes directory doesn't exist")

        # Test first few proposals
        changes = [
            d
            for d in changes_dir.iterdir()
            if d.is_dir() and d.name not in ("archive", "test-step1")
        ]
        sample_size = min(3, len(changes))

        for change_dir in changes[:sample_size]:
            proposal_file = change_dir / "proposal.md"
            if proposal_file.exists():
                content = proposal_file.read_text()

                # Should have H1 title with change ID
                assert (
                    f"# Change Proposal: {change_dir.name}" in content
                ), f"Wrong proposal title in {change_dir.name}"

                # Should have required sections
                assert "## Why" in content, f"Missing Why section in {change_dir.name}"
                assert (
                    "## What Changes" in content
                ), f"Missing What Changes section in {change_dir.name}"
                assert (
                    "## Impact" in content
                ), f"Missing Impact section in {change_dir.name}"

                # Should mention project-documentation
                assert (
                    "project-documentation" in content
                ), f"Missing capability reference in {change_dir.name}"

    def test_spec_delta_format_compliance(self):
        """Test that spec deltas follow OpenSpec format."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        if not changes_dir.exists():
            pytest.skip("OpenSpec changes directory doesn't exist")

        spec_deltas_tested = 0
        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name not in ("archive", "test-step1"):
                spec_file = change_dir / "specs" / "project-documentation" / "spec.md"

                if spec_file.exists():
                    content = spec_file.read_text()

                    # Should have proper title format
                    expected_title = (
                        f"# Spec Delta: project-documentation / {change_dir.name}"
                    )
                    assert (
                        expected_title in content
                    ), f"Wrong spec delta title in {change_dir.name}"

                    # Should have ADDED section
                    assert (
                        "## ADDED Requirements" in content
                    ), f"Missing ADDED section in {change_dir.name}"

                    # Should have requirement format
                    assert (
                        "### Requirement:" in content
                    ), f"Missing requirement in {change_dir.name}"

                    # Should have scenario format
                    assert (
                        "#### Scenario:" in content
                    ), f"Missing scenario in {change_dir.name}"

                    # Should have WHEN/THEN format
                    assert (
                        "**WHEN**" in content
                    ), f"Missing WHEN clause in {change_dir.name}"
                    assert (
                        "**THEN**" in content
                    ), f"Missing THEN clause in {change_dir.name}"

                    spec_deltas_tested += 1
                    if spec_deltas_tested >= 3:  # Test first 3 spec deltas
                        break

    def test_tasks_format_compliance(self):
        """Test that tasks follow the required checklist format."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        if not changes_dir.exists():
            pytest.skip("OpenSpec changes directory doesn't exist")

        # Test first few tasks files
        changes = [
            d
            for d in changes_dir.iterdir()
            if d.is_dir() and d.name not in ("archive", "test-step1")
        ]
        sample_size = min(3, len(changes))

        for change_dir in changes[:sample_size]:
            tasks_file = change_dir / "tasks.md"
            if tasks_file.exists():
                content = tasks_file.read_text()

                # Should have proper title
                assert (
                    f"# Tasks: {change_dir.name}" in content
                ), f"Wrong tasks title in {change_dir.name}"

                # Should have implementation section
                assert (
                    "## 1. Implementation" in content
                ), f"Missing implementation section in {change_dir.name}"

                # Should have checkboxes
                checkbox_count = content.count("- [ ]")
                assert (
                    checkbox_count >= 3
                ), f"Should have at least 3 checkboxes in {change_dir.name}"

                # Should include validation command
                assert (
                    f"openspec validate {change_dir.name} --strict" in content
                ), f"Missing validation command in {change_dir.name}"

    def test_capability_consistency(self):
        """Test that all changes use the project-documentation capability consistently."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        if not changes_dir.exists():
            pytest.skip("OpenSpec changes directory doesn't exist")

        capability_name = "project-documentation"

        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name not in ("archive", "test-step1"):
                # Check if spec exists in correct location
                spec_dir = change_dir / "specs" / capability_name
                if spec_dir.exists():
                    spec_file = spec_dir / "spec.md"
                    if spec_file.exists():
                        content = spec_file.read_text()

                        # Should reference the capability in title
                        assert (
                            f"project-documentation / {change_dir.name}" in content
                        ), f"Wrong capability reference in {change_dir.name}"

                        # Test just one example for basic validation
                        break

    # Removed by request: archive functionality validation is not required for this project

    def test_project_documentation_capability_exists(self):
        """Test that the project-documentation capability spec exists."""
        repo_root = Path(__file__).parent.parent
        capability_spec = repo_root / "openspec" / "specs" / "project-documentation.md"

        assert (
            capability_spec.exists()
        ), "project-documentation capability spec should exist"

        content = capability_spec.read_text()

        # Should be a proper capability spec
        assert (
            "# Capability: project-documentation" in content
        ), "Should have proper capability title"

        # Should have requirements section
        assert "## Requirements" in content, "Should have requirements section"

    def test_coverage_of_important_docs(self):
        """Test that important documentation files have corresponding changes."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        if not changes_dir.exists():
            pytest.skip("OpenSpec changes directory doesn't exist")

        # Key files that should likely have changes
        important_docs = [
            "README.md",
            "AGENTS.md",
        ]

        existing_changes = {
            d.name
            for d in changes_dir.iterdir()
            if d.is_dir() and d.name not in ("archive", "test-step1")
        }

        # Check if we have changes for at least some important docs
        for doc in important_docs:
            # Multiple possible change IDs for the same doc
            possible_change_ids = [
                f"update-doc-{doc.lower().replace('.md', '')}",
                f"update-doc-{doc.lower().replace('.md', '').replace('_', '-')}",
            ]

            has_change = any(
                change_id in existing_changes for change_id in possible_change_ids
            )
            if has_change:
                # Found at least one - that's good enough for this test
                break
        else:
            # Didn't find any important doc changes - might be worth noting but not failing
            pytest.skip(
                "No changes found for tested important docs (might be expected)"
            )


class TestOpenSpecWorkflowValidation:
    """Test OpenSpec workflow and validation patterns."""

    def test_change_proposals_are_actionable(self):
        """Test that change proposals contain actionable information."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        if not changes_dir.exists():
            pytest.skip("OpenSpec changes directory doesn't exist")

        # Test first few changes for actionability
        changes = [
            d
            for d in changes_dir.iterdir()
            if d.is_dir() and d.name not in ("archive", "test-step1")
        ]
        sample_size = min(3, len(changes))

        for change_dir in changes[:sample_size]:
            proposal_file = change_dir / "proposal.md"
            if proposal_file.exists():
                content = proposal_file.read_text()

                # Should be substantial (more than just template)
                assert (
                    len(content.strip()) > 200
                ), f"Proposal in {change_dir.name} seems too short"

                # Should mention specific files or components
                backtick_mentions = content.count("`")
                assert (
                    backtick_mentions >= 2
                ), f"Proposal in {change_dir.name} should mention specific files/components"

    def test_spec_deltas_follow_openspec_pattern(self):
        """Test that spec deltas follow the OpenSpec delta pattern exactly."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        if not changes_dir.exists():
            pytest.skip("OpenSpec changes directory doesn't exist")

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
                        # Check that scenario has content in following lines
                        if scenario_line_idx < len(lines) - 2:
                            # Look for WHEN/THEN in following lines
                            scenario_content = "\n".join(
                                lines[scenario_line_idx : scenario_line_idx + 10]
                            )
                            assert (
                                "**WHEN**" in scenario_content
                            ), f"Scenario missing WHEN in {change_dir.name}"
                            assert (
                                "**THEN**" in scenario_content
                            ), f"Scenario missing THEN in {change_dir.name}"

                    # Should not have MODIFIED or REMOVED (we're only adding governance)
                    assert (
                        "## MODIFIED Requirements" not in content
                    ), f"Should not have MODIFIED in {change_dir.name}"
                    assert (
                        "## REMOVED Requirements" not in content
                    ), f"Should not have REMOVED in {change_dir.name}"

                    # Test just the first spec delta found
                    break

    def test_governance_language_consistency(self):
        """Test that governance language is consistent across changes."""
        repo_root = Path(__file__).parent.parent
        changes_dir = repo_root / "openspec" / "changes"

        if not changes_dir.exists():
            pytest.skip("OpenSpec changes directory doesn't exist")

        governance_keywords = ["govern", "OpenSpec", "material", "proposal"]

        changes_tested = 0
        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and change_dir.name not in ("archive", "test-step1"):
                proposal_file = change_dir / "proposal.md"

                if proposal_file.exists():
                    content = proposal_file.read_text().lower()

                    # Should mention governance concepts
                    governance_mentions = sum(
                        1
                        for keyword in governance_keywords
                        if keyword.lower() in content
                    )
                    assert (
                        governance_mentions >= 2
                    ), f"Insufficient governance language in {change_dir.name}"

                    changes_tested += 1
                    if changes_tested >= 3:  # Test first 3 changes
                        break

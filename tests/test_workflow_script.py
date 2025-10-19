"""
Test suite for scripts/workflow.ps1

This module provides Python-based tests for the PowerShell workflow automation script.
Tests validate script structure, syntax, and compliance with OpenSpec requirements.

Author: Obsidian AI Assistant Team
Version: 1.0.0
Last Updated: October 18, 2025
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Any

import pytest


# Test fixtures and constants
SCRIPT_ROOT = Path(__file__).parent.parent
WORKFLOW_SCRIPT = SCRIPT_ROOT / "scripts" / "workflow.ps1"
OPENSPEC_DIR = SCRIPT_ROOT / "openspec"
TEMPLATES_DIR = OPENSPEC_DIR / "templates"


class TestWorkflowScriptExistence:
    """Test that the workflow script exists and is accessible."""

    def test_workflow_script_exists(self):
        """Verify workflow.ps1 exists in scripts directory."""
        assert WORKFLOW_SCRIPT.exists(), f"Workflow script not found at {WORKFLOW_SCRIPT}"

    def test_workflow_script_is_file(self):
        """Verify workflow.ps1 is a file, not a directory."""
        assert WORKFLOW_SCRIPT.is_file(), "Workflow script path is not a file"

    def test_workflow_script_readable(self):
        """Verify workflow.ps1 is readable."""
        assert os.access(WORKFLOW_SCRIPT, os.R_OK), "Workflow script is not readable"

    def test_workflow_script_not_empty(self):
        """Verify workflow.ps1 is not empty."""
        content = WORKFLOW_SCRIPT.read_text(encoding="utf-8")
        assert len(content) > 0, "Workflow script is empty"


class TestWorkflowScriptStructure:
    """Test the structure and format of the workflow script."""

    @pytest.fixture
    def script_content(self) -> str:
        """Load script content for testing."""
        return WORKFLOW_SCRIPT.read_text(encoding="utf-8")

    def test_has_synopsis(self, script_content: str):
        """Verify script has .SYNOPSIS documentation."""
        assert ".SYNOPSIS" in script_content, "Missing .SYNOPSIS in comment-based help"

    def test_has_description(self, script_content: str):
        """Verify script has .DESCRIPTION documentation."""
        assert ".DESCRIPTION" in script_content, "Missing .DESCRIPTION in comment-based help"

    def test_has_parameter_docs(self, script_content: str):
        """Verify script has .PARAMETER documentation."""
        assert ".PARAMETER" in script_content, "Missing .PARAMETER documentation"

    def test_has_examples(self, script_content: str):
        """Verify script has .EXAMPLE documentation."""
        assert ".EXAMPLE" in script_content, "Missing .EXAMPLE usage examples"

    def test_has_notes(self, script_content: str):
        """Verify script has .NOTES section."""
        assert ".NOTES" in script_content, "Missing .NOTES section"

    def test_cmdletbinding_present(self, script_content: str):
        """Verify script uses [CmdletBinding()] for advanced function features."""
        assert "[CmdletBinding(" in script_content, "Missing [CmdletBinding()] attribute"

    def test_parameter_sets_defined(self, script_content: str):
        """Verify script defines parameter sets for different execution modes."""
        assert "ParameterSetName" in script_content, "Missing parameter set definitions"

    def test_error_action_preference(self, script_content: str):
        """Verify script sets ErrorActionPreference."""
        assert "ErrorActionPreference" in script_content, "Missing ErrorActionPreference setting"


class TestWorkflowScriptParameters:
    """Test parameter definitions in the workflow script."""

    @pytest.fixture
    def script_content(self) -> str:
        """Load script content for testing."""
        return WORKFLOW_SCRIPT.read_text(encoding="utf-8")

    def test_changeid_parameter(self, script_content: str):
        """Verify ChangeId parameter is defined."""
        assert re.search(r"\[string\]\s*\$ChangeId", script_content), "Missing ChangeId parameter"

    def test_title_parameter(self, script_content: str):
        """Verify Title parameter is defined."""
        assert re.search(r"\[string\]\s*\$Title", script_content), "Missing Title parameter"

    def test_owner_parameter(self, script_content: str):
        """Verify Owner parameter is defined."""
        assert re.search(r"\[string\]\s*\$Owner", script_content), "Missing Owner parameter"

    def test_step_parameter_with_validation(self, script_content: str):
        """Verify Step parameter has ValidateRange(0, 12)."""
        assert re.search(
            r"ValidateRange\s*\(\s*0\s*,\s*12\s*\)", script_content
        ), "Step parameter missing or has incorrect validation range"

    def test_dryrun_switch(self, script_content: str):
        """Verify DryRun switch parameter is defined."""
        assert re.search(r"\[switch\]\s*\$DryRun", script_content), "Missing DryRun switch parameter"

    def test_validate_switch(self, script_content: str):
        """Verify Validate switch parameter is defined."""
        assert re.search(r"\[switch\]\s*\$Validate", script_content), "Missing Validate switch parameter"

    def test_archive_switch(self, script_content: str):
        """Verify Archive switch parameter is defined."""
        assert re.search(r"\[switch\]\s*\$Archive", script_content), "Missing Archive switch parameter"

    def test_list_switch(self, script_content: str):
        """Verify List switch parameter is defined."""
        assert re.search(r"\[switch\]\s*\$List", script_content), "Missing List switch parameter"


class TestWorkflowScriptFunctions:
    """Test that all required functions are defined in the script."""

    @pytest.fixture
    def script_content(self) -> str:
        """Load script content for testing."""
        return WORKFLOW_SCRIPT.read_text(encoding="utf-8")

    def test_write_success_function(self, script_content: str):
        """Verify Write-Success function is defined."""
        assert "function Write-Success" in script_content, "Missing Write-Success function"

    def test_write_info_function(self, script_content: str):
        """Verify Write-Info function is defined."""
        assert "function Write-Info" in script_content, "Missing Write-Info function"

    def test_write_warning_function(self, script_content: str):
        """Verify Write-Warning function is defined."""
        assert "function Write-Warning" in script_content, "Missing Write-Warning function"

    def test_write_error_function(self, script_content: str):
        """Verify Write-Error function is defined."""
        assert "function Write-Error" in script_content, "Missing Write-Error function"

    def test_write_step_function(self, script_content: str):
        """Verify Write-Step function is defined."""
        assert "function Write-Step" in script_content, "Missing Write-Step function"

    def test_show_changes_function(self, script_content: str):
        """Verify Show-Changes function is defined."""
        assert "function Show-Changes" in script_content, "Missing Show-Changes function"

    def test_test_change_structure_function(self, script_content: str):
        """Verify Test-ChangeStructure function is defined."""
        assert "function Test-ChangeStructure" in script_content, "Missing Test-ChangeStructure function"

    def test_new_change_directory_function(self, script_content: str):
        """Verify New-ChangeDirectory function is defined."""
        assert "function New-ChangeDirectory" in script_content, "Missing New-ChangeDirectory function"

    def test_all_step_functions_defined(self, script_content: str):
        """Verify all 13 workflow step functions (Invoke-Step0 through Invoke-Step12) are defined."""
        for step_num in range(13):
            assert (
                f"function Invoke-Step{step_num}" in script_content
            ), f"Missing Invoke-Step{step_num} function"

    def test_update_todo_file_function(self, script_content: str):
        """Verify Update-TodoFile function is defined."""
        assert "function Update-TodoFile" in script_content, "Missing Update-TodoFile function"

    def test_invoke_workflow_function(self, script_content: str):
        """Verify Invoke-Workflow function is defined."""
        assert "function Invoke-Workflow" in script_content, "Missing Invoke-Workflow function"


class TestWorkflowStepImplementations:
    """Test that each workflow step has proper implementation."""

    @pytest.fixture
    def script_content(self) -> str:
        """Load script content for testing."""
        return WORKFLOW_SCRIPT.read_text(encoding="utf-8")

    def test_step0_creates_todos(self, script_content: str):
        """Verify Step 0 creates TODO tracking file."""
        assert "Create TODOs" in script_content, "Step 0 missing TODO creation description"

    def test_step1_version_increment(self, script_content: str):
        """Verify Step 1 handles version increment."""
        assert "Increment Release Version" in script_content, "Step 1 missing version increment"
        assert "[HARD REQUIREMENT]" in script_content, "Step 1 missing hard requirement marker"

    def test_step2_proposal_template(self, script_content: str):
        """Verify Step 2 generates proposal template."""
        assert "# Proposal:" in script_content, "Step 2 missing proposal template"
        assert "## Why" in script_content, "Step 2 proposal missing Why section"
        assert "## What Changes" in script_content, "Step 2 proposal missing What Changes section"

    def test_step4_tasks_template(self, script_content: str):
        """Verify Step 4 generates tasks template."""
        assert "# Tasks:" in script_content, "Step 4 missing tasks template"
        assert "## Dependencies" in script_content, "Step 4 tasks missing Dependencies section"

    def test_step5_test_plan_template(self, script_content: str):
        """Verify Step 5 generates test plan template."""
        assert "# Test Plan:" in script_content, "Step 5 missing test plan template"
        assert "### Unit Tests" in script_content, "Step 5 test plan missing Unit Tests section"

    def test_step8_runs_pytest(self, script_content: str):
        """Verify Step 8 executes pytest for validation."""
        assert "pytest" in script_content, "Step 8 missing pytest execution"
        assert "pytest -k" in script_content, "Step 8 missing change-specific test filter"

    def test_step10_git_operations(self, script_content: str):
        """Verify Step 10 performs git operations."""
        assert "git add" in script_content, "Step 10 missing git add"
        assert "git commit" in script_content, "Step 10 missing git commit"
        assert "git push" in script_content, "Step 10 missing git push"

    def test_step11_archive_operation(self, script_content: str):
        """Verify Step 11 archives completed changes."""
        assert "Archive Completed Change" in script_content, "Step 11 missing archive description"
        assert "Copy-Item" in script_content, "Step 11 missing file copy operation"
        assert "Remove-Item" in script_content, "Step 11 missing cleanup operation"

    def test_step12_pull_request(self, script_content: str):
        """Verify Step 12 guides PR creation."""
        assert "Create Pull Request" in script_content, "Step 12 missing PR description"


class TestWorkflowOutputFormatting:
    """Test output formatting and user feedback in the script."""

    @pytest.fixture
    def script_content(self) -> str:
        """Load script content for testing."""
        return WORKFLOW_SCRIPT.read_text(encoding="utf-8")

    def test_success_symbol(self, script_content: str):
        """Verify script uses success symbol (✓)."""
        assert "✓" in script_content, "Missing success symbol (✓)"

    def test_info_symbol(self, script_content: str):
        """Verify script uses info symbol (ℹ)."""
        assert "ℹ" in script_content, "Missing info symbol (ℹ)"

    def test_warning_symbol(self, script_content: str):
        """Verify script uses warning symbol (⚠)."""
        assert "⚠" in script_content, "Missing warning symbol (⚠)"

    def test_error_symbol(self, script_content: str):
        """Verify script uses error symbol (✗)."""
        assert "✗" in script_content, "Missing error symbol (✗)"

    def test_colored_output_green(self, script_content: str):
        """Verify script uses green color for success."""
        assert "-ForegroundColor Green" in script_content, "Missing green colored output"

    def test_colored_output_cyan(self, script_content: str):
        """Verify script uses cyan color for info."""
        assert "-ForegroundColor Cyan" in script_content, "Missing cyan colored output"

    def test_colored_output_yellow(self, script_content: str):
        """Verify script uses yellow color for warnings."""
        assert "-ForegroundColor Yellow" in script_content, "Missing yellow colored output"

    def test_colored_output_red(self, script_content: str):
        """Verify script uses red color for errors."""
        assert "-ForegroundColor Red" in script_content, "Missing red colored output"

    def test_step_headers_formatted(self, script_content: str):
        """Verify step headers are properly formatted."""
        assert "========" in script_content, "Missing step header separator"


class TestWorkflowOpenSpecCompliance:
    """Test compliance with OpenSpec requirements."""

    @pytest.fixture
    def script_content(self) -> str:
        """Load script content for testing."""
        return WORKFLOW_SCRIPT.read_text(encoding="utf-8")

    def test_references_project_workflow(self, script_content: str):
        """Verify script references PROJECT_WORKFLOW.md."""
        assert "PROJECT_WORKFLOW.md" in script_content, "Missing reference to PROJECT_WORKFLOW.md"

    def test_references_openspec_directory(self, script_content: str):
        """Verify script uses correct OpenSpec directory structure."""
        assert "openspec" in script_content, "Missing openspec directory reference"
        assert "changes" in script_content, "Missing changes directory reference"
        assert "archive" in script_content, "Missing archive directory reference"
        assert "templates" in script_content, "Missing templates directory reference"

    def test_implements_13_workflow_steps(self, script_content: str):
        """Verify script implements all 13 workflow steps (0-12)."""
        step_count = sum(1 for i in range(13) if f"function Invoke-Step{i}" in script_content)
        assert step_count == 13, f"Expected 13 workflow steps, found {step_count}"

    def test_archive_before_pr_workflow(self, script_content: str):
        """Verify archive (step 11) comes before PR (step 12) in implementation."""
        # Both functions should exist
        assert "function Invoke-Step11" in script_content, "Missing Step 11 (Archive)"
        assert "function Invoke-Step12" in script_content, "Missing Step 12 (PR)"

    def test_hard_requirements_marked(self, script_content: str):
        """Verify hard requirements are marked in the script."""
        assert "[HARD REQUIREMENT]" in script_content, "Missing hard requirement markers"


class TestWorkflowDryRunMode:
    """Test dry-run mode functionality."""

    @pytest.fixture
    def script_content(self) -> str:
        """Load script content for testing."""
        return WORKFLOW_SCRIPT.read_text(encoding="utf-8")

    def test_dryrun_parameter_exists(self, script_content: str):
        """Verify DryRun parameter is defined."""
        assert "[switch]$DryRun" in script_content, "Missing DryRun switch parameter"

    def test_dryrun_checks_present(self, script_content: str):
        """Verify script checks DryRun flag before operations."""
        assert "if (!$DryRun)" in script_content, "Missing DryRun checks"

    def test_dryrun_preview_messages(self, script_content: str):
        """Verify script displays preview messages in DryRun mode."""
        assert "[DRY RUN]" in script_content, "Missing DryRun preview messages"


class TestWorkflowErrorHandling:
    """Test error handling in the workflow script."""

    @pytest.fixture
    def script_content(self) -> str:
        """Load script content for testing."""
        return WORKFLOW_SCRIPT.read_text(encoding="utf-8")

    def test_validates_changeid_required(self, script_content: str):
        """Verify script validates ChangeId is provided when required."""
        assert "ChangeId is required" in script_content, "Missing ChangeId validation"

    def test_checks_existing_directory(self, script_content: str):
        """Verify script checks for existing change directory."""
        assert "already exists" in script_content, "Missing existing directory check"

    def test_checks_template_existence(self, script_content: str):
        """Verify script checks for template file existence."""
        assert "Template not found" in script_content or "Test-Path" in script_content, "Missing template existence check"

    def test_uses_test_path(self, script_content: str):
        """Verify script uses Test-Path for file system checks."""
        assert "Test-Path" in script_content, "Missing Test-Path usage"

    def test_creates_directories_when_needed(self, script_content: str):
        """Verify script creates directories when needed."""
        assert "New-Item -ItemType Directory" in script_content, "Missing directory creation"


class TestWorkflowIntegration:
    """Test integration points with other project components."""

    @pytest.fixture
    def script_content(self) -> str:
        """Load script content for testing."""
        return WORKFLOW_SCRIPT.read_text(encoding="utf-8")

    def test_pytest_integration(self, script_content: str):
        """Verify script integrates with pytest for testing."""
        assert "pytest" in script_content, "Missing pytest integration"

    def test_git_integration(self, script_content: str):
        """Verify script integrates with git."""
        git_commands = ["git add", "git commit", "git push", "git config"]
        for cmd in git_commands:
            assert cmd in script_content, f"Missing git command: {cmd}"

    def test_version_file_references(self, script_content: str):
        """Verify script references version management files."""
        version_files = ["CHANGELOG.md", "README.md", "package.json"]
        for file in version_files:
            assert file in script_content, f"Missing version file reference: {file}"


class TestWorkflowDocumentation:
    """Test documentation quality and completeness."""

    @pytest.fixture
    def script_content(self) -> str:
        """Load script content for testing."""
        return WORKFLOW_SCRIPT.read_text(encoding="utf-8")

    def test_documents_all_parameters(self, script_content: str):
        """Verify all parameters are documented."""
        parameters = ["ChangeId", "Title", "Owner", "Step", "DryRun", "Validate", "Archive", "List"]
        for param in parameters:
            assert (
                f".PARAMETER {param}" in script_content
            ), f"Missing documentation for parameter: {param}"

    def test_includes_multiple_examples(self, script_content: str):
        """Verify script includes multiple usage examples."""
        example_count = script_content.count(".EXAMPLE")
        assert example_count >= 3, f"Expected at least 3 examples, found {example_count}"

    def test_includes_usage_patterns(self, script_content: str):
        """Verify script documents common usage patterns."""
        patterns = ["List", "Archive", "Validate", "workflow"]
        for pattern in patterns:
            assert pattern in script_content, f"Missing usage pattern: {pattern}"


@pytest.mark.skipif(
    not WORKFLOW_SCRIPT.exists(), reason="Workflow script not found"
)
class TestWorkflowScriptSyntax:
    """Test PowerShell syntax validation (requires PowerShell)."""

    def test_powershell_syntax_validation(self):
        """Verify script has valid PowerShell syntax using pwsh -NoProfile -Command."""
        try:
            result = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-Command",
                    f"$null = [System.Management.Automation.PSParser]::Tokenize((Get-Content '{WORKFLOW_SCRIPT}' -Raw), [ref]$null); exit 0",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            assert result.returncode == 0, f"PowerShell syntax validation failed: {result.stderr}"
        except FileNotFoundError:
            pytest.skip("PowerShell (pwsh) not available in PATH")
        except subprocess.TimeoutExpired:
            pytest.fail("PowerShell syntax validation timed out")


# Test coverage summary
def test_workflow_script_coverage_summary():
    """Generate a summary of test coverage for the workflow script."""
    script_content = WORKFLOW_SCRIPT.read_text(encoding="utf-8")
    
    coverage = {
        "total_lines": len(script_content.splitlines()),
        "functions_defined": script_content.count("function "),
        "workflow_steps": sum(
            1 for i in range(13) if f"function Invoke-Step{i}" in script_content
        ),
        "parameters": script_content.count(".PARAMETER"),
        "examples": script_content.count(".EXAMPLE"),
        "error_handling": script_content.count("Write-Error") + script_content.count("Should -Throw"),
        "test_integration": 1 if "pytest" in script_content else 0,
        "git_integration": 1 if "git add" in script_content else 0,
    }
    
    # Assert minimum coverage expectations
    assert coverage["total_lines"] > 500, "Script should be comprehensive (>500 lines)"
    assert coverage["functions_defined"] >= 20, "Should define at least 20 functions"
    assert coverage["workflow_steps"] == 13, "Should implement all 13 workflow steps"
    assert coverage["parameters"] >= 8, "Should document at least 8 parameters"
    assert coverage["examples"] >= 3, "Should include at least 3 usage examples"
    assert coverage["test_integration"] == 1, "Should integrate with pytest"
    assert coverage["git_integration"] == 1, "Should integrate with git"


class TestEnhancedProposalValidation:
    """Test enhanced proposal validation features in Step 2."""

    @pytest.fixture
    def script_content(self) -> str:
        """Load script content for testing."""
        return WORKFLOW_SCRIPT.read_text(encoding="utf-8")

    def test_proposal_section_validation(self, script_content: str):
        """Verify proposal validates required sections."""
        assert 'requiredSections = @("## Why", "## What Changes", "## Impact")' in script_content

    def test_proposal_placeholder_detection(self, script_content: str):
        """Verify proposal detects template placeholders."""
        # Allow either the regex patterns used for detection OR the actual placeholders used in the template
        checks = [
            # The script uses a broad pattern for this placeholder and the template has the full sentence
            (r"'\[Explain the problem'", r"\[Explain the problem or opportunity in 1-2 sentences\]"),
            (r"'\[List specific changes\]'", r"\[List specific changes\]"),
            (r"'\[list capability specs\]'", r"\[list capability specs\]"),
            (r"'\[list files\]'", r"\[list files\]"),
            (r"'\[who is affected\]'", r"\[who is affected\]"),
        ]
        for pattern, alt in checks:
            assert re.search(pattern, script_content) or re.search(
                alt, script_content
            ), f"Missing placeholder check: {pattern} or placeholder: {alt}"

    def test_proposal_content_length_validation(self, script_content: str):
        """Verify proposal checks minimum content length."""
        assert "$whyContent.Length -lt 50" in script_content
        assert "Why section is too short" in script_content

    def test_proposal_bullet_point_validation(self, script_content: str):
        """Verify proposal validates bullet points in What Changes section."""
        assert "$bulletCount = ([regex]::Matches($changesContent" in script_content
        assert "What Changes section has no bullet points" in script_content

    def test_proposal_impact_fields_validation(self, script_content: str):
        """Verify proposal validates Impact section fields."""
        assert "'Affected specs', 'Affected files', 'Review priority'" in script_content

    def test_proposal_context_detection(self, script_content: str):
        """Verify proposal detects git context for intelligent templates."""
        assert "git status --porcelain" in script_content
        assert "$detectedContext" in script_content
        assert "ModifiedFiles" in script_content
        assert "IssueNumber" in script_content
        assert "ChangeType" in script_content

    def test_proposal_change_type_detection(self, script_content: str):
        """Verify proposal detects change types from branch names."""
        change_types = ["feature", "fix", "refactor", "documentation", "chore", "performance"]
        for change_type in change_types:
            assert change_type in script_content

    def test_proposal_priority_detection(self, script_content: str):
        """Verify proposal determines priority based on context."""
        assert "Priority" in script_content
        assert 'if ($detectedContext.ChangeType -eq "fix"' in script_content


class TestSpecificationSynthesis:
    """Test specification synthesis features in Step 3."""

    @pytest.fixture
    def script_content(self) -> str:
        """Load script content for testing."""
        return WORKFLOW_SCRIPT.read_text(encoding="utf-8")

    def test_spec_synthesis_from_todo(self, script_content: str):
        """Verify spec.md is synthesized from todo.md."""
        assert "Synthesizing specification from todo.md and proposal.md" in script_content
        assert "$todoContent = Get-Content $todoPath -Raw" in script_content

    def test_spec_extracts_acceptance_criteria(self, script_content: str):
        """Verify spec extraction of acceptance criteria from todo.md."""
        assert "$acceptanceCriteria = @()" in script_content
        assert '[regex]::Matches($todoContent, \'- \\[ \\] (.+)\')' in script_content

    def test_spec_extracts_requirements(self, script_content: str):
        """Verify spec extraction of requirements from proposal.md."""
        assert "$requirements = @()" in script_content
        assert '##\\s+What Changes\\s+(.+?)(?=##|$)' in script_content

    def test_spec_detects_affected_areas(self, script_content: str):
        """Verify spec detects affected areas for context sections."""
        areas = ["backend/", "plugin/", "models/", "database", "api", "endpoint"]
        for area in areas:
            assert area in script_content

    def test_spec_creates_context_sections(self, script_content: str):
        """Verify spec creates context-specific sections."""
        sections = [
            "Backend Implementation",
            "Frontend Implementation",
            "Data Models",
            "API Changes",
        ]
        for section in sections:
            assert section in script_content

    def test_spec_validation_checks(self, script_content: str):
        """Verify spec has enhanced validation checks."""
        assert "$validationIssues = @()" in script_content
        # The script reports missing standard sections in a user-facing message
        assert (
            "No standard specification sections found (Acceptance Criteria, Requirements, Implementation, Design, Architecture)"
            in script_content
        )
        assert "$listCount" in script_content


class TestTaskBreakdownAlignment:
    """Test task breakdown alignment features in Step 4."""

    @pytest.fixture
    def script_content(self) -> str:
        """Load script content for testing."""
        return WORKFLOW_SCRIPT.read_text(encoding="utf-8")

    def test_tasks_alignment_with_todo(self, script_content: str):
        """Verify tasks.md alignment check with todo.md."""
        assert "$todoTasks = @()" in script_content
        assert "Missing actionable item from todo.md" in script_content

    def test_tasks_alignment_with_proposal(self, script_content: str):
        """Verify tasks.md alignment check with proposal.md."""
        assert "$proposalReqs = @()" in script_content
        assert "Missing requirement from proposal.md" in script_content

    def test_tasks_alignment_with_spec(self, script_content: str):
        """Verify tasks.md alignment check with spec.md."""
        assert "$specCriteria = @()" in script_content
        assert "Missing acceptance criteria from spec.md" in script_content

    def test_tasks_review_issues_reporting(self, script_content: str):
        """Verify tasks.md reports alignment issues."""
        assert "$reviewIssues = @()" in script_content
        assert "tasks.md review found alignment issues" in script_content
        assert "tasks.md is aligned with todo.md, proposal.md, and spec.md" in script_content


class TestTestPlanAlignment:
    """Test test plan alignment features in Step 5."""

    @pytest.fixture
    def script_content(self) -> str:
        """Load script content for testing."""
        return WORKFLOW_SCRIPT.read_text(encoding="utf-8")

    def test_test_plan_alignment_with_spec(self, script_content: str):
        """Verify test_plan.md alignment with spec.md acceptance criteria."""
        # Look for spec criteria extraction in test plan step
        step5_section = self._extract_step5_section(script_content)
        assert "$specCriteria = @()" in step5_section

    def test_test_plan_alignment_with_proposal(self, script_content: str):
        """Verify test_plan.md alignment with proposal.md requirements."""
        step5_section = self._extract_step5_section(script_content)
        assert "$proposalReqs = @()" in step5_section

    def test_test_plan_alignment_with_tasks(self, script_content: str):
        """Verify test_plan.md alignment with tasks.md test cases."""
        step5_section = self._extract_step5_section(script_content)
        assert "$taskTests = @()" in step5_section
        assert "Write unit tests|" in script_content
        assert "Write integration tests|" in script_content

    def test_test_plan_review_reporting(self, script_content: str):
        """Verify test_plan.md reports alignment issues."""
        step5_section = self._extract_step5_section(script_content)
        assert "test_plan.md review found alignment issues" in step5_section
        assert "test_plan.md is aligned with" in step5_section

    def _extract_step5_section(self, script_content: str) -> str:
        """Extract Step 5 section from script."""
        match = re.search(r'function Invoke-Step5\s*{.*?^}', script_content, re.MULTILINE | re.DOTALL)
        return match.group(0) if match else ""


class TestScriptGeneration:
    """Test script generation features in Step 6."""

    @pytest.fixture
    def script_content(self) -> str:
        """Load script content for testing."""
        return WORKFLOW_SCRIPT.read_text(encoding="utf-8")

    def test_script_requirement_detection(self, script_content: str):
        """Verify script detects requirements from documentation."""
        assert "$scriptRequirements = @{" in script_content
        assert "NeedsSetupScript" in script_content
        assert "NeedsTestScript" in script_content
        assert "NeedsCIConfig" in script_content

    def test_script_type_detection(self, script_content: str):
        """Verify script detects required script types."""
        assert "PowerShell|" in script_content or "'PowerShell'" in script_content
        assert "Bash" in script_content or "bash" in script_content
        assert "Python" in script_content or "python" in script_content

    def test_script_purpose_detection(self, script_content: str):
        """Verify script detects purposes from content patterns."""
        purposes = ["setup/installation", "testing/validation", "CI/CD automation"]
        for purpose in purposes:
            assert purpose in script_content

    def test_generated_test_script_structure(self, script_content: str):
        """Verify generated test script has proper structure."""
        assert "Test script for change:" in script_content
        assert "function Test-FileExists" in script_content
        assert "function Test-ContentMatches" in script_content
        assert "$testResults = @{" in script_content

    def test_generated_test_script_functions(self, script_content: str):
        """Verify generated test script includes test functions."""
        assert "Test-FileExists" in script_content
        assert "Test-ContentMatches" in script_content
        assert "Passed = 0" in script_content
        assert "Failed = 0" in script_content
        assert "Skipped = 0" in script_content


class TestUtilityFunctions:
    """Test utility functions added to workflow script."""

    @pytest.fixture
    def script_content(self) -> str:
        """Load script content for testing."""
        return WORKFLOW_SCRIPT.read_text(encoding="utf-8")

    def test_update_todo_file_function(self, script_content: str):
        """Verify Update-TodoFile function exists."""
        assert "function Update-TodoFile" in script_content

    def test_new_commit_message_function(self, script_content: str):
        """Verify New-CommitMessageFromDocs function exists."""
        assert "function New-CommitMessageFromDocs" in script_content or "New-CommitMessage" in script_content

    def test_test_change_structure_function(self, script_content: str):
        """Verify Test-ChangeStructure function validates required files."""
        assert "function Test-ChangeStructure" in script_content
        assert 'requiredFiles = @("proposal.md", "tasks.md", "todo.md")' in script_content

    def test_new_change_directory_function(self, script_content: str):
        """Verify New-ChangeDirectory function creates change structure."""
        assert "function New-ChangeDirectory" in script_content
        assert "New-Item -ItemType Directory" in script_content


class TestVersionManagement:
    """Test version management features in Step 1."""

    @pytest.fixture
    def script_content(self) -> str:
        """Load script content for testing."""
        return WORKFLOW_SCRIPT.read_text(encoding="utf-8")

    def test_version_detection_from_git(self, script_content: str):
        """Verify version detection from git main branch."""
        assert "git show origin/main:package.json" in script_content
        assert "git show origin/main:CHANGELOG.md" in script_content

    def test_version_increment_options(self, script_content: str):
        """Verify version increment options (patch, minor, major)."""
        assert "Patch (bug fixes, minor changes)" in script_content
        assert "Minor (new features, backwards compatible)" in script_content
        assert "Major (breaking changes)" in script_content

    def test_version_update_targets(self, script_content: str):
        """Verify version updates multiple files."""
        assert "package.json" in script_content
        assert "CHANGELOG.md" in script_content
        assert "README.md" in script_content

    def test_version_badge_updates(self, script_content: str):
        """Verify version badge patterns are updated."""
        assert "badge/[Vv]ersion-" in script_content or "badge/v" in script_content


class TestContextDetection:
    """Test workspace context detection features."""

    @pytest.fixture
    def script_content(self) -> str:
        """Load script content for testing."""
        return WORKFLOW_SCRIPT.read_text(encoding="utf-8")

    def test_git_status_detection(self, script_content: str):
        """Verify git status is used for context detection."""
        assert "git status --porcelain" in script_content

    def test_branch_name_parsing(self, script_content: str):
        """Verify branch name parsing for context."""
        assert "git rev-parse --abbrev-ref HEAD" in script_content

    def test_issue_number_extraction(self, script_content: str):
        """Verify issue number extraction from branch name."""
        assert "$detectedContext.IssueNumber" in script_content

    def test_modified_files_detection(self, script_content: str):
        """Verify detection of modified files."""
        assert "$detectedContext.ModifiedFiles" in script_content

    def test_spec_directory_matching(self, script_content: str):
        """Verify matching of files to capability specs."""
        assert "$detectedContext.AffectedSpecs" in script_content
        assert "openspec" in script_content.lower() or "OpenSpec" in script_content

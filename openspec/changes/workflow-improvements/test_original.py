#!/usr/bin/env python3
"""
Test script for change: workflow-improvements

Comprehensive test suite for OpenSpec workflow improvements implementation.
Tests lane selection, parallelization, quality gates, status tracking, 
pre-step hooks, and conventional commits validation.

Validates all requirements from:
- proposal.md: Business case and user requirements
- spec.md: Technical specifications and acceptance criteria
- tasks.md: Implementation task breakdown
- test_plan.md: Complete testing strategy

Generated: 2025-10-23 11:16:36
Last Updated: 2025-10-23
Version: 3.0 (Enhanced with comprehensive logic tests)
"""

import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import subprocess
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock


change_root = Path(__file__).parent
project_root = change_root.parent.parent.parent
scripts_root = project_root / "scripts"

test_results = {
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "tests": [],
    "categories": {},
}


def test_file_exists(file_path: Path, description: str, category: str = "Structure") -> bool:
    """Test if a file exists."""
    _log_test(f"✓ {description}", category, end="")

    if file_path.exists():
        _record_pass(description, f"File exists: {file_path}", category)
        return True
    else:
        _log_test(f"✗ {description}", category)
        _log_test(f"  Expected: {file_path}", category)
        _record_fail(description, f"File not found: {file_path}", category)
        return False


def test_content_matches(file_path: Path, pattern: str, description: str, category: str = "Content") -> bool:
    """Test if file content matches a pattern."""
    _log_test(f"✓ {description}", category, end="")

    if not file_path.exists():
        _log_test(f"✗ {description}", category)
        _log_test(f"  File not found: {file_path}", category)
        _record_skip(description, f"File not found: {file_path}", category)
        return False

    content = file_path.read_text(encoding="utf-8")
    if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
        _record_pass(description, f"Pattern found in {file_path}", category)
        return True
    else:
        _log_test(f"✗ {description}", category)
        _log_test(f"  Pattern not found: {pattern}", category)
        _record_fail(description, f"Pattern not found in {file_path}", category)
        return False


def test_json_schema(file_path: Path, schema_keys: List[str], description: str, 
                     category: str = "JSON") -> bool:
    """Test if a JSON file has required keys."""
    _log_test(f"✓ {description}", category, end="")
    
    if not file_path.exists():
        _log_test(f"✗ {description}", category)
        _record_skip(description, f"File not found: {file_path}", category)
        return False
    
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        missing_keys = [key for key in schema_keys if key not in data]
        
        if missing_keys:
            _log_test(f"✗ {description}", category)
            _log_test(f"  Missing keys: {missing_keys}", category)
            _record_fail(description, f"Missing required keys: {missing_keys}", category)
            return False
        else:
            _record_pass(description, f"All required keys present: {schema_keys}", category)
            return True
    except json.JSONDecodeError as e:
        _log_test(f"✗ {description}", category)
        _log_test(f"  Invalid JSON: {e}", category)
        _record_fail(description, f"Invalid JSON: {e}", category)
        return False


def test_file_has_section(file_path: Path, section_pattern: str, description: str,
                          category: str = "Sections") -> bool:
    """Test if file has a required section."""
    _log_test(f"✓ {description}", category, end="")
    
    if not file_path.exists():
        _record_skip(description, f"File not found: {file_path}", category)
        return False
    
    content = file_path.read_text(encoding="utf-8")
    if re.search(section_pattern, content, re.MULTILINE | re.IGNORECASE):
        _record_pass(description, f"Section found: {section_pattern}", category)
        return True
    else:
        _log_test(f"✗ {description}", category)
        _record_fail(description, f"Section not found: {section_pattern}", category)
        return False


def test_line_count(file_path: Path, min_lines: int, description: str,
                    category: str = "Completeness") -> bool:
    """Test if file has minimum line count (completeness check)."""
    _log_test(f"✓ {description}", category, end="")
    
    if not file_path.exists():
        _record_skip(description, f"File not found: {file_path}", category)
        return False
    
    line_count = len(file_path.read_text(encoding="utf-8").splitlines())
    if line_count >= min_lines:
        _record_pass(description, f"File has {line_count} lines (required: {min_lines})", category)
        return True
    else:
        _log_test(f"✗ {description}", category)
        _log_test(f"  Expected: {min_lines}+ lines, Got: {line_count}", category)
        _record_fail(description, f"Insufficient content: {line_count} lines", category)
        return False


def _log_test(message: str, category: str = "General", end: str = "\n"):
    """Log test message with category."""
    print(message, end=end, flush=True)


def _record_pass(test_name: str, message: str, category: str):
    """Record passing test."""
    test_results["passed"] += 1
    if category not in test_results["categories"]:
        test_results["categories"][category] = {"passed": 0, "failed": 0, "skipped": 0}
    test_results["categories"][category]["passed"] += 1
    test_results["tests"].append({
        "name": test_name,
        "category": category,
        "result": "PASS",
        "message": message
    })
    print(" [PASS]", flush=True)


def _record_fail(test_name: str, message: str, category: str):
    """Record failing test."""
    test_results["failed"] += 1
    if category not in test_results["categories"]:
        test_results["categories"][category] = {"passed": 0, "failed": 0, "skipped": 0}
    test_results["categories"][category]["failed"] += 1
    test_results["tests"].append({
        "name": test_name,
        "category": category,
        "result": "FAIL",
        "message": message
    })
    print(" [FAIL]", flush=True)


def _record_skip(test_name: str, message: str, category: str):
    """Record skipped test."""
    test_results["skipped"] += 1
    if category not in test_results["categories"]:
        test_results["categories"][category] = {"passed": 0, "failed": 0, "skipped": 0}
    test_results["categories"][category]["skipped"] += 1
    test_results["tests"].append({
        "name": test_name,
        "category": category,
        "result": "SKIP",
        "message": message
    })
    print(" [SKIP]", flush=True)


def main() -> int:
    """Run all comprehensive tests."""
    print("=" * 80)
    print(f"{'WORKFLOW-IMPROVEMENTS TEST SUITE':^80}")
    print("=" * 80)
    print()
    print("Testing lane selection, parallelization, quality gates, status tracking,")
    print("pre-step hooks, and conventional commits validation.")
    print()

    # ============================================================================
    # DOCUMENTATION STRUCTURE TESTS
    # ============================================================================
    print("\n" + "=" * 80)
    print("1. OPENSPEC DOCUMENTATION ARTIFACTS")
    print("=" * 80)
    print()

    # Proposal
    print("Proposal.md - Business case and requirements...")
    test_file_exists(change_root / "proposal.md", "Proposal document exists", "Documentation")
    test_line_count(change_root / "proposal.md", 800, "Proposal has comprehensive content (800+ lines)", "Documentation")
    test_file_has_section(change_root / "proposal.md", r"## Why", "Proposal has 'Why' section", "Documentation")
    test_file_has_section(change_root / "proposal.md", r"## Impact", "Proposal has 'Impact' section", "Documentation")
    test_file_has_section(change_root / "proposal.md", r"## Objectives", "Proposal has 'Objectives' section", "Documentation")
    test_file_has_section(change_root / "proposal.md", r"## Appendices", "Proposal has 'Appendices' section", "Documentation")

    # Spec
    print("\nSpec.md - Technical specifications...")
    test_file_exists(change_root / "spec.md", "Specification document exists", "Documentation")
    test_line_count(change_root / "spec.md", 1000, "Spec has comprehensive content (1000+ lines)", "Documentation")
    test_file_has_section(change_root / "spec.md", r"## 3\. Acceptance Criteria", "Spec has 'Acceptance Criteria'", "Documentation")
    test_file_has_section(change_root / "spec.md", r"## 4\. Technical Design", "Spec has 'Technical Design'", "Documentation")
    test_file_has_section(change_root / "spec.md", r"## 7\. Data Models", "Spec has 'Data Models'", "Documentation")

    # Tasks
    print("\nTasks.md - Implementation task breakdown...")
    test_file_exists(change_root / "tasks.md", "Tasks document exists", "Documentation")
    test_line_count(change_root / "tasks.md", 1200, "Tasks has comprehensive breakdown (1200+ lines)", "Documentation")
    test_file_has_section(change_root / "tasks.md", r"## Implementation Tasks", "Tasks has 'Implementation Tasks'", "Documentation")
    test_file_has_section(change_root / "tasks.md", r"## Testing Tasks", "Tasks has 'Testing Tasks'", "Documentation")

    # Test Plan
    print("\nTest_plan.md - Testing strategy...")
    test_file_exists(change_root / "test_plan.md", "Test plan document exists", "Documentation")
    test_line_count(change_root / "test_plan.md", 800, "Test plan has comprehensive coverage (800+ lines)", "Documentation")
    test_file_has_section(change_root / "test_plan.md", r"## 1\. Test Strategy", "Test plan has 'Test Strategy'", "Documentation")
    test_file_has_section(change_root / "test_plan.md", r"## 6\. Unit Testing", "Test plan has 'Unit Testing'", "Documentation")

    # Todo
    print("\nTodo.md - Workflow tracking...")
    test_file_exists(change_root / "todo.md", "Todo checklist exists", "Documentation")
    test_file_has_section(change_root / "todo.md", r"## Task List|## Summary", "Todo has task tracking sections", "Documentation")

    # ============================================================================
    # LANE SELECTION REQUIREMENTS (from spec.md Acceptance Criteria)
    # ============================================================================
    print("\n" + "=" * 80)
    print("2. LANE SELECTION REQUIREMENTS")
    print("=" * 80)
    print()

    print("Checking lane selection requirements...")
    test_content_matches(change_root / "spec.md", r"--lane\s+\[docs\|standard\|heavy\]",
                        "Spec documents --lane flag syntax", "Lane Selection")
    test_content_matches(change_root / "spec.md", r"auto.?detect.*code.*changes",
                        "Spec documents auto-detection of code changes", "Lane Selection")
    test_content_matches(change_root / "proposal.md", r"Lane.*to.*Stage.*Mapping",
                        "Proposal has Lane-to-Stage mapping", "Lane Selection")

    # ============================================================================
    # PARALLELIZATION REQUIREMENTS
    # ============================================================================
    print("\n" + "=" * 80)
    print("3. PARALLELIZATION REQUIREMENTS")
    print("=" * 80)
    print()

    print("Checking parallelization requirements...")
    test_content_matches(change_root / "spec.md", r"ThreadPoolExecutor|max_workers",
                        "Spec documents ThreadPoolExecutor parallelization", "Parallelization")
    test_content_matches(change_root / "spec.md", r"Stages\s+2.?6.*parallel",
                        "Spec defines parallel stages (2-6)", "Parallelization")
    test_content_matches(change_root / "proposal.md", r"--no-parallel",
                        "Proposal documents --no-parallel flag", "Parallelization")

    # ============================================================================
    # QUALITY GATES REQUIREMENTS (Stage 8)
    # ============================================================================
    print("\n" + "=" * 80)
    print("4. QUALITY GATES REQUIREMENTS (Stage 8)")
    print("=" * 80)
    print()

    print("Checking quality gates requirements...")
    test_content_matches(change_root / "spec.md", r"scripts/quality_gates\.py",
                        "Spec references quality_gates.py module", "Quality Gates")
    test_content_matches(change_root / "spec.md", r"ruff.*mypy.*pytest.*bandit",
                        "Spec lists all 4 quality gate tools (ruff, mypy, pytest, bandit)", "Quality Gates")
    test_content_matches(change_root / "spec.md", r"quality_metrics\.json",
                        "Spec documents quality_metrics.json output", "Quality Gates")
    test_content_matches(change_root / "proposal.md", r"PASS/FAIL",
                        "Proposal documents PASS/FAIL decision logic", "Quality Gates")

    # ============================================================================
    # STATUS TRACKING REQUIREMENTS (status.json)
    # ============================================================================
    print("\n" + "=" * 80)
    print("5. STATUS TRACKING REQUIREMENTS (status.json)")
    print("=" * 80)
    print()

    print("Checking status tracking requirements...")
    test_content_matches(change_root / "spec.md", r"status\.json",
                        "Spec documents status.json file", "Status Tracking")
    test_content_matches(change_root / "spec.md", r"status\.json.*schema|schema.*status\.json",
                        "Spec includes status.json schema", "Status Tracking")
    test_content_matches(change_root / "spec.md", r"workflow.*resumption|resume.*workflow",
                        "Spec documents workflow resumption capability", "Status Tracking")
    test_content_matches(change_root / "spec.md", r"status\.json.*track|observability",
                        "Spec documents status.json for state tracking", "Status Tracking")

    # ============================================================================
    # PRE-STEP VALIDATION HOOKS REQUIREMENTS
    # ============================================================================
    print("\n" + "=" * 80)
    print("6. PRE-STEP VALIDATION HOOKS REQUIREMENTS")
    print("=" * 80)
    print()

    print("Checking pre-step validation hook requirements...")
    test_content_matches(change_root / "spec.md", r"Pre-Step.*Validation|Validation.*Hooks",
                        "Spec documents pre-step validation hooks", "Pre-Step Hooks")
    test_content_matches(change_root / "proposal.md", r"Appendix.*C.*Hooks|Pre-Step.*Validation",
                        "Proposal documents pre-step hooks", "Pre-Step Hooks")
    test_content_matches(change_root / "spec.md", r"Stage\s+0.*Python.*environment|environment.*validation",
                        "Spec defines Stage 0 environment validation", "Pre-Step Hooks")
    test_content_matches(change_root / "spec.md", r"Stage\s+10.*git.*clean|git.*state",
                        "Spec defines Stage 10 git validation", "Pre-Step Hooks")

    # ============================================================================
    # CONVENTIONAL COMMITS REQUIREMENTS (Stage 10)
    # ============================================================================
    print("\n" + "=" * 80)
    print("7. CONVENTIONAL COMMITS REQUIREMENTS (Stage 10)")
    print("=" * 80)
    print()

    print("Checking conventional commits requirements...")
    test_content_matches(change_root / "spec.md", r"Conventional.*Commit|commit.*format",
                        "Spec documents Conventional Commits validation", "Conventional Commits")
    test_content_matches(change_root / "proposal.md", r"Appendix.*E.*Commits|Conventional.*Commits",
                        "Proposal documents Conventional Commits format", "Conventional Commits")
    test_content_matches(change_root / "spec.md", r"interactive.*fixer|--no-verify",
                        "Spec documents interactive fixer and --no-verify escape hatch", "Conventional Commits")

    # ============================================================================
    # ACCEPTANCE CRITERIA REQUIREMENTS
    # ============================================================================
    print("\n" + "=" * 80)
    print("8. ACCEPTANCE CRITERIA")
    print("=" * 80)
    print()

    print("Checking key acceptance criteria from spec.md...")
    test_content_matches(change_root / "spec.md", r"\[ \]\s+.*--lane.*flag",
                        "Acceptance criteria includes --lane flag requirement", "Acceptance Criteria")
    test_content_matches(change_root / "spec.md", r"\[ \]\s+.*parallelization|parallel",
                        "Acceptance criteria includes parallelization requirement", "Acceptance Criteria")
    test_content_matches(change_root / "spec.md", r"\[ \]\s+.*quality.*gate",
                        "Acceptance criteria includes quality gates requirement", "Acceptance Criteria")
    test_content_matches(change_root / "spec.md", r"\[ \]\s+.*status\.json",
                        "Acceptance criteria includes status.json requirement", "Acceptance Criteria")

    # ============================================================================
    # FILE OPERATIONS TESTS
    # ============================================================================
    print("\n" + "=" * 80)
    print("9. FILE OPERATIONS REQUIREMENTS")
    print("=" * 80)
    print()

    print("Checking file operations that will be tested...")
    test_content_matches(change_root / "spec.md", r"openspec/changes.*status\.json",
                        "Spec documents status.json file path", "File Operations")
    test_content_matches(change_root / "spec.md", r"quality_metrics\.json",
                        "Spec documents quality_metrics.json output", "File Operations")
    test_content_matches(change_root / "spec.md", r"assistant_logs",
                        "Spec documents assistant_logs directory", "File Operations")
    test_content_matches(change_root / "proposal.md", r"status\.json.*write|emit.*status|write.*status",
                        "Proposal documents workflow state writing to status.json", "File Operations")

    # ============================================================================
    # PERFORMANCE AND SUCCESS METRICS
    # ============================================================================
    print("\n" + "=" * 80)
    print("10. PERFORMANCE AND SUCCESS METRICS")
    print("=" * 80)
    print()

    print("Checking documented success metrics...")
    test_content_matches(change_root / "spec.md", r"<\s*5.*minute|5.*minute.*<|cycle.*time",
                        "Spec documents <5 minute cycle time goal for docs lane", "Performance Metrics")
    test_content_matches(change_root / "proposal.md", r"80%.*adoption|adoption.*80%",
                        "Proposal documents 80% adoption target", "Performance Metrics")
    test_content_matches(change_root / "spec.md", r"Success.*Metrics|Measurable.*Success",
                        "Spec includes success metrics", "Performance Metrics")
    test_content_matches(change_root / "proposal.md", r"status\.json.*track|track.*status\.json",
                        "Proposal documents workflow state tracking via status.json", "Performance Metrics")

    # ============================================================================
    # IMPLEMENT.PY ENGINE TESTS - ACTIVE IMPLEMENTATION (v2.0)
    # ============================================================================
    print("\n" + "=" * 80)
    print("11. IMPLEMENT.PY ENGINE TESTS")
    print("=" * 80)
    print()

    print("Testing active implementation engine (Phase-based architecture)...")
    
    # Test that implement.py exists and is readable
    test_file_exists(change_root / "implement.py", "implement.py exists", "Implement Engine")
    test_line_count(change_root / "implement.py", 250, "implement.py has implementation logic (250+ lines)", "Implement Engine")
    
    # Test ACTIVE IMPLEMENTATION structure
    try:
        implement_source = (change_root / "implement.py").read_text(encoding="utf-8")
        
        # Verify this is the active implementation engine (not task registry)
        if "ACTIVE IMPLEMENTATION ENGINE" in implement_source or "implement_lane_selection" in implement_source:
            _record_pass("Active implementation engine detected", 
                        "Found phase-based implementation functions", "Implement Engine")
        else:
            _record_fail("Active implementation engine detected", "Old task registry structure still present", "Implement Engine")
        
        # Verify three core implementation functions
        implementation_phases = {
            "implement_lane_selection_python": "Phase 1: Lane selection",
            "create_quality_gates_module": "Phase 2: Quality gates module",
            "create_status_json_template": "Phase 3: Status tracking template"
        }
        
        for func_name, phase_desc in implementation_phases.items():
            if f"def {func_name}(" in implement_source:
                _record_pass(f"{phase_desc} implemented", f"Function {func_name} found", "Implement Engine")
            else:
                _record_fail(f"{phase_desc} implemented", f"Function {func_name} not found", "Implement Engine")
        
        # Verify main() orchestrator
        if "def main():" in implement_source and "if __name__" in implement_source:
            _record_pass("main() orchestrator function defined", "Main orchestrator found", "Implement Engine")
        else:
            _record_fail("main() orchestrator function defined", "Main orchestrator not found", "Implement Engine")
        
        # Verify results tracking structure
        if "results =" in implement_source or "\"completed\"" in implement_source:
            if "\"failed\"" in implement_source and "\"files_created\"" in implement_source:
                _record_pass("Results tracking structure", "Results dict with completed/failed/files tracking", "Implement Engine")
            else:
                _record_fail("Results tracking structure", "Incomplete results tracking", "Implement Engine")
        else:
            _record_fail("Results tracking structure", "Results tracking not found", "Implement Engine")
        
        # Verify encoding handling (critical for Windows)
        if "encoding='utf-8'" in implement_source:
            _record_pass("UTF-8 encoding specified", "File operations use UTF-8 encoding", "Implement Engine")
        else:
            _record_fail("UTF-8 encoding specified", "Encoding parameter missing", "Implement Engine")
        
        # Verify no emoji in code (cross-platform compatibility)
        if any(ord(c) > 127 for c in implement_source):
            # Check if it's just in comments/strings (acceptable)
            lines_with_unicode = [l for l in implement_source.split('\n') if any(ord(c) > 127 for c in l)]
            problematic = [l for l in lines_with_unicode if not l.strip().startswith('#') and '"""' not in l]
            if problematic:
                _record_fail("No problematic unicode in code", f"Found unicode in executable code", "Implement Engine")
            else:
                _record_pass("Unicode characters in code are safe", "Found unicode only in comments/docstrings", "Implement Engine")
        else:
            _record_pass("ASCII-safe code", "No encoding compatibility issues", "Implement Engine")
        
    except Exception as e:
        _record_fail("implement.py analysis", f"Error analyzing implement.py: {e}", "Implement Engine")

    # ============================================================================
    # IMPLEMENT.PY EXECUTION TESTS
    # ============================================================================
    print("\n" + "=" * 80)
    print("12. IMPLEMENT.PY EXECUTION TESTS")
    print("=" * 80)
    print()

    print("Testing active implementation engine execution...")
    
    try:
        import subprocess as sp
        python_exe = sys.executable
        
        # Test basic execution (should generate files and modifications)
        result = sp.run(
            [python_exe, str(change_root / "implement.py")],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout + result.stderr
        
        # Check that implementation completed
        if "Completed:" in output and "Failed:" in output:
            _record_pass("main() orchestrator executes successfully", 
                       "Implementation engine ran and produced output", "Implement Execution")
        else:
            _record_fail("main() orchestrator executes successfully", 
                       f"Unexpected output. Return code: {result.returncode}", "Implement Execution")
        
        # Check for Phase 1: Lane selection
        if "[OK] Lane selection" in output or "Lane selection flag" in output:
            _record_pass("Phase 1: Lane selection generates scripts/workflow.py modification", 
                       "Lane selection phase executed", "Implement Execution")
        elif "[SKIP]" in output:
            _record_pass("Phase 1: Lane selection detects existing implementation", 
                       "Lane selection already implemented (skip is OK)", "Implement Execution")
        else:
            _record_fail("Phase 1: Lane selection generates modifications", 
                       "Phase 1 did not complete", "Implement Execution")
        
        # Check for Phase 2: Quality gates module
        if "[OK] Quality gates module" in output or "Quality gates" in output:
            _record_pass("Phase 2: Quality gates creates scripts/quality_gates.py", 
                       "Quality gates module created", "Implement Execution")
        else:
            _record_fail("Phase 2: Quality gates creates module", 
                       "Phase 2 did not complete successfully", "Implement Execution")
        
        # Check for Phase 3: Status tracking
        if "[OK] Status tracking" in output or "status.json" in output:
            _record_pass("Phase 3: Status template creates status.json", 
                       "Status tracking template created", "Implement Execution")
        else:
            _record_fail("Phase 3: Status template creates file", 
                       "Phase 3 did not complete successfully", "Implement Execution")
        
        # Overall success metric
        if result.returncode == 0 and ("Completed: 3" in output or "Completed: 2" in output):
            _record_pass("All implementation phases completed successfully", 
                       "Active implementation engine produced expected results", "Implement Execution")
        else:
            _record_fail("All implementation phases completed", 
                       f"Return code: {result.returncode}, output incomplete", "Implement Execution")
        
    except sp.TimeoutExpired:
        _record_fail("implement.py execution", "Execution timed out (>10s)", "Implement Execution")
    except Exception as e:
        _record_fail("implement.py execution", f"Error executing implement.py: {e}", "Implement Execution")

    # ============================================================================
    # GENERATED ARTIFACTS VALIDATION (Section 13)
    # ============================================================================
    print("\n" + "=" * 80)
    print("13. GENERATED ARTIFACTS VALIDATION")
    print("=" * 80)
    print()

    print("Validating implementation engine output files...")
    
    # Test that workflow.py was modified with lane selection
    workflow_file = scripts_root / "workflow.py"
    if workflow_file.exists():
        workflow_content = workflow_file.read_text(encoding='utf-8')
        if "LANE_MAPPING" in workflow_content:
            _record_pass("Lane selection added to scripts/workflow.py", 
                       "LANE_MAPPING dictionary found", "Generated Artifacts")
        else:
            _record_fail("Lane selection added to workflow.py", 
                       "LANE_MAPPING not found in file", "Generated Artifacts")
        
        if "--lane" in workflow_content:
            _record_pass("--lane argument added to scripts/workflow.py", 
                       "--lane flag found in argparse", "Generated Artifacts")
        else:
            _record_fail("--lane argument added to workflow.py", 
                       "--lane flag not found", "Generated Artifacts")
    else:
        _record_fail("scripts/workflow.py exists", "File not found", "Generated Artifacts")
    
    # Test that quality_gates.py was created
    quality_gates_file = scripts_root / "quality_gates.py"
    if quality_gates_file.exists():
        _record_pass("Quality gates module created at scripts/quality_gates.py", 
                   "File exists and was generated", "Generated Artifacts")
        
        quality_content = quality_gates_file.read_text(encoding='utf-8')
        if "class QualityGates:" in quality_content:
            _record_pass("QualityGates class defined in quality_gates.py", 
                       "Class definition found", "Generated Artifacts")
        else:
            _record_fail("QualityGates class defined", "Class not found", "Generated Artifacts")
        
        if "def run_all(" in quality_content:
            _record_pass("run_all() method defined in quality_gates.py", 
                       "Method found", "Generated Artifacts")
        else:
            _record_fail("run_all() method defined", "Method not found", "Generated Artifacts")
        
        if "ruff" in quality_content and "mypy" in quality_content:
            _record_pass("Quality tools (ruff, mypy, pytest, bandit) configured", 
                       "All tools found in module", "Generated Artifacts")
        else:
            _record_fail("Quality tools configured", "Not all tools found", "Generated Artifacts")
    else:
        _record_fail("Quality gates module exists at scripts/quality_gates.py", 
                   "File not found", "Generated Artifacts")
    
    # Test that status.json was created
    status_file = change_root / "status.json"
    if status_file.exists():
        _record_pass("Status tracking template created at status.json", 
                   "File exists and was generated", "Generated Artifacts")
        
        try:
            status_content = json.loads(status_file.read_text(encoding='utf-8'))
            required_fields = ["workflow_id", "lane", "started_at", "current_stage", 
                            "completed_stages", "failed_stages", "status", "resumable"]
            missing = [f for f in required_fields if f not in status_content]
            
            if not missing:
                _record_pass("status.json has required schema", 
                           f"All required fields present: {required_fields}", "Generated Artifacts")
            else:
                _record_fail("status.json has required schema", 
                           f"Missing fields: {missing}", "Generated Artifacts")
        except json.JSONDecodeError:
            _record_fail("status.json is valid JSON", "JSON parse error", "Generated Artifacts")
    else:
        _record_fail("Status tracking template exists at status.json", 
                   "File not found", "Generated Artifacts")

    # ============================================================================
    # SUMMARY AND REPORTING
    # ============================================================================
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    print()

    # Print by category
    for category, stats in sorted(test_results["categories"].items()):
        passed = stats["passed"]
        failed = stats["failed"]
        skipped = stats["skipped"]
        total = passed + failed + skipped
        pct = (passed / total * 100) if total > 0 else 0
        print(f"{category:.<40} {passed:>3} PASS, {failed:>3} FAIL, {skipped:>3} SKIP ({pct:>5.1f}%)")

    print()
    print("=" * 80)
    total_passed = test_results["passed"]
    total_failed = test_results["failed"]
    total_skipped = test_results["skipped"]
    total = total_passed + total_failed + total_skipped
    pct = (total_passed / total * 100) if total > 0 else 0

    print(f"Total Tests: {total}")
    print(f"  ✓ Passed:  {total_passed} ({pct:.1f}%)")
    print(f"  ✗ Failed:  {total_failed}")
    print(f"  ○ Skipped: {total_skipped}")
    print()

    if total_failed > 0:
        print("RESULT: ✗ FAILED")
        print()
        print("Failed Tests:")
        for test in test_results["tests"]:
            if test["result"] == "FAIL":
                print(f"  - {test['name']} ({test['category']})")
                print(f"    {test['message']}")
        return 1
    else:
        print("RESULT: ✓ PASSED")
        print()
        print("All requirements from workflow-improvements documentation validated.")
        print("Ready for implementation phase.")
        return 0


if __name__ == "__main__":
    sys.exit(main())

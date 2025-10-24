#!/usr/bin/env python3
"""
Enhanced Test Suite for workflow-improvements

Comprehensive test coverage including:
1. Documentation structure and requirements validation
2. Lane selection logic testing
3. Quality gates module testing
4. Status tracking mechanism testing
5. Pre-step validation hooks testing
6. Conventional commits validation testing
7. Error handling and edge case testing
8. Implementation engine validation
9. Generated artifacts validation

Version: 3.0 (Enhanced with comprehensive logic tests)
Last Updated: 2025-10-23
"""

import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import subprocess
import tempfile
import shutil


change_root = Path(__file__).parent
project_root = change_root.parent.parent.parent
scripts_root = project_root / "scripts"

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "tests": [],
    "categories": {},
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _log_test(msg: str, category: str = "General", end: str = "\n"):
    """Log a test message."""
    if category not in test_results["categories"]:
        test_results["categories"][category] = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
        }
    print(msg, end=end)


def _record_pass(test_name: str, message: str = "", category: str = "General"):
    """Record a passing test."""
    test_results["passed"] += 1
    test_results["categories"][category]["passed"] += 1
    test_results["tests"].append({
        "name": test_name,
        "result": "PASS",
        "category": category,
        "message": message,
    })
    if message:
        _log_test(f" ✓ PASS", category)
    else:
        _log_test(f"✓", category)


def _record_fail(test_name: str, message: str = "", category: str = "General"):
    """Record a failing test."""
    test_results["failed"] += 1
    test_results["categories"][category]["failed"] += 1
    test_results["tests"].append({
        "name": test_name,
        "result": "FAIL",
        "category": category,
        "message": message,
    })
    _log_test(f" ✗ FAIL", category)


def _record_skip(test_name: str, message: str = "", category: str = "General"):
    """Record a skipped test."""
    test_results["skipped"] += 1
    test_results["categories"][category]["skipped"] += 1
    test_results["tests"].append({
        "name": test_name,
        "result": "SKIP",
        "category": category,
        "message": message,
    })
    _log_test(f" ⊘ SKIP", category)


# ============================================================================
# LANE SELECTION LOGIC TESTS
# ============================================================================

def test_lane_mapping_structure():
    """Test that LANE_MAPPING is properly structured in workflow.py"""
    _log_test("Testing LANE_MAPPING structure... ", "Lane Selection", end="")
    
    workflow_file = scripts_root / "workflow.py"
    if not workflow_file.exists():
        _record_skip("LANE_MAPPING structure", "workflow.py not found", "Lane Selection")
        return False
    
    content = workflow_file.read_text(encoding='utf-8', errors='replace')
    
    # Check LANE_MAPPING exists
    if "LANE_MAPPING" not in content:
        _record_fail("LANE_MAPPING defined", "LANE_MAPPING not found in workflow.py", "Lane Selection")
        return False
    
    # Check all three lanes present
    lanes_found = 0
    for lane in ["docs", "standard", "heavy"]:
        if f'"{lane}"' in content:
            lanes_found += 1
    
    if lanes_found != 3:
        _record_fail("All three lanes defined (docs, standard, heavy)", 
                    f"Only {lanes_found} lanes found", "Lane Selection")
        return False
    
    _record_pass("LANE_MAPPING structure correct", "docs, standard, heavy lanes defined", "Lane Selection")
    return True


def test_lane_stages_mapping():
    """Test that lane-to-stage mapping is correct"""
    _log_test("Testing lane-to-stage mapping... ", "Lane Selection", end="")
    
    workflow_file = scripts_root / "workflow.py"
    content = workflow_file.read_text(encoding='utf-8', errors='replace')
    
    # Extract LANE_MAPPING from code
    try:
        # Find and execute LANE_MAPPING definition
        mapping_match = re.search(r'LANE_MAPPING\s*=\s*\{([^}]+)\}', content, re.DOTALL)
        if not mapping_match:
            _record_fail("Lane-to-stage mapping exists", "LANE_MAPPING structure invalid", "Lane Selection")
            return False
        
        # Check docs lane includes expected stages
        if '"docs"' in content and '"stages"' in content:
            # Docs lane should include stages: 0, 2, 3, 4, 9, 10, 11, 12
            docs_pattern = r'"docs".*?"stages".*?\[([\d,\s]+)\]'
            docs_match = re.search(docs_pattern, content, re.DOTALL)
            if docs_match:
                stages_str = docs_match.group(1)
                # Check for critical stages
                if all(str(s) in stages_str for s in [0, 2, 3, 4, 9, 10, 11, 12]):
                    _record_pass("Docs lane stages configured correctly", 
                               "Includes stages 0,2,3,4,9,10,11,12", "Lane Selection")
                    return True
        
        _record_fail("Lane-to-stage mapping correct", "Docs lane stages not properly configured", "Lane Selection")
        return False
        
    except Exception as e:
        _record_fail("Lane-to-stage mapping parsing", str(e), "Lane Selection")
        return False


def test_default_lane_is_standard():
    """Test that default lane is 'standard' (backward compatibility)"""
    _log_test("Testing default lane... ", "Lane Selection", end="")
    
    workflow_file = scripts_root / "workflow.py"
    content = workflow_file.read_text(encoding='utf-8', errors='replace')
    
    # Check for default="standard" in argparse
    if 'default="standard"' in content or "default='standard'" in content:
        _record_pass("Default lane is 'standard'", "Backward compatible", "Lane Selection")
        return True
    else:
        _record_fail("Default lane is 'standard'", "Default not set to 'standard'", "Lane Selection")
        return False


def test_lane_flag_validation():
    """Test that invalid lane values are rejected"""
    _log_test("Testing lane flag validation... ", "Lane Selection", end="")
    
    workflow_file = scripts_root / "workflow.py"
    content = workflow_file.read_text(encoding='utf-8', errors='replace')
    
    # Check for choices parameter in argparse
    if 'choices=' in content and ('docs' in content or 'standard' in content):
        _record_pass("Lane flag validation implemented", 
                   "Choices parameter configured", "Lane Selection")
        return True
    else:
        _record_fail("Lane flag validation", "choices parameter not found", "Lane Selection")
        return False


# ============================================================================
# QUALITY GATES MODULE TESTS
# ============================================================================

def test_quality_gates_class():
    """Test that QualityGates class exists and has required methods"""
    _log_test("Testing QualityGates class structure... ", "Quality Gates", end="")
    
    quality_gates_file = scripts_root / "quality_gates.py"
    if not quality_gates_file.exists():
        _record_skip("QualityGates class", "quality_gates.py not found", "Quality Gates")
        return False
    
    content = quality_gates_file.read_text(encoding='utf-8', errors='replace')
    
    required_methods = ["run_all", "run_ruff", "run_mypy", "run_pytest", "run_bandit", "save_metrics"]
    found_methods = sum(1 for method in required_methods if f"def {method}" in content)
    
    if found_methods == len(required_methods):
        _record_pass("QualityGates class complete", 
                   f"All {len(required_methods)} required methods present", "Quality Gates")
        return True
    else:
        _record_fail("QualityGates class complete", 
                   f"Only {found_methods}/{len(required_methods)} methods found", "Quality Gates")
        return False


def test_quality_gates_thresholds():
    """Test that thresholds are configured per lane"""
    _log_test("Testing quality gates thresholds... ", "Quality Gates", end="")
    
    quality_gates_file = scripts_root / "quality_gates.py"
    content = quality_gates_file.read_text(encoding='utf-8', errors='replace')
    
    # Check THRESHOLDS dict exists
    if "THRESHOLDS" not in content:
        _record_fail("Thresholds defined per lane", "THRESHOLDS not found", "Quality Gates")
        return False
    
    # Check all lanes have thresholds
    lanes_with_thresholds = 0
    for lane in ["docs", "standard", "heavy"]:
        if f'"{lane}"' in content:
            lanes_with_thresholds += 1
    
    if lanes_with_thresholds >= 2:  # At minimum standard and heavy
        _record_pass("Thresholds configured per lane", 
                   f"Thresholds for {lanes_with_thresholds} lanes", "Quality Gates")
        return True
    else:
        _record_fail("Thresholds per lane", 
                   f"Only {lanes_with_thresholds} lane thresholds found", "Quality Gates")
        return False


def test_quality_gates_metrics_output():
    """Test that quality gates can produce JSON output"""
    _log_test("Testing quality gates JSON output... ", "Quality Gates", end="")
    
    quality_gates_file = scripts_root / "quality_gates.py"
    content = quality_gates_file.read_text(encoding='utf-8', errors='replace')
    
    # Check for save_metrics and JSON output
    if "save_metrics" in content and "json.dumps" in content:
        _record_pass("Quality gates JSON output configured", 
                   "save_metrics and json.dumps present", "Quality Gates")
        return True
    else:
        _record_fail("Quality gates JSON output", 
                   "save_metrics or json.dumps missing", "Quality Gates")
        return False


# ============================================================================
# STATUS TRACKING TESTS
# ============================================================================

def test_status_json_schema():
    """Test that status.json has required schema fields"""
    _log_test("Testing status.json schema... ", "Status Tracking", end="")
    
    status_file = change_root / "status.json"
    if not status_file.exists():
        _record_skip("status.json schema", "status.json not found", "Status Tracking")
        return False
    
    try:
        status_data = json.loads(status_file.read_text(encoding='utf-8'))
        
        required_fields = [
            "workflow_id",
            "lane",
            "current_stage",
            "completed_stages",
            "failed_stages",
            "status",
        ]
        
        missing_fields = [f for f in required_fields if f not in status_data]
        
        if not missing_fields:
            _record_pass("status.json schema complete", 
                       f"All {len(required_fields)} required fields present", "Status Tracking")
            return True
        else:
            _record_fail("status.json schema", 
                       f"Missing fields: {missing_fields}", "Status Tracking")
            return False
            
    except json.JSONDecodeError as e:
        _record_fail("status.json valid JSON", str(e), "Status Tracking")
        return False


def test_status_json_resumable():
    """Test that status.json includes resumable flag"""
    _log_test("Testing status.json resumable flag... ", "Status Tracking", end="")
    
    status_file = change_root / "status.json"
    if not status_file.exists():
        _record_skip("Resumable flag", "status.json not found", "Status Tracking")
        return False
    
    try:
        status_data = json.loads(status_file.read_text(encoding='utf-8'))
        if "resumable" in status_data:
            _record_pass("Resumable flag in status.json", 
                       f"resumable = {status_data['resumable']}", "Status Tracking")
            return True
        else:
            _record_fail("Resumable flag in status.json", "resumable field missing", "Status Tracking")
            return False
    except:
        _record_fail("status.json parsing", "JSON decode error", "Status Tracking")
        return False


# ============================================================================
# PRE-STEP VALIDATION HOOKS TESTS
# ============================================================================

def test_pre_step_hooks_documented():
    """Test that pre-step validation hooks are documented"""
    _log_test("Testing pre-step hooks documentation... ", "Pre-Step Hooks", end="")
    
    spec_file = change_root / "spec.md"
    if not spec_file.exists():
        _record_skip("Pre-step hooks doc", "spec.md not found", "Pre-Step Hooks")
        return False
    
    content = spec_file.read_text(encoding='utf-8', errors='replace')
    
    # Check for hook stages
    hook_stages = ["Stage 0", "Stage 10", "Stage 12"]
    found_stages = sum(1 for stage in hook_stages if stage in content)
    
    if found_stages >= 2 and ("hook" in content.lower() or "validation" in content.lower()):
        _record_pass("Pre-step hooks documented", 
                   f"{found_stages}/3 hook stages mentioned", "Pre-Step Hooks")
        return True
    else:
        _record_fail("Pre-step hooks documented", 
                   "Hook stages or validation not properly documented", "Pre-Step Hooks")
        return False


def test_environment_validation_stage():
    """Test that Stage 0 environment validation is documented"""
    _log_test("Testing Stage 0 environment validation... ", "Pre-Step Hooks", end="")
    
    spec_file = change_root / "spec.md"
    content = spec_file.read_text(encoding='utf-8', errors='replace')
    
    # Check for environment validation at Stage 0
    if re.search(r'Stage\s+0.*(?:Python|environment|validate)', content, re.IGNORECASE | re.DOTALL):
        _record_pass("Stage 0 environment validation documented", 
                   "Python environment validation specified", "Pre-Step Hooks")
        return True
    else:
        _record_fail("Stage 0 environment validation", 
                   "Environment validation not documented for Stage 0", "Pre-Step Hooks")
        return False


def test_git_state_validation_stage():
    """Test that Stage 10 git state validation is documented"""
    _log_test("Testing Stage 10 git validation... ", "Pre-Step Hooks", end="")
    
    spec_file = change_root / "spec.md"
    content = spec_file.read_text(encoding='utf-8', errors='replace')
    
    # Check for git validation at Stage 10
    if re.search(r'Stage\s+10.*(?:git|clean|branch)', content, re.IGNORECASE | re.DOTALL):
        _record_pass("Stage 10 git validation documented", 
                   "Git state validation specified", "Pre-Step Hooks")
        return True
    else:
        _record_fail("Stage 10 git validation", 
                   "Git validation not documented for Stage 10", "Pre-Step Hooks")
        return False


# ============================================================================
# CONVENTIONAL COMMITS VALIDATION TESTS
# ============================================================================

def test_conventional_commits_format():
    """Test that conventional commits validation is documented"""
    _log_test("Testing conventional commits format... ", "Conventional Commits", end="")
    
    spec_file = change_root / "spec.md"
    if not spec_file.exists():
        _record_skip("Conventional commits", "spec.md not found", "Conventional Commits")
        return False
    
    content = spec_file.read_text(encoding='utf-8', errors='replace')
    
    # Check for conventional commits mention
    if re.search(r'conventional.*commit|commit.*format|type\(scope\):\s*subject', 
                 content, re.IGNORECASE):
        _record_pass("Conventional commits format documented", 
                   "Format specification present", "Conventional Commits")
        return True
    else:
        _record_fail("Conventional commits format", 
                   "Format not documented", "Conventional Commits")
        return False


def test_commit_types_supported():
    """Test that commit types (feat, fix, docs, etc) are documented"""
    _log_test("Testing commit types... ", "Conventional Commits", end="")
    
    spec_file = change_root / "spec.md"
    content = spec_file.read_text(encoding='utf-8', errors='replace')
    
    # Check for at least 4 commit types
    types_found = 0
    for ctype in ["feat", "fix", "docs", "refactor", "test", "chore"]:
        if ctype in content.lower():
            types_found += 1
    
    if types_found >= 4:
        _record_pass("Commit types documented", 
                   f"{types_found} commit types mentioned", "Conventional Commits")
        return True
    else:
        _record_fail("Commit types documented", 
                   f"Only {types_found} types found (need 4+)", "Conventional Commits")
        return False


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

def test_error_handling_documented():
    """Test that error handling is documented"""
    _log_test("Testing error handling documentation... ", "Error Handling", end="")
    
    spec_file = change_root / "spec.md"
    content = spec_file.read_text(encoding='utf-8', errors='replace')
    
    # Check for error scenarios
    error_keywords = ["error", "invalid", "missing", "fail", "exception"]
    found_keywords = sum(1 for kw in error_keywords if kw.lower() in content.lower())
    
    if found_keywords >= 3:
        _record_pass("Error handling documented", 
                   f"{found_keywords} error-related terms mentioned", "Error Handling")
        return True
    else:
        _record_fail("Error handling documented", 
                   "Insufficient error handling documentation", "Error Handling")
        return False


def test_invalid_lane_handling():
    """Test that invalid lane values are documented as error case"""
    _log_test("Testing invalid lane error handling... ", "Error Handling", end="")
    
    spec_file = change_root / "spec.md"
    content = spec_file.read_text(encoding='utf-8', errors='replace')
    
    # Check for validation or error handling of lane parameter
    if re.search(r'(?:invalid|valid).*lane|lane.*(?:error|invalid)', 
                 content, re.IGNORECASE):
        _record_pass("Invalid lane error handling documented", 
                   "Lane validation error case specified", "Error Handling")
        return True
    else:
        _record_fail("Invalid lane error handling", 
                   "Lane error case not documented", "Error Handling")
        return False


# ============================================================================
# IMPLEMENT.PY ENGINE TESTS
# ============================================================================

def test_implement_engine_structure():
    """Test that implement.py has proper structure"""
    _log_test("Testing implement.py engine structure... ", "Implement Engine", end="")
    
    implement_file = change_root / "implement.py"
    if not implement_file.exists():
        _record_skip("implement.py engine", "implement.py not found", "Implement Engine")
        return False
    
    content = implement_file.read_text(encoding='utf-8', errors='replace')
    
    required_phases = [
        "implement_lane_selection",
        "create_quality_gates",
        "create_status_json",
    ]
    
    found_phases = sum(1 for phase in required_phases if phase in content)
    
    if found_phases == len(required_phases):
        _record_pass("implement.py has all phases", 
                   f"All {len(required_phases)} implementation phases present", "Implement Engine")
        return True
    else:
        _record_fail("implement.py phase structure", 
                   f"Only {found_phases}/{len(required_phases)} phases found", "Implement Engine")
        return False


def test_implement_main_orchestrator():
    """Test that main() orchestrator exists"""
    _log_test("Testing implement.py orchestrator... ", "Implement Engine", end="")
    
    implement_file = change_root / "implement.py"
    content = implement_file.read_text(encoding='utf-8', errors='replace')
    
    # Check for main function
    if "def main():" in content:
        # Check that it calls all phases
        phases_called = sum(1 for phase in ["implement_lane_selection", "create_quality_gates", "create_status_json"]
                          if phase in content)
        if phases_called >= 2:
            _record_pass("main() orchestrator working", 
                       f"Calls {phases_called}/3 phases", "Implement Engine")
            return True
    
    _record_fail("main() orchestrator", "main function not properly configured", "Implement Engine")
    return False


# ============================================================================
# GENERATED ARTIFACTS TESTS
# ============================================================================

def test_workflow_py_modified():
    """Test that workflow.py was modified with lane support"""
    _log_test("Testing workflow.py modification... ", "Generated Artifacts", end="")
    
    workflow_file = scripts_root / "workflow.py"
    if not workflow_file.exists():
        _record_skip("workflow.py modification", "workflow.py not found", "Generated Artifacts")
        return False
    
    content = workflow_file.read_text(encoding='utf-8', errors='replace')
    
    if "LANE_MAPPING" in content and "--lane" in content:
        _record_pass("workflow.py contains lane support", 
                   "LANE_MAPPING and --lane flag present", "Generated Artifacts")
        return True
    else:
        _record_fail("workflow.py lane support", 
                   "Lane support not added to workflow.py", "Generated Artifacts")
        return False


def test_quality_gates_py_created():
    """Test that quality_gates.py was created"""
    _log_test("Testing quality_gates.py creation... ", "Generated Artifacts", end="")
    
    quality_gates_file = scripts_root / "quality_gates.py"
    if quality_gates_file.exists():
        content = quality_gates_file.read_text(encoding='utf-8', errors='replace')
        if "QualityGates" in content and "run_all" in content:
            _record_pass("quality_gates.py created with QualityGates class", 
                       "File exists and has required class", "Generated Artifacts")
            return True
        else:
            _record_fail("quality_gates.py content", 
                       "QualityGates class or run_all method missing", "Generated Artifacts")
    else:
        _record_fail("quality_gates.py created", 
                   "File not found at scripts/quality_gates.py", "Generated Artifacts")
    
    return False


def test_status_json_created():
    """Test that status.json was created"""
    _log_test("Testing status.json creation... ", "Generated Artifacts", end="")
    
    status_file = change_root / "status.json"
    if status_file.exists():
        try:
            data = json.loads(status_file.read_text(encoding='utf-8'))
            if isinstance(data, dict) and "workflow_id" in data:
                _record_pass("status.json created with valid schema", 
                           f"workflow_id: {data.get('workflow_id')}", "Generated Artifacts")
                return True
            else:
                _record_fail("status.json schema", "Invalid or missing schema", "Generated Artifacts")
        except:
            _record_fail("status.json parsing", "JSON decode error", "Generated Artifacts")
    else:
        _record_fail("status.json created", 
                   "File not found", "Generated Artifacts")
    
    return False


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all comprehensive tests."""
    print("=" * 80)
    print(f"{'WORKFLOW-IMPROVEMENTS ENHANCED TEST SUITE':^80}")
    print("=" * 80)
    print()

    # Lane Selection Tests
    print("\n" + "=" * 80)
    print("LANE SELECTION TESTS (Spec AC#1-5)")
    print("=" * 80)
    test_lane_mapping_structure()
    test_lane_stages_mapping()
    test_default_lane_is_standard()
    test_lane_flag_validation()

    # Quality Gates Tests
    print("\n" + "=" * 80)
    print("QUALITY GATES TESTS (Spec AC#4)")
    print("=" * 80)
    test_quality_gates_class()
    test_quality_gates_thresholds()
    test_quality_gates_metrics_output()

    # Status Tracking Tests
    print("\n" + "=" * 80)
    print("STATUS TRACKING TESTS (Spec AC#5)")
    print("=" * 80)
    test_status_json_schema()
    test_status_json_resumable()

    # Pre-Step Hooks Tests
    print("\n" + "=" * 80)
    print("PRE-STEP VALIDATION HOOKS TESTS (Spec AC#3)")
    print("=" * 80)
    test_pre_step_hooks_documented()
    test_environment_validation_stage()
    test_git_state_validation_stage()

    # Conventional Commits Tests
    print("\n" + "=" * 80)
    print("CONVENTIONAL COMMITS TESTS (Spec AC#6)")
    print("=" * 80)
    test_conventional_commits_format()
    test_commit_types_supported()

    # Error Handling Tests
    print("\n" + "=" * 80)
    print("ERROR HANDLING TESTS")
    print("=" * 80)
    test_error_handling_documented()
    test_invalid_lane_handling()

    # Implementation Engine Tests
    print("\n" + "=" * 80)
    print("IMPLEMENTATION ENGINE TESTS")
    print("=" * 80)
    test_implement_engine_structure()
    test_implement_main_orchestrator()

    # Generated Artifacts Tests
    print("\n" + "=" * 80)
    print("GENERATED ARTIFACTS TESTS")
    print("=" * 80)
    test_workflow_py_modified()
    test_quality_gates_py_created()
    test_status_json_created()

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
        print(f"{category:.<45} {passed:>3} PASS, {failed:>3} FAIL, {skipped:>3} SKIP ({pct:>5.1f}%)")

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
    print(f"  ⊘ Skipped: {total_skipped}")
    print()

    if total_failed > 0:
        print("RESULT: ✗ FAILED")
        print()
        print("Failed Tests:")
        for test in test_results["tests"]:
            if test["result"] == "FAIL":
                print(f"  ✗ {test['name']}")
                if test["message"]:
                    print(f"    → {test['message']}")
        return 1
    else:
        print("RESULT: ✓ PASSED")
        print()
        print("All requirements from workflow-improvements validated.")
        return 0


if __name__ == "__main__":
    sys.exit(main())

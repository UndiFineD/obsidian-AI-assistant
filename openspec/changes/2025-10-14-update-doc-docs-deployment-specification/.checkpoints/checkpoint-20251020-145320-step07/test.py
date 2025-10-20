#!/usr/bin/env python3
"""
Test script for change: 2025-10-14-update-doc-docs-deployment-specification

Automated test script generated from OpenSpec workflow documentation.
Tests the implementation of the changes defined in proposal.md and spec.md.

Generated: 2025-10-20 15:53:20
"""

import sys
from pathlib import Path
from typing import List, Dict


change_root = Path(__file__).parent
project_root = change_root.parent.parent.parent

test_results = {
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "tests": [],
}


def test_file_exists(file_path: Path, description: str) -> bool:
    """Test if a file exists."""
    print(f"Testing: {description}", end="")
    
    if file_path.exists():
        print(" [PASS]", flush=True)
        test_results["passed"] += 1
        test_results["tests"].append({
            "name": description,
            "result": "PASS",
            "message": f"File exists: {file_path}"
        })
        return True
    else:
        print(" [FAIL]", flush=True)
        print(f"  Expected: {file_path}")
        test_results["failed"] += 1
        test_results["tests"].append({
            "name": description,
            "result": "FAIL",
            "message": f"File not found: {file_path}"
        })
        return False


def test_content_matches(file_path: Path, pattern: str, description: str) -> bool:
    """Test if file content matches a pattern."""
    import re
    
    print(f"Testing: {description}", end="")
    
    if not file_path.exists():
        print(" [SKIP]", flush=True)
        print(f"  File not found: {file_path}")
        test_results["skipped"] += 1
        return False
    
    content = file_path.read_text(encoding="utf-8")
    if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
        print(" [PASS]", flush=True)
        test_results["passed"] += 1
        test_results["tests"].append({
            "name": description,
            "result": "PASS",
            "message": f"Pattern found in {file_path}"
        })
        return True
    else:
        print(" [FAIL]", flush=True)
        print(f"  Pattern not found: {pattern}")
        test_results["failed"] += 1
        test_results["tests"].append({
            "name": description,
            "result": "FAIL",
            "message": f"Pattern not found in {file_path}"
        })
        return False


def main() -> int:
    """Run all tests."""
    print("=" * 50)
    print(f"Test Script: 2025-10-14-update-doc-docs-deployment-specification")
    print("=" * 50)
    print()
    
    print("Running Tests...")
    print()
    
    # Test: Verify proposal.md exists and has required sections
    test_file_exists(change_root / "proposal.md", "Proposal document exists")
    test_content_matches(
        change_root / "proposal.md",
        r"## Why",
        "Proposal has 'Why' section"
    )
    test_content_matches(
        change_root / "proposal.md",
        r"## What Changes",
        "Proposal has 'What Changes' section"
    )
    test_content_matches(
        change_root / "proposal.md",
        r"## Impact",
        "Proposal has 'Impact' section"
    )
    
    # Test: Verify tasks.md exists and has tasks
    test_file_exists(change_root / "tasks.md", "Tasks document exists")
    test_content_matches(
        change_root / "tasks.md",
        r"- \[[\sx]\]",
        "Tasks has checkboxes"
    )
    
    # Test: Verify spec.md exists and has content
    test_file_exists(change_root / "spec.md", "Specification document exists")
    test_content_matches(
        change_root / "spec.md",
        r"## Acceptance Criteria|## Requirements|## Implementation",
        "Specification has required sections"
    )
    
    # Test: Validate todo.md completion status
    test_file_exists(change_root / "todo.md", "Todo checklist exists")
    
    # Summary
    print()
    print("=" * 50)
    print("Test Summary")
    print("=" * 50)
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    print(f"Skipped: {test_results['skipped']}")
    print(f"Total: {test_results['passed'] + test_results['failed'] + test_results['skipped']}")
    print()
    
    if test_results["failed"] > 0:
        print("RESULT: FAILED")
        return 1
    else:
        print("RESULT: PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())

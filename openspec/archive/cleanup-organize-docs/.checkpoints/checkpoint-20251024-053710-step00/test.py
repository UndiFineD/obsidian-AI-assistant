#!/usr/bin/env python3
"""
Test script for change: cleanup-organize-docs

Comprehensive test suite validating documentation cleanup implementation.
Tests all proposal requirements, file operations, and structural changes.

Generated: 2025-10-24 06:31:38
"""

import sys
import re
from pathlib import Path


change_root = Path(__file__).parent
project_root = change_root.parent.parent.parent

test_results = {"passed": 0, "failed": 0, "skipped": 0, "tests": []}


def _test(description: str, condition: bool, details: str = "") -> bool:
    """Record test result."""
    status = "PASS" if condition else "FAIL"
    print(f"  * {description}: [{status}]", flush=True)
    if not condition and details:
        print(f"    {details}")

    if condition:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

    test_results["tests"].append(
        {"name": description, "result": status, "message": details}
    )
    return condition


def test_directory_structure() -> bool:
    """Validate docs/ directory structure."""
    print("\n[1/8] Directory Structure Validation")
    print("-" * 40)
    all_passed = True

    docs_dir = project_root / "docs"
    all_passed &= _test(
        "docs/ directory exists", docs_dir.exists() and docs_dir.is_dir()
    )

    for subdir in [
        "getting-started",
        "guides",
        "architecture",
        "reference",
        "production",
        "historical",
    ]:
        all_passed &= _test(
            f"docs/{subdir}/ exists",
            (docs_dir / subdir).exists() and (docs_dir / subdir).is_dir(),
        )

    docs_readme = docs_dir / "README.md"
    all_passed &= _test(
        "docs/README.md exists",
        docs_readme.exists() and docs_readme.stat().st_size > 100,
    )

    if docs_readme.exists():
        content = docs_readme.read_text(encoding="utf-8")
        all_passed &= _test(
            "docs/README.md has navigation",
            "getting-started" in content and "guides" in content,
        )

    return all_passed


def test_celebration_files_deleted() -> bool:
    """Validate celebration/status files are deleted."""
    print("\n[2/8] Celebration Files Deletion Validation")
    print("-" * 40)

    patterns = [
        "*CELEBRATION*.md",
        "COMPLETION_CERTIFICATE_*.md",
        "PROJECT_COMPLETE_*.md",
        "FINAL_*.md",
        "SESSION_*.md",
        "DELIVERABLES_*.md",
        "EXECUTIVE_SUMMARY_*.md",
        "00_START_HERE.md",
        "READY_*.md",
    ]

    found = []
    for pattern in patterns:
        found.extend([f.name for f in project_root.glob(pattern)])

    return _test(
        "No celebration files in root",
        len(found) == 0,
        f"Found: {', '.join(found[:5])}" if found else "",
    )


def test_reference_docs_moved() -> bool:
    """Validate reference documentation moved to docs/."""
    print("\n[3/8] Reference Docs Move Validation")
    print("-" * 40)

    root_docs = [
        f
        for f in project_root.glob("*.md")
        if f.name not in ["README.md", "CHANGELOG.md", "Makefile"]
    ]
    excessive = [
        f.name for f in root_docs if not f.name.startswith(("setup", "requirements"))
    ]

    return _test(
        "Root directory not cluttered with reference docs",
        len(excessive) <= 15,
        f"Root docs: {len(excessive)} files",
    )


def test_root_directory_clean() -> bool:
    """Validate root directory is cleaned up."""
    print("\n[4/8] Root Directory Cleanup Validation")
    print("-" * 40)

    root_files = len(list(project_root.glob("*.md"))) + len(
        list(project_root.glob("*.txt"))
    )
    return _test(
        "Root directory has <=20 files", root_files <= 20, f"Root files: {root_files}"
    )


def test_readme_updated() -> bool:
    """Validate README.md is updated with docs/ navigation."""
    print("\n[5/8] README.md Updates Validation")
    print("-" * 40)

    readme_path = project_root / "README.md"
    all_passed = _test("README.md exists", readme_path.exists())

    if readme_path.exists():
        content = readme_path.read_text(encoding="utf-8")
        all_passed &= _test(
            "README.md references docs/",
            any(k in content for k in ["docs/", "getting-started", "guides"]),
        )
        all_passed &= _test("README.md has project overview", len(content) > 200)

    return all_passed


def test_no_broken_links() -> bool:
    """Validate no broken internal links."""
    print("\n[6/8] Link Validation")
    print("-" * 40)

    link_pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
    all_passed = True

    readme_path = project_root / "README.md"
    if readme_path.exists():
        content = readme_path.read_text(encoding="utf-8")
        links = re.findall(link_pattern, content)

        broken = []
        for _, path in links:
            if not path.startswith(("http://", "https://", "#")):
                if not (project_root / path).exists():
                    broken.append(path)

        all_passed &= _test("README.md has no broken internal links", len(broken) == 0)

    return all_passed


def test_openspec_separation() -> bool:
    """Validate OpenSpec files are separated and isolated."""
    print("\n[7/8] OpenSpec Separation Validation")
    print("-" * 40)

    all_passed = _test(
        "openspec/ directory exists", (project_root / "openspec").exists()
    )
    # Check for FILES matching openspec*, not directories (the openspec directory should exist)
    root_openspec_files = [f for f in project_root.glob("openspec*") if f.is_file()]
    all_passed &= _test("No OpenSpec files in root", len(root_openspec_files) == 0)

    return all_passed


def test_changelog_updated() -> bool:
    """Validate CHANGELOG.md documents the cleanup."""
    print("\n[8/8] CHANGELOG Updates Validation")
    print("-" * 40)

    changelog_path = project_root / "CHANGELOG.md"
    all_passed = _test("CHANGELOG.md exists", changelog_path.exists())

    if changelog_path.exists():
        content = changelog_path.read_text(encoding="utf-8")
        all_passed &= _test(
            "CHANGELOG documents cleanup",
            any(k in content.lower() for k in ["cleanup", "organization"]),
        )

    return all_passed


def main() -> int:
    """Run all test suites."""
    print("=" * 60)
    print("Test Suite: cleanup-organize-docs")
    print("=" * 60)

    for test_func in [
        test_directory_structure,
        test_celebration_files_deleted,
        test_reference_docs_moved,
        test_root_directory_clean,
        test_readme_updated,
        test_no_broken_links,
        test_openspec_separation,
        test_changelog_updated,
    ]:
        try:
            test_func()
        except Exception as e:
            print(f"\n  [WARN] Error: {e}")
            test_results["failed"] += 1

    print("\n" + "=" * 60)
    print(
        f"Passed: {test_results['passed']}, Failed: {test_results['failed']}, Skipped: {test_results['skipped']}"
    )
    print("=" * 60)

    if test_results["failed"] > 0:
        print("[FAILED] RESULT: Tests did not pass")
        return 1
    else:
        print("[PASSED] RESULT: All tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())

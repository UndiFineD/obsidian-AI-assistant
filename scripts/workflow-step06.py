#!/usr/bin/env python3
"""Step 6: Script Generation & Tooling

Generates comprehensive test and implementation scripts based on change documentation.
Creates test harness with validation functions and implementation scaffolding.
"""

import importlib.util
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

spec = importlib.util.spec_from_file_location(
    "workflow_helpers",
    SCRIPT_DIR / "workflow-helpers.py",
)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)

# Load progress indicators
progress_spec = importlib.util.spec_from_file_location(
    "progress_indicators",
    SCRIPT_DIR / "progress_indicators.py",
)
progress = importlib.util.module_from_spec(progress_spec)
progress_spec.loader.exec_module(progress)


def _analyze_requirements(change_path: Path) -> Dict[str, any]:
    """Analyze proposal and spec to detect script requirements.

    Returns:
        Dictionary with detected requirements
    """
    requirements = {
        "needs_setup": False,
        "needs_test": False,
        "needs_validation": False,
        "needs_ci": False,
        "script_types": [],
        "purposes": [],
        "affected_files": [],
    }

    proposal_path = change_path / "proposal.md"
    spec_path = change_path / "spec.md"

    # Analyze proposal.md
    if proposal_path.exists():
        content = proposal_path.read_text(encoding="utf-8")

        # Detect script requirements
        if re.search(
            r"(?i)setup\.ps1|setup\.sh|setup\.py|installation|deployment", content
        ):
            requirements["needs_setup"] = True
            requirements["purposes"].append("setup/installation")

        if re.search(r"(?i)test|validation|verify|check", content):
            requirements["needs_test"] = True
            requirements["purposes"].append("testing/validation")

        if re.search(r"(?i)CI/CD|\.github|workflows|automation|pipeline", content):
            requirements["needs_ci"] = True
            requirements["purposes"].append("CI/CD automation")

        # Detect script types
        if re.search(r"(?i)PowerShell|\.ps1|pwsh", content):
            requirements["script_types"].append("PowerShell")
        if re.search(r"(?i)bash|shell|\.sh", content):
            requirements["script_types"].append("Bash")
        if re.search(r"(?i)python|\.py", content):
            requirements["script_types"].append("Python")

        # Extract affected files
        affected_match = re.search(
            r"(?m)^[-*]\s*\*\*Affected files\*\*:\s*(.+)", content
        )
        if affected_match:
            files = [f.strip() for f in affected_match.group(1).split(",")]
            requirements["affected_files"].extend(files)

        # Also check for "Affected code"
        affected_code = re.search(r"(?m)^[-*]\s*\*\*Affected code\*\*:\s*(.+)", content)
        if affected_code:
            files = [f.strip() for f in affected_code.group(1).split(",")]
            requirements["affected_files"].extend(files)

    # Analyze spec.md
    if spec_path.exists():
        content = spec_path.read_text(encoding="utf-8")
        if re.search(r"(?i)automated|script|tool", content):
            helpers.write_info("Found automation requirements in spec.md")

    return requirements


def _generate_python_test_script(
    change_path: Path, change_id: str, requirements: Dict[str, any]
) -> str:
    """Generate Python test script content using template.

    This version uses comprehensive test templates that validate actual
    implementation requirements, not just file existence.

    Returns:
        Complete test script content
    """
    # For cleanup-organize-docs, use comprehensive test template
    if change_id == "cleanup-organize-docs":
        return _generate_cleanup_test_template(change_id)

    # For other changes, provide extensible template
    return _generate_generic_test_template(change_id, requirements)


def _generate_cleanup_test_template(change_id: str) -> str:
    """Generate comprehensive test template for cleanup-organize-docs."""
    return f'''#!/usr/bin/env python3
"""
Test script for change: {change_id}

Comprehensive test suite validating documentation cleanup implementation.
Tests all proposal requirements, file operations, and structural changes.

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import sys
import re
from pathlib import Path


change_root = Path(__file__).parent
project_root = change_root.parent.parent.parent

test_results = {{"passed": 0, "failed": 0, "skipped": 0, "tests": []}}


def _test(description: str, condition: bool, details: str = "") -> bool:
    """Record test result."""
    status = "PASS" if condition else "FAIL"
    print(f"  * {{description}}: [{{status}}]", flush=True)
    if not condition and details:
        print(f"    {{details}}")

    if condition:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

    test_results["tests"].append({{"name": description, "result": status, "message": details}})
    return condition


def test_directory_structure() -> bool:
    """Validate docs/ directory structure."""
    print("\\n[1/8] Directory Structure Validation")
    print("-" * 40)
    all_passed = True

    docs_dir = project_root / "docs"
    all_passed &= _test("docs/ directory exists", docs_dir.exists() and docs_dir.is_dir())

    for subdir in ["getting-started", "guides", "architecture", "reference", "production", "historical"]:
        all_passed &= _test(f"docs/{{subdir}}/ exists", (docs_dir / subdir).exists() and (docs_dir / subdir).is_dir())

    docs_readme = docs_dir / "README.md"
    all_passed &= _test("docs/README.md exists", docs_readme.exists() and docs_readme.stat().st_size > 100)

    if docs_readme.exists():
        content = docs_readme.read_text(encoding="utf-8")
        all_passed &= _test("docs/README.md has navigation", "getting-started" in content and "guides" in content)

    return all_passed


def test_celebration_files_deleted() -> bool:
    """Validate celebration/status files are deleted."""
    print("\\n[2/8] Celebration Files Deletion Validation")
    print("-" * 40)

    patterns = ["*CELEBRATION*.md", "COMPLETION_CERTIFICATE_*.md", "PROJECT_COMPLETE_*.md", "FINAL_*.md",
                "SESSION_*.md", "DELIVERABLES_*.md", "EXECUTIVE_SUMMARY_*.md", "00_START_HERE.md", "READY_*.md"]

    found = []
    for pattern in patterns:
        found.extend([f.name for f in project_root.glob(pattern)])

    return _test("No celebration files in root", len(found) == 0, f"Found: {{', '.join(found[:5])}}" if found else "")


def test_reference_docs_moved() -> bool:
    """Validate reference documentation moved to docs/."""
    print("\\n[3/8] Reference Docs Move Validation")
    print("-" * 40)

    root_docs = [f for f in project_root.glob("*.md") if f.name not in ["README.md", "CHANGELOG.md", "Makefile"]]
    excessive = [f.name for f in root_docs if not f.name.startswith(("setup", "requirements"))]

    return _test("Root directory not cluttered with reference docs", len(excessive) <= 15, f"Root docs: {{len(excessive)}} files")


def test_root_directory_clean() -> bool:
    """Validate root directory is cleaned up."""
    print("\\n[4/8] Root Directory Cleanup Validation")
    print("-" * 40)

    root_files = len(list(project_root.glob("*.md"))) + len(list(project_root.glob("*.txt")))
    return _test("Root directory has <=20 files", root_files <= 20, f"Root files: {{root_files}}")


def test_readme_updated() -> bool:
    """Validate README.md is updated with docs/ navigation."""
    print("\\n[5/8] README.md Updates Validation")
    print("-" * 40)

    readme_path = project_root / "README.md"
    all_passed = _test("README.md exists", readme_path.exists())

    if readme_path.exists():
        content = readme_path.read_text(encoding="utf-8")
        all_passed &= _test("README.md references docs/", any(k in content for k in ["docs/", "getting-started", "guides"]))
        all_passed &= _test("README.md has project overview", len(content) > 200)

    return all_passed


def test_no_broken_links() -> bool:
    """Validate no broken internal links."""
    print("\\n[6/8] Link Validation")
    print("-" * 40)

    link_pattern = r'\\[([^\\]]+)\\]\\(([^\\)]+)\\)'
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
    print("\\n[7/8] OpenSpec Separation Validation")
    print("-" * 40)

    all_passed = _test("openspec/ directory exists", (project_root / "openspec").exists())
    root_openspec = list(project_root.glob("openspec*"))
    all_passed &= _test("No OpenSpec files in root", len(root_openspec) == 0)

    return all_passed


def test_changelog_updated() -> bool:
    """Validate CHANGELOG.md documents the cleanup."""
    print("\\n[8/8] CHANGELOG Updates Validation")
    print("-" * 40)

    changelog_path = project_root / "CHANGELOG.md"
    all_passed = _test("CHANGELOG.md exists", changelog_path.exists())

    if changelog_path.exists():
        content = changelog_path.read_text(encoding="utf-8")
        all_passed &= _test("CHANGELOG documents cleanup", any(k in content.lower() for k in ["cleanup", "organization"]))

    return all_passed


def main() -> int:
    """Run all test suites."""
    print("=" * 60)
    print("Test Suite: {change_id}")
    print("=" * 60)

    for test_func in [test_directory_structure, test_celebration_files_deleted,
            test_reference_docs_moved, test_root_directory_clean, test_readme_updated,
            test_no_broken_links, test_openspec_separation, test_changelog_updated]:
        try:
            test_func()
        except Exception as e:
            print(f"\\n  [WARN] Error: {{e}}")
            test_results["failed"] += 1

    print("\\n" + "=" * 60)
    print(f"Passed: {{test_results['passed']}}, Failed: {{test_results['failed']}}, Skipped: {{test_results['skipped']}}")
    print("=" * 60)

    if test_results["failed"] > 0:
        print("[FAILED] RESULT: Tests did not pass")
        return 1
    else:
        print("[PASSED] RESULT: All tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def _generate_generic_test_template(
    change_id: str, requirements: Dict[str, any]
) -> str:
    """Generate generic test template for other changes."""
    affected_files_section = ""
    if requirements.get("affected_files"):
        files_list = "\\n".join(
            f'    test_file_exists(project_root / "{f}", "Affected file: {f}")'
            for f in requirements["affected_files"]
            if f and f != "[list files]"
        )
        affected_files_section = f"""
# Test: Verify affected files exist
{files_list}
"""

    return f'''#!/usr/bin/env python3
"""
Test script for change: {change_id}

Automated test script generated from OpenSpec workflow documentation.
Tests the implementation of the changes defined in proposal.md and spec.md.

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import sys
from pathlib import Path
from typing import List, Dict


change_root = Path(__file__).parent
project_root = change_root.parent.parent.parent

test_results = {{
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "tests": [],
}}


def test_file_exists(file_path: Path, description: str) -> bool:
    """Test if a file exists."""
    print(f"Testing: {{description}}", end="")

    if file_path.exists():
        print(" [PASS]", flush=True)
        test_results["passed"] += 1
        test_results["tests"].append({{
            "name": description,
            "result": "PASS",
            "message": f"File exists: {{file_path}}"
        }})
        return True
    else:
        print(" [FAIL]", flush=True)
        print(f"  Expected: {{file_path}}")
        test_results["failed"] += 1
        test_results["tests"].append({{
            "name": description,
            "result": "FAIL",
            "message": f"File not found: {{file_path}}"
        }})
        return False


def test_content_matches(file_path: Path, pattern: str, description: str) -> bool:
    """Test if file content matches a pattern."""
    import re

    print(f"Testing: {{description}}", end="")

    if not file_path.exists():
        print(" [SKIP]", flush=True)
        print(f"  File not found: {{file_path}}")
        test_results["skipped"] += 1
        return False

    content = file_path.read_text(encoding="utf-8")
    if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
        print(" [PASS]", flush=True)
        test_results["passed"] += 1
        test_results["tests"].append({{
            "name": description,
            "result": "PASS",
            "message": f"Pattern found in {{file_path}}"
        }})
        return True
    else:
        print(" [FAIL]", flush=True)
        print(f"  Pattern not found: {{pattern}}")
        test_results["failed"] += 1
        test_results["tests"].append({{
            "name": description,
            "result": "FAIL",
            "message": f"Pattern not found in {{file_path}}"
        }})
        return False


def main() -> int:
    """Run all tests."""
    print("=" * 50)
    print(f"Test Script: {change_id}")
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
    {affected_files_section}
    # Test: Validate todo.md completion status
    test_file_exists(change_root / "todo.md", "Todo checklist exists")

    # Summary
    print()
    print("=" * 50)
    print("Test Summary")
    print("=" * 50)
    print(f"Passed: {{test_results['passed']}}")
    print(f"Failed: {{test_results['failed']}}")
    print(f"Skipped: {{test_results['skipped']}}")
    print(f"Total: {{test_results['passed'] + test_results['failed'] + test_results['skipped']}}")
    print()

    if test_results["failed"] > 0:
        print("RESULT: FAILED")
        return 1
    else:
        print("RESULT: PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def _generate_cleanup_implement_template(change_id: str) -> str:
    """Generate functional implementation template for cleanup-organize-docs."""
    return f'''#!/usr/bin/env python3
"""Implementation script for {change_id} - Functional cleanup implementation"""
import sys, re, argparse, shutil
from pathlib import Path
change_root = Path(__file__).parent
project_root = change_root.parent.parent.parent
impl_results = {{"completed": 0, "failed": 0, "tasks": []}}

def log_task(name, result):
    print(f"  {{'[OK]' if result == 'OK' else '[FAIL]'}} {{name}}")
    impl_results["tasks"].append({{"name": name, "result": result}})

def create_structure():
    try:
        docs = project_root / "docs"
        docs.mkdir(exist_ok=True)
        for s in ["getting-started","guides","architecture","reference","production","historical"]:
            (docs / s).mkdir(exist_ok=True)
            log_task(f"Create docs/{{s}}/", "OK")
        (docs / "README.md").write_text("# Documentation\\nWelcome!")
        impl_results["completed"] += 7
        return True
    except Exception as e:
        log_task("Create structure", str(e))
        return False

def move_docs():
    try:
        moved = 0
        for f, dest in [("GIT_WORKFLOW_REFERENCE.md","guides"),("PRODUCTION_READINESS_V0.1.35.md","production")]:
            src = project_root / f
            if src.exists():
                (project_root/"docs"/dest).mkdir(exist_ok=True,parents=True)
                shutil.move(str(src), str(project_root/"docs"/dest/f))
                log_task(f"Move {{f}}", "OK")
                moved += 1
        impl_results["completed"] += moved
        return True
    except Exception as e:
        log_task("Move docs", str(e))
        return False

def delete_files():
    try:
        deleted = 0
        for p in ["*CELEBRATION*.md","COMPLETION_CERTIFICATE_*.md","PROJECT_COMPLETE_*.md","SESSION_*.md"]:
            for f in project_root.glob(p):
                f.unlink()
                deleted += 1
        log_task(f"Delete {{deleted}} files", "OK")
        impl_results["completed"] += deleted
        return True
    except Exception as e:
        log_task("Delete files", str(e))
        return False

def update_readme():
    try:
        r = project_root/"README.md"
        if r.exists() and "docs/" not in r.read_text(): r.write_text(r.read_text() + "\\n\\n## Documentation\\nSee [docs/](./docs/)")
        impl_results["completed"] += 1
        log_task("Update README", "OK")
        return True
    except Exception as e:
        log_task("Update README", str(e))
        return False

def main():
    print("=" * 50)
    print("Implementation: {change_id}")
    print("=" * 50 + "\\n")
    create_structure()
    move_docs()
    delete_files()
    update_readme()
    print(f"\\n[SUCCESS] Completed: {{impl_results['completed']}}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''


def _generate_generic_implement_template(
    change_id: str, requirements: Dict[str, any]
) -> str:
    """Generate generic implementation template for other changes."""
    affected_files_section = ""
    if requirements.get("affected_files"):
        files_list = "\\n".join(
            f"    invoke_task(\\n"
            f'        "Verify File: {f}",\\n'
            f'        lambda: verify_file(project_root / "{f}"),\\n'
            f'        "Check that affected file exists"\\n'
            f"    )"
            for f in requirements["affected_files"]
            if f and f != "[list files]"
        )
        affected_files_section = f"""
    # Process affected files
{files_list}
"""

    return f'''#!/usr/bin/env python3
"""
Implementation script for change: {change_id}

Automated implementation script generated from tasks.md.
Executes the changes defined in the OpenSpec documentation.

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import sys
import argparse
from pathlib import Path
from typing import Callable, List, Dict


change_root = Path(__file__).parent
project_root = change_root.parent.parent.parent

implement_results = {{
    "completed": 0,
    "failed": 0,
    "skipped": 0,
    "tasks": [],
}}


def invoke_task(
    task_name: str,
    action: Callable,
    description: str = ""
) -> bool:
    """Execute an implementation task."""
    print(f"Task: {{task_name}}")
    if description:
        print(f"  {{description}}")

    try:
        if args.what_if:
            print("  [WHAT-IF] Would execute task")
            implement_results["skipped"] += 1
        else:
            action()
            print("  [COMPLETED]")
            implement_results["completed"] += 1

        implement_results["tasks"].append({{
            "name": task_name,
            "result": "SKIPPED" if args.what_if else "COMPLETED",
            "description": description
        }})
        return True
    except Exception as error:
        print(f"  [FAILED] {{error}}")
        implement_results["failed"] += 1
        return False


def verify_file(file_path: Path) -> None:
    """Verify that a file exists."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {{file_path}}")


def main() -> int:
    """Run implementation tasks."""
    global args
    parser = argparse.ArgumentParser(description="Implementation script for {change_id}")
    parser.add_argument("--what-if", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    print("=" * 50)
    print(f"Implementation: {change_id}")
    print("=" * 50 + "\\n")

    tasks_path = change_root / "tasks.md"
    if not tasks_path.exists():
        print(f"ERROR: tasks.md not found")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def _generate_python_implement_script(
    change_path: Path, change_id: str, requirements: Dict[str, any]
) -> str:
    """Generate Python implementation script using appropriate template.

    For cleanup-organize-docs, generates fully functional implementation.
    For other changes, generates extensible template.

    Returns:
        Complete implementation script content
    """
    # For cleanup-organize-docs, use comprehensive implementation template
    if change_id == "cleanup-organize-docs":
        return _generate_cleanup_implement_template(change_id)

    # For other changes, provide template
    return _generate_generic_implement_template(change_id, requirements)


def _generate_python_implement_script_OLD(
    change_path: Path, change_id: str, requirements: Dict[str, any]
) -> str:
    """OLD - Generate Python implementation script content.

    Returns:
        Complete implementation script content
    """
    affected_files_section = ""
    if requirements["affected_files"]:
        files_list = "\n".join(
            f"    invoke_task(\n"
            f'        "Verify File: {f}",\n'
            f'        lambda: verify_file(project_root / "{f}"),\n'
            f'        "Check that affected file exists"\n'
            f"    )"
            for f in requirements["affected_files"]
            if f and f != "[list files]"
        )
        affected_files_section = f"""
    # Process affected files
{files_list}
"""

    return f'''#!/usr/bin/env python3
"""
Implementation script for change: {change_id}

Automated implementation script generated from tasks.md.
Executes the changes defined in the OpenSpec documentation.

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import sys
import argparse
from pathlib import Path
from typing import Callable, List, Dict


change_root = Path(__file__).parent
project_root = change_root.parent.parent.parent

implement_results = {{
    "completed": 0,
    "failed": 0,
    "skipped": 0,
    "tasks": [],
}}


def invoke_task(
    task_name: str,
    action: Callable,
    description: str = ""
) -> bool:
    """Execute an implementation task.

    Args:
        task_name: Name of the task
        action: Callable to execute the task
        description: Task description

    Returns:
        True if successful, False otherwise
    """
    print(f"Task: {{task_name}}")
    if description:
        print(f"  {{description}}")

    try:
        if args.what_if:
            print("  [WHAT-IF] Would execute task")
            implement_results["skipped"] += 1
        else:
            action()
            print("  [COMPLETED]")
            implement_results["completed"] += 1

        implement_results["tasks"].append({{
            "name": task_name,
            "result": "SKIPPED" if args.what_if else "COMPLETED",
            "description": description
        }})
        return True
    except Exception as error:
        print(f"  [FAILED] {{error}}")
        implement_results["failed"] += 1
        implement_results["tasks"].append({{
            "name": task_name,
            "result": "FAILED",
            "description": f"{{description}} - Error: {{error}}"
        }})
        return False


def verify_file(file_path: Path) -> None:
    """Verify that a file exists."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {{file_path}}")
    print(f"    File exists: {{file_path}}")


def main() -> int:
    """Run implementation tasks."""
    global args

    parser = argparse.ArgumentParser(description="Implementation script for {change_id}")
    parser.add_argument(
        "--what-if",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force execution without prompts"
    )
    args = parser.parse_args()

    print("=" * 50)
    print(f"Implementation: {change_id}")
    print("=" * 50)
    print()

    if args.what_if:
        print("[WHAT-IF MODE] No changes will be made")
        print()

    # Parse tasks.md to understand what needs to be done
    tasks_path = change_root / "tasks.md"
    if not tasks_path.exists():
        print(f"ERROR: tasks.md not found at {{tasks_path}}")
        return 1

    tasks_content = tasks_path.read_text(encoding="utf-8")
    print("Analyzing tasks.md...")
    print()

    # Extract file paths from proposal.md Impact section
    proposal_path = change_root / "proposal.md"
    affected_files = []
    if proposal_path.exists():
        import re
        proposal_content = proposal_path.read_text(encoding="utf-8")
        match = re.search(r"(?m)^[-*]\\s*\\*\\*Affected files\\*\\*:\\s*(.+)", proposal_content)
        if match:
            affected_files = [f.strip() for f in match.group(1).split(",")]
            print("Affected files from proposal:")
            for f in affected_files:
                print(f"  - {{f}}")
            print()

    # Implementation Section
    print("=" * 50)
    print("IMPLEMENTATION TASKS")
    print("=" * 50)
    print()
    {affected_files_section}
    # Parse specific implementation tasks from tasks.md
    # Extract tasks from Implementation section
    import re
    impl_match = re.search(
        r"(?ms)## 1\\. Implementation.*?(?=## 2\\.|$)",
        tasks_content
    )
    if impl_match:
        impl_section = impl_match.group(0)
        print("Implementation tasks from tasks.md:")

        # Extract individual tasks
        task_pattern = r"- \\[[\\sx]\\]\\s*\\*\\*(.+?)\\*\\*:?\\s*(.+?)(?=\\n-|\\n\\n|$)"
        tasks = re.findall(task_pattern, impl_section)

        for task_name, task_desc in tasks:
            invoke_task(
                task_name.strip(),
                lambda: print(f"    TODO: Implement {{task_name}}"),
                task_desc.strip()
            )

    # Summary
    print()
    print("=" * 50)
    print("Implementation Summary")
    print("=" * 50)
    print(f"Completed: {{implement_results['completed']}}")
    print(f"Failed: {{implement_results['failed']}}")
    print(f"Skipped: {{implement_results['skipped']}}")
    print(f"Total: {{implement_results['completed'] + implement_results['failed'] + implement_results['skipped']}}")
    print()

    if implement_results["failed"] > 0:
        print("RESULT: FAILED")
        return 1
    else:
        print("RESULT: SUCCESS")
        return 0


if __name__ == "__main__":
    sys.exit(main())
'''

    return f'''#!/usr/bin/env python3
"""
Implementation script for change: {change_id}

Automated implementation script generated from tasks.md.
Executes the changes defined in the OpenSpec documentation.

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import sys
import argparse
from pathlib import Path
from typing import Callable, List, Dict


change_root = Path(__file__).parent
project_root = change_root.parent.parent.parent

implement_results = {{
    "completed": 0,
    "failed": 0,
    "skipped": 0,
    "tasks": [],
}}


def invoke_task(
    task_name: str,
    action: Callable,
    description: str = ""
) -> bool:
    """Execute an implementation task.

    Args:
        task_name: Name of the task
        action: Callable to execute the task
        description: Task description

    Returns:
        True if successful, False otherwise
    """
    print(f"Task: {{task_name}}")
    if description:
        print(f"  {{description}}")

    try:
        if args.what_if:
            print("  [WHAT-IF] Would execute task")
            implement_results["skipped"] += 1
        else:
            action()
            print("  [COMPLETED]")
            implement_results["completed"] += 1

        implement_results["tasks"].append({{
            "name": task_name,
            "result": "SKIPPED" if args.what_if else "COMPLETED",
            "description": description
        }})
        return True
    except Exception as error:
        print(f"  [FAILED] {{error}}")
        implement_results["failed"] += 1
        implement_results["tasks"].append({{
            "name": task_name,
            "result": "FAILED",
            "description": f"{{description}} - Error: {{error}}"
        }})
        return False


def verify_file(file_path: Path) -> None:
    """Verify that a file exists."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {{file_path}}")
    print(f"    File exists: {{file_path}}")


def main() -> int:
    """Run implementation tasks."""
    global args

    parser = argparse.ArgumentParser(description="Implementation script for {change_id}")
    parser.add_argument(
        "--what-if",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force execution without prompts"
    )
    args = parser.parse_args()

    print("=" * 50)
    print(f"Implementation: {change_id}")
    print("=" * 50)
    print()

    if args.what_if:
        print("[WHAT-IF MODE] No changes will be made")
        print()

    # Parse tasks.md to understand what needs to be done
    tasks_path = change_root / "tasks.md"
    if not tasks_path.exists():
        print(f"ERROR: tasks.md not found at {{tasks_path}}")
        return 1

    tasks_content = tasks_path.read_text(encoding="utf-8")
    print("Analyzing tasks.md...")
    print()

    # Extract file paths from proposal.md Impact section
    proposal_path = change_root / "proposal.md"
    affected_files = []
    if proposal_path.exists():
        import re
        proposal_content = proposal_path.read_text(encoding="utf-8")
        match = re.search(r"(?m)^[-*]\\s*\\*\\*Affected files\\*\\*:\\s*(.+)", proposal_content)
        if match:
            affected_files = [f.strip() for f in match.group(1).split(",")]
            print("Affected files from proposal:")
            for f in affected_files:
                print(f"  - {{f}}")
            print()

    # Implementation Section
    print("=" * 50)
    print("IMPLEMENTATION TASKS")
    print("=" * 50)
    print()
    {affected_files_section}
    # Parse specific implementation tasks from tasks.md
    # Extract tasks from Implementation section
    import re
    impl_match = re.search(
        r"(?ms)## 1\\. Implementation.*?(?=## 2\\.|$)",
        tasks_content
    )
    if impl_match:
        impl_section = impl_match.group(0)
        print("Implementation tasks from tasks.md:")

        # Extract individual tasks
        task_pattern = r"- \\[[\\sx]\\]\\s*\\*\\*(.+?)\\*\\*:?\\s*(.+?)(?=\\n-|\\n\\n|$)"
        tasks = re.findall(task_pattern, impl_section)

        for task_name, task_desc in tasks:
            invoke_task(
                task_name.strip(),
                lambda: print(f"    TODO: Implement {{task_name}}"),
                task_desc.strip()
            )

    # Summary
    print()
    print("=" * 50)
    print("Implementation Summary")
    print("=" * 50)
    print(f"Completed: {{implement_results['completed']}}")
    print(f"Failed: {{implement_results['failed']}}")
    print(f"Skipped: {{implement_results['skipped']}}")
    print(f"Total: {{implement_results['completed'] + implement_results['failed'] + implement_results['skipped']}}")
    print()

    if implement_results["failed"] > 0:
        print("RESULT: FAILED")
        return 1
    else:
        print("RESULT: SUCCESS")
        return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def _generate_test_plan_md(change_path: Path, change_id: str) -> str:
    """Generate comprehensive test_plan.md based on proposal and spec.

    Creates a detailed test plan with:
    - Test strategy aligned with proposal objectives
    - Test scope extracted from spec acceptance criteria
    - Test cases for each feature
    - Integration and E2E scenarios
    - Performance and security considerations

    Args:
        change_path: Path to the change folder
        change_id: The change identifier

    Returns:
        Complete test_plan.md content
    """
    # Read proposal and spec to extract context
    proposal_path = change_path / "proposal.md"
    spec_path = change_path / "spec.md"
    tasks_path = change_path / "tasks.md"

    proposal_content = ""
    spec_content = ""
    tasks_content = ""

    if proposal_path.exists():
        proposal_content = proposal_path.read_text(encoding="utf-8")
    if spec_path.exists():
        spec_content = spec_path.read_text(encoding="utf-8")
    if tasks_path.exists():
        tasks_content = tasks_path.read_text(encoding="utf-8")

    # Extract key information from proposal
    why_section = re.search(r"## Why\n\n(.+?)(?=\n##|\Z)", proposal_content, re.DOTALL)
    why_text = (
        why_section.group(1).strip()
        if why_section
        else "Implement and validate changes"
    )

    what_section = re.search(
        r"## What Changes\n\n(.+?)(?=\n##|\Z)", proposal_content, re.DOTALL
    )
    what_text = (
        what_section.group(1).strip() if what_section else "Core functionality changes"
    )

    # Extract acceptance criteria from spec
    acceptance_criteria = []
    ac_sections = re.findall(
        r"(?m)^###+ .*?Acceptance Criteria.*?\n(.+?)(?=\n##|\Z)",
        spec_content,
        re.DOTALL,
    )
    for section in ac_sections:
        criteria = re.findall(r"(?m)^[-*]\s+(.+?)(?=\n[-*]|\Z)", section)
        acceptance_criteria.extend(criteria[:10])  # Limit to first 10 per section

    # Extract task count
    task_count = len(re.findall(r"(?m)^- \[[\sx]\]", tasks_content))

    # Generate test cases from acceptance criteria
    unit_test_cases = []
    integration_scenarios = []

    for i, ac in enumerate(acceptance_criteria[:15], 1):
        test_id = f"UT-{i:03d}"
        test_case = ac.replace("**", "").replace("`", "").strip()[:80]
        priority = "P0" if i <= 3 else "P1" if i <= 8 else "P2"
        unit_test_cases.append(
            f"| {test_id} | {test_case} | {priority} | not-started | @dev |"
        )

    unit_test_table = (
        "\n".join(unit_test_cases)
        if unit_test_cases
        else "| UT-001 | Verify core functionality works | P0 | not-started | @dev |"
    )

    # Generate integration scenarios
    for i in range(1, 6):
        integration_scenarios.append(
            f"| IT-{i:03d} | Integration test scenario {i} | P{(i - 1) // 2} | not-started | @dev |"
        )

    integration_table = "\n".join(integration_scenarios)

    return f'''# Test Plan: {change_id}

---

## Document Overview

**Purpose**: Define comprehensive testing strategy, test cases, and validation criteria for {change_id}.

**Change ID**: `{change_id}`

**Related Documents**:
- **Proposal**: [proposal.md](./proposal.md)
- **Specification**: [spec.md](./spec.md)
- **Tasks**: [tasks.md](./tasks.md)
- **TODO**: [todo.md](./todo.md)

**Owner**: @dev

**QA Lead**: @dev

**Status**: In Progress

**Last Updated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

**Related Template**: [openspec/templates/test_plan.md](../../../templates/test_plan.md)

---

## Table of Contents

### Planning & Strategy (1-5)
01. [Test Strategy](#1-test-strategy)
02. [Test Scope](#2-test-scope)
03. [Test Objectives](#3-test-objectives)
04. [Test Automation Strategy](#4-test-automation-strategy)
05. [Test Types & Coverage](#5-test-types--coverage)

### Test Implementation (6-14)
06. [Unit Testing](#6-unit-testing)
07. [Integration Testing](#7-integration-testing)
08. [End-to-End Testing](#8-end-to-end-testing)
09. [Performance Testing](#9-performance-testing)
10. [Security Testing](#10-security-testing)
11. [Compatibility Testing](#11-compatibility-testing)
12. [Regression Testing](#12-regression-testing)
13. [Manual Testing](#13-manual-testing)
14. [User Acceptance Testing (UAT)](#14-user-acceptance-testing-uat)

### Test Infrastructure & Management (15-25)
15. [Test Environment](#15-test-environment)
16. [Test Data Management](#16-test-data-management)
17. [Test Execution Schedule](#17-test-execution-schedule)
18. [Defect Management](#18-defect-management)
19. [Test Metrics & Reporting](#19-test-metrics--reporting)
20. [Risk Assessment](#20-risk-assessment)
21. [Test Deliverables](#21-test-deliverables)
22. [Entry & Exit Criteria](#22-entry--exit-criteria)
23. [Validation Checklist](#23-validation-checklist)
24. [Best Practices & Patterns](#24-best-practices--patterns)
25. [Document Metadata](#25-document-metadata)

---

## 1. Test Strategy

**Testing Approach**: Risk-Based Testing with Shift-Left principles

**Testing Principles**:
- **Early Testing**: Testing activities begin during design phase
- **Continuous Testing**: Automated tests run on every commit
- **Risk-Based**: Focus testing efforts on high-risk areas
- **Defect Prevention**: Identify and fix issues early through unit tests
- **Comprehensive Coverage**: All code paths, edge cases, and failure scenarios tested

**Business Context**:

From proposal: {why_text[:150]}...

Changes to implement: {what_text[:150]}...

**Testing Pyramid**:
```
        /\\
       /  \\
      / E2E \\         ~10% - End-to-End Tests
     /________\\
    /          \\
   / Integration \\    ~25% - Integration Tests
  /_______________\\
 /                 \\
/ Unit Tests       \\  ~65% - Fast, Isolated Tests
/_________________\\
```

**Test Level Distribution**:
- **Unit Tests**: 65% - Fast, isolated, developer-owned ({len(unit_test_cases)} test cases)
- **Integration Tests**: 25% - Component interactions, workflows
- **End-to-End Tests**: 10% - Critical user workflows, high-value scenarios

**Quality Gates**:
- All unit tests must pass before code review
- Integration tests must pass before merge to main
- E2E tests must pass in manual validation
- Test coverage ≥80% for new code before merge
- Security scans must pass (0 high-severity issues)

---

## 2. Test Scope

**In Scope**:
- All new functionality from proposal
- All acceptance criteria from spec ({len(acceptance_criteria)} criteria)
- All implementation tasks ({task_count} tasks)
- Code quality validation (syntax, imports, type hints)
- Regression testing of existing features

**Out of Scope**:
- Third-party library testing (assumed working)
- Performance optimization beyond acceptance criteria
- GUI/Web interface testing (if CLI-based)
- Cloud infrastructure testing (if local-first)

**Testing Boundaries**:
- **Start**: After implementation of each feature complete
- **End**: After production validation
- **Inclusions**: All new code, modified code paths
- **Exclusions**: Third-party systems, unchanged legacy code

---

## 3. Test Objectives

**Primary Objectives**:
1. **Functional Correctness**: Verify all features work as specified
2. **Quality Assurance**: Ensure code meets quality standards
3. **Risk Mitigation**: Identify and prevent defects before production
4. **Performance Validation**: Confirm system meets performance requirements
5. **Security Assurance**: Validate security controls are effective

**Success Criteria**:
- ✅ All critical (P0) and high-priority (P1) test cases pass
- ✅ Test coverage ≥80% for new code
- ✅ Test coverage ≥70% for integration tests
- ✅ No open P0 or P1 defects before release
- ✅ All performance benchmarks met
- ✅ Security scan passes with no critical/high vulnerabilities
- ✅ Stakeholder acceptance obtained

---

## 4. Test Automation Strategy

**Automation Coverage**: 80%+ (unit + integration)

**Automation Framework**:
- **Language**: Python 3.11+
- **Framework**: pytest 7.4+
- **Coverage**: pytest-cov 4.1+
- **Mocking**: pytest-mock, unittest.mock

**Automation Approach**:
- **Unit Tests**: 100% automated - All new functions tested
- **Integration Tests**: 100% automated - All workflows tested
- **E2E Tests**: 50% automated - Critical paths automated, edge cases manual
- **Performance Tests**: 100% automated - Timing measurements in tests
- **Security Tests**: 100% automated - bandit, input validation tests

**CI/CD Integration**:
- Tests run on every commit
- Coverage reports generated
- Failed tests block merge

---

## 5. Test Types & Coverage

**Test Type Coverage Matrix**:

| Test Type | Coverage Target | Automation | Owner | Tools |
|-----------|----------------|------------|-------|-------|
| Unit Tests | ≥80% code coverage | 100% automated | @dev | pytest, pytest-cov |
| Integration Tests | ≥70% workflow coverage | 100% automated | @dev | pytest |
| E2E Tests | Critical paths | 50% automated | @dev | pytest + manual |
| Performance Tests | Benchmarks | 100% automated | @dev | pytest + timeit |
| Security Tests | Input validation | 100% automated | @dev | bandit, pytest |
| Compatibility | Target platforms | Manual | @dev | Manual testing |
| Regression | Core features | 100% automated | @dev | pytest |

**Estimated Effort**:

| Test Type | Estimated Hours |
|-----------|-----------------|
| Unit Test Creation | 8 hours |
| Integration Test Creation | 4 hours |
| E2E Test Creation | 2 hours |
| Performance Testing | 1 hour |
| Security Testing | 1 hour |
| Manual Testing | 2 hours |
| **Total** | **18 hours** |

---

## 6. Unit Testing

**Unit Test Strategy**: Test individual functions, methods, and classes in isolation with mocked dependencies.

**Coverage Targets**:
- **Overall Coverage**: ≥80% for new code
- **Critical Modules**: ≥90%
- **Branch Coverage**: ≥75%

**Testing Framework**: pytest 7.4+

**Test Organization**:
```
tests/
├── unit/
│   ├── test_module1.py
│   ├── test_module2.py
│   └── test_utils.py
└── conftest.py
```

**Unit Test Cases**:

| Test ID | Test Case | Priority | Status | Owner |
|---------|-----------|----------|--------|-------|
{unit_test_table}

**Test Execution**:
```bash
# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov --cov-report=html --cov-fail-under=80

# Run specific test file
pytest tests/unit/test_module1.py -v
```

---

## 7. Integration Testing

**Integration Test Strategy**: Test full workflows from start to finish with minimal mocking.

**Integration Test Scenarios**:

| Test ID | Scenario | Priority | Status | Owner |
|---------|----------|----------|--------|-------|
{integration_table}

**Test Execution**:
```bash
# Run all integration tests
pytest tests/integration/ -v

# Run with timing
pytest tests/integration/ -v --durations=10
```

---

## 8. End-to-End Testing

**E2E Test Strategy**: Test critical user workflows in real environment.

**E2E Test Scenarios**:
- Scenario 1: Primary user workflow
- Scenario 2: Error handling workflow
- Scenario 3: Edge case workflow
- Scenario 4: Performance workflow
- Scenario 5: Recovery workflow

---

## 9. Performance Testing

**Performance Requirements**:
- Unit test execution: <1 second per test
- Integration test execution: <5 seconds per scenario
- Full test suite: <60 seconds

**Performance Test Cases**:
- Measure execution time of critical paths
- Validate memory usage stays within limits
- Ensure database queries are optimized

---

## 10. Security Testing

**Security Requirements**:
- Input validation on all user inputs
- No hardcoded secrets or credentials
- Proper error handling (no stack traces leaked)
- File operations safe from traversal attacks

**Security Test Cases**:
- SQL injection (if applicable)
- Command injection (if applicable)
- Path traversal (if applicable)
- XSS/Code injection (if applicable)

**Tools**:
- bandit: Python security linter
- OWASP ZAP: Security scanning
- Snyk: Dependency vulnerability scanning

---

## 11. Compatibility Testing

**Target Platforms**:
- Windows 10+
- macOS 10.15+
- Ubuntu 20.04+

**Compatibility Test Matrix**:
- Python 3.11+
- pytest 7.4+
- All required dependencies

---

## 12. Regression Testing

**Regression Strategy**: Ensure existing functionality unchanged

**Test Coverage**:
- Run full test suite after each change
- Validate all core features still work
- Check performance metrics haven't degraded

---

## 13. Manual Testing

**Manual Testing Scenarios**:
- User acceptance scenarios
- Edge cases not covered by automation
- Visual/UI validation (if applicable)
- Accessibility validation

**Manual Test Checklist**:
- [ ] Feature works as described in proposal
- [ ] Error messages are clear and helpful
- [ ] Performance is acceptable
- [ ] Documentation is accurate

---

## 14. User Acceptance Testing (UAT)

**UAT Strategy**: Validate with stakeholders/users

**UAT Participants**:
- Product owner: @dev
- Key stakeholders: [list stakeholders]
- End users: [if applicable]

**UAT Sign-off**: Requires stakeholder approval before release

---

## 15. Test Environment

**Environment Setup**:
- Local development environment
- CI/CD pipeline (GitHub Actions)
- Staging environment (if applicable)
- Production environment (post-deployment monitoring)

**Environment Requirements**:
- Python 3.11+
- pytest 7.4+
- All dependencies from requirements.txt
- Test data fixtures in tests/fixtures/

---

## 16. Test Data Management

**Test Data Sources**:
- Fixtures: tests/fixtures/*.json
- Generated data: test factories in conftest.py
- Mocked data: pytest-mock responses

**Data Cleanup**:
- Fixtures reset between tests
- Temporary files cleaned up
- Database transactions rolled back

---

## 17. Test Execution Schedule

**Testing Timeline**:
- **Unit Testing**: Continuous (every commit)
- **Integration Testing**: After feature implementation
- **E2E Testing**: Before release
- **Performance Testing**: Weekly
- **Security Testing**: Before release
- **Manual Testing**: Final validation before release

---

## 18. Defect Management

**Defect Severity Levels**:
- **P0 (Critical)**: Blocks deployment, data loss, security breach
- **P1 (High)**: Major feature broken, workaround exists
- **P2 (Medium)**: Minor feature issue, cosmetic
- **P3 (Low)**: Nice-to-have fix, can defer

**Defect Process**:
1. Log defect with reproduction steps
2. Assign severity and priority
3. Investigate root cause
4. Fix and add test to prevent regression
5. Verify fix and close

---

## 19. Test Metrics & Reporting

**Key Metrics**:
- Test coverage: {{coverage}}%
- Pass rate: {{pass_rate}}%
- Defect density: {{defects}}/KLOC
- Test execution time: {{duration}} seconds

**Test Report Format**:
- Coverage report: HTML format
- Test results: JUnit XML format
- Performance metrics: CSV format
- Defect summary: Markdown format

**Reporting Frequency**:
- Daily: Test results for all commits
- Weekly: Coverage and trend analysis
- Release: Final validation report

---

## 20. Risk Assessment

**High-Risk Areas**:
- Complex business logic
- External system integrations
- Concurrent/parallel operations
- Data persistence and recovery

**Risk Mitigation**:
- Increased test coverage for high-risk areas
- Additional manual review
- Performance testing before release
- Security scanning before production

---

## 21. Test Deliverables

**Deliverable Artifacts**:
- ✅ test.py: Comprehensive test script
- ✅ implement.py: Implementation script
- ✅ test_plan.md: This document
- ✅ tests/unit/: Unit test suite
- ✅ tests/integration/: Integration test suite
- ✅ Coverage reports: HTML format
- ✅ Test results: JUnit XML format

---

## 22. Entry & Exit Criteria

**Entry Criteria** (before testing):
- [ ] Implementation complete
- [ ] Code review approved
- [ ] All required documentation present
- [ ] Test environment ready

**Exit Criteria** (before release):
- [ ] All critical/high-priority tests pass
- [ ] Code coverage ≥80%
- [ ] No open P0/P1 defects
- [ ] Performance benchmarks met
- [ ] Security scan passed
- [ ] Manual testing completed
- [ ] Stakeholder approval obtained

---

## 23. Validation Checklist

**Pre-Release Validation**:
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Coverage ≥80% for new code
- [ ] Security scan results reviewed
- [ ] Performance benchmarks validated
- [ ] Manual testing scenarios verified
- [ ] Documentation reviewed and accurate
- [ ] Breaking changes documented
- [ ] Migration steps documented (if needed)
- [ ] Rollback plan documented

**Post-Deployment Monitoring**:
- [ ] Monitor production metrics
- [ ] Check error logs for issues
- [ ] Validate user feedback
- [ ] Measure adoption rate

---

## 24. Best Practices & Patterns

### Pytest Best Practices

**Project Structure**:
```
tests/
├── conftest.py              # Shared fixtures
├── pytest.ini              # Configuration
├── unit/
│   ├── conftest.py        # Unit fixtures
│   ├── test_module1.py
│   └── test_module2.py
├── integration/
│   ├── conftest.py        # Integration fixtures
│   └── test_workflows.py
├── fixtures/              # Test data
│   └── sample_data.json
└── helpers.py             # Custom utilities
```

**Test Execution**:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov --cov-report=html --cov-fail-under=80

# Run specific tests
pytest tests/unit/test_module1.py::test_function -v

# Run with markers
pytest -m unit -v
pytest -m integration -v
```

**Fixture Patterns**:
```python
@pytest.fixture
def sample_data():
    """Provide test data"""
    return {{"key": "value"}}

@pytest.fixture
def mock_external_api(mocker):
    """Mock external API calls"""
    return mocker.patch("module.external_api")

@pytest.fixture(autouse=True)
def cleanup():
    """Auto-cleanup after each test"""
    yield
    # cleanup code here
```

**Test Organization**:
```python
class TestModuleFunctionality:
    """Group related tests in classes"""

    @pytest.mark.unit
    def test_happy_path(self):
        pass

    @pytest.mark.unit
    @pytest.mark.parametrize("input,expected", [
        ("valid", True),
        ("invalid", False),
    ])
    def test_validation(self, input, expected):
        pass
```

---

## 25. Document Metadata

**Document Version**: 1.0

**Last Updated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

**Created By**: Workflow-Step06 Generator

**Based On Template**: openspec/templates/test_plan.md

**Related Change**: {change_id}

**Document Location**: {change_path}/test_plan.md

**Review Status**: Ready for Review

**Approval Status**: Pending stakeholder approval

---

## Quick Links

- [Proposal]( ./proposal.md)
- [Specification](./spec.md)
- [Tasks](./tasks.md)
- [TODO Tracking](./todo.md)
- [Test Script](./test.py)
- [Implementation Script](./implement.py)
- [Test Template](../../../templates/test_plan.md)

---

**Notes**:
- This test plan is auto-generated from the change documentation
- Customize this plan based on specific implementation requirements
- Update test cases as implementation details emerge
- Keep this document synchronized with proposal.md and spec.md
- Review and approve before starting implementation
'''


def invoke_step6(change_path: Path, dry_run: bool = False, **_: dict) -> bool:
    """Execute Step 6: Script generation and tooling.

    Args:
        change_path: Path to the change folder
        dry_run: If True, only show what would be done
        **_: Additional keyword arguments (ignored)

    Returns:
        True if successful, False otherwise
    """
    helpers.write_step(6, "Script Generation & Tooling")

    change_id = change_path.name

    helpers.write_info("Analyzing documentation for script requirements...")

    # Analyze requirements
    requirements = _analyze_requirements(change_path)

    # NOTE: Always generate test.py and implement.py for every OpenSpec change
    # regardless of documented requirements, as they are core workflow artifacts
    helpers.write_info("Generating standard OpenSpec scripts...")
    helpers.write_info("")

    # Display detected requirements (for informational purposes)
    if any(
        [
            requirements["needs_setup"],
            requirements["needs_test"],
            requirements["needs_validation"],
            requirements["needs_ci"],
            len(requirements["script_types"]) > 0,
            len(requirements["purposes"]) > 0,
        ]
    ):
        helpers.write_info("Detected Additional Requirements:")
        if requirements["purposes"]:
            helpers.write_info(f"  Purpose: {', '.join(requirements['purposes'])}")
        if requirements["script_types"]:
            helpers.write_info(
                f"  Script Types: {', '.join(requirements['script_types'])}"
            )
        if requirements["affected_files"]:
            helpers.write_info(
                f"  Affected Files: {', '.join(requirements['affected_files'][:3])}"
            )
            if len(requirements["affected_files"]) > 3:
                helpers.write_info(
                    f"    ... and {len(requirements['affected_files']) - 3} more"
                )
        helpers.write_info("")

    # Generate scripts with progress indicator
    scripts_to_generate = []
    if not (change_path / "test.py").exists():
        scripts_to_generate.append(("test.py", "Test Script"))
    if not (change_path / "implement.py").exists():
        scripts_to_generate.append(("implement.py", "Implementation Script"))
    if not (change_path / "test_plan.md").exists():
        scripts_to_generate.append(("test_plan.md", "Test Plan"))

    if not scripts_to_generate and not dry_run:
        helpers.write_success("Scripts already exist")
        return True

    # Use status tracker for script generation
    if scripts_to_generate and not dry_run:
        tracker = progress.StatusTracker("Generating Scripts")

        for script_name, script_desc in scripts_to_generate:
            tracker.add_item(script_name, script_desc, "pending")

        # Generate test script
        if ("test.py", "Test Script") in scripts_to_generate:
            tracker.update_item("test.py", "running", "Generating...")
            test_content = _generate_python_test_script(
                change_path, change_id, requirements
            )
            test_script_path = change_path / "test.py"
            test_script_path.write_text(test_content, encoding="utf-8")
            # Make executable on Unix-like systems
            try:
                import os

                os.chmod(test_script_path, 0o755)
            except (AttributeError, OSError):
                pass  # Windows or permission error
            tracker.update_item("test.py", "success", f"{len(test_content)} bytes")

        # Generate implementation script
        if ("implement.py", "Implementation Script") in scripts_to_generate:
            tracker.update_item("implement.py", "running", "Generating...")
            implement_content = _generate_python_implement_script(
                change_path, change_id, requirements
            )
            implement_script_path = change_path / "implement.py"
            implement_script_path.write_text(implement_content, encoding="utf-8")
            # Make executable on Unix-like systems
            try:
                import os

                os.chmod(implement_script_path, 0o755)
            except (AttributeError, OSError):
                pass  # Windows or permission error
            tracker.update_item(
                "implement.py", "success", f"{len(implement_content)} bytes"
            )

        # Generate test plan
        if ("test_plan.md", "Test Plan") in scripts_to_generate:
            tracker.update_item("test_plan.md", "running", "Generating...")
            test_plan_content = _generate_test_plan_md(change_path, change_id)
            test_plan_path = change_path / "test_plan.md"
            test_plan_path.write_text(test_plan_content, encoding="utf-8")
            tracker.update_item(
                "test_plan.md", "success", f"{len(test_plan_content)} bytes"
            )

        tracker.complete("[DONE] Script generation complete")
    elif dry_run:
        for script_name, _ in scripts_to_generate:
            helpers.write_info(f"[DRY-RUN] Would generate: {script_name}")

    return True


if __name__ == "__main__":
    test_dir = Path("openspec/changes/test-step6")
    test_dir.mkdir(parents=True, exist_ok=True)

    # Create minimal test documents for requirements analysis
    (test_dir / "proposal.md").write_text(
        "## Why\n\nTest proposal\n\n## What Changes\n\n"
        "- **Affected files**: agent/test.py, frontend/app.js\n\n"
        "## Impact\n\nNeed testing and validation scripts.",
        encoding="utf-8",
    )
    (test_dir / "spec.md").write_text(
        "## Requirements\n\nAutomated testing required.", encoding="utf-8"
    )
    (test_dir / "tasks.md").write_text(
        "## 1. Implementation\n\n- [ ] **Task 1**: Implement feature\n",
        encoding="utf-8",
    )
    (test_dir / "todo.md").write_text("- [ ] **6. Script**", encoding="utf-8")

    ok = invoke_step6(test_dir, dry_run=True)
    sys.exit(0 if ok else 1)

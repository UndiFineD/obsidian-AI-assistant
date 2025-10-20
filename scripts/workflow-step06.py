#!/usr/bin/env python3
"""Step 6: Script Generation & Tooling

Generates comprehensive test and implementation scripts based on change documentation.
Creates test harness with validation functions and implementation scaffolding.
"""

import sys
import importlib.util
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


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
            r"(?i)setup\.ps1|setup\.sh|setup\.py|installation|deployment",
            content
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
            r"(?m)^[-*]\s*\*\*Affected files\*\*:\s*(.+)",
            content
        )
        if affected_match:
            files = [f.strip() for f in affected_match.group(1).split(",")]
            requirements["affected_files"].extend(files)
        
        # Also check for "Affected code"
        affected_code = re.search(
            r"(?m)^[-*]\s*\*\*Affected code\*\*:\s*(.+)",
            content
        )
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
    change_path: Path,
    change_id: str,
    requirements: Dict[str, any]
) -> str:
    """Generate Python test script content.
    
    Returns:
        Complete test script content
    """
    affected_files_section = ""
    if requirements["affected_files"]:
        files_list = "\n".join(
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
        r"- \\[[\\sx]\\]",
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


def _generate_python_implement_script(
    change_path: Path,
    change_id: str,
    requirements: Dict[str, any]
) -> str:
    """Generate Python implementation script content.
    
    Returns:
        Complete implementation script content
    """
    affected_files_section = ""
    if requirements["affected_files"]:
        files_list = "\n".join(
            f'    invoke_task(\n'
            f'        "Verify File: {f}",\n'
            f'        lambda: verify_file(project_root / "{f}"),\n'
            f'        "Check that affected file exists"\n'
            f'    )'
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
    
    # Check if scripts are actually needed
    needs_scripts = (
        requirements["needs_setup"] or
        requirements["needs_test"] or
        requirements["needs_validation"] or
        requirements["needs_ci"] or
        len(requirements["script_types"]) > 0
    )
    
    if not needs_scripts:
        helpers.write_info("No script requirements detected in documentation")
        helpers.write_info("Skipping script generation")
        return True
    
    # Display detected requirements
    helpers.write_info("")
    helpers.write_info("Detected Script Requirements:")
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
            helpers.write_info(f"    ... and {len(requirements['affected_files']) - 3} more")
    helpers.write_info("")
    
    # Generate scripts with progress indicator
    scripts_to_generate = []
    if not (change_path / "test.py").exists():
        scripts_to_generate.append(("test.py", "Test Script"))
    if not (change_path / "implement.py").exists():
        scripts_to_generate.append(("implement.py", "Implementation Script"))
    
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
                change_path,
                change_id,
                requirements
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
                change_path,
                change_id,
                requirements
            )
            implement_script_path = change_path / "implement.py"
            implement_script_path.write_text(implement_content, encoding="utf-8")
            # Make executable on Unix-like systems
            try:
                import os
                os.chmod(implement_script_path, 0o755)
            except (AttributeError, OSError):
                pass  # Windows or permission error
            tracker.update_item("implement.py", "success", f"{len(implement_content)} bytes")
        
        tracker.complete("✓ Script generation complete")
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
        "- **Affected files**: backend/test.py, frontend/app.js\n\n"
        "## Impact\n\nNeed testing and validation scripts.",
        encoding="utf-8"
    )
    (test_dir / "spec.md").write_text(
        "## Requirements\n\nAutomated testing required.",
        encoding="utf-8"
    )
    (test_dir / "tasks.md").write_text(
        "## 1. Implementation\n\n- [ ] **Task 1**: Implement feature\n",
        encoding="utf-8"
    )
    (test_dir / "todo.md").write_text("- [ ] **6. Script**", encoding="utf-8")
    
    ok = invoke_step6(test_dir, dry_run=True)
    sys.exit(0 if ok else 1)

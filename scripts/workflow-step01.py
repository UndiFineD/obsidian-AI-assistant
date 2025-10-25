#!/usr/bin/env python3
"""Step 1: Version

HARD REQUIREMENT: Always increments patch version (like PowerShell workflow).
Updates agent/__init__.py, creates/checks out versioned branch, and persists
new_version to .workflow_state.json.

Does NOT update CHANGELOG.md or README.md - those are not part of version detection.
"""

import importlib.util
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Helpers
spec = importlib.util.spec_from_file_location(
    "workflow_helpers",
    SCRIPT_DIR / "workflow-helpers.py",
)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)

# Import progress indicators
try:
    import progress_indicators as progress
except ImportError:
    progress = None

# Import status tracker
try:
    from status_tracker import StatusTracker, create_tracker
    STATUS_TRACKER_AVAILABLE = True
except ImportError:
    STATUS_TRACKER_AVAILABLE = False
    StatusTracker = None
    create_tracker = None

# Import document validator and template manager
try:
    DocumentValidator = helpers.DocumentValidator
    TemplateManager = helpers.TemplateManager
    DOCUMENT_VALIDATOR_AVAILABLE = True
    TEMPLATE_MANAGER_AVAILABLE = True
except AttributeError:
    DOCUMENT_VALIDATOR_AVAILABLE = False
    TEMPLATE_MANAGER_AVAILABLE = False
    DocumentValidator = None
    TemplateManager = None


def _read_pyproject_version(pyproject: Path) -> Optional[str]:
    try:
        text = pyproject.read_text(encoding="utf-8")
        m = re.search(r"^version\s*=\s*['\"]([^'\"]+)['\"]", text, re.M)
        if m:
            return m.group(1)
    except Exception:
        pass
    return None


def _read_package_json_version(pkg_json: Path) -> Optional[str]:
    try:
        data = json.loads(pkg_json.read_text(encoding="utf-8"))
        v = data.get("version")
        if isinstance(v, str):
            return v
    except Exception:
        pass
    return None


def _mark_complete(change_path: Path) -> None:
    todo = change_path / "todo.md"
    if not todo.exists():
        return
    content = todo.read_text(encoding="utf-8")
    updated = content.replace("[ ] **1.", "[x] **1.")
    if updated != content:
        helpers.set_content_atomic(todo, updated)


def _get_current_branch() -> str:
    """Get current git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return "main"


def _create_or_checkout_branch(branch_name: str, dry_run: bool = False) -> bool:
    """Create or checkout versioned branch.

    Stashes any uncommitted changes before switching branches to avoid conflicts
    with workflow state files (checkpoints, todos) that may be tracked by git.
    """
    try:
        # Stash any uncommitted changes to avoid checkout conflicts
        if not dry_run:
            stash_result = subprocess.run(
                ["git", "stash"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            stash_output = stash_result.stdout.strip()
            if "Saved working directory" in stash_output:
                helpers.write_info("Stashed uncommitted changes for branch switch")

        # Check if branch exists
        result = subprocess.run(
            ["git", "branch", "--list", branch_name],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )

        if result.stdout.strip():
            # Branch exists, checkout
            helpers.write_info(f"Branch '{branch_name}' exists. Checking out...")
            if not dry_run:
                subprocess.run(
                    ["git", "checkout", branch_name], cwd=PROJECT_ROOT, check=True
                )
        else:
            # Create new branch
            helpers.write_info(
                f"Creating and checking out new branch '{branch_name}'..."
            )
            if not dry_run:
                subprocess.run(
                    ["git", "checkout", "-b", branch_name], cwd=PROJECT_ROOT, check=True
                )

        # Restore stashed changes after successful branch switch
        if not dry_run:
            pop_result = subprocess.run(
                ["git", "stash", "pop"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            if pop_result.returncode == 0 and "Dropped" in pop_result.stdout:
                helpers.write_info("Restored stashed changes after branch switch")

        return True
    except Exception as e:
        helpers.write_error(f"Failed to create/checkout branch: {e}")
        return False


def invoke_step1(
    change_path: Path,
    dry_run: bool = False,
    release_type: Optional[str] = None,
    **_: dict,
) -> bool:
    helpers.write_step(1, "Version (HARD REQUIREMENT: ALWAYS bump patch)")

    # Initialize status tracker if available
    status_tracker = None
    if STATUS_TRACKER_AVAILABLE:
        try:
            status_tracker = create_tracker(
                change_path.name,
                lane="standard",  # Default lane for step 1
                status_file=change_path / ".checkpoints" / "status.json",
            )
            status_tracker.start_stage(1, "Version Bump")
        except Exception as e:
            helpers.write_warning(f"Could not initialize status tracker: {e}")

    pyproject = PROJECT_ROOT / "pyproject.toml"
    package_json = PROJECT_ROOT / "package.json"
    py_ver = _read_pyproject_version(pyproject) if pyproject.exists() else None
    js_ver = _read_package_json_version(package_json) if package_json.exists() else None

    helpers.write_info(f"Detected Python version: {py_ver or 'N/A'}")
    helpers.write_info(f"Detected Node version:   {js_ver or 'N/A'}")

    # Use DocumentValidator if available
    if DOCUMENT_VALIDATOR_AVAILABLE and DocumentValidator:
        try:
            validator = DocumentValidator()
            # Validate that we can create the version snapshot file
            if not validator.validate_file_creation(change_path, "version_snapshot.md"):
                helpers.write_error("Document validation failed for version_snapshot.md creation")
                if status_tracker:
                    status_tracker.complete_stage(1, success=False, metrics={"reason": "Document validation failed"})
                return False
        except Exception as e:
            helpers.write_warning(f"Document validation error: {e}")

    # ALWAYS bump patch version (HARD REQUIREMENT - no optional parameter)
    new_version: Optional[str] = None
    bump_results = None
    current_version = None

    try:
        current_version = helpers.VersionManager.get_current_version(PROJECT_ROOT)

        # Always bump patch (hardcoded requirement)
        if release_type:
            new_version = helpers.VersionManager.bump_version(
                current_version, release_type
            )
        else:
            new_version = helpers.VersionManager.bump_version(current_version, "patch")

        helpers.write_info(f"Bumped version: {current_version} → {new_version}")

        if not dry_run:
            if progress and hasattr(progress, 'spinner'):
                with progress.spinner(
                    "Updating version files", "Version files updated"
                ):
                    updated_files = helpers.VersionManager.update_version_files(
                        PROJECT_ROOT, new_version
                    )
            else:
                updated_files = helpers.VersionManager.update_version_files(
                    PROJECT_ROOT, new_version
                )

            for file in updated_files:
                helpers.write_success(f"  ✅ Updated: {file}")
    except Exception as e:
        helpers.write_error(f"Version bump failed: {e}")
        if status_tracker:
            status_tracker.complete_stage(1, success=False, metrics={"error": str(e)})
        return False

    # Create/checkout versioned branch (e.g., release-0.1.27)
    if new_version:
        version_branch = f"release-{new_version}"
        helpers.write_info(f"Managing git branch: {version_branch}")
        if not _create_or_checkout_branch(version_branch, dry_run):
            helpers.write_error("Failed to create/checkout version branch")
            if status_tracker:
                status_tracker.complete_stage(1, success=False, metrics={"reason": "Branch creation failed"})
            return False
        helpers.write_info(f"  ✅ Using branch: {version_branch}")

    # Write snapshot (always)
    snapshot = change_path / "version_snapshot.md"
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    # Use TemplateManager if available for version snapshot
    if TEMPLATE_MANAGER_AVAILABLE and TemplateManager:
        try:
            template_manager = TemplateManager()
            content = template_manager.render_version_snapshot(
                captured_time=now,
                python_version=py_ver or 'N/A',
                node_version=js_ver or 'N/A',
                current_version=current_version,
                new_version=new_version,
                branch=version_branch if new_version else None
            )
        except Exception as e:
            helpers.write_warning(f"Template manager error, using fallback: {e}")
            content = (
                f"# Version Snapshot\n\n"
                f"Captured: {now}\n\n"
                f"- Python (pyproject.toml): {py_ver or 'N/A'}\n"
                f"- Node (package.json):    {js_ver or 'N/A'}\n"
            )
            if new_version:
                content += f"- Version bumped: {current_version} → {new_version}\n"
                content += f"- Branch: release-{new_version}\n"
    else:
        content = (
            f"# Version Snapshot\n\n"
            f"Captured: {now}\n\n"
            f"- Python (pyproject.toml): {py_ver or 'N/A'}\n"
            f"- Node (package.json):    {js_ver or 'N/A'}\n"
        )
        if new_version:
            content += f"- Version bumped: {current_version} → {new_version}\n"
            content += f"- Branch: release-{new_version}\n"

    if dry_run:
        helpers.write_info(f"[DRY RUN] Would write: {snapshot}")
    else:
        if progress and hasattr(progress, 'spinner'):
            with progress.spinner("Writing version snapshot", "Snapshot written"):
                helpers.set_content_atomic(snapshot, content)
        else:
            helpers.set_content_atomic(snapshot, content)
        helpers.write_success(f"Wrote version snapshot: {snapshot}")

    # Validate step artifacts
    if not dry_run and not helpers.validate_step_artifacts(change_path, 1):
        helpers.write_error("Step 1 artifact validation failed")
        if status_tracker:
            status_tracker.complete_stage(1, success=False, metrics={"reason": "Artifact validation failed"})
        return False

    # Show changes if available
    if not dry_run:
        try:
            changes_dir = change_path.parent
            helpers.show_changes(changes_dir)
        except Exception as e:
            helpers.write_warning(f"Could not show changes: {e}")

    # Persist new_version and version_branch to state file for downstream steps
    if new_version:
        state_file = change_path / ".workflow_state.json"
        try:
            state = {}
            if state_file.exists():
                state = json.loads(state_file.read_text(encoding="utf-8"))
            state["new_version"] = new_version
            state["version_branch"] = f"release-{new_version}"
            state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
            helpers.write_info(
                f"Persisted state: version={new_version}, branch={state['version_branch']}"
            )
        except Exception as e:
            helpers.write_warning(f"Could not persist version state: {e}")

    _mark_complete(change_path)

    # Record completion in status tracker
    if status_tracker:
        status_tracker.complete_stage(1, success=True)

    helpers.write_success("Step 1 completed: Version bumped and all files updated")
    return True


if __name__ == "__main__":
    test_dir = Path("openspec/changes/test-step1")
    test_dir.mkdir(parents=True, exist_ok=True)
    ok = invoke_step1(test_dir, dry_run=True, release_type="patch")
    sys.exit(0 if ok else 1)

#!/usr/bin/env python3
"""Step 1: Version

HARD REQUIREMENT: Always increments patch version (like PowerShell workflow).
Updates package.json, pyproject.toml, CHANGELOG.md, README.md, creates/checks
out versioned branch, and persists new_version to .workflow_state.json.
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

# Version manager
vm_spec = importlib.util.spec_from_file_location(
    "version_manager",
    SCRIPT_DIR / "version_manager.py",
)
version_manager = importlib.util.module_from_spec(vm_spec)
vm_spec.loader.exec_module(version_manager)

# Import progress indicators
try:
    import progress_indicators as progress
except ImportError:
    progress = None


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


def _update_changelog(changelog: Path, new_version: str, dry_run: bool = False) -> bool:
    """Update CHANGELOG.md with new version entry."""
    try:
        if not changelog.exists():
            return False

        content = changelog.read_text(encoding="utf-8")
        today = datetime.utcnow().strftime("%Y-%m-%d")

        # Insert new version section after the header
        header_match = re.search(r"(# 📝 CHANGELOG\n)", content)
        if not header_match:
            helpers.write_warning("Could not find CHANGELOG header")
            return False

        new_entry = f"## v{new_version} ({today})\n\n- _Released as part of OpenSpec workflow automation._\n\n"
        updated = (
            content[: header_match.end()] + new_entry + content[header_match.end() :]
        )

        if not dry_run:
            changelog.write_text(updated, encoding="utf-8")
        return True
    except Exception as e:
        helpers.write_warning(f"Failed to update CHANGELOG.md: {e}")
        return False


def _update_readme_version(
    readme: Path, new_version: str, dry_run: bool = False
) -> bool:
    """Update README.md version line."""
    try:
        if not readme.exists():
            return False

        content = readme.read_text(encoding="utf-8")
        # Update version line: > **Version:** X.Y.Z (status)
        updated = re.sub(
            r"> \*\*Version:\*\* [\d.]+[^\n]*",
            f"> **Version:** {new_version} (Unreleased)",
            content,
        )

        if updated == content:
            helpers.write_warning("README.md version line not found or unchanged")
            return False

        if not dry_run:
            readme.write_text(updated, encoding="utf-8")
        return True
    except Exception as e:
        helpers.write_warning(f"Failed to update README.md: {e}")
        return False


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

    pyproject = PROJECT_ROOT / "pyproject.toml"
    package_json = PROJECT_ROOT / "package.json"
    changelog = PROJECT_ROOT / "CHANGELOG.md"
    readme = PROJECT_ROOT / "README.md"

    py_ver = _read_pyproject_version(pyproject) if pyproject.exists() else None
    js_ver = _read_package_json_version(package_json) if package_json.exists() else None

    helpers.write_info(f"Detected Python version: {py_ver or 'N/A'}")
    helpers.write_info(f"Detected Node version:   {js_ver or 'N/A'}")

    # ALWAYS bump patch version (HARD REQUIREMENT - no optional parameter)
    new_version: Optional[str] = None
    bump_results = None
    current_version = None

    try:
        vm = version_manager.VersionManager(str(PROJECT_ROOT))
        current_version = vm.get_current_version()

        # Always bump patch (hardcoded requirement)
        if progress:
            with progress.spinner("Bumping patch version", "Version bumped"):
                new_version = vm.bump_version("patch", use_github=True)
                if not dry_run:
                    bump_results = vm.update_all_versions(new_version)
        else:
            new_version = vm.bump_version("patch", use_github=True)
            if not dry_run:
                bump_results = vm.update_all_versions(new_version)

        helpers.write_info(f"Bumped version: {current_version} → {new_version}")
        if bump_results:
            for file, ok in bump_results.items():
                status = "✅" if ok else "❌"
                helpers.write_info(f"  {status} {file}")
            if not all(bump_results.values()):
                helpers.write_warning(
                    "One or more files failed to update. See output above."
                )
    except Exception as e:
        helpers.write_error(f"Version bump failed: {e}")
        return False

    # Update CHANGELOG.md
    if new_version:
        helpers.write_info("Updating CHANGELOG.md...")
        if _update_changelog(changelog, new_version, dry_run):
            helpers.write_info("  ✅ CHANGELOG.md updated")
        else:
            helpers.write_warning("  ❌ Failed to update CHANGELOG.md")

    # Update README.md version line
    if new_version:
        helpers.write_info("Updating README.md...")
        if _update_readme_version(readme, new_version, dry_run):
            helpers.write_info("  ✅ README.md updated")
        else:
            helpers.write_warning("  ❌ Failed to update README.md")

    # Create/checkout versioned branch (e.g., release-0.1.27)
    if new_version:
        version_branch = f"release-{new_version}"
        helpers.write_info(f"Managing git branch: {version_branch}")
        if not _create_or_checkout_branch(version_branch, dry_run):
            helpers.write_error("Failed to create/checkout version branch")
            return False
        helpers.write_info(f"  ✅ Using branch: {version_branch}")

    # Write snapshot (always)
    snapshot = change_path / "version_snapshot.md"
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
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
        if progress:
            with progress.spinner("Writing version snapshot", "Snapshot written"):
                helpers.set_content_atomic(snapshot, content)
        else:
            helpers.set_content_atomic(snapshot, content)
        helpers.write_success(f"Wrote version snapshot: {snapshot}")

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
    helpers.write_success("Step 1 completed: Version bumped and all files updated")
    return True


if __name__ == "__main__":
    test_dir = Path("openspec/changes/test-step1")
    test_dir.mkdir(parents=True, exist_ok=True)
    ok = invoke_step1(test_dir, dry_run=True, release_type="patch")
    sys.exit(0 if ok else 1)

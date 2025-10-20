#!/usr/bin/env python3
"""Step 1: Version

Captures current repository versions (pyproject.toml, package.json) into
version_snapshot.md under the change directory. Optionally bumps versions
using VersionManager when release_type is provided (patch|minor|major).
"""

import importlib.util
import json
import re
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
    updated = content.replace("[ ] **1. Version", "[x] **1. Version")
    if updated != content:
        helpers.set_content_atomic(todo, updated)


def invoke_step1(
    change_path: Path,
    dry_run: bool = False,
    release_type: Optional[str] = None,
    **_: dict,
) -> bool:
    helpers.write_step(1, "Version")

    pyproject = PROJECT_ROOT / "pyproject.toml"
    package_json = PROJECT_ROOT / "package.json"

    py_ver = _read_pyproject_version(pyproject) if pyproject.exists() else None
    js_ver = _read_package_json_version(package_json) if package_json.exists() else None

    helpers.write_info(f"Detected Python version: {py_ver or 'N/A'}")
    helpers.write_info(f"Detected Node version:   {js_ver or 'N/A'}")

    # Optional version bump using VersionManager
    new_version: Optional[str] = None
    bump_results = None
    if release_type:
        rt = release_type.lower()
        if rt not in {"patch", "minor", "major"}:
            helpers.write_warning(
                f"Ignoring invalid release_type '{release_type}'. Expected patch|minor|major."
            )
        else:
            if progress:
                with progress.spinner(f"Bumping version ({rt})", "Version bumped"):
                    vm = version_manager.VersionManager(str(PROJECT_ROOT))
                    current = vm.get_current_version()
                    new_version = vm.bump_version(rt)
                    if not dry_run:
                        bump_results = vm.update_all_versions(new_version)
            else:
                vm = version_manager.VersionManager(str(PROJECT_ROOT))
                current = vm.get_current_version()
                new_version = vm.bump_version(rt)

            try:
                if dry_run:
                    helpers.write_info(
                        f"[DRY RUN] Would bump version: {current} → {new_version}"
                    )
                else:
                    helpers.write_info(f"Bumped version: {current} → {new_version}")
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
        content += f"- New version (after bump): {new_version}\n"

    if dry_run:
        helpers.write_info(f"[DRY RUN] Would write: {snapshot}")
    else:
        if progress:
            with progress.spinner("Writing version snapshot", "Snapshot written"):
                helpers.set_content_atomic(snapshot, content)
        else:
            helpers.set_content_atomic(snapshot, content)
            helpers.write_success(f"Wrote version snapshot: {snapshot}")

    # Persist new_version to state file for downstream steps (especially Step 12)
    if new_version:
        state_file = change_path / ".workflow_state.json"
        try:
            state = {}
            if state_file.exists():
                state = json.loads(state_file.read_text(encoding="utf-8"))
            state["new_version"] = new_version
            state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
            helpers.write_info(f"Persisted new_version to state: {new_version}")
        except Exception as e:
            helpers.write_warning(f"Could not persist version state: {e}")

    _mark_complete(change_path)
    helpers.write_success("Step 1 completed")
    return True


if __name__ == "__main__":
    test_dir = Path("openspec/changes/test-step1")
    test_dir.mkdir(parents=True, exist_ok=True)
    ok = invoke_step1(test_dir, dry_run=True, release_type="patch")
    sys.exit(0 if ok else 1)

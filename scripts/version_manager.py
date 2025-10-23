#!/usr/bin/env python3
"""
Version Management Script for Obsidian AI Agent
Handles version bumping, validation, and synchronization across all project files.
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional


class VersionManager:
    """Manages version information across multiple project files."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        # Only Python files maintained by this workflow (not Node.js or Obsidian plugin)
        self.version_files = [
            "agent/__init__.py",
        ]

    def get_current_version(self) -> str:
        """Get current version from agent/__init__.py (primary Python source).

        Note: This method reads the Python package version only.
        Node.js (package.json) and Obsidian plugin (manifest.json) versions
        are no longer maintained by this workflow.
        """
        init_path = self.project_root / "agent/__init__.py"
        if not init_path.exists():
            raise FileNotFoundError("agent/__init__.py not found")

        try:
            with open(init_path, "r") as f:
                content = f.read()
            match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
            raise ValueError("__version__ not found in agent/__init__.py")
        except Exception as e:
            print(f"Error reading version from agent/__init__.py: {e}")
            raise

    def get_github_version(self, branch: Optional[str] = None) -> Optional[str]:
        """Fetch current version from GitHub branch agent/__init__.py.

        Args:
            branch: Git branch to fetch from. If None, uses current branch.

        Returns:
            Version string from GitHub, or None if unable to fetch.
        """
        try:
            # Determine which branch to use
            if not branch:
                result = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    branch = result.stdout.strip()
                    # If we're on a feature branch, try to get from origin/main as fallback
                    if branch == "HEAD" or not branch:
                        branch = "origin/main"
                else:
                    branch = "origin/main"

            # Fetch from remote if not already prefixed
            if not branch.startswith("origin/"):
                branch = f"origin/{branch}"

            result = subprocess.run(
                ["git", "show", f"{branch}:agent/__init__.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                match = re.search(
                    r'__version__\s*=\s*["\']([^"\']+)["\']', result.stdout
                )
                if match:
                    return match.group(1)
            else:
                # Try main as fallback
                if branch != "origin/main":
                    result = subprocess.run(
                        ["git", "show", "origin/main:agent/__init__.py"],
                        cwd=self.project_root,
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    if result.returncode == 0:
                        match = re.search(
                            r'__version__\s*=\s*["\']([^"\']+)["\']', result.stdout
                        )
                        if match:
                            return match.group(1)

            return None
        except Exception as e:
            print(f"Warning: Could not fetch GitHub version: {e}", file=sys.stderr)
            return None

    def get_latest_version(self, use_github: bool = True) -> str:
        """Get the latest version from GitHub (if available) or local.

        Args:
            use_github: If True, try GitHub first, fall back to local.

        Returns:
            Latest version string.
        """
        if use_github:
            github_version = self.get_github_version()
            if github_version:
                return github_version

        # Fall back to local version
        return self.get_current_version()

    def validate_version(self, version: str) -> bool:
        """Validate semantic version format."""
        pattern = r"^\d+\.\d+\.\d+(-[\w\.-]+)?(\+[\w\.-]+)?$"
        return bool(re.match(pattern, version))

    def bump_version(self, release_type: str, use_github: bool = True) -> str:
        """Bump version based on release type (patch, minor, major).

        Args:
            release_type: Type of bump (patch, minor, major)
            use_github: If True, bump from GitHub version; else from local

        Returns:
            New version string
        """
        # Get the latest version (from GitHub if available)
        current = self.get_latest_version(use_github=use_github)

        # Parse current version
        version_parts = current.split(".")
        if len(version_parts) < 3:
            raise ValueError(f"Invalid version format: {current}")

        major, minor, patch = map(int, version_parts[:3])

        # Bump based on type
        if release_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif release_type == "minor":
            minor += 1
            patch = 0
        elif release_type == "patch":
            patch += 1
        else:
            raise ValueError(f"Invalid release type: {release_type}")

        new_version = f"{major}.{minor}.{patch}"

        if not self.validate_version(new_version):
            raise ValueError(f"Generated invalid version: {new_version}")

        return new_version

    def update_package_json(self, version: str) -> bool:
        """Update version in package.json."""
        package_path = self.project_root / "package.json"
        if not package_path.exists():
            return False

        try:
            with open(package_path, "r") as f:
                data = json.load(f)

            data["version"] = version

            with open(package_path, "w") as f:
                json.dump(data, f, indent=4)

            return True
        except Exception as e:
            print(f"Error updating package.json: {e}")
            return False

    def update_manifest_json(self, version: str) -> bool:
        """Update version in Obsidian plugin manifest."""
        manifest_path = (
            self.project_root / ".obsidian/plugins/obsidian-ai-agent/manifest.json"
        )
        if not manifest_path.exists():
            return False

        try:
            with open(manifest_path, "r") as f:
                data = json.load(f)

            data["version"] = version

            with open(manifest_path, "w") as f:
                json.dump(data, f, indent=4)

            return True
        except Exception as e:
            print(f"Error updating manifest.json: {e}")
            return False

    def update_python_init(self, version: str) -> bool:
        """Update version in Python __init__.py file."""
        init_path = self.project_root / "agent/__init__.py"
        if not init_path.exists():
            return False

        try:
            with open(init_path, "r") as f:
                content = f.read()

            # Update or add __version__ variable
            version_pattern = r'__version__\s*=\s*["\'].*?["\']'
            new_version_line = f'__version__ = "{version}"'

            if re.search(version_pattern, content):
                content = re.sub(version_pattern, new_version_line, content)
            else:
                # Add version line at the top
                content = f"{new_version_line}\n{content}"

            with open(init_path, "w") as f:
                f.write(content)

            return True
        except Exception as e:
            print(f"Error updating __init__.py: {e}")
            return False

    def update_setup_py(self, version: str) -> bool:
        """Update version in setup.py if it exists."""
        setup_path = self.project_root / "setup.py"
        if not setup_path.exists():
            return False

        try:
            with open(setup_path, "r") as f:
                content = f.read()

            # Update version in setup() call
            version_pattern = r'version\s*=\s*["\'].*?["\']'
            new_version_line = f'version="{version}"'

            content = re.sub(version_pattern, new_version_line, content)

            with open(setup_path, "w") as f:
                f.write(content)

            return True
        except Exception as e:
            print(f"Error updating setup.py: {e}")
            return False

    def update_all_versions(self, version: str) -> Dict[str, bool]:
        """Update version in all Python project files.

        Only updates agent/__init__.py as other files (package.json, manifest.json, setup.py)
        are not maintained by this workflow.
        """
        results = {}

        results["agent/__init__.py"] = self.update_python_init(version)

        return results

    def check_version_consistency(self) -> Dict[str, str]:
        """Check version consistency for Python project files.

        Only checks agent/__init__.py as package.json, manifest.json, and setup.py
        are not maintained by this workflow.
        """
        versions = {}

        # Check __init__.py (only file maintained by this workflow)
        try:
            with open(self.project_root / "agent/__init__.py", "r") as f:
                content = f.read()
                match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
                versions["agent/__init__.py"] = match.group(1) if match else "NOT_FOUND"
        except:
            versions["agent/__init__.py"] = "ERROR"

        return versions


def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("Usage: python version_manager.py <command> [args]")
        print("\nCommands:")
        print("  current                     - Show current version")
        print("  check                       - Check version consistency")
        print("  bump <patch|minor|major>    - Bump version")
        print("  set <version>               - Set specific version")
        print("  validate <version>          - Validate version format")
        return

    vm = VersionManager()
    command = sys.argv[1].lower()

    if command == "current":
        try:
            version = vm.get_current_version()
            print(f"Current version: {version}")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif command == "check":
        versions = vm.check_version_consistency()
        print("Version consistency check:")
        for file, version in versions.items():
            status = "✅" if version not in ["ERROR", "NOT_FOUND"] else "❌"
            print(f"  {status} {file}: {version}")

        # Check if all versions are the same
        valid_versions = [
            v for v in versions.values() if v not in ["ERROR", "NOT_FOUND"]
        ]
        if valid_versions and len(set(valid_versions)) == 1:
            print(f"\n✅ All versions are consistent: {valid_versions[0]}")
        else:
            print("\n❌ Version inconsistency detected!")
            sys.exit(1)

    elif command == "bump":
        if len(sys.argv) < 3:
            print("Error: Please specify release type (patch, minor, major)")
            sys.exit(1)

        release_type = sys.argv[2].lower()
        if release_type not in ["patch", "minor", "major"]:
            print("Error: Release type must be patch, minor, or major")
            sys.exit(1)

        try:
            current = vm.get_current_version()
            new_version = vm.bump_version(release_type)
            print(f"Bumping version: {current} → {new_version}")

            results = vm.update_all_versions(new_version)

            print("\nUpdate results:")
            for file, success in results.items():
                status = "✅" if success else "❌"
                print(f"  {status} {file}")

            if all(results.values()):
                print(f"\n🎉 Successfully bumped version to {new_version}")
            else:
                print("\n⚠️  Some files failed to update")
                sys.exit(1)

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif command == "set":
        if len(sys.argv) < 3:
            print("Error: Please specify version")
            sys.exit(1)

        version = sys.argv[2]

        if not vm.validate_version(version):
            print(f"Error: Invalid version format: {version}")
            sys.exit(1)

        try:
            results = vm.update_all_versions(version)

            print(f"Setting version to: {version}")
            print("\nUpdate results:")
            for file, success in results.items():
                status = "✅" if success else "❌"
                print(f"  {status} {file}")

            if all(results.values()):
                print(f"\n🎉 Successfully set version to {version}")
            else:
                print("\n⚠️  Some files failed to update")
                sys.exit(1)

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif command == "validate":
        if len(sys.argv) < 3:
            print("Error: Please specify version to validate")
            sys.exit(1)

        version = sys.argv[2]
        if vm.validate_version(version):
            print(f"✅ Version {version} is valid")
        else:
            print(f"❌ Version {version} is invalid")
            sys.exit(1)

    else:
        print(f"Error: Unknown command '{command}'")
        sys.exit(1)


if __name__ == "__main__":
    main()

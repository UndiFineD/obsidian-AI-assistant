#!/usr/bin/env python3
"""
Version Management Script for Obsidian AI Assistant
Handles version bumping, validation, and synchronization across all project files.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class VersionManager:
    """Manages version information across multiple project files."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.version_files = [
            "package.json",
            ".obsidian/plugins/obsidian-ai-assistant/manifest.json",
            "backend/__init__.py",
            "setup.py",
        ]
    
    def get_current_version(self) -> str:
        """Get current version from package.json (primary source)."""
        package_path = self.project_root / "package.json"
        if not package_path.exists():
            raise FileNotFoundError("package.json not found")
        
        with open(package_path, 'r') as f:
            package_data = json.load(f)
        
        return package_data.get("version", "0.1.0")
    
    def validate_version(self, version: str) -> bool:
        """Validate semantic version format."""
        pattern = r'^\d+\.\d+\.\d+(-[\w\.-]+)?(\+[\w\.-]+)?$'
        return bool(re.match(pattern, version))
    
    def bump_version(self, release_type: str) -> str:
        """Bump version based on release type (patch, minor, major)."""
        current = self.get_current_version()
        
        # Parse current version
        version_parts = current.split('.')
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
            with open(package_path, 'r') as f:
                data = json.load(f)
            
            data["version"] = version
            
            with open(package_path, 'w') as f:
                json.dump(data, f, indent=4)
            
            return True
        except Exception as e:
            print(f"Error updating package.json: {e}")
            return False
    
    def update_manifest_json(self, version: str) -> bool:
        """Update version in Obsidian plugin manifest."""
        manifest_path = self.project_root / ".obsidian/plugins/obsidian-ai-assistant/manifest.json"
        if not manifest_path.exists():
            return False
        
        try:
            with open(manifest_path, 'r') as f:
                data = json.load(f)
            
            data["version"] = version
            
            with open(manifest_path, 'w') as f:
                json.dump(data, f, indent=4)
            
            return True
        except Exception as e:
            print(f"Error updating manifest.json: {e}")
            return False
    
    def update_python_init(self, version: str) -> bool:
        """Update version in Python __init__.py file."""
        init_path = self.project_root / "backend/__init__.py"
        if not init_path.exists():
            return False
        
        try:
            with open(init_path, 'r') as f:
                content = f.read()
            
            # Update or add __version__ variable
            version_pattern = r'__version__\s*=\s*["\'].*?["\']'
            new_version_line = f'__version__ = "{version}"'
            
            if re.search(version_pattern, content):
                content = re.sub(version_pattern, new_version_line, content)
            else:
                # Add version line at the top
                content = f'{new_version_line}\n{content}'
            
            with open(init_path, 'w') as f:
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
            with open(setup_path, 'r') as f:
                content = f.read()
            
            # Update version in setup() call
            version_pattern = r'version\s*=\s*["\'].*?["\']'
            new_version_line = f'version="{version}"'
            
            content = re.sub(version_pattern, new_version_line, content)
            
            with open(setup_path, 'w') as f:
                f.write(content)
            
            return True
        except Exception as e:
            print(f"Error updating setup.py: {e}")
            return False
    
    def update_all_versions(self, version: str) -> Dict[str, bool]:
        """Update version in all project files."""
        results = {}
        
        results["package.json"] = self.update_package_json(version)
        results["manifest.json"] = self.update_manifest_json(version)
        results["backend/__init__.py"] = self.update_python_init(version)
        results["setup.py"] = self.update_setup_py(version)
        
        return results
    
    def check_version_consistency(self) -> Dict[str, str]:
        """Check version consistency across all files."""
        versions = {}
        
        # Check package.json
        try:
            with open(self.project_root / "package.json", 'r') as f:
                data = json.load(f)
                versions["package.json"] = data.get("version", "NOT_FOUND")
        except:
            versions["package.json"] = "ERROR"
        
        # Check manifest.json
        try:
            manifest_path = self.project_root / ".obsidian/plugins/obsidian-ai-assistant/manifest.json"
            with open(manifest_path, 'r') as f:
                data = json.load(f)
                versions["manifest.json"] = data.get("version", "NOT_FOUND")
        except:
            versions["manifest.json"] = "ERROR"
        
        # Check __init__.py
        try:
            with open(self.project_root / "backend/__init__.py", 'r') as f:
                content = f.read()
                match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
                versions["backend/__init__.py"] = match.group(1) if match else "NOT_FOUND"
        except:
            versions["backend/__init__.py"] = "ERROR"
        
        # Check setup.py
        try:
            with open(self.project_root / "setup.py", 'r') as f:
                content = f.read()
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                versions["setup.py"] = match.group(1) if match else "NOT_FOUND"
        except:
            versions["setup.py"] = "ERROR"
        
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
        valid_versions = [v for v in versions.values() if v not in ["ERROR", "NOT_FOUND"]]
        if valid_versions and len(set(valid_versions)) == 1:
            print(f"\n✅ All versions are consistent: {valid_versions[0]}")
        else:
            print(f"\n❌ Version inconsistency detected!")
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
                print(f"\n⚠️  Some files failed to update")
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
                print(f"\n⚠️  Some files failed to update")
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
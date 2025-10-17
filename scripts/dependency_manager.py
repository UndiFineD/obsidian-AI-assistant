#!/usr/bin/env python3
"""
Comprehensive Dependency Management System for Obsidian AI Assistant

This script provides comprehensive dependency management capabilities including:
- Requirements validation and conflict detection
- Security vulnerability scanning
- Version constraint analysis
- Dependency tree visualization
- Update recommendations
- License compliance checking
"""

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union
import argparse
import tempfile
import pkg_resources
from packaging import version, specifiers
import requests
import time


@dataclass
class DependencyInfo:
    """Information about a single dependency."""
    name: str
    version: Optional[str] = None
    installed_version: Optional[str] = None
    constraint: Optional[str] = None
    source_file: Optional[str] = None
    is_dev: bool = False
    vulnerabilities: List[Dict] = None
    license: Optional[str] = None
    homepage: Optional[str] = None
    description: Optional[str] = None
    
    def __post_init__(self):
        if self.vulnerabilities is None:
            self.vulnerabilities = []


@dataclass
class ConflictInfo:
    """Information about a dependency conflict."""
    package: str
    required_versions: List[str]
    source_files: List[str]
    resolution: Optional[str] = None


class DependencyManager:
    """Comprehensive dependency management system."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the dependency manager."""
        self.project_root = project_root or Path.cwd()
        self.requirements_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "requirements-test.txt",
            "requirements-prod.txt"
        ]
        self.dependencies: Dict[str, DependencyInfo] = {}
        self.conflicts: List[ConflictInfo] = []
        self.vulnerabilities: List[Dict] = []
        
    def discover_requirements_files(self) -> List[Path]:
        """Discover all requirements files in the project."""
        found_files = []
        for req_file in self.requirements_files:
            file_path = self.project_root / req_file
            if file_path.exists():
                found_files.append(file_path)
        return found_files
    
    def parse_requirements_file(self, file_path: Path) -> List[DependencyInfo]:
        """Parse a requirements file and extract dependency information."""
        dependencies = []
        is_dev = "dev" in file_path.name.lower() or "test" in file_path.name.lower()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                    
                # Parse dependency specification
                dep_info = self._parse_dependency_line(line, file_path, is_dev)
                if dep_info:
                    dependencies.append(dep_info)
                    
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            
        return dependencies
    
    def _parse_dependency_line(self, line: str, source_file: Path, is_dev: bool) -> Optional[DependencyInfo]:
        """Parse a single dependency line."""
        # Remove inline comments
        line = line.split('#')[0].strip()
        if not line:
            return None
            
        # Handle various dependency formats
        # Simple format: package>=1.0.0
        match = re.match(r'^([a-zA-Z0-9_-]+[a-zA-Z0-9_.-]*)(.*?)$', line)
        if not match:
            return None
            
        package_name = match.group(1).lower()
        constraint_part = match.group(2).strip()
        
        # Extract version constraint
        constraint = constraint_part if constraint_part else None
        
        return DependencyInfo(
            name=package_name,
            constraint=constraint,
            source_file=str(source_file),
            is_dev=is_dev
        )
    
    def load_all_dependencies(self) -> None:
        """Load all dependencies from requirements files."""
        self.dependencies.clear()
        
        for req_file in self.discover_requirements_files():
            deps = self.parse_requirements_file(req_file)
            for dep in deps:
                if dep.name in self.dependencies:
                    # Handle duplicate dependencies
                    existing = self.dependencies[dep.name]
                    if existing.constraint != dep.constraint:
                        # Potential conflict
                        conflict = ConflictInfo(
                            package=dep.name,
                            required_versions=[existing.constraint or "any", dep.constraint or "any"],
                            source_files=[existing.source_file or "unknown", dep.source_file or "unknown"]
                        )
                        self.conflicts.append(conflict)
                else:
                    self.dependencies[dep.name] = dep
                    
    def get_installed_versions(self) -> None:
        """Get currently installed versions of dependencies."""
        try:
            installed = {}
            for dist in pkg_resources.working_set:
                installed[dist.project_name.lower()] = dist.version
                
            for dep_name, dep_info in self.dependencies.items():
                if dep_name in installed:
                    dep_info.installed_version = installed[dep_name]
                    
        except Exception as e:
            print(f"Error getting installed versions: {e}")
    
    def check_version_compatibility(self) -> List[Dict]:
        """Check version compatibility for all dependencies."""
        compatibility_issues = []
        
        for dep_name, dep_info in self.dependencies.items():
            if not dep_info.installed_version or not dep_info.constraint:
                continue
                
            try:
                spec = specifiers.SpecifierSet(dep_info.constraint)
                installed_ver = version.Version(dep_info.installed_version)
                
                if installed_ver not in spec:
                    compatibility_issues.append({
                        'package': dep_name,
                        'installed': dep_info.installed_version,
                        'required': dep_info.constraint,
                        'source': dep_info.source_file,
                        'compatible': False
                    })
                else:
                    compatibility_issues.append({
                        'package': dep_name,
                        'installed': dep_info.installed_version,
                        'required': dep_info.constraint,
                        'source': dep_info.source_file,
                        'compatible': True
                    })
                    
            except Exception as e:
                compatibility_issues.append({
                    'package': dep_name,
                    'installed': dep_info.installed_version,
                    'required': dep_info.constraint,
                    'source': dep_info.source_file,
                    'error': str(e)
                })
                
        return compatibility_issues
    
    def check_security_vulnerabilities(self) -> List[Dict]:
        """Check for security vulnerabilities using safety."""
        vulnerabilities = []
        
        try:
            # Create a temporary requirements file with all dependencies
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
                for dep_name, dep_info in self.dependencies.items():
                    if dep_info.constraint:
                        tmp_file.write(f"{dep_name}{dep_info.constraint}\n")
                    else:
                        tmp_file.write(f"{dep_name}\n")
                tmp_file_path = tmp_file.name
            
            # Run safety check
            result = subprocess.run([
                sys.executable, '-m', 'safety', 'check', '-r', tmp_file_path, '--json'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # No vulnerabilities found
                vulnerabilities = []
            else:
                try:
                    vulnerabilities = json.loads(result.stdout)
                except json.JSONDecodeError:
                    # Fallback: parse text output
                    vulnerabilities = self._parse_safety_text_output(result.stdout)
                    
            # Clean up temp file
            os.unlink(tmp_file_path)
            
        except subprocess.CalledProcessError as e:
            print(f"Error running safety check: {e}")
        except Exception as e:
            print(f"Error checking vulnerabilities: {e}")
            
        return vulnerabilities
    
    def _parse_safety_text_output(self, output: str) -> List[Dict]:
        """Parse safety text output as fallback."""
        vulnerabilities = []
        lines = output.split('\n')
        
        for line in lines:
            if 'vulnerability' in line.lower() and '/' in line:
                parts = line.split('/')
                if len(parts) >= 2:
                    package = parts[0].strip()
                    vuln_info = parts[1].strip()
                    vulnerabilities.append({
                        'package': package,
                        'vulnerability': vuln_info,
                        'severity': 'unknown'
                    })
                    
        return vulnerabilities
    
    def get_package_info(self, package_name: str) -> Dict:
        """Get package information from PyPI."""
        try:
            response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'name': data['info']['name'],
                    'version': data['info']['version'],
                    'description': data['info']['summary'],
                    'homepage': data['info']['home_page'],
                    'license': data['info']['license'],
                    'author': data['info']['author'],
                    'requires_python': data['info']['requires_python'],
                    'classifiers': data['info']['classifiers']
                }
        except Exception as e:
            print(f"Error fetching info for {package_name}: {e}")
            
        return {}
    
    def analyze_licenses(self) -> Dict[str, List[str]]:
        """Analyze licenses of all dependencies."""
        license_groups = {
            'permissive': [],
            'copyleft': [],
            'proprietary': [],
            'unknown': []
        }
        
        # Known license classifications
        permissive_licenses = ['MIT', 'BSD', 'Apache', 'ISC', 'Unlicense']
        copyleft_licenses = ['GPL', 'LGPL', 'AGPL', 'MPL']
        
        for dep_name in self.dependencies:
            package_info = self.get_package_info(dep_name)
            if package_info:
                license_text = package_info.get('license', '').upper()
                
                if any(perm in license_text for perm in permissive_licenses):
                    license_groups['permissive'].append(dep_name)
                elif any(copy in license_text for copy in copyleft_licenses):
                    license_groups['copyleft'].append(dep_name)
                elif license_text and 'PROPRIETARY' in license_text:
                    license_groups['proprietary'].append(dep_name)
                else:
                    license_groups['unknown'].append(dep_name)
            else:
                license_groups['unknown'].append(dep_name)
                
            # Add small delay to be respectful to PyPI
            time.sleep(0.1)
            
        return license_groups
    
    def generate_dependency_tree(self) -> Dict:
        """Generate a dependency tree showing relationships."""
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pipdeptree', '--json'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                print("pipdeptree not available. Install with: pip install pipdeptree")
                return {}
                
        except Exception as e:
            print(f"Error generating dependency tree: {e}")
            return {}
    
    def suggest_updates(self) -> List[Dict]:
        """Suggest dependency updates based on latest versions."""
        suggestions = []
        
        for dep_name, dep_info in self.dependencies.items():
            package_info = self.get_package_info(dep_name)
            if package_info and package_info.get('version'):
                latest_version = package_info['version']
                current_version = dep_info.installed_version
                
                if current_version and latest_version:
                    try:
                        current_ver = version.Version(current_version)
                        latest_ver = version.Version(latest_version)
                        
                        if latest_ver > current_ver:
                            suggestions.append({
                                'package': dep_name,
                                'current': current_version,
                                'latest': latest_version,
                                'source': dep_info.source_file,
                                'is_dev': dep_info.is_dev,
                                'constraint': dep_info.constraint
                            })
                    except Exception:
                        pass
                        
            # Small delay to be respectful
            time.sleep(0.1)
            
        return suggestions
    
    def generate_report(self) -> Dict:
        """Generate a comprehensive dependency report."""
        print("🔍 Analyzing dependencies...")
        
        # Load all dependencies
        self.load_all_dependencies()
        print(f"📦 Found {len(self.dependencies)} unique dependencies")
        
        # Get installed versions
        self.get_installed_versions()
        
        # Check compatibility
        print("🔧 Checking version compatibility...")
        compatibility = self.check_version_compatibility()
        
        # Check security vulnerabilities
        print("🔒 Checking security vulnerabilities...")
        vulnerabilities = self.check_security_vulnerabilities()
        
        # Analyze licenses
        print("📄 Analyzing licenses...")
        licenses = self.analyze_licenses()
        
        # Generate dependency tree
        print("🌳 Generating dependency tree...")
        dependency_tree = self.generate_dependency_tree()
        
        # Suggest updates
        print("⬆️ Checking for updates...")
        update_suggestions = self.suggest_updates()
        
        report = {
            'summary': {
                'total_dependencies': len(self.dependencies),
                'production_dependencies': len([d for d in self.dependencies.values() if not d.is_dev]),
                'development_dependencies': len([d for d in self.dependencies.values() if d.is_dev]),
                'conflicts': len(self.conflicts),
                'vulnerabilities': len(vulnerabilities),
                'update_suggestions': len(update_suggestions)
            },
            'dependencies': {name: {
                'constraint': dep.constraint,
                'installed_version': dep.installed_version,
                'source_file': dep.source_file,
                'is_dev': dep.is_dev
            } for name, dep in self.dependencies.items()},
            'conflicts': [
                {
                    'package': c.package,
                    'required_versions': c.required_versions,
                    'source_files': c.source_files
                } for c in self.conflicts
            ],
            'compatibility': compatibility,
            'vulnerabilities': vulnerabilities,
            'licenses': licenses,
            'dependency_tree': dependency_tree,
            'update_suggestions': update_suggestions
        }
        
        return report
    
    def save_report(self, report: Dict, output_file: Optional[Path] = None) -> None:
        """Save the dependency report to a file."""
        if output_file is None:
            output_file = self.project_root / "dependency-report.json"
            
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
            
        print(f"📊 Report saved to {output_file}")
    
    def print_summary(self, report: Dict) -> None:
        """Print a summary of the dependency analysis."""
        summary = report['summary']
        
        print("\n" + "="*60)
        print("🏆 DEPENDENCY ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"📦 Total Dependencies: {summary['total_dependencies']}")
        print(f"🏭 Production: {summary['production_dependencies']}")
        print(f"🧪 Development: {summary['development_dependencies']}")
        print()
        
        # Conflicts
        if summary['conflicts'] > 0:
            print(f"⚠️  Conflicts Found: {summary['conflicts']}")
            for conflict in report['conflicts']:
                print(f"   - {conflict['package']}: {', '.join(conflict['required_versions'])}")
        else:
            print("✅ No dependency conflicts detected")
        print()
        
        # Security
        if summary['vulnerabilities'] > 0:
            print(f"🚨 Security Vulnerabilities: {summary['vulnerabilities']}")
            for vuln in report['vulnerabilities'][:5]:  # Show first 5
                print(f"   - {vuln.get('package', 'unknown')}: {vuln.get('vulnerability', 'unknown')}")
            if len(report['vulnerabilities']) > 5:
                print(f"   ... and {len(report['vulnerabilities']) - 5} more")
        else:
            print("🔒 No known security vulnerabilities")
        print()
        
        # Updates
        if summary['update_suggestions'] > 0:
            print(f"⬆️  Update Suggestions: {summary['update_suggestions']}")
            for update in report['update_suggestions'][:5]:  # Show first 5
                print(f"   - {update['package']}: {update['current']} → {update['latest']}")
            if len(report['update_suggestions']) > 5:
                print(f"   ... and {len(report['update_suggestions']) - 5} more")
        else:
            print("✨ All dependencies are up to date")
        print()
        
        # License summary
        licenses = report['licenses']
        print("📄 License Summary:")
        print(f"   - Permissive: {len(licenses['permissive'])}")
        print(f"   - Copyleft: {len(licenses['copyleft'])}")
        print(f"   - Proprietary: {len(licenses['proprietary'])}")
        print(f"   - Unknown: {len(licenses['unknown'])}")
        
        print("\n" + "="*60)


def main():
    """Main entry point for the dependency management CLI."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Dependency Management for Obsidian AI Assistant"
    )
    parser.add_argument(
        '--project-root', 
        type=Path, 
        help="Project root directory (default: current directory)"
    )
    parser.add_argument(
        '--output', 
        type=Path, 
        help="Output file for the report (default: dependency-report.json)"
    )
    parser.add_argument(
        '--format', 
        choices=['json', 'summary'], 
        default='summary',
        help="Output format (default: summary)"
    )
    parser.add_argument(
        '--check-security', 
        action='store_true',
        help="Focus on security vulnerability checking"
    )
    parser.add_argument(
        '--check-updates', 
        action='store_true',
        help="Focus on checking for available updates"
    )
    
    args = parser.parse_args()
    
    # Initialize dependency manager
    dm = DependencyManager(args.project_root)
    
    # Generate report
    report = dm.generate_report()
    
    # Output results
    if args.format == 'json':
        dm.save_report(report, args.output)
    else:
        dm.print_summary(report)
        if args.output:
            dm.save_report(report, args.output)
    
    # Check for critical issues
    critical_issues = len(report['conflicts']) + len(report['vulnerabilities'])
    if critical_issues > 0:
        print(f"\n🚨 {critical_issues} critical issues found!")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
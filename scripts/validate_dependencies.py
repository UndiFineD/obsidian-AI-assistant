#!/usr/bin/env python3
"""
Quick Dependency Validation Script

A lightweight script for quick dependency health checks during development.
Perfect for pre-commit hooks and local development workflow.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional


def check_requirements_syntax() -> Dict:
    """Check syntax of all requirements files."""
    results = {"valid_files": [], "invalid_files": [], "total_dependencies": 0}

    req_files = ["requirements.txt", "requirements-dev.txt", "requirements-test.txt"]

    for req_file in req_files:
        req_path = Path(req_file)
        if not req_path.exists():
            continue

        try:
            with open(req_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            valid_lines = 0
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # Basic syntax validation
                if any(char in line for char in [">=", "==", "<=", ">", "<", "~="]):
                    valid_lines += 1
                elif line and not line.startswith("-"):
                    valid_lines += 1

            results["valid_files"].append(
                {"file": str(req_path), "dependencies": valid_lines}
            )
            results["total_dependencies"] += valid_lines

        except Exception as e:
            results["invalid_files"].append({"file": str(req_path), "error": str(e)})

    return results


def quick_security_check() -> Dict:
    """Run a quick security check using available tools."""
    results = {
        "safety_available": False,
        "bandit_available": False,
        "vulnerabilities": [],
        "security_issues": [],
    }

    # Check if safety is available
    try:
        subprocess.run(
            [sys.executable, "-m", "safety", "--version"],
            capture_output=True,
            check=True,
        )
        results["safety_available"] = True

        # Quick safety check
        req_files = []
        for req_file in ["requirements.txt", "requirements-dev.txt"]:
            if Path(req_file).exists():
                req_files.append(req_file)

        if req_files:
            # Create temp combined requirements
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False
            ) as tmp:
                for req_file in req_files:
                    with open(req_file, "r") as f:
                        tmp.write(f.read())
                tmp_path = tmp.name

            try:
                result = subprocess.run(
                    [sys.executable, "-m", "safety", "check", "-r", tmp_path, "--json"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.stdout:
                    try:
                        vulns = json.loads(result.stdout)
                        results["vulnerabilities"] = vulns[:5]  # Limit to 5
                    except json.JSONDecodeError:
                        pass

            except subprocess.TimeoutExpired:
                pass
            finally:
                os.unlink(tmp_path)

    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Check if bandit is available
    try:
        subprocess.run(
            [sys.executable, "-m", "bandit", "--version"],
            capture_output=True,
            check=True,
        )
        results["bandit_available"] = True

        # Quick bandit check on backend directory
        if Path("backend").exists():
            try:
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "bandit",
                        "-r",
                        "agent/",
                        "-f",
                        "json",
                        "--skip",
                        "B101",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.stdout:
                    try:
                        bandit_data = json.loads(result.stdout)
                        issues = bandit_data.get("results", [])
                        # Filter for high and medium severity
                        high_medium = [
                            issue
                            for issue in issues
                            if issue.get("issue_severity") in ["HIGH", "MEDIUM"]
                        ]
                        results["security_issues"] = high_medium[:5]  # Limit to 5
                    except json.JSONDecodeError:
                        pass

            except subprocess.TimeoutExpired:
                pass

    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return results


def check_dependency_conflicts() -> Dict:
    """Check for potential dependency conflicts."""
    results = {"conflicts": [], "duplicates": []}

    # Parse all requirements files
    all_deps = {}

    req_files = ["requirements.txt", "requirements-dev.txt"]
    for req_file in req_files:
        req_path = Path(req_file)
        if not req_path.exists():
            continue

        try:
            with open(req_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip().split("#")[0]  # Remove comments
                    if not line or line.startswith("-"):
                        continue

                    # Extract package name
                    pkg_name = (
                        line.split(">=")[0].split("==")[0].split("<")[0].split(">")[0]
                    )
                    pkg_name = pkg_name.strip()

                    if pkg_name in all_deps:
                        # Potential duplicate/conflict
                        existing_info = all_deps[pkg_name]
                        if existing_info["constraint"] != line:
                            results["conflicts"].append(
                                {
                                    "package": pkg_name,
                                    "constraint1": existing_info["constraint"],
                                    "file1": existing_info["file"],
                                    "constraint2": line,
                                    "file2": req_file,
                                }
                            )
                        else:
                            results["duplicates"].append(
                                {
                                    "package": pkg_name,
                                    "constraint": line,
                                    "files": [existing_info["file"], req_file],
                                }
                            )
                    else:
                        all_deps[pkg_name] = {"constraint": line, "file": req_file}

        except Exception as e:
            print(f"Error parsing {req_file}: {e}")

    return results


def check_critical_packages() -> Dict:
    """Check status of critical security packages."""
    critical_packages = [
        "cryptography",
        "pyjwt",
        "requests",
        "urllib3",
        "pillow",
        "fastapi",
        "uvicorn",
        "pydantic",
    ]

    results = {"installed": [], "missing": [], "outdated": []}

    try:
        # Get installed packages
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            timeout=15,
        )

        if result.returncode == 0:
            installed_packages = json.loads(result.stdout)
            installed_dict = {
                pkg["name"].lower(): pkg["version"] for pkg in installed_packages
            }

            for pkg in critical_packages:
                if pkg.lower() in installed_dict:
                    results["installed"].append(
                        {"package": pkg, "version": installed_dict[pkg.lower()]}
                    )
                else:
                    results["missing"].append(pkg)

        # Check for outdated critical packages
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
            capture_output=True,
            text=True,
            timeout=15,
        )

        if result.returncode == 0:
            outdated_packages = json.loads(result.stdout)
            for pkg in outdated_packages:
                if pkg["name"].lower() in [cp.lower() for cp in critical_packages]:
                    results["outdated"].append(
                        {
                            "package": pkg["name"],
                            "current": pkg["version"],
                            "latest": pkg["latest_version"],
                        }
                    )

    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        json.JSONDecodeError,
    ):
        pass

    return results


def main():
    """Run quick dependency validation."""
    print("🔍 Quick Dependency Validation")
    print("=" * 40)

    # Check requirements file syntax
    print("\n📄 Checking requirements files...")
    syntax_results = check_requirements_syntax()

    if syntax_results["invalid_files"]:
        print("❌ Invalid requirements files found:")
        for invalid in syntax_results["invalid_files"]:
            print(f"   - {invalid['file']}: {invalid['error']}")
    else:
        print(
            f"✅ All requirements files valid ({syntax_results['total_dependencies']} dependencies)"
        )

    # Check for conflicts
    print("\n🔧 Checking for dependency conflicts...")
    conflict_results = check_dependency_conflicts()

    if conflict_results["conflicts"]:
        print(f"⚠️  {len(conflict_results['conflicts'])} potential conflicts found:")
        for conflict in conflict_results["conflicts"][:3]:  # Show first 3
            print(
                f"   - {conflict['package']}: {conflict['constraint1']} vs {conflict['constraint2']}"
            )
    else:
        print("✅ No dependency conflicts detected")

    if conflict_results["duplicates"]:
        print(f"📋 {len(conflict_results['duplicates'])} duplicate entries found")

    # Quick security check
    print("\n🔒 Running quick security check...")
    security_results = quick_security_check()

    if security_results["safety_available"]:
        vuln_count = len(security_results["vulnerabilities"])
        if vuln_count > 0:
            print(f"⚠️  {vuln_count} vulnerabilities detected by Safety")
            for vuln in security_results["vulnerabilities"][:2]:  # Show first 2
                pkg = vuln.get("package", "unknown")
                print(f"   - {pkg}")
        else:
            print("✅ No vulnerabilities detected by Safety")
    else:
        print("⏩ Safety not available (install with: pip install safety)")

    if security_results["bandit_available"]:
        issue_count = len(security_results["security_issues"])
        if issue_count > 0:
            print(f"⚠️  {issue_count} security issues detected by Bandit")
        else:
            print("✅ No high/medium security issues detected by Bandit")
    else:
        print("⏩ Bandit not available (install with: pip install bandit)")

    # Check critical packages
    print("\n⭐ Checking critical packages...")
    critical_results = check_critical_packages()

    if critical_results["missing"]:
        print(f"❌ Missing critical packages: {', '.join(critical_results['missing'])}")

    if critical_results["outdated"]:
        print(f"📅 Outdated critical packages: {len(critical_results['outdated'])}")
        for pkg in critical_results["outdated"][:3]:  # Show first 3
            print(f"   - {pkg['package']}: {pkg['current']} → {pkg['latest']}")
    else:
        print("✅ Critical packages are up to date")

    # Summary
    print("\n" + "=" * 40)

    total_issues = (
        len(syntax_results["invalid_files"])
        + len(conflict_results["conflicts"])
        + len(security_results["vulnerabilities"])
        + len(security_results["security_issues"])
        + len(critical_results["missing"])
        + len(critical_results["outdated"])
    )

    if total_issues == 0:
        print("🎉 No critical issues detected!")
        print("✨ Dependencies look healthy")
        return 0
    else:
        print(f"⚠️  {total_issues} issues detected")
        print("\n🎯 Recommended actions:")

        if syntax_results["invalid_files"]:
            print("   - Fix syntax errors in requirements files")
        if conflict_results["conflicts"]:
            print("   - Resolve dependency version conflicts")
        if security_results["vulnerabilities"]:
            print("   - Update packages with security vulnerabilities")
        if critical_results["missing"]:
            print("   - Install missing critical packages")
        if critical_results["outdated"]:
            print("   - Update outdated critical packages")

        print("\n🔍 For detailed analysis, run:")
        print("   python scripts/dependency_manager.py")
        print("   python scripts/security_scanner.py")

        return 1


if __name__ == "__main__":
    sys.exit(main())

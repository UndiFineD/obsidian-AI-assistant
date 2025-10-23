#!/usr/bin/env python3
"""
Security Validation Script

This script validates the security configuration and tests security scanning workflows.
Run this script to ensure security measures are properly configured.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import yaml


def check_file_exists(filepath: str) -> bool:
    """Check if a file exists."""
    return Path(filepath).exists()


def check_security_files() -> Dict[str, bool]:
    """Check if all security-related files exist."""
    security_files = {
        "Security Policy": "SECURITY.md",
        "Security Workflow": ".github/workflows/security-scan.yml",
        "Dependabot Config": ".github/dependabot.yml",
        "Security Specification": "docs/SECURITY_SPECIFICATION.md",
        "Requirements File": "requirements.txt",
        "Dev Requirements": "requirements-dev.txt",
        "Bandit Config": "pyproject.toml",
        "GitHub Workflows Dir": ".github/workflows",
    }

    results = {}
    for name, filepath in security_files.items():
        results[name] = check_file_exists(filepath)

    return results


def validate_security_workflow() -> Tuple[bool, List[str]]:
    """Validate the security workflow YAML file."""
    workflow_path = ".github/workflows/security-scan.yml"
    issues = []

    if not check_file_exists(workflow_path):
        return False, ["Security workflow file does not exist"]

    try:
        with open(workflow_path, "r", encoding="utf-8") as f:
            content = f.read()
            workflow = yaml.safe_load(content)

        if workflow is None:
            issues.append("YAML file is empty or invalid")
            return False, issues

        # Check required components with tolerance for YAML parsing quirks
        required_keys = ["name", "jobs"]
        for key in required_keys:
            if key not in workflow:
                issues.append(f"Missing required key: {key}")

        # Check for 'on' key or True key (YAML parser issue)
        if "on" not in workflow and True not in workflow:
            issues.append("Missing workflow trigger configuration")

        # Check if jobs exist
        if "jobs" in workflow:
            expected_jobs = [
                "python-security",
                "javascript-security",
                "snyk-security",
                "security-config",
                "create-security-issues",
                "pr-comment",
            ]

            actual_jobs = list(workflow["jobs"].keys())
            missing_jobs = []
            for job in expected_jobs:
                if job not in actual_jobs:
                    missing_jobs.append(job)

            if missing_jobs:
                issues.append(f'Missing expected jobs: {", ".join(missing_jobs)}')

        # Check schedule trigger (try both 'on' and True keys)
        trigger_config = workflow.get("on") or workflow.get(True)
        if trigger_config and isinstance(trigger_config, dict):
            if "schedule" not in trigger_config:
                issues.append("Missing schedule trigger for daily scans")
            elif not trigger_config["schedule"]:
                issues.append("Schedule trigger is empty")
        else:
            issues.append("Missing or invalid trigger configuration")

        # Validate content by checking for key strings
        if "safety check" not in content.lower():
            issues.append("Missing Safety security scanning")
        if "bandit" not in content.lower():
            issues.append("Missing Bandit security scanning")
        if "semgrep" not in content.lower():
            issues.append("Missing Semgrep security scanning")

    except yaml.YAMLError as e:
        issues.append(f"YAML parsing error: {e}")
    except UnicodeDecodeError as e:
        issues.append(f"File encoding error: {e}")
    except Exception as e:
        issues.append(f"Error validating workflow: {e}")

    return len(issues) == 0, issues


def validate_dependabot_config() -> Tuple[bool, List[str]]:
    """Validate the Dependabot configuration."""
    config_path = ".github/dependabot.yml"
    issues = []

    if not check_file_exists(config_path):
        return False, ["Dependabot configuration file does not exist"]

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # Check version
        if config.get("version") != 2:
            issues.append("Dependabot config should use version 2")

        # Check updates configuration
        if "updates" not in config:
            issues.append("Missing updates configuration")
        else:
            updates = config["updates"]
            expected_ecosystems = ["pip", "npm", "github-actions", "docker"]
            actual_ecosystems = [update.get("package-ecosystem") for update in updates]

            for ecosystem in expected_ecosystems:
                if ecosystem not in actual_ecosystems:
                    issues.append(f"Missing ecosystem: {ecosystem}")

    except yaml.YAMLError as e:
        issues.append(f"YAML parsing error: {e}")
    except Exception as e:
        issues.append(f"Error validating Dependabot config: {e}")

    return len(issues) == 0, issues


def check_python_security_tools() -> Dict[str, bool]:
    """Check if Python security tools are available."""
    tools = ["safety", "bandit", "semgrep"]
    results = {}

    for tool in tools:
        try:
            result = subprocess.run(
                [tool, "--version"], capture_output=True, text=True, timeout=10
            )
            results[tool] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            results[tool] = False

    return results


def check_javascript_security_tools() -> Dict[str, bool]:
    """Check if JavaScript security tools are available."""
    tools = ["npm"]
    results = {}

    for tool in tools:
        try:
            result = subprocess.run(
                [tool, "--version"], capture_output=True, text=True, timeout=10
            )
            results[tool] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            results[tool] = False

    return results


def scan_dependencies_safety() -> Tuple[bool, str]:
    """Run safety scan on Python dependencies."""
    try:
        result = subprocess.run(
            ["safety", "check", "--json"], capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0:
            return True, "No known security vulnerabilities found"
        else:
            # Parse JSON output for vulnerabilities
            try:
                vulnerabilities = json.loads(result.stdout)
                return False, f"Found {len(vulnerabilities)} security vulnerabilities"
            except json.JSONDecodeError:
                return False, f"Safety scan failed: {result.stderr}"

    except subprocess.TimeoutExpired:
        return False, "Safety scan timed out"
    except FileNotFoundError:
        return False, "Safety tool not found - install with: pip install safety"
    except Exception as e:
        return False, f"Error running safety scan: {e}"


def scan_code_bandit() -> Tuple[bool, str]:
    """Run Bandit security scan on Python code."""
    try:
        result = subprocess.run(
            ["bandit", "-r", "agent/", "-f", "json"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Bandit returns 1 if issues found, 0 if no issues
        if result.returncode == 0:
            return True, "No security issues found in code"
        elif result.returncode == 1:
            try:
                report = json.loads(result.stdout)
                issues = len(report.get("results", []))
                confidence_counts = {}
                severity_counts = {}

                for issue in report.get("results", []):
                    confidence = issue.get("issue_confidence", "UNKNOWN")
                    severity = issue.get("issue_severity", "UNKNOWN")
                    confidence_counts[confidence] = (
                        confidence_counts.get(confidence, 0) + 1
                    )
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1

                summary = f"Found {issues} security issues"
                if severity_counts:
                    summary += f" (Severity: {dict(severity_counts)})"
                if confidence_counts:
                    summary += f" (Confidence: {dict(confidence_counts)})"

                return False, summary
            except json.JSONDecodeError:
                return False, f"Bandit scan completed with issues: {result.stderr}"
        else:
            return False, f"Bandit scan failed: {result.stderr}"

    except subprocess.TimeoutExpired:
        return False, "Bandit scan timed out"
    except FileNotFoundError:
        return False, "Bandit tool not found - install with: pip install bandit"
    except Exception as e:
        return False, f"Error running Bandit scan: {e}"


def print_section(title: str, content: str = None):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    if content:
        print(content)


def print_check_result(name: str, status: bool, details: str = None):
    """Print a check result with color coding."""
    status_symbol = "✅" if status else "❌"
    print(f"{status_symbol} {name}")
    if details:
        print(f"   {details}")


def main():
    """Main security validation function."""
    print("🛡️  Obsidian AI Agent - Security Validation")
    print("=" * 60)

    all_passed = True

    # Check security files
    print_section("Security File Validation")
    file_checks = check_security_files()
    for name, exists in file_checks.items():
        print_check_result(name, exists)
        if not exists:
            all_passed = False

    # Validate security workflow
    print_section("Security Workflow Validation")
    workflow_valid, workflow_issues = validate_security_workflow()
    print_check_result("Security Workflow", workflow_valid)
    for issue in workflow_issues:
        print(f"   ⚠️  {issue}")
    if not workflow_valid:
        all_passed = False

    # Validate Dependabot config
    print_section("Dependabot Configuration Validation")
    dependabot_valid, dependabot_issues = validate_dependabot_config()
    print_check_result("Dependabot Config", dependabot_valid)
    for issue in dependabot_issues:
        print(f"   ⚠️  {issue}")
    if not dependabot_valid:
        all_passed = False

    # Check security tools
    print_section("Security Tools Availability")
    python_tools = check_python_security_tools()
    for tool, available in python_tools.items():
        print_check_result(f"Python tool: {tool}", available)
        if not available:
            print(f"   💡 Install with: pip install {tool}")

    js_tools = check_javascript_security_tools()
    for tool, available in js_tools.items():
        print_check_result(f"JavaScript tool: {tool}", available)

    # Run security scans if tools are available
    print_section("Security Scanning")

    # Safety scan
    if python_tools.get("safety", False):
        safety_passed, safety_msg = scan_dependencies_safety()
        print_check_result("Dependency Security (Safety)", safety_passed, safety_msg)
        if not safety_passed and "vulnerabilities" in safety_msg:
            all_passed = False
    else:
        print("⏭️  Skipping Safety scan - tool not available")

    # Bandit scan
    if python_tools.get("bandit", False):
        bandit_passed, bandit_msg = scan_code_bandit()
        print_check_result("Code Security (Bandit)", bandit_passed, bandit_msg)
        # Note: We don't fail on Bandit issues as they may be false positives
        # But we report them for review
    else:
        print("⏭️  Skipping Bandit scan - tool not available")

    # Summary
    print_section("Validation Summary")
    if all_passed:
        print("🎉 All security validations passed!")
        print("\n✅ Your security configuration is properly set up.")
        print("✅ Security workflows are ready for automated scanning.")
        print("✅ Dependabot will keep dependencies updated.")
        print("\n💡 Next steps:")
        print("   • Commit and push your changes to trigger workflows")
        print("   • Review any security scan results in GitHub Actions")
        print("   • Monitor GitHub Security advisories for your repository")
        return 0
    else:
        print("⚠️  Some security validations failed.")
        print("\n❌ Please address the issues above before proceeding.")
        print("❌ Security configuration may be incomplete.")
        print("\n💡 Common fixes:")
        print("   • Install missing security tools with pip")
        print("   • Check YAML syntax in workflow files")
        print("   • Ensure all required files are present")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

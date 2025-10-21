#!/usr/bin/env python3
"""
Security-focused Dependency Scanner for Obsidian AI Agent

This script focuses specifically on security aspects of dependency management:
- CVE vulnerability scanning
- License compliance checking
- Outdated package detection with security implications
- Supply chain risk assessment
- Integration with GitHub security advisories
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import requests


class SecurityScanner:
    """Security-focused dependency scanner."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the security scanner."""
        self.project_root = project_root or Path.cwd()
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.snyk_token = os.environ.get("SNYK_TOKEN")
        # Allow disabling network-heavy scans by default for offline/CI stability
        self.enable_network_scans = os.environ.get("SECURITY_SCANNER_NETWORK", "0") in (
            "1",
            "true",
            "yes",
        )

    def scan_with_safety(self) -> Dict:
        """Scan dependencies using Python Safety."""
        print("[security] Running Safety security scan...")

        results = {
            "tool": "safety",
            "scan_time": datetime.now().isoformat(),
            "vulnerabilities": [],
            "status": "success",
        }

        try:
            # Create consolidated requirements file
            req_files = ["requirements.txt", "requirements-dev.txt"]
            temp_reqs = []

            for req_file in req_files:
                req_path = self.project_root / req_file
                if req_path.exists():
                    with open(req_path, "r") as f:
                        temp_reqs.extend(f.readlines())

            if not temp_reqs:
                results["status"] = "no_requirements"
                return results

            # Write temporary requirements file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False
            ) as tmp:
                tmp.writelines(temp_reqs)
                tmp_path = tmp.name

            try:
                # Run safety check
                cmd = [
                    sys.executable,
                    "-m",
                    "safety",
                    "check",
                    "-r",
                    tmp_path,
                    "--json",
                ]
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=300
                )

                if result.returncode == 0:
                    results["vulnerabilities"] = []
                elif result.stdout:
                    try:
                        vuln_data = json.loads(result.stdout)
                        results["vulnerabilities"] = vuln_data
                    except json.JSONDecodeError:
                        # Parse text output
                        results["vulnerabilities"] = self._parse_safety_text(
                            result.stdout
                        )
                else:
                    results["status"] = "error"
                    results["error"] = result.stderr

            finally:
                os.unlink(tmp_path)

        except subprocess.TimeoutExpired:
            results["status"] = "timeout"
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)

        print(f"   Found {len(results.get('vulnerabilities', []))} vulnerabilities")
        return results

    def _parse_safety_text(self, output: str) -> List[Dict]:
        """Parse safety text output."""
        vulnerabilities = []
        lines = output.strip().split("\n")

        current_vuln = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("->"):
                # Vulnerability description
                current_vuln["description"] = line[2:].strip()
            elif "/" in line and any(char.isdigit() for char in line):
                # Package/version line
                parts = line.split("/")
                if len(parts) >= 2:
                    current_vuln["package"] = parts[0].strip()
                    current_vuln["version"] = parts[1].strip()
                    vulnerabilities.append(current_vuln.copy())
                    current_vuln = {}

        return vulnerabilities

    def scan_with_bandit(self) -> Dict:
        """Scan Python code for security issues using Bandit."""
        print("[security] Running Bandit security scan...")

        results = {
            "tool": "bandit",
            "scan_time": datetime.now().isoformat(),
            "issues": [],
            "status": "success",
        }

        try:
            agent_path = self.project_root / "backend"
            if not agent_path.exists():
                results["status"] = "no_backend"
                return results

            cmd = [
                sys.executable,
                "-m",
                "bandit",
                "-r",
                str(agent_path),
                "-f",
                "json",
                "--skip",
                "B101",  # Skip assert statements
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.stdout:
                try:
                    bandit_data = json.loads(result.stdout)
                    results["issues"] = bandit_data.get("results", [])
                    results["metrics"] = bandit_data.get("metrics", {})
                except json.JSONDecodeError:
                    results["status"] = "parse_error"
                    results["raw_output"] = result.stdout
            else:
                results["status"] = "no_output"

        except subprocess.TimeoutExpired:
            results["status"] = "timeout"
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)

        print(f"   Found {len(results.get('issues', []))} security issues")
        return results

    def check_outdated_packages(self) -> Dict:
        """Check for outdated packages with security implications."""
        print("[security] Checking for outdated packages...")

        results = {
            "tool": "pip-outdated",
            "scan_time": datetime.now().isoformat(),
            "outdated": [],
            "status": "success",
        }

        try:
            cmd = [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0 and result.stdout:
                outdated_data = json.loads(result.stdout)

                # Filter for security-sensitive packages
                security_packages = [
                    "cryptography",
                    "pyjwt",
                    "requests",
                    "urllib3",
                    "pillow",
                    "django",
                    "flask",
                    "fastapi",
                    "sqlalchemy",
                    "psycopg2",
                    "paramiko",
                    "pyopenssl",
                    "certifi",
                    "click",
                    "jinja2",
                ]

                for pkg in outdated_data:
                    pkg_info = {
                        "name": pkg["name"],
                        "current": pkg["version"],
                        "latest": pkg["latest_version"],
                        "type": pkg.get("latest_filetype", "unknown"),
                        "is_security_sensitive": pkg["name"].lower()
                        in security_packages,
                    }
                    results["outdated"].append(pkg_info)

            else:
                results["status"] = "error"
                results["error"] = result.stderr

        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)

        print(f"   Found {len(results.get('outdated', []))} outdated packages")
        return results

    def check_github_advisories(self) -> Dict:
        """Check GitHub security advisories for project dependencies."""
        print("[security] Checking GitHub security advisories...")

        results = {
            "tool": "github-advisories",
            "scan_time": datetime.now().isoformat(),
            "advisories": [],
            "status": "success",
        }

        if not self.github_token:
            results["status"] = "no_token"
            print("   GitHub token not available, skipping...")
            return results
        if not self.enable_network_scans:
            results["status"] = "skipped"
            print("   Network scans disabled (SECURITY_SCANNER_NETWORK=0). Skipping...")
            return results

        try:
            # Get list of dependencies
            dependencies = self._get_project_dependencies()

            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json",
            }

            for dep_name in dependencies[:10]:  # Limit to avoid rate limiting
                url = f"https://api.github.com/advisories?affects={dep_name}"
                response = requests.get(url, headers=headers, timeout=30)

                if response.status_code == 200:
                    advisories = response.json()
                    for advisory in advisories:
                        results["advisories"].append(
                            {
                                "package": dep_name,
                                "ghsa_id": advisory.get("ghsa_id"),
                                "summary": advisory.get("summary"),
                                "severity": advisory.get("severity"),
                                "published_at": advisory.get("published_at"),
                                "updated_at": advisory.get("updated_at"),
                                "cve_id": advisory.get("cve_id"),
                                "url": advisory.get("html_url"),
                            }
                        )

        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)

        print(f"   Found {len(results.get('advisories', []))} relevant advisories")
        return results

    def _get_project_dependencies(self) -> List[str]:
        """Extract dependency names from requirements files."""
        dependencies = []

        for req_file in ["requirements.txt", "requirements-dev.txt"]:
            req_path = self.project_root / req_file
            if req_path.exists():
                with open(req_path, "r") as f:
                    for line in f:
                        line = line.strip().split("#")[0]  # Remove comments
                        if line and not line.startswith("-"):
                            # Extract package name
                            pkg_name = (
                                line.split(">=")[0]
                                .split("==")[0]
                                .split("<")[0]
                                .split(">")[0]
                            )
                            dependencies.append(pkg_name.strip())

        return list(set(dependencies))  # Remove duplicates

    def analyze_supply_chain_risk(self) -> Dict:
        """Analyze supply chain risks in dependencies."""
        print("[security] Analyzing supply chain risks...")

        results = {
            "tool": "supply-chain-analysis",
            "scan_time": datetime.now().isoformat(),
            "risks": [],
            "status": "success",
        }
        if not self.enable_network_scans:
            results["status"] = "skipped"
            print("   Network scans disabled (SECURITY_SCANNER_NETWORK=0). Skipping...")
            return results

        try:
            dependencies = self._get_project_dependencies()
            high_risk_indicators = []

            for dep_name in dependencies:
                risk_score = 0
                risk_factors = []

                # Check package age and activity
                pkg_info = self._get_pypi_info(dep_name)
                if pkg_info:
                    # Check for recent updates
                    if pkg_info.get("last_updated"):
                        last_update = datetime.fromisoformat(
                            pkg_info["last_updated"].replace("Z", "+00:00")
                        )
                        days_since_update = (
                            datetime.now().replace(tzinfo=None)
                            - last_update.replace(tzinfo=None)
                        ).days

                        if days_since_update > 365:
                            risk_score += 2
                            risk_factors.append(
                                f"No updates in {days_since_update} days"
                            )
                        elif days_since_update > 180:
                            risk_score += 1
                            risk_factors.append(
                                f"Last updated {days_since_update} days ago"
                            )

                    # Check maintainer count
                    maintainers = pkg_info.get("maintainers", [])
                    if len(maintainers) < 2:
                        risk_score += 1
                        risk_factors.append("Single maintainer")

                    # Check download count (low downloads = higher risk)
                    downloads = pkg_info.get("downloads", {}).get("last_month", 0)
                    if downloads < 1000:
                        risk_score += 2
                        risk_factors.append("Low download count")

                if risk_score >= 2:
                    results["risks"].append(
                        {
                            "package": dep_name,
                            "risk_score": risk_score,
                            "risk_factors": risk_factors,
                            "severity": "high" if risk_score >= 3 else "medium",
                        }
                    )

        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)

        print(f"   Identified {len(results.get('risks', []))} supply chain risks")
        return results

    def _get_pypi_info(self, package_name: str) -> Optional[Dict]:
        """Get package information from PyPI."""
        try:
            response = requests.get(
                f"https://pypi.org/pypi/{package_name}/json", timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "name": data["info"]["name"],
                    "version": data["info"]["version"],
                    "last_updated": data["info"].get("upload_time"),
                    "maintainers": data.get("maintainers", []),
                    "downloads": data.get("downloads", {}),
                    "description": data["info"]["summary"],
                    "homepage": data["info"]["home_page"],
                }
        except Exception:
            pass
        return None

    def generate_security_report(self) -> Dict:
        """Generate comprehensive security report."""
        print("[security] Generating comprehensive security report...")
        print("=" * 60)

        report = {
            "scan_metadata": {
                "scan_time": datetime.now().isoformat(),
                "project_root": str(self.project_root),
                "tools_used": [],
            },
            "summary": {
                "total_vulnerabilities": 0,
                "high_severity": 0,
                "medium_severity": 0,
                "low_severity": 0,
                "security_issues": 0,
                "outdated_packages": 0,
                "supply_chain_risks": 0,
            },
            "scans": {},
        }

        # Run all scans
        scans = [
            ("safety", self.scan_with_safety),
            ("bandit", self.scan_with_bandit),
            ("outdated", self.check_outdated_packages),
            ("github_advisories", self.check_github_advisories),
            ("supply_chain", self.analyze_supply_chain_risk),
        ]

        for scan_name, scan_func in scans:
            try:
                scan_result = scan_func()
                report["scans"][scan_name] = scan_result
                report["scan_metadata"]["tools_used"].append(scan_name)

                # Update summary
                if scan_name == "safety":
                    vulns = scan_result.get("vulnerabilities", [])
                    report["summary"]["total_vulnerabilities"] += len(vulns)

                elif scan_name == "bandit":
                    issues = scan_result.get("issues", [])
                    report["summary"]["security_issues"] += len(issues)
                    for issue in issues:
                        severity = issue.get("issue_severity", "low").lower()
                        if severity == "high":
                            report["summary"]["high_severity"] += 1
                        elif severity == "medium":
                            report["summary"]["medium_severity"] += 1
                        else:
                            report["summary"]["low_severity"] += 1

                elif scan_name == "outdated":
                    report["summary"]["outdated_packages"] = len(
                        scan_result.get("outdated", [])
                    )

                elif scan_name == "supply_chain":
                    report["summary"]["supply_chain_risks"] = len(
                        scan_result.get("risks", [])
                    )

            except Exception as e:
                print(f"ERROR: Error running {scan_name} scan: {e}")
                report["scans"][scan_name] = {"status": "error", "error": str(e)}

        return report

    def save_security_report(
        self, report: Dict, output_file: Optional[Path] = None
    ) -> None:
        """Save security report to file."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.project_root / f"security-report-{timestamp}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\nREPORT: Security report saved to {output_file}")

    def print_security_summary(self, report: Dict) -> None:
        """Print security scan summary."""
        summary = report["summary"]

        print("\n" + "=" * 60)
        print("[summary] SECURITY SCAN SUMMARY")
        print("=" * 60)

        # Overall status
        total_issues = (
            summary["total_vulnerabilities"]
            + summary["security_issues"]
            + summary["supply_chain_risks"]
        )

        if total_issues == 0:
            print("No critical security issues found.")
        else:
            print(f"{total_issues} security issues detected")
        print()

        # Vulnerability details
        print("VULNERABILITY SUMMARY:")
        print(f"   Total Vulnerabilities: {summary['total_vulnerabilities']}")
        print(f"   High Severity: {summary['high_severity']}")
        print(f"   Medium Severity: {summary['medium_severity']}")
        print(f"   Low Severity: {summary['low_severity']}")
        print()

        # Code security issues
        print("CODE SECURITY ISSUES:")
        print(f"   Bandit Issues: {summary['security_issues']}")
        print()

        # Maintenance issues
        print("MAINTENANCE ISSUES:")
        print(f"   Outdated Packages: {summary['outdated_packages']}")
        print(f"   Supply Chain Risks: {summary['supply_chain_risks']}")
        print()

        # Tool status
        print("SCAN TOOL STATUS:")
        for tool_name, scan_data in report["scans"].items():
            status = scan_data.get("status", "unknown")
            print(f"   {tool_name.title()}: {status}")

        print("\n" + "=" * 60)

        # Action items
        if total_issues > 0:
            print("RECOMMENDED ACTIONS:")
            if summary["total_vulnerabilities"] > 0:
                print("   1. Review and update vulnerable packages")
            if summary["security_issues"] > 0:
                print("   2. Address Bandit security warnings in code")
            if summary["outdated_packages"] > 0:
                print(
                    "   3. Update outdated packages, especially security-sensitive ones"
                )
            if summary["supply_chain_risks"] > 0:
                print("   4. Review supply chain risks and consider alternatives")
            print()


def main():
    """Main entry point for security scanner."""
    import argparse

    parser = argparse.ArgumentParser(description="Security-focused dependency scanner")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    parser.add_argument("--output", type=Path, help="Output file for security report")
    parser.add_argument("--format", choices=["json", "summary"], default="summary")
    parser.add_argument(
        "--strict-exit",
        action="store_true",
        help="Return non-zero exit when issues found",
    )

    args = parser.parse_args()

    scanner = SecurityScanner(args.project_root)
    report = scanner.generate_security_report()

    if args.format == "json":
        scanner.save_security_report(report, args.output)
    else:
        scanner.print_security_summary(report)
        if args.output:
            scanner.save_security_report(report, args.output)

    # Return error code if critical issues found
    if args.strict_exit:
        critical_issues = (
            report["summary"]["total_vulnerabilities"]
            + report["summary"]["high_severity"]
        )
        return 1 if critical_issues > 0 else 0
    # Default non-strict exit to keep CI stable when running this helper without flags
    return 0


if __name__ == "__main__":
    sys.exit(main())

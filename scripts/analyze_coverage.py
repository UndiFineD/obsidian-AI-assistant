#!/usr/bin/env python3
"""
Coverage Analysis and Improvement Script

This script analyzes test coverage and provides actionable recommendations
for improving coverage to meet the 85% threshold.
"""

import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple


def run_coverage_analysis() -> Tuple[float, Dict[str, Dict[str, any]]]:
    """Run coverage analysis and return overall percentage and per-file details."""
    try:
        # Get Python executable path
        python_exe = sys.executable

        # Run pytest with coverage
        result = subprocess.run(
            [
                python_exe,
                "-m",
                "pytest",
                "tests/agent/",
                "--cov=backend",
                "--cov-report=xml",
                "--cov-report=json",
                "-q",
            ],
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=300,
        )

        print(f"Coverage command exit code: {result.returncode}")
        if result.stderr:
            print(f"Coverage stderr: {result.stderr}")

        # Parse coverage.xml for detailed information
        coverage_data = {}
        overall_coverage = 0.0

        if os.path.exists("coverage.xml"):
            tree = ET.parse("coverage.xml")
            root = tree.getroot()

            # Get overall coverage
            overall_coverage = float(root.get("line-rate", 0)) * 100

            # Get per-file coverage
            for package in root.findall(".//package"):
                for class_elem in package.findall("classes/class"):
                    filename = class_elem.get("filename", "")
                    if filename.startswith("agent/"):
                        lines_valid = int(class_elem.get("lines-valid", 0))
                        lines_covered = int(class_elem.get("lines-covered", 0))
                        line_rate = float(class_elem.get("line-rate", 0))

                        coverage_data[filename] = {
                            "lines_total": lines_valid,
                            "lines_covered": lines_covered,
                            "lines_missed": lines_valid - lines_covered,
                            "coverage_percent": line_rate * 100,
                            "missing_lines": [],
                        }

                        # Get missing line numbers
                        for line in class_elem.findall('.//line[@hits="0"]'):
                            line_num = int(line.get("number", 0))
                            coverage_data[filename]["missing_lines"].append(line_num)
        else:
            print("No coverage.xml file found")

        return overall_coverage, coverage_data

    except subprocess.TimeoutExpired:
        print("⚠️ Coverage analysis timed out")
        return 0.0, {}
    except Exception as e:
        print(f"❌ Error running coverage analysis: {e}")
        import traceback

        traceback.print_exc()
        return 0.0, {}


def categorize_files_by_coverage(
    coverage_data: Dict[str, Dict],
) -> Dict[str, List[str]]:
    """Categorize files by coverage level."""
    categories = {
        "excellent": [],  # >= 95%
        "good": [],  # >= 85%
        "needs_work": [],  # >= 70%
        "critical": [],  # < 70%
    }

    for filename, data in coverage_data.items():
        coverage = data["coverage_percent"]
        if coverage >= 95:
            categories["excellent"].append(filename)
        elif coverage >= 85:
            categories["good"].append(filename)
        elif coverage >= 70:
            categories["needs_work"].append(filename)
        else:
            categories["critical"].append(filename)

    return categories


def identify_improvement_opportunities(coverage_data: Dict[str, Dict]) -> List[Dict]:
    """Identify files with the biggest improvement opportunities."""
    opportunities = []

    for filename, data in coverage_data.items():
        if data["coverage_percent"] < 85:
            # Calculate impact of improving this file
            lines_missed = data["lines_missed"]
            current_coverage = data["coverage_percent"]

            # Estimate impact if we improved this file to 85%
            total_lines = data["lines_total"]
            if total_lines > 0:
                target_covered = int(total_lines * 0.85)
                additional_lines_needed = max(0, target_covered - data["lines_covered"])
                impact_score = additional_lines_needed * (100 - current_coverage)

                opportunities.append(
                    {
                        "filename": filename,
                        "current_coverage": current_coverage,
                        "lines_missed": lines_missed,
                        "additional_lines_needed": additional_lines_needed,
                        "impact_score": impact_score,
                        "missing_lines": data["missing_lines"][
                            :10
                        ],  # First 10 missing lines
                    }
                )

    # Sort by impact score (highest first)
    opportunities.sort(key=lambda x: x["impact_score"], reverse=True)
    return opportunities


def suggest_testing_strategies(filename: str) -> List[str]:
    """Suggest testing strategies based on file type and name."""
    suggestions = []

    if "enterprise" in filename:
        suggestions.extend(
            [
                "Add tests for enterprise features and authentication flows",
                "Test multi-tenant scenarios and data isolation",
                "Verify role-based access control and permissions",
            ]
        )

    if "security" in filename or "auth" in filename:
        suggestions.extend(
            [
                "Test authentication success and failure scenarios",
                "Verify security middleware and validation",
                "Test edge cases and error handling",
            ]
        )

    if "performance" in filename:
        suggestions.extend(
            [
                "Test caching mechanisms and cache hits/misses",
                "Verify performance monitoring and metrics collection",
                "Test connection pooling and resource management",
            ]
        )

    if "backend.py" in filename:
        suggestions.extend(
            [
                "Test all API endpoints with various input scenarios",
                "Verify error handling and status codes",
                "Test middleware integration and request/response processing",
            ]
        )

    if not suggestions:
        suggestions = [
            "Add unit tests for core functionality",
            "Test error handling and edge cases",
            "Verify integration with dependencies",
        ]

    return suggestions


def generate_improvement_plan(opportunities: List[Dict]) -> str:
    """Generate a prioritized improvement plan."""
    plan = []

    plan.append("# 📈 Coverage Improvement Plan")
    plan.append("")
    plan.append("## 🎯 Goal: Reach 85% Coverage Threshold")
    plan.append("")

    if not opportunities:
        plan.append("✅ **All files already meet the 85% coverage threshold!**")
        return "\n".join(plan)

    plan.append("## 🚀 High-Priority Files (Biggest Impact)")
    plan.append("")

    for i, opportunity in enumerate(opportunities[:5], 1):
        filename = opportunity["filename"]
        current = opportunity["current_coverage"]
        needed = opportunity["additional_lines_needed"]
        missing_lines = opportunity["missing_lines"]

        plan.append(f"### {i}. `{filename}`")
        plan.append(f"- **Current Coverage**: {current:.1f}%")
        plan.append(f"- **Additional Lines Needed**: {needed}")
        plan.append(
            f"- **Sample Missing Lines**: {', '.join(map(str, missing_lines[:5]))}"
        )

        suggestions = suggest_testing_strategies(filename)
        plan.append("- **Suggested Tests**:")
        for suggestion in suggestions[:3]:
            plan.append(f"  - {suggestion}")
        plan.append("")

    plan.append("## 📋 Implementation Strategy")
    plan.append("")
    plan.append("1. **Start with high-impact files** (listed above)")
    plan.append("2. **Focus on untested code paths** (use missing line numbers)")
    plan.append("3. **Add edge case tests** for error handling")
    plan.append("4. **Test integration points** between modules")
    plan.append("5. **Run coverage locally** to verify improvements")
    plan.append("")

    plan.append("## 🔧 Local Development Commands")
    plan.append("")
    plan.append("```bash")
    plan.append("# Run tests with coverage report")
    plan.append("python -m pytest tests/agent/ --cov=backend --cov-report=html")
    plan.append("")
    plan.append("# Open coverage report in browser")
    plan.append("# Windows: start htmlcov/index.html")
    plan.append("# macOS: open htmlcov/index.html")
    plan.append("# Linux: xdg-open htmlcov/index.html")
    plan.append("")
    plan.append("# Test specific file with coverage")
    plan.append(
        "python -m pytest tests/agent/test_specific.py --cov=agent/specific.py --cov-report=term-missing"
    )
    plan.append("```")
    plan.append("")

    plan.append("## 📊 Coverage Monitoring")
    plan.append("")
    plan.append("- **CI/CD**: Tests will fail if coverage drops below 85%")
    plan.append("- **PR Comments**: Coverage percentage shown on pull requests")
    plan.append("- **Artifacts**: Detailed HTML reports available in GitHub Actions")
    plan.append("")

    return "\n".join(plan)


def create_coverage_report_html(
    overall_coverage: float, categories: Dict[str, List[str]], opportunities: List[Dict]
) -> str:
    """Create an HTML coverage dashboard."""
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Coverage Analysis Dashboard</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 2rem; }}
        .metric {{ background: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 1rem 0; }}
        .critical {{ border-left: 4px solid #dc3545; }}
        .warning {{ border-left: 4px solid #ffc107; }}
        .success {{ border-left: 4px solid #28a745; }}
        .excellent {{ border-left: 4px solid #17a2b8; }}
        .file-list {{ max-height: 200px; overflow-y: auto; background: #f8f9fa; padding: 1rem; border-radius: 4px; }}
        h1, h2 {{ color: #343a40; }}
        .coverage-badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            color: white;
            font-weight: bold;
        }}
        .coverage-85 {{ background-color: #28a745; }}
        .coverage-70 {{ background-color: #ffc107; color: #212529; }}
        .coverage-low {{ background-color: #dc3545; }}
    </style>
</head>
<body>
    <h1>📊 Coverage Analysis Dashboard</h1>

    <div class="metric {'success' if overall_coverage >= 85 else 'warning' if overall_coverage >= 70 else 'critical'}">
        <h2>Overall Coverage: {overall_coverage:.1f}%</h2>
        <p>Target: 85% | Status: {'✅ Meets Target' if overall_coverage >= 85 else '⚠️ Below Target'}</p>
    </div>

    <h2>📁 Files by Coverage Level</h2>

    <div class="metric excellent">
        <h3>🏆 Excellent (≥95%): {len(categories['excellent'])} files</h3>
        <div class="file-list">
            {', '.join(categories['excellent']) if categories['excellent'] else 'None'}
        </div>
    </div>

    <div class="metric success">
        <h3>✅ Good (≥85%): {len(categories['good'])} files</h3>
        <div class="file-list">
            {', '.join(categories['good']) if categories['good'] else 'None'}
        </div>
    </div>

    <div class="metric warning">
        <h3>⚠️ Needs Work (70-84%): {len(categories['needs_work'])} files</h3>
        <div class="file-list">
            {', '.join(categories['needs_work']) if categories['needs_work'] else 'None'}
        </div>
    </div>

    <div class="metric critical">
        <h3>🚨 Critical (<70%): {len(categories['critical'])} files</h3>
        <div class="file-list">
            {', '.join(categories['critical']) if categories['critical'] else 'None'}
        </div>
    </div>

    <h2>🎯 Top Improvement Opportunities</h2>

    {' '.join([f'''
    <div class="metric warning">
        <h3>{i+1}. {opp['filename']}</h3>
        <p>Current: {opp['current_coverage']:.1f}% | Need {opp['additional_lines_needed']} more lines</p>
        <small>Missing lines: {', '.join(map(str, opp['missing_lines'][:10]))}</small>
    </div>
    ''' for i, opp in enumerate(opportunities[:5])]) if opportunities else '<p>No improvements needed - all files meet target!</p>'}

    <h2>🔗 Next Steps</h2>
    <ul>
        <li>Focus on critical and needs-work files first</li>
        <li>Use <code>htmlcov/index.html</code> for detailed line-by-line coverage</li>
        <li>Add tests for missing lines identified above</li>
        <li>Run <code>python -m pytest --cov=backend --cov-report=html</code> locally</li>
    </ul>

    <hr>
    <p><small>Generated by coverage analysis script | Target: 85% | Current: {overall_coverage:.1f}%</small></p>
</body>
</html>
"""
    return html


def main():
    """Main coverage analysis function."""
    print("🔍 Running Coverage Analysis...")
    print("=" * 60)

    # Run coverage analysis
    overall_coverage, coverage_data = run_coverage_analysis()

    if not coverage_data:
        print("❌ Could not generate coverage data. Ensure pytest-cov is installed.")
        return 1

    # Categorize files
    categories = categorize_files_by_coverage(coverage_data)
    opportunities = identify_improvement_opportunities(coverage_data)

    # Print summary
    print(f"📊 **Overall Coverage**: {overall_coverage:.1f}%")
    print("🎯 **Target**: 85%")
    print(
        f"📈 **Status**: {'✅ MEETS TARGET' if overall_coverage >= 85 else '⚠️ BELOW TARGET'}"
    )
    print()

    print("📁 **Files by Coverage Level**:")
    print(f"  🏆 Excellent (≥95%): {len(categories['excellent'])} files")
    print(f"  ✅ Good (≥85%): {len(categories['good'])} files")
    print(f"  ⚠️ Needs Work (70-84%): {len(categories['needs_work'])} files")
    print(f"  🚨 Critical (<70%): {len(categories['critical'])} files")
    print()

    if opportunities:
        print("🎯 **Top 3 Improvement Opportunities**:")
        for i, opp in enumerate(opportunities[:3], 1):
            print(
                f"  {i}. {opp['filename']} ({opp['current_coverage']:.1f}% - need {opp['additional_lines_needed']} lines)"
            )
        print()

    # Generate improvement plan
    improvement_plan = generate_improvement_plan(opportunities)

    # Write improvement plan to file
    with open("coverage_improvement_plan.md", "w") as f:
        f.write(improvement_plan)
    print("📝 **Improvement plan** written to: coverage_improvement_plan.md")

    # Generate HTML dashboard
    html_dashboard = create_coverage_report_html(
        overall_coverage, categories, opportunities
    )
    with open("coverage_dashboard.html", "w") as f:
        f.write(html_dashboard)
    print("📊 **Coverage dashboard** written to: coverage_dashboard.html")

    print()
    print("🔧 **Next Steps**:")
    print("  1. Review coverage_improvement_plan.md for detailed guidance")
    print("  2. Open coverage_dashboard.html for visual overview")
    print("  3. Open htmlcov/index.html for line-by-line coverage details")
    print(
        "  4. Run tests locally with: python -m pytest --cov=backend --cov-report=html"
    )

    # Return appropriate exit code
    return 0 if overall_coverage >= 85 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
from pathlib import Path

# Update test metrics in README.md and docs, and (optionally) scaffold an OpenSpec change.
# Usage (PowerShell):
#   python scripts/update_test_metrics.py            # runs pytest, updates files, dry-run by default
#   python scripts/update_test_metrics.py --apply    # apply changes to files
#   python scripts/update_test_metrics.py --skip-pytest --passed 691 --skipped 2 --duration "141.90s" --date 2025-10-15 --apply
# Notes:
#   - Cross-platform Python script; prefers explicit flags for CI
#   - When --apply is omitted, changes are printed (dry-run)
#   - When --scaffold-openspec is provided, creates a compliant OpenSpec change directory


REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"
DOC_TEST_RESULTS = REPO_ROOT / "docs" / "TEST_RESULTS_OCTOBER_2025.md"
DOC_SYSTEM_STATUS = REPO_ROOT / "docs" / "SYSTEM_STATUS_OCTOBER_2025.md"
OPEN_SPEC_CHANGES = REPO_ROOT / "openspec" / "changes"


def make_benchmark_table(bench: dict) -> str:
    if not bench:
        return "No benchmark metrics available."
    table = [
        "| Benchmark | Min | Max | Mean | Stddev | Rounds |",
        "|-----------|-----|-----|------|--------|--------|",
    ]
    table.append(
        f"| {bench.get('name', 'N/A')} | {bench.get('min', 'N/A')} | {bench.get('max', 'N/A')} | {bench.get('mean', 'N/A')} | {bench.get('stddev', 'N/A')} | {bench.get('rounds', 'N/A')} |"
    )
    return "\n".join(table)


def insert_benchmark_table(text, bench_table):
    # Remove any existing Benchmark Metrics section to prevent duplicates
    text = re.sub(
        r"### Benchmark Metrics\n\|.*?\n\|.*?\n(?:\|.*?\n)*\n*",
        "",
        text,
        flags=re.MULTILINE,
    )
    # Prefer to insert after Summary Statistics if present
    summary_match = re.search(
        r"(### Summary Statistics \(Last 10 Runs\)[\s\S]*?)(?=\n##|\Z)", text
    )
    if summary_match:
        insert_pos = summary_match.end(1)
        return (
            text[:insert_pos]
            + "\n\n### Benchmark Metrics\n"
            + bench_table
            + "\n\n"
            + text[insert_pos:]
        )
    # Fallback: insert after Recent Test Runs
    recent_runs_match = re.search(r"(### Recent Test Runs\n(?:.*?\n)+)\n", text)
    if recent_runs_match:
        insert_pos = recent_runs_match.end(1)
        return (
            text[:insert_pos]
            + "\n### Benchmark Metrics\n"
            + bench_table
            + "\n\n"
            + text[insert_pos:]
        )
    # Last fallback: append at end
    return text + "\n### Benchmark Metrics\n" + bench_table + "\n"


def run_pytest() -> tuple[int, int, int, str]:
    # Run pytest -q and parse (passed, skipped, failed, duration_str).
    proc = subprocess.run(
        ["python", "-m", "pytest", "-q"], capture_output=True, text=True, cwd=REPO_ROOT
    )
    out = proc.stdout + "\n" + proc.stderr

    # Look for summary with failures: "684 passed, 2 failed, 1 skipped in 141.90s"
    m = re.search(
        r"(\d+) passed(?:,\s*(\d+) failed)?(?:,\s*(\d+) skipped)?.*? in ([0-9.]+s)", out
    )
    if not m:
        # Fallback: handle case with only passed tests
        m = re.search(r"(\d+) passed.*? in ([0-9.]+s)", out)
        if not m:
            raise RuntimeError("Could not parse pytest summary")
        passed = int(m.group(1))
        failed = 0
        skipped = 0
        duration = m.group(2)
    else:
        passed = int(m.group(1))
        failed = int(m.group(2)) if m.group(2) else 0
        skipped = int(m.group(3)) if m.group(3) else 0
        duration = m.group(4)

    return passed, skipped, failed, duration


# --- Metrics Extraction Logic ---
def get_coverage() -> str:
    # Parse code coverage percentage from htmlcov/index.html.
    cov_file = REPO_ROOT / "htmlcov" / "index.html"
    if not cov_file.exists():
        print("[Warning] Coverage file not found at htmlcov/index.html")
        return "N/A"
    text = cov_file.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r'<span class="pc_cov">(\d+)%</span>', text)
    if m:
        return m.group(1) + "%"
    # Try alternative pattern
    m = re.search(r"(\d+)%\s+coverage", text, re.IGNORECASE)
    if m:
        return m.group(1) + "%"
    print("[Warning] Could not parse coverage percentage from HTML")
    return "N/A"


def get_benchmark_metrics() -> dict:
    # Extract benchmark metrics from pytest-benchmark results if available.
    import json

    bench_dir = REPO_ROOT / ".benchmarks" / "latest"
    results_file = bench_dir / "results.json"
    if not results_file.exists():
        return {}
    try:
        data = json.loads(results_file.read_text(encoding="utf-8"))
        # Find first benchmark entry
        if "benchmarks" in data and data["benchmarks"]:
            bm = data["benchmarks"][0]
            stats = bm.get("stats", {})
            return {
                "min": (
                    f"{stats.get('min', 0.0):.4f}s"
                    if isinstance(stats.get("min"), (int, float))
                    else "N/A"
                ),
                "max": (
                    f"{stats.get('max', 0.0):.4f}s"
                    if isinstance(stats.get("max"), (int, float))
                    else "N/A"
                ),
                "mean": (
                    f"{stats.get('mean', 0.0):.4f}s"
                    if isinstance(stats.get("mean"), (int, float))
                    else "N/A"
                ),
                "stddev": (
                    f"{stats.get('stddev', 0.0):.4f}s"
                    if isinstance(stats.get("stddev"), (int, float))
                    else "N/A"
                ),
                "rounds": bm.get("rounds", "N/A"),
                "name": bm.get("fullname", bm.get("name", "N/A")),
            }
    except Exception as e:
        print(f"[Warning] Could not parse benchmark metrics: {e}")
        return {}
    return {}


def replace_readme_metrics(
    text: str,
    passed: int,
    skipped: int,
    failed: int,
    date_str: str,
    duration: str,
    coverage: str,
) -> str:
    # ...existing code...
    text = re.sub(
        r"\[!\[Tests\]\(https://img.shields.io/badge/tests-[^)]+\)\]",
        f"[![Tests](https://img.shields.io/badge/tests-{passed}%20passed%20%7C%20{skipped}%20skipped-brightgreen)]",
        text,
        count=1,
    )
    # ...existing code...
    text = re.sub(
        r"Latest test run \(.*?\): .*?passed, .*?skipped, .*? failed",
        f"Latest test run ({date_str}): {passed} passed, {skipped} skipped, {failed} failed",
        text,
        count=1,
    )
    text = re.sub(
        r"#### \*\*Comprehensive Test Results \(.*?\)\*\*",
        f"#### **Comprehensive Test Results ({date_str})**",
        text,
        count=1,
    )
    text = re.sub(
        r"\| \*\*📊 TOTAL\*\*\s*\|\s*\*\*\d+\*\*",
        f"| **📊 TOTAL**                  | **{passed}**",
        text,
        count=1,
    )
    text = re.sub(
        r"#### \*\*Latest Test Run Statistics \(.*?\)\*\*",
        f"#### **Latest Test Run Statistics ({date_str})**",
        text,
        count=1,
    )
    # Compute success rate on executed tests (exclude skipped)
    executed = max(passed + failed, 0)
    success_rate = f"{(passed / executed * 100):.1f}%" if executed else "N/A"
    text = re.sub(
        r"\*\*Success Rate\*\*:[^\n]+",
        f"**Success Rate**: {success_rate} pass ({passed} passed, {failed} failed, {skipped} skipped)",
        text,
        count=1,
    )
    text = re.sub(
        r"\*\*Total Tests\*\*:[^\n]+",
        f"**Total Tests**: {passed + skipped + failed} collected (includes skipped and failed)",
        text,
        count=1,
    )
    text = re.sub(
        r"\*\*Execution Time\*\*:[^\n]+",
        f"**Execution Time**: ~{duration} on Windows (Python 3.14)",
        text,
        count=1,
    )
    # Add or update coverage line
    if "**Coverage**:" in text:
        text = re.sub(
            r"\*\*Coverage\*\*:[^\n]+", f"**Coverage**: {coverage}", text, count=1
        )
    else:
        exec_time_match = re.search(r"(\*\*Execution Time\*\*:[^\n]+\n)", text)
        if exec_time_match:
            insert_pos = exec_time_match.end(1)
            text = text[:insert_pos] + f"**Coverage**: {coverage}\n" + text[insert_pos:]
    return text


def replace_test_results_doc(
    text: str,
    date_str: str,
    passed: int,
    skipped: int,
    failed: int,
    duration: str,
    coverage: str,
) -> str:
    text = re.sub(
        r"# 🏆 Comprehensive Test Results - .*",
        f"# 🏆 Comprehensive Test Results - {date_str}",
        text,
        count=1,
    )
    executed = max(passed + failed, 0)
    success_rate = f"{(passed / executed * 100):.1f}%" if executed else "N/A"
    text = re.sub(
        r"\*\*Test Results\*\*: \*\*.*\*\*",
        f"**Test Results**: **{passed} passed, {skipped} skipped, {failed} failed ({success_rate} success rate)**",
        text,
        count=1,
    )
    text = re.sub(
        r"\*\*Execution Time\*\*: .*",
        f"**Execution Time**: ~{duration} on Windows (Python 3.14)",
        text,
        count=1,
    )
    # Add or update coverage line
    if "**Coverage**:" in text:
        text = re.sub(
            r"\*\*Coverage\*\*:[^\n]+", f"**Coverage**: {coverage}", text, count=1
        )
    else:
        exec_time_match = re.search(r"(\*\*Execution Time\*\*:.*\n)", text)
        if exec_time_match:
            insert_pos = exec_time_match.end(1)
            text = text[:insert_pos] + f"**Coverage**: {coverage}\n" + text[insert_pos:]
    return text


def replace_system_status_doc(
    text: str, date_str: str, passed: int, skipped: int, failed: int
) -> str:
    text = re.sub(
        r"\*\*Test Results\*\*: .*",
        (
            f"**Test Results**: {passed} passed, {skipped} skipped, {failed} failed "
            + ("(100% success rate) 🏆" if failed == 0 else "(issues detected) ❗")
        ),
        text,
        count=1,
    )
    text = re.sub(
        r"\*\*Latest Update\*\*: .*",
        f"**Latest Update**: {date_str} - Automated test metrics update",
        text,
        count=1,
    )
    return text


def scaffold_openspec_change(
    date_str: str, passed: int, skipped: int, duration: str
) -> None:
    change_id = f"update-doc-docs-test-results-auto-{date_str.lower()}"
    change_dir = OPEN_SPEC_CHANGES / change_id
    change_dir.mkdir(parents=True, exist_ok=True)

    proposal = (
        f"# Change Proposal: {change_id}\n\n"
        f"## Why\n\n"
        f"We keep docs/TEST_RESULTS_OCTOBER_2025.md in sync with the latest full-suite run.\n\n"
        f"Capability: project-documentation\n\n"
        f"## What Changes\n\n"
        f"- Update test counts and runtime in README and docs\n"
        f"- Align dates to {date_str}\n"
        f"- Ensure OpenSpec compliance and governance wording\n\n"
        f"## Impact\n\n"
        f"- Consistent and accurate project status reporting\n"
        f"- Documentation-only change, no code risk\n"
        f"- OpenSpec governance maintained"
    )
    (change_dir / "proposal.md").write_text(proposal, encoding="utf-8")

    tasks = (
        f"# Tasks: {change_id}\n\n"
        f"## 1. Implementation\n\n"
        f"- [ ] 1.1 Update docs/TEST_RESULTS_OCTOBER_2025.md\n"
        f"- [ ] 1.2 Update README.md badges and statistics\n"
        f"- [ ] 1.3 Update docs/SYSTEM_STATUS_OCTOBER_2025.md\n"
        f"- [ ] 1.4 Verify markdown lint (MD022/MD029/MD032)\n\n"
        f"## 2. Validation\n\n"
        f"- [ ] 2.1 Run OpenSpec tests\n"
        f"- [ ] 2.2 Verify spec delta sections present\n\n"
        f"## 3. Governance\n\n"
        f"- [ ] 3.1 Capability is project-documentation\n"
        f"- [ ] 3.2 Spec delta contains ADDED Requirements and scenarios\n\n"
        f"## 4. Validation Command\n\n"
        f"openspec validate {change_id} --strict"
    )
    (change_dir / "tasks.md").write_text(tasks, encoding="utf-8")

    spec_dir = change_dir / "specs" / "project-documentation"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec = (
        f"# Spec Delta: project-documentation / {change_id}\n\n"
        f"This change updates documentation under OpenSpec governance. Material changes require proposals and tasks in openspec/changes.\n\n"
        f"## ADDED Requirements\n\n"
        f"### Requirement: Maintain current test result summaries\n\n"
        f"The system SHALL maintain current and accurate test result summaries across governed documents.\n\n"
        f"- Capability: project-documentation\n"
        f"- Artifact: docs/TEST_RESULTS_OCTOBER_2025.md\n\n"
        f"#### Scenario: Documentation reflects latest test suite execution\n\n"
        f"- GIVEN the full test suite has been run\n"
        f"- WHEN counts or timing change (e.g., {passed} passed, {skipped} skipped on {date_str})\n"
        f"- THEN docs/TEST_RESULTS_OCTOBER_2025.md MUST reflect the latest results within 24 hours\n\n"
        f"### Requirement: Consistency across status pages\n\n"
        f"All listed artifacts SHALL remain consistent with respect to the latest test metrics and dates.\n\n"
        f"- Capability: project-documentation\n"
        f"- Artifact: README.md, docs/SYSTEM_STATUS_OCTOBER_2025.md\n\n"
        f"#### Scenario: Cross-document consistency\n\n"
        f"- GIVEN README, system status, and test results pages\n"
        f"- WHEN one document is updated with new test metrics\n"
        f"- THEN the other documents MUST be updated to ensure aligned counts and dates"
    )
    (spec_dir / "spec.md").write_text(spec, encoding="utf-8")


# --- Execution Time Trend & History Logic ---
PREV_METRICS_FILE = REPO_ROOT / "docs" / ".test_metrics_prev.json"
HISTORY_FILE = REPO_ROOT / "docs" / ".test_metrics_history.json"


def load_prev_metrics():
    if PREV_METRICS_FILE.exists():
        try:
            data = json.loads(PREV_METRICS_FILE.read_text(encoding="utf-8"))
            return data.get("duration"), data.get("date"), data.get("coverage")
        except Exception:
            return None, None, None
    return None, None, None


def save_current_metrics(duration, date_str, coverage):
    data = {"duration": duration, "date": date_str, "coverage": coverage}
    PREV_METRICS_FILE.write_text(json.dumps(data), encoding="utf-8")


def get_duration_seconds(duration_str):
    # Converts "148.15s" to float seconds
    try:
        return float(duration_str.rstrip("s"))
    except Exception:
        return None


def make_trend_summary(prev_duration, prev_date, curr_duration, curr_date):
    prev_sec = get_duration_seconds(prev_duration) if prev_duration else None
    curr_sec = get_duration_seconds(curr_duration)
    if prev_sec is None or curr_sec is None:
        return "No previous run data available."
    delta = curr_sec - prev_sec
    pct = (delta / prev_sec) * 100 if prev_sec else 0
    if abs(delta) < 0.01:
        trend = "No significant change."
    elif delta < 0:
        trend = f"Improved by {-delta:.2f}s ({-pct:.1f}%) since {prev_date}."
    else:
        trend = f"Regressed by {delta:.2f}s (+{pct:.1f}%) since {prev_date}."
    return f"**Execution Time Trend**: {trend}"


def make_coverage_trend(prev_coverage, prev_date, curr_coverage, curr_date):
    # Parse coverage percentages
    def parse_coverage(cov_str):
        if not cov_str or cov_str == "N/A":
            return None
        try:
            return int(cov_str.rstrip("%"))
        except (ValueError, AttributeError):
            return None

    prev_pct = parse_coverage(prev_coverage) if prev_coverage else None
    curr_pct = parse_coverage(curr_coverage)

    if prev_pct is None or curr_pct is None:
        return None

    delta = curr_pct - prev_pct
    if delta == 0:
        trend = "No change in coverage."
    elif delta > 0:
        trend = f"Improved by {delta}% since {prev_date}. 📈"
    else:
        trend = f"Decreased by {-delta}% since {prev_date}. 📉"
    return f"**Coverage Trend**: {trend}"


def insert_trend_summary(text, trend_summary):
    # Remove any existing trend summaries to prevent duplicates
    text = re.sub(r"\*\*Execution Time Trend\*\*:.*?\n", "", text)
    text = re.sub(r"\*\*Coverage Trend\*\*:.*?\n", "", text)

    # Insert after Execution Time line (or Coverage line if adding coverage trend)
    if "Coverage Trend" in trend_summary:
        # Insert after Coverage line
        coverage_match = re.search(r"(\*\*Coverage\*\*:[^\n]+\n)", text)
        if coverage_match:
            insert_pos = coverage_match.end(1)
            return text[:insert_pos] + trend_summary + "\n" + text[insert_pos:]
    else:
        # Insert after Execution Time line
        exec_time_match = re.search(r"(\*\*Execution Time\*\*:[^\n]+\n)", text)
        if exec_time_match:
            insert_pos = exec_time_match.end(1)
            return text[:insert_pos] + trend_summary + "\n" + text[insert_pos:]

    return text + "\n" + trend_summary


def load_history():
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_history(history):
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")


def append_run_to_history(
    date_str, passed, skipped, failed, duration, coverage, max_entries=10
):
    history = load_history()
    entry = {
        "date": date_str,
        "passed": passed,
        "skipped": skipped,
        "failed": failed,
        "duration": duration,
        "coverage": coverage,
    }
    # Remove duplicate date if present
    history = [h for h in history if h["date"] != date_str]
    history.append(entry)
    # Keep only last N
    history = history[-max_entries:]
    save_history(history)
    return history


def make_history_table(history):
    if not history:
        return "No recent test run history available."
    table = [
        "| Date | Passed | Skipped | Failed | Duration | Coverage |",
        "|------|--------|---------|--------|----------|----------|",
    ]
    for h in reversed(history):
        failed = h.get("failed", 0)
        status_emoji = "✅" if failed == 0 else "❌"
        table.append(
            f"| {h['date']} {status_emoji} | {h['passed']} | {h['skipped']} | {failed} | {h['duration']} | {h['coverage']} |"
        )
    return "\n".join(table)


def make_summary_stats(history):
    """Generate summary statistics from test history."""
    if not history or len(history) < 2:
        return None

    # Extract numeric values
    durations = []
    coverages = []
    for h in history:
        dur_sec = get_duration_seconds(h.get("duration", ""))
        if dur_sec:
            durations.append(dur_sec)
        cov_str = h.get("coverage", "N/A")
        if cov_str and cov_str != "N/A":
            try:
                coverages.append(int(cov_str.rstrip("%")))
            except (ValueError, AttributeError):
                pass

    stats = []
    if durations:
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        stats.append(
            f"**Average Execution Time**: {avg_duration:.2f}s (min: {min_duration:.2f}s, max: {max_duration:.2f}s)"
        )

    if coverages:
        avg_coverage = sum(coverages) / len(coverages)
        min_coverage = min(coverages)
        max_coverage = max(coverages)
        stats.append(
            f"**Average Coverage**: {avg_coverage:.1f}% (min: {min_coverage}%, max: {max_coverage}%)"
        )

    if stats:
        return "\n".join(["### Summary Statistics (Last 10 Runs)"] + [""] + stats)
    return None


def insert_history_table(text, history_table):
    # Remove any existing "Recent Test Runs" sections to prevent duplicates
    text = re.sub(
        r"### Recent Test Runs\n\|.*?\n\|.*?\n(?:\|.*?\n)*\n*",
        "",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"### Summary Statistics \(Last 10 Runs\)\n(?:.*?\n)*?(?=\n##|\Z)",
        "",
        text,
        flags=re.MULTILINE,
    )

    # Insert after Executive Summary
    summary_match = re.search(r"(## 📊 Executive Summary\n.*?\n---\n)", text, re.DOTALL)
    if summary_match:
        insert_pos = summary_match.end(1)
        return (
            text[:insert_pos]
            + "\n### Recent Test Runs\n"
            + history_table
            + "\n\n"
            + text[insert_pos:]
        )
    return text + "\n### Recent Test Runs\n" + history_table + "\n"


def insert_summary_stats(text, summary_stats_section):
    if not summary_stats_section:
        return text
    # Remove existing summary stats to prevent duplicates
    text = re.sub(
        r"### Summary Statistics \(Last 10 Runs\)\n(?:.*?\n)*?(?=\n##|\Z)",
        "",
        text,
        flags=re.MULTILINE,
    )
    # Insert after Recent Test Runs section
    recent_match = re.search(
        r"(### Recent Test Runs\n\|.*?\n\|.*?\n(?:\|.*?\n)+)", text, re.DOTALL
    )
    if recent_match:
        insert_pos = recent_match.end(1)
        return (
            text[:insert_pos]
            + "\n\n"
            + summary_stats_section
            + "\n\n"
            + text[insert_pos:]
        )
    return text + "\n" + summary_stats_section + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply changes to files")
    parser.add_argument(
        "--skip-pytest",
        action="store_true",
        help="Do not run pytest; use provided counts",
    )
    parser.add_argument("--passed", type=int, default=None)
    parser.add_argument("--skipped", type=int, default=None)
    parser.add_argument("--failed", type=int, default=0, help="Number of failed tests")
    parser.add_argument("--duration", type=str, default=None)
    parser.add_argument(
        "--date", type=str, default=None, help="YYYY-MM-DD (defaults to today)"
    )
    parser.add_argument(
        "--scaffold-openspec",
        action="store_true",
        help="Create an OpenSpec change directory for this update",
    )
    parser.add_argument(
        "--coverage", type=str, default=None, help="Coverage percentage (optional)"
    )

    args = parser.parse_args()

    today = dt.date.today()
    date_str = args.date or today.strftime("%Y-%m-%d")

    if args.skip_pytest:
        if args.passed is None or args.duration is None:
            raise SystemExit("--skip-pytest requires --passed and --duration")
        passed = args.passed
        skipped = int(args.skipped or 0)
        failed = int(args.failed or 0)
        duration = args.duration
        coverage = args.coverage if args.coverage is not None else get_coverage()
    else:
        passed, skipped, failed, duration = run_pytest()
        coverage = get_coverage()

    # --- Load previous metrics and compute trend ---
    prev_duration, prev_date, prev_coverage = load_prev_metrics()
    trend_summary = make_trend_summary(prev_duration, prev_date, duration, date_str)
    coverage_trend = make_coverage_trend(prev_coverage, prev_date, coverage, date_str)

    # --- Update history and create table ---
    history = append_run_to_history(
        date_str, passed, skipped, failed, duration, coverage
    )
    history_table = make_history_table(history)
    summary_stats = make_summary_stats(history)

    # Update README
    readme_text = README.read_text(encoding="utf-8")
    new_readme = replace_readme_metrics(
        readme_text, passed, skipped, failed, date_str, duration, coverage
    )

    # Update test results doc
    test_results_text = DOC_TEST_RESULTS.read_text(encoding="utf-8")
    new_test_results = replace_test_results_doc(
        test_results_text, date_str, passed, skipped, failed, duration, coverage
    )
    new_test_results = insert_trend_summary(new_test_results, trend_summary)
    if coverage_trend:
        new_test_results = insert_trend_summary(new_test_results, coverage_trend)
    new_test_results = insert_history_table(new_test_results, history_table)
    if summary_stats:
        new_test_results = insert_summary_stats(new_test_results, summary_stats)
    # Add benchmark metrics table
    bench_metrics = get_benchmark_metrics()
    bench_table = make_benchmark_table(bench_metrics)
    new_test_results = insert_benchmark_table(new_test_results, bench_table)

    # Update system status doc
    sys_status_text = DOC_SYSTEM_STATUS.read_text(encoding="utf-8")
    new_sys_status = replace_system_status_doc(
        sys_status_text, date_str, passed, skipped, failed
    )

    if args.apply:
        README.write_text(new_readme, encoding="utf-8")
        DOC_TEST_RESULTS.write_text(new_test_results, encoding="utf-8")
        DOC_SYSTEM_STATUS.write_text(new_sys_status, encoding="utf-8")
        save_current_metrics(duration, date_str, coverage)
        # Always create OpenSpec change directory for governance
        scaffold_openspec_change(date_str, passed, skipped, duration)
        # Post-update: Validate OpenSpec compliance
        validate_cmd = f"openspec validate update-doc-docs-test-results-auto-{date_str.lower()} --strict"
        try:
            result = subprocess.run(
                validate_cmd, shell=True, cwd=REPO_ROOT, capture_output=True, text=True
            )
            print(result.stdout)
            if result.returncode != 0:
                print("[OpenSpec Validation] FAILED:")
                print(result.stderr)
            else:
                print("[OpenSpec Validation] PASSED.")
        except Exception as e:
            print(f"[OpenSpec Validation] Error: {e}")
        print(
            f"Updated docs with {passed} passed, {skipped} skipped, {failed} failed in {duration} on {date_str}."
        )
    else:
        print("--- README preview (first 5 lines) ---")
        print("\n".join(new_readme.splitlines()[:5]))
        print("--- TEST RESULTS preview (first 5 lines) ---")
        print("\n".join(new_test_results.splitlines()[:5]))
        print("--- SYSTEM STATUS preview (first 5 lines) ---")
        print("\n".join(new_sys_status.splitlines()[:5]))


if __name__ == "__main__":
    main()

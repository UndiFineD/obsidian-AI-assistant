#!/usr/bin/env python3
"""
Interactive Lane Selector - Rich Terminal UI for Workflow Lane Selection

Provides an interactive command-line interface for users to:
1. Review change scope and statistics
2. Get lane recommendations
3. View suggested lane benefits
4. Confirm and execute workflow in selected lane
5. Track execution with real-time progress indicators

Features:
- Rich terminal UI with colors and formatting
- Intelligent lane recommendation based on change analysis
- Visual decision trees and statistics
- Confidence scoring for recommendations
- Confirmation dialogs before execution
- Real-time progress tracking
- Success/failure summaries

Usage:
    python scripts/interactive_lane_selector.py [options]

Options:
    --auto-confirm      Skip confirmation dialogs (development/CI mode)
    --json              Output results as JSON
    --verbose           Enable verbose logging
    --lane LANE         Skip selection and use specific lane
    --dry-run           Show what would happen without executing
    --project-root ROOT Override project root path
"""

import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import argparse
import logging
from collections import Counter

# Try to import rich for better terminal UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.text import Text
    from rich.tree import Tree
    from rich import box

    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

console = Console() if HAS_RICH else None


class LaneType(Enum):
    """Workflow lanes available."""

    DOCS = "docs"
    STANDARD = "standard"
    HEAVY = "heavy"


class RecommendationConfidence(Enum):
    """Confidence level for lane recommendations."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ChangeStatistics:
    """Statistics about changes in the repository."""

    total_files: int
    changed_files: int
    file_types: Dict[str, int]
    docs_changes: int
    code_changes: int
    config_changes: int
    test_changes: int
    size_bytes: int

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class LaneRecommendation:
    """Lane recommendation with reasoning."""

    recommended_lane: LaneType
    confidence: RecommendationConfidence
    reasoning: str
    alternative_lanes: List[Tuple[LaneType, str]]
    estimated_duration: int  # seconds
    sla_target: int  # seconds
    key_factors: List[str]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = asdict(self)
        data["recommended_lane"] = self.recommended_lane.value
        data["confidence"] = self.confidence.value
        data["alternative_lanes"] = [
            (lane.value, reason) for lane, reason in self.alternative_lanes
        ]
        return data


@dataclass
class ExecutionResult:
    """Result of workflow execution."""

    success: bool
    lane: LaneType
    duration: int
    timestamp: str
    output: str
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = asdict(self)
        data["lane"] = self.lane.value
        return data


class ChangeAnalyzer:
    """Analyzes repository changes to generate statistics."""

    def __init__(self, project_root: Path = None):
        """Initialize analyzer."""
        self.project_root = project_root or Path.cwd()

    def analyze_changes(self) -> ChangeStatistics:
        """
        Analyze git changes and return statistics.

        Returns:
            ChangeStatistics object with change metrics
        """
        try:
            # Get list of changed files
            result = subprocess.run(
                ["git", "diff", "--name-only", "main...HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10,
            )

            changed_files = (
                result.stdout.strip().split("\n") if result.stdout.strip() else []
            )

            # Also include staged changes
            result_staged = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10,
            )

            staged_files = (
                result_staged.stdout.strip().split("\n")
                if result_staged.stdout.strip()
                else []
            )
            all_changed = list(set(changed_files + staged_files))
            all_changed = [f for f in all_changed if f]  # Remove empty strings

            # Categorize files by type
            file_types = Counter()
            docs_changes = 0
            code_changes = 0
            config_changes = 0
            test_changes = 0
            size_bytes = 0

            for file_path in all_changed:
                full_path = self.project_root / file_path

                # Count file type
                if file_path.endswith((".md", ".txt", ".rst", ".adoc")):
                    docs_changes += 1
                    file_types["docs"] += 1
                elif file_path.endswith(
                    (".test.py", ".spec.py", "test_", "_test.py", "/tests/")
                ):
                    test_changes += 1
                    file_types["tests"] += 1
                elif file_path.endswith(
                    (".yaml", ".yml", ".json", ".toml", ".cfg", ".conf", ".ini")
                ):
                    config_changes += 1
                    file_types["config"] += 1
                else:
                    code_changes += 1
                    if file_path.endswith(".py"):
                        file_types["python"] += 1
                    elif file_path.endswith((".js", ".ts", ".jsx", ".tsx")):
                        file_types["javascript"] += 1
                    elif file_path.endswith((".go", ".rs", ".c", ".cpp", ".java")):
                        file_types["compiled"] += 1
                    else:
                        file_types["other"] += 1

                # Try to get file size
                try:
                    if full_path.exists():
                        size_bytes += full_path.stat().st_size
                except Exception as e:
                    logger.debug(f"Could not get size for {file_path}: {e}")

            return ChangeStatistics(
                total_files=len(all_changed),
                changed_files=len(all_changed),
                file_types=dict(file_types),
                docs_changes=docs_changes,
                code_changes=code_changes,
                config_changes=config_changes,
                test_changes=test_changes,
                size_bytes=size_bytes,
            )

        except Exception as e:
            logger.error(f"Error analyzing changes: {e}")
            # Return default stats if analysis fails
            return ChangeStatistics(
                total_files=0,
                changed_files=0,
                file_types={},
                docs_changes=0,
                code_changes=0,
                config_changes=0,
                test_changes=0,
                size_bytes=0,
            )

    def get_git_branch(self) -> str:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip()
        except Exception:
            return "unknown"

    def get_commit_count(self) -> int:
        """Get number of commits since main."""
        try:
            result = subprocess.run(
                ["git", "rev-list", "--count", "main...HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
        except Exception:
            return 0


class LaneRecommender:
    """Recommends appropriate workflow lane based on change analysis."""

    def __init__(self, stats: ChangeStatistics):
        """Initialize recommender with change statistics."""
        self.stats = stats

    def recommend(self) -> LaneRecommendation:
        """
        Recommend appropriate lane based on change statistics.

        Lane Selection Logic:
        - DOCS: Only documentation changes, ≤2 files
        - STANDARD: Mixed changes, ≤10 files, includes tests
        - HEAVY: Large changes, >10 files, significant code changes

        Returns:
            LaneRecommendation with reasoning and confidence
        """
        # Extract metrics
        total = self.stats.total_files
        docs = self.stats.docs_changes
        code = self.stats.code_changes
        tests = self.stats.test_changes
        config = self.stats.config_changes

        # Calculate percentages
        docs_pct = (docs / total * 100) if total > 0 else 0
        code_pct = (code / total * 100) if total > 0 else 0
        test_pct = (tests / total * 100) if total > 0 else 0

        key_factors = []

        # DOCS lane: Only documentation, minimal files
        if total <= 2 and docs_pct >= 90 and code == 0:
            return LaneRecommendation(
                recommended_lane=LaneType.DOCS,
                confidence=RecommendationConfidence.HIGH,
                reasoning="Pure documentation changes with minimal scope",
                alternative_lanes=[
                    (LaneType.STANDARD, "If documentation includes code examples"),
                ],
                estimated_duration=180,  # 3 minutes
                sla_target=300,  # 5 minutes
                key_factors=[
                    f"Only {total} file(s) changed",
                    f"{docs_pct:.0f}% documentation",
                    "No code changes",
                ],
            )

        # DOCS lane: Mostly docs, few files
        if total <= 5 and docs_pct >= 70 and code_pct <= 20:
            return LaneRecommendation(
                recommended_lane=LaneType.DOCS,
                confidence=RecommendationConfidence.MEDIUM,
                reasoning="Primarily documentation changes with minimal code",
                alternative_lanes=[
                    (LaneType.STANDARD, "If code validation needed"),
                ],
                estimated_duration=300,  # 5 minutes
                sla_target=300,
                key_factors=[
                    f"{total} files changed",
                    f"{docs_pct:.0f}% documentation",
                    f"{code_pct:.0f}% code",
                ],
            )

        # STANDARD lane: Mixed changes, moderate scope
        if total <= 10 and (tests > 0 or code_pct > 0):
            key_factors = [
                f"{total} files changed",
                f"{code_pct:.0f}% code changes",
                f"{test_pct:.0f}% test coverage",
            ]

            confidence = (
                RecommendationConfidence.HIGH
                if tests > 0
                else RecommendationConfidence.MEDIUM
            )

            return LaneRecommendation(
                recommended_lane=LaneType.STANDARD,
                confidence=confidence,
                reasoning="Moderate scope with mixed changes and test coverage",
                alternative_lanes=[
                    (LaneType.DOCS, "If mostly documentation"),
                    (LaneType.HEAVY, "If expecting longer execution"),
                ],
                estimated_duration=720,  # 12 minutes
                sla_target=900,  # 15 minutes
                key_factors=key_factors,
            )

        # HEAVY lane: Large scope or risky changes
        if total > 10 or code_pct > 50 or (code > 5 and tests == 0):
            key_factors = [
                f"{total} files changed",
                f"{code_pct:.0f}% code changes",
            ]

            if tests == 0 and code > 0:
                key_factors.append("⚠️  Code changes without test coverage")

            if config > 0:
                key_factors.append(f"{config} configuration file(s)")

            return LaneRecommendation(
                recommended_lane=LaneType.HEAVY,
                confidence=RecommendationConfidence.HIGH,
                reasoning="Large scope or risky changes requiring comprehensive validation",
                alternative_lanes=[
                    (LaneType.STANDARD, "If changes are lower-risk than expected"),
                ],
                estimated_duration=1200,  # 20 minutes
                sla_target=1200,  # 20 minutes
                key_factors=key_factors,
            )

        # Default to STANDARD
        return LaneRecommendation(
            recommended_lane=LaneType.STANDARD,
            confidence=RecommendationConfidence.MEDIUM,
            reasoning="Moderate complexity changes",
            alternative_lanes=[],
            estimated_duration=720,
            sla_target=900,
            key_factors=[f"{total} files changed"],
        )


class InteractiveLaneSelector:
    """Main interactive UI for lane selection."""

    def __init__(self, project_root: Optional[Path] = None, verbose: bool = False):
        """Initialize selector."""
        self.project_root = project_root or Path.cwd()
        self.verbose = verbose
        self.analyzer = ChangeAnalyzer(self.project_root)
        self.stats: Optional[ChangeStatistics] = None
        self.recommendation: Optional[LaneRecommendation] = None
        self.selected_lane: Optional[LaneType] = None

    def run(
        self,
        auto_confirm: bool = False,
        force_lane: Optional[str] = None,
        dry_run: bool = False,
        json_output: bool = False,
    ) -> ExecutionResult:
        """
        Run the interactive lane selector.

        Args:
            auto_confirm: Skip confirmation dialogs
            force_lane: Skip selection and use specific lane
            dry_run: Show what would happen without executing
            json_output: Output results as JSON

        Returns:
            ExecutionResult with execution details
        """
        start_time = datetime.now()

        try:
            # Step 1: Display welcome and analyze changes
            self._display_welcome()
            self._display_environment()

            # Step 2: Analyze changes
            logger.info("Analyzing repository changes...")
            self.stats = self.analyzer.analyze_changes()
            self._display_change_statistics()

            # Step 3: Get recommendation
            logger.info("Generating lane recommendation...")
            recommender = LaneRecommender(self.stats)
            self.recommendation = recommender.recommend()
            self._display_recommendation()

            # Step 4: Select lane
            if force_lane:
                self.selected_lane = LaneType(force_lane.lower())
                self._display_info(f"Using forced lane: {force_lane.upper()}")
            else:
                self.selected_lane = self._prompt_lane_selection()

            # Step 5: Display benefits and confirm
            self._display_lane_benefits()

            if not auto_confirm and not dry_run:
                if not self._prompt_confirmation():
                    return ExecutionResult(
                        success=False,
                        lane=self.selected_lane,
                        duration=int((datetime.now() - start_time).total_seconds()),
                        timestamp=start_time.isoformat(),
                        output="User cancelled execution",
                        error_message="Execution cancelled by user",
                    )

            # Step 6: Execute workflow
            if dry_run:
                self._display_info("DRY RUN MODE - Skipping execution")
                output = "Dry run completed successfully"
            else:
                self._display_execution_progress()
                output = self._execute_workflow()

            # Step 7: Display results
            duration = int((datetime.now() - start_time).total_seconds())
            self._display_success_summary(duration)

            result = ExecutionResult(
                success=True,
                lane=self.selected_lane,
                duration=duration,
                timestamp=start_time.isoformat(),
                output=output,
            )

            if json_output:
                console.print_json(data=result.to_dict()) if HAS_RICH else print(
                    json.dumps(result.to_dict(), indent=2)
                )

            return result

        except KeyboardInterrupt:
            duration = int((datetime.now() - start_time).total_seconds())
            self._display_error("User interrupted execution")
            return ExecutionResult(
                success=False,
                lane=self.selected_lane or LaneType.STANDARD,
                duration=duration,
                timestamp=start_time.isoformat(),
                output="",
                error_message="User interrupted execution",
            )
        except Exception as e:
            duration = int((datetime.now() - start_time).total_seconds())
            logger.exception("Error during execution")
            self._display_error(f"Execution error: {str(e)}")
            return ExecutionResult(
                success=False,
                lane=self.selected_lane or LaneType.STANDARD,
                duration=duration,
                timestamp=start_time.isoformat(),
                output="",
                error_message=str(e),
            )

    def _display_welcome(self):
        """Display welcome message."""
        if HAS_RICH:
            panel = Panel(
                "[bold cyan]🚀 Workflow Lane Selector[/bold cyan]\n"
                "Interactive tool for selecting the right workflow lane\n"
                "[dim]Press Ctrl+C to cancel at any time[/dim]",
                border_style="cyan",
            )
            console.print(panel)
        else:
            print("=" * 60)
            print("Workflow Lane Selector")
            print("=" * 60)

    def _display_environment(self):
        """Display environment information."""
        branch = self.analyzer.get_git_branch()
        commits = self.analyzer.get_commit_count()

        if HAS_RICH:
            table = Table(title="Environment", box=box.SIMPLE)
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            table.add_row("Branch", branch)
            table.add_row("Commits", str(commits))
            table.add_row("Project Root", str(self.project_root))
            console.print(table)
        else:
            print(f"\nBranch: {branch}")
            print(f"Commits: {commits}")
            print(f"Project Root: {self.project_root}\n")

    def _display_change_statistics(self):
        """Display change statistics."""
        if HAS_RICH:
            table = Table(title="Change Statistics", box=box.SIMPLE)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            table.add_row("Total Files", str(self.stats.total_files))
            table.add_row("Documentation", str(self.stats.docs_changes))
            table.add_row("Code", str(self.stats.code_changes))
            table.add_row("Tests", str(self.stats.test_changes))
            table.add_row("Configuration", str(self.stats.config_changes))
            table.add_row("Total Size", self._format_size(self.stats.size_bytes))
            console.print(table)
        else:
            print("\nChange Statistics:")
            print(f"  Files: {self.stats.total_files}")
            print(f"  Documentation: {self.stats.docs_changes}")
            print(f"  Code: {self.stats.code_changes}")
            print(f"  Tests: {self.stats.test_changes}")
            print(f"  Size: {self._format_size(self.stats.size_bytes)}\n")

    def _display_recommendation(self):
        """Display lane recommendation."""
        rec = self.recommendation
        confidence_color = {
            RecommendationConfidence.HIGH: "green",
            RecommendationConfidence.MEDIUM: "yellow",
            RecommendationConfidence.LOW: "red",
        }

        if HAS_RICH:
            color = confidence_color.get(rec.confidence, "white")
            panel = Panel(
                f"[bold {color}]{rec.recommended_lane.value.upper()} LANE[/bold {color}]\n\n"
                f"[dim]Confidence: {rec.confidence.value.upper()}[/dim]\n"
                f"{rec.reasoning}",
                title="Recommendation",
                border_style=color,
            )
            console.print(panel)

            # Display factors
            console.print("\n[bold cyan]Key Factors:[/bold cyan]")
            for factor in rec.key_factors:
                console.print(f"  • {factor}")
        else:
            print("\nRecommendation:")
            print(f"  Lane: {rec.recommended_lane.value.upper()}")
            print(f"  Confidence: {rec.confidence.value.upper()}")
            print(f"  Reason: {rec.reasoning}")
            print("  Factors:")
            for factor in rec.key_factors:
                print(f"    - {factor}")

    def _prompt_lane_selection(self) -> LaneType:
        """Prompt user to select lane."""
        if HAS_RICH:
            console.print("\n[bold]Select Lane:[/bold]")
            console.print("  1. [green]DOCS[/green] - Documentation changes")
            console.print(
                "  2. [yellow]STANDARD[/yellow] - Standard changes (recommended)"
            )
            console.print("  3. [red]HEAVY[/red] - Large/complex changes")

            while True:
                choice = console.input("\n[cyan]Enter choice (1-3)[/cyan]: ").strip()
                if choice == "1":
                    return LaneType.DOCS
                elif choice == "2":
                    return LaneType.STANDARD
                elif choice == "3":
                    return LaneType.HEAVY
                else:
                    console.print("[red]Invalid choice. Please enter 1, 2, or 3.[/red]")
        else:
            print("\nSelect Lane:")
            print("  1. DOCS - Documentation changes")
            print("  2. STANDARD - Standard changes (recommended)")
            print("  3. HEAVY - Large/complex changes")

            while True:
                choice = input("\nEnter choice (1-3): ").strip()
                if choice == "1":
                    return LaneType.DOCS
                elif choice == "2":
                    return LaneType.STANDARD
                elif choice == "3":
                    return LaneType.HEAVY
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")

    def _display_lane_benefits(self):
        """Display benefits of selected lane."""
        benefits = {
            LaneType.DOCS: [
                "Fast execution (<5 min)",
                "Minimal resource usage",
                "Documentation focus",
                "Quick feedback",
            ],
            LaneType.STANDARD: [
                "Balanced execution (15 min)",
                "Comprehensive checks",
                "Quality gate validation",
                "Standard CI/CD pipeline",
            ],
            LaneType.HEAVY: [
                "Thorough validation (20 min)",
                "Stress testing included",
                "Performance benchmarks",
                "High confidence merge",
            ],
        }

        if HAS_RICH:
            console.print(
                f"\n[bold]Benefits of {self.selected_lane.value.upper()} Lane:[/bold]"
            )
            for benefit in benefits[self.selected_lane]:
                console.print(f"  ✓ {benefit}")
        else:
            print(f"\nBenefits of {self.selected_lane.value.upper()} Lane:")
            for benefit in benefits[self.selected_lane]:
                print(f"  ✓ {benefit}")

    def _prompt_confirmation(self) -> bool:
        """Prompt user for confirmation."""
        if HAS_RICH:
            response = (
                console.input(
                    f"\n[bold cyan]Execute workflow in {self.selected_lane.value.upper()} lane? (y/n):[/bold cyan] "
                )
                .strip()
                .lower()
            )
        else:
            response = (
                input(
                    f"\nExecute workflow in {self.selected_lane.value.upper()} lane? (y/n): "
                )
                .strip()
                .lower()
            )

        return response in ["y", "yes"]

    def _display_execution_progress(self):
        """Display execution progress."""
        if HAS_RICH:
            console.print("\n[bold cyan]Executing Workflow...[/bold cyan]\n")
        else:
            print("\nExecuting Workflow...\n")

    def _execute_workflow(self) -> str:
        """Execute the selected workflow lane."""
        try:
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                "-v",
                f"--lane={self.selected_lane.value}",
            ]

            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=1800,  # 30 minute timeout
            )

            return result.stdout

        except subprocess.TimeoutExpired:
            raise Exception("Workflow execution timed out")
        except Exception as e:
            raise Exception(f"Workflow execution failed: {str(e)}")

    def _display_success_summary(self, duration: int):
        """Display execution success summary."""
        if HAS_RICH:
            panel = Panel(
                f"[bold green]✓ Workflow Completed Successfully[/bold green]\n"
                f"Lane: [yellow]{self.selected_lane.value.upper()}[/yellow]\n"
                f"Duration: [cyan]{self._format_duration(duration)}[/cyan]",
                border_style="green",
            )
            console.print(panel)
        else:
            print(f"\n✓ Workflow Completed Successfully")
            print(f"  Lane: {self.selected_lane.value.upper()}")
            print(f"  Duration: {self._format_duration(duration)}")

    def _display_info(self, message: str):
        """Display info message."""
        if HAS_RICH:
            console.print(f"[cyan ℹ️ {message}[/cyan]")
        else:
            print(f"ℹ️  {message}")

    def _display_error(self, message: str):
        """Display error message."""
        if HAS_RICH:
            console.print(f"[red]✗ Error: {message}[/red]")
        else:
            print(f"✗ Error: {message}")

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format byte size to human-readable."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    @staticmethod
    def _format_duration(seconds: int) -> str:
        """Format seconds to human-readable duration."""
        mins = seconds // 60
        secs = seconds % 60
        if mins > 0:
            return f"{mins}m {secs}s"
        return f"{secs}s"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Interactive Workflow Lane Selector")
    parser.add_argument(
        "--auto-confirm", action="store_true", help="Skip confirmation dialogs"
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument(
        "--lane",
        choices=["docs", "standard", "heavy"],
        help="Skip selection and use specific lane",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without executing",
    )
    parser.add_argument("--project-root", type=Path, help="Project root path")

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create and run selector
    selector = InteractiveLaneSelector(
        project_root=args.project_root, verbose=args.verbose
    )

    result = selector.run(
        auto_confirm=args.auto_confirm,
        force_lane=args.lane,
        dry_run=args.dry_run,
        json_output=args.json,
    )

    # Exit with appropriate code
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()

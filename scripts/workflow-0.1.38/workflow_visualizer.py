#!/usr/bin/env python3
"""
Workflow Visualization Module

Provides visual representation of OpenSpec workflow state including:
- Completed steps (with checkmarks)
- Current step (highlighted)
- Remaining steps (with dots)
- Checkpoint markers
- Success/failure indicators
- Progress percentage

Supports multiple display formats:
- Tree view (hierarchical)
- Linear timeline
- Compact status bar
- Detailed report
"""

import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

# Try to import checkpoint manager for checkpoint info
try:
    from checkpoint_manager import CheckpointManager

    CHECKPOINT_AVAILABLE = True
except ImportError:
    CHECKPOINT_AVAILABLE = False
    CheckpointManager = None

# Import workflow helpers for colors and utilities
try:
    import workflow_helpers as helpers
except ImportError:
    # Fallback if helpers not available
    class helpers:
        class Colors:
            GREEN = "\033[92m"
            YELLOW = "\033[93m"
            RED = "\033[91m"
            CYAN = "\033[96m"
            WHITE = "\033[97m"
            GRAY = "\033[90m"
            RESET = "\033[0m"
            BOLD = "\033[1m"
            DIM = "\033[2m"


@dataclass
class StepInfo:
    """Information about a workflow step."""

    number: int
    name: str
    status: str  # 'completed', 'current', 'pending', 'failed', 'skipped'
    has_checkpoint: bool = False
    checkpoint_count: int = 0
    last_checkpoint_time: Optional[datetime] = None


@dataclass
class WorkflowState:
    """Current state of the workflow."""

    change_id: str
    total_steps: int
    completed_steps: List[int]
    current_step: Optional[int]
    failed_steps: List[int]
    skipped_steps: List[int]
    checkpoints: Dict[int, int]  # step_number -> checkpoint_count
    last_checkpoint_time: Optional[datetime]


class WorkflowVisualizer:
    """Visualizes workflow state in various formats."""

    # Step definitions (0-12)
    STEPS = {
        0: "GitHub Issue Sync",
        1: "Change Setup",
        2: "Proposal Review",
        3: "Capability Spec",
        4: "Dependency Spec",
        5: "Risk Assessment",
        6: "Script Generation",
        7: "Implementation",
        8: "Testing",
        9: "Documentation",
        10: "Review",
        11: "Merge",
        12: "Archive",
        13: "Pull Request",
    }

    # Unicode symbols for different states
    SYMBOLS = {
        "completed": "✓",
        "current": "▶",
        "pending": "○",
        "failed": "✗",
        "skipped": "⊝",
        "checkpoint": "⚑",
        "branch": "├─",
        "branch_last": "└─",
        "vertical": "│",
        "connector": "──",
    }

    def __init__(self, change_path: Path):
        """
        Initialize visualizer for a change directory.

        Args:
            change_path: Path to change directory
        """
        self.change_path = Path(change_path)
        self.change_id = self.change_path.name
        self.checkpoint_manager = None

        if CHECKPOINT_AVAILABLE and (self.change_path / ".checkpoints").exists():
            try:
                self.checkpoint_manager = CheckpointManager(self.change_path)
            except Exception:
                pass  # Continue without checkpoint info

    def analyze_state(self) -> WorkflowState:
        """
        Analyze current workflow state from filesystem.

        Returns:
            WorkflowState object with current status
        """
        completed = []
        failed = []
        skipped = []
        current = None
        checkpoints = {}
        last_checkpoint_time = None

        # Detect completed steps by checking for required files
        step_markers = {
            0: [],  # GitHub sync has no specific marker
            1: ["proposal.md"],  # Change setup creates proposal
            2: ["proposal.md"],  # Proposal review validates
            3: ["spec.md"],  # Capability spec creates spec.md
            4: ["spec.md"],  # Dependency spec updates spec.md
            5: ["spec.md"],  # Risk assessment updates spec.md
            6: ["test.sh", "implement.sh"],  # Script generation
            7: [],  # Implementation has no specific marker
            8: [],  # Testing has no specific marker
            9: ["README.md"],  # Documentation creates README
            10: [],  # Review has no specific marker
            11: [],  # Merge has no specific marker
            12: [],  # Archive has no specific marker
        }

        # Check which steps are completed based on files
        for step_num in range(13):
            markers = step_markers.get(step_num, [])
            if markers:
                if all((self.change_path / marker).exists() for marker in markers):
                    completed.append(step_num)
            # Steps with no markers are detected via checkpoints or assumed pending

        # Get checkpoint information if available
        if self.checkpoint_manager:
            try:
                checkpoint_list = self.checkpoint_manager.list_checkpoints()

                # Count checkpoints per step
                for cp in checkpoint_list:
                    step_num = cp.step_num
                    checkpoints[step_num] = checkpoints.get(step_num, 0) + 1

                    # Track last checkpoint time
                    cp_time = datetime.fromisoformat(cp.timestamp)
                    if last_checkpoint_time is None or cp_time > last_checkpoint_time:
                        last_checkpoint_time = cp_time

                # Get last successful step
                last_success = self.checkpoint_manager.get_last_successful_step()
                if last_success is not None:
                    # All steps up to last success are completed
                    for step_num in range(last_success + 1):
                        if step_num not in completed:
                            completed.append(step_num)

                # Determine current step (next after last success)
                if last_success is not None and last_success < 12:
                    current = last_success + 1
            except Exception:
                pass  # Continue without checkpoint info

        # If no checkpoint info, detect current step from latest file
        if current is None and completed:
            current = max(completed) + 1 if max(completed) < 13 else None

        return WorkflowState(
            change_id=self.change_id,
            total_steps=14,
            completed_steps=sorted(completed),
            current_step=current,
            failed_steps=failed,
            skipped_steps=skipped,
            checkpoints=checkpoints,
            last_checkpoint_time=last_checkpoint_time,
        )

    def get_step_info(self, step_num: int, state: WorkflowState) -> StepInfo:
        """
        Get detailed information about a specific step.

        Args:
            step_num: Step number (0-12)
            state: Current workflow state

        Returns:
            StepInfo object
        """
        # Determine status
        if step_num in state.failed_steps:
            status = "failed"
        elif step_num in state.skipped_steps:
            status = "skipped"
        elif step_num in state.completed_steps:
            status = "completed"
        elif step_num == state.current_step:
            status = "current"
        else:
            status = "pending"

        # Get checkpoint info
        has_checkpoint = step_num in state.checkpoints
        checkpoint_count = state.checkpoints.get(step_num, 0)
        last_checkpoint_time = None

        if has_checkpoint and self.checkpoint_manager:
            try:
                checkpoint_list = self.checkpoint_manager.list_checkpoints()
                step_checkpoints = [
                    cp for cp in checkpoint_list if cp.step_num == step_num
                ]
                if step_checkpoints:
                    last_cp = max(step_checkpoints, key=lambda cp: cp.timestamp)
                    last_checkpoint_time = datetime.fromisoformat(last_cp.timestamp)
            except Exception:
                pass

        return StepInfo(
            number=step_num,
            name=self.STEPS.get(step_num, f"Step {step_num}"),
            status=status,
            has_checkpoint=has_checkpoint,
            checkpoint_count=checkpoint_count,
            last_checkpoint_time=last_checkpoint_time,
        )

    def render_tree(self, state: WorkflowState, show_checkpoints: bool = True) -> str:
        """
        Render workflow as a tree view.

        Args:
            state: Current workflow state
            show_checkpoints: Whether to show checkpoint markers

        Returns:
            Formatted tree string
        """
        lines = []

        # Header
        lines.append(
            f"{helpers.Colors.BOLD}Workflow: {state.change_id}{helpers.Colors.RESET}"
        )
        lines.append(f"{helpers.Colors.GRAY}{'─' * 60}{helpers.Colors.RESET}")
        lines.append("")

        # Progress summary
        completed_count = len(state.completed_steps)
        progress_pct = (completed_count / state.total_steps) * 100
        lines.append(
            f"Progress: {completed_count}/{state.total_steps} steps ({progress_pct:.1f}%)"
        )
        lines.append("")

        # Render each step
        for step_num in range(state.total_steps):
            step_info = self.get_step_info(step_num, state)
            lines.append(
                self._render_tree_step(
                    step_info, step_num == state.total_steps - 1, show_checkpoints
                )
            )

        # Footer with checkpoint summary
        if show_checkpoints and state.checkpoints:
            lines.append("")
            lines.append(f"{helpers.Colors.GRAY}{'─' * 60}{helpers.Colors.RESET}")
            total_checkpoints = sum(state.checkpoints.values())
            lines.append(
                f"{helpers.Colors.CYAN}Total Checkpoints: {total_checkpoints}{helpers.Colors.RESET}"
            )
            if state.last_checkpoint_time:
                lines.append(
                    f"Last Checkpoint: {state.last_checkpoint_time.strftime('%Y-%m-%d %H:%M:%S')}"
                )

        return "\n".join(lines)

    def _render_tree_step(
        self, step: StepInfo, is_last: bool, show_checkpoints: bool
    ) -> str:
        """Render a single step in tree format."""
        # Select symbol and color based on status
        if step.status == "completed":
            symbol = self.SYMBOLS["completed"]
            color = helpers.Colors.GREEN
        elif step.status == "current":
            symbol = self.SYMBOLS["current"]
            color = helpers.Colors.YELLOW
        elif step.status == "failed":
            symbol = self.SYMBOLS["failed"]
            color = helpers.Colors.RED
        elif step.status == "skipped":
            symbol = self.SYMBOLS["skipped"]
            color = helpers.Colors.GRAY
        else:  # pending
            symbol = self.SYMBOLS["pending"]
            color = helpers.Colors.GRAY

        # Branch character
        branch = self.SYMBOLS["branch_last"] if is_last else self.SYMBOLS["branch"]

        # Build step line
        step_line = f"{branch} {color}{symbol} Step {step.number:2d}: {step.name}{helpers.Colors.RESET}"

        # Add checkpoint marker if present
        if show_checkpoints and step.has_checkpoint:
            checkpoint_marker = f" {helpers.Colors.CYAN}{self.SYMBOLS['checkpoint']} {step.checkpoint_count}{helpers.Colors.RESET}"
            step_line += checkpoint_marker

        return step_line

    def render_timeline(self, state: WorkflowState) -> str:
        """
        Render workflow as a linear timeline.

        Args:
            state: Current workflow state

        Returns:
            Formatted timeline string
        """
        lines = []

        # Header
        lines.append(
            f"{helpers.Colors.BOLD}Workflow Timeline: {state.change_id}{helpers.Colors.RESET}"
        )
        lines.append("")

        # Timeline with symbols
        timeline_symbols = []
        for step_num in range(state.total_steps):
            step_info = self.get_step_info(step_num, state)

            if step_info.status == "completed":
                timeline_symbols.append(
                    f"{helpers.Colors.GREEN}{self.SYMBOLS['completed']}{helpers.Colors.RESET}"
                )
            elif step_info.status == "current":
                timeline_symbols.append(
                    f"{helpers.Colors.YELLOW}{self.SYMBOLS['current']}{helpers.Colors.RESET}"
                )
            elif step_info.status == "failed":
                timeline_symbols.append(
                    f"{helpers.Colors.RED}{self.SYMBOLS['failed']}{helpers.Colors.RESET}"
                )
            else:
                timeline_symbols.append(
                    f"{helpers.Colors.GRAY}{self.SYMBOLS['pending']}{helpers.Colors.RESET}"
                )

        # Join with connectors
        timeline = f" {helpers.Colors.GRAY}{self.SYMBOLS['connector']}{helpers.Colors.RESET} ".join(
            timeline_symbols
        )
        lines.append(timeline)

        # Step numbers
        step_numbers = "   ".join([f"{n:2d}" for n in range(state.total_steps)])
        lines.append(f"{helpers.Colors.GRAY}{step_numbers}{helpers.Colors.RESET}")
        lines.append("")

        # Progress bar
        completed_count = len(state.completed_steps)
        progress_pct = (completed_count / state.total_steps) * 100
        bar_width = 50
        filled = int((completed_count / state.total_steps) * bar_width)
        bar = f"[{'=' * filled}{' ' * (bar_width - filled)}]"
        lines.append(
            f"{helpers.Colors.CYAN}{bar} {progress_pct:.1f}%{helpers.Colors.RESET}"
        )
        lines.append(f"{completed_count}/{state.total_steps} steps complete")

        return "\n".join(lines)

    def render_compact(self, state: WorkflowState) -> str:
        """
        Render workflow as a compact status bar.

        Args:
            state: Current workflow state

        Returns:
            Formatted status bar string
        """
        completed_count = len(state.completed_steps)
        progress_pct = (completed_count / state.total_steps) * 100

        # Current step info
        current_info = ""
        if state.current_step is not None:
            step_name = self.STEPS.get(state.current_step, f"Step {state.current_step}")
            current_info = f" | Current: {step_name}"

        # Checkpoint info
        checkpoint_info = ""
        if state.checkpoints:
            total_checkpoints = sum(state.checkpoints.values())
            checkpoint_info = f" | {self.SYMBOLS['checkpoint']} {total_checkpoints}"

        return (
            f"{helpers.Colors.BOLD}{state.change_id}{helpers.Colors.RESET} "
            f"[{completed_count}/{state.total_steps} - {progress_pct:.0f}%]"
            f"{current_info}{checkpoint_info}"
        )

    def render_detailed(self, state: WorkflowState) -> str:
        """
        Render detailed workflow report.

        Args:
            state: Current workflow state

        Returns:
            Formatted detailed report string
        """
        lines = []

        # Header
        lines.append("=" * 70)
        lines.append(
            f"{helpers.Colors.BOLD}Workflow Detailed Report{helpers.Colors.RESET}"
        )
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Change ID: {state.change_id}")
        lines.append(f"Total Steps: {state.total_steps}")
        lines.append("")

        # Progress section
        completed_count = len(state.completed_steps)
        progress_pct = (completed_count / state.total_steps) * 100
        lines.append(f"{helpers.Colors.BOLD}Progress:{helpers.Colors.RESET}")
        lines.append(
            f"  Completed: {completed_count}/{state.total_steps} ({progress_pct:.1f}%)"
        )
        lines.append(
            f"  Current: {state.current_step if state.current_step is not None else 'N/A'}"
        )
        lines.append(f"  Failed: {len(state.failed_steps)}")
        lines.append(f"  Skipped: {len(state.skipped_steps)}")
        lines.append("")

        # Completed steps
        if state.completed_steps:
            lines.append(
                f"{helpers.Colors.GREEN}Completed Steps:{helpers.Colors.RESET}"
            )
            for step_num in state.completed_steps:
                step_name = self.STEPS.get(step_num, f"Step {step_num}")
                checkpoint_marker = ""
                if step_num in state.checkpoints:
                    checkpoint_marker = (
                        f" {self.SYMBOLS['checkpoint']} {state.checkpoints[step_num]}"
                    )
                lines.append(
                    f"  {self.SYMBOLS['completed']} {step_num:2d}: {step_name}{checkpoint_marker}"
                )
            lines.append("")

        # Current step
        if state.current_step is not None:
            lines.append(f"{helpers.Colors.YELLOW}Current Step:{helpers.Colors.RESET}")
            step_name = self.STEPS.get(state.current_step, f"Step {state.current_step}")
            checkpoint_marker = ""
            if state.current_step in state.checkpoints:
                checkpoint_marker = f" {self.SYMBOLS['checkpoint']} {state.checkpoints[state.current_step]}"
            lines.append(
                f"  {self.SYMBOLS['current']} {state.current_step:2d}: {step_name}{checkpoint_marker}"
            )
            lines.append("")

        # Pending steps
        pending_steps = [
            i
            for i in range(state.total_steps)
            if i not in state.completed_steps
            and i != state.current_step
            and i not in state.failed_steps
            and i not in state.skipped_steps
        ]
        if pending_steps:
            lines.append(f"{helpers.Colors.GRAY}Pending Steps:{helpers.Colors.RESET}")
            for step_num in pending_steps:
                step_name = self.STEPS.get(step_num, f"Step {step_num}")
                lines.append(f"  {self.SYMBOLS['pending']} {step_num:2d}: {step_name}")
            lines.append("")

        # Checkpoint summary
        if state.checkpoints:
            lines.append(
                f"{helpers.Colors.CYAN}Checkpoint Summary:{helpers.Colors.RESET}"
            )
            total_checkpoints = sum(state.checkpoints.values())
            lines.append(f"  Total: {total_checkpoints}")
            if state.last_checkpoint_time:
                lines.append(
                    f"  Last: {state.last_checkpoint_time.strftime('%Y-%m-%d %H:%M:%S')}"
                )
            lines.append("")

        lines.append("=" * 70)

        return "\n".join(lines)


def show_workflow_status(change_path: str, format_type: str = "tree") -> None:
    """
    Display workflow status for a change.

    Args:
        change_path: Path to change directory
        format_type: Display format ('tree', 'timeline', 'compact', 'detailed')
    """
    visualizer = WorkflowVisualizer(Path(change_path))
    state = visualizer.analyze_state()

    if format_type == "tree":
        output = visualizer.render_tree(state)
    elif format_type == "timeline":
        output = visualizer.render_timeline(state)
    elif format_type == "compact":
        output = visualizer.render_compact(state)
    elif format_type == "detailed":
        output = visualizer.render_detailed(state)
    else:
        output = visualizer.render_tree(state)  # Default to tree

    print(output)


if __name__ == "__main__":
    """Command-line interface for workflow visualization."""
    import argparse

    parser = argparse.ArgumentParser(description="Visualize OpenSpec workflow state")
    parser.add_argument("change_path", help="Path to change directory")
    parser.add_argument(
        "--format",
        choices=["tree", "timeline", "compact", "detailed"],
        default="tree",
        help="Display format (default: tree)",
    )

    args = parser.parse_args()

    try:
        show_workflow_status(args.change_path, args.format)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

#!/usr/bin/env python3
"""
OpenSpec Workflow Automation Script (Python Version)

Automates the OpenSpec workflow for change management. This Python version
provides better encoding handling, cleaner syntax, and easier maintenance
compared to the PowerShell version.

Usage:
    python workflow.py --list                           # List all active changes
    python workflow.py --change-id my-change            # Run interactive workflow
    python workflow.py --change-id my-change --step 0   # Run specific step
    python workflow.py --change-id my-change --validate # Validate structure
    python workflow.py --change-id my-change --archive  # Archive change

Author: Obsidian AI Agent Team
License: MIT
"""

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

# Import checkpoint manager
try:
    from checkpoint_manager import CheckpointManager, format_checkpoint_list

    CHECKPOINT_AVAILABLE = True
except ImportError:
    CHECKPOINT_AVAILABLE = False
    CheckpointManager = None

# Import workflow visualizer
try:
    from workflow_visualizer import WorkflowVisualizer

    VISUALIZER_AVAILABLE = True
except ImportError:
    VISUALIZER_AVAILABLE = False
    WorkflowVisualizer = None

# Import helpers with hyphenated filename
spec = importlib.util.spec_from_file_location(
    "workflow_helpers", SCRIPT_DIR / "workflow-helpers.py"
)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)

# Import progress indicators
try:
    from progress_indicators import workflow_progress

    PROGRESS_AVAILABLE = True
except ImportError:
    PROGRESS_AVAILABLE = False
    helpers.write_warning("Progress indicators not available")

# Directory paths
CHANGES_DIR = PROJECT_ROOT / "openspec" / "changes"
ARCHIVE_DIR = PROJECT_ROOT / "openspec" / "archive"
TEMPLATES_DIR = PROJECT_ROOT / "openspec" / "templates"

# Step names for progress display
STEP_NAMES = {
    0: "Create TODOs",
    1: "Version Bump",
    2: "Proposal Review",
    3: "Capability Spec",
    4: "Task Breakdown",
    5: "Implementation Checklist",
    6: "Script Generation",
    7: "Document Review",
    8: "Test Execution",
    9: "Review Changes",
    10: "Git Operations",
    11: "Commit Changes",
    12: "Pull Request",
}


def load_step_module(step_num: int):
    """
    Dynamically load a step module.

    Args:
        step_num: Step number (0-12)

    Returns:
        Module object or None if not found
    """
    step_file = SCRIPT_DIR / f"workflow-step{step_num:02d}.py"

    if not step_file.exists():
        return None

    try:
        spec = importlib.util.spec_from_file_location(
            f"workflow_step{step_num:02d}", step_file
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        helpers.write_warning(f"Failed to load step {step_num}: {e}")
        return None


def get_git_user() -> str:
    """Get git user.name from config."""
    try:
        result = subprocess.run(
            ["git", "config", "user.name"], capture_output=True, text=True, check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            return f"@{result.stdout.strip()}"
    except:
        pass
    return "@unknown"


def derive_title_from_change_id(change_id: str) -> str:
    """Convert kebab-case change-id to Title Case."""
    return " ".join(word.capitalize() for word in change_id.split("-"))


def extract_metadata_from_proposal(proposal_path: Path) -> tuple[Optional[str], Optional[str]]:
    """
    Extract title and owner from existing proposal.md file.
    
    Args:
        proposal_path: Path to proposal.md file
        
    Returns:
        Tuple of (title, owner) or (None, None) if not found
    """
    if not proposal_path.exists():
        return None, None
    
    try:
        content = proposal_path.read_text(encoding='utf-8')
        
        # Extract title from first heading or Change ID context
        title = None
        owner = None
        
        for line in content.split('\n'):
            if line.startswith('# '):
                title = line.replace('# ', '').strip()
                break
        
        # Extract owner from metadata section
        for line in content.split('\n'):
            if line.startswith('**Owner**:'):
                owner = line.replace('**Owner**:', '').strip()
                break
        
        return title, owner
    except Exception as e:
        helpers.write_warning(f"Could not extract metadata from proposal: {e}")
        return None, None


def prompt_for_missing_info(
    change_id: str,
    title: Optional[str],
    owner: Optional[str],
    template: Optional[str] = None,
) -> tuple[str, str, str]:
    """Interactively prompt for title/owner/template if missing, with sensible defaults."""
    # Note: Keep prompts minimal and safe for non-interactive environments
    
    # Try to extract from existing proposal first
    change_path = CHANGES_DIR / change_id
    proposal_path = change_path / "proposal.md"
    proposal_title, proposal_owner = extract_metadata_from_proposal(proposal_path)
    
    derived_title = title or proposal_title or derive_title_from_change_id(change_id)
    detected_owner = owner or proposal_owner or get_git_user()

    # Suggest template based on change_id keywords
    suggested_template = "default"
    if template and template != "default":
        suggested_template = template
    elif any(
        keyword in change_id.lower() for keyword in ["doc", "readme", "guide", "manual"]
    ):
        suggested_template = "docs"
    elif any(
        keyword in change_id.lower() for keyword in ["fix", "bug", "defect", "issue"]
    ):
        suggested_template = "bugfix"
    elif any(
        keyword in change_id.lower()
        for keyword in ["refactor", "cleanup", "restructure"]
    ):
        suggested_template = "refactor"
    elif any(
        keyword in change_id.lower()
        for keyword in ["feature", "add", "new", "implement"]
    ):
        suggested_template = "feature"

    # Skip prompts if we have valid title and owner (e.g., from existing proposal)
    if proposal_title and proposal_owner:
        # Already have metadata from proposal, no need to prompt
        return derived_title, detected_owner, suggested_template

    try:
        print()
        print(
            f"{helpers.Colors.YELLOW}Press Enter to accept defaults or type a new value.{helpers.Colors.RESET}"
        )
        t = input(f"Title [{derived_title}]: ").strip()
        o = input(f"Owner [{detected_owner}]: ").strip()
        print(
            f"{helpers.Colors.CYAN}Template options: feature, bugfix, docs, refactor, default{helpers.Colors.RESET}"
        )
        tmpl = input(f"Template [{suggested_template}]: ").strip()
    except Exception:
        # Fallback silently if input() is not available (e.g., piped execution)
        t, o, tmpl = "", "", ""

    final_title = t if t else derived_title
    final_owner = o if o else detected_owner
    final_template = tmpl if tmpl else suggested_template

    # Validate template choice
    valid_templates = ["feature", "bugfix", "docs", "refactor", "default"]
    if final_template not in valid_templates:
        helpers.write_warning(f"Invalid template '{final_template}', using 'default'")
        final_template = "default"

    return final_title, final_owner, final_template


def list_changes():
    """List all active changes with completion percentages."""
    helpers.show_changes(CHANGES_DIR)
    return 0


def validate_change(change_id: str):
    """Validate change directory structure."""
    change_path = CHANGES_DIR / change_id

    if not change_path.exists():
        helpers.write_error(f"Change not found: {change_id}")
        return 1

    print(
        f"{helpers.Colors.CYAN}Validating change: {change_id}{helpers.Colors.RESET}\n"
    )

    is_valid = helpers.test_change_structure(change_path)

    print()
    if is_valid:
        helpers.write_success("✓ Change structure is valid")
        return 0
    else:
        helpers.write_error("✗ Change structure validation failed")
        return 1


def archive_change(change_id: str):
    """Archive a completed change."""
    # Load step 11 (Archive)
    step11 = load_step_module(11)
    if not step11:
        helpers.write_error("Step 11 (Archive) module not found")
        return 1

    change_path = CHANGES_DIR / change_id
    if not change_path.exists():
        helpers.write_error(f"Change not found: {change_id}")
        return 1

    success = step11.invoke_step11(change_path)
    return 0 if success else 1


def show_status(change_id: str, format_type: str = "tree"):
    """
    Show workflow status visualization for a change.

    Args:
        change_id: Change identifier
        format_type: Display format ('tree', 'timeline', 'compact', 'detailed')
    """
    if not VISUALIZER_AVAILABLE:
        helpers.write_error("Workflow visualizer not available")
        return 1

    change_path = CHANGES_DIR / change_id
    if not change_path.exists():
        helpers.write_error(f"Change not found: {change_id}")
        return 1

    try:
        visualizer = WorkflowVisualizer(change_path)
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
            output = visualizer.render_tree(state)

        print(output)
        return 0
    except Exception as e:
        helpers.write_error(f"Failed to show status: {e}")
        return 1
    return 0 if success else 1


def list_checkpoints_cmd(change_id: str):
    """List all checkpoints for a change."""
    if not CHECKPOINT_AVAILABLE:
        helpers.write_error("Checkpoint system not available")
        return 1

    change_path = CHANGES_DIR / change_id
    if not change_path.exists():
        helpers.write_error(f"Change not found: {change_id}")
        return 1

    try:
        checkpoint_manager = CheckpointManager(change_path)
        checkpoints = checkpoint_manager.list_checkpoints()

        print(
            f"\n{helpers.Colors.CYAN}Checkpoints for: {change_id}{helpers.Colors.RESET}"
        )
        print(format_checkpoint_list(checkpoints))

        last_step = checkpoint_manager.get_last_successful_step()
        if last_step >= 0:
            print(
                f"\n{helpers.Colors.GREEN}Last Successful Step: {last_step}{helpers.Colors.RESET}"
            )

        return 0
    except Exception as e:
        helpers.write_error(f"Failed to list checkpoints: {e}")
        return 1


def rollback_cmd(change_id: str, checkpoint_id: str):
    """Rollback to a specific checkpoint."""
    if not CHECKPOINT_AVAILABLE:
        helpers.write_error("Checkpoint system not available")
        return 1

    change_path = CHANGES_DIR / change_id
    if not change_path.exists():
        helpers.write_error(f"Change not found: {change_id}")
        return 1

    try:
        checkpoint_manager = CheckpointManager(change_path)

        # Show checkpoint details
        checkpoint = checkpoint_manager.get_checkpoint(checkpoint_id)
        if not checkpoint:
            helpers.write_error(f"Checkpoint not found: {checkpoint_id}")
            return 1

        print(f"\n{helpers.Colors.YELLOW}Rollback Details:{helpers.Colors.RESET}")
        print(f"  Checkpoint: {checkpoint_id}")
        print(f"  Step: {checkpoint.step_num} - {checkpoint.step_name}")
        print(f"  Time: {checkpoint.timestamp}")
        print(f"  Files: {len(checkpoint.files_snapshot)} file(s)")

        # Confirm rollback
        response = input(
            f"\n{helpers.Colors.YELLOW}Proceed with rollback? [y/N]: {helpers.Colors.RESET}"
        )
        if response.lower() != "y":
            print("Rollback cancelled.")
            return 0

        # Perform rollback
        success = checkpoint_manager.rollback_to_checkpoint(checkpoint_id)
        return 0 if success else 1

    except Exception as e:
        helpers.write_error(f"Failed to rollback: {e}")
        import traceback

        traceback.print_exc()
        return 1


def cleanup_checkpoints_cmd(change_id: str, keep_count: int):
    """Clean up old checkpoints."""
    if not CHECKPOINT_AVAILABLE:
        helpers.write_error("Checkpoint system not available")
        return 1

    change_path = CHANGES_DIR / change_id
    if not change_path.exists():
        helpers.write_error(f"Change not found: {change_id}")
        return 1

    try:
        checkpoint_manager = CheckpointManager(change_path)
        removed = checkpoint_manager.cleanup_old_checkpoints(keep_count)

        if removed > 0:
            helpers.write_success(
                f"Removed {removed} old checkpoint(s), kept {keep_count} most recent"
            )
        else:
            helpers.write_info(
                f"No checkpoints to remove (have {len(checkpoint_manager.list_checkpoints())})"
            )

        return 0
    except Exception as e:
        helpers.write_error(f"Failed to cleanup checkpoints: {e}")
        return 1


def execute_step(
    step_num: int,
    change_path: Path,
    title: Optional[str] = None,
    owner: Optional[str] = None,
    dry_run: bool = False,
    release_type: Optional[str] = None,
    template: str = "default",
    enable_checkpoints: bool = True,
) -> bool:
    """
    Execute a specific workflow step with optional checkpoint creation.

    Args:
        step_num: Step number (0-12)
        change_path: Path to change directory
        title: Change title (for steps that need it)
        owner: Change owner (for step 0)
        dry_run: If True, preview without making changes
        template: Proposal template type (for step 2)
        enable_checkpoints: If True, create checkpoint before execution

    Returns:
        True if successful, False otherwise
    """
    # Initialize checkpoint manager if available and enabled
    checkpoint_manager = None
    checkpoint_id = None

    if CHECKPOINT_AVAILABLE and enable_checkpoints and not dry_run:
        try:
            checkpoint_manager = CheckpointManager(change_path)
            step_name = STEP_NAMES.get(step_num, f"Step {step_num}")
            checkpoint_id = checkpoint_manager.create_checkpoint(
                step_num, step_name, notes=f"Before executing step {step_num}"
            )
        except Exception as e:
            helpers.write_warning(f"Could not create checkpoint: {e}")

    # Load step module
    step_module = load_step_module(step_num)
    if not step_module:
        helpers.write_error(f"Step {step_num} module not found")
        helpers.write_info(f"Expected: {SCRIPT_DIR}/workflow-step{step_num:02d}.py")
        return False

    # Get the invoke function
    invoke_func = getattr(step_module, f"invoke_step{step_num}", None)
    if not invoke_func:
        helpers.write_error(
            f"Step {step_num} module missing invoke_step{step_num} function"
        )
        return False

    # Build arguments based on step requirements
    kwargs = {"change_path": change_path}

    if step_num == 0:
        # Step 0 needs title and owner
        kwargs["title"] = title or derive_title_from_change_id(change_path.name)
        kwargs["owner"] = owner or get_git_user()
    elif step_num == 2:
        # Step 2 needs title and template
        kwargs["title"] = title or derive_title_from_change_id(change_path.name)
        kwargs["template"] = template
    elif step_num in [3, 4, 5]:
        # These steps need title
        kwargs["title"] = title or derive_title_from_change_id(change_path.name)
    elif step_num == 1 and release_type:
        # Optional release type for version bump
        kwargs["release_type"] = release_type

    if dry_run:
        kwargs["dry_run"] = dry_run

    # Execute step
    try:
        success = invoke_func(**kwargs)

        # Mark step as successful if checkpoint was created
        if success and checkpoint_manager:
            checkpoint_manager.mark_step_success(step_num)

        return success
    except Exception as e:
        helpers.write_error(f"Step {step_num} failed: {e}")
        import traceback

        traceback.print_exc()

        # Offer rollback if checkpoint was created
        if checkpoint_manager and checkpoint_id:
            helpers.write_info(f"\nCheckpoint available: {checkpoint_id}")
            helpers.write_info("To rollback, run:")
            helpers.write_info(
                f"  python workflow.py --change-id {change_path.name} --rollback {checkpoint_id}"
            )

        return False


def run_single_step(
    change_id: str,
    step_num: int,
    title: Optional[str] = None,
    owner: Optional[str] = None,
    dry_run: bool = False,
    release_type: Optional[str] = None,
    template: str = "default",
    enable_checkpoints: bool = True,
):
    """Run a single workflow step."""
    change_path = CHANGES_DIR / change_id

    # Create change directory if it doesn't exist
    if not change_path.exists():
        print(
            f"{helpers.Colors.CYAN}Creating new change: {change_id}{helpers.Colors.RESET}"
        )
        change_path.mkdir(parents=True, exist_ok=True)
        helpers.write_success(f"Created directory: {change_path}\n")

    print(f"{helpers.Colors.CYAN}Executing Step {step_num}...{helpers.Colors.RESET}\n")

    success = execute_step(
        step_num,
        change_path,
        title,
        owner,
        dry_run,
        release_type,
        template,
        enable_checkpoints,
    )

    print()
    if success:
        helpers.write_success(f"✓ Step {step_num} completed successfully")
        return 0
    else:
        helpers.write_error(f"✗ Step {step_num} failed")
        return 1


def run_interactive_workflow(
    change_id: str,
    title: Optional[str] = None,
    owner: Optional[str] = None,
    dry_run: bool = False,
    release_type: Optional[str] = None,
    template: str = "default",
    enable_checkpoints: bool = True,
):
    """Run the complete interactive workflow."""
    change_path = CHANGES_DIR / change_id

    # Derive title/owner/template and allow interactive confirmation/override
    title, owner, template = prompt_for_missing_info(change_id, title, owner, template)

    # Create change directory if it doesn't exist
    if not change_path.exists():
        print(
            f"{helpers.Colors.CYAN}Creating new change: {change_id}{helpers.Colors.RESET}"
        )
        change_path.mkdir(parents=True, exist_ok=True)
        helpers.write_success(f"Created directory: {change_path}\n")

    # Display workflow header
    print("═" * 55)
    print(
        f"{helpers.Colors.CYAN}  OpenSpec Workflow - Interactive Mode{helpers.Colors.RESET}"
    )
    print("═" * 55)
    print()
    print(f"{helpers.Colors.WHITE}Change ID  : {change_id}{helpers.Colors.RESET}")
    print(f"{helpers.Colors.WHITE}Title      : {title}{helpers.Colors.RESET}")
    print(f"{helpers.Colors.WHITE}Owner      : {owner}{helpers.Colors.RESET}")
    print(f"{helpers.Colors.WHITE}Template   : {template}{helpers.Colors.RESET}")
    print(
        f"{helpers.Colors.WHITE}Dry Run    : {'Yes' if dry_run else 'No'}{helpers.Colors.RESET}"
    )
    print()

    # Determine which step to start from using helpers.detect_next_step
    start_step = helpers.detect_next_step(change_path)
    if start_step > 0 and start_step < 13:
        print(
            f"{helpers.Colors.YELLOW}Resuming from Step {start_step} (previous steps validated){helpers.Colors.RESET}\n"
        )

    # Calculate total steps to execute
    total_steps = 14 - start_step

    # Execute steps with nested progress indicator if available
    if PROGRESS_AVAILABLE and total_steps > 1:
        print()  # Add space for progress display

        with workflow_progress(total_steps, "OpenSpec Workflow") as wp:
            for i, current_step in enumerate(range(start_step, 13), 1):
                step_name = STEP_NAMES.get(current_step, f"Step {current_step}")
                wp.start_step(i, step_name)
                wp.update_step_progress("Starting...")

                success = execute_step(
                    current_step,
                    change_path,
                    title,
                    owner,
                    dry_run,
                    release_type,
                    template,
                    enable_checkpoints,
                )

                if not success:
                    wp.finish(f"Failed at Step {current_step}")
                    print()
                    helpers.write_error(
                        f"Step {current_step} failed. Stopping workflow."
                    )
                    helpers.write_info(
                        f"Fix the issue and re-run with: python workflow.py --change-id {change_id} --step {current_step}"
                    )
                    return 1

                wp.update_step_progress("Complete")
                wp.complete_step()

        print()  # Add space after progress
    else:
        # Fallback to non-progress mode
        for current_step in range(start_step, 13):
            success = execute_step(
                current_step,
                change_path,
                title,
                owner,
                dry_run,
                release_type,
                template,
                enable_checkpoints,
            )

            if not success:
                print()
                helpers.write_error(f"Step {current_step} failed. Stopping workflow.")
                helpers.write_info(
                    f"Fix the issue and re-run with: python workflow.py --change-id {change_id} --step {current_step}"
                )
                return 1

            print()

    # Workflow complete
    print("═" * 55)
    print(f"{helpers.Colors.GREEN}  Workflow Complete!{helpers.Colors.RESET}")
    print("═" * 55)
    print()
    helpers.write_success(f"Change '{change_id}' has completed all workflow steps")
    print()

    # Show final workflow visualization
    if VISUALIZER_AVAILABLE:
        print()
        show_status(change_id, "tree")

    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="OpenSpec Workflow Automation (Python)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list
  %(prog)s --change-id my-feature
  %(prog)s --change-id my-feature --step 0
  %(prog)s --change-id my-feature --step 2 --dry-run
  %(prog)s --change-id my-feature --validate
  %(prog)s --change-id my-feature --archive
        """,
    )

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--list", action="store_true", help="List all active changes"
    )
    mode_group.add_argument(
        "--validate", action="store_true", help="Validate change directory structure"
    )
    mode_group.add_argument(
        "--archive", action="store_true", help="Archive a completed change"
    )
    mode_group.add_argument(
        "--status", action="store_true", help="Show workflow status visualization"
    )
    mode_group.add_argument(
        "--list-checkpoints",
        action="store_true",
        help="List all checkpoints for a change",
    )
    mode_group.add_argument(
        "--rollback",
        type=str,
        metavar="CHECKPOINT_ID",
        help="Rollback to a specific checkpoint",
    )
    mode_group.add_argument(
        "--cleanup-checkpoints",
        type=int,
        metavar="KEEP",
        nargs="?",
        const=10,
        help="Remove old checkpoints, keeping the most recent N (default: 10)",
    )

    # Change identification
    parser.add_argument(
        "--change-id",
        type=str,
        help='Change identifier (kebab-case, e.g., "update-readme")',
    )

    parser.add_argument(
        "--path",
        type=str,
        help='Path to change directory (e.g., "openspec/changes/my-change")',
    )

    # Change metadata
    parser.add_argument(
        "--title",
        type=str,
        help="Human-readable title (auto-derived from change-id if not provided)",
    )
    parser.add_argument(
        "--owner",
        type=str,
        help='GitHub handle (e.g., "@username", auto-detected from git if not provided)',
    )
    parser.add_argument(
        "--template",
        type=str,
        choices=["feature", "bugfix", "docs", "refactor", "default"],
        default="default",
        help="Proposal template to use (feature, bugfix, docs, refactor, or default)",
    )

    # Execution control
    parser.add_argument(
        "--step",
        type=int,
        choices=range(0, 13),
        metavar="N",
        help="Execute specific step (0-12)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview actions without making changes"
    )
    parser.add_argument(
        "--release-type",
        type=str,
        choices=["patch", "minor", "major"],
        help="Optional version bump to perform in Step 1",
    )
    parser.add_argument(
        "--no-checkpoints",
        action="store_true",
        help="Disable automatic checkpoint creation",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["tree", "timeline", "compact", "detailed"],
        default="tree",
        help="Status visualization format (default: tree)",
    )

    args = parser.parse_args()

    # Ensure changes directory exists
    CHANGES_DIR.mkdir(parents=True, exist_ok=True)

    # Normalize --path to change_id if provided
    if args.path:
        change_id = Path(args.path).name
        args.change_id = change_id
    elif args.change_id:
        pass  # Already set
    else:
        change_id = None

    # Route to appropriate handler
    if args.list:
        return list_changes()

    if args.validate:
        if not args.change_id:
            parser.error("--validate requires either --change-id or --path")
        return validate_change(args.change_id)

    if args.archive:
        if not args.change_id:
            parser.error("--archive requires either --change-id or --path")
        return archive_change(args.change_id)

    if args.status:
        if not args.change_id:
            parser.error("--status requires either --change-id or --path")
        return show_status(args.change_id, args.format)

    # Checkpoint operations
    if args.list_checkpoints:
        if not args.change_id:
            parser.error("--list-checkpoints requires either --change-id or --path")
        return list_checkpoints_cmd(args.change_id)

    if args.rollback:
        if not args.change_id:
            parser.error("--rollback requires either --change-id or --path")
        return rollback_cmd(args.change_id, args.rollback)

    if args.cleanup_checkpoints is not None:
        if not args.change_id:
            parser.error("--cleanup-checkpoints requires either --change-id or --path")
        return cleanup_checkpoints_cmd(args.change_id, args.cleanup_checkpoints)

    # Regular workflow execution
    if not args.change_id:
        parser.error("--change-id or --path is required (or use --list)")

    # Determine if checkpoints should be enabled
    enable_checkpoints = not args.no_checkpoints

    if args.step is not None:
        # Single step execution
        return run_single_step(
            args.change_id,
            args.step,
            args.title,
            args.owner,
            args.dry_run,
            args.release_type,
            args.template,
            enable_checkpoints,
        )
    else:
        # Interactive workflow
        return run_interactive_workflow(
            args.change_id,
            args.title,
            args.owner,
            args.dry_run,
            args.release_type,
            args.template,
            enable_checkpoints,
        )


if __name__ == "__main__":
    sys.exit(main())

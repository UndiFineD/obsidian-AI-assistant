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
    skip_quality_gates: bool = False,
    lane: str = "standard",
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
        skip_quality_gates: If True, skip quality gates (not recommended)
        lane: Workflow lane (docs, standard, heavy)

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

    # Note: skip_quality_gates is tracked at workflow level but not passed to individual
    # steps since they don't directly control quality gate execution. The flag is meant
    # to be used by generated test.py and implement.py scripts.

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
    skip_quality_gates: bool = False,
    lane: str = "standard",
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

    if skip_quality_gates:
        helpers.write_warning(
            "⚠️  Quality gates SKIPPED - output may not meet production standards"
        )
        print()

    success = execute_step(
        step_num,
        change_path,
        title,
        owner,
        dry_run,
        release_type,
        template,
        enable_checkpoints,
        skip_quality_gates,
        lane,
    )

    print()
    if success:
        helpers.write_success(f"✓ Step {step_num} completed successfully")
        return 0
    else:
        helpers.write_error(f"✗ Step {step_num} failed")
        return 1


def check_code_changes_in_docs_lane(change_path: Path) -> bool:
    """
    Check if code changes exist in a docs-lane workflow.
    
    Scans for Python, JavaScript, and TypeScript files that indicate
    code changes requiring standard or heavy lane validation.
    
    Args:
        change_path: Path to the change directory
        
    Returns:
        True if NO code changes detected (safe for docs lane)
        False if code changes detected (should switch lanes)
    """
    code_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.go', '.rs', '.c', '.h', '.hpp'}
    ignore_patterns = {'__pycache__', '.pyc', 'node_modules', '.git', '.venv', 'venv', '.next', 'dist', 'build'}
    
    code_files_found = []
    
    try:
        for file_path in change_path.rglob('*'):
            if not file_path.is_file():
                continue
                
            # Check if file should be ignored
            if any(ignore in str(file_path) for ignore in ignore_patterns):
                continue
            
            # Check if file is a code file
            if file_path.suffix in code_extensions:
                code_files_found.append(file_path.relative_to(change_path))
    except Exception as e:
        helpers.write_warning(f"Could not check for code changes: {e}")
        return True  # Assume no code changes on error, let user decide
    
    if code_files_found:
        helpers.write_warning(f"Detected {len(code_files_found)} code file(s) in docs lane:")
        for code_file in code_files_found[:5]:  # Show first 5
            helpers.write_info(f"  - {code_file}")
        if len(code_files_found) > 5:
            helpers.write_info(f"  ... and {len(code_files_found) - 5} more")
        return False
    
    return True


def detect_code_changes(change_path: Path) -> dict:
    """
    Analyze a change directory for code changes.
    
    Provides detailed information about code changes detected.
    
    Args:
        change_path: Path to the change directory
        
    Returns:
        Dictionary with code analysis results
    """
    code_extensions = {
        'python': {'.py', '.pyi'},
        'javascript': {'.js', '.jsx', '.mjs'},
        'typescript': {'.ts', '.tsx'},
        'other': {'.java', '.cpp', '.c', '.h', '.hpp', '.go', '.rs'},
    }
    
    ignore_patterns = {'__pycache__', '.pyc', 'node_modules', '.git', '.venv', 'venv', '.next', 'dist', 'build', '.egg-info'}
    
    results = {
        'has_code_changes': False,
        'by_language': {lang: [] for lang in code_extensions},
        'total_count': 0,
        'affected_directories': set(),
    }
    
    try:
        for file_path in change_path.rglob('*'):
            if not file_path.is_file():
                continue
            
            # Skip ignored patterns
            if any(ignore in str(file_path) for ignore in ignore_patterns):
                continue
            
            # Check against all code extensions
            for language, extensions in code_extensions.items():
                if file_path.suffix in extensions:
                    rel_path = file_path.relative_to(change_path)
                    results['by_language'][language].append(str(rel_path))
                    results['affected_directories'].add(str(rel_path.parent))
                    results['total_count'] += 1
                    results['has_code_changes'] = True
                    break
    except Exception as e:
        helpers.write_warning(f"Error analyzing code changes: {e}")
    
    # Convert set to sorted list for consistent output
    results['affected_directories'] = sorted(list(results['affected_directories']))
    
    return results


def run_interactive_workflow(
    change_id: str,
    title: Optional[str] = None,
    owner: Optional[str] = None,
    dry_run: bool = False,
    release_type: Optional[str] = None,
    template: str = "default",
    enable_checkpoints: bool = True,
    skip_quality_gates: bool = False,
    lane: str = "standard",
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

    # Check for code changes in docs lane
    if lane == "docs":
        if not check_code_changes_in_docs_lane(change_path):
            helpers.write_warning("Code files detected in documentation-only lane")
            
            # Get detailed analysis
            code_analysis = detect_code_changes(change_path)
            
            print()
            helpers.write_info("Code Change Analysis:")
            for language, files in code_analysis['by_language'].items():
                if files:
                    helpers.write_info(f"  {language.capitalize()}: {len(files)} file(s)")
            
            if code_analysis['affected_directories']:
                helpers.write_info(f"  Affected dirs: {', '.join(code_analysis['affected_directories'][:3])}")
            
            print()
            helpers.write_warning("The docs lane is optimized for documentation changes only.")
            helpers.write_warning("Code changes require the 'standard' or 'heavy' lane for proper validation.")
            print()
            
            try:
                response = input("Switch to 'standard' lane? (y/n): ").strip().lower()
                if response == 'y':
                    lane = "standard"
                    helpers.write_success("Switched to standard lane")
                    print()
                else:
                    helpers.write_warning("Continuing with docs lane (code validation will be skipped)")
                    print()
            except:
                helpers.write_info("Continuing with docs lane...")
                print()

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
    print(f"{helpers.Colors.WHITE}Lane       : {lane}{helpers.Colors.RESET}")
    print(
        f"{helpers.Colors.WHITE}Dry Run    : {'Yes' if dry_run else 'No'}{helpers.Colors.RESET}"
    )
    if skip_quality_gates:
        print(
            f"{helpers.Colors.YELLOW}Quality Gates: SKIPPED (not recommended for production){helpers.Colors.RESET}"
        )
    print()

    # Log lane configuration
    log_lane_configuration(lane)

    # Determine which step to start from using helpers.detect_next_step
    start_step = helpers.detect_next_step(change_path)
    if start_step > 0 and start_step < 13:
        print(
            f"{helpers.Colors.YELLOW}Resuming from Step {start_step} (previous steps validated){helpers.Colors.RESET}\n"
        )

    # Get stages for this lane
    stages_to_execute = get_stages_for_lane(lane)
    lane_config = LANE_MAPPING[lane]
    
    # Calculate which steps will actually execute
    steps_to_run = [s for s in range(start_step, 13) if s in stages_to_execute]
    total_steps = len(steps_to_run)

    # Execute steps with nested progress indicator if available
    if PROGRESS_AVAILABLE and total_steps > 1:
        print()  # Add space for progress display

        with workflow_progress(total_steps, "OpenSpec Workflow") as wp:
            for i, current_step in enumerate(steps_to_run, 1):
                # Skip steps not in this lane
                if current_step not in stages_to_execute:
                    helpers.write_info(f"[SKIP] Step {current_step} - not in {lane} lane")
                    continue
                
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
                    skip_quality_gates,
                    lane=lane,
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
            # Skip steps not in this lane
            if current_step not in stages_to_execute:
                helpers.write_info(f"[SKIP] Step {current_step} - not in {lane} lane")
                continue
                
            success = execute_step(
                current_step,
                change_path,
                title,
                owner,
                dry_run,
                release_type,
                template,
                enable_checkpoints,
                skip_quality_gates,
                lane=lane,
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


# Lane-to-stage mapping for different workflow intensities
LANE_MAPPING = {
    "docs": {
        "name": "Documentation-Only Lane",
        "description": "Fast docs-only workflow (<5 min)",
        "stages": [0, 1, 2, 3, 4, 5, 7, 9, 10, 12],  # Skip scripts, testing, git ops
        "quality_gates_enabled": False,
        "parallelization_enabled": False,
        "code_change_check": True,  # Warn if code changes detected
        "max_duration_seconds": 300,
    },
    "standard": {
        "name": "Standard Lane",
        "description": "Standard workflow with basic validation (~15 min)",
        "stages": list(range(0, 13)),  # All stages
        "quality_gates_enabled": True,
        "parallelization_enabled": True,
        "code_change_check": False,
        "max_duration_seconds": 900,
    },
    "heavy": {
        "name": "Heavy Lane",
        "description": "Strict validation workflow (~20 min)",
        "stages": list(range(0, 13)),  # All stages
        "quality_gates_enabled": True,
        "parallelization_enabled": True,
        "code_change_check": False,
        "max_duration_seconds": 1200,
    },
}


def get_lane_config(lane: str) -> dict:
    """
    Get configuration for a workflow lane.
    
    Args:
        lane: Lane identifier ('docs', 'standard', or 'heavy')
        
    Returns:
        Dictionary with lane configuration
        
    Raises:
        ValueError if lane is invalid
    """
    if lane not in LANE_MAPPING:
        raise ValueError(f"Invalid lane: {lane}. Valid options: {', '.join(LANE_MAPPING.keys())}")
    
    return LANE_MAPPING[lane].copy()


def get_stages_for_lane(lane: str) -> List[int]:
    """
    Get list of stages to execute for a specific lane.
    
    Args:
        lane: Lane identifier
        
    Returns:
        List of stage numbers to execute
    """
    config = get_lane_config(lane)
    return config.get("stages", list(range(0, 13)))


def should_execute_stage(stage_num: int, lane: str) -> bool:
    """
    Check if a stage should be executed in the given lane.
    
    Args:
        stage_num: Stage number (0-12)
        lane: Lane identifier
        
    Returns:
        True if stage should be executed, False otherwise
    """
    stages = get_stages_for_lane(lane)
    return stage_num in stages


def log_lane_configuration(lane: str):
    """
    Log the selected lane configuration to console.
    
    Args:
        lane: Lane identifier
    """
    config = get_lane_config(lane)
    print()
    print(f"{helpers.Colors.CYAN}╔══════════════════════════════════════════╗{helpers.Colors.RESET}")
    print(f"{helpers.Colors.CYAN}║  Workflow Lane: {config['name']:<20}{helpers.Colors.CYAN}║{helpers.Colors.RESET}")
    print(f"{helpers.Colors.CYAN}╠══════════════════════════════════════════╣{helpers.Colors.RESET}")
    print(f"{helpers.Colors.CYAN}║{helpers.Colors.RESET} {config['description']:<39} {helpers.Colors.CYAN}║{helpers.Colors.RESET}")
    print(f"{helpers.Colors.CYAN}║{helpers.Colors.RESET} Stages: {len(config['stages'])}/13                      {helpers.Colors.CYAN}║{helpers.Colors.RESET}")
    print(f"{helpers.Colors.CYAN}║{helpers.Colors.RESET} Quality Gates: {'Enabled' if config['quality_gates_enabled'] else 'Disabled':<27} {helpers.Colors.CYAN}║{helpers.Colors.RESET}")
    print(f"{helpers.Colors.CYAN}║{helpers.Colors.RESET} Parallelization: {'Enabled' if config['parallelization_enabled'] else 'Disabled':<23} {helpers.Colors.CYAN}║{helpers.Colors.RESET}")
    print(f"{helpers.Colors.CYAN}╚══════════════════════════════════════════╝{helpers.Colors.RESET}")
    print()


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
        "--lane",
        type=str,
        choices=["docs", "standard", "heavy"],
        default="standard",
        help="Workflow lane selection: docs (fast docs-only, <5min), standard (default, ~15min), or heavy (strict, ~20min)",
    )
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
    parser.add_argument(
        "--lane",
        choices=["docs", "standard", "heavy"],
        default="standard",
        help="Workflow lane: docs (fast), standard (default), or heavy (strict)",
    )
    parser.add_argument(
        "--skip-quality-gates",
        action="store_true",
        help="Skip quality gates for faster local iteration (not recommended for production)",
    )

    args = parser.parse_args()
    
    # Configure workflow based on selected lane
    if args.lane:
        lane_config = LANE_MAPPING.get(args.lane, LANE_MAPPING["standard"])
        print(f"[LANE] {lane_config['name']}: {lane_config['description']}")
        # Stages to execute will be determined by: get_stages_for_lane(args.lane)
        # Quality gates will run: {should_run_quality_gates(args.lane)}

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
            args.skip_quality_gates,
            args.lane,
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
            args.skip_quality_gates,
            args.lane,
        )





if __name__ == "__main__":
    sys.exit(main())

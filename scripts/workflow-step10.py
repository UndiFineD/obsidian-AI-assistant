#!/usr/bin/env python3
"""Step 10: Git Operations & GitHub Issue Sync

Prepares git-related notes. Non-destructive by default; no automatic commit.
Optionally syncs open GitHub issues to create change folders.
"""

import sys
import subprocess
import importlib.util
import json
from pathlib import Path
from typing import Optional, List, Dict, Any


SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CHANGES_DIR = PROJECT_ROOT / "openspec" / "changes"
TEMPLATES_DIR = PROJECT_ROOT / "openspec" / "templates"

spec = importlib.util.spec_from_file_location(
    "workflow_helpers",
    SCRIPT_DIR / "workflow-helpers.py",
)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)

# Load progress indicators
progress_spec = importlib.util.spec_from_file_location(
    "progress_indicators",
    SCRIPT_DIR / "progress_indicators.py",
)
progress = importlib.util.module_from_spec(progress_spec)
progress_spec.loader.exec_module(progress)


def _mark_complete(change_path: Path) -> None:
    todo = change_path / "todo.md"
    if not todo.exists():
        return
    content = todo.read_text(encoding="utf-8")
    updated = content.replace("[ ] **10. Git", "[x] **10. Git")
    if updated != content:
        helpers.set_content_atomic(todo, updated)


def _git(args: List[str]) -> str:
    """Execute a git command and return output."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as error:
        return ""


def _check_gh_cli() -> bool:
    """Check if GitHub CLI (gh) is available."""
    try:
        subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _fetch_github_issues() -> List[Dict[str, Any]]:
    """Fetch open GitHub issues using gh CLI.
    
    Returns:
        List of issue dictionaries with number, title, body, labels.
    """
    try:
        result = subprocess.run(
            [
                "gh",
                "issue",
                "list",
                "--state",
                "open",
                "--json",
                "number,title,body,labels",
                "--limit",
                "50",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",  # Replace undecodable bytes
            check=True,
        )
        
        if not result.stdout:
            return []
            
        issues = json.loads(result.stdout)
        return issues if issues else []
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError) as error:
        helpers.write_warning(f"Failed to fetch GitHub issues: {error}")
        return []


def _sanitize_folder_name(issue_number: int, title: str) -> str:
    """Create sanitized folder name from issue number and title.
    
    Args:
        issue_number: GitHub issue number
        title: Issue title
        
    Returns:
        Sanitized folder name like 'issue-123-fix-bug'
    """
    # Take first 50 chars of title, lowercase, replace non-alphanumeric with dash
    sanitized = title.lower()[:50]
    sanitized = "".join(c if c.isalnum() else "-" for c in sanitized)
    # Remove consecutive dashes and strip
    sanitized = "-".join(filter(None, sanitized.split("-")))
    return f"issue-{issue_number}-{sanitized}"


def _create_proposal_from_issue(issue: Dict[str, Any]) -> str:
    """Generate proposal.md content from GitHub issue.
    
    Args:
        issue: Issue dictionary with number, title, body, labels
        
    Returns:
        Formatted proposal.md content
    """
    number = issue.get("number", "N/A")
    title = issue.get("title", "Untitled")
    body = issue.get("body", "No description provided.")
    labels = issue.get("labels", [])
    label_names = [label.get("name", "") for label in labels]
    
    content = f"""# Proposal: {title}

**Source**: GitHub Issue #{number}

## Overview

{body}

## Labels

{", ".join(label_names) if label_names else "None"}

## Proposed Changes

<!-- Fill in specific implementation details -->

## Tasks

See `todo.md` for detailed task breakdown.

## Testing

<!-- Describe how changes will be tested -->

## Impact Analysis

<!-- Describe potential impacts and risks -->
"""
    return content


def _create_todo_from_template() -> str:
    """Generate todo.md content with workflow steps pre-populated.
    
    Returns:
        Formatted todo.md content with workflow steps
    """
    content = """# Task Checklist

## Setup & Planning
- [ ] Step 0: Create change template structure
- [ ] Step 1: Create version snapshot
- [ ] Step 2: Generate capability specification

## Development
- [ ] Step 3: Generate tasks.md with specific implementation tasks
- [ ] Step 4: Generate test specification
- [ ] Step 5: Generate implementation checklist
- [ ] Step 6: Create test and implementation scripts

## Implementation
- [ ] Step 7: Execute tests (if applicable)
- [ ] Step 8: Execute implementation tasks

## Review & Documentation
- [ ] Step 9: Review and update documentation
- [ ] Step 10: Prepare git notes and sync issues

## Finalization
- [ ] Step 11: Create archive of completed change
- [ ] Step 12: Clean up change folder

## Additional Tasks
<!-- Add any issue-specific tasks here -->
"""
    return content


def _sync_github_issues(dry_run: bool = False) -> int:
    """Sync open GitHub issues to create change folders.
    
    Args:
        dry_run: If True, only show what would be created
        
    Returns:
        Number of issues synced/would be synced
    """
    if not _check_gh_cli():
        helpers.write_warning("GitHub CLI (gh) not available. Skipping issue sync.")
        helpers.write_info("Install gh CLI: https://cli.github.com/")
        return 0
    
    # Fetch issues with spinner
    with progress.spinner("Fetching open GitHub issues", "Issues fetched"):
        issues = _fetch_github_issues()
    
    if not issues:
        helpers.write_info("No open GitHub issues found.")
        return 0
    
    helpers.write_success(f"Found {len(issues)} open issue(s)")
    
    synced_count = 0
    
    # Process issues with progress bar
    with progress.progress_bar(
        len(issues),
        "Syncing issues",
        f"Synced {len(issues)} issue(s)"
    ) as bar:
        for issue in issues:
            issue_number = issue.get("number")
            title = issue.get("title", "Untitled")
            
            if not issue_number:
                bar.update(1)
                continue
            
            # Check if change folder already exists (by issue number pattern)
            existing_folders = list(CHANGES_DIR.glob(f"issue-{issue_number}-*"))
            
            if existing_folders:
                helpers.write_info(
                    f"  Issue #{issue_number}: Folder already exists "
                    f"({existing_folders[0].name})"
                )
                bar.update(1, f"#{issue_number} (skipped)")
                continue
            
            folder_name = _sanitize_folder_name(issue_number, title)
            change_path = CHANGES_DIR / folder_name
            
            if dry_run:
                helpers.write_info(f"  [DRY-RUN] Would create: {folder_name}")
                helpers.write_info(f"    Title: {title}")
                synced_count += 1
                bar.update(1, f"#{issue_number} (would create)")
            else:
                # Create change folder structure
                change_path.mkdir(parents=True, exist_ok=True)
                
                # Generate proposal.md
                proposal_content = _create_proposal_from_issue(issue)
                proposal_path = change_path / "proposal.md"
                proposal_path.write_text(proposal_content, encoding="utf-8")
                
                # Generate todo.md
                todo_content = _create_todo_from_template()
                todo_path = change_path / "todo.md"
                todo_path.write_text(todo_content, encoding="utf-8")
                
                # Create empty specs directory
                specs_dir = change_path / "specs"
                specs_dir.mkdir(exist_ok=True)
                
                helpers.write_success(f"  Created: {folder_name}")
                helpers.write_info(f"    Issue #{issue_number}: {title}")
                synced_count += 1
                bar.update(1, f"#{issue_number}")
    
    return synced_count


def invoke_step10(
    change_path: Path, 
    dry_run: bool = False, 
    sync_issues: bool = True,
    **_: dict
) -> bool:
    """Execute Step 10: Git operations and GitHub issue sync.
    
    Args:
        change_path: Path to the change folder
        dry_run: If True, only show what would be done
        sync_issues: If True, sync GitHub issues to create change folders
        **_: Additional keyword arguments (ignored)
        
    Returns:
        True if successful, False otherwise
    """
    helpers.write_step(10, "Git Operations & GitHub Issue Sync")
    
    # Part 1: GitHub Issue Synchronization
    if sync_issues:
        synced_count = _sync_github_issues(dry_run=dry_run)
        if synced_count > 0:
            helpers.write_success(
                f"Synced {synced_count} issue(s) to change folders"
            )
    
    # Part 2: Git notes for current change
    notes_path = change_path / "git_notes.md"

    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"])
    branch = branch if branch else "unknown"

    content = (
        f"## Git Context\n\n"
        f"- Branch: {branch}\n"
        f"- Suggested commit message: chore(openspec): {change_path.name}\n"
    )

    if dry_run:
        helpers.write_info("[DRY-RUN] Would write git_notes.md:")
        helpers.write_info(content)
    else:
        notes_path.write_text(content, encoding="utf-8")
        helpers.write_success(f"Created: {notes_path.name}")

    return True


if __name__ == "__main__":
    test_dir = Path("openspec/changes/test-step10")
    test_dir.mkdir(parents=True, exist_ok=True)
    ok = invoke_step10(test_dir, dry_run=True)
    sys.exit(0 if ok else 1)

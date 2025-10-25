#!/usr/bin/env python3
"""Step 10: Git Operations & GitHub Issue Sync

Prepares git-related notes, commits changes, and pushes to remote.
Optionally syncs open GitHub issues to create change folders.
Validates commit messages against Conventional Commits format.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

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

# Import conventional commits validator
try:
    spec_cc = importlib.util.spec_from_file_location(
        "conventional_commits",
        SCRIPT_DIR / "conventional_commits.py",
    )
    cc_module = importlib.util.module_from_spec(spec_cc)
    spec_cc.loader.exec_module(cc_module)
    CC_AVAILABLE = True
except ImportError:
    CC_AVAILABLE = False
    cc_module = None

# Load progress indicators
progress_spec = importlib.util.spec_from_file_location(
    "progress_indicators",
    SCRIPT_DIR / "progress_indicators.py",
)
progress = importlib.util.module_from_spec(progress_spec)
progress_spec.loader.exec_module(progress)

# Import status tracking
try:
    from status_tracker import StatusTracker
except ImportError:
    StatusTracker = None


def _mark_complete(change_path: Path) -> None:
    todo = change_path / "todo.md"
    if not todo.exists():
        return
    content = todo.read_text(encoding="utf-8")
    updated = content.replace("[ ] **10. Git", "[x] **10. Git")
    if updated != content:
        helpers.set_content_atomic(todo, updated)


def _get_git_diff_summary() -> str:
    """Get a summary of all changes in the working tree.

    Returns:
        Formatted string with git diff statistics and file changes
    """
    try:
        # Get diff statistics
        result = subprocess.run(
            ["git", "diff", "--stat"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "Unable to generate diff summary"


def _get_git_status_details() -> str:
    """Get detailed git status of changed, added, deleted files.

    Returns:
        Formatted string with file status details
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        if not result.stdout.strip():
            return "No changes"

        lines = result.stdout.strip().split("\n")
        modified = [l for l in lines if l.startswith(" M")]
        added = [l for l in lines if l.startswith("??")]
        deleted = [l for l in lines if l.startswith(" D")]

        summary = (
            f"Changed: {len(modified)}, Added: {len(added)}, Deleted: {len(deleted)}"
        )
        return summary
    except subprocess.CalledProcessError:
        return "Unable to get status details"


def _build_comprehensive_commit_message(
    change_name: str,
    new_version: Optional[str],
    change_path: Path,
) -> str:
    """Build a comprehensive commit message with scope, description, and details.

    Args:
        change_name: Name of the OpenSpec change
        new_version: Version number if this is a release
        change_path: Path to the change folder

    Returns:
        Multi-line commit message in conventional commit format
    """
    if new_version:
        scope = "release"
        subject = f"Bump version to v{new_version}"
    else:
        scope = "openspec"
        subject = f"Implement {change_name}"

    # Build body with details
    body_lines = [
        f"OpenSpec Change: {change_name}",
        "",
        "Changes:",
        _get_git_status_details(),
    ]

    # Add change documentation if available
    proposal_path = change_path / "proposal.md"
    if proposal_path.exists():
        try:
            proposal_content = proposal_path.read_text(encoding="utf-8")
            # Extract first few lines of proposal for context
            lines = proposal_content.split("\n")
            for line in lines[1:4]:  # Skip title, get next 3 lines
                if line.strip() and not line.startswith("#"):
                    body_lines.append(line)
                    break
        except Exception:
            pass

    body_lines.extend(
        [
            "",
            "Automated by OpenSpec workflow (Step 10)",
        ]
    )

    # Build complete message: subject + blank line + body
    message = f"{scope}: {subject}\n\n" + "\n".join(body_lines)
    return message


def _update_changelog(
    new_version: Optional[str],
    change_name: str,
) -> bool:
    """Update CHANGELOG.md with new version and changes.

    Args:
        new_version: Version number if this is a release
        change_name: Name of the OpenSpec change

    Returns:
        True if successful, False otherwise
    """
    if not new_version:
        return True  # No changelog update needed for non-release changes

    changelog_path = PROJECT_ROOT / "CHANGELOG.md"
    if not changelog_path.exists():
        helpers.write_warning("CHANGELOG.md not found")
        return False

    try:
        current_content = changelog_path.read_text(encoding="utf-8")

        # Get current date
        from datetime import date

        today = date.today().strftime("%Y-%m-%d")

        # Build changelog entry
        entry = (
            f"## v{new_version} ({today})\n\n"
            f"- **OpenSpec Change**: {change_name}\n"
            f"- **Git Status**: Changes staged, committed, and pushed\n"
            f"- _Released as part of OpenSpec workflow automation._\n\n"
        )

        # Find insertion point (after the header)
        lines = current_content.split("\n")
        insert_index = 0
        for i, line in enumerate(lines):
            if line.startswith("## v") or line.startswith("# 📝"):
                insert_index = i
                break

        # If first version section found, insert before it
        if insert_index > 0:
            new_content = (
                "\n".join(lines[:insert_index])
                + "\n"
                + entry
                + "\n".join(lines[insert_index:])
            )
        else:
            new_content = entry + current_content

        changelog_path.write_text(new_content, encoding="utf-8")
        helpers.write_success("CHANGELOG.md updated")
        return True

    except Exception as error:
        helpers.write_error(f"Failed to update CHANGELOG.md: {error}")
        return False


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
    except subprocess.CalledProcessError:
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
    except (
        subprocess.CalledProcessError,
        json.JSONDecodeError,
        FileNotFoundError,
    ) as error:
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
        len(issues), "Syncing issues", f"Synced {len(issues)} issue(s)"
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
    skip_verify: bool = False,
    **_: dict,
) -> bool:
    """Execute Step 10: Git operations and GitHub issue sync.

    Stages and commits version-bumped files (package.json, CHANGELOG.md, README.md)
    from Step 1, using the versioned branch. Then syncs GitHub issues.

    Args:
        change_path: Path to the change folder
        dry_run: If True, only show what would be done
        sync_issues: If True, sync GitHub issues to create change folders
        skip_verify: If True, skip git commit hooks (like --no-verify)
        **_: Additional keyword arguments (ignored)

    Returns:
        True if successful, False otherwise
    """
    helpers.write_step(10, "Git Operations & GitHub Issue Sync")

    # Initialize status tracker
    tracker = StatusTracker(change_path, "step10") if StatusTracker else None

    # Load version info from state file (set by Step 1)
    version_branch = None
    new_version = None
    state_file = change_path / ".workflow_state.json"
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
            version_branch = state.get("version_branch")
            new_version = state.get("new_version")
            if version_branch:
                helpers.write_info(
                    f"Using version branch from Step 1: {version_branch}"
                )
            if new_version:
                helpers.write_info(f"Version bumped in Step 1: {new_version}")
        except Exception as e:
            helpers.write_warning(f"Could not load version state: {e}")

    # Part 1: GitHub Issue Synchronization
    if sync_issues:
        synced_count = _sync_github_issues(dry_run=dry_run)
        if synced_count > 0:
            helpers.write_success(f"Synced {synced_count} issue(s) to change folders")

    # Part 2: Git notes for current change
    notes_path = change_path / "git_notes.md"

    branch = version_branch or _git(["rev-parse", "--abbrev-ref", "HEAD"])
    branch = branch if branch else "unknown"

    # Build comprehensive commit message
    commit_message = _build_comprehensive_commit_message(
        change_path.name, new_version, change_path
    )

    content = (
        f"## Git Context\n\n"
        f"- Branch: {branch}\n"
        f"- Version: {new_version}\n"
        f"- Commit: See git log for full message\n"
        f"- Tag: v{new_version}\n"
        if new_version
        else f"## Git Context\n\n"
        f"- Branch: {branch}\n"
        f"- Commit: See git log for full message\n"
    )

    if dry_run:
        helpers.write_info("[DRY-RUN] Would write git_notes.md:")
        helpers.write_info(content)
    else:
        notes_path.write_text(content, encoding="utf-8")
        helpers.write_success(f"Created: {notes_path.name}")

    # Part 3: Commit and push changes (including version-bumped files from Step 1)
    if not dry_run:
        try:
            # Stage version-bumped files explicitly
            files_to_stage = [
                "package.json",
                "pyproject.toml",
                "CHANGELOG.md",
                "README.md",
            ]

            # Check which files exist and have changes
            files_with_changes = []
            for file_name in files_to_stage:
                file_path = PROJECT_ROOT / file_name
                if file_path.exists():
                    # Check if file has changes
                    status_check = subprocess.run(
                        ["git", "diff", "--name-only", file_name],
                        cwd=PROJECT_ROOT,
                        capture_output=True,
                        text=True,
                    )
                    if status_check.stdout.strip():
                        files_with_changes.append(file_name)

            # Also check for any other changes (from issue sync, git_notes, etc)
            status_output = _git(["status", "--porcelain"])

            if status_output or files_with_changes:
                helpers.write_info("Staging changes...")

                # Stage all changes
                result = subprocess.run(
                    ["git", "add", "."],
                    cwd=PROJECT_ROOT,
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    helpers.write_error(f"Git add failed: {result.stderr}")
                    return False

                helpers.write_success("Changes staged")

                # Use comprehensive commit message
                helpers.write_info("Committing changes...")
                helpers.write_info(f"Scope: {'release' if new_version else 'openspec'}")

                # Validate commit message against Conventional Commits format
                if CC_AVAILABLE:
                    valid, error = cc_module.CommitValidator.validate_commit(
                        commit_message, skip_verify=skip_verify
                    )
                    if not valid:
                        helpers.write_error(
                            "Commit message not in Conventional Commits format:"
                        )
                        helpers.write_error(f"  {error}")

                        # Suggest fix
                        fixed = cc_module.CommitValidator.fix_commit(commit_message)
                        helpers.write_info(f"Suggested: {fixed}")

                        # Ask user
                        try:
                            response = (
                                input("Use suggested fix? (y/n): ").strip().lower()
                            )
                            if response == "y":
                                commit_message = fixed
                                helpers.write_success(
                                    f"Using fixed message: {commit_message}"
                                )
                            else:
                                helpers.write_warning(
                                    "Proceeding with original message (not recommended)"
                                )
                        except KeyboardInterrupt:
                            helpers.write_error("Commit aborted by user")
                            return False
                    else:
                        helpers.write_success(
                            f"Commit message valid: {commit_message[:60]}..."
                        )

                result = subprocess.run(
                    ["git", "commit", "-m", commit_message],
                    cwd=PROJECT_ROOT,
                    capture_output=True,
                    text=True,
                    # Skip commit hooks if --no-verify flag is set
                    env={
                        "GIT_COMMITTER_NAME": "OpenSpec",
                        "GIT_COMMITTER_EMAIL": "openspec@example.com",
                    },
                )
                if result.returncode != 0:
                    helpers.write_error(f"Git commit failed: {result.stderr}")
                    return False

                helpers.write_success("Changes committed")

                # Create git tag if version available
                if new_version:
                    tag_name = f"v{new_version}"
                    tag_message = f"Release {tag_name}: {change_path.name}"

                    helpers.write_info(f"Creating git tag: {tag_name}")

                    result = subprocess.run(
                        ["git", "tag", "-a", tag_name, "-m", tag_message],
                        cwd=PROJECT_ROOT,
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        helpers.write_success(f"Git tag created: {tag_name}")
                    else:
                        helpers.write_warning(
                            f"Failed to create tag (may already exist): {result.stderr}"
                        )

                # Push changes
                helpers.write_info(f"Pushing to {branch}...")

                result = subprocess.run(
                    ["git", "push", "origin", branch],
                    cwd=PROJECT_ROOT,
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    helpers.write_error(f"Git push failed: {result.stderr}")
                    return False

                helpers.write_success(f"Changes pushed to {branch}")

                # Push tags if version available
                if new_version:
                    helpers.write_info("Pushing git tags...")

                    result = subprocess.run(
                        ["git", "push", "origin", "--tags"],
                        cwd=PROJECT_ROOT,
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        helpers.write_success("Git tags pushed")
                    else:
                        helpers.write_warning(f"Failed to push tags: {result.stderr}")

                # Update CHANGELOG.md
                if new_version:
                    helpers.write_info("Updating CHANGELOG.md...")
                    if _update_changelog(new_version, change_path.name):
                        # Stage and commit CHANGELOG update
                        result = subprocess.run(
                            ["git", "add", "CHANGELOG.md"],
                            cwd=PROJECT_ROOT,
                            capture_output=True,
                            text=True,
                        )
                        if result.returncode == 0:
                            changelog_commit_msg = (
                                f"docs(changelog): Document v{new_version} release"
                            )
                            result = subprocess.run(
                                [
                                    "git",
                                    "commit",
                                    "-m",
                                    changelog_commit_msg,
                                ],
                                cwd=PROJECT_ROOT,
                                capture_output=True,
                                text=True,
                            )
                            if result.returncode == 0:
                                helpers.write_success("CHANGELOG.md committed")
                                # Push the changelog update
                                subprocess.run(
                                    ["git", "push", "origin", branch],
                                    cwd=PROJECT_ROOT,
                                    capture_output=True,
                                    text=True,
                                )
            else:
                helpers.write_info("No changes to commit")
        except Exception as error:
            helpers.write_error(f"Git operations failed: {error}")
            return False

    _mark_complete(change_path)
    helpers.write_success("Step 10 completed")

    # Show changes and validate artifacts
    if not dry_run:
        helpers.show_changes(change_path)
        helpers.validate_step_artifacts(change_path, 10)

    # Detect next step
    helpers.detect_next_step(change_path, 10)

    return True


if __name__ == "__main__":
    test_dir = Path("openspec/changes/test-step10")
    test_dir.mkdir(parents=True, exist_ok=True)
    ok = invoke_step10(test_dir, dry_run=True)
    sys.exit(0 if ok else 1)

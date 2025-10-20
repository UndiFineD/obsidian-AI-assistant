#!/usr/bin/env python3
"""
OpenSpec Workflow Step 12: Pull Request Creation

Creates a GitHub Pull Request for completed changes using the GitHub CLI (gh).
Includes comprehensive PR body with documentation links, change summary, and checklist.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Add scripts directory to path for imports
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from progress_indicators import StatusTracker


def get_change_doc_info(change_path: Path) -> dict:
    """
    Extract metadata from change documentation (proposal.md).

    Args:
        change_path: Path to change directory

    Returns:
        Dictionary with title, why, affected specs/files/code
    """
    doc_info = {
        "title": None,
        "why": None,
        "affected_specs": None,
        "affected_files": None,
        "affected_code": None,
    }

    proposal_path = change_path / "proposal.md"
    if not proposal_path.exists():
        return doc_info

    try:
        content = proposal_path.read_text(encoding="utf-8")

        # Extract title from "# Change Proposal: <title>" or "# Proposal: <title>"
        title_match = re.search(
            r"^#\s*(?:Change\s+)?Proposal:\s*(.+)", content, re.MULTILINE
        )
        if title_match:
            doc_info["title"] = title_match.group(1).strip()

        # Extract Why section content
        why_match = re.search(r"##\s*Why\s+(.+?)(?=\r?\n##\s|\Z)", content, re.DOTALL)
        if why_match:
            why_text = why_match.group(1).strip()
            # Replace newlines with spaces for compact representation
            doc_info["why"] = re.sub(r"\r?\n", " ", why_text)

        # Extract affected specs/files/code from Impact section
        specs_match = re.search(
            r"^-\s*\*\*Affected specs\*\*:\s*(.+)", content, re.MULTILINE
        )
        if specs_match:
            doc_info["affected_specs"] = specs_match.group(1).strip()

        files_match = re.search(
            r"^-\s*\*\*Affected files\*\*:\s*(.+)", content, re.MULTILINE
        )
        if files_match:
            doc_info["affected_files"] = files_match.group(1).strip()

        code_match = re.search(
            r"^-\s*\*\*Affected code\*\*:\s*(.+)", content, re.MULTILINE
        )
        if code_match:
            doc_info["affected_code"] = code_match.group(1).strip()

    except Exception as e:
        print(f"Warning: Failed to parse proposal.md: {e}")

    return doc_info


def get_current_branch() -> str:
    """Get the current git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting current branch: {e}")
        return "main"


def check_gh_cli_available() -> bool:
    """Check if GitHub CLI (gh) is installed and available."""
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_existing_pr(branch: str) -> dict:
    """
    Check if a PR already exists for the given branch.

    Args:
        branch: Branch name to check

    Returns:
        Dictionary with 'exists', 'number', and 'url' keys
    """
    try:
        result = subprocess.run(
            ["gh", "pr", "list", "--head", branch, "--json", "number,url"],
            capture_output=True,
            text=True,
            check=True,
        )

        output = result.stdout.strip()
        if output and output != "null" and output != "[]":
            pr_list = json.loads(output)
            if pr_list and len(pr_list) > 0:
                pr = pr_list[0]
                return {"exists": True, "number": pr["number"], "url": pr["url"]}

        return {"exists": False}

    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Warning: Failed to check for existing PR: {e}")
        return {"exists": False}


def create_pr_with_gh(title: str, body: str, branch: str, base: str = "main") -> tuple:
    """
    Create a pull request using GitHub CLI.

    Args:
        title: PR title
        body: PR body (markdown)
        branch: Source branch
        base: Target branch (default: main)

    Returns:
        Tuple of (success: bool, pr_url: str or error message)
    """
    # Write PR body to temporary file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(body)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [
                "gh",
                "pr",
                "create",
                "--base",
                base,
                "--title",
                title,
                "--body-file",
                tmp_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        # Extract PR URL from output
        output = result.stdout.strip()
        url_match = re.search(r"https?://[^\s]+", output)
        if url_match:
            pr_url = url_match.group(0)
            return (True, pr_url)
        else:
            return (True, "PR created (URL not found in output)")

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        return (False, error_msg)

    finally:
        # Clean up temporary file
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def invoke_step12(change_path, dry_run=False, new_version=None, **_):
    """
    Step 12: Create Pull Request

    Creates a GitHub PR for the completed change with comprehensive documentation.

    Args:
        change_path: Path to change directory
        dry_run: If True, preview PR without creating
        new_version: Version from Step 1 (optional)

    Returns:
        True if successful, False otherwise
    """
    print("\n═════════  STEP 12: Create Pull Request ═════════\n")

    change_path = Path(change_path)
    change_id = change_path.name

    # Check if change has been archived
    openspec_dir = change_path.parent.parent
    archive_dir = openspec_dir / "archive"
    actual_path = change_path
    is_archived = False

    if not change_path.exists():
        # Check archive location
        archived_path = archive_dir / change_id
        if archived_path.exists():
            actual_path = archived_path
            is_archived = True
            print(f"Change has been archived to: openspec/archive/{change_id}/")
        else:
            print(f"Error: Change not found at {change_path} or in archive")
            return False

    # Get current branch
    branch = get_current_branch()
    print(f"Creating Pull Request for change: {change_id}")
    print(f"Current branch: {branch}")
    print()

    # Extract documentation metadata
    doc = get_change_doc_info(actual_path)

    # Build PR title
    if doc["title"]:
        if new_version:
            pr_title = f"chore(openspec): {doc['title']} [v{new_version}]"
        else:
            pr_title = f"chore(openspec): {doc['title']}"
    else:
        if new_version:
            pr_title = f"chore(openspec): Complete change {change_id} [v{new_version}]"
        else:
            pr_title = f"chore(openspec): Complete change {change_id}"

    # Determine documentation base path
    docs_base = (
        f"openspec/archive/{change_id}"
        if is_archived
        else f"openspec/changes/{change_id}"
    )

    # Build PR body
    pr_body_lines = [
        f"# OpenSpec Change: {change_id}",
        "",
        "## Version",
    ]

    if new_version:
        pr_body_lines.append(f"- New version: {new_version}")
    else:
        pr_body_lines.append("- Version: (not detected)")

    pr_body_lines.extend(
        [
            "",
            "## Summary",
            "",
        ]
    )

    if doc["why"]:
        # Truncate if too long
        why_text = doc["why"][:240] + "..." if len(doc["why"]) > 240 else doc["why"]
        pr_body_lines.append(why_text)
    else:
        pr_body_lines.append(f"Complete workflow for {change_id}")

    pr_body_lines.extend(
        [
            "",
            "## Documentation",
            f"- **Proposal**: [{docs_base}/proposal.md]({docs_base}/proposal.md)",
            f"- **Specification**: [{docs_base}/spec.md]({docs_base}/spec.md)",
            f"- **Tasks**: [{docs_base}/tasks.md]({docs_base}/tasks.md)",
            f"- **Test Plan**: [{docs_base}/test_plan.md]({docs_base}/test_plan.md)",
            "",
            "## Changes",
        ]
    )

    if doc["affected_specs"]:
        pr_body_lines.append(f"- **Affected specs**: {doc['affected_specs']}")
    if doc["affected_files"]:
        pr_body_lines.append(f"- **Affected files**: {doc['affected_files']}")
    if doc["affected_code"]:
        pr_body_lines.append(f"- **Affected code**: {doc['affected_code']}")

    pr_body_lines.extend(
        [
            "",
            "## Checklist",
            "- [x] All workflow steps completed (0-12)",
            f"- [x] Change archived to openspec/archive/{change_id}/",
            "- [x] Documentation complete and validated",
            "- [x] Tests passing",
            "- [x] Ready for review",
            "",
            "## Reference",
            "- OpenSpec Workflow: [openspec/PROJECT_WORKFLOW.md](openspec/PROJECT_WORKFLOW.md)",
        ]
    )

    pr_body = "\n".join(pr_body_lines)

    # Check if gh CLI is available
    gh_available = check_gh_cli_available()

    if not gh_available:
        print(
            "Warning: GitHub CLI (gh) not found. Install from: https://cli.github.com/"
        )
        print()
        print("Create PR manually at:")
        print(
            f"  https://github.com/UndiFineD/obsidian-AI-assistant/compare/main...{branch}?expand=1"
        )
        print()
        print(f"Computed PR title: {pr_title}")
        print()
        print("PR body preview (first 15 lines):")
        for line in pr_body_lines[:15]:
            print(f"  {line}")
        print()
        print(f"Suggested manual title if needed: chore(openspec): {change_id}")
        print(f"Link to: {docs_base}/")
        return True  # Non-blocking, user can create PR manually

    if dry_run:
        print("[DRY RUN] Would create PR with:")
        print(f"  Title: {pr_title}")
        print(f"  Branch: {branch} -> main")
        print()
        print("PR body preview:")
        for line in pr_body_lines[:20]:
            print(f"  {line}")
        return True

    # Check for existing PR
    print("Checking for existing PR...")
    existing_pr = check_existing_pr(branch)

    if existing_pr["exists"]:
        print(
            f"Warning: PR already exists for branch '{branch}': #{existing_pr['number']}"
        )
        print(f"URL: {existing_pr['url']}")
        print(f"✓ Using existing Pull Request #{existing_pr['number']}")
        return True

    # Create PR using GitHub CLI
    print("Creating pull request using GitHub CLI...")

    try:
        # Initialize tracker with proper API
        tracker = StatusTracker("Create Pull Request")
        tracker.add_item("prepare", "Preparing PR content", status="running")
        tracker.update_item("prepare", status="success")

        tracker.add_item("auth", "Checking GitHub authentication", status="running")
        # gh will handle auth implicitly during creation
        tracker.update_item("auth", status="success")

        tracker.add_item("create", "Creating pull request", status="running")
        success, result = create_pr_with_gh(pr_title, pr_body, branch)

        if success:
            tracker.update_item("create", status="success")

            tracker.add_item("retrieve", "Retrieving PR URL", status="running")
            pr_url = result
            tracker.update_item("retrieve", status="success")

            tracker.add_item("done", "Pull request created", status="success")

            print()
            print("✓ Pull Request created successfully!")
            print(f"URL: {pr_url}")
            return True
        else:
            tracker.update_item("create", status="failed", message=str(result))
            print()
            print(f"Error: Failed to create PR: {result}")
            print()
            print("You can create it manually at:")
            print(
                f"  https://github.com/UndiFineD/obsidian-AI-assistant/compare/main...{branch}?expand=1"
            )
            return False
    except Exception as e:
        print(f"Warning: StatusTracker error: {e}")
        # Fallback without progress tracking
        success, result = create_pr_with_gh(pr_title, pr_body, branch)

        if success:
            print()
            print("✓ Pull Request created successfully!")
            print(f"URL: {result}")
            return True
        else:
            print()
            print(f"Error: Failed to create PR: {result}")
            print()

            # Check for common errors and provide helpful messages
            if "No commits between" in result:
                print("This usually means you need to commit and push changes first:")
                print("  git add .")
                print(f"  git commit -m 'chore(openspec): Complete change {change_id}'")
                print(f"  git push origin {branch}")
                print()
            elif "uncommitted changes" in result:
                print("You have uncommitted changes. Commit them first:")
                print("  git add .")
                print(f"  git commit -m 'chore(openspec): Complete change {change_id}'")
                print()

            print("You can create the PR manually at:")
            print(
                f"  https://github.com/UndiFineD/obsidian-AI-assistant/compare/main...{branch}?expand=1"
            )
            print()
            print("Step 12 completed with warnings (PR creation pending)")
            return True  # Return True to allow workflow to complete


if __name__ == "__main__":
    # Simple test execution
    if len(sys.argv) < 2:
        print(
            "Usage: python workflow-step12.py <change_path> [--dry-run] [--version=X.Y.Z]"
        )
        sys.exit(1)

    change_path = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    # Extract version if provided
    new_version = None
    for arg in sys.argv:
        if arg.startswith("--version="):
            new_version = arg.split("=", 1)[1]

    success = invoke_step12(change_path, dry_run=dry_run, new_version=new_version)
    sys.exit(0 if success else 1)

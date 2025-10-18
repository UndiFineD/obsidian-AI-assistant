#!/usr/bin/env python3
"""
GitHub Issue Import to OpenSpec

Fetches a GitHub issue and creates an OpenSpec change directory with all required files.
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("Error: 'requests' library not found. Install with: pip install requests")
    sys.exit(1)


def slugify(text: str, max_length: int = 50) -> str:
    """Convert text to URL-safe slug."""
    # Convert to lowercase
    text = text.lower()
    # Replace non-alphanumeric with hyphens
    text = re.sub(r"[^a-z0-9]+", "-", text)
    # Remove leading/trailing hyphens
    text = text.strip("-")
    # Truncate to max length
    if len(text) > max_length:
        text = text[:max_length].rstrip("-")
    return text


def parse_issue_url(
    url_or_number: str,
    default_owner: Optional[str] = None,
    default_repo: Optional[str] = None,
) -> Tuple[str, str, int]:
    """
    Parse GitHub issue URL, short format, or number.

    Supports three formats:
    - Full URL: https://github.com/owner/repo/issues/123
    - Short format: owner/repo#123
    - Number only: 123 (requires --owner and --repo flags)

    Args:
        url_or_number: Full URL, short format, or just issue number
        default_owner: Default repository owner
        default_repo: Default repository name

    Returns:
        Tuple of (owner, repo, issue_number)
    """
    # Try parsing as URL first
    if url_or_number.startswith("http"):
        parsed = urlparse(url_or_number)
        if parsed.hostname != "github.com":
            raise ValueError(f"Invalid GitHub URL: {url_or_number}")

        # Extract owner/repo/issues/number
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) < 4 or path_parts[2] != "issues":
            raise ValueError(f"Invalid GitHub issue URL format: {url_or_number}")

        owner, repo, _, number_str = path_parts[:4]
        try:
            issue_number = int(number_str)
        except ValueError:
            raise ValueError(f"Invalid issue number: {number_str}")

        return owner, repo, issue_number

    # Try parsing as short format: owner/repo#number
    short_pattern = r"^([^/]+)/([^/#]+)#(\d+)$"
    short_match = re.match(short_pattern, url_or_number)

    if short_match:
        owner, repo, number_str = short_match.groups()
        issue_number = int(number_str)
        return owner, repo, issue_number

    # Try parsing as just a number
    try:
        issue_number = int(url_or_number)
        if not default_owner or not default_repo:
            raise ValueError(
                "Issue number provided without URL. "
                "Use --owner and --repo flags or provide full URL/short format."
            )
        return default_owner, default_repo, issue_number
    except ValueError as e:
        # Re-raise if it's already our custom error
        if "Issue number provided without URL" in str(e):
            raise
        raise ValueError(
            f"Invalid issue format: {url_or_number}\n"
            f"Expected formats:\n"
            f"  - Full URL: https://github.com/owner/repo/issues/123\n"
            f"  - Short format: owner/repo#123\n"
            f"  - Number only: 123 (with --owner and --repo flags)"
        )


def fetch_github_issue(
    owner: str, repo: str, issue_number: int, token: Optional[str] = None
) -> Dict:
    """
    Fetch issue data from GitHub API.

    Args:
        owner: Repository owner
        repo: Repository name
        issue_number: Issue number
        token: Optional GitHub token for authentication

    Returns:
        Issue data dictionary
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "OpenSpec-GitHub-Import/1.0",
    }

    if token:
        headers["Authorization"] = f"token {token}"

    try:
        response = requests.get(url, headers=headers, timeout=10)

        # Check status before raising
        if response.status_code == 404:
            raise ValueError(
                f"Issue not found: {owner}/{repo}#{issue_number}\n"
                f"Check that the repository and issue number are correct."
            )
        elif response.status_code == 403:
            raise ValueError(
                f"Access forbidden to {owner}/{repo}#{issue_number}\n"
                f"The repository may be private. Set GITHUB_TOKEN environment variable."
            )

        response.raise_for_status()

        # Check rate limit
        remaining = response.headers.get("X-RateLimit-Remaining")
        if remaining and int(remaining) < 10:
            print(
                f"Warning: GitHub API rate limit low ({remaining} requests remaining)"
            )

        return response.json()

    except Exception as e:
        # HTTPError or mocked Exception path from tests
        status = getattr(getattr(e, "response", None), "status_code", None)
        if status == 404 or (isinstance(e, Exception) and "404" in str(e)):
            raise ValueError(
                f"Issue not found: {owner}/{repo}#{issue_number}\n"
                f"Check that the repository and issue number are correct."
            )
        elif status == 403 or (isinstance(e, Exception) and "403" in str(e)):
            raise ValueError(
                f"Access forbidden to {owner}/{repo}#{issue_number}\n"
                f"The repository may be private. Set GITHUB_TOKEN environment variable."
            )
        else:
            raise ValueError(f"GitHub API error: {e}")

    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch issue: {e}")


def build_change_id(issue_title: str, date_str: Optional[str] = None) -> str:
    """Build OpenSpec change ID from issue title."""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    slug = slugify(issue_title)
    return f"{date_str}-{slug}"


def create_change_directory(
    issue_data: Dict,
    base_dir: Path,
    change_id: Optional[str] = None,
    owner: Optional[str] = None,
    force: bool = False,
) -> Path:
    """
    Create OpenSpec change directory with all files.

    Args:
        issue_data: GitHub issue data
        base_dir: Base directory (project root)
        change_id: Optional custom change ID
        owner: Optional change owner (default: issue author)
        force: Overwrite existing directory

    Returns:
        Path to created change directory
    """
    # Generate change ID
    if not change_id:
        change_id = build_change_id(issue_data["title"])

    # Determine owner
    if not owner:
        owner = f"@{issue_data['user']['login']}"

    # Create directory
    change_dir = base_dir / "openspec" / "changes" / change_id

    if change_dir.exists() and not force:
        raise ValueError(
            f"Change directory already exists: {change_dir}\n"
            f"Use --force to overwrite."
        )

    change_dir.mkdir(parents=True, exist_ok=True)

    # Create proposal.md
    proposal_content = f"""# Proposal: {issue_data['title']}

## Problem Statement

{issue_data['body'] or 'No description provided.'}

## Rationale

This change addresses GitHub issue #{issue_data['number']} in {issue_data['html_url'].rsplit('/', 3)[0]}.

## Labels

{', '.join(label['name'] for label in issue_data.get('labels', [])) or 'None'}

## Links

- **GitHub Issue**: {issue_data['html_url']}
- **Author**: [{issue_data['user']['login']}]({issue_data['user']['html_url']})
- **Created**: {issue_data['created_at'][:10]}
- **State**: {issue_data['state']}

## Impact Analysis

_To be completed during specification phase._
"""

    (change_dir / "proposal.md").write_text(proposal_content, encoding="utf-8")

    # Create spec.md
    spec_content = f"""# Specification: {issue_data['title']}

## Acceptance Criteria

_Define specific, measurable criteria for completion._

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Details

_Document technical approach, data models, API changes, etc._

## Security & Privacy

_Document security considerations and privacy implications._

## Performance Requirements

_Define performance targets and optimization strategies._

## Related GitHub Issue

**Issue**: {issue_data['html_url']}
"""

    (change_dir / "spec.md").write_text(spec_content, encoding="utf-8")

    # Create tasks.md
    tasks_content = f"""# Tasks: {issue_data['title']}

## Implementation Tasks

- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## Testing Tasks

- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Validate acceptance criteria

## Documentation Tasks

- [ ] Update relevant documentation
- [ ] Update CHANGELOG.md
- [ ] Update API docs (if applicable)

## Related GitHub Issue

**Issue**: {issue_data['html_url']}
"""

    (change_dir / "tasks.md").write_text(tasks_content, encoding="utf-8")

    # Create test_plan.md
    test_plan_content = f"""# Test Plan: {issue_data['title']}

## Unit Tests

- [ ] Test case 1
- [ ] Test case 2
- [ ] Test case 3

## Integration Tests

- [ ] Integration test 1
- [ ] Integration test 2

## Coverage Goals

- Unit tests: 90%+
- Integration tests: Key workflows covered

## Related GitHub Issue

**Issue**: {issue_data['html_url']}
"""

    (change_dir / "test_plan.md").write_text(test_plan_content, encoding="utf-8")

    # Read and populate todo.md template
    template_path = base_dir / "openspec" / "templates" / "todo.md"

    if template_path.exists():
        todo_content = template_path.read_text(encoding="utf-8")

        # Replace placeholders
        today = datetime.now().strftime("%Y-%m-%d")
        todo_content = todo_content.replace("<Change Title>", issue_data["title"])
        todo_content = todo_content.replace("<change-id>", change_id)
        todo_content = todo_content.replace("YYYY-MM-DD", today)
        todo_content = todo_content.replace("@username", owner)

        # Add GitHub issue link (try multiple formats)
        if "- **GitHub Issue**: #XXX" in todo_content:
            todo_content = todo_content.replace(
                "- **GitHub Issue**: #XXX",
                f"- **GitHub Issue**: {issue_data['html_url']}",
            )
        elif "GitHub Issue: #XXX" in todo_content:
            todo_content = todo_content.replace(
                "GitHub Issue: #XXX", f"GitHub Issue: {issue_data['html_url']}"
            )

        (change_dir / "todo.md").write_text(todo_content, encoding="utf-8")
    else:
        print(f"Warning: Template not found at {template_path}")
        # Create basic todo.md
        basic_todo = f"""# TODO: {issue_data['title']}

## Change Information
- **Change ID**: `{change_id}`
- **Created**: {datetime.now().strftime('%Y-%m-%d')}
- **Owner**: {owner}
- **GitHub Issue**: {issue_data['html_url']}

## Workflow Progress

Follow the OpenSpec workflow stages 0-12.
"""
        (change_dir / "todo.md").write_text(basic_todo, encoding="utf-8")

    return change_dir


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Import GitHub issue to OpenSpec change directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import by full URL
  python scripts/import_github_issue.py https://github.com/owner/repo/issues/42

  # Import by short format
  python scripts/import_github_issue.py owner/repo#42

  # Import by number (requires --owner and --repo)
  python scripts/import_github_issue.py 42 --owner owner --repo repo

  # Custom change ID and owner
  python scripts/import_github_issue.py owner/repo#42 --id my-custom-id --owner @myhandle

  # Dry run (preview only)
  python scripts/import_github_issue.py owner/repo#42 --dry-run

  # Use GitHub token for authentication
  export GITHUB_TOKEN=your_token_here
  python scripts/import_github_issue.py owner/repo#42
""",
    )

    parser.add_argument(
        "issue",
        help="GitHub issue URL, short format (owner/repo#number), or number only",
    )
    parser.add_argument(
        "--owner", help="Repository owner (required if using issue number)"
    )
    parser.add_argument(
        "--repo", help="Repository name (required if using issue number)"
    )
    parser.add_argument(
        "--id",
        dest="change_id",
        help="Custom change ID (default: auto-generated from title)",
    )
    parser.add_argument(
        "--owner-name", dest="owner_name", help="Change owner (default: issue author)"
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path.cwd(),
        help="Base directory (default: current directory)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview without creating files"
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite existing change directory"
    )

    args = parser.parse_args()

    # Get GitHub token from environment
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print("Note: No GITHUB_TOKEN found. Using unauthenticated API (rate-limited).")
        print("Set GITHUB_TOKEN environment variable for higher rate limits.")

    try:
        # Parse issue URL/number
        owner, repo, issue_number = parse_issue_url(args.issue, args.owner, args.repo)

        print(f"Fetching issue: {owner}/{repo}#{issue_number}")

        # Fetch issue data
        issue_data = fetch_github_issue(owner, repo, issue_number, github_token)

        print(f"✓ Found issue: {issue_data['title']}")
        print(f"  Author: {issue_data['user']['login']}")
        print(f"  State: {issue_data['state']}")
        print(f"  Created: {issue_data['created_at'][:10]}")

        if issue_data.get("labels"):
            print(f"  Labels: {', '.join(l['name'] for l in issue_data['labels'])}")

        # Generate change ID
        change_id = args.change_id or build_change_id(issue_data["title"])
        print(f"\nChange ID: {change_id}")

        if args.dry_run:
            print("\n[DRY RUN] Would create:")
            print(f"  openspec/changes/{change_id}/")
            print("    ├── todo.md")
            print("    ├── proposal.md")
            print("    ├── spec.md")
            print("    ├── tasks.md")
            print("    └── test_plan.md")
            return 0

        # Create change directory
        change_dir = create_change_directory(
            issue_data, args.base_dir, change_id, args.owner_name, args.force
        )

        print(f"\n✓ Created change directory: {change_dir}")
        print("\nNext steps:")
        print(f"  1. Review and update files in {change_dir}")
        print("  2. Follow OpenSpec workflow stages 0-12")
        print("  3. See openspec/PROJECT_WORKFLOW.md for details")

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

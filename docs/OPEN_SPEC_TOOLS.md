# OpenSpec Tools

This project includes helper CLIs to scaffold new OpenSpec change directories.

## 1. Scaffold a New Change from Scratch

Use `openspec_new_change.py` to create a new change directory manually:

- Preview actions (no files created):

```bash
python scripts/openspec_new_change.py "My New Change" --dry-run
```

- Create with defaults (change-id will be `YYYY-MM-DD-my-new-change`):

```bash
python scripts/openspec_new_change.py "My New Change" --owner @yourhandle
```

- Create with explicit id:

```bash
python scripts/openspec_new_change.py --id 2025-10-18-my-new-change --title "My New Change"
```

## 2. Import from GitHub Issue

Use `import_github_issue.py` to automatically create an OpenSpec change from an existing GitHub issue:

### Basic Usage

```bash
# Import by full URL
python scripts/import_github_issue.py https://github.com/owner/repo/issues/42

# Import by number (requires --owner and --repo)
python scripts/import_github_issue.py 42 --owner owner --repo repo

# Preview without creating files
python scripts/import_github_issue.py <URL> --dry-run
```

### Advanced Options

```bash
# Custom change ID
python scripts/import_github_issue.py <URL> --id my-custom-id

# Custom owner
python scripts/import_github_issue.py <URL> --owner-name @myhandle

# Overwrite existing directory
python scripts/import_github_issue.py <URL> --force

# Use GitHub token for higher rate limits
export GITHUB_TOKEN=your_token_here  # Linux/macOS
$env:GITHUB_TOKEN="your_token_here"  # PowerShell
python scripts/import_github_issue.py <URL>
```

### What It Does

The tool:
1. Fetches issue data from GitHub API
2. Generates a change-id from the issue title
3. Creates all required OpenSpec files:
   - `proposal.md` - populated with issue details
   - `spec.md` - template for technical specification
   - `tasks.md` - template for task breakdown
   - `test_plan.md` - template for test planning
   - `todo.md` - workflow checklist with placeholders filled

### Authentication

- **Without token**: Works with public repositories, but rate-limited to 60 requests/hour
- **With token**: Higher rate limits (5000 requests/hour) and access to private repositories
- Set `GITHUB_TOKEN` environment variable (not stored in files)

### Example Output

```
Fetching issue: microsoft/vscode/issues/12345
✓ Found issue: Add new feature for...
  Author: contributor
  State: open
  Created: 2025-10-18
  Labels: enhancement, good-first-issue

Change ID: 2025-10-18-add-new-feature-for

✓ Created change directory: openspec/changes/2025-10-18-add-new-feature-for

Next steps:
  1. Review and update files in openspec/changes/2025-10-18-add-new-feature-for
  2. Follow OpenSpec workflow stages 0-12
  3. See openspec/PROJECT_WORKFLOW.md for details
```

## Output Structure

Both tools create the same structure:

```
openspec/
  changes/
    <change-id>/
      todo.md        # workflow checklist with placeholders filled
      proposal.md    # problem statement and rationale
      spec.md        # technical specification
      tasks.md       # actionable task breakdown
      test_plan.md   # test strategy and coverage goals
```

## Notes

- Use `--force` to overwrite an existing directory
- Use `--base-dir` if you're running from a different working directory
- The `todo.md` template lives in `openspec/templates/todo.md`
- GitHub issue import requires the `requests` library: `pip install requests`

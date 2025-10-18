# Proposal: Short Format Support for GitHub Issue Import

## Problem Statement

During validation testing of the GitHub issue import tool (v0.1.3), we discovered that the parser only accepts full GitHub issue URLs:

```bash
# ✅ Works
python scripts/import_github_issue.py https://github.com/microsoft/vscode/issues/1000

# ❌ Doesn't work
python scripts/import_github_issue.py microsoft/vscode#1000
```

The short format (`owner/repo#number`) is commonly used in GitHub discussions, commit messages, and documentation. Supporting this format would improve usability and match user expectations.

## Proposed Solution

Enhance the `parse_issue_url()` function in `scripts/import_github_issue.py` to accept both formats:

1. **Full URL format**: `https://github.com/owner/repo/issues/number`
2. **Short format**: `owner/repo#number`

The parser should:
- Detect which format is provided
- Extract owner, repo, and issue number from either format
- Return a consistent tuple `(owner, repo, issue_number)`
- Provide clear error messages for invalid formats

## Benefits

- **Improved usability**: Users can paste short references from commit messages, PR comments, etc.
- **Reduced friction**: No need to navigate to GitHub to get the full URL
- **Consistent with GitHub conventions**: Matches how GitHub displays and references issues
- **Backward compatible**: Existing full URL format continues to work

## Implementation Scope

**Files to modify:**
- `scripts/import_github_issue.py` - Update `parse_issue_url()` function
- `tests/test_import_github_issue.py` - Add test cases for short format
- `docs/OPEN_SPEC_TOOLS.md` - Add short format examples

**Estimated effort**: 30 minutes
- Implementation: 10 minutes
- Testing: 10 minutes
- Documentation: 10 minutes

## Success Criteria

1. Parser accepts both full URLs and short format
2. All existing tests continue to pass
3. New tests cover short format parsing
4. Documentation includes examples of both formats
5. Clear error messages for invalid formats (e.g., `microsoft/vscode` without `#number`)

## Links

- **GitHub Issue**: Not applicable (internal enhancement)
- **Related Change**: openspec/changes/2025-10-18-automate-github-issue-import/
- **Validation Report**: See retrospective.md in above change


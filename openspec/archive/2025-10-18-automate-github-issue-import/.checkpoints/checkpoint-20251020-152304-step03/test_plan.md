# Test Plan: Automate GitHub Issue Import to OpenSpec

## Unit Tests

### 1. URL/Number Parsing
- **Test:** Parse full GitHub issue URL
- **Input:** `https://github.com/owner/repo/issues/42`
- **Expected:** `owner="owner", repo="repo", number=42`

- **Test:** Parse issue number only
- **Input:** `42` (with config or flag for owner/repo)
- **Expected:** `number=42`, use default owner/repo

- **Test:** Invalid URL format
- **Input:** `https://example.com/not-a-github-url`
- **Expected:** Raise ValueError with helpful message

### 2. Change ID Generation
- **Test:** Generate from issue title
- **Input:** Issue title "Add automated testing"
- **Expected:** `2025-10-18-add-automated-testing`

- **Test:** Handle special characters
- **Input:** Issue title "Fix: Bug in @user's feature (v2.0)"
- **Expected:** `2025-10-18-fix-bug-in-users-feature-v2-0`

- **Test:** Handle very long titles
- **Input:** 150-character title
- **Expected:** Truncated to reasonable length with slug

### 3. GitHub API Integration
- **Test:** Fetch issue with auth token
- **Mock:** GitHub API response with token
- **Expected:** Issue data retrieved, token used in headers

- **Test:** Fetch issue without auth token
- **Mock:** GitHub API response (rate-limited)
- **Expected:** Issue data retrieved, warning about rate limits

- **Test:** 404 Not Found
- **Mock:** GitHub API 404 response
- **Expected:** Clear error message about missing issue

- **Test:** 403 Forbidden (private repo, no access)
- **Mock:** GitHub API 403 response
- **Expected:** Error message about permissions

### 4. File Creation
- **Test:** Create all required files
- **Input:** Issue data
- **Expected:** proposal.md, spec.md, tasks.md, test_plan.md, todo.md created

- **Test:** Populate proposal.md with issue data
- **Input:** Issue #42 with title, body, labels
- **Expected:** proposal.md contains title, body, labels, link to issue

- **Test:** Replace placeholders in todo.md
- **Input:** Template with `<change-id>`, `YYYY-MM-DD`, `@username`
- **Expected:** All placeholders replaced with actual values

### 5. Error Handling
- **Test:** Directory already exists (no --force)
- **Expected:** Error, suggest --force flag

- **Test:** Directory exists with --force
- **Expected:** Overwrite with confirmation

- **Test:** Network timeout
- **Mock:** Timeout exception
- **Expected:** Retry or clear error message

## Integration Tests

### 1. End-to-End Workflow
- **Test:** Full import from public issue
- **Steps:**
  1. Run script with public GitHub issue URL
  2. Verify all files created
  3. Check proposal.md contains issue data
  4. Validate todo.md placeholders replaced
- **Expected:** Complete change directory ready for workflow

### 2. Dry-Run Mode
- **Test:** Preview without creating files
- **Steps:**
  1. Run with --dry-run flag
  2. Check console output
  3. Verify no files created
- **Expected:** Output shows what would be created, no side effects

### 3. CLI Flag Combinations
- **Test:** Various flag combinations
- **Cases:**
    - `--issue URL --owner @user`
    - `--id custom-id --issue URL`
    - `--force --issue URL` (overwrite existing)
- **Expected:** All combinations work correctly

## Manual Testing

### 1. Real GitHub Issues
- Test with actual public issues from popular repositories
- Verify issue data extraction accuracy
- Check formatting and markdown rendering

### 2. Authentication
- Test with `GITHUB_TOKEN` environment variable
- Test without token (rate-limited)
- Verify token not logged or written to files

### 3. Edge Cases
- Very long issue bodies (>10k characters)
- Issues with code blocks, images, tables
- Issues with special characters in title
- Closed vs open issues
- Issues with many labels

## Coverage Goals

- **Unit tests**: 90%+ coverage for core functions
- **Integration tests**: All CLI entry points tested
- **Error paths**: All error conditions have tests
- **Mock usage**: All GitHub API calls mocked in unit tests

## Success Criteria

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Coverage meets 90%+ threshold
- [ ] Manual testing completed for edge cases
- [ ] Documentation updated with test results
- [ ] No security issues (no token leakage)

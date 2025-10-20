# Tasks: Short Format Support Implementation

## Task 1: Update Parser Function

**File**: `scripts/import_github_issue.py`

**Changes**:
1. Locate the `parse_issue_url()` function
2. Add short format regex pattern
3. Try URL pattern first
4. Try short pattern second
5. Enhance error message

**Acceptance Criteria**:
- Function accepts both URL and short format
- Error message includes both format examples

## Task 2: Add Test Cases

**File**: `tests/test_import_github_issue.py`

**New Tests**:
1. `test_parse_short_format_basic()`
2. `test_parse_short_format_with_dash()`
3. `test_parse_short_format_large_number()`
4. `test_parse_short_format_missing_hash()`
5. `test_parse_short_format_missing_repo()`
6. `test_parse_short_format_only_hash()`

**Acceptance Criteria**:
- All 6 new tests pass
- All existing tests continue to pass

## Task 3: Update Documentation

**File**: `docs/OPEN_SPEC_TOOLS.md`

**Changes**:
- Add short format examples
- Add comparison table

## Task 4: Update CLI Help

**File**: `scripts/import_github_issue.py`

**Changes**:
- Update argparse help text

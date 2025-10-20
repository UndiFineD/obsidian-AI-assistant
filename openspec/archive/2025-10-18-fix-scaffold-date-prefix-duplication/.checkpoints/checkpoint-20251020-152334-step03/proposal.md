# Proposal: Fix Scaffold Date Prefix Duplication

## Problem Statement

During v0.1.4 development, we discovered a bug in `scripts/openspec_new_change.py`:

```bash
# Bug: Adds date prefix twice
$ python scripts/openspec_new_change.py "2025-10-18-short-format-support"
# Creates: openspec/changes/2025-10-18-2025-10-18-short-format-support/
```

**Root Cause**: The `build_change_id()` function always prepends the current date, even when the input title already contains a date prefix.

**Impact**:
- Confusing directory names with duplicate dates
- Developer has to manually rename directories
- Breaks convention of clean change-id format

## Proposed Solution

Enhance `build_change_id()` to detect and strip existing date prefixes before adding the date:

```python
def build_change_id(title: str, date: Optional[str] = None, explicit_id: Optional[str] = None) -> str:
    if explicit_id:
        return explicit_id
    
    # Strip existing date prefix if present
    date_pattern = r'^\d{4}-\d{2}-\d{2}-'
    clean_title = re.sub(date_pattern, '', title)
    
    date_str = date or dt.date.today().isoformat()
    return f"{date_str}-{slugify(clean_title)}"
```

**Benefits**:
- **Idempotent**: Same input produces same output regardless of date prefix presence
- **User-friendly**: Accepts both formats gracefully
- **Backward compatible**: Works with existing usage patterns

## Use Cases

| Input | Current Output | Fixed Output |
|-------|---------------|--------------|
| `"my-feature"` | `2025-10-18-my-feature` | `2025-10-18-my-feature` ✅ |
| `"2025-10-18-my-feature"` | `2025-10-18-2025-10-18-my-feature` ❌ | `2025-10-18-my-feature` ✅ |
| `"2025-10-17-old-feature"` | `2025-10-18-2025-10-17-old-feature` ❌ | `2025-10-18-old-feature` ✅ |

## Implementation Scope

**Files to modify:**
- `scripts/openspec_new_change.py` - Update `build_change_id()` function
- `tests/test_openspec_scaffold.py` - Add test cases for date prefix handling

**Estimated effort**: 15 minutes
- Implementation: 5 minutes
- Testing: 5 minutes
- Documentation: 5 minutes

## Success Criteria

1. Script detects and strips existing date prefixes
2. Date prefix is only added once
3. All existing tests continue to pass
4. New tests cover date prefix scenarios
5. Backward compatible with existing usage

## Links

- **Related Issue**: Discovered during v0.1.4 development
- **Retrospective**: openspec/changes/2025-10-18-short-format-support/retrospective.md
- **Action Item**: Listed in v0.1.4 retrospective as "Fix scaffold script"

## Context

Describe the background and motivation.


## What Changes

List the proposed changes at a high level.


## Goals

- Goal 1: ...
- Goal 2: ...


## Stakeholders

- Owner: [owner]
- Reviewers: [reviewers]


# Technical Specification: Fix Date Prefix Duplication

## Current Implementation

```python
def build_change_id(title: str, date: Optional[str] = None, explicit_id: Optional[str] = None) -> str:
    if explicit_id:
        return explicit_id
    date_str = date or dt.date.today().isoformat()
    return f"{date_str}-{slugify(title)}"
```

**Problem**: Always prepends date, creating duplicates like `2025-10-18-2025-10-18-feature`.

## Proposed Implementation

```python
def build_change_id(title: str, date: Optional[str] = None, explicit_id: Optional[str] = None) -> str:
    if explicit_id:
        return explicit_id
    
    # Strip existing date prefix (YYYY-MM-DD-) if present
    date_pattern = r'^\d{4}-\d{2}-\d{2}-'
    clean_title = re.sub(date_pattern, '', title)
    
    date_str = date or dt.date.today().isoformat()
    return f"{date_str}-{slugify(clean_title)}"
```

**Solution**: Detect and remove existing date prefix before slugifying and adding new date.

## Test Cases

### Valid Inputs (No Date Prefix)
- `"my-feature"` → `"2025-10-18-my-feature"`
- `"Fix Bug"` → `"2025-10-18-fix-bug"`
- `"Add Feature!"` → `"2025-10-18-add-feature"`

### Valid Inputs (With Date Prefix)
- `"2025-10-18-my-feature"` → `"2025-10-18-my-feature"` (no duplicate)
- `"2025-10-17-old-feature"` → `"2025-10-18-old-feature"` (uses current date)
- `"2025-10-18-2025-10-18-already-broken"` → `"2025-10-18-already-broken"` (fixes existing)

### Edge Cases
- `"2025-my-feature"` → `"2025-10-18-2025-my-feature"` (not a valid date prefix)
- `"20251018-my-feature"` → `"2025-10-18-20251018-my-feature"` (wrong format)
- `""` → `"2025-10-18-change"` (empty title uses default)

## Regex Pattern

```python
date_pattern = r'^\d{4}-\d{2}-\d{2}-'
```

- `^` - Start of string
- `\d{4}` - Four digits (year)
- `-` - Literal hyphen
- `\d{2}` - Two digits (month)
- `-` - Literal hyphen
- `\d{2}` - Two digits (day)
- `-` - Literal hyphen (part of separator)

## Backward Compatibility

✅ **Fully backward compatible**:
- Existing calls without date prefix: unchanged behavior
- Explicit `--id` flag: unchanged (skips this logic)
- Custom `--date` flag: works as before

## Performance

- **Impact**: One additional regex operation
- **Complexity**: O(n) where n = title length
- **Typical input**: <50 characters
- **Expected overhead**: <0.1ms

## Requirements

- **R-01**: ...
- **R-02**: ...


## Acceptance Criteria

- [ ] AC-01: ...
- [ ] AC-02: ...


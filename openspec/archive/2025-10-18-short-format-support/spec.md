# Technical Specification: Short Format Support

## Overview

Extend the GitHub issue import parser to accept short format issue references (`owner/repo#number`) in addition to full URLs.

## Current Implementation

### Existing Parser Logic

```python
def parse_issue_url(url: str) -> tuple[str, str, int]:
    """Parse GitHub issue URL into owner, repo, and issue number."""
    pattern = r'github\.com/([^/]+)/([^/]+)/issues/(\d+)'
    match = re.search(pattern, url)
    
    if not match:
        raise ValueError(f"Invalid issue format: {url}")
    
    owner, repo, issue_num = match.groups()
    return owner, repo, int(issue_num)
```

**Limitations:**
- Only accepts full URLs
- Rejects short format references
- Error message doesn't guide users to correct format

## Proposed Implementation

### Enhanced Parser Logic

```python
def parse_issue_url(issue_ref: str) -> tuple[str, str, int]:
    """
    Parse GitHub issue reference into owner, repo, and issue number.
    
    Supports two formats:
    - Full URL: https://github.com/owner/repo/issues/123
    - Short format: owner/repo#123
    """
    # Try full URL format first
    url_pattern = r'github\.com/([^/]+)/([^/]+)/issues/(\d+)'
    url_match = re.search(url_pattern, issue_ref)
    
    if url_match:
        owner, repo, issue_num = url_match.groups()
        return owner, repo, int(issue_num)
    
    # Try short format: owner/repo#number
    short_pattern = r'^([^/]+)/([^/#]+)#(\d+)$'
    short_match = re.match(short_pattern, issue_ref)
    
    if short_match:
        owner, repo, issue_num = short_match.groups()
        return owner, repo, int(issue_num)
    
    # Neither format matched
    raise ValueError(
        f"Invalid issue format: {issue_ref}\n"
        f"Expected: 'owner/repo#123' or full GitHub URL"
    )
```

## Test Cases

### Valid Inputs

- `https://github.com/microsoft/vscode/issues/1` → `('microsoft', 'vscode', 1)`
- `microsoft/vscode#1` → `('microsoft', 'vscode', 1)`
- `owner/repo-name#12345` → `('owner', 'repo-name', 12345)`

### Invalid Inputs

- `microsoft/vscode` → Error (missing #number)
- `microsoft#123` → Error (missing repo)
- `#123` → Error (missing owner/repo)

## Backward Compatibility

- ✅ All existing full URL inputs continue to work
- ✅ No breaking changes to function signature
- ✅ Return type remains the same

## Requirements

- **R-01**: ...
- **R-02**: ...


## Acceptance Criteria

- [ ] AC-01: ...
- [ ] AC-02: ...


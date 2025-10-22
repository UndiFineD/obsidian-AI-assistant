# Test Plan

## Overview

This test plan validates that the implementation successfully meets all acceptance criteria.

## Testing Strategy

The testing approach validates:

1. **Structure Validation**: Verify docs/ directory structure is created correctly
2. **File Operations**: Verify files are moved and deleted as specified
3. **Root Cleanup**: Verify root directory is cleaned (≤10 files)
4. **Documentation Updates**: Verify README and links are updated
5. **Link Validation**: Verify no broken internal links
6. **OpenSpec Separation**: Verify governance files are isolated
7. **CHANGELOG Updates**: Verify cleanup is documented

## Mapping to Acceptance Criteria

- **AC-1**: All root markdown files categorized and accounted for
  - Covered by: Structure validation
  - Covered by: Directory creation tests
- **AC-2**: docs/ directory structure created with 6 subdirectories
  - Covered by: File inventory
  - Covered by: Categorization tests
- **AC-3**: 15-20 reference documentation files moved to appropriate subdirectories
  - Covered by: File move operations
  - Covered by: Reference file tests
- **AC-4**: 20-30 celebration/status/self-reporting files deleted
  - Covered by: File deletion
  - Covered by: Celebration file removal tests
- **AC-5**: Root directory contains ≤10 files (down from 30+)
  - Covered by: Root directory check
  - Covered by: File count validation
- **AC-6**: README.md updated with new documentation structure and navigation
  - Covered by: README updates
  - Covered by: Documentation structure tests
- **AC-7**: All internal links validated and updated (no 404s)
  - Covered by: Link validation
  - Covered by: Reference integrity tests
- **AC-8**: docs/README.md created with clear navigation guide
  - Covered by: docs/README.md creation
  - Covered by: Navigation guide tests

## Test Suites

### 1. Directory Structure Validation
- [ ] docs/ directory exists
- [ ] docs/getting-started/ subdirectory exists
- [ ] docs/guides/ subdirectory exists
- [ ] docs/architecture/ subdirectory exists
- [ ] docs/reference/ subdirectory exists
- [ ] docs/production/ subdirectory exists
- [ ] docs/historical/ subdirectory exists
- [ ] docs/README.md exists and is readable

### 2. File Deletion Validation

### 3. File Move Validation

### 4. Root Directory Cleanup
- [ ] Root directory contains ≤10 essential files
- [ ] No extraneous markdown files in root

### 5. Documentation Updates
- [ ] README.md updated with docs/ navigation
- [ ] README.md has getting-started link
- [ ] README.md has guides link
- [ ] README.md has architecture link
- [ ] docs/README.md created with full navigation
- [ ] Contributing.md updated with new structure

### 6. Link Validation
- [ ] No broken relative links in README.md
- [ ] No broken relative links in docs/README.md
- [ ] No broken relative links in docs/ subdirectories
- [ ] All cross-document links valid

### 7. OpenSpec Separation
- [ ] openspec/ files remain unchanged
- [ ] openspec/ files not in root directory
- [ ] openspec/ path references correct in documentation

### 8. CHANGELOG Updates
- [ ] CHANGELOG.md documents cleanup change
- [ ] CHANGELOG.md lists deleted file categories
- [ ] CHANGELOG.md documents new docs/ structure


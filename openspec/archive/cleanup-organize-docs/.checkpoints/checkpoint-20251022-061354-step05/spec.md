# Specification

## Overview

This specification documents the acceptance criteria and requirements for the change.

## Acceptance Criteria

- **AC-1**: All root markdown files categorized and accounted for
- **AC-2**: docs/ directory structure created with 6 subdirectories
- **AC-3**: 15-20 reference documentation files moved to appropriate subdirectories
- **AC-4**: 20-30 celebration/status/self-reporting files deleted
- **AC-5**: Root directory contains ≤10 files (down from 30+)
- **AC-6**: README.md updated with new documentation structure and navigation
- **AC-7**: All internal links validated and updated (no 404s)
- **AC-8**: docs/README.md created with clear navigation guide
- **AC-9**: Contributing guidelines reference docs/ structure
- **AC-10**: OpenSpec files remain unchanged and isolated in openspec/
- **AC-11**: Git history preserves all deleted content
- **AC-12**: New contributors spend <2 minutes finding relevant documentation

## Implementation Requirements

### Directory Structure
- Create `docs/` directory with subdirectories:
  - docs/getting-started/
  - docs/guides/
  - docs/architecture/
  - docs/reference/
  - docs/production/
  - docs/historical/
- Create docs/README.md with navigation

### File Operations

### Documentation Updates
- Update README.md with docs/ navigation
- Update all internal links
- Validate no broken links
- Update CHANGELOG.md to document cleanup
- Update Contributing guidelines with new structure

## Implementation Phases

### Phase 1: Inventory & Categorization

Audit all root markdown files and categorize by type:
- Document each file's purpose and value
- Identify self-reporting/celebration files (no operational value)
- Map user-facing guides and references
- Create categorization matrix (KEEP / MOVE / DELETE)

## Requirements

- **R-01**: ...
- **R-02**: ...


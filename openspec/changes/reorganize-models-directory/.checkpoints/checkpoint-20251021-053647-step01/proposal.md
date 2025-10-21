# Proposal: Reorganize Models Directory

## Context

The current architecture places AI models in the `backend/models/` directory, but there are
organizational issues with the existing structure. Models should be accessible from the
top-level directory to follow standard ML project conventions and improve accessibility
for deployment configurations.

## Why

1. **Consistency with ML Best Practices**: Standard ML projects keep models at the top level
2. **Simplified Access**: Deployment scripts and configuration can reference models more clearly
3. **Better Organization**: Separates models from backend code, making the structure clearer
4. **CI/CD Efficiency**: Easier to version and cache models separately from code
5. **Onboarding**: New developers understand the structure more intuitively

## What Changes

- Move models from `backend/models/` to top-level `models/` directory
- Update all import paths and references throughout backend and plugin code
- Update configuration files to reference the new path
- Ensure CI/CD pipelines correctly handle the new structure
- Update documentation to reflect new directory layout

## Impact

- **Complexity**: Low - primarily file movements and path updates
- **Risk**: Low - changes are isolated to configuration and imports
- **Breaking Changes**: Yes - requires path updates throughout codebase
- **Performance**: No impact expected
- **Security**: No security implications

## Goals

- Goal 1: Successfully reorganize models directory without breaking functionality
- Goal 2: Update all references consistently across backend and plugin
- Goal 3: Improve project structure clarity and maintainability
- Goal 4: Ensure CI/CD compatibility with new structure

## Stakeholders

- Owner: @Keimpe de Jong
- Reviewers: AI Team
- Affected: Backend, Plugin, CI/CD

## Timeline

- Proposed: October 2025
- Implementation: Current sprint
- Testing: 1-2 days
- Deployment: Next release

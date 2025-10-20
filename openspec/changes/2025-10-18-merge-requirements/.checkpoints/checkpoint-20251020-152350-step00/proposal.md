# Proposal: Merge Requirements Files and Improve Dependency Management

## Problem Statement
The project currently has multiple requirements files (`requirements.txt`, `requirements-dev.txt`, `requirements-ml.txt`) which creates:
- Confusion about which file to install from
- Duplicate package declarations across files
- Maintenance overhead when updating dependencies
- Inconsistent dependency management across environments

## Motivation
- **Simplicity**: Single source of truth for all project dependencies
- **Maintainability**: Easier to audit, update, and manage versions
- **Clarity**: Clear categorization of dependencies by purpose
- **Deduplication**: Eliminate duplicate package entries

## Proposed Solution
Merge all requirements files into a single `requirements.txt` with clear categorical organization:
1. Core dependencies (FastAPI, Pydantic, etc.)
2. AI/ML dependencies (GPT4All, transformers, etc.)
3. Vector database dependencies (ChromaDB, etc.)
4. Development tools (pytest, coverage, etc.)
5. Security & validation tools (bandit, safety, etc.)

## Alternatives Considered
1. **Keep separate files**: Rejected - adds complexity without clear benefits
2. **Use pyproject.toml**: Considered for future - requires build system changes
3. **Use requirements/*.txt structure**: Over-engineered for current project size

## Impact Analysis
- **Positive**: Simpler onboarding, cleaner dependency management, less duplication
- **Risk**: Minimal - all dependencies remain the same, just reorganized
- **Migration**: None required - existing setup scripts already use requirements.txt

## Success Criteria
- Single requirements.txt with all dependencies
- No duplicate package entries
- Clear categorical grouping with comments
- All tests pass after merge
- Setup scripts work without modification

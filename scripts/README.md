# Scripts Directory

This directory contains utility scripts for development, validation, and maintenance tasks.

## Validation Scripts

These scripts validate the structure, syntax, and basic functionality of various backend components.
They are **not** pytest tests but standalone verification tools used during development.

### Infrastructure Validation

- **`validate_caching.py`** - Validates caching system structure and integration
- **`validate_enhanced_caching.py`** - Validates enhanced caching implementation with multi-level cache
- **`validate_error_handling.py`** - Quick validation of error handling integration
- **`validate_error_handling_integration.py`** - Comprehensive error handling validation
- **`validate_logging.py`** - Validates logging framework structure and configuration
- **`validate_security_hardening.py`** - Validates security hardening middleware and features
- **`validate_security.py`** - General security validation
- **`validate_dependencies.py`** - Validates project dependencies

### Usage

Run validation scripts directly with Python:

```bash
# Validate caching implementation
python scripts/validate_caching.py

# Validate error handling
python scripts/validate_error_handling.py

# Validate security hardening
python scripts/validate_security_hardening.py
```

### Development Scripts

- **`analyze_coverage.py`** - Analyze test coverage reports
- **`auto_fix_issues.py`** - Automatically fix common code issues
- **`clean_nonprintable.py`** - Clean non-printable characters from files
- **`code_quality_improvements.py`** - Apply code quality improvements
- **`dependency_manager.py`** - Manage project dependencies
- **`find_broken_files.py`** - Find files with syntax or structural issues
- **`find_missing_impact.py`** - Find missing impact analysis in changes
- **`fix_dependencies.py`** - Fix dependency issues
- **`fix_empty_blocks.py`** - Fix empty code blocks
- **`fix_indentation.py`** - Fix indentation issues
- **`fix_markdown_lint.py`** - Fix markdown linting issues
- **`fix_removed_markers.py`** - Fix removed markers in code
- **`fix_spec_format.py`** - Fix specification format issues
- **`generate_changelog.py`** - Generate changelog from commits
- **`generate_openspec_changes.py`** - Generate OpenSpec change proposals
- **`probe_cors.py`** - Test CORS configuration
- **`remove_bad_pass.py`** - Remove empty pass statements
- **`repair_openspec_changes.py`** - Repair OpenSpec change files
- **`restore_backups.py`** - Restore files from backups
- **`run_dependency_audit.py`** - Audit project dependencies for security
- **`run_tests.py`** - Run test suite with options
- **`run_tests_safe.py`** - Run tests with enhanced safety checks
- **`security_scanner.py`** - Scan code for security issues
- **`update_test_metrics.py`** - Update test metrics and reports
- **`version_manager.py`** - Manage project versioning

### OpenSpec Scripts

- **`openspec-validate.ps1`** - PowerShell script to validate OpenSpec changes
- **`workflow.ps1`** - Comprehensive OpenSpec workflow automation (see below)

## OpenSpec Workflow Automation (`workflow.ps1`)

Automates the 13-stage OpenSpec workflow for change management.

### Quick Start

```powershell
# List all active changes
.\scripts\workflow.ps1 -List

# Create a new change and run interactively
.\scripts\workflow.ps1 -ChangeId "update-doc-readme" -Title "Update README.md" -Owner "@johndoe"

# Run a specific workflow step
.\scripts\workflow.ps1 -ChangeId "update-doc-readme" -Step 8

# Validate a change structure
.\scripts\workflow.ps1 -ChangeId "update-doc-readme" -Validate

# Archive a completed change
.\scripts\workflow.ps1 -ChangeId "update-doc-readme" -Archive

# Dry run (preview without making changes)
.\scripts\workflow.ps1 -ChangeId "my-change" -DryRun
```

### Workflow Steps

The script implements all 13 stages defined in `openspec/PROJECT_WORKFLOW.md`:

0. **Create TODOs** - Initialize workflow tracking
1. **Increment Release Version** - Update version numbers [HARD REQUIREMENT]
2. **Proposal** - Create proposal.md with problem statement
3. **Specification** - Define technical requirements
4. **Task Breakdown** - Create tasks.md with actionable items
5. **Test Definition** - Create test_plan.md
6. **Script & Tooling** - Update automation scripts
7. **Implementation** - Execute the changes
8. **Test Run & Validation** - Run tests and validate
9. **Documentation Update** - Update docs and changelog
10. **Git Operations** - Commit and push changes
11. **Archive Completed Change** - Move to archive/
12. **Create Pull Request** - Open PR on GitHub

### Parameters

- **`-ChangeId`**: Unique identifier for the change (kebab-case)
- **`-Title`**: Human-readable title (auto-generated if not provided)
- **`-Owner`**: GitHub handle (auto-detected from git config if not provided)
- **`-Step`**: Execute a specific step (0-12)
- **`-DryRun`**: Preview actions without making changes
- **`-Validate`**: Check change structure
- **`-Archive`**: Archive a completed change
- **`-List`**: Show all active changes with progress

### Examples

```powershell
# Create and run full workflow
.\scripts\workflow.ps1 -ChangeId "add-new-feature" -Title "Add New Feature" -Owner "@me"

# Resume from step 8 (Test Run & Validation)
.\scripts\workflow.ps1 -ChangeId "add-new-feature" -Step 8

# Check progress of all changes
.\scripts\workflow.ps1 -List

# Archive a completed change
.\scripts\workflow.ps1 -ChangeId "update-doc-readme" -Archive
```

### Features

- **Template Generation**: Auto-creates proposal.md, tasks.md, test_plan.md from templates
- **Progress Tracking**: Updates todo.md checkboxes automatically
- **Git Integration**: Automates git add, commit, push operations
- **Color-Coded Output**: Clear visual feedback (✓ success, ⚠ warning, ✗ error)
- **Error Handling**: Validates inputs and provides helpful error messages
- **Dry Run Mode**: Preview actions without making changes
- **Flexible Execution**: Run full workflow or individual steps

### Related Documentation

- `openspec/PROJECT_WORKFLOW.md` - Complete workflow specification
- `openspec/AGENTS.md` - Governance guide
- `openspec/README.md` - OpenSpec overview
- `.github/copilot-instructions.md` - AI agent instructions

## Note on Validation vs. Testing

- **Validation scripts** (`validate_*.py`) - Standalone scripts for quick verification during development
- **Test files** (`tests/**/*`) - Pytest-based automated tests for CI/CD pipeline

Validation scripts are useful for:
- Quick sanity checks during development
- Debugging new implementations
- Verifying file structure and syntax before committing
- Development workflow validation

For automated testing and CI/CD, use the pytest test suite in the `tests/` directory.

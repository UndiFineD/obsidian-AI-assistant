# Scripts Directory

This directory contains utility scripts for development, validation, and maintenance tasks.

## Validation Scripts

These scripts validate the structure, syntax, and basic functionality of various backend components. They are **not** pytest tests but standalone verification tools used during development.

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

## Note on Validation vs. Testing

- **Validation scripts** (`validate_*.py`) - Standalone scripts for quick verification during development
- **Test files** (`tests/**/*`) - Pytest-based automated tests for CI/CD pipeline

Validation scripts are useful for:
- Quick sanity checks during development
- Debugging new implementations
- Verifying file structure and syntax before committing
- Development workflow validation

For automated testing and CI/CD, use the pytest test suite in the `tests/` directory.

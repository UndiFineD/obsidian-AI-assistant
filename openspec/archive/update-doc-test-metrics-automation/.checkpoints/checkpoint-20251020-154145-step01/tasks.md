# Tasks: update-doc-test-metrics-automation

## 1. Implementation

- [x] 1.1 Fix Unicode escape issue in `scripts/update_test_metrics.py` docstring
- [x] 1.2 Test automation script with `--skip-pytest` and dry-run mode
- [x] 1.3 Create `.github/workflows/update-test-metrics.yml` with scheduled/manual triggers
- [x] 1.4 Add comprehensive automation documentation to `docs/TESTING_GUIDE.md`

## 2. Validation

- [x] 2.1 Verify dry-run output matches expected format
- [x] 2.2 Run OpenSpec validation tests (17/17 passed)
- [x] 2.3 Validate CI workflow syntax and structure
- [x] 2.4 Test automation script with current metrics

## 3. Documentation

- [x] 3.1 Document all CLI flags and options
- [x] 3.2 Add CI/CD integration examples
- [x] 3.3 Include troubleshooting section
- [x] 3.4 Provide best practices for automation usage

## 4. OpenSpec Compliance

- [x] 4.1 Create change proposal with capability declaration
- [x] 4.2 Add spec delta with governance language
- [x] 4.3 Validate capability consistency across files
- [x] 4.4 Ensure spec delta has required sections (ADDED Requirements, scenarios)

## 5. Validation Command

```bash
# Validate OpenSpec compliance
openspec validate update-doc-test-metrics-automation --strict

# Test automation script
python scripts/update_test_metrics.py --skip-pytest --passed 691 --skipped 2 --duration "3m19s"

# Full test suite
python -m pytest tests/ -v
```

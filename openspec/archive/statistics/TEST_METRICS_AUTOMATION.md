# Test Metrics Automation Documentation

## Overview

The test metrics automation system automatically updates test results, coverage, benchmarks, and execution trends
across all project documentation while maintaining OpenSpec governance compliance.

## Key Features

### 1. Automated Metrics Collection

- **Test Results**: Passes, skips, failures from pytest execution

- **Code Coverage**: Percentage from htmlcov/index.html

- **Execution Time**: Test suite duration with trend analysis

- **Benchmark Metrics**: Performance data from pytest-benchmark (when available)

### 2. Historical Tracking

- **Test Run History**: Maintains last 10 test runs in `.test_metrics_history.json`

- **Execution Trends**: Compares current vs. previous run (improvement/regression)

- **Coverage Trends**: Tracks coverage changes over time

### 3. Documentation Updates

- **README.md**: Test badges, statistics, and latest run info

- **docs/TEST_RESULTS_OCTOBER_2025.md**: Comprehensive test breakdown with trends

- **docs/SYSTEM_STATUS_OCTOBER_2025.md**: System health status

### 4. OpenSpec Governance

- **Auto-scaffolding**: Creates compliant OpenSpec change directories

- **Validation**: Runs `openspec validate` after each update

- **Compliance**: Ensures all changes follow governance requirements

## Usage

### Basic Usage (Dry Run)

```powershell
python scripts/update_test_metrics.py
```
Shows preview of changes without applying them.

### Apply Changes

```powershell
python scripts/update_test_metrics.py --apply
```
Runs pytest, collects metrics, and updates all documentation.

### Manual Metrics Entry

```powershell
python scripts/update_test_metrics.py --apply --skip-pytest --passed 686 --skipped 0 --duration 120.31s --date
2025-10-15 --coverage 100.0
```
Updates documentation with provided metrics without running pytest.

### CI/CD Integration

```yaml

# .github/workflows/test-metrics.yml

- name: Update Test Metrics
  run: |
    python -m pytest --cov=backend --cov-report=html
    python scripts/update_test_metrics.py --apply
```

## Command-Line Arguments

| Argument | Description | Required | Default |
|----------|-------------|----------|---------|
| `--apply` | Apply changes to files | No | False (dry-run) |
| `--skip-pytest` | Use provided metrics instead of running pytest | No | False |
| `--passed` | Number of passed tests | With --skip-pytest | Auto-detected |
| `--skipped` | Number of skipped tests | No | 0 |
| `--duration` | Test execution duration (e.g., "120.31s") | With --skip-pytest | Auto-detected |
| `--date` | Date for metrics (YYYY-MM-DD) | No | Today |
| `--coverage` | Coverage percentage | No | Auto-detected |

## File Structure

### Generated Files

```
docs/
├── .test_metrics_prev.json          # Previous run for trend comparison
├── .test_metrics_history.json       # Last 10 test runs
├── TEST_RESULTS_OCTOBER_2025.md     # Updated with latest metrics
└── SYSTEM_STATUS_OCTOBER_2025.md    # Updated system status

openspec/changes/
└── update-doc-docs-test-results-auto-YYYY-MM-DD/
    ├── proposal.md                   # Change proposal
    ├── tasks.md                      # Implementation tasks
    └── specs/
        └── project-documentation/
            └── spec.md               # Spec delta
```

### Data Formats

#### .test_metrics_prev.json

```json
{
  "duration": "120.31s",
  "date": "2025-10-15"
}
```

#### .test_metrics_history.json

```json
[
  {
    "date": "2025-10-15",
    "passed": 686,
    "skipped": 0,
    "duration": "120.31s",
    "coverage": "100.0"
  }
]
```

## Metrics Extraction Logic

### Coverage Parsing

Extracts coverage percentage from `htmlcov/index.html`:
```python
<span class="pc_cov">85%</span>  # Parsed as "85%"
```

### Benchmark Metrics

Extracts from `.benchmarks/latest/results.json`:

- Min/Max/Mean execution time

- Standard deviation

- Number of rounds

- Benchmark name

### Execution Time Trends

Compares current vs. previous run:

- **Improved**: Faster execution (green indicator)

- **Regressed**: Slower execution (yellow indicator)

- **No change**: <0.01s difference

## OpenSpec Integration

### Auto-generated Change Structure

Each metrics update creates:

1. **proposal.md**: Change rationale and impact

1. **tasks.md**: Implementation and validation checklist

1. **spec.md**: ADDED requirements with scenarios

### Validation

Post-update validation ensures:

- Spec deltas contain MUST/SHALL keywords

- All scenarios have GIVEN/WHEN/THEN format

- Capability is set to `project-documentation`

### Compliance Commands

```powershell

# Validate specific change

openspec validate update-doc-docs-test-results-auto-2025-10-15 --strict

# View change deltas

openspec change show update-doc-docs-test-results-auto-2025-10-15 --json --deltas-only
```

## Troubleshooting

### Common Issues

#### Coverage Not Detected

**Symptom**: Coverage shows "N/A"
**Solution**: Run `pytest --cov=backend --cov-report=html` first

#### Benchmark Metrics Missing

**Symptom**: "No benchmark metrics available."
**Solution**: Ensure pytest-benchmark is installed and tests use `@pytest.mark.benchmark`

#### OpenSpec Validation Failed

**Symptom**: Requirements missing SHALL/MUST
**Solution**: Auto-generated specs include MUST; validation warnings are cosmetic

#### Duplicate Entries in History

**Symptom**: Same date appears multiple times
**Solution**: Script automatically deduplicates by date; run once per day

### Debug Mode

View changes without applying:
```powershell
python scripts/update_test_metrics.py
```

## Performance

### Execution Time Targets

- **Metrics Collection**: <2s

- **Coverage Parsing**: <0.5s

- **Benchmark Extraction**: <0.1s

- **Documentation Updates**: <1s

- **OpenSpec Scaffolding**: <0.5s

- **Total**: <5s

### Resource Usage

- **Memory**: <50MB

- **Disk I/O**: Minimal (reads 3 files, writes 6 files)

- **Network**: None (fully offline)

## Best Practices

### Daily Updates

Run after significant test suite changes:
```powershell
python -m pytest --cov=backend --cov-report=html
python scripts/update_test_metrics.py --apply
```

### CI/CD Integration

Add to GitHub Actions workflow:
```yaml

- name: Update Metrics
  run: python scripts/update_test_metrics.py --apply

- name: Commit Updates
  run: |
    git config user.name "github-actions"
    git add docs/ openspec/
    git commit -m "chore: update test metrics [skip ci]"
```

### Manual Review

Always review changes before committing:
```powershell
git diff docs/
git diff openspec/changes/
```

## Future Enhancements

### Planned Features

- [ ] Performance regression alerts

- [ ] Coverage trend visualization

- [ ] Benchmark comparison charts

- [ ] Automated changelog generation

- [ ] Slack/Discord notifications

- [ ] Historical metrics dashboard

### Integration Opportunities

- Jenkins/GitLab CI support

- Prometheus metrics export

- Grafana dashboard templates

- JSON API for metrics query

## Contributing

### Adding New Metrics

1. Add extraction function in metrics extraction section

1. Update `main()` to call new function

1. Add documentation update logic

1. Update this documentation

### Modifying OpenSpec Structure

1. Update `scaffold_openspec_change()` function

1. Test with `openspec validate`

1. Update compliance documentation

## Support

For issues or questions:

- **GitHub Issues**: obsidian-AI-assistant repository

- **Documentation**: See `docs/COMPREHENSIVE_SPECIFICATION.md`

- **OpenSpec**: See `openspec/AGENTS.md`

## Changelog

### 2025-10-15

- ✅ Initial automation script implementation

- ✅ Historical tracking with `.test_metrics_history.json`

- ✅ Execution time trend analysis

- ✅ Benchmark metrics integration

- ✅ OpenSpec auto-scaffolding

- ✅ Post-update validation

- ✅ Comprehensive documentation

---

**Last Updated**: 2025-10-15
**Maintainer**: Development Team
**Status**: Production Ready ✅

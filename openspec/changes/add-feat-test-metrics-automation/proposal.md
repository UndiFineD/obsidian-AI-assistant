# Change Proposal: add-feat-test-metrics-automation

## Why

Manual updates of test metrics across multiple documentation files are error-prone and time-consuming. We need automated tooling to ensure consistency and reduce maintenance burden.

Capability: project-documentation

## What Changes

- **Automation Script**: Enhanced `scripts/update_test_metrics.py` with pytest execution, file updating, and OpenSpec scaffolding
- **CI/CD Workflow**: New `.github/workflows/update-test-metrics.yml` for scheduled and manual test metrics updates
- **Documentation**: Comprehensive automation guide in `docs/TESTING_GUIDE.md` with usage examples and troubleshooting

## Impact

- **Consistency**: Automated updates ensure all documentation files stay synchronized
- **Efficiency**: Reduces manual effort from ~15 minutes to <1 minute per update
- **Governance**: Built-in OpenSpec compliance with `--scaffold-openspec` flag
- **Quality**: Eliminates human error in metric transcription
- **CI Integration**: Enables automated weekly updates or on-demand triggers

This change supports OpenSpec governance by automating the creation of compliant change directories for documentation updates.

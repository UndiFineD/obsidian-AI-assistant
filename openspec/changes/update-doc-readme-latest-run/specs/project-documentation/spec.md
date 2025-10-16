# Spec Delta: project-documentation / update-doc-readme-latest-run

## MODIFIED Requirements

### Requirement: Governance for README.md

The project SHALL govern material changes to `README.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change requires proposal

- **WHEN** a contributor plans a material update to `README.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: Keep README test status current

- **WHEN** a new full-suite test run completes and counts or timing change
- **THEN** `README.md` SHALL be updated to match the latest status within 24 hours and remain consistent with `docs/SYSTEM_STATUS_OCTOBER_2025.md` and `docs/TEST_RESULTS_OCTOBER_2025.md`

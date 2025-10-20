# OpenSpec Best Practices Checklist

This checklist helps contributors and reviewers ensure high-quality,
consistent OpenSpec documentation and change proposals.

## For Contributors

- [ ] Use SHALL or MUST in every requirement statement
- [ ] Provide at least one scenario per requirement (#### Scenario: ...)
- [ ] Use WHEN/THEN format for scenarios
- [ ] Match requirement names exactly for MODIFIED/REMOVED deltas
- [ ] Include complete requirement text for MODIFIED deltas
- [ ] Use correct delta headers (## ADDED, ## MODIFIED, ## REMOVED, ## RENAMED)
- [ ] Validate with `openspec validate --strict` before submitting
- [ ] Pass markdown linting (no formatting errors)
- [ ] Complete proposal.md (Why/What/Impact)
- [ ] Complete tasks.md (implementation checklist)
- [ ] Keep changes focused (one logical change per proposal)
- [ ] Reference related docs and examples

## For Reviewers

- [ ] Confirm all requirements use normative language (SHALL/MUST)
- [ ] Check for ≥1 scenario per requirement
- [ ] Verify scenario format (#### Scenario: ...)
- [ ] Ensure MODIFIED deltas have full requirement text and all scenarios
- [ ] Confirm requirement names match baseline exactly
- [ ] Validate file structure and directory naming
- [ ] Review proposal.md for clarity and impact
- [ ] Review tasks.md for completeness and validation steps
- [ ] Check cross-references and links
- [ ] Validate with strict mode and markdown lint
- [ ] Provide actionable feedback and request fixes as needed

## Common Pitfalls

- Using MODIFIED without full requirement text
- Missing SHALL/MUST in requirements
- Scenario format errors (wrong heading, missing colon)
- Incomplete tasks or proposal sections
- Multiple unrelated changes in one proposal
- Typos in requirement names (causes validation failure)

## References

- [Contributor Guide](./contributor-guide.md)
- [Troubleshooting Guide](./troubleshooting.md)
- [Change Patterns](./change-patterns.md)
- [Sample Change Proposal](../changes/update-doc-sample-change-demo/)
- [Governance Overview](../README.md)

---

**Last Updated:** October 16, 2025

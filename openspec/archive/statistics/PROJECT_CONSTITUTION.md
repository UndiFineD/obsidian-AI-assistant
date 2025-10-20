# Obsidian AI Assistant Project Constitution

## Governance Notice

This document is governed by OpenSpec documentation governance. Material changes
must be proposed via `openspec/changes/` with deltas under the `project-documentation`
capability. See `openspec/AGENTS.md` for the workflow. Changes include governance
principles, decision-making processes, roles, responsibilities, and community standards.

## 1. Mission and Scope

The Obsidian AI Assistant project aims to deliver a secure, scalable, and
extensible AI-powered assistant for Obsidian users, integrating advanced
language models, voice recognition, and knowledge management features.

### Success Metrics
- **Adoption**: 5,000+ active users within 12 months
- **Quality**: 95%+ test pass rate, 85%+ code coverage
- **Performance**: SLA targets met (Tier 1-5 response times)
- **Security**: Zero critical vulnerabilities in production
- **Community**: Active contributor base with regular submissions

## 2. Governance Structure

### Roles and Responsibilities

#### Project Lead
- **Authority**: Final decision-making authority; resolves governance disputes
- **Responsibilities**:
    - Oversee project direction and strategic alignment
    - Approve major architectural decisions
    - Resolve escalated conflicts
    - Ensure compliance with constitution
- **Accountability**: Quarterly governance review with core maintainers
- **Term**: Indefinite (until succession planned or voluntary step-down)

#### Core Maintainers
- **Authority**: Approve PRs, manage releases, define code standards
- **Responsibilities**:
    - Code review and quality gates
    - Release management and versioning
    - Security vulnerability response
    - Mentoring new contributors
    - Maintaining code quality standards
- **Minimum count**: 2 (ensures continuity)
- **Selection**: Nomination by existing maintainers + Project Lead approval
- **Performance review**: Annually

#### Contributors
- **Authority**: Submit proposals, code, documentation, and ideas
- **Responsibilities**:
    - Follow contribution standards and code of conduct
    - Include tests and documentation with submissions
    - Respond to review feedback
    - Participate in community discussions
- **Support**: Access to issue tracker, discussions, and documentation

#### Security Advisors
- **Authority**: Review security-sensitive changes; advise on threat models
- **Responsibilities**:
    - Conduct security reviews for critical changes
    - Advise on cryptography, authentication, compliance
    - Perform or coordinate security audits
    - Respond to security incident reports
- **Selection**: Expert recommendation + Project Lead approval
- **Meeting frequency**: Quarterly or as-needed

#### Documentation Advisors
- **Authority**: Oversee documentation governance via OpenSpec
- **Responsibilities**:
    - Review documentation proposals and quality
    - Maintain consistency across documentation
    - Advise on governance processes
    - Ensure compliance with OpenSpec requirements
- **Selection**: Nomination from contributor base + Core Maintainer approval

#### Enterprise Advisors (if enterprise features enabled)
- **Authority**: Advise on multi-tenant, compliance, and enterprise features
- **Responsibilities**:
    - Review enterprise architecture decisions
    - Advise on GDPR, SOC2, HIPAA compliance
    - Guide role-based access control and tenant isolation
    - Recommend enterprise security practices
- **Selection**: Enterprise expertise requirement + Project Lead approval

## 3. Decision-Making Process

### Decision Categories and Authorities

#### Category A: Strategic Decisions (Project Lead + Consensus)
**Timeframe**: 7-14 days for discussion, final decision within 21 days

Examples:
- Project mission or scope changes
- New major capabilities or features
- Sunset or deprecation of major features
- Breaking API changes
- License or legal matters
- Community governance changes
- Long-term roadmap direction

**Process**:
1. Proposal issued with rationale and impact assessment
2. Public discussion period (7 days minimum)
3. Vote among core maintainers (consensus required = 100% agreement)
4. Project lead makes final decision if consensus not reached within 14 days
5. Decision documented in project governance log

#### Category B: Technical Decisions (Core Maintainers, 2+ Required)
**Timeframe**: 3-7 days for review, decision within 10 days

Examples:
- Architecture changes
- Performance optimizations
- API design decisions
- Test strategy changes
- Security improvements
- Dependency updates

**Process**:
1. Technical proposal with design rationale
2. Core maintainers review (minimum 2 required for approval)
3. Community comment period (3 days)
4. Final approval or iteration
5. Implementation tracking

#### Category C: Minor Changes (Any Core Maintainer)
**Timeframe**: Same-day to 3 days

Examples:
- Bug fixes
- Documentation updates (non-governance)
- Code style improvements
- Test additions
- Performance tuning
- Dependency patch updates

**Process**:
1. PR submission with clear description
2. Single core maintainer review required
3. Automated tests must pass
4. Merge upon approval

#### Category D: Emergency Decisions (Project Lead + 1 Core Maintainer)
**Timeframe**: Immediate (within hours)

Examples:
- Critical security vulnerabilities
- Production outages
- Data loss prevention
- Immediate compliance violations

**Process**:
1. Emergency declared by discoverer
2. Project lead and any available core maintainer convene
3. Decision made and implemented immediately
4. Post-incident review within 48 hours
5. Full governance process for permanent fixes

### Dispute Resolution

**Escalation Path**:
1. **Level 1**: Attempt resolution through discussion (3 days)
2. **Level 2**: Request mediation from another core maintainer (5 days)
3. **Level 3**: Project lead final decision (within 7 days)
4. **Level 4**: If Project Lead involved: external arbitrator (if major impact)

**Documentation**: All disputes and resolutions logged in `docs/GOVERNANCE_LOG.md`

**Appeals**: After 30 days, disputes can be reopened if new evidence emerges

## 4. Contribution Guidelines

### Submission Requirements

All contributions must:

- Follow the [Code of Conduct](#5-code-of-conduct)
- Adhere to [Contribution Standards](#6-contribution-standards)
- Include tests with ≥85% coverage for backend code
- Include documentation (code comments, docstrings, guides)
- Pass OpenSpec governance validation (for doc changes)
- Reference related issues or discussions

### Contribution Process

**Before Implementation**:
- Check existing issues to avoid duplication
- For major features: discuss in GitHub Discussions first
- For documentation: verify OpenSpec governance requirements
- Get agreement on approach from at least one core maintainer

**During Development**:
- Create feature branch from `main`
- Make commits with clear messages (see commit standards)
- Keep PR focused on single concern
- Update tests as you code, not after
- Keep PR ≤400 lines when possible (split if larger)

**Review and Approval**:
- PR requires at least one core maintainer review
- Address review feedback within 7 days or PR will be closed
- All CI checks must pass (tests, linting, security)
- For enterprise features: enterprise advisor review required
- Maintainer approval is final gate before merge

**After Merge**:
- Contributor credited in CHANGELOG.md (if major)
- Changes released in next scheduled release
- Contributor added to acknowledgments section

### Contribution Tiers

#### Tier 1: Minor Contributions (Typos, style fixes)
- **Review time**: 1-2 days
- **Approval**: Single core maintainer
- **Testing**: Minimal
- **Documentation**: Not required

#### Tier 2: Moderate Contributions (Bug fixes, small features)
- **Review time**: 3-5 days
- **Approval**: One core maintainer + CI pass
- **Testing**: Unit + integration tests required
- **Documentation**: Code-level required, user guide optional

#### Tier 3: Major Contributions (New features, architecture)
- **Review time**: 7-14 days
- **Approval**: Two core maintainers + Project Lead for strategy
- **Testing**: 85%+ coverage required
- **Documentation**: Full guide + API docs + examples
- **Discussion**: GitHub Discussions recommended before starting

#### Tier 4: Strategic Contributions (New capabilities, governance)
- **Review time**: 14-21 days
- **Approval**: All core maintainers + Project Lead
- **Testing**: Comprehensive (unit, integration, load, security)
- **Documentation**: Complete with governance implications
- **Process**: OpenSpec governance required

## 5. Code of Conduct

- Be respectful, inclusive, and collaborative.

- No harassment, discrimination, or abusive language.

- Report violations to the project lead or core maintainers.

## 6. Contribution Standards

### Code Quality Standards

#### Python Backend
- **Style**: PEP 8 compliant, 88-character line limit (Black formatter)
- **Type Hints**: Required for all public functions and methods
- **Linting**: Pass `ruff` checks (E, F, W, C, I rules)
- **Security**: Pass `bandit` security scan
- **Testing**: ≥85% code coverage; 95%+ for security-critical code
- **Performance**: Must not exceed SLA targets (Tiers 1-5)
- **Imports**: Organized with `isort`

#### JavaScript Plugin
- **Style**: 4-space indentation, double quotes, 100-char line limit
- **Naming**: PascalCase for classes, camelCase for functions/variables
- **Error Handling**: Try-catch blocks with descriptive messages
- **Documentation**: JSDoc comments for public functions
- **No Build Step**: Vanilla JavaScript, ready-to-use files
- **Testing**: 90%+ code quality validation

#### Documentation
- **Markdown**: Comply with markdownlint (MD013 = 120-char limit)
- **Clarity**: Plain language, avoid jargon
- **Structure**: Use headings, bullet lists, code blocks
- **Examples**: Include practical examples for complex topics
- **Cross-references**: Link to related docs
- **Accessibility**: Descriptive alt text for images, semantic HTML

### Performance Requirements

**Contribution must not degrade these SLA targets**:

| Tier | Target | Examples |
|------|--------|----------|
| T1 | <100ms | Health, status, config |
| T2 | <500ms | Cached asks, simple search |
| T3 | <2s | AI generation, document search |
| T4 | <10s | Web analysis, complex ops |
| T5 | <60s | Vault reindex, model loading |

**For contributions that affect Tier 1-2**:
- Benchmark before and after
- Include performance test in PR
- Document any optimizations

### Accessibility Requirements

- **WCAG 2.1 AA Compliance**: Minimum standard for UI changes
- **Keyboard Navigation**: All features usable without mouse
- **Screen Reader**: Support for assistive technologies
- **Color Contrast**: ≥4.5:1 for normal text
- **Font Size**: Minimum 14px for body text
- **Testing**: Manual accessibility testing for UI changes

### Security Standards

- **Input Validation**: All external inputs validated with Pydantic
- **Authentication**: JWT tokens with secure expiration
- **Authorization**: Role-based access control (RBAC)
- **Encryption**: TLS 1.2+ for all network communication
- **Secrets**: Never commit API keys, tokens, or credentials
- **Dependencies**: No security-flagged dependencies
- **Logging**: No sensitive data in logs
- **SQL Injection**: Use parameterized queries (not applicable yet)

### API Stability Guarantees

- **Major Version**: Breaking changes allowed, 6-month deprecation period
- **Minor Version**: New features, backward compatible
- **Patch Version**: Bug fixes only, no behavioral changes
- **Deprecation Policy**: 
    - Mark as `@deprecated` with replacement guidance
    - Support for 2 major versions minimum
    - Clear migration guide provided
    - Announce in release notes and CHANGELOG

### Backward Compatibility

- **Configuration**: Old config keys remain valid with warnings
- **API Endpoints**: Response schema can only extend (add fields), not remove
- **Database Migrations**: Always reversible to previous version
- **Plugin API**: Maintain compatibility with published versions

### Enterprise vs. Standard Code

**Enterprise-specific code**:
- Located in `backend/enterprise_*.py` or `plugin/enterprise*.js`
- Loaded dynamically with try-catch fallback
- Must not break standard deployments if unavailable
- Separate test suite: `tests/enterprise/`
- Configuration flags for feature gating

**Standard code**:
- Core functionality always available
- Works offline without enterprise modules
- Minimal dependencies
- Fully tested with standard test suite

## 7. Review and Approval Process

### Automated Quality Gates

**All PRs must pass**:
- ✅ Linting (`ruff`, `bandit`, `markdownlint`)
- ✅ Type checking (`mypy`)
- ✅ Unit tests (100% pass rate)
- ✅ Integration tests
- ✅ Performance regression tests (if applicable)
- ✅ Security scans
- ✅ OpenSpec validation (for doc changes)
- ✅ Code coverage ≥85% (backend)

**Workflow**: GitHub Actions runs automatically on PR creation/update

### Manual Review Requirements

**Code Review Checklist**:
- [ ] Changes align with project mission
- [ ] Code quality meets standards
- [ ] Security best practices followed
- [ ] Performance within SLA limits
- [ ] Tests cover new functionality (85%+ coverage)
- [ ] Documentation complete and accurate
- [ ] No breaking changes (or documented with migration path)
- [ ] Commit messages are clear and descriptive
- [ ] Related issues/discussions referenced

**Review Timeline**:
- **Urgent fixes** (security, critical bugs): ≤24 hours
- **Regular features**: 3-7 days
- **Major changes**: 7-14 days
- **Complex PRs**: May extend to 21 days with clear communication

**Approval Authority**:
- **Regular code**: One core maintainer required
- **Security-sensitive**: Security advisor + one core maintainer
- **Enterprise features**: Enterprise advisor + one core maintainer
- **Governance/breaking changes**: Project lead + 2 core maintainers
- **Documentation governance**: Documentation advisor + one core maintainer

### PR Response SLAs

**Core Maintainers commit to**:
- First review within 3 business days
- Feedback on all substantial changes
- Clear reasoning if changes requested
- Support for new contributor fixes

**PR Author commits to**:
- Address feedback within 7 days or notify reviewer
- Respond to questions/comments promptly
- Keep PR up-to-date with base branch
- Resolve conflicts before merge

### Release Process

**Release Cadence**: Monthly on the last Friday of each month

**Pre-Release**:
1. Create release branch from `main` (7 days before release)
2. Bump version following semantic versioning
3. Update CHANGELOG.md with all changes
4. Run full test suite + performance benchmarks
5. Security scan for vulnerabilities
6. Documentation review

**Release**:
1. Create GitHub release with changelog
2. Tag commit with version
3. Build artifacts (if applicable)
4. Announce in release notes

**Post-Release**:
1. Update version in code/docs
2. Open new development cycle
3. Backport critical fixes to previous version if needed

## 8. Change Management & Versioning

### Semantic Versioning

**Format**: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (increment, reset others to 0)
- **MINOR**: New features, backward compatible (increment, reset PATCH to 0)
- **PATCH**: Bug fixes and performance improvements (increment)

**Examples**:
- 0.1.27 → 0.2.0 (new features)
- 0.2.0 → 1.0.0 (stable release or breaking changes)
- 0.1.27 → 0.1.28 (patch)

### Breaking Changes

**Definition**: Any change that requires user or developer action

**Process**:
1. Requires major version increment
2. Migration guide mandatory in release notes
3. Deprecation period: minimum 2 major versions (≈2 months)
4. Pre-announcement: mentioned in 2-3 releases before removal
5. Clear upgrade instructions provided

**Examples**:
- API endpoint removal or signature change
- Configuration key removal
- Required dependency upgrade
- Database schema breaking change
- Plugin API breaking change
- Model format incompatibility

### Deprecation Policy

**For Features/APIs Being Removed**:

1. **Announcement Phase** (current release):
   - Mark with `@deprecated` decorator
   - Add warning to logs/UI
   - Document replacement in docstring
   - Announce in release notes

2. **Support Phase** (2 major versions minimum):
   - Feature continues to work
   - Redirects to replacement if applicable
   - Migration guide in docs

3. **Removal Phase** (planned release):
   - Remove code/endpoint
   - Update changelog with removal
   - Provide final migration guide

**Timeline Example**:
```
v0.8.0: Feature marked deprecated
v0.9.0: Still works, migration guide available
v0.10.0: Still works, final warning
v1.0.0: Feature removed
```

### Change Documentation

**All changes tracked in**:
- `CHANGELOG.md` (human-readable)
- Git commit history (technical details)
- GitHub releases (public announcements)
- `docs/GOVERNANCE_LOG.md` (governance decisions)

**CHANGELOG Format**:
```markdown
## [0.2.0] - 2025-11-30

### Added
- New feature description

### Changed
- Breaking change with migration info

### Fixed
- Bug fix description

### Deprecated
- Deprecated feature with replacement

### Security
- Security fix description
```

### OpenSpec Governance for Documentation

**Material changes to governed documents** must follow OpenSpec workflow:
- Create change proposal in `openspec/changes/`
- Define delta spec under `specs/project-documentation/`
- Submit for review before implementation
- Archive completed changes for audit trail

**See `openspec/AGENTS.md` for detailed workflow**

## 9. Licensing and Compliance

### Project License

- **License**: MIT License (see LICENSE file)
- **Terms**: Free to use, modify, distribute with attribution
- **Liability**: No warranty, use at your own risk

### Dependency Licensing

**Requirements**:
- All dependencies must be compatible with MIT license
- No GPL, AGPL, or incompatible licenses without explicit approval
- Maintain LICENSE.txt summary of all dependencies
- Quarterly dependency audit for license changes
- Rejected licenses reviewed annually for policy updates

**Process for adding dependencies**:
1. Verify license compatibility before adding
2. Include license info in PR description
3. Add to dependencies list during merge
4. Update LICENSE.txt summary
5. Check in security scan

### Compliance Standards

**Required Compliance**:
- ✅ **GDPR**: Personal data protection and user rights
- ✅ **SOC2**: Security controls and audit trails
- ✅ **HIPAA** (if medical data): Health data protection (optional)
- ✅ **WCAG 2.1 AA**: Accessibility standards
- ✅ **CWE/OWASP**: Security best practices

**Compliance Responsibilities**:

| Compliance | Owner | Frequency |
|-----------|-------|-----------|
| GDPR | Security Advisor | Quarterly audit |
| SOC2 | Security Advisor | Annual assessment |
| HIPAA | Enterprise Advisor (if enabled) | Annual if applicable |
| WCAG | UI/UX Contributors | Per release |
| OWASP | Security Advisor | Monthly scan |

### Data Handling

**Personal Data Protection**:
- No collection without explicit consent
- Encrypted in transit (TLS 1.2+) and at rest (AES-256)
- Data retention: Minimum necessary duration only
- User right to access and deletion honored
- Privacy policy available and updated annually

**User Rights (GDPR)**:
- **Access**: Users can request their data
- **Rectification**: Users can correct their data
- **Deletion**: Right to be forgotten implemented
- **Portability**: Export data in standard formats
- **Objection**: Opt-out of analytics/profiling

**Data Breach Response**:
1. **Assessment**: Determine scope and impact (24 hours)
2. **Notification**: Notify affected users (72 hours for GDPR)
3. **Remediation**: Fix vulnerability immediately
4. **Review**: Post-incident review within 1 week
5. **Communication**: Transparent disclosure of learnings

### Security Audit Schedule

| Audit Type | Frequency | Owner |
|-----------|-----------|-------|
| Dependency scan | Weekly (automated) | CI/CD |
| Bandit security scan | Per PR | CI/CD |
| OWASP check | Monthly | Security Advisor |
| Penetration test | Annually | External firm |
| Code review audit | Quarterly | Security Advisor |
| Compliance audit | Annually | Compliance team |

### Accessibility Compliance

**Standards**: WCAG 2.1 Level AA minimum

**Requirement Coverage**:
- Perceivable: Text alternatives, captions, adaptable layouts
- Operable: Keyboard navigation, enough time, seizure prevention
- Understandable: Readable text, predictable behavior, help available
- Robust: Compatible with assistive technologies

**Testing**:
- Automated scanning: Per PR
- Manual testing: Before each release
- User testing: Quarterly with accessibility users
- Issue response: Critical accessibility bugs fixed within 48 hours

## 10. Communication Channels

### Primary Channels

| Channel | Purpose | Response Time |
|---------|---------|---|
| **GitHub Issues** | Bug reports, feature requests, technical discussions | 3 business days |
| **GitHub Discussions** | Ideas, announcements, community Q&A | 5 business days |
| **GitHub PRs** | Code review, implementation feedback | 3 business days |
| **Release Notes** | Major announcements, version updates | Monthly |
| **README.md** | Project overview, getting started | Updated per release |
| **Email** | Private/sensitive matters, direct contact | 5 business days |

### Issue Communication Standards

**Bug Reports**:
- Use bug report template
- Include reproduction steps
- Attach logs/screenshots
- Note version and OS
- Expected vs. actual behavior

**Feature Requests**:
- Use feature request template
- Explain use case and value
- Link related issues
- Suggest implementation approach
- Note priority/impact

**Discussion Topics**:
- Architecture decisions
- Design feedback
- Community ideas
- General questions
- Process improvements

### Announcement Schedule

**Breaking Changes**: Announced in:
1. GitHub Discussions (immediately)
2. Release notes (at next release)
3. CHANGELOG.md (with migration guide)
4. Email notification (if major)

**Security Updates**: Announced in:
1. GitHub Security Advisory (immediately)
2. Email to security subscribers (immediately)
3. Release notes (at patch release)
4. Blog post (post-fix, explaining vulnerability)

**Major Releases**: Announced in:
1. Release notes (comprehensive)
2. GitHub Discussions (summary)
3. Email newsletter (if available)

### Developer Communication

**Escalation Path for Contributors**:
1. Comment on issue/PR
2. Mention core maintainer (@username)
3. Request discussion in Discussions forum
4. Email project lead if urgent

**Office Hours** (if established):
- Regular time slot for community Q&A
- Open technical discussions
- Mentoring for new contributors
- Roadmap updates

**Response Guidelines**:
- Acknowledge receipt within 24 hours
- Provide status update within 3 days
- Avoid communication dark periods
- Explain decisions even if disagreement
- Thank contributors for feedback

## 11. Conflict Resolution

### Conflict Resolution Process

**Level 1: Direct Discussion** (3 days)
- Involved parties discuss respectfully
- Focus on facts, not personalities
- Seek common ground and compromise
- Document discussion in issue/PR
- Attempt to reach resolution

**Level 2: Mediation** (5 days)
- Request neutral core maintainer to mediate
- Mediator facilitates discussion
- Presents both perspectives objectively
- Proposes compromise solution
- Escalate if no resolution

**Level 3: Project Lead Decision** (7 days)
- Project lead reviews all arguments
- Makes binding decision
- Documents reasoning clearly
- Communicates decision to all parties
- Implements decision

**Level 4: Appeals** (if governance impact - 30 days)
- For significant governance disputes
- May request external arbitration
- Used only for exceptional circumstances
- Decision documented in governance log

### Code of Conduct Violations

**Reporting**:
- Report via email to project lead
- Include incident details, witnesses, impact
- All reports treated confidentially
- Acknowledge receipt within 24 hours

**Investigation**:
- Impartial investigation within 7 days
- Interview involved parties separately
- Review communication history
- Consult code of conduct standards
- Document findings

**Resolution**:
- Warnings for minor violations
- Temporary ban (7-30 days) for moderate violations
- Permanent ban for severe/repeated violations
- Appeal process available (7 days)
- Previous violations considered

**Transparency**:
- Outcome communicated to reporter
- Aggregate statistics published quarterly
- Patterns identified and addressed
- Policy improvements implemented

### Governance Disputes

**Documentation**: All decisions, disputes, and resolutions logged in:
- `docs/GOVERNANCE_LOG.md` (permanent record)
- GitHub issue (if public)
- Core maintainer meeting notes (if private)

**Escalation Authority**:
```
Contributor ↓
Core Maintainer ↓
Project Lead ↓
External Arbitrator (rare)
```

**Appeals Process**:
- Available 30 days after decision
- New evidence must be presented
- Same path as original dispute
- Maximum 2 appeals per issue

---

## 12. Roadmap and Release Planning

### Roadmap Development

**Process**:
1. **Community Input** (ongoing): GitHub Discussions, issues feedback
2. **Team Discussion** (quarterly): Core maintainers align on priorities
3. **Public Roadmap** (published quarterly): Available in project wiki
4. **Release Planning** (monthly): Assign features to upcoming releases

**Roadmap Horizon**: 
- 3-month detailed (specific features and timelines)
- 6-month high-level (themes and goals)
- 12-month vision (strategic direction)

**Roadmap Criteria**:
- Impact on users (adoption, problem-solving)
- Maintainability (technical debt reduction)
- Security improvements
- Performance enhancements
- Community requests
- Strategic alignment

---

## 13. Release Planning and Schedules

### Release Schedule

**Regular Releases**: Last Friday of each month
- Feature releases with bug fixes
- Security patches included
- Performance improvements
- Documentation updates

**Patch Releases**: As-needed (within 7 days)
- Critical bug fixes
- Security vulnerabilities
- Data corruption issues

**Major Releases**: Every 6-12 months
- Strategic milestones
- Significant new features
- Breaking changes (if any)
- Long-term support designation

### Maintenance SLAs

| Severity | Response Time | Resolution Time |
|----------|---|---|
| Critical (data loss, security) | 4 hours | 24 hours |
| High (major feature broken) | 24 hours | 7 days |
| Medium (partial functionality) | 3 days | 30 days |
| Low (minor issues, UX) | 7 days | 90 days |

**SLA Tracking**: Published monthly in project status report

---

## 14. Deprecation and Sunset Policy

### Feature Lifecycle

**Proposal** → **Active** → **Deprecated** → **Removed**

### Deprecation Timeline

- **Announcement**: Clearly mark as deprecated
- **Support Period**: Minimum 2 major versions
- **Migration Path**: Clear documentation provided
- **Final Release**: Last version supporting feature
- **Removal**: Feature deleted in next major version

### Sunset Decision Criteria

Features sunset when:
- No longer aligned with project mission
- Maintenance burden exceeds value
- Better alternatives exist
- Security vulnerabilities not justifiable
- Community consensus (no usage)

---

## 15. Amendment and Review

### Constitution Review

**Frequency**: Annual review (September)
- Community feedback collection
- Core maintainer discussion
- Project lead approval
- Update via OpenSpec governance

**Emergency Amendments**:
- Critical governance gaps
- Urgent security policy needed
- Legal/compliance requirement
- Requires project lead + 2 core maintainers approval
- Followed by community discussion

### Amendment Process

1. **Proposal**: Issue proposal via GitHub
2. **Discussion**: 14-day community feedback period
3. **Review**: Core maintainers evaluate
4. **Vote**: If major change, full contributor vote
5. **Implementation**: Update via OpenSpec process
6. **Communication**: Announce changes in release notes

---

## Governance Principles

This constitution upholds these core principles:

1. **Transparency**: Decisions made openly with clear reasoning
2. **Inclusivity**: All voices heard; decisions by consensus when possible
3. **Accountability**: Roles have clear responsibilities and authority
4. **Quality**: High standards maintained through review and automation
5. **Community**: Contributors valued and supported in growth
6. **Sustainability**: Balance feature development with maintenance
7. **Security**: Safety prioritized over convenience
8. **Accessibility**: Features available to all users

---

## Document Governance

**Governed by OpenSpec**: Material changes tracked in 'openspec/changes/' with
deltas under the 'project-documentation' capability.

**Last Updated**: October 20, 2025

**Review Date**: September 2026 (annual review)

**Approval**: Project Lead + Core Maintainers consensus

---

This constitution establishes the governance framework for the Obsidian AI Assistant
project. All contributors are expected to uphold these principles to ensure a healthy,
productive, inclusive, and sustainable project environment. Questions or suggestions
about governance should be raised in GitHub Discussions or via email to the project lead.

# PROJECT_CONSTITUTION Quick Reference

**Document Location**: `docs/PROJECT_CONSTITUTION.md`

**Governance**: OpenSpec-governed (material changes via `openspec/changes/`)

**Last Updated**: October 20, 2025

---

## Key Decision Timelines

| Category | Authority | Timeline | Review Period |
|----------|-----------|----------|---|
| **Strategic** | Lead + Consensus | 21 days | 7-14 days discussion |
| **Technical** | 2+ Maintainers | 10 days | 3-7 days review |
| **Minor** | Any Maintainer | 3 days | 1 day |
| **Emergency** | Lead + 1 Maintainer | Hours | Post-incident review |

---

## Contribution Tiers at a Glance

| Tier | Examples | Review Time | Tests | Coverage | Approvals |
|------|----------|---|---|---|---|
| 1 | Typos, style | 1-2d | Minimal | N/A | 1 maintainer |
| 2 | Bug fixes | 3-5d | Unit + integration | 85%+ | 1 maintainer |
| 3 | New features | 7-14d | Comprehensive | 85%+ | 1 maintainer |
| 4 | Architecture | 14-21d | Full test suite | 95%+ | 2 maintainers + lead |

---

## SLA Targets

### Performance (Response/Resolution)

| Tier | Target | Type |
|------|--------|------|
| T1 | <100ms | Health, status, config |
| T2 | <500ms | Cached ops, search |
| T3 | <2s | AI generation |
| T4 | <10s | Web analysis |
| T5 | <60s | Batch operations |

### Issue Resolution SLAs

| Severity | Response | Resolution |
|----------|----------|------------|
| Critical | 4 hours | 24 hours |
| High | 24 hours | 7 days |
| Medium | 3 days | 30 days |
| Low | 7 days | 90 days |

### Communication Response Times

| Channel | Response |
|---------|----------|
| Issues | 3 business days |
| Discussions | 5 business days |
| PRs | 3 business days |
| Email | 5 business days |

---

## Roles & Responsibilities

| Role | Key Responsibility | Authority | Min Count |
|------|---|---|---|
| **Project Lead** | Direction, disputes | Final decision | 1 |
| **Core Maintainers** | Reviews, releases | Approve PRs | 2+ |
| **Security Advisor** | Security reviews | Security gate | As needed |
| **Enterprise Advisor** | Compliance | Enterprise gate | As needed |
| **Contributors** | Code/docs | Submit changes | Unlimited |

---

## Critical Code Standards

### All Code
- ✅ Pass automated tests (100% pass rate)
- ✅ Pass linting (`ruff`, `bandit`, `markdownlint`)
- ✅ ≥85% code coverage
- ✅ Backward compatible OR migration guide provided

### Python
- ✅ Type hints required
- ✅ PEP 8 + 88-char limit
- ✅ Ruff linting
- ✅ Bandit security scan

### JavaScript
- ✅ PascalCase/camelCase naming
- ✅ 4-space indentation
- ✅ JSDoc comments
- ✅ Error handling required

### Documentation
- ✅ Markdown linting (120-char limit)
- ✅ WCAG 2.1 AA accessibility
- ✅ Cross-references
- ✅ Practical examples

---

## Versioning Quick Rules

```
MAJOR.MINOR.PATCH

v0.1.0 → v0.2.0 = New features (backward compatible)
v0.2.0 → v1.0.0 = Stable release OR breaking changes
v0.1.0 → v0.1.1 = Bug fixes only
```

### Breaking Changes
- ✅ Requires MAJOR version bump
- ✅ Migration guide mandatory
- ✅ 2-version deprecation minimum
- ✅ Clear replacement provided

---

## Conflict Resolution Escalation

```
1. Direct Discussion (3 days)
   ↓
2. Mediation (5 days)
   ↓
3. Project Lead Decision (7 days)
   ↓
4. Appeals (30-day window)
```

---

## Compliance Requirements

### Standards (Minimum)
- ✅ **GDPR**: Personal data protection
- ✅ **SOC2**: Security controls
- ✅ **WCAG 2.1 AA**: Accessibility
- ✅ **OWASP**: Security practices
- ⚠️ **HIPAA**: If medical data

### Audit Schedule
- **Weekly**: Dependency scan (automated)
- **Per PR**: Bandit security scan
- **Monthly**: OWASP check
- **Quarterly**: Code review audit
- **Annually**: Penetration test, full compliance audit

---

## Release Schedule

**Regular**: Last Friday of month
**Patches**: As-needed (within 7 days)
**Major**: Every 6-12 months

### Pre-Release Checklist
- [ ] Version bump (MAJOR.MINOR.PATCH)
- [ ] CHANGELOG.md updated
- [ ] Full test suite passed
- [ ] Performance benchmarks OK
- [ ] Security scan clean
- [ ] Documentation reviewed

---

## Getting Help

### For Decisions
1. Comment on issue/PR
2. Mention @CoreMaintainer (if needed)
3. Post in GitHub Discussions
4. Email Project Lead (if urgent)

### For Questions
- 📖 See `docs/API_REFERENCE.md` for API
- 🏗️ See `docs/SYSTEM_ARCHITECTURE_SPECIFICATION.md` for design
- 🤖 See `openspec/AGENTS.md` for governance workflow
- 💬 Use GitHub Discussions

### For Issues
- 🐛 **Bug**: Use bug template, include reproduction steps
- ✨ **Feature**: Use feature template, explain use case
- 🤔 **Question**: Post in Discussions

---

## Common Timelines

### PR to Merge
- Small (Tier 1): **1-2 days**
- Regular (Tier 2): **3-7 days**
- Major (Tier 3): **7-14 days**
- Strategic (Tier 4): **14-21 days**

### Feature to Release
- Minor fix: **7 days** (next patch)
- Feature: **30 days** (next minor)
- Breaking change: **60+ days** (next major)

### Documentation to Live
- Quick update: **3-7 days**
- Governed doc: **10-21 days** (OpenSpec workflow)

---

## Key Documents

| Document | Purpose | Location |
|----------|---------|----------|
| **Constitution** | Governance framework | `docs/PROJECT_CONSTITUTION.md` |
| **Contributing** | Contributor guide | `docs/CONTRIBUTING.md` |
| **API Reference** | Endpoint documentation | `docs/API_REFERENCE.md` |
| **System Architecture** | Design & components | `docs/SYSTEM_ARCHITECTURE_SPECIFICATION.md` |
| **OpenSpec AGENTS** | Governance workflow | `openspec/AGENTS.md` |
| **Governance Log** | Decision history | `docs/GOVERNANCE_LOG.md` |

---

## Constitution Review Schedule

**Annual Review**: September (1st Friday)
- Collect community feedback
- Discuss changes with maintainers
- Update as needed
- Approve via OpenSpec

**Next Review**: September 2026

**For Questions**: Raise in GitHub Discussions or email Project Lead

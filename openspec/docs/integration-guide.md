# OpenSpec Integration with Development Workflow

This guide explains how OpenSpec integrates with your daily development workflow,
CI/CD pipeline, releases, and team processes.

---

## Table of Contents

- [Development Workflow Integration](#development-workflow-integration)
- [CI/CD Pipeline Integration](#cicd-pipeline-integration)
- [Release Process Integration](#release-process-integration)
- [Team Coordination](#team-coordination)
- [Common Workflows](#common-workflows)
- [Troubleshooting Integration](#troubleshooting-integration)

---

## Development Workflow Integration

### Before You Start

**When is OpenSpec governance required?**

✅ **Governed documents** (material changes):
- Top-level docs: `README.md`, `AGENTS.md`, `.github/copilot-instructions.md`
- Docs folder: Any `*_SPECIFICATION.md` files
- Architecture, security, testing, deployment guides
- OpenSpec directory itself

❌ **Not governed** (edit freely):
- Quick fix docs
- Internal notes
- Comments in code
- Log files
- Temporary documentation

### Local Development Workflow

```bash
# 1. Identify what needs to change
# Is the document governed? Check openspec/specs/project-documentation/spec.md

# 2. If governed, create a change proposal
mkdir -p openspec/changes/update-doc-my-change/specs/project-documentation

# 3. Create required files
# - proposal.md (Why, What, Impact)
# - tasks.md (Implementation checklist)
# - spec.md (Delta: ADDED/MODIFIED/REMOVED)

# 4. Validate locally
openspec validate update-doc-my-change --strict

# 5. Make the actual changes to the document

# 6. Test locally
openspec validate update-doc-my-change --strict  # Should pass again

# 7. Commit and push
git add openspec/changes/update-doc-my-change/
git add docs/MY_DOCUMENT.md
git commit -m "docs: update my document (proposal + implementation)"
git push origin feature/update-doc-my-change
```

### Feature Branch Strategy

**For OpenSpec changes**:
```
main
 └── feature/update-doc-<name>
      ├── openspec/changes/<change-id>/         # Proposal files
      │   ├── proposal.md
      │   ├── tasks.md
      │   └── specs/project-documentation/spec.md
      └── docs/AFFECTED_FILE.md                 # Implementation
```

**Key points**:
- Keep OpenSpec changes in same PR as implementation
- Validator runs on both during PR checks
- After merge, apply change to baseline specs
- Archive the change for audit trail

---

## CI/CD Pipeline Integration

### Automated Checks

**On every PR**:

```yaml
# GitHub Actions workflow (openspec-pr-validate.yml)
1. Lint: markdownlint, ruff, etc.
2. OpenSpec validation: `openspec validate --strict`
3. Spec consistency: Verify deltas match baselines
4. Link checking: Internal reference validation
5. Code quality: Standard linting + bandit
```

**Status checks required to merge**:
- ✅ All lint passes (markdown, code)
- ✅ OpenSpec validation passes (if any changes to `openspec/`)
- ✅ All tests pass
- ✅ No security vulnerabilities

### Required vs Optional Validations

| Check | Required | Fails PR? | When |
|-------|----------|-----------|------|
| OpenSpec strict validation | For `openspec/changes/` | Yes | On modified deltas |
| Markdown linting (MD013) | Always | Yes | Line length violations |
| Markdown linting (others) | Always | Yes | Formatting issues |
| Spec baseline verification | For applied changes | Yes | After merge |
| Link validation | For doc changes | No (warning) | Links to other docs |

### CI/CD Workflow for OpenSpec

```
Developer pushes PR
        ↓
[GitHub Actions Starts]
├─ Lint: Check formatting
├─ OpenSpec: Validate proposal structure
├─ OpenSpec: Validate deltas against baseline
├─ Specs: Check baseline consistency
└─ Tests: Run full test suite
        ↓
All checks pass? → [Ready for review]
                → [Request review]
                → [Reviewer approves]
        ↓
[Merge to main]
        ↓
[Post-merge automation]
├─ Apply: Run `openspec apply <change-id>`
│   └─ Updates baseline specs
├─ Archive: Move change to `archive/`
│   └─ Creates backup of applied changes
└─ Cleanup: Remove from `changes/`
        ↓
[Complete]
```

### Running Validations Locally

```bash
# Before pushing
./openspec/scripts/validate-all.ps1        # All changes
openspec validate <change-id> --strict     # Specific change

# During development
openspec validate <change-id>              # Non-strict (warnings OK)
openspec validate <change-id> --strict     # Production-ready

# After merge (maintainer)
openspec apply <change-id>                 # Apply deltas to baselines
openspec archive <change-id> --yes         # Archive completed change
```

---

## Release Process Integration

### Pre-Release

**Week before release** (if documentation changes):

```bash
# 1. Review all changes in `openspec/changes/`
openspec list changes

# 2. For each change not yet applied:
openspec validate <change-id> --strict

# 3. Apply changes to baselines
openspec apply <change-id>

# 4. Archive completed changes
openspec archive <change-id> --yes

# 5. Update CHANGELOG.md to reference changes
# Example: "Governance improvements via change-id-123"
```

**Release day**:

```bash
# 1. Verify no pending changes blocking release
openspec list changes

# 2. Generate release notes including documentation updates
# Include references to major documentation changes

# 3. Tag and release
git tag v0.2.0
git push --tags
```

### Post-Release

```bash
# 1. Verify archives created successfully
ls -la openspec/archive/

# 2. Confirm baseline specs updated
# Check `openspec/specs/project-documentation/spec.md`

# 3. Archive remains in `openspec/archive/` forever
# (used for historical reference and audit trail)
```

### Release Notes Integration

**For documentation-heavy releases**:

```markdown
## v0.2.0 - 2025-11-30

### Documentation Improvements
- Enhanced governance framework (change-id-1)
- Updated API reference with new endpoints (change-id-2)
- Added enterprise feature guide (change-id-3)

### Changes Applied via OpenSpec
- All changes reviewed and applied to baseline specifications
- See `openspec/archive/` for detailed change history
```

---

## Team Coordination

### Code Review Process

**When reviewing OpenSpec changes**:

1. **Check proposal structure**:
   - [ ] `proposal.md` explains Why/What/Impact
   - [ ] `tasks.md` includes implementation checklist
   - [ ] Delta spec uses ADDED/MODIFIED/REMOVED
   - [ ] All requirements have scenarios

2. **Verify deltas match baseline**:
   - [ ] MODIFIED requirements include full text
   - [ ] Requirement names match exactly
   - [ ] No new requirements marked MODIFIED

3. **Validate implementation**:
   - [ ] Document changes match proposal description
   - [ ] All tasks in `tasks.md` completed
   - [ ] No breaking changes to governed docs

4. **Check consistency**:
   - [ ] Markdown linting passes
   - [ ] Cross-references correct
   - [ ] Examples accurate

### Delegation Pattern

**Maintainer delegation**:

```bash
# Delegate spec application to team member
# (They have limited permissions)

# Team member runs after PR merge:
cd openspec
./scripts/apply-change.ps1 <change-id>

# This:
# 1. Applies delta to baseline spec
# 2. Generates backup
# 3. Updates metadata
# 4. Runs validation

# Maintainer then archives:
openspec archive <change-id> --yes
```

### Communication

**When proposing changes**:

1. **In GitHub PR description**:
   ```markdown
   ## OpenSpec Changes
   - Change ID: `update-doc-api-reference`
   - Type: MODIFIED (API section)
   - Impact: Updates API stability guarantees
   ```

2. **In GitHub Discussions** (for major changes):
   ```markdown
   ## Documentation Governance Change: API Reference
   Proposed changes update API response contract...
   Change proposal: `openspec/changes/update-doc-api-reference/`
   ```

3. **In Slack/Team Chat** (informal):
   - "Updated API docs via #update-doc-api-reference"
   - Link to PR for review

---

## Common Workflows

### Workflow 1: Simple Documentation Update

```bash
# 1. Edit document
code docs/MY_SPEC.md

# 2. Create OpenSpec change
mkdir -p openspec/changes/update-doc-my-spec/specs/project-documentation

# 3. Write proposal
# proposal.md: "Updated performance targets section"

# 4. Write tasks
# tasks.md: "Update document, test examples, validate links"

# 5. Write delta
# spec.md: MODIFIED requirement with full text

# 6. Validate and commit
openspec validate update-doc-my-spec --strict
git add .
git commit -m "docs: update my spec"
git push

# 7. After merge: Apply and archive (maintainer)
openspec apply update-doc-my-spec
openspec archive update-doc-my-spec --yes
```

### Workflow 2: Multi-Document Change

```bash
# Example: Update both API reference and deployment guide

openspec/changes/update-doc-deployment-guidance/
├── proposal.md          # Covers both docs
├── tasks.md
└── specs/project-documentation/
    ├── spec.md          # Delta for project-documentation

# Delta includes both MODIFIED requirements:
# - API Reference requirements
# - Deployment requirements
```

### Workflow 3: Adding New Governed Document

```bash
# 1. Propose new documentation governance
openspec/changes/add-doc-new-guide/proposal.md

# 2. Create new governed requirement in spec
# spec.md: ADDED requirement for new doc governance

# 3. Create the document
docs/NEW_GUIDE.md

# 4. Reference in delta spec (examples, links)

# After merge: baseline updated to include new doc governance
```

### Workflow 4: Deprecating Old Documentation

```bash
# 1. Mark document as deprecated
# proposal.md: "Mark OLD_GUIDE.md as deprecated, users should use NEW_GUIDE.md"

# 2. Create REMOVED delta
# spec.md: REMOVED requirement for old doc governance

# 3. Update document to point to replacement
docs/OLD_GUIDE.md:
  "⚠️ DEPRECATED: Use docs/NEW_GUIDE.md instead"

# 4. Confirm archiving process for historical reference
# Archive stores removed requirements permanently
```

---

## Troubleshooting Integration

### Common Issues

#### Issue: "Validation failed - delta doesn't match baseline"

**Cause**: MODIFIED delta references requirement that doesn't exist in baseline

**Solution**:
```bash
# 1. Check baseline
cat openspec/specs/project-documentation/spec.md

# 2. Find exact requirement name
rg "### R.*Your Requirement" openspec/specs/

# 3. Update delta to match exactly
# spec.md: "### Requirement: [exact name]"

# 4. Revalidate
openspec validate <change-id> --strict
```

#### Issue: "Markdown linting fails on line 150"

**Cause**: Line exceeds 120-character limit

**Solution**:
```bash
# View the line
sed -n '150p' openspec/changes/<id>/specs/project-documentation/spec.md

# Fix by wrapping
# Instead of: "This is a very long requirement explanation that exceeds..."
# Use: "This is a very long requirement explanation that
#       exceeds the character limit..."

# Revalidate
openspec validate <change-id> --strict
```

#### Issue: "Can't apply change - baseline has conflicts"

**Cause**: Baseline already modified manually

**Solution**:
```bash
# 1. Backup current baseline
cp openspec/specs/project-documentation/spec.md \
   openspec/specs/project-documentation/spec.md.bak

# 2. Manually merge changes
# Edit baseline to include new requirements from delta

# 3. Run validation
openspec validate --strict

# 4. Document the manual merge in notes/comments
```

### Prevention Strategies

1. **Always validate before pushing**
   ```bash
   openspec validate <id> --strict  # Every time
   ```

2. **Review baseline before proposing**
   ```bash
   openspec show project-documentation --type spec
   ```

3. **Keep changes focused**
   - One logical change per proposal
   - Easier to review and apply
   - Reduces merge conflicts

4. **Communicate changes early**
   - GitHub Discussions for major changes
   - Slack notifications before proposing
   - Coordinate with team

---

## Integration Checklist

Use this checklist when integrating OpenSpec into your workflow:

### Setup Phase
- [ ] OpenSpec CLI installed and working
- [ ] Scripts in `openspec/scripts/` are executable
- [ ] GitHub Actions workflows configured
- [ ] Validation passing on clean repo

### Development Phase
- [ ] Identify governed documents
- [ ] Create OpenSpec change structure
- [ ] Write proposal, tasks, deltas
- [ ] Validate locally before pushing
- [ ] Include OpenSpec changes in PR

### Review Phase
- [ ] PR passes all automated checks
- [ ] Reviewer verifies delta structure
- [ ] Implementation matches proposal
- [ ] Documentation quality approved

### Merge Phase
- [ ] PR approved by reviewer
- [ ] All checks passing
- [ ] Ready to merge
- [ ] No blocking issues

### Post-Merge Phase
- [ ] Apply change to baseline: `openspec apply`
- [ ] Archive change: `openspec archive`
- [ ] Update CHANGELOG if major
- [ ] Communicate release notes

### Release Phase
- [ ] All changes applied and archived
- [ ] Baseline specs consistent
- [ ] Release notes reference changes
- [ ] Archive preserved for audit trail

---

## Performance & Scale

### Performance Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| Validate single change | <5s | Local, strict mode |
| Validate all changes | <30s | Full repo, strict mode |
| Apply change | <2s | Update baseline + archive |
| List changes | <1s | No I/O |
| Create new change | <10s | Scaffold structure |

### Scaling Considerations

As your project grows:

- **More specs**: Add new capabilities to baseline
- **More changes**: Archive completed changes regularly
- **Larger docs**: Break into multiple governed files
- **More team members**: Distribute application/archiving duties

### Optimization

```bash
# Batch validation (faster than individual)
openspec validate --changes --strict

# Batch archiving (after release)
for change in openspec/changes/*/; do
  openspec archive "$(basename "$change")" --yes
done

# Cleanup
rm -rf openspec/changes/*
```

---

## Next Steps

- Read: `contributor-guide.md` for day-to-day workflow
- Review: `change-patterns.md` for writing quality deltas
- Explore: `openspec/archive/` for examples
- Experiment: Create a test change and validate it locally

Need help? See `troubleshooting.md` or open a GitHub Discussion.

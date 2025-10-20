# OpenSpec Frequently Asked Questions (FAQ)

Quick answers to common questions about OpenSpec governance.

---

## Table of Contents

- [General Questions](#general-questions)
- [Getting Started](#getting-started)
- [Working with Changes](#working-with-changes)
- [Validation & Testing](#validation--testing)
- [Review & Approval](#review--approval)
- [Common Mistakes](#common-mistakes)
- [Technical Questions](#technical-questions)

---

## General Questions

### Q: What is OpenSpec?

**A:** OpenSpec is a documentation governance system that tracks changes to
critical project documents. It ensures documentation is:
- **Reviewed**: Changes reviewed for accuracy and quality
- **Auditable**: Complete change history preserved
- **Consistent**: Standards applied uniformly
- **Traceable**: Links changes to decisions and requirements

### Q: Why do we need OpenSpec?

**A:** Without governance:
- Documentation gets out of sync with code
- Changes aren't reviewed or approved
- No audit trail of why things changed
- Hard to maintain consistency across docs

With OpenSpec:
- Changes follow formal process
- Every change has justification (proposal.md)
- Deltas show exactly what changed
- Archive provides complete history

### Q: Is every document governed?

**A:** No. Only critical documents:
- Top-level: `README.md`, `AGENTS.md`
- Specifications: `*_SPECIFICATION.md` files
- Architecture & security guides
- API reference
- OpenSpec itself

See `openspec/specs/project-documentation/spec.md` for complete list.

### Q: Can I just edit a governed document?

**A:** For **typos/formatting**: Yes, minor fixes don't need OpenSpec.

For **material changes**: No, use the OpenSpec workflow:
1. Create change proposal
2. Write delta spec
3. Validate
4. Submit PR
5. Apply to baseline

**Rule of thumb**: If someone reviewing the PR would question the change,
use OpenSpec.

### Q: How long does the OpenSpec process take?

**A:** For typical changes: **3-5 days**

- Creating proposal: **1-2 hours**
- Validation: **<1 minute**
- Review: **1-3 days**
- Merge & apply: **Same day**

Fast-tracked changes: **1-2 days** (if simple, clear)

Emergency changes: **Hours** (security issues, critical bugs)

### Q: Who decides what needs OpenSpec?

**A:** Generally:
- **Your judgment**: Is this an important change?
- **Diff size**: Large changes likely need it
- **Impact scope**: Affects multiple components/docs?
- **Stability**: Changes user-facing contracts?

When in doubt: Ask in GitHub Discussions or chat with maintainers.

---

## Getting Started

### Q: I'm new, where do I start?

**A:** 1-hour onboarding:

```bash
# 15 min: Read core docs
openspec/README.md          # Overview
openspec/AGENTS.md          # Workflow
openspec/docs/contributor-guide.md  # Your role

# 15 min: Review example
openspec list changes
openspec show changes/<any-id>

# 15 min: Create test change
mkdir test-change
# Write proposal, tasks, delta

# 15 min: Validate and get feedback
openspec validate test-change --strict
```

### Q: How do I know if a document is governed?

**A:** Check the baseline spec:

```bash
# See all governed documents
cat openspec/specs/project-documentation/spec.md | grep "### R[0-9]:"

# Or search for specific doc
rg "README\.md" openspec/specs/
```

Files with `@SINCE` tags in the spec are governed.

### Q: What tools do I need?

**A:** Minimum:
- Git (for commits/PRs)
- Text editor (VS Code recommended)
- PowerShell 5.1+ or bash

Optional:
- OpenSpec CLI (for validation - included in repo)
- VS Code extensions (markdown linting)

---

## Working with Changes

### Q: How do I create a change?

**A:** Three files required:

```bash
mkdir -p openspec/changes/my-change-id/specs/project-documentation
```

**File 1: proposal.md**
```markdown
## Why
[Problem or opportunity]

## What Changes
[Description of changes]

## Impact
[Who affected, downstream effects]
```

**File 2: tasks.md**
```markdown
- [ ] Update document X
- [ ] Test changes locally
- [ ] Validate deltas
- [ ] Create PR
```

**File 3: spec.md** (delta)
```markdown
## MODIFIED Requirements

### Requirement Name: [exact name from baseline]

[Full requirement text including all sections]

#### Scenario:
- WHEN [condition]
- THEN [result]
```

### Q: Should I create one change per file or one per concept?

**A:** One per **logical concept**. Examples:

✅ **Good**:
- One change: "Update API response formats"
  (affects README + API_REFERENCE.md)

❌ **Not ideal**:
- Separate changes for README + API_REFERENCE
  (same logical concept, split unnecessarily)

❌ **Not ideal**:
- One mega-change: "Update all docs"
  (too broad, hard to review)

### Q: Can I skip the proposal/tasks and just submit deltas?

**A:** Not recommended:

- **Proposal**: Explains context for reviewers
- **Tasks**: Shows you have a plan
- **Validation**: Requires all three

However, for **very simple changes** (1-2 line updates):
- Minimal proposal OK ("Update version number")
- Tasks can be brief ("Update file, validate")

All three files still required structurally.

### Q: What if I need to change multiple documents?

**A:** Create **one change** with multiple deltas:

```
openspec/changes/my-multi-change/
├── proposal.md          # Single proposal covering all
├── tasks.md
└── specs/
    └── project-documentation/
        └── spec.md      # Includes MODIFIED for both docs
```

Delta example:
```markdown
## MODIFIED Requirements

### Requirement 1 (from README spec)
[Full text]

### Requirement 2 (from API Reference spec)
[Full text]
```

### Q: Can I update a change after submission?

**A:** Before **PR review**: Yes, commit updates to branch

```bash
git add .
git commit -m "docs: update proposal based on feedback"
git push
```

After **PR approved**: Don't edit, create new change instead

---

## Validation & Testing

### Q: How do I validate my changes?

**A:** Three levels:

```bash
# Basic check (finds syntax errors)
openspec validate my-change

# Strict mode (production-ready)
openspec validate my-change --strict

# All changes
openspec validate --changes --strict
```

### Q: What do validation errors mean?

**A:** Common errors:

| Error | Cause | Fix |
|-------|-------|-----|
| `Missing proposal.md` | File not found | Create file |
| `Delta has no scenarios` | Requirement missing scenarios | Add `#### Scenario:` section |
| `Requirement name mismatch` | MODIFIED ref doesn't match baseline | Copy exact name from spec |
| `Invalid WHEN/THEN format` | Scenario syntax wrong | Use "- WHEN" and "- THEN" |
| `Line too long` | Markdown line >120 chars | Wrap lines |

### Q: Can I validate offline?

**A:** Yes:

```bash
# Works without internet
openspec validate my-change --strict

# (Doesn't check GitHub, just local files)
```

### Q: What if I can't figure out the validation error?

**A:** 1. Run validation with verbose output

```bash
openspec validate my-change --strict --verbose
```

2. Check the specific file mentioned

3. Compare against example in `openspec/archive/`

4. Ask in GitHub Discussions (post the error)

---

## Review & Approval

### Q: Who reviews my change?

**A:** GitHub PR review process:

- **Automatic**: Linting, validation (GitHub Actions)
- **Manual**: Core maintainers (1-2 required)
- **Domain expert**: If security/compliance related

### Q: What will reviewers check?

**A:**

1. **Proposal**: Is the change justified? Is impact clear?
2. **Delta spec**: Do requirements use normative language (SHALL/MUST)?
3. **Scenarios**: Is there ≥1 scenario per requirement?
4. **Baseline match**: Do MODIFIED requirements reference exact names?
5. **Implementation**: Does document change match proposal?
6. **Quality**: Is writing clear? Are examples helpful?

### Q: How do I respond to review feedback?

**A:** 1. Read the feedback carefully

2. Make changes to files (proposal/delta/docs)

3. Test locally

```bash
openspec validate my-change --strict
```

4. Commit and push updates

```bash
git add .
git commit -m "docs: address reviewer feedback"
git push
```

5. Reply to each comment (even if just "Fixed!")

### Q: What if I disagree with reviewer feedback?

**A:** 1. Respectfully explain your position

2. Reference spec or documentation to support

3. Ask for clarification if needed

4. If still disagreement: escalate to maintainers

(Usually resolved quickly - most review feedback is clarification)

---

## Common Mistakes

### Mistake 1: MODIFIED without full requirement text

**Wrong**:
```markdown
## MODIFIED Requirements

### Old Feature: Update description
Updated the description to be clearer.
```

**Right**:
```markdown
## MODIFIED Requirements

### Old Feature

Here is the FULL requirement text including everything.

#### Scenario:
- WHEN X
- THEN Y
```

✅ **Always include complete requirement text for MODIFIED**

### Mistake 2: Missing scenarios

**Wrong**:
```markdown
### New Requirement: Add feature X
The system SHALL support feature X.
```

**Right**:
```markdown
### New Requirement: Add feature X
The system SHALL support feature X.

#### Scenario: Basic usage
- WHEN user enables feature X
- THEN system shows feature Y
```

✅ **Every requirement needs ≥1 scenario**

### Mistake 3: Wrong requirement name in MODIFIED

**Baseline has**:
```markdown
### Requirement: Developer Onboarding
```

**You write MODIFIED**:
```markdown
### Requirement: Onboarding
[...]
```

**Error**: Name doesn't match exactly

✅ **Copy requirement name exactly from baseline**

### Mistake 4: Normative language missing

**Wrong**:
```markdown
### Feature: Caching
The system should cache results for performance.
```

**Right**:
```markdown
### Feature: Caching
The system SHALL cache results to improve performance.
```

✅ **Use SHALL or MUST in every requirement**

### Mistake 5: Multi-concern MODIFIED

**Wrong** (tries to do too much):
```markdown
## MODIFIED Requirements

### API Design
The API SHALL... (plus added 5 new concerns)
```

**Better** (split if too much):
```markdown
## ADDED Requirements
### New API Feature 1
[...]

## MODIFIED Requirements
### API Design
[Just update existing parts]
```

✅ **Keep MODIFIED focused; use ADDED for new things**

---

## Technical Questions

### Q: Where are the archived changes stored?

**A:** In `openspec/archive/`:

```
openspec/archive/
├── 2025-10-14/         # Date-based directories
│   ├── update-doc-readme/
│   ├── update-doc-api/
│   └── ...
└── 2025-10-15/
    └── ...
```

These are **permanent**. They're your audit trail and historical record.

### Q: Can I delete an archived change?

**A:** **No**. Archives are immutable:
- Used for compliance/audit
- Provide historical context
- Can't be recreated

If needed, create a new change to revert/modify.

### Q: How do I "undo" a change?

**A:** Create a new change that reverts:

```markdown
# proposal.md
## Why
Previous change X had unintended consequences.

## What Changes
Revert changes from change-id-123.

# spec.md
## MODIFIED Requirements

### Requirement Name
[Restore to previous text from baseline]
```

This creates audit trail showing reversion.

### Q: Can I have multiple deltas in one file?

**A:** Not recommended. Better to:
- **One file per logical change** (one `spec.md`)
- **Each requirement in own MODIFIED/ADDED section**
- **Multiple changes per file only for related items**

Example (OK):
```markdown
## MODIFIED Requirements

### API Authentication
[...]

### API Rate Limiting
[...]

## ADDED Requirements

### New API Feature
[...]
```

### Q: How does OpenSpec handle conflicts?

**A:** In baseline specs:

```bash
# If baseline changed between your PR and merge:
# 1. GitHub shows conflict
# 2. You resolve in the file
# 3. Retest: openspec validate --strict
# 4. Push resolved version
```

**Prevention**:
- Keep changes small and focused
- Validate before every push
- Merge frequently
- Communicate major changes in advance

### Q: What's the difference between spec and change?

**A:**

| Item | Location | Role |
|------|----------|------|
| **Spec (baseline)** | `openspec/specs/` | Source of truth |
| **Change (delta)** | `openspec/changes/` | Proposal for update |
| **Archive** | `openspec/archive/` | Applied changes (history) |

**Flow**: Change → (Review) → (Apply) → Spec, Archive

---

## Still Have Questions?

### Resources

- **Quick reference**: See `best-practices.md`
- **Workflows**: See `change-patterns.md`
- **Integration**: See `integration-guide.md`
- **Examples**: Browse `openspec/archive/`
- **Scripts**: See `openspec/scripts/README.md`

### Get Help

- **GitHub Discussions**: Ask public questions
- **GitHub Issues**: Report bugs/improvements
- **PR Comments**: Ask during review
- **Slack/Chat**: Quick clarifications

### Report Problems

Found something broken or unclear?

```bash
# Report validation bug
git log openspec/scripts/validate.py  # See recent changes

# Report documentation issue
openspec list changes
# Create new change proposing fix
```

---

Last Updated: October 2025

Need to update this FAQ? Create an OpenSpec change proposing updates! 👍

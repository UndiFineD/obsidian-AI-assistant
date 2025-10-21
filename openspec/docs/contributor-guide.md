# OpenSpec Contributor Guide

Welcome! This guide will walk you through making your first contribution to OpenSpec-governed documentation.

## Table of Contents

- [Quick Start](#quick-start)
- [Your First Contribution](#your-first-contribution)
- [Understanding OpenSpec](#understanding-openspec)
- [Review Process](#review-process)
- [Governance Rules](#governance-rules)
- [Quick Reference](#quick-reference)
- [Getting Help](#getting-help)

## Quick Start

### Prerequisites

- Git installed and configured
- PowerShell 5.1+ (Windows) or PowerShell Core (cross-platform)
- OpenSpec CLI installed and in PATH
- Text editor (VS Code recommended)

### Installation Check

```powershell
# Verify OpenSpec CLI
openspec --version

# Verify Git
git --version

# Clone repository (if not already done)
git clone https://github.com/UndiFineD/obsidian-ai-agent.git
cd obsidian-ai-agent/openspec
```

### 5-Minute Setup

```powershell
# 1. Read the governance overview (2 minutes)
code README.md

# 2. Review an example change (2 minutes)
openspec list changes
openspec show changes/<any-change-id>

# 3. Validate your setup (1 minute)
.\scripts\validate-all.ps1
```

**Expected output**: ✅ All validations passed!

---

## Your First Contribution

### Time Estimate: 15-30 minutes

Let's walk through creating a simple documentation update from start to finish.
For a complete example, see the sample change proposal in `openspec/changes/update-doc-sample-change-demo/`
(includes proposal.md, tasks.md, and delta spec).

### Step 1: Identify What Needs to Change (2 minutes)

**Example scenario**: You notice that `README.md` is missing information about a new feature.

**Ask yourself**:
- Is this a material change? (Yes - adds new feature documentation)
- Which file am I changing? (`README.md`)
- What capability does this affect? (`project-documentation`)

### Step 2: Create a Change Proposal (3 minutes)

```powershell
# Navigate to openspec directory
cd openspec

# Create new change with automation script
.\scripts\create-change.ps1 -ChangeId "add-readme-feature-docs" `
                             -Title "Add documentation for new feature" `
                             -Description "Document the XYZ feature in README.md"

# Or review the sample change for a template:
code changes/update-doc-sample-change-demo/
```

**Output**:
```
✅ Change scaffolded successfully!
📁 Location: changes/add-readme-feature-docs/
📝 Next steps:
  1. Edit add-readme-feature-docs\proposal.md (Why/What/Impact)
  2. Edit add-readme-feature-docs\specs\project-documentation\spec.md
  3. Run: openspec validate --strict
```

### Step 3: Edit the Proposal (5 minutes)

Open `changes/add-readme-feature-docs/proposal.md`:

```markdown
# Proposal: Add documentation for new feature

## Why

README.md is missing documentation for the XYZ feature that was recently 
added. New users are confused about how to use this feature.

## What

This change proposes to:

- Add a "Using the XYZ Feature" section to README.md
- Include usage examples and prerequisites
- Link to detailed documentation in docs/

## Impact

**Affected users**: All new users and contributors

**Benefits**:
- Improved discoverability of XYZ feature
- Reduced support questions
- Better onboarding experience

**Risks**:
- Minimal - documentation-only change
- Mitigation: Peer review for accuracy
```

### Step 4: Write the Change Delta (5 minutes)

Open `changes/add-readme-feature-docs/specs/project-documentation/spec.md`:

**Option A**: If this is a NEW requirement (feature never documented before):

```markdown
## ADDED Requirements

### Requirement: Governance for XYZ feature documentation

The project SHALL govern material changes to XYZ feature documentation 
in README.md via OpenSpec change proposals to maintain consistency.

#### Scenario: Material change to XYZ feature docs requires proposal

- **WHEN** a contributor plans updates to XYZ feature documentation
- **THEN** they MUST create or update an OpenSpec change with deltas 
  under `project-documentation`
```

**Option B**: If this updates EXISTING README.md governance:

```markdown
## MODIFIED Requirements

### Requirement: Governance for README.md

The project SHALL govern material changes to key documentation files 
via OpenSpec change proposals to maintain consistency and review. 
This includes the new XYZ feature documentation section.

#### Scenario: Material change to README.md requires proposal

- **WHEN** a contributor plans a material update to `README.md`
- **THEN** they MUST create or update an OpenSpec change with deltas 
  under `project-documentation`

#### Scenario: XYZ feature documentation updates

- **WHEN** a contributor updates XYZ feature documentation in README.md
- **THEN** the changes SHALL be reviewed for technical accuracy and 
  clarity before merge
```

### Step 5: Validate Your Changes (2 minutes)

```powershell
# Validate your specific change
.\scripts\validate-all.ps1 -ChangeId "add-readme-feature-docs"
```

**Common errors and fixes**:

❌ **"Requirement must contain SHALL or MUST keyword"**
```markdown
# Wrong
The project will govern changes...

# Right
The project SHALL govern changes...
```

❌ **"Requirement must have at least one scenario"**
```markdown
# Wrong
### Requirement: My requirement
The system SHALL do something.

# Right
### Requirement: My requirement
The system SHALL do something.

#### Scenario: When it does the thing
- **WHEN** trigger happens
- **THEN** expected outcome occurs
```

❌ **"Change must have at least one delta operation"**
```markdown
# Wrong (empty spec.md)

# Right (has at least one delta type)
## ADDED Requirements
...
```

### Step 6: Submit for Review (3 minutes)

```powershell
# Create feature branch
git checkout -b feature/add-readme-feature-docs

# Stage your changes
git add changes/add-readme-feature-docs/

# Commit with descriptive message
git commit -m "docs: Add governance for XYZ feature documentation

- Created change proposal for README.md XYZ feature docs
- Added/modified project-documentation spec
- All validations passing"

# Push to remote
git push origin feature/add-readme-feature-docs
```

**Create Pull Request**:
1. Go to GitHub repository
2. Click "New Pull Request"
3. Select your branch
4. Title: `docs: Add governance for XYZ feature documentation`
5. Description: Link to your proposal:
   ```markdown
   ## Proposal
   See `openspec/changes/add-readme-feature-docs/proposal.md`
   
   ## Validation
   All OpenSpec validations passing ✅
   
   ## Checklist
   - [x] Proposal.md completed
   - [x] Spec.md with proper deltas
   - [x] Tasks.md checklist updated
   - [x] Validation passing
   ```

### Step 7: Post-Merge Actions (After Approval)

Once your PR is merged, the change needs to be applied and archived:

```powershell
# Pull latest changes
git checkout main
git pull

# Apply the change to baseline spec
.\scripts\apply-change.ps1 -ChangeId "add-readme-feature-docs"

# Archive the completed change
.\scripts\archive-change.ps1 -ChangeId "add-readme-feature-docs"

# Commit updated baseline and archive
git add specs/ archive/
git commit -m "chore: Apply and archive XYZ feature docs change"
git push
```

**🎉 Congratulations!** You've completed your first OpenSpec contribution.

---

## Understanding OpenSpec

### What is OpenSpec?

OpenSpec is a **specification governance system** that:
- Tracks changes to important documentation
- Enforces quality standards (SHALL/MUST keywords, scenarios)
- Provides audit trails for all specification updates
- Enables review and collaboration on documentation changes

### Why Do We Use It?

**Without OpenSpec**:
- ❌ Documentation inconsistencies
- ❌ Unclear change history
- ❌ No review process for spec updates
- ❌ Hard to track "who changed what and why"

**With OpenSpec**:
- ✅ All changes documented with proposals
- ✅ Clear rationale (Why/What/Impact)
- ✅ Peer review and validation
- ✅ Complete audit trail in archive/

### Key Concepts

#### 1. Capability Specifications

A **capability** is a major functional area of the project.

Example: `project-documentation` capability governs files like:
- `README.md`
- `AGENTS.md`
- `.github/copilot-instructions.md`
- `docs/SYSTEM_ARCHITECTURE_SPECIFICATION.md`

Each capability has a **baseline spec** in `specs/<capability>/spec.md`.

#### 2. Change Proposals

A **change proposal** is a directory in `changes/<id>/` containing:
- `proposal.md` - Why, What, Impact
- `tasks.md` - Implementation checklist
- `specs/<capability>/spec.md` - Delta specifications

#### 3. Delta Types

**ADDED** - New requirements that don't exist yet
```markdown
## ADDED Requirements
### Requirement: New thing
The system SHALL do new thing.
```

**MODIFIED** - Updates to existing requirements (include FULL text)
```markdown
## MODIFIED Requirements
### Requirement: Existing thing
The system SHALL do existing thing with new behavior added.
```

**REMOVED** - Delete deprecated requirements
```markdown
## REMOVED Requirements
### Requirement: Old thing
#### Reason
No longer needed because...
```

**RENAMED** - Change requirement names only
```markdown
## RENAMED Requirements
- FROM: `### Requirement: Old name`
- TO: `### Requirement: Better name`
```

#### 4. Requirements Format

Every requirement MUST have:
1. **Heading**: `### Requirement: [Name]`
2. **Normative statement**: Contains SHALL or MUST
3. **Scenarios**: At least one `#### Scenario:` with WHEN/THEN

Example:
```markdown
### Requirement: User authentication

The system SHALL authenticate users before granting access.

#### Scenario: Successful login

- **WHEN** user provides valid credentials
- **THEN** system grants access and returns session token

#### Scenario: Invalid credentials

- **WHEN** user provides incorrect password
- **THEN** system denies access and logs the attempt
```

---

## Review Process

### What Reviewers Look For

#### 1. Proposal Quality (proposal.md)

- ✅ **Clear rationale**: Why is this change needed?
- ✅ **Specific scope**: What exactly is changing?
- ✅ **Impact analysis**: Who is affected and how?
- ✅ **Risk assessment**: What could go wrong?

#### 2. Delta Correctness (spec.md)

- ✅ **Proper delta type**: ADDED vs MODIFIED vs REMOVED
- ✅ **Complete requirements**: MODIFIED has full text, not just changes
- ✅ **Normative language**: SHALL or MUST present
- ✅ **Sufficient scenarios**: Each requirement has ≥1 scenario

#### 3. Validation Passing

- ✅ **Strict mode**: `openspec validate --strict` returns 0 errors
- ✅ **Markdown lint**: No formatting violations
- ✅ **Cross-references**: Links to related docs are valid

#### 4. Task Completeness (tasks.md)

- ✅ **All tasks checked**: No incomplete items in PR
- ✅ **Realistic estimates**: Task complexity matches changes
- ✅ **Documentation updates**: Related docs updated if needed

### Typical Review Timeline

| Stage | Time | Actions |
|-------|------|---------|
| **Initial Review** | 2-4 hours | Reviewer checks proposal, deltas, validation |
| **Feedback Round** | 1-2 days | Author addresses comments and feedback |
| **Final Review** | 2-4 hours | Reviewer verifies changes and approves |
| **Merge** | <1 hour | Maintainer merges PR |
| **Post-Merge** | 1 hour | Apply and archive change |

**Total**: Usually 1-3 days for standard changes

### Common Review Comments

**"Missing normative language"**
```markdown
# Reviewer comment
The requirement "The system will authenticate users" should use SHALL.

# Fix
The system SHALL authenticate users...
```

**"Incomplete MODIFIED delta"**
```markdown
# Reviewer comment
This MODIFIED requirement only shows the new scenario. 
Please include all existing scenarios too.

# Fix
## MODIFIED Requirements
### Requirement: Existing requirement
[Full requirement text with ALL scenarios, old and new]
```

**"Scenario format incorrect"**
```markdown
# Reviewer comment
Scenarios must use #### heading, not bullet points.

# Fix (before)
- **Scenario: User login**

# Fix (after)
#### Scenario: User login
```

---

## Governance Rules

### Material vs Non-Material Changes

**Material changes** (require OpenSpec proposal):
- ✅ Adding new features or capabilities
- ✅ Changing system behavior or requirements
- ✅ Updating architectural decisions
- ✅ Modifying API contracts or interfaces
- ✅ Significant restructuring of documentation

**Non-material changes** (direct commit OK):
- ✅ Fixing typos or grammar
- ✅ Updating code examples with no behavior change
- ✅ Reformatting or clarifying existing content
- ✅ Updating timestamps or version numbers
- ✅ Adding cross-references or links

**When in doubt**: Create a proposal. It's better to be thorough.

### Validation Requirements

All changes MUST pass strict validation:

```powershell
openspec validate --strict changes/<your-change-id>
```

**Validation checks**:
1. Every requirement has SHALL or MUST
2. Every requirement has ≥1 scenario
3. Scenarios use `#### Scenario:` heading format
4. MODIFIED deltas reference actual baseline requirements
5. Markdown formatting is correct
6. No broken cross-references

### File Structure Rules

```
changes/<change-id>/
  ├── proposal.md          # Required: Why/What/Impact
  ├── tasks.md             # Required: Implementation checklist
  └── specs/
      └── <capability>/
          └── spec.md      # Required: Delta specifications
```

**All three files are mandatory** for a valid change.

### Commit Message Format

Use conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `docs:` - Documentation changes
- `feat:` - New features
- `fix:` - Bug fixes
- `chore:` - Maintenance tasks

**Examples**:
```
docs(openspec): Add governance for API documentation

- Created change proposal add-api-docs-governance
- Added ADDED requirement for docs/API_REFERENCE.md
- All validations passing

Closes #123
```

---

## Quick Reference

### Common Commands

```powershell
# Create new change
.\scripts\create-change.ps1 -ChangeId "my-change" -Title "My Change"

# Validate specific change
.\scripts\validate-all.ps1 -ChangeId "my-change"

# Validate everything
.\scripts\validate-all.ps1

# Dry run apply
.\scripts\apply-change.ps1 -ChangeId "my-change" -DryRun

# Apply change
.\scripts\apply-change.ps1 -ChangeId "my-change"

# Archive change
.\scripts\archive-change.ps1 -ChangeId "my-change"
```

### Requirement Template

```markdown
### Requirement: [Clear descriptive name]

The [subject] SHALL [normative statement with clear action].

#### Scenario: [Success case name]

- **WHEN** [trigger condition]
- **THEN** [expected outcome]

#### Scenario: [Edge case or failure]

- **WHEN** [edge condition]
- **THEN** [expected behavior]
```

### Proposal Template Checklist

- [ ] **Why**: Clear problem statement or opportunity
- [ ] **What**: Specific changes being proposed (bulleted list)
- [ ] **Impact**: Who is affected, benefits, and risks
- [ ] **Implementation Notes**: Dependencies, references, rollback plan

### Tasks Template Checklist

- [ ] **Documentation Updates**: What files are changing
- [ ] **Capability Spec Changes**: ADDED/MODIFIED/REMOVED deltas
- [ ] **Validation**: Passes strict mode
- [ ] **Review**: Self-review and peer review completed
- [ ] **Submission**: PR created and merged
- [ ] **Post-Merge**: Applied and archived

---

## Getting Help

### Documentation Resources

1. **[README.md](../README.md)** - OpenSpec governance overview
2. **[AGENTS.md](../AGENTS.md)** - Complete governance workflow
3. **[change-patterns.md](./change-patterns.md)** - Delta examples and pitfalls
4. **[scripts/README.md](../scripts/README.md)** - Automation scripts guide
5. **[troubleshooting.md](./troubleshooting.md)** - Common errors _(planned)_
6. **Sample change proposal**: [changes/update-doc-sample-change-demo/](../changes/update-doc-sample-change-demo/)
— full example with proposal, tasks, and delta spec

### Ask Questions

**Stuck on something?** Here's how to get help:

1. **Check existing changes**:
   ```powershell
   openspec list changes
   openspec show changes/<similar-change-id>
   ```

2. **Review examples** in `archive/` - successful past changes

3. **Read validation errors carefully** - they usually point to the fix

4. **Ask in PR comments** - reviewers can guide you

5. **Check GitHub Discussions** - community Q&A

### Common Questions

**Q: Can I update multiple files in one change?**

A: Yes, but keep changes focused. One logical change per proposal.

**Q: What if I'm just fixing a typo?**

A: Typos are non-material - commit directly without OpenSpec proposal.

**Q: How do I know if my change is ADDED vs MODIFIED?**

A: Check the baseline spec in `specs/<capability>/spec.md`:
- If requirement name exists → MODIFIED
- If requirement name is new → ADDED

**Q: Do I need to run `apply` and `archive` myself?**

A: Usually maintainers handle this after merge. Check project conventions.

**Q: What if validation fails and I don't understand why?**

A: Run with JSON output for details:
   ```powershell
   openspec validate --strict --json changes/<id> | ConvertFrom-Json
   ```

**Q: Can I skip scenarios for simple requirements?**

A: No - every requirement MUST have ≥1 scenario. It's a validation rule.

---

## Next Steps

### After Your First Contribution

1. **Review your archived change** in `archive/<your-change-id>/`
2. **Read 2-3 other changes** to see different patterns
3. **Try a more complex change** (MODIFIED or multi-scenario)
4. **Help review others' proposals** - great way to learn

### Learning Path

**Level 1: First Contribution** (30 minutes)
- Create simple ADDED requirement
- Write proposal and basic delta
- Pass validation and get merged

**Level 2: Documentation Updates** (1-2 hours)
- MODIFIED requirements with complete text
- Multiple scenarios per requirement
- Cross-reference other docs

**Level 3: Cross-Cutting Changes** (2-4 hours)
- Changes affecting multiple capabilities
- RENAMED + MODIFIED combinations
- Complex impact analysis

**Level 4: New Capabilities** (4-8 hours)
- Create new capability from scratch
- Define governance model
- Multiple requirements with scenarios

### Contributing to OpenSpec Itself

Want to improve the governance system?

- Propose improvements to workflow in `AGENTS.md`
- Suggest new automation scripts
- Enhance validation rules
- Contribute to troubleshooting docs

**Meta rule**: Changes to OpenSpec governance docs follow OpenSpec process!

---

## Summary

**You now know**:
- ✅ How to create a change proposal
- ✅ How to write proper deltas (ADDED/MODIFIED/REMOVED)
- ✅ How to validate your changes
- ✅ How to submit for review
- ✅ How to apply and archive changes

**Key takeaways**:
1. Material changes → OpenSpec proposal
2. Every requirement needs SHALL/MUST
3. Every requirement needs ≥1 scenario
4. Validate early and often
5. Read examples when stuck

**Ready to contribute?** Go to [Quick Start](#quick-start) and create your first change!

---

**Questions or feedback?** Open an issue or discussion on GitHub.

**Found an error in this guide?** Submit a PR - this guide is governed by OpenSpec too! 😊


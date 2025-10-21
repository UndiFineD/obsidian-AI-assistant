# OpenSpec Validation Troubleshooting Guide

This guide provides solutions to common validation errors encountered when working with OpenSpec.

## Table of Contents

- [Quick Diagnosis](#quick-diagnosis)
- [Common Errors](#common-errors)
- [Error Categories](#error-categories)
- [Debugging Workflow](#debugging-workflow)
- [Prevention Tips](#prevention-tips)

## Quick Diagnosis

### Step 1: Run Validation with JSON Output

```powershell
openspec validate --strict --json changes/<your-change-id>
```

This provides detailed error information including:
- Error type
- File path
- Line number
- Specific issue

### Step 2: Check Error Category

| Error Message Contains | Category | See Section |
|----------------------|----------|-------------|
| "SHALL or MUST keyword" | Normative Language | [#1](#error-1-requirement-must-contain-shall-or-must-keyword) |
| "at least one scenario" | Scenarios | [#2](#error-2-requirement-must-have-at-least-one-scenario) |
| "delta operation" | Delta Types | [#3](#error-3-change-must-have-at-least-one-delta-operation) |
| "MD" or "markdown" | Markdown Lint | [#4](#error-4-markdown-formatting-errors) |
| "requirement not found" | References | [#5](#error-5-modified-requirement-not-found-in-baseline) |
| "Scenario:" format | Scenario Format | [#6](#error-6-scenario-format-invalid) |

### Step 3: Apply the Fix

Jump to the specific error section below for detailed solutions.

---

## Common Errors

### Error 1: "Requirement must contain SHALL or MUST keyword"

#### What it Means

Every requirement MUST include normative language (SHALL or MUST) to be enforceable.

#### Example Error

```json
{
  "path": "requirements.0.text",
  "error": "Requirement must contain SHALL or MUST keyword"
}
```

#### Cause

The requirement text doesn't contain SHALL or MUST:

```markdown
❌ WRONG:
### Requirement: User authentication

The system will authenticate users before granting access.
```

#### Solution

Add SHALL or MUST to the requirement statement:

```markdown
✅ CORRECT:
### Requirement: User authentication

The system SHALL authenticate users before granting access.
```

#### Where to Add the Keyword

The keyword MUST appear in the **first sentence after the heading**:

```markdown
### Requirement: API rate limiting

The API SHALL enforce rate limits of 100 requests per minute per user.
Additional context can follow without SHALL/MUST.
```

#### Common Mistakes

**Mistake 1: Keyword in heading only**
```markdown
❌ WRONG:
### Requirement: The system SHALL authenticate users

Users are authenticated before access.
```

**Mistake 2: Keyword too late in text**
```markdown
❌ WRONG:
### Requirement: User authentication

The system authenticates users. Access is granted only after the 
system SHALL verify credentials.
```

**Fix**: Move SHALL to the first sentence:
```markdown
✅ CORRECT:
### Requirement: User authentication

The system SHALL authenticate users and verify credentials before 
granting access.
```

---

### Error 2: "Requirement must have at least one scenario"

#### What it Means

Every requirement MUST have concrete, testable scenarios showing how it works.

#### Example Error

```json
{
  "path": "requirements.1",
  "error": "Requirement must have at least one scenario"
}
```

#### Cause

The requirement has no `#### Scenario:` sections:

```markdown
❌ WRONG:
### Requirement: User authentication

The system SHALL authenticate users before granting access.

[No scenarios provided]
```

#### Solution

Add at least one scenario with WHEN/THEN structure:

```markdown
✅ CORRECT:
### Requirement: User authentication

The system SHALL authenticate users before granting access.

#### Scenario: Successful authentication

- **WHEN** user provides valid credentials
- **THEN** system grants access and returns session token

#### Scenario: Invalid credentials

- **WHEN** user provides incorrect password
- **THEN** system denies access and logs attempt
```

#### Scenario Format Requirements

1. **Heading level**: Must be `####` (4 hashes)
2. **Keyword**: Must include "Scenario:" after the hashes
3. **Name**: Descriptive name after the colon
4. **Structure**: WHEN/THEN bullets (recommended but not enforced)

#### Common Mistakes

**Mistake 1: Wrong heading level**
```markdown
❌ WRONG - ### (3 hashes):
### Scenario: User login

❌ WRONG - ##### (5 hashes):
##### Scenario: User login

✅ CORRECT - #### (4 hashes):
#### Scenario: User login
```

**Mistake 2: Bullet point instead of heading**
```markdown
❌ WRONG:
- **Scenario: User login**
  - WHEN user provides credentials
  - THEN system authenticates

✅ CORRECT:
#### Scenario: User login

- **WHEN** user provides credentials
- **THEN** system authenticates
```

**Mistake 3: Missing colon**
```markdown
❌ WRONG:
#### Scenario User login

✅ CORRECT:
#### Scenario: User login
```

---

### Error 3: "Change must have at least one delta operation"

#### What it Means

Every change spec MUST have at least one delta section (ADDED, MODIFIED, REMOVED, or RENAMED).

#### Example Error

```json
{
  "path": "spec.md",
  "error": "Change must have at least one delta operation"
}
```

#### Cause

The `spec.md` file is empty or has no delta headers:

```markdown
❌ WRONG:
# Capability: project-documentation

**Change ID**: my-change

[No delta sections]
```

#### Solution

Add at least one delta operation:

```markdown
✅ CORRECT:
# Capability: project-documentation

**Change ID**: my-change

---

## ADDED Requirements

### Requirement: New requirement name

The system SHALL do something new.

#### Scenario: New scenario

- **WHEN** condition
- **THEN** outcome
```

#### Valid Delta Headers

Must use **exact header format** (case-sensitive):

```markdown
## ADDED Requirements       ✅ Correct
## MODIFIED Requirements    ✅ Correct
## REMOVED Requirements     ✅ Correct
## RENAMED Requirements     ✅ Correct
```

#### Common Mistakes

**Mistake 1: Wrong case**
```markdown
❌ WRONG:
## Added Requirements
## added requirements
## ADDED REQUIREMENTS

✅ CORRECT:
## ADDED Requirements
```

**Mistake 2: Wrong heading level**
```markdown
❌ WRONG:
### ADDED Requirements  (3 hashes)
# ADDED Requirements    (1 hash)

✅ CORRECT:
## ADDED Requirements   (2 hashes)
```

**Mistake 3: Typos**
```markdown
❌ WRONG:
## ADDED Requirement   (singular)
## ADD Requirements
## ADDED Requiremnts   (typo)

✅ CORRECT:
## ADDED Requirements  (plural, spelled correctly)
```

---

### Error 4: Markdown Formatting Errors

#### What it Means

The markdown doesn't conform to linting rules defined in `.markdownlint.json`.

#### Example Error

```
MD013/line-length: Line length [Expected: 80; Actual: 145]
MD032/blanks-around-lists: Lists should be surrounded by blank lines
```

#### Common Markdown Issues

**Issue 1: Line too long (MD013)**

```markdown
❌ WRONG (145 characters):
The project SHALL govern material changes to key documentation files via OpenSpec change proposals to maintain consistency and review and ensure quality.

✅ CORRECT (split across lines):
The project SHALL govern material changes to key documentation files 
via OpenSpec change proposals to maintain consistency, review, and 
quality assurance.
```

**Note**: Some projects disable MD013. Check `.markdownlint.json`:
```json
{
  "MD013": false  // Line length disabled
}
```

**Issue 2: Lists need blank lines (MD032)**

```markdown
❌ WRONG:
The requirements are:
- Requirement 1
- Requirement 2
The next paragraph.

✅ CORRECT:
The requirements are:

- Requirement 1
- Requirement 2

The next paragraph.
```

**Issue 3: Multiple headings without content (MD022)**

```markdown
❌ WRONG:
### Requirement: First
### Requirement: Second

✅ CORRECT:
### Requirement: First

Content for first requirement.

### Requirement: Second

Content for second requirement.
```

#### Solution: Auto-fix with Scripts

If you have auto-fix scripts:

```powershell
# Fix JavaScript quality issues (if applicable)
python fix_js_quality.py

# Fix Python formatting (if applicable)
black agent/
```

For markdown, manually adjust or disable rules in `.markdownlint.json`.

---

### Error 5: "MODIFIED requirement not found in baseline"

#### What it Means

You're trying to MODIFY a requirement that doesn't exist in the baseline spec.

#### Example Error

```json
{
  "path": "requirements.0",
  "error": "MODIFIED requirement 'Governance for API docs' not found in baseline spec"
}
```

#### Cause

The requirement name in your MODIFIED delta doesn't match any requirement in 
`specs/<capability>/spec.md`:

```markdown
❌ WRONG (in changes/<id>/specs/project-documentation/spec.md):
## MODIFIED Requirements

### Requirement: Governance for API docs

[But baseline has "Governance for README.md", not "Governance for API docs"]
```

#### Solution 1: Fix the Name

Match the exact name from baseline (whitespace-insensitive):

```powershell
# Check baseline spec
code openspec\specs\project-documentation\spec.md

# Find existing requirement names like:
# "Governance for README.md"
# "Backend agent orchestration and extensibility"
```

Then use the exact name:

```markdown
✅ CORRECT:
## MODIFIED Requirements

### Requirement: Governance for README.md

[Full requirement text with modifications]
```

#### Solution 2: Use ADDED Instead

If this is truly a NEW requirement, use ADDED:

```markdown
✅ CORRECT:
## ADDED Requirements

### Requirement: Governance for API docs

The project SHALL govern material changes to API documentation...

#### Scenario: API docs change

- **WHEN** contributor updates API docs
- **THEN** they create an OpenSpec change
```

#### Common Mistakes

**Mistake 1: Renamed requirement but using MODIFIED**

If you want to change the name, use RENAMED first:

```markdown
✅ CORRECT:
## RENAMED Requirements

- FROM: `### Requirement: Old name`
- TO: `### Requirement: New name`

## MODIFIED Requirements

### Requirement: New name

[Updated requirement using NEW name]
```

**Mistake 2: Typo in requirement name**

```markdown
❌ WRONG:
### Requirement: Governence for README.md  (typo: "Governence")

✅ CORRECT:
### Requirement: Governance for README.md
```

---

### Error 6: "Scenario format invalid"

#### What it Means

Scenarios must use proper heading format, not other markdown elements.

#### Example Error

```json
{
  "path": "requirements.0.scenarios.0",
  "error": "Scenario must use #### heading format with 'Scenario:' keyword"
}
```

#### Cause

Using wrong format for scenarios:

```markdown
❌ WRONG - Bullet point:
- **Scenario: User login**

❌ WRONG - Bold text:
**Scenario: User login**

❌ WRONG - Wrong heading level:
### Scenario: User login

❌ WRONG - Missing colon:
#### Scenario User login
```

#### Solution

Use `####` heading with `Scenario:` keyword:

```markdown
✅ CORRECT:
#### Scenario: User login

- **WHEN** user provides credentials
- **THEN** system authenticates
```

#### Format Breakdown

```
####          Scenario:                User login
^             ^                         ^
|             |                         |
4 hashes      Keyword with colon        Descriptive name
```

#### Common Mistakes

**Mistake: Nesting scenarios under bullets**

```markdown
❌ WRONG:
The requirement has scenarios:
- #### Scenario: First scenario
- #### Scenario: Second scenario

✅ CORRECT:
The requirement has scenarios:

#### Scenario: First scenario

- **WHEN** condition 1
- **THEN** outcome 1

#### Scenario: Second scenario

- **WHEN** condition 2
- **THEN** outcome 2
```

---

## Error Categories

### Validation Error Types

#### 1. **Structural Errors**
- Missing delta operations
- Missing proposal.md or tasks.md
- Incorrect directory structure

**Fix**: Use automation scripts to scaffold correctly:
```powershell
.\scripts\create-change.ps1 -ChangeId "my-change"
```

#### 2. **Content Errors**
- Missing SHALL/MUST keywords
- Missing scenarios
- Wrong scenario format

**Fix**: Review [change-patterns.md](./change-patterns.md) for correct format.

#### 3. **Reference Errors**
- MODIFIED requirement not in baseline
- RENAMED requirement not found
- Broken cross-references

**Fix**: Check baseline spec in `specs/<capability>/spec.md` for exact names.

#### 4. **Formatting Errors**
- Markdown lint violations
- Line length issues
- Missing blank lines

**Fix**: Adjust formatting or update `.markdownlint.json` to disable rules.

---

## Debugging Workflow

### Level 1: Quick Check

```powershell
# Validate specific change
.\scripts\validate-all.ps1 -ChangeId "my-change"
```

**Look for**:
- ✅ Green checkmarks = passing
- ❌ Red errors = needs fixing
- Error messages point to specific issues

### Level 2: Detailed Analysis

```powershell
# Get JSON output for programmatic analysis
openspec validate --strict --json changes/my-change | ConvertFrom-Json
```

**Inspect**:
- `path`: Which requirement or scenario has the issue
- `error`: Exact validation rule that failed
- `line`: Line number (if provided)

### Level 3: Manual Inspection

```powershell
# Open the spec file
code changes\my-change\specs\project-documentation\spec.md

# Compare with baseline
code openspec\specs\project-documentation\spec.md
```

**Check**:
- Requirement names match exactly (for MODIFIED)
- All requirements have SHALL/MUST
- All requirements have ≥1 scenario
- Scenarios use `#### Scenario:` format

### Level 4: Example Review

```powershell
# List successful changes in archive
openspec list archive

# Show a similar archived change
openspec show archive/<similar-change-id>
```

**Learn from**:
- How others structured similar changes
- Proper delta patterns
- Scenario examples

---

## Prevention Tips

### Before Writing

1. **Review examples**: Look at 2-3 archived changes similar to yours
2. **Read patterns guide**: [change-patterns.md](./change-patterns.md)
3. **Use scaffolding**: `.\scripts\create-change.ps1` generates correct structure

### While Writing

1. **Validate often**: Run `validate-all.ps1` after each section
2. **Check templates**: Use requirement/scenario templates from docs
3. **Copy-paste carefully**: When copying from baseline, get ALL content

### Before Submitting

1. **Full validation**: `.\scripts\validate-all.ps1 -ChangeId "my-change"`
2. **Self-review checklist**:
   - [ ] All requirements have SHALL/MUST
   - [ ] All requirements have ≥1 scenario
   - [ ] Scenarios use `#### Scenario:` format
   - [ ] MODIFIED deltas have complete requirement text
   - [ ] Requirement names match baseline exactly (if MODIFIED)
   - [ ] No markdown lint errors
3. **Dry run apply**: `.\scripts\apply-change.ps1 -ChangeId "my-change" -DryRun`

### Validation Checklist Template

```markdown
## Validation Checklist

- [ ] Ran `openspec validate --strict` locally
- [ ] All requirements contain SHALL or MUST
- [ ] All requirements have ≥1 scenario (#### Scenario:)
- [ ] All scenarios use proper heading format
- [ ] MODIFIED deltas include complete requirement text
- [ ] Requirement names match baseline exactly
- [ ] No markdown formatting errors
- [ ] Cross-references are valid
- [ ] proposal.md is complete (Why/What/Impact)
- [ ] tasks.md is complete and checked
```

---

## Quick Reference Card

### Top 5 Validation Errors & Fixes

| # | Error | Quick Fix |
|---|-------|-----------|
| 1 | SHALL/MUST missing | Add to first sentence after heading |
| 2 | No scenarios | Add `#### Scenario:` with WHEN/THEN |
| 3 | No delta operation | Add `## ADDED Requirements` section |
| 4 | Scenario format | Use `####` heading, not bullets |
| 5 | MODIFIED not found | Check baseline for exact requirement name |

### Validation Command Cheat Sheet

```powershell
# Single change validation
openspec validate --strict changes/<id>

# All changes validation
.\scripts\validate-all.ps1

# JSON output for debugging
openspec validate --strict --json changes/<id>

# Specific change with script
.\scripts\validate-all.ps1 -ChangeId "<id>"

# Quiet mode (summary only)
.\scripts\validate-all.ps1 -Quiet
```

### File Location Reference

| Need to check... | File location |
|-----------------|---------------|
| Baseline spec | `specs/<capability>/spec.md` |
| Your change spec | `changes/<id>/specs/<capability>/spec.md` |
| Archived examples | `archive/<id>/` |
| Lint rules | `.markdownlint.json` |
| Automation scripts | `openspec/scripts/` |

---

## Still Stuck?

### Escalation Path

1. **Review this guide** - Most issues have solutions above
2. **Check examples** - `openspec show archive/<similar-change>`
3. **Read change patterns** - [change-patterns.md](./change-patterns.md)
4. **Ask in PR** - Reviewers can help debug
5. **GitHub Discussions** - Community support

### Reporting Validation Bugs

If you believe validation is incorrectly failing:

```markdown
**Title**: Validation error despite correct format

**Steps to reproduce**:
1. Create change with [exact structure]
2. Run `openspec validate --strict`
3. See error: [exact error message]

**Expected**: Validation should pass

**Actual**: Error: [exact error]

**Files**: Attach or link to your change files

**OpenSpec version**: [output of `openspec --version`]
```

### Contributing Improvements

Found this guide helpful? Know a common error we missed?

Submit a PR adding your experience to this troubleshooting guide!

---

**See also**:
- [contributor-guide.md](./contributor-guide.md) - Full contributor walkthrough
- [change-patterns.md](./change-patterns.md) - Delta pattern examples
- [../README.md](../README.md) - OpenSpec overview
- [../scripts/README.md](../scripts/README.md) - Automation scripts

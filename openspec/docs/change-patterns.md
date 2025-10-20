# OpenSpec Change Delta Patterns

This document provides comprehensive guidance on writing change deltas
(ADDED, MODIFIED, REMOVED, RENAMED) for OpenSpec governance.

## Table of Contents

- [Overview](#overview)
- [Delta Types](#delta-types)
- [Pattern Reference](#pattern-reference)
- [Common Pitfalls](#common-pitfalls)
- [Validation Requirements](#validation-requirements)
- [Examples](#examples)

## Overview

**Change deltas** describe how a capability specification changes.
They are the core mechanism for proposing updates to governed documentation.

### Key Principles

1. **Explicit operations**: Always use `## ADDED`, `## MODIFIED`, `## REMOVED`, or `## RENAMED` headers
2. **Complete requirements**: MODIFIED deltas must include full requirement text (not just the changes)
3. **Mandatory scenarios**: Every requirement MUST have at least one scenario
4. **Normative language**: Requirements MUST use SHALL or MUST keywords

### When to Create Deltas

Create a change delta when:

- ✅ Adding new documentation governance requirements
- ✅ Updating existing documentation structure or policies
- ✅ Removing deprecated documentation requirements
- ✅ Renaming capabilities or requirements for clarity

Skip change deltas for:

- ❌ Typo fixes (unless significant)
- ❌ Comment updates
- ❌ Non-normative clarifications
- ❌ Internal documentation notes

## Delta Types

### ADDED

**Purpose**: Introduce new requirements that don't exist in the baseline spec.

**When to use**:
- Adding governance for a new documentation file
- Adding new validation rules or processes
- Introducing new scenarios to handle edge cases

**Pattern**:

```markdown
## ADDED Requirements

### Requirement: [Descriptive name]

The [subject] SHALL [normative statement].

#### Scenario: [Success case name]

- **WHEN** [trigger condition]
- **THEN** [expected outcome]

#### Scenario: [Edge case name]

- **WHEN** [edge condition]
- **THEN** [expected behavior]
```

**Example**:

```markdown
## ADDED Requirements

### Requirement: Governance for API Documentation

The project SHALL govern material changes to `docs/API_REFERENCE.md` via OpenSpec change proposals to 
maintain consistency and review.

#### Scenario: Material change to API_REFERENCE.md requires proposal

- **WHEN** a contributor plans a material update to `docs/API_REFERENCE.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: Minor API documentation updates

- **WHEN** a contributor fixes a typo in API examples
- **THEN** they MAY commit directly without a change proposal
```

### MODIFIED

**Purpose**: Change existing requirements (behavior, scope, or acceptance criteria).

**When to use**:
- Updating governance rules for existing files
- Expanding or restricting requirement scope
- Adding new scenarios to existing requirements
- Clarifying ambiguous language

**Pattern**:

```markdown
## MODIFIED Requirements

### Requirement: [Exact name from baseline spec]

[COMPLETE requirement text with all changes incorporated]

The [subject] SHALL [updated normative statement].

#### Scenario: [Updated or new scenario]

- **WHEN** [condition]
- **THEN** [outcome]

#### Scenario: [Existing scenario if still relevant]

- **WHEN** [condition]
- **THEN** [outcome]
```

**Critical rules**:
1. **Copy the entire baseline requirement** as your starting point
2. **Make your changes** to the copied text
3. **Include ALL scenarios** (old and new)
4. **Match the requirement name exactly** (whitespace-insensitive)

**Example**:

```markdown
## MODIFIED Requirements

### Requirement: Governance for README.md

The project SHALL govern material changes to key documentation files via OpenSpec change proposals to maintain 
consistency and review, and SHALL provide automated validation for all proposals.

#### Scenario: Material change to README.md requires proposal

- **WHEN** a contributor plans a material update to `README.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: Automated validation of README changes

- **WHEN** a change proposal modifies README.md governance
- **THEN** the CI system SHALL automatically validate the proposal before merge
```

### REMOVED

**Purpose**: Deprecate or delete requirements that are no longer applicable.

**When to use**:
- Removing governance for deprecated documentation
- Eliminating outdated validation rules
- Simplifying overly complex requirements

**Pattern**:

```markdown
## REMOVED Requirements

### Requirement: [Name of requirement being removed]

#### Reason

[Explain why this requirement is being removed]

#### Migration

[Explain how to handle existing usage, if applicable]
```

**Example**:

```markdown
## REMOVED Requirements

### Requirement: Governance for CHANGELOG.md

#### Reason

The project has migrated to automated changelog generation via GitHub Actions. Manual CHANGELOG.md updates are no longer required.

#### Migration

Existing CHANGELOG.md entries are preserved in the repository history. Future release notes will be generated automatically from commit messages and pull request descriptions.
```

### RENAMED

**Purpose**: Change the name of a requirement without altering its behavior.

**When to use**:
- Improving requirement clarity with better naming
- Aligning naming conventions across capabilities
- Fixing ambiguous or misleading names

**Pattern**:

```markdown
## RENAMED Requirements

- FROM: `### Requirement: [Old name]`
- TO: `### Requirement: [New name]`
```

**Notes**:
- If you're also changing behavior, use both RENAMED and MODIFIED
- MODIFIED should reference the new name
- Whitespace in names is ignored during matching

**Example**:

```markdown
## RENAMED Requirements

- FROM: `### Requirement: Governance for SETUP.md`
- TO: `### Requirement: Governance for Plugin Setup Documentation`
```

**With behavior change**:

```markdown
## RENAMED Requirements

- FROM: `### Requirement: Governance for SETUP.md`
- TO: `### Requirement: Governance for Plugin Setup Documentation`

## MODIFIED Requirements

### Requirement: Governance for Plugin Setup Documentation

The project SHALL govern material changes to plugin setup documentation files via OpenSpec change proposals 
to maintain consistency, and SHALL require peer review for all setup procedure changes.

#### Scenario: Material change requires proposal and review

- **WHEN** a contributor plans an update to plugin setup documentation
- **THEN** they MUST create a change proposal AND obtain peer review approval
```

## Pattern Reference

### Scenario Format (CRITICAL)

**CORRECT**:

```markdown
#### Scenario: User successfully logs in

- **WHEN** valid credentials are provided
- **THEN** the system returns a JWT token
```

**WRONG** (will fail validation):

```markdown
# These all fail validation:

- **Scenario: User login**  ❌ (bullet point, not heading)
**Scenario: User login**    ❌ (bold only, not heading)
### Scenario: User login   ❌ (wrong heading level - must be ####)
#### Scenario User login   ❌ (missing colon after "Scenario")
```

### Multi-Scenario Requirements

Requirements can (and should) have multiple scenarios:

```markdown
### Requirement: User Authentication

The system SHALL authenticate users via username and password.

#### Scenario: Successful authentication

- **WHEN** valid credentials are provided
- **THEN** the system grants access and returns a session token

#### Scenario: Invalid credentials

- **WHEN** incorrect credentials are provided
- **THEN** the system denies access and logs the attempt

#### Scenario: Account locked after failed attempts

- **WHEN** 5 consecutive failed login attempts occur
- **THEN** the system locks the account for 30 minutes
```

### Requirement Naming

**Good names** (clear, specific, actionable):
- `Governance for README.md`
- `Automated validation in CI`
- `Multi-tenant data isolation`
- `Backend agent orchestration and extensibility`

**Poor names** (vague, ambiguous, or too broad):
- `Documentation` ❌ (too vague)
- `Stuff that needs to happen` ❌ (not descriptive)
- `Requirements for the thing` ❌ (unclear scope)

## Common Pitfalls

### Pitfall 1: Using MODIFIED Without Full Requirement Text

**WRONG**:

```markdown
## MODIFIED Requirements

### Requirement: Governance for README.md

Add automated CI validation.

#### Scenario: CI validation

- **WHEN** PR is submitted
- **THEN** CI validates changes
```

**Problem**: This only shows the addition, not the complete updated requirement.
The archiver will replace the baseline entirely, losing previous content.

**CORRECT**:

```markdown
## MODIFIED Requirements

### Requirement: Governance for README.md

The project SHALL govern material changes to key documentation files via OpenSpec change proposals to maintain 
consistency and review. The system SHALL automatically validate all README.md changes via CI before merge.

#### Scenario: Material change to README.md requires proposal

- **WHEN** a contributor plans a material update to `README.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: Automated CI validation

- **WHEN** a pull request modifies README.md
- **THEN** the CI system SHALL validate the changes before allowing merge
```

### Pitfall 2: Wrong Scenario Format

**WRONG**:

```markdown
- **Scenario: Login success**
  - User provides valid credentials
  - System returns token
```

**CORRECT**:

```markdown
#### Scenario: Login success

- **WHEN** user provides valid credentials
- **THEN** system returns a JWT token
```

### Pitfall 3: Missing SHALL/MUST in Requirement

**WRONG**:

```markdown
### Requirement: User authentication

Users should be authenticated before accessing protected resources.
```

**CORRECT**:

```markdown
### Requirement: User authentication

The system SHALL authenticate users before granting access to protected resources.
```

### Pitfall 4: Using ADDED When Should Use MODIFIED

**WRONG** (if requirement already exists):

```markdown
## ADDED Requirements

### Requirement: Governance for README.md

The project SHALL govern README.md changes with automated CI validation.

#### Scenario: CI validation

- **WHEN** PR submitted
- **THEN** CI validates
```

**Problem**: If "Governance for README.md" already exists in the baseline, this is a MODIFIED change, not ADDED.

**CORRECT**:

```markdown
## MODIFIED Requirements

### Requirement: Governance for README.md

[Full requirement text with CI validation added]

#### Scenario: [All existing scenarios]

#### Scenario: CI validation

- **WHEN** PR submitted
- **THEN** CI validates
```

### Pitfall 5: Incomplete Task List

**WRONG**:

```markdown
## 1. Implementation

- [ ] Update the thing
- [ ] Do stuff
```

**CORRECT**:

```markdown
## 1. Documentation Updates

- [ ] 1.1 Update README.md section 3 with new CI validation info
- [ ] 1.2 Add CI workflow file `.github/workflows/openspec-validate.yml`
- [ ] 1.3 Update contributing guide with validation requirements

## 2. Validation

- [ ] 2.1 Run `openspec validate --strict` and fix all errors
- [ ] 2.2 Test CI workflow in pull request
- [ ] 2.3 Verify all links and cross-references

## 3. Review

- [ ] 3.1 Self-review for completeness
- [ ] 3.2 Request peer review
- [ ] 3.3 Address all feedback
```

## Validation Requirements

### Strict Mode Checks

When you run `openspec validate --strict`, the validator checks:

1. **Requirement keywords**: Every requirement MUST contain SHALL or MUST
2. **Scenario format**: Every requirement MUST have ≥1 scenario with `#### Scenario:` heading
3. **WHEN/THEN format**: Scenarios SHOULD use WHEN/THEN structure (not enforced but strongly recommended)
4. **Delta operations**: At least one `## ADDED`, `## MODIFIED`, `## REMOVED`, or `## RENAMED` section
5. **Markdown formatting**: Passes markdownlint rules (see `.markdownlint.json`)
6. **Reference integrity**: MODIFIED deltas reference actual baseline requirements

### Pre-Validation Checklist

Before running `openspec validate --strict`:

- [ ] All requirements use SHALL or MUST
- [ ] Every requirement has ≥1 scenario
- [ ] All scenarios use `#### Scenario:` format (4 hashes)
- [ ] MODIFIED deltas include complete requirement text
- [ ] Requirement names match baseline exactly (for MODIFIED)
- [ ] File structure is correct (`changes/<id>/specs/<capability>/spec.md`)
- [ ] `proposal.md` and `tasks.md` exist and are complete

## Examples

### Example 1: Adding Governance for New File

**Scenario**: We want to govern a new documentation file that doesn't have governance yet.

**Delta type**: ADDED

**File**: `openspec/changes/add-governance-api-ref/specs/project-documentation/spec.md`

```markdown
## ADDED Requirements

### Requirement: Governance for API Reference Documentation

The project SHALL govern material changes to `docs/API_REFERENCE.md` via OpenSpec change proposals to 
maintain API documentation consistency and accuracy.

#### Scenario: Material API documentation change requires proposal

- **WHEN** a contributor plans a material update to `docs/API_REFERENCE.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: API endpoint documentation updates

- **WHEN** a new API endpoint is added or modified
- **THEN** the contributor SHALL update `docs/API_REFERENCE.md` and include the changes in their proposal

#### Scenario: Minor API documentation corrections

- **WHEN** a contributor fixes typos or formatting in API examples
- **THEN** they MAY commit directly without a formal change proposal
```

### Example 2: Updating Existing Governance Rule

**Scenario**: We want to add automated validation to an existing governance requirement.

**Delta type**: MODIFIED

**File**: `openspec/changes/add-ci-validation/specs/project-documentation/spec.md`

```markdown
## MODIFIED Requirements

### Requirement: Governance for README.md

The project SHALL govern material changes to key documentation files via OpenSpec change proposals to maintain 
consistency and review. All README.md change proposals SHALL be automatically validated in the CI/CD pipeline 
before merge approval.

#### Scenario: Material change to README.md requires proposal

- **WHEN** a contributor plans a material update to `README.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: Automated CI validation for README proposals

- **WHEN** a pull request includes changes to README.md governance
- **THEN** the CI system SHALL run `openspec validate --strict` and block merge if validation fails

#### Scenario: CI validation failure notification

- **WHEN** automated validation detects errors in a README.md proposal
- **THEN** the system SHALL post detailed error messages as PR comments and mark the check as failed
```

### Example 3: Removing Deprecated Governance

**Scenario**: A documentation file is no longer maintained, so we remove its governance requirement.

**Delta type**: REMOVED

**File**: `openspec/changes/remove-legacy-doc-governance/specs/project-documentation/spec.md`

```markdown
## REMOVED Requirements

### Requirement: Governance for LEGACY_GUIDE.md

#### Reason

The `docs/LEGACY_GUIDE.md` file has been deprecated and replaced by the comprehensive `docs/COMPREHENSIVE_GUIDE.md`. The legacy guide is no longer maintained and will be removed in the next major release.

#### Migration

All content from `LEGACY_GUIDE.md` has been migrated to `COMPREHENSIVE_GUIDE.md` with updated examples and current best practices. Contributors should update `COMPREHENSIVE_GUIDE.md` instead.

Existing references to `LEGACY_GUIDE.md` in other documentation will be updated to point to the new comprehensive guide.
```

### Example 4: Renaming for Clarity

**Scenario**: A requirement name is confusing and needs to be clarified without changing behavior.

**Delta type**: RENAMED (only)

**File**: `openspec/changes/clarify-governance-names/specs/project-documentation/spec.md`

```markdown
## RENAMED Requirements

- FROM: `### Requirement: Governance for SETUP.md`
- TO: `### Requirement: Governance for Plugin Installation Guide`
```

### Example 5: Renaming with Behavior Change

**Scenario**: We're renaming AND expanding the scope of a requirement.

**Delta types**: RENAMED + MODIFIED

**File**: `openspec/changes/expand-setup-governance/specs/project-documentation/spec.md`

```markdown
## RENAMED Requirements

- FROM: `### Requirement: Governance for SETUP.md`
- TO: `### Requirement: Governance for Plugin Installation and Configuration`

## MODIFIED Requirements

### Requirement: Governance for Plugin Installation and Configuration

The project SHALL govern material changes to all plugin installation and configuration documentation files 
via OpenSpec change proposals, including setup procedures, configuration examples, and troubleshooting guides.

#### Scenario: Material change to installation documentation requires proposal

- **WHEN** a contributor plans updates to plugin installation documentation
- **THEN** they MUST create an OpenSpec change proposal with deltas under `project-documentation`

#### Scenario: Configuration example updates require review

- **WHEN** a contributor modifies plugin configuration examples
- **THEN** the changes SHALL be reviewed for accuracy and security implications before merge

#### Scenario: Troubleshooting guide additions

- **WHEN** a contributor adds new troubleshooting content to installation guides
- **THEN** they SHALL include reproduction steps and verified solutions in the proposal
```

## Summary Checklist

When creating a change delta:

- [ ] Choose the correct delta type (ADDED, MODIFIED, REMOVED, RENAMED)
- [ ] Use `## [TYPE] Requirements` header
- [ ] Include complete requirement text for MODIFIED deltas
- [ ] Add ≥1 scenario per requirement using `#### Scenario:` format
- [ ] Use SHALL or MUST in requirement statements
- [ ] Match requirement names exactly for MODIFIED/REMOVED deltas
- [ ] Include reason and migration for REMOVED deltas
- [ ] Validate with `openspec validate --strict` before submitting
- [ ] Update `proposal.md` and `tasks.md` accordingly

---

**See also**:
- [README.md](../README.md) - OpenSpec governance overview
- [AGENTS.md](../AGENTS.md) - Complete governance workflow
- [troubleshooting.md](./troubleshooting.md) - Validation error solutions _(planned)_
- [contributor-guide.md](./contributor-guide.md) - Step-by-step onboarding _(planned)_

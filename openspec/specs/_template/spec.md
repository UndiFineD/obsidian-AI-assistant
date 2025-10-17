# [capability-name] Specification Template

## Governed Files and Change History (Summary)
| File/Artifact | Governance Requirement | Last Change Delta Example |
|--------------|-----------------------|--------------------------|
| [file.md]    | Yes/No                | [change-id]              |

## Purpose
Describe the purpose and scope of this capability. What documentation, features, or processes does it govern?

## References
- [README.md](../../README.md)
- [AGENTS.md](../../AGENTS.md)
- [change-patterns.md](../../docs/change-patterns.md)
- [contributor-guide.md](../../docs/contributor-guide.md)
- [troubleshooting.md](../../docs/troubleshooting.md)

## Requirements
### Requirement: [Clear, descriptive name]
The [subject] SHALL [normative statement with clear action].

#### Scenario: [Success case name]
- **WHEN** [trigger condition]
- **THEN** [expected outcome]

#### Scenario: [Edge case or failure]
- **WHEN** [edge condition]
- **THEN** [expected behavior]

---

## Delta Section Examples

### ADDED Requirements
```markdown
## ADDED Requirements

### Requirement: [New requirement name]
The [subject] SHALL [new action].

#### Scenario: [New scenario]
- **WHEN** [condition]
- **THEN** [outcome]
```

### MODIFIED Requirements
```markdown
## MODIFIED Requirements

### Requirement: [Exact name from baseline spec]
[COMPLETE requirement text with all changes incorporated]

#### Scenario: [Updated or new scenario]
- **WHEN** [condition]
- **THEN** [outcome]
```

### REMOVED Requirements
```markdown
## REMOVED Requirements

### Requirement: [Name of requirement being removed]
#### Reason
[Explain why this requirement is being removed]
#### Migration
[Explain how to handle existing usage, if applicable]
```

### RENAMED Requirements
```markdown
## RENAMED Requirements
- FROM: `### Requirement: [Old name]`
- TO: `### Requirement: [New name]`
```

---

**Instructions:**
- Copy this template to create a new capability spec in `specs/<capability>/spec.md`
- Fill in governed files, purpose, references, and requirements
- Use strict format for requirements and scenarios
- Add delta sections for changes (ADDED, MODIFIED, REMOVED, RENAMED)
- Validate with `openspec validate --strict` before submitting

**Last Updated:** October 16, 2025

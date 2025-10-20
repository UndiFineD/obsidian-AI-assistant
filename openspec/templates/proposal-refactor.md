# Proposal: [Refactoring Title]

## Context

**Technical Debt**: Describe the code quality issues being addressed.

**Current Problems**:
- Maintainability: [how current design hampers changes]
- Complexity: [what makes code hard to understand]
- Performance: [if applicable - bottlenecks]
- Testing: [difficult to test scenarios]
- Duplication: [repeated code patterns]

**Motivation**: Why refactor now?
- Blocking: [future features that require this]
- Risk: [increasing bug rate or maintenance cost]
- Opportunity: [related work that makes this timely]

# Proposal: [Refactoring Title]

## Context

**Technical Debt**: Describe the code quality issues being addressed.

**Current Problems**:
- Maintainability: [how current design hampers changes]
- Complexity: [what makes code hard to understand]
- Performance: [if applicable - bottlenecks]
- Testing: [difficult to test scenarios]
- Duplication: [repeated code patterns]

**Motivation**: Why refactor now?
- Blocking: [future features that require this]
- Risk: [increasing bug rate or maintenance cost]
- Opportunity: [related work that makes this timely]

## Goals

**Goals**:
- Improve code maintainability and readability
- Reduce complexity of [specific areas]
- Enable easier testing and debugging
- Maintain 100% backward compatibility (or document breaking changes)
- Keep existing functionality identical

**Non-Goals**:
- Not adding new features (refactor only)
- Not changing external APIs unless necessary
- Not rewriting [parts that work well]
- Not addressing [other technical debt - separate proposal]

## Stakeholders

- **Owner**: [owner]
- **Reviewers**: [reviewers]
- **Affected Teams**: [who maintains this code]
- **Downstream Dependencies**: [who depends on this code]

## What Changes

- Refactor [component/module] to [improved design]
- Extract [shared functionality] into [reusable component]
- Simplify [complex logic] by [approach]
- Improve [code organization/structure]
- Update tests to match new structure
- Update documentation for API changes (if any)

## Goals / Non-Goals

**Goals**:
- Improve code maintainability and readability
- Reduce complexity of [specific areas]
- Enable easier testing and debugging
- Maintain 100% backward compatibility (or document breaking changes)
- Keep existing functionality identical

**Non-Goals**:
- Not adding new features (refactor only)
- Not changing external APIs unless necessary
- Not rewriting [parts that work well]
- Not addressing [other technical debt - separate proposal]

## Stakeholders

- **Owner**: [owner]
- **Reviewers**: [reviewers]
- **Affected Teams**: [who maintains this code]
- **Downstream Dependencies**: [who depends on this code]

## Refactoring Approach

**Current Architecture**:
```
[Diagram or description of current design]
- Component A: [responsibility]
- Component B: [responsibility]
- Issues: [what's problematic]
```

**Proposed Architecture**:
```
[Diagram or description of new design]
- Component A': [improved responsibility]
- Component B': [improved responsibility]
- Benefits: [what this solves]
```

**Migration Strategy**:
1. [Phase 1]: [incremental changes]
2. [Phase 2]: [next set of changes]
3. [Phase 3]: [final cleanup]

**Backward Compatibility**:
- Breaking Changes: [list any - or "None"]
- Deprecation Plan: [if applicable]
- Migration Guide: [how users update their code]

## Risk Assessment

**Low-Risk Changes**:
- [Changes that are safe and isolated]

**Medium-Risk Changes**:
- [Changes that need careful testing]

**High-Risk Changes**:
- [Changes that could affect many systems]
- Mitigation: [how we reduce risk]

**Rollback Plan**:
- [How to revert if issues are discovered]

## Testing Strategy

- **Unit Tests**: [coverage requirements]
- **Integration Tests**: [end-to-end validation]
- **Performance Tests**: [ensure no regressions]
- **Compatibility Tests**: [verify backward compatibility]
- **Pre-Production Testing**: [staging environment validation]

## Success Criteria

- All existing tests pass without modification
- Code complexity metrics improve by [target]
- No performance regressions
- Test coverage maintained or improved
- Documentation updated

## Timeline

- **Proposed**: [date]
- **Target Completion**: [estimate based on scope]
- **Phases**:
    - Phase 1: [scope] - [timeframe]
    - Phase 2: [scope] - [timeframe]
    - Phase 3: [scope] - [timeframe]

## Benefits

- **Maintainability**: [specific improvements]
- **Velocity**: [how this speeds up future work]
- **Quality**: [how this reduces bugs]
- **Developer Experience**: [how this helps the team]

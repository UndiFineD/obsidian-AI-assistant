# Workflow Lanes Guide - How to Choose and Use the Right Lane

**Version**: v0.1.36  
**Status**: ✅ Complete  
**Purpose**: Comprehensive guide for selecting and using appropriate workflow lanes  
**Audience**: Developers, contributors, DevOps engineers, release managers

## Quick Reference

| Lane | Best For | Time | Quality Gates | Coverage | When to Use |
|------|----------|------|---|---|---|
| **📄 Docs** | Documentation-only | <5 min | Minimal | N/A | README, CHANGELOG, docs updates |
| **⚙️ Standard** | Code + Docs | <15 min | Full | 70%+ | Features, bug fixes, typical changes |
| **🔧 Heavy** | Complex refactoring | <20 min | Enhanced | 85%+ | Major refactoring, architecture changes |

---

## Table of Contents

1. [Understanding the Three Lanes](#understanding-the-three-lanes)
2. [Decision Tree: Which Lane Should I Use?](#decision-tree-which-lane-should-i-use)
3. [Detailed Lane Descriptions](#detailed-lane-descriptions)
4. [Using Lanes in Your Workflow](#using-lanes-in-your-workflow)
5. [Examples by Use Case](#examples-by-use-case)
6. [Automatic Lane Detection](#automatic-lane-detection)
7. [Troubleshooting Lane Issues](#troubleshooting-lane-issues)
8. [FAQ](#faq)

---

## Understanding the Three Lanes

The workflow system includes three "lanes" that balance quality assurance with development speed:

### 🟢 Green Lane: Docs (Documentation)
- **Purpose**: Ultra-fast processing for documentation-only changes
- **Time**: <5 minutes (67% faster than standard)
- **Use When**: Updating README, CHANGELOG, API docs, guides
- **Quality**: Focused on documentation completeness
- **Best For**: Quick documentation fixes, releases notes

### 🟡 Yellow Lane: Standard (Normal)
- **Purpose**: Balanced quality and speed for typical development
- **Time**: <15 minutes (typical)
- **Use When**: Adding features, fixing bugs, normal development
- **Quality**: Full validation (all quality gates)
- **Best For**: Everyday development work

### 🔴 Red Lane: Heavy (Complex)
- **Purpose**: Comprehensive validation for critical changes
- **Time**: <20 minutes (with enhanced validation)
- **Use When**: Major refactoring, architecture changes, critical systems
- **Quality**: Stricter thresholds, enhanced security validation
- **Best For**: Large structural changes, security-critical updates

---

## Decision Tree: Which Lane Should I Use?

```
START: What files are you changing?
│
├─ ONLY markdown/documentation files?
│  └─→ YES: Use 📄 DOCS lane
│  └─→ NO: Continue to next question
│
├─ Adding/modifying Python code?
│  └─→ YES: Continue to next question
│  └─→ NO: Use 📄 DOCS lane
│
├─ Is this a small, localized change?
│  │  (1-3 files, <50 lines, single feature)
│  └─→ YES: Use ⚙️ STANDARD lane
│  └─→ NO: Continue to next question
│
├─ Is this affecting >5 files OR >500 lines?
│  │  (refactoring, restructuring)
│  └─→ YES: Use 🔴 HEAVY lane
│  └─→ NO: Use ⚙️ STANDARD lane
│
└─ Does this change core architecture/security?
   └─→ YES: Use 🔴 HEAVY lane
   └─→ NO: Use ⚙️ STANDARD lane (or 📄 DOCS if docs-only)
```

### Quick Decision Rules

1. **Is it ONLY documentation?** → Use 📄 **DOCS**
2. **Is it a BIG change (>5 files, >500 lines)?** → Use 🔴 **HEAVY**
3. **Does it touch ARCHITECTURE or SECURITY?** → Use 🔴 **HEAVY**
4. **Is it a typical FEATURE/BUGFIX?** → Use ⚙️ **STANDARD**
5. **When in doubt** → Use ⚙️ **STANDARD** (safe default)

---

## Detailed Lane Descriptions

### 📄 Docs Lane (Documentation)

**Time Commitment**: ⏱️ <5 minutes

**When to Use**:
- ✅ Updating README.md
- ✅ Modifying CHANGELOG.md
- ✅ Adding documentation files
- ✅ Creating guides or tutorials
- ✅ Fixing typos in docs
- ✅ Adding code comments (no code logic changes)

**When NOT to Use**:
- ❌ Changing any Python code
- ❌ Modifying configuration files (unless purely documentation)
- ❌ Creating new modules or classes
- ❌ Refactoring existing code

**Quality Gates**:
- Documentation completeness check
- Markdown syntax validation
- No code quality gates (ruff, mypy, pytest not needed)

**Pass/Fail Criteria**:
- Documentation files are valid
- Markdown formatting is correct
- No broken links (if checked)

**Example Use Case**:
```
Release Manager updates CHANGELOG.md with v0.1.36 release notes
→ This is documentation-only
→ Use: 📄 DOCS lane
→ Expected time: 2-3 minutes
→ Result: Fast changelog update with minimal validation
```

**Performance**:
- Baseline: 45-90 seconds
- SLA: 300 seconds (5 minutes)
- Typical buffer: 55-85% remaining time

---

### ⚙️ Standard Lane (Normal Development)

**Time Commitment**: ⏱️ <15 minutes

**When to Use**:
- ✅ Adding new features
- ✅ Fixing bugs
- ✅ Modifying existing code
- ✅ Updating tests
- ✅ Adding new modules
- ✅ Updating configuration
- ✅ Typical development work

**When NOT to Use**:
- ❌ Major refactoring across >5 files
- ❌ Architectural changes
- ❌ Security-critical changes
- ❌ Documentation-only updates (use 📄 DOCS instead)

**Quality Gates** (All Enabled):
- Linting (ruff): Code style and correctness
- Type checking (mypy): Type safety
- Testing (pytest): Unit and integration tests
- Security (bandit): Vulnerability scanning

**Coverage Requirements**:
- Minimum 70% test coverage
- All tests must pass
- No high-severity security issues

**Pass/Fail Criteria**:
- ✅ All quality gates pass
- ✅ Code coverage ≥70%
- ✅ No security issues
- ✅ Code style compliant
- ✅ Types valid
- ✅ All tests green

**Example Use Case**:
```
Developer adds a new feature (UserAuthentication class)
→ Touches 3-4 files, 200 lines of code
→ New tests required for coverage
→ Use: ⚙️ STANDARD lane
→ Expected time: 8-12 minutes
→ Result: Full validation with balanced speed
```

**Performance**:
- Baseline: 350-450 seconds
- SLA: 900 seconds (15 minutes)
- Typical buffer: 50-60% remaining time

---

### 🔴 Heavy Lane (Complex Changes)

**Time Commitment**: ⏱️ <20 minutes

**When to Use**:
- ✅ Major refactoring (>5 files)
- ✅ Large structural changes
- ✅ Architectural updates
- ✅ Security-critical changes
- ✅ Cross-module modifications
- ✅ Significant test rewrites
- ✅ Critical system components

**When NOT to Use**:
- ❌ Simple bug fixes
- ❌ Small feature additions
- ❌ Documentation-only updates
- ❌ Typical daily development

**Quality Gates** (Enhanced):
- Linting (ruff): Strict code style
- Type checking (mypy): Complete type coverage
- Testing (pytest): Comprehensive test suite
- Security (bandit): Enhanced vulnerability scanning
- Additional manual review recommended

**Coverage Requirements**:
- Minimum 85% test coverage (vs 70% for standard)
- All tests must pass
- Zero high-severity security issues
- Zero medium-severity security issues in critical paths

**Pass/Fail Criteria**:
- ✅ All quality gates pass with stricter rules
- ✅ Code coverage ≥85%
- ✅ No security issues
- ✅ Code style impeccable
- ✅ Complete type coverage
- ✅ All tests green
- ⚠️ Human review recommended

**Example Use Case**:
```
DevOps engineer restructures entire authentication system
→ Touches 8+ files, 1500+ lines of code
→ Changes core security architecture
→ Extensive test rewrite needed
→ Use: 🔴 HEAVY lane
→ Expected time: 15-20 minutes
→ Result: Comprehensive validation with enhanced security focus
```

**Performance**:
- Baseline: 700-950 seconds
- SLA: 1200 seconds (20 minutes)
- Typical buffer: 20-40% remaining time

---

## Using Lanes in Your Workflow

### Command Line Usage

**Run with explicit lane selection**:
```powershell
python scripts/workflow.py `
    --change-id my-feature `
    --title "Add user authentication" `
    --owner kdejo `
    --lane standard
```

**Options**: `docs`, `standard`, `heavy`

### Automatic Lane Detection

The workflow system can automatically detect the appropriate lane:
```powershell
python scripts/workflow.py `
    --change-id my-feature `
    --title "Add user authentication" `
    --owner kdejo
    # --lane omitted → auto-detects based on changed files
```

**Detection Logic**:
- Scans changed files in current git diff
- Counts Python files, documentation files, total lines changed
- Maps to appropriate lane based on thresholds

See [Automatic Lane Detection](#automatic-lane-detection) below for details.

### In GitHub Actions

Lane detection automatically works in GitHub Actions:

```yaml
name: Workflow with Auto Lane Detection

on: [push, pull_request]

jobs:
  workflow:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Detect lane and run workflow
        run: |
          python scripts/workflow.py \
            --change-id "${{ github.event.pull_request.title }}" \
            --title "${{ github.event.pull_request.title }}" \
            --owner "${{ github.actor }}"
            # Lane auto-detected from changed files
```

---

## Examples by Use Case

### Example 1: Quick Documentation Update

**Scenario**: Release manager updates CHANGELOG.md

**Files Changed**:
- `CHANGELOG.md` (50 lines added)

**Decision**:
- ✅ Only documentation file changed
- ✅ No code changes
- → Use 📄 **DOCS** lane

**Command**:
```powershell
python scripts/workflow.py `
    --change-id release-0.1.36-changelog `
    --title "Release v0.1.36 notes" `
    --owner release-manager `
    --lane docs
```

**Expected Result**:
- ⏱️ Execution: 2-3 minutes
- ✅ Documentation validation passes
- ✅ No quality gates run
- 💾 Quick deployment of release notes

---

### Example 2: Standard Feature Implementation

**Scenario**: Developer adds user login feature

**Files Changed**:
- `agent/auth.py` (250 lines)
- `tests/test_auth.py` (180 lines)
- `docs/AUTHENTICATION.md` (100 lines)
- `agent/settings.py` (30 lines modified)

**Decision Analysis**:
- ❌ NOT documentation-only (code changes exist)
- ✅ Moderate scope (4 files, 560 lines)
- ✅ Single feature focus
- ✅ Typical development work
- → Use ⚙️ **STANDARD** lane

**Command**:
```powershell
python scripts/workflow.py `
    --change-id auth-login-feature `
    --title "Add user login authentication" `
    --owner kdejo `
    --lane standard
```

**Quality Gate Checks**:
- ✅ Ruff linting: Pass
- ✅ MyPy typing: Pass
- ✅ Pytest coverage: 75% (meets 70% minimum)
- ✅ Bandit security: Pass
- ✅ All tests: Green

**Expected Result**:
- ⏱️ Execution: 8-12 minutes
- ✅ All gates pass
- ✅ Ready for merge
- 💾 Feature ready to deploy

---

### Example 3: Major System Refactoring

**Scenario**: Architect refactors entire performance system

**Files Changed**:
- `agent/performance.py` (400 lines rewritten)
- `agent/caching.py` (300 lines refactored)
- `agent/cache_management.py` (250 lines moved)
- `agent/memory_optimization.py` (150 lines new)
- `tests/test_performance.py` (350 lines rewritten)
- `tests/test_caching.py` (300 lines added)
- `docs/PERFORMANCE.md` (200 lines updated)

**Decision Analysis**:
- ❌ NOT documentation-only
- ❌ NOT a small change (7 files, 1950 lines)
- ✅ Major architectural change
- ✅ Cross-module modifications
- ✅ Significant test rewrite
- → Use 🔴 **HEAVY** lane

**Command**:
```powershell
python scripts/workflow.py `
    --change-id perf-system-refactor `
    --title "Refactor performance system architecture" `
    --owner architect `
    --lane heavy
```

**Quality Gate Checks** (Stricter Thresholds):
- ✅ Ruff linting: Pass (strict rules)
- ✅ MyPy typing: Pass (100% coverage)
- ✅ Pytest coverage: 88% (meets 85% minimum)
- ✅ Bandit security: Pass (zero critical/medium)
- ✅ All tests: Green (comprehensive suite)
- ⚠️ Manual review: Recommended before merge

**Expected Result**:
- ⏱️ Execution: 15-20 minutes
- ✅ Enhanced validation passes
- ⚠️ Ready for human review
- 💾 Ready for merge after approval

---

### Example 4: Quick Typo Fix

**Scenario**: Contributor fixes typo in README

**Files Changed**:
- `README.md` (1 line changed: "feture" → "feature")

**Decision**:
- ✅ Documentation-only
- → Use 📄 **DOCS** lane

**Command**:
```powershell
python scripts/workflow.py `
    --change-id readme-typo-fix `
    --title "Fix typo in README" `
    --owner contributor `
    --lane docs
```

**Expected Result**:
- ⏱️ Execution: <1 minute
- ✅ Documentation check passes
- 💾 Immediate merge
- ✨ Community contribution processed instantly

---

### Example 5: Bug Fix with Tests

**Scenario**: Developer fixes issue in indexing module

**Files Changed**:
- `agent/indexing.py` (80 lines fixed)
- `tests/test_indexing.py` (100 lines added for test)

**Decision Analysis**:
- ❌ NOT documentation-only
- ✅ Small, localized change (2 files, 180 lines)
- ✅ Single module focus
- ✅ Bug fix (not refactoring)
- → Use ⚙️ **STANDARD** lane

**Command**:
```powershell
python scripts/workflow.py `
    --change-id indexing-bug-fix `
    --title "Fix PDF indexing crash" `
    --owner kdejo `
    --lane standard
```

**Expected Result**:
- ⏱️ Execution: 6-10 minutes
- ✅ All gates pass
- 💾 Bug fix deployed

---

## Automatic Lane Detection

The workflow system can automatically detect the appropriate lane by analyzing changed files.

### Detection Algorithm

```
1. Identify all changed files in git diff
2. Count:
   - Python files (.py): N_py
   - Documentation files (.md, .txt, .rst): N_doc
   - Total lines changed: N_lines
3. Apply thresholds:
   - IF N_py == 0 AND N_doc > 0:
       → DOCS lane
   - ELIF N_py > 5 OR N_lines > 500:
       → HEAVY lane
   - ELSE:
       → STANDARD lane
```

### Enabling Auto-Detection

**Omit the `--lane` parameter**:
```powershell
python scripts/workflow.py `
    --change-id my-change `
    --title "My change" `
    --owner kdejo
    # --lane omitted → auto-detection active
```

**Output**:
```
[INFO] Lane auto-detection enabled
[INFO] Analyzing changed files...
[INFO] Detected: 3 Python files, 250 lines changed
[INFO] Selected lane: STANDARD (typical code change)
```

### Detection Examples

| Change Type | Files | Lines | Result |
|---|---|---|---|
| README update | 1 (README.md) | 50 | 📄 **DOCS** |
| New feature | 3 (py, py, py) | 300 | ⚙️ **STANDARD** |
| Bug fix | 2 (py, py) | 150 | ⚙️ **STANDARD** |
| Major refactor | 8 (py, py, py, ...) | 1200 | 🔴 **HEAVY** |
| Config + docs | 2 (yaml, md) | 80 | 📄 **DOCS** |
| Feature + tests | 4 (py, py, py, py) | 450 | ⚙️ **STANDARD** |

### Override Auto-Detection

You can always override automatic detection:

```powershell
# Even though auto-detection might suggest STANDARD,
# you know this is heavy, so specify it explicitly
python scripts/workflow.py `
    --change-id my-change `
    --title "My change" `
    --owner kdejo `
    --lane heavy  # Explicit override
```

**When to Override**:
- You know your change is more complex than detected
- Architectural impact not obvious from file count
- Security-critical despite small file count
- When in doubt, use next larger lane

---

## Troubleshooting Lane Issues

### Problem: Wrong Lane Detected

**Symptom**: Auto-detection selected STANDARD but you expected HEAVY

**Solution**:
1. Check file count: `git diff --stat`
2. If >5 files or >500 lines, explicitly specify: `--lane heavy`
3. Or provide context to auto-detection via file analysis

**Example**:
```powershell
# See what changed
git diff --stat

# If many files, explicitly choose HEAVY
python scripts/workflow.py `
    --change-id my-change `
    --title "My change" `
    --owner kdejo `
    --lane heavy
```

### Problem: Docs Lane Selected but Code Also Changed

**Symptom**: Using `--lane docs` but actually have Python code changes

**Issue**: This will skip quality gates that should run!

**Solution**:
1. Double-check: `git diff --name-only | grep -E '\.py$'`
2. If Python files changed, use `--lane standard` instead
3. Always verify before running

**Example**:
```powershell
# Wrong - will skip quality gates for code!
python scripts/workflow.py --lane docs  # ❌ Don't do this if code changed

# Right - includes full validation
python scripts/workflow.py --lane standard  # ✅ Correct
```

### Problem: Execution Takes Longer Than Expected

**Symptom**: STANDARD lane taking 20+ minutes (vs <15 expected)

**Causes**:
1. System resource contention (CPU/memory/disk usage)
2. Quality gate tools running slow (ruff, mypy, pytest)
3. Large test suite or heavy computations

**Solutions**:
1. Check system resources: `top` or Task Manager
2. Run quality gates individually to identify bottleneck:
   ```powershell
   ruff check agent/        # Check linting time
   mypy agent/              # Check type checking time
   pytest tests/            # Check testing time
   ```
3. If still slow, consider using HEAVY lane's parallel execution

### Problem: Lane Took Maximum Time (SLA at Limit)

**Symptom**: DOCS lane took 4:50 (almost 5 minutes)

**Analysis**:
- ✅ Still passing (under 5 minute limit)
- ⚠️ Using most of available buffer

**Recommendations**:
1. Review for unnecessary checks in docs lane
2. Verify no code files accidentally included
3. Monitor future runs for consistency
4. If consistently at limit, consider system upgrade

---

## FAQ

### Q: Which lane should I use by default?

**A**: Use **STANDARD** lane by default for any code change. It provides:
- Full quality validation (all gates)
- Balanced speed (< 15 minutes)
- Safe default (won't skip important checks)

Only use DOCS if truly documentation-only, and HEAVY only for major refactoring.

---

### Q: Can I change lanes mid-workflow?

**A**: No, the lane is set at workflow start. If you need to change lanes:
1. Cancel current workflow: `Ctrl+C`
2. Restart with different `--lane` parameter
3. Or adjust your changes and re-run

---

### Q: What if I'm unsure which lane to use?

**A**: Use this priority:
1. **Default**: ⚙️ STANDARD (always safe)
2. **If 100% docs**: 📄 DOCS
3. **If major refactor**: 🔴 HEAVY

When in doubt, STANDARD is always the safe choice.

---

### Q: Can I enable all quality gates for DOCS lane?

**A**: Yes, you can explicitly override:
```powershell
python scripts/workflow.py `
    --change-id my-docs-change `
    --title "Important docs" `
    --owner kdejo `
    --lane docs `
    --enable-all-gates  # Hypothetical flag
```

However, this defeats the purpose of DOCS lane (speed). Better to use STANDARD.

---

### Q: What if my change doesn't fit any lane?

**A**: The lanes are designed to cover all scenarios:
- **Pure docs?** → 📄 DOCS
- **Code + docs?** → ⚙️ STANDARD
- **Large complex code?** → 🔴 HEAVY

If unsure, use ⚙️ STANDARD. There's no scenario that doesn't fit one of these three.

---

### Q: How do I know if my change qualifies for DOCS lane?

**A**: DOCS lane requires:
- ✅ Zero Python code changes
- ✅ Zero configuration changes
- ✅ Only markdown/text/documentation files modified
- ✅ No infrastructure or deployment changes

If ANY of these aren't met, use STANDARD.

---

### Q: Can I run tests manually before choosing a lane?

**A**: Yes! Use dry-run mode:
```powershell
python scripts/workflow.py `
    --change-id my-change `
    --title "My change" `
    --owner kdejo `
    --lane standard `
    --dry-run  # See what would run
```

This shows what quality gates would execute without actually running them.

---

### Q: What's the performance difference between lanes?

**A**: 
- 📄 DOCS: 45-90 seconds (baseline, no validation)
- ⚙️ STANDARD: 350-450 seconds (4x slower, full validation)
- 🔴 HEAVY: 700-950 seconds (10x slower, enhanced validation)

---

### Q: Are there situations where STANDARD might miss issues?

**A**: STANDARD covers 95% of typical changes. Use HEAVY if:
- Changing 5+ core modules
- >500 lines of code changed
- Architecture/security implications
- Cross-system impact

---

### Q: Can lanes work in GitHub Actions?

**A**: Yes! Example workflow:
```yaml
jobs:
  workflow:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: python scripts/workflow.py \
              --change-id "${{ github.event.pull_request.title }}" \
              --title "${{ github.event.pull_request.title }}" \
              --owner "${{ github.actor }}" \
              --lane standard
```

---

### Q: What if a lane fails? How do I recover?

**A**: All lanes support resumption:
1. Fix the issue
2. Re-run the workflow with same `--change-id`
3. Workflow will resume from checkpoint

Example:
```powershell
# First run fails at mypy check
python scripts/workflow.py --change-id my-change ...

# Fix type errors
# Fix types in your code

# Re-run same command - resumes from checkpoint
python scripts/workflow.py --change-id my-change ...
```

---

## Summary

### Quick Lane Selection

```
Is it ONLY documentation?     → 📄 DOCS (< 5 min)
Is it a big refactor?         → 🔴 HEAVY (< 20 min)
Does it touch architecture?   → 🔴 HEAVY (< 20 min)
Otherwise (typical work)      → ⚙️ STANDARD (< 15 min)
```

### Key Takeaways

1. ✅ **Use DOCS for documentation-only** - Fast and efficient
2. ✅ **Use STANDARD by default for code changes** - Safe and balanced
3. ✅ **Use HEAVY for major refactoring** - Comprehensive validation
4. ✅ **Auto-detection available** - Omit `--lane` to auto-detect
5. ✅ **Override when needed** - Explicit lane always wins

### Next Steps

- ✅ Understand the three lanes
- ✅ Use the decision tree to choose appropriate lane
- ✅ Run your first workflow with lane selection
- ✅ Monitor execution time vs SLA targets
- ✅ Adjust lane if needed for future changes

---

**Last Updated**: v0.1.36  
**For Support**: See [Troubleshooting](#troubleshooting-lane-issues) or consult project documentation  
**Questions?**: Create an issue or ask in discussions

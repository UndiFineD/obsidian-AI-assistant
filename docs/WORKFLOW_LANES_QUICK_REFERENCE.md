# Workflow Lanes Quick Reference Card

**v0.1.36** - Workflow Improvements Three-Lane System

---

## 🎯 Lane Selection Cheat Sheet

| Question | Answer | Lane |
|----------|--------|------|
| **Is it ONLY markdown/docs?** | Yes | 📄 DOCS |
| **Is it code changes?** | Yes | Continue ↓ |
| **Is it >5 files OR >500 lines?** | Yes | 🔴 HEAVY |
| **Architecture or security change?** | Yes | 🔴 HEAVY |
| **Otherwise** | Any code | ⚙️ STANDARD |

---

## ⏱️ Execution Times

```
📄 DOCS:     < 5 minutes   (300s)   - Fast documentation updates
⚙️ STANDARD: < 15 minutes  (900s)   - Typical development work
🔴 HEAVY:    < 20 minutes (1200s)  - Major refactoring
```

---

## ✅ Quality Gates by Lane

| Gate | Docs | Standard | Heavy |
|------|------|----------|-------|
| **Linting (ruff)** | ❌ | ✅ | ✅ |
| **Type check (mypy)** | ❌ | ✅ | ✅ |
| **Tests (pytest)** | ❌ | ✅ | ✅ |
| **Security (bandit)** | ❌ | ✅ | ✅ |
| **Coverage** | N/A | 70%+ | 85%+ |

---

## 🚀 Usage Examples

### Docs Lane (Quick Documentation)
```powershell
python scripts/workflow.py `
    --change-id readme-update `
    --title "Update README" `
    --owner kdejo `
    --lane docs
```
**Use when**: Updating README, CHANGELOG, API docs, guides
**Time**: 1-2 minutes

---

### Standard Lane (Normal Development)
```powershell
python scripts/workflow.py `
    --change-id auth-feature `
    --title "Add user authentication" `
    --owner kdejo `
    --lane standard
```
**Use when**: Features, bug fixes, typical code changes
**Time**: 8-12 minutes

---

### Heavy Lane (Large Refactoring)
```powershell
python scripts/workflow.py `
    --change-id perf-refactor `
    --title "Refactor performance system" `
    --owner kdejo `
    --lane heavy
```
**Use when**: Major refactoring, architecture changes
**Time**: 15-20 minutes

---

### Auto-Detection (Let System Decide)
```powershell
python scripts/workflow.py `
    --change-id my-change `
    --title "My change" `
    --owner kdejo
    # Omit --lane to auto-detect
```
**Result**: System analyzes files and selects appropriate lane

---

## 📊 Lane Decision Matrix

### Docs Lane - Use If
- ✅ Only markdown files changed
- ✅ Only documentation updates
- ✅ No code modifications
- ✅ No configuration changes

### Docs Lane - Don't Use If
- ❌ Any Python files modified
- ❌ Configuration changes
- ❌ Any code logic changed
- ❌ New modules/classes created

---

### Standard Lane - Use If
- ✅ Adding new features
- ✅ Fixing bugs
- ✅ Modifying existing code
- ✅ 1-5 files, <500 lines
- ✅ Typical development work

### Standard Lane - Don't Use If
- ❌ Documentation-only (use DOCS)
- ❌ Major refactoring >5 files
- ❌ Architecture changes
- ❌ Security-critical updates

---

### Heavy Lane - Use If
- ✅ Major refactoring (>5 files)
- ✅ Architecture changes
- ✅ Security-critical changes
- ✅ Cross-module modifications
- ✅ >500 lines of code

### Heavy Lane - Don't Use If
- ❌ Simple documentation updates
- ❌ Small bug fixes
- ❌ Single feature (1-3 files)
- ❌ Typical daily development

---

## 🔧 Troubleshooting

### Wrong Lane Selected?
```powershell
# Check what changed
git diff --stat

# Explicitly override
python scripts/workflow.py `
    --change-id my-change `
    ... parameters ...
    --lane heavy  # Force specific lane
```

### Test Hanging?
- Check system resources: `Get-Process | Measure-Object`
- Increase timeout if needed
- Run quality gates individually to identify bottleneck

### Want to See What Would Run?
```powershell
python scripts/workflow.py `
    ... parameters ...
    --dry-run  # Preview without execution
```

---

## 📚 When to Use Each Lane

### 📄 Docs Lane
**Best for:**
- README, CHANGELOG updates
- Documentation additions
- API guides, tutorials
- Quick typo fixes
- Release notes

**Avoids:**
- Quality gate delays
- Unnecessary code validation
- Complex testing

---

### ⚙️ Standard Lane
**Best for:**
- New features
- Bug fixes
- Code improvements
- Typical PRs
- Most development work

**Provides:**
- Full validation (all gates)
- Balanced speed
- Production confidence

---

### 🔴 Heavy Lane
**Best for:**
- Major refactoring
- Architectural changes
- Security updates
- System redesigns
- Critical components

**Ensures:**
- Stricter validation
- Enhanced security focus
- Comprehensive testing
- 85%+ coverage

---

## 🎓 Learning Resources

**Quick Start**
- This cheat sheet (you are here)

**Comprehensive Guide**
- `docs/WORKFLOW_LANES_GUIDE.md` (5,000+ lines)
- Decision trees, examples, troubleshooting
- Real-world scenarios, FAQ

**Technical Design**
- `openspec/changes/workflow-improvements/spec.md`
- Implementation details
- Performance targets

**Manual Testing**
- `tests/manual_lane_validation.py`
- Optional smoke tests for each lane
- `tests/MANUAL_LANE_VALIDATION_README.md`

---

## 💡 Pro Tips

1. **When unsure → Use STANDARD** (safe default)
2. **Check file count**: `git diff --stat`
3. **Preview first**: Use `--dry-run` flag
4. **Auto-detect**: Omit `--lane` parameter
5. **Override if needed**: Always can specify explicit lane

---

## ✨ Key Features

- ✅ 67% faster for docs-only changes (DOCS lane)
- ✅ Balanced quality/speed for typical work (STANDARD)
- ✅ Enhanced validation for critical changes (HEAVY)
- ✅ Automatic lane detection
- ✅ Checkpoint-based resumption
- ✅ Full test coverage (19/19 tests passing)

---

## 📞 Support

**Can't decide?** → Use STANDARD lane (safest)

**Questions?** → See `docs/WORKFLOW_LANES_GUIDE.md` (comprehensive guide)

**Running tests?** → Use `tests/manual_lane_validation.py` (optional suite)

**GitHub Actions?** → See `INFRA-1_GitHub_Actions_Lane_Support.md` (v0.1.37)

---

**Version**: v0.1.36  
**Updated**: Phase 6 Enhancement  
**Confidence**: ✅ Production Ready

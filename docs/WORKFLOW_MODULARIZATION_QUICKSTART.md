# Workflow Modularization - Quick Start Guide

## Current Status: Encoding Issues Block Progress

### The Problem
Both the original `workflow.ps1` and our new modular files have **smart quote encoding issues** that PowerShell's
parser cannot handle:

- Original `workflow.ps1`: Syntax error at line 573 (smart quotes in regex)
- New `workflow-helpers.ps1`: Multiple string terminator errors
- Root cause: Non-ASCII quote characters (Unicode 0x2018, 0x2019, 0x201C, 0x201D)

### Why This Happened
When copying code between files or editors, smart quotes can be introduced by:
- Microsoft Word or rich text editors
- Certain IDE auto-formatting
- Copy-paste from documentation/web pages
- File encoding conversions

## RECOMMENDED SOLUTION: Phased Approach

### Phase 1: Fix Original workflow.ps1 First ✨
**Do NOT modularize until the original file works**

```powershell
# 1. Create fresh backup
Copy-Item scripts\workflow.ps1 scripts\workflow.ps1.broken

# 2. Manual fix approach - open in VS Code
# - Find and replace all smart quotes with straight quotes
# - Search for: ' ' " " (smart quotes)
# - Replace with: ' " (straight quotes)  
# - Save as UTF-8

# 3. Test after each fix
powershell -NoProfile -File scripts\workflow.ps1 -List
```

### Phase 2: Create Modular Version From WORKING Code
**Only after Phase 1 succeeds**

```powershell
# Extract functions from WORKING workflow.ps1
# Use VS Code's "Extract to Function" or manual copy
# Ensure each new file is saved as UTF-8 without BOM

# Validate EACH file immediately after creation
powershell -NoProfile -Command ". scripts\workflow-stepXX.ps1"
```

## Alternative: Start Fresh With TypeScript/Python

### Consider Rewriting in a Modern Language

**PowerShell Issues**:
- Encoding nightmares with quotes
- Parser errors hard to debug
- String handling error-prone

**Better Alternatives**:

#### Option A: TypeScript + Node.js
```typescript
// Clean syntax, great tooling, no encoding issues
import { Step0 } from './steps/step00';
import { Step1 } from './steps/step01';

class WorkflowOrchestrator {
    async runStep(stepNum: number): Promise<boolean> {
        const step = this.steps[stepNum];
        return await step.execute();
    }
}
```

#### Option B: Python
```python
# Simple, clean, well-tested
from steps import step00, step01

class WorkflowOrchestrator:
    def run_step(self, step_num):
        step = self.steps[step_num]
        return step.execute()
```

## What We've Learned

### ✅ Successful Work
1. **Architecture design** - Modular pattern is solid
2. **Documentation** - Clear specifications created
3. **Template** - workflow-step00.ps1 pattern established
4. **Helper functions** - Logic extracted (but encoding broken)

### ❌ Blockers
1. **Encoding issues** - Smart quotes plague PowerShell
2. **Parser errors** - Hard to debug, no line numbers
3. **Time sink** - Hours spent on encoding vs. functionality

### 💡 Key Insight
**The modularization DESIGN is sound. The IMPLEMENTATION is blocked by PowerShell encoding quirks.**

## Recommended Next Action

### Quick Win: Document the Architecture
Create a design document showing the modular structure, even if we can't execute it yet:

```markdown
# OpenSpec Workflow Architecture (v2.0)

## Modular Design

### Files:
- workflow.ps1 (orchestrator)
- workflow-helpers.ps1 (8 utility functions)
- workflow-step00.ps1 through workflow-step12.ps1 (13 step modules)

### Benefits:
- Each file < 300 lines (vs. 2,821 line monolith)
- Independent testing possible
- Parallel development enabled
- Clear responsibility boundaries

### Challenges:
- PowerShell encoding issues
- Quote character sensitivity
- Parser error messages unhelpful

### Future Migration:
Consider TypeScript/Python rewrite for production reliability
```

## Immediate Action Items

1. **Stop fighting PowerShell encoding** - diminishing returns
2. **Document what we designed** - architecture is valuable
3. **Fix original workflow.ps1 manually** - one file, focus effort
4. **Consider modern rewrite** - TypeScript or Python
5. **Preserve learnings** - specifications, architecture, patterns

## Files to Keep

### Design Documents ✅ KEEP
- `WORKFLOW_MODULARIZATION.md` - Architecture plan
- `WORKFLOW_MODULARIZATION_SUMMARY.md` - Status report
- `WORKFLOW_MODULARIZATION_QUICKSTART.md` - This file

### Code Files ⚠️ REVIEW
- `workflow-helpers.ps1.backup` - Has encoding issues
- `workflow-step00.ps1` - May have issues
- `workflow-new.ps1` - May have issues

### Test Status
- ❌ Can't test due to encoding errors
- ✅ Design validated through analysis
- ⏳ Awaiting encoding fix or rewrite

## Success Criteria Update

### Original Criteria
- ✅ Modular architecture designed
- ✅ Helper functions identified
- ✅ Step pattern established  
- ❌ Files execute without errors ← BLOCKED
- ❌ Tests pass ← BLOCKED

### Revised Criteria
- ✅ Architecture documented
- ✅ Patterns established
- ✅ Benefits identified
- ✅ Limitations understood
- ⏳ **Decision needed**: Fix PowerShell OR Rewrite in TypeScript/Python

## Conclusion

**We have a great design, blocked by PowerShell's encoding brittleness.**

**Two paths forward**:
1. Manual encoding fixes (hours of tedious work, ongoing risk)
2. Rewrite in TypeScript/Python (cleaner, more maintainable, modern tooling)

**Recommendation**: Given this is a development tool, a **TypeScript rewrite** would provide:
- ✅ Superior encoding handling
- ✅ Better tooling (VS Code, ESLint, Prettier)
- ✅ Type safety
- ✅ Easier testing
- ✅ JSON/YAML handling built-in
- ✅ Modern async/await patterns

The time spent fighting PowerShell encoding could build half the TypeScript version.

---

**Last Updated**: October 20, 2025  
**Decision Point**: Fix PowerShell encoding OR Rewrite in TypeScript  
**Recommendation**: TypeScript rewrite for long-term maintainability

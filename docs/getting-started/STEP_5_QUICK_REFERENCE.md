# Step 5 Quick Reference

## What Changed ✅

**Removed:**
- ❌ test_plan.md generation (moved to Step 6)
- ❌ `_generate_test_plan_md()` function

**Added:**
- ✅ spec.md template copy from `openspec/templates/spec.md`
- ✅ Copilot assistance request with instructions
- ✅ Better spec.md creation flow

**Updated:**
- ✅ Module docstring: "Test Definition" → "Specification Definition"

---

## Step 5 Flow

```
Input Files:
├── proposal.md
├── tasks.md
└── todo.md

Process:
├── Check if spec.md exists
├── If template exists → Copy template
│   └── Request Copilot assistance ✨
└── Else → Generate from proposal (fallback)

Output Files:
├── spec.md (from template or generated)
└── updated todo.md (mark Step 5 complete)
```

---

## Copilot Assistance Output

When Step 5 creates spec.md from template, users see:

```
📝 Requesting Copilot assistance to improve spec.md...
Copilot will enhance spec.md based on:
  • proposal.md: [path]
  • tasks.md: [path]
  • todo.md: [path]

Use @copilot in your editor to:
  1. Review the spec.md template structure
  2. Extract key information from proposal.md, tasks.md, and todo.md
  3. Fill in the relevant sections with accurate project details
  4. Ensure specifications are clear, complete, and testable
  5. Add any missing non-functional requirements
```

---

## File Locations

```
scripts/
├── workflow-step05.py ✅ (Modified - test_plan removed)
├── workflow-step06.py ✅ (Unchanged - test_plan still here)
└── workflow-helpers.py (Unchanged)

templates/
└── spec.md (Template for copying)

Documentation:
├── STEP_5_UPDATE_SUMMARY.md (Overview)
├── STEP_5_VERIFICATION_REPORT.md (Technical verification)
└── STEP_5_BEFORE_AFTER.md (Detailed comparison)
```

---

## Key Responsibilities by Step

| Step | Handles | Creates |
|------|---------|---------|
| Step 4 | Proposal & Tasks | proposal.md, tasks.md, todo.md |
| **Step 5** | **Specification** | **spec.md** |
| Step 6 | Implementation | test.py, implement.py, **test_plan.md** |

✅ **test_plan.md is ONLY created by Step 6**

---

## Testing

**Verify Step 5 works:**
```python
from scripts.workflow_step05 import invoke_step5
from pathlib import Path

change_path = Path("openspec/changes/test-change")
result = invoke_step5(change_path, dry_run=False)
assert result, "Step 5 should complete successfully"
```

**Expected files after Step 5:**
- ✅ spec.md (from template or generated)
- ✅ todo.md (updated to mark Step 5 complete)
- ❌ test_plan.md (NOT created here - Step 6's job)

---

## Common Questions

**Q: Where is test_plan.md created now?**
A: Step 6 (workflow-step06.py) - it's no longer in Step 5

**Q: How do I improve spec.md?**
A: Use `@copilot` in your editor - Step 5 shows instructions

**Q: What if template doesn't exist?**
A: Step 5 falls back to generating spec.md from proposal.md

**Q: Does this break existing code?**
A: No - the `invoke_step5()` function signature is unchanged

---

## Verification Checklist

- ✅ test_plan.md removed from Step 5
- ✅ test_plan.md still in Step 6
- ✅ Copilot assistance integrated
- ✅ Template copy working
- ✅ Backward compatible
- ✅ Documentation updated

---

**Status**: ✅ COMPLETE
**Date**: October 23, 2025
**Version**: 0.1.39

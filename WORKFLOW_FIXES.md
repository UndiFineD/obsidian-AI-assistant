# Workflow Script Fixes - October 19, 2025

## Issues Found and Fixed

### 1. Git Commit Messages Not Quoted (Critical)
**Problem**: Git commit commands were missing quotes around commit messages, causing failures when messages contained spaces.

**Error**: `error: switch 'm' requires a value`

**Fixed Lines**:
- Line 1695: `git commit -m $autoMsg` → `git commit -m "$autoMsg"`
- Line 1733: `git commit -m $archiveMsg` → `git commit -m "$archiveMsg"`

### 2. Step 12 (PR Creation) Receiving Invalid Path
**Problem**: After Step 11 archives the change (moving from `openspec/changes/` to `openspec/archive/`), Step 12 was called with the old path that no longer exists. This caused:
- Unable to update todo.md
- Incorrect PR URL generation

**Fix**: Modified `Invoke-Step12` to:
1. Detect if the change has been archived
2. Use the archived path if the original path doesn't exist
3. Update todo.md in the correct location

### 3. PR URL Generation Incorrect
**Problem**: The PR comparison URL was malformed: `compare/$branch?expand=1` instead of `compare/main...$branch?expand=1`

**Fix**: Changed URL format to properly compare against main branch:
```powershell
Write-Info "Visit: https://github.com/UndiFineD/obsidian-AI-assistant/compare/main...$branch?expand=1"
```

## Testing Recommendations

1. **Test git commit with multi-word messages**: Ensure commits work with spaces in messages
2. **Test Step 12 after archiving**: Run workflow through Steps 11-12 to verify PR creation works
3. **Verify PR URL**: Ensure the generated URL properly compares the feature branch against main

## Impact

These fixes resolve:
- Git commit failures in Step 10 (Git Operations)
- Git commit failures in Step 11 (Archive)
- Path resolution issues in Step 12 (PR Creation)
- Incorrect PR URL generation

## Files Modified

- `scripts/workflow.ps1` - Lines 1695, 1733, and 1747-1775 (Step 12 function)

# Workflow Modularization Plan

## Overview

The `scripts/workflow.ps1` file has grown to 2,821 lines, making it difficult to maintain and debug. This document
outlines the modularization strategy to split it into manageable, focused files.

## File Structure

```
scripts/
├── workflow.ps1                 # Main orchestration (parameters, main loop, ~300 lines)
├── workflow-helpers.ps1         # Helper functions (COMPLETED)
├── workflow-step00.ps1          # Step 0: Create TODOs
├── workflow-step01.ps1          # Step 1: Version Increment
├── workflow-step02.ps1          # Step 2: Create Proposal
├── workflow-step03.ps1          # Step 3: Create Specification
├── workflow-step04.ps1          # Step 4: Create Task Breakdown
├── workflow-step05.ps1          # Step 5: Create Test Definition
├── workflow-step06.ps1          # Step 6: Script & Tooling
├── workflow-step07.ps1          # Step 7: Implementation
├── workflow-step08.ps1          # Step 8: Test Run & Validation
├── workflow-step09.ps1          # Step 9: Documentation Update
├── workflow-step10.ps1          # Step 10: Git Operations
├── workflow-step11.ps1          # Step 11: Archive
└── workflow-step12.ps1          # Step 12: Pull Request
```

## Module Responsibilities

### workflow.ps1 (Main Orchestrator)
- Command-line parameter parsing
- Script-level variables
- Dot-sourcing of helper and step modules
- Main execution logic (List mode, Validate mode, Archive mode)
- Interactive workflow loop
- Step execution dispatch

### workflow-helpers.ps1 ✓ COMPLETED
- `Write-Step` - Step header formatting
- `Write-Info`, `Write-Success`, `Write-Error` - Output formatting
- `Set-ContentAtomic` - Atomic file writing
- `Show-Changes` - Display active changes with completion %
- `Test-ChangeStructure` - Validate required files exist
- `Test-DocumentationCrossValidation` - Cross-validate OpenSpec docs (5 checks)

### workflow-step*.ps1 (Individual Steps)
Each step module contains:
- Single `Invoke-StepN` function
- Step-specific validation logic
- Template handling
- Error handling
- Return boolean for success/failure

## Implementation Guidelines

### 1. Module Structure Template

```powershell
<#
.SYNOPSIS
    OpenSpec Workflow - Step N: Description

.DESCRIPTION
    Detailed description of what this step does

.NOTES
    File Name      : workflow-stepNN.ps1
    Requires       : workflow-helpers.ps1
#>

function Invoke-StepN {
    param(
        [string]$ChangePath,
        [string]$Title,
        [string]$Owner
    )
    
    Write-Step N "Step Description"
    
    # Step implementation
    
    return $true  # or $false on failure
}
```

### 2. Dot-Sourcing in Main Script

```powershell
# Load helpers and step functions
. "$PSScriptRoot\workflow-helpers.ps1"
. "$PSScriptRoot\workflow-step00.ps1"
. "$PSScriptRoot\workflow-step01.ps1"
# ... continue for all steps
```

### 3. Shared Variables

Module files access parent scope variables:
- `$ScriptRoot` - Project root directory
- `$ChangesDir` - openspec/changes directory
- `$ArchiveDir` - openspec/archive directory
- `$TemplatesDir` - openspec/templates directory
- `$DryRun` - Dry-run mode flag
- `$script:NewVersion` - Version set in Step 1

### 4. Error Handling Pattern

```powershell
try {
    # Step logic
    return $true
} catch {
    Write-Error "Step N failed: $_"
    return $false
}
```

## Migration Steps

1. ✅ **Create workflow-helpers.ps1**
   - Extract helper functions
   - Add Export-ModuleMember
   - Test independently

1. **Create individual step files** (workflow-step00.ps1 through workflow-step12.ps1)
   - Copy function from original workflow.ps1
   - Add proper header comments
   - Ensure parent scope variable access
   - Test syntax

1. **Refactor main workflow.ps1**
   - Keep parameters and script-level variables
   - Add dot-sourcing of all modules
   - Keep main execution logic
   - Remove extracted functions

1. **Validation**
   - Run syntax check: `powershell -NoProfile -File scripts\workflow.ps1 -List`
   - Test each step individually: `.\workflow.ps1 -ChangeId test -Step N`
   - Verify error handling
   - Check output formatting

## Benefits

### Maintainability
- Each file < 300 lines (vs. 2,821 lines monolith)
- Single responsibility per file
- Easier code review

### Debuggability
- Isolate step-specific issues quickly
- Syntax errors limited to single file
- Clearer stack traces

### Testability
- Unit test individual step functions
- Mock dependencies per module
- Faster test execution

### Collaboration
- Reduced merge conflicts
- Parallel development on different steps
- Clear ownership boundaries

## Testing Plan

### Phase 1: Syntax Validation
```powershell
Get-ChildItem scripts\workflow*.ps1 | ForEach-Object {
    $parseErrors = $null
    [System.Management.Automation.PSParser]::Tokenize(
        (Get-Content $_.FullName -Raw),
        [ref]$parseErrors
    )
    if ($parseErrors) {
        Write-Error "$($_.Name): $($parseErrors.Count) errors"
    } else {
        Write-Host "$($_.Name): OK" -ForegroundColor Green
    }
}
```

### Phase 2: Functional Testing
```powershell
# Test List mode
.\scripts\workflow.ps1 -List

# Test individual steps (dry-run)
for ($i=0; $i -le 12; $i++) {
    .\scripts\workflow.ps1 -ChangeId test-modular -Step $i -DryRun
}

# Test full workflow
.\scripts\workflow.ps1 -ChangeId test-modular -DryRun
```

### Phase 3: Integration Testing
- Run complete workflow on real change
- Verify file creation
- Check cross-validation
- Validate PR creation

## Rollback Plan

If modularization causes issues:

1. **Immediate Rollback**: Use `scripts\workflow.ps1.bak`
   ```powershell
   Copy-Item scripts\workflow.ps1.bak scripts\workflow.ps1 -Force
   ```

1. **Gradual Rollback**: Comment out dot-sourcing, restore functions
   - Keep modular files for reference
   - Re-integrate functions into main script
   - Commit stable state

1. **Hybrid Approach**: Keep complex steps modular, inline simple ones
   - Modularize Steps 2, 4, 6, 7, 10 (most complex)
   - Keep Steps 0, 1, 5, 8, 9, 11, 12 inline

## Current Status

- ✅ **workflow-helpers.ps1**: Created with 8 functions, 425 lines
- ⏳ **Step files**: Pending creation
- ⏳ **Main script refactor**: Pending
- ⏳ **Testing**: Pending

## Next Actions

1. Create workflow-step00.ps1 through workflow-step12.ps1
2. Refactor main workflow.ps1 to use modules
3. Run comprehensive syntax and functional tests
4. Update CHANGELOG.md with modularization details
5. Update documentation references

## Success Criteria

- ✅ All step files < 300 lines
- ✅ No syntax errors in any module
- ✅ `workflow.ps1 -List` works correctly
- ✅ All 13 steps execute successfully in dry-run mode
- ✅ Full workflow completes without errors
- ✅ Test coverage maintained or improved
- ✅ Documentation updated

---

**Last Updated**: October 20, 2025  
**Status**: In Progress - Helpers Complete

<#
.SYNOPSIS
    OpenSpec Workflow Automation Script

.DESCRIPTION
    Automates the OpenSpec workflow for change management in the Obsidian AI Assistant project.
    Implements the 13-stage workflow defined in openspec/PROJECT_WORKFLOW.md.

.PARAMETER ChangeId
    The unique identifier for the change (kebab-case, e.g., "update-doc-readme")

.PARAMETER Title
    The human-readable title of the change

.PARAMETER Owner
    The GitHub handle of the change owner (e.g., "@username")

.PARAMETER Step
    Specific workflow step to execute (0-12). If not specified, runs interactively.

.PARAMETER DryRun
    Preview actions without making changes

.PARAMETER Validate
    Validate the current state of a change

.PARAMETER Archive
    Archive a completed change to openspec/archive/

.PARAMETER List
    List all active changes

.EXAMPLE
    .\scripts\workflow.ps1 -ChangeId "update-doc-readme" -Title "Update README.md" -Owner "@johndoe"
    Creates a new change and runs through the workflow interactively

.EXAMPLE
    .\scripts\workflow.ps1 -ChangeId "update-doc-readme" -Step 8
    Execute step 8 (Test Run & Validation) for an existing change

.EXAMPLE
    .\scripts\workflow.ps1 -List
    List all active changes in openspec/changes/

.EXAMPLE
    .\scripts\workflow.ps1 -ChangeId "update-doc-readme" -Archive
    Archive a completed change

.NOTES
    Author: Obsidian AI Assistant Team
    Version: 1.0.0
    Last Updated: October 18, 2025
    Reference: openspec/PROJECT_WORKFLOW.md
#>

[CmdletBinding(DefaultParameterSetName='Interactive')]
param(
    [Parameter(ParameterSetName='Interactive', Position=0)]
    [Parameter(ParameterSetName='Step')]
    [Parameter(ParameterSetName='Archive', Mandatory=$true)]
    [Parameter(ParameterSetName='Validate', Mandatory=$true)]
    [string]$ChangeId,

    [Parameter(ParameterSetName='Interactive')]
    [string]$Title,

    [Parameter(ParameterSetName='Interactive')]
    [string]$Owner,

    [Parameter(ParameterSetName='Step', Mandatory=$true)]
    [ValidateRange(0, 12)]
    [int]$Step,

    [Parameter(ParameterSetName='Interactive')]
    [Parameter(ParameterSetName='Step')]
    [switch]$DryRun,

    [Parameter(ParameterSetName='Validate', Mandatory=$true)]
    [switch]$Validate,

    [Parameter(ParameterSetName='Archive', Mandatory=$true)]
    [switch]$Archive,

    [Parameter(ParameterSetName='List', Mandatory=$true)]
    [switch]$List
)

# Script variables
$ErrorActionPreference = "Stop"
$ScriptRoot = Split-Path -Parent $PSScriptRoot
$OpenSpecRoot = Join-Path $ScriptRoot "openspec"
$ChangesDir = Join-Path $OpenSpecRoot "changes"
$ArchiveDir = Join-Path $OpenSpecRoot "archive"
$TemplatesDir = Join-Path $OpenSpecRoot "templates"

# Color output functions
function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Step {
    param([int]$StepNumber, [string]$StepName)
    Write-Host "`n========================================" -ForegroundColor Magenta
    Write-Host "Step $StepNumber`: $StepName" -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
}

# List all active changes
function Show-Changes {
    Write-Info "Active changes in openspec/changes/:"
    if (!(Test-Path $ChangesDir)) {
        Write-Warning "No changes directory found at $ChangesDir"
        return
    }

    $changes = Get-ChildItem -Path $ChangesDir -Directory
    if ($changes.Count -eq 0) {
        Write-Info "No active changes found."
        return
    }

    foreach ($change in $changes) {
        $todoPath = Join-Path $change.FullName "todo.md"
        $proposalPath = Join-Path $change.FullName "proposal.md"
        
        Write-Host "`n📁 $($change.Name)" -ForegroundColor Yellow
        
        if (Test-Path $todoPath) {
            $todoContent = Get-Content $todoPath -Raw
            $completedSteps = ([regex]::Matches($todoContent, '\[x\]')).Count
            $totalSteps = ([regex]::Matches($todoContent, '\[[ x]\]')).Count
            Write-Host "   Progress: $completedSteps/$totalSteps steps" -ForegroundColor Cyan
        }
        
        if (Test-Path $proposalPath) {
            $proposalContent = Get-Content $proposalPath -Raw
            if ($proposalContent -match '##\s+Why\s+(.+?)##') {
                $why = $matches[1].Trim() -replace '\r?\n', ' '
                if ($why.Length -gt 80) { $why = $why.Substring(0, 77) + "..." }
                Write-Host "   Why: $why" -ForegroundColor Gray
            }
        }
    }
}

# Validate change structure
function Test-ChangeStructure {
    param([string]$ChangePath)
    
    $valid = $true
    $requiredFiles = @("proposal.md", "tasks.md", "todo.md")
    
    foreach ($file in $requiredFiles) {
        $filePath = Join-Path $ChangePath $file
        if (!(Test-Path $filePath)) {
            Write-Error "Missing required file: $file"
            $valid = $false
        } else {
            Write-Success "Found: $file"
        }
    }
    
    return $valid
}

# Create new change directory structure
function New-ChangeDirectory {
    param(
        [string]$Id,
        [string]$Title,
        [string]$Owner
    )
    
    $changePath = Join-Path $ChangesDir $Id
    
    if (Test-Path $changePath) {
        Write-Error "Change directory already exists: $changePath"
        return $null
    }
    
    Write-Info "Creating change directory: $Id"
    if (!$DryRun) {
        New-Item -ItemType Directory -Path $changePath -Force | Out-Null
        New-Item -ItemType Directory -Path (Join-Path $changePath "specs") -Force | Out-Null
    }
    
    return $changePath
}

# Step 0: Create TODOs
function Invoke-Step0 {
    param([string]$ChangePath, [string]$Title, [string]$Owner)
    
    Write-Step 0 "Create TODOs"
    
    $todoPath = Join-Path $ChangePath "todo.md"
    $templatePath = Join-Path $TemplatesDir "todo.md"
    
    if (!(Test-Path $templatePath)) {
        Write-Error "Template not found: $templatePath"
        return $false
    }
    
    if (!$DryRun) {
        $content = Get-Content $templatePath -Raw
        $content = $content -replace '<Change Title>', $Title
        $content = $content -replace '<change-id>', (Split-Path $ChangePath -Leaf)
        $content = $content -replace '@username', $Owner
        $content = $content -replace 'YYYY-MM-DD', (Get-Date -Format "yyyy-MM-dd")
        $content = $content -replace '\[ \] \*\*0\. Create TODOs\*\*', '[x] **0. Create TODOs**'
        
        Set-Content -Path $todoPath -Value $content -Encoding UTF8
        Write-Success "Created todo.md"
    } else {
        Write-Info "[DRY RUN] Would create: $todoPath"
    }
    
    return $true
}

# Step 1: Increment Release Version
function Invoke-Step1 {
    param([string]$ChangePath)
    
    Write-Step 1 "Increment Release Version [HARD REQUIREMENT]"
    
    Write-Warning "This step requires manual verification!"
    Write-Info "Please ensure you have:"
    Write-Info "  1. Updated CHANGELOG.md with new version (e.g., 0.1.8 → 0.1.9)"
    Write-Info "  2. Updated README.md with new version"
    Write-Info "  3. Updated package.json with new version (if applicable)"
    Write-Info "  4. Documented the version increment"
    
    $response = Read-Host "Have you completed the version increment? (y/n)"
    if ($response -eq 'y') {
        Write-Success "Version increment confirmed"
        if (!$DryRun) {
            Update-TodoFile -ChangePath $ChangePath -CompletedStep 1
        }
        return $true
    }
    
    Write-Warning "Version increment not confirmed. Please complete before proceeding."
    return $false
}

# Step 2: Create Proposal
function Invoke-Step2 {
    param([string]$ChangePath, [string]$Title)
    
    Write-Step 2 "Proposal"
    
    $proposalPath = Join-Path $ChangePath "proposal.md"
    
    # Check if proposal already exists
    if (Test-Path $proposalPath) {
        Write-Info "proposal.md already exists"
        
        # Validate it has required sections
        $content = Get-Content $proposalPath -Raw
        $requiredSections = @("## Why", "## What Changes", "## Impact")
        $missing = @()
        
        foreach ($section in $requiredSections) {
            if ($content -notmatch [regex]::Escape($section)) {
                $missing += $section
            }
        }
        
        if ($missing.Count -gt 0) {
            Write-Error "proposal.md is missing required sections: $($missing -join ', ')"
            Write-Info "Please add these sections before proceeding"
            return $false
        }
        
        # Check if it's still template content
        if ($content -match '\[Explain the problem' -or $content -match '\[List specific changes\]') {
            Write-Error "proposal.md still contains template placeholders"
            Write-Info "Please fill in the proposal content before proceeding"
            Write-Info "Edit: $proposalPath"
            return $false
        }
        
        Write-Success "proposal.md validated"
        if (!$DryRun) {
            Update-TodoFile -ChangePath $ChangePath -CompletedStep 2
        }
        return $true
    }
    
    # Create template
    $template = @"
# Proposal: $Title

## Why

[Explain the problem or opportunity in 1-2 sentences]

## What Changes

- [List specific changes]
- [Mark breaking changes with **BREAKING**]

## Impact

- **Affected specs**: [list capability specs]
- **Affected files**: [list files]
- **Users impacted**: [who is affected]
- **Review priority**: [Low/Medium/High/Critical]

## Alternatives Considered

- [Alternative 1]: [Why not chosen]
- [Alternative 2]: [Why not chosen]

## Related

- **GitHub Issue**: #XXX
- **Related Changes**: [list related change IDs]
"@
    
    if (!$DryRun) {
        Set-Content -Path $proposalPath -Value $template -Encoding UTF8
        Write-Success "Created proposal.md template"
        Write-Info "Please edit: $proposalPath"
        Write-Error "Cannot proceed until proposal.md is filled in"
        Write-Info "Re-run with -Step 2 after editing"
        return $false
    } else {
        Write-Info "[DRY RUN] Would create: $proposalPath"
        return $true
    }
}

# Step 3: Create Specification
function Invoke-Step3 {
    param([string]$ChangePath, [string]$Title)
    
    Write-Step 3 "Specification"
    
    $specsDir = Join-Path $ChangePath "specs"
    
    # Check if specs directory exists and has content
    if (Test-Path $specsDir) {
        $specFiles = Get-ChildItem -Path $specsDir -Filter "*.md" -Recurse
        
        if ($specFiles.Count -eq 0) {
            Write-Error "specs/ directory exists but contains no .md files"
            Write-Info "Create specification files in: $specsDir"
            Write-Info "Example structure: specs/project-documentation/spec.md"
            return $false
        }
        
        # Validate spec files have content (not just templates)
        $validSpecs = 0
        foreach ($specFile in $specFiles) {
            $content = Get-Content $specFile.FullName -Raw
            
            # Check for template placeholders or very short content
            if ($content.Length -lt 200) {
                Write-Warning "Spec file $($specFile.Name) is very short (< 200 chars)"
            } elseif ($content -notmatch '\[' -or $content.Length -gt 500) {
                # Assume valid if no placeholders or substantial content
                $validSpecs++
            }
        }
        
        if ($validSpecs -eq 0) {
            Write-Error "Specification files appear to be incomplete or template-only"
            Write-Info "Please fill in the specification content"
            return $false
        }
        
        Write-Success "Found $($specFiles.Count) specification file(s)"
        Write-Success "Specification files validated"
        if (!$DryRun) {
            Update-TodoFile -ChangePath $ChangePath -CompletedStep 3
        }
        return $true
    }
    
    # Create specs directory if it doesn't exist
    if (!$DryRun) {
        New-Item -ItemType Directory -Path $specsDir -Force | Out-Null
        Write-Success "Created specs/ directory at: $specsDir"
    }
    
    Write-Error "Specification files required before proceeding"
    Write-Info "Create delta specs for each affected capability in: $specsDir"
    Write-Info "Example: specs/project-documentation/spec.md"
    Write-Info "Re-run with -Step 3 after creating specification files"
    
    return $false
}

# Step 4: Create Task Breakdown
function Invoke-Step4 {
    param([string]$ChangePath, [string]$Title)
    
    Write-Step 4 "Task Breakdown"
    
    $tasksPath = Join-Path $ChangePath "tasks.md"
    
    # Check if tasks.md already exists
    if (Test-Path $tasksPath) {
        Write-Info "tasks.md already exists"
        
        # Validate it has content and task checkboxes
        $content = Get-Content $tasksPath -Raw
        
        # Check for task checkboxes
        $taskCount = ([regex]::Matches($content, '- \[[ x]\]')).Count
        
        if ($taskCount -eq 0) {
            Write-Error "tasks.md has no task checkboxes (- [ ] format)"
            Write-Info "Please add actionable tasks before proceeding"
            return $false
        }
        
        # Check if it's still mostly template content
        if ($content -match '\[List any dependencies or blockers\]' -and 
            $content -match '\[Provide effort estimates') {
            Write-Error "tasks.md still contains template placeholders"
            Write-Info "Please fill in the task breakdown before proceeding"
            Write-Info "Edit: $tasksPath"
            return $false
        }
        
        Write-Success "Found $taskCount tasks in tasks.md"
        Write-Success "tasks.md validated"
        if (!$DryRun) {
            Update-TodoFile -ChangePath $ChangePath -CompletedStep 4
        }
        return $true
    }
    
    # Create template
    $template = @"
# Tasks: $Title

## 1. Documentation Updates

- [ ] 1.1 Update relevant documentation
- [ ] 1.2 Add cross-references
- [ ] 1.3 Update table of contents

## 2. Implementation

- [ ] 2.1 Implement core changes
- [ ] 2.2 Add error handling
- [ ] 2.3 Add logging

## 3. Testing

- [ ] 3.1 Write unit tests
- [ ] 3.2 Write integration tests
- [ ] 3.3 Run test suite

## 4. Validation

- [ ] 4.1 Run ``openspec validate --strict``
- [ ] 4.2 Check markdown formatting
- [ ] 4.3 Verify all links work

## 5. Review

- [ ] 5.1 Self-review for clarity
- [ ] 5.2 Submit for team review
- [ ] 5.3 Address feedback

---

## Dependencies

[List any dependencies or blockers]

## Estimated Effort

[Provide effort estimates for each task group]
"@
    
    if (!$DryRun) {
        Set-Content -Path $tasksPath -Value $template -Encoding UTF8
        Write-Success "Created tasks.md template"
        Write-Info "Please edit: $tasksPath"
        Write-Error "Cannot proceed until tasks.md is filled in"
        Write-Info "Re-run with -Step 4 after editing"
        return $false
    } else {
        Write-Info "[DRY RUN] Would create: $tasksPath"
        return $true
    }
}

# Step 5: Create Test Definition
function Invoke-Step5 {
    param([string]$ChangePath, [string]$Title)
    
    Write-Step 5 "Test Definition"
    
    $testPlanPath = Join-Path $ChangePath "test_plan.md"
    
    $template = @"
# Test Plan: $Title

## Test Strategy

### Unit Tests
- [List unit test requirements]
- Coverage goal: XX%

### Integration Tests
- [List integration test scenarios]

### Performance Tests
- [List performance benchmarks, if applicable]

### Security Tests
- [List security validation, if applicable]

## Test Execution

``````bash
# Run unit tests
pytest tests/ -v

# Run with coverage
pytest --cov=backend --cov-report=html --cov-report=term

# Run security scan
bandit -r backend/ -f json -o tests/bandit_report.json
``````

## Acceptance Criteria

- [ ] All tests pass
- [ ] Coverage meets or exceeds goal
- [ ] No new security vulnerabilities
- [ ] Performance benchmarks met

## Test Results

[Document test results after execution]
"@
    
    if (!$DryRun) {
        Set-Content -Path $testPlanPath -Value $template -Encoding UTF8
        Write-Success "Created test_plan.md template"
        Write-Info "Please edit: $testPlanPath"
        Update-TodoFile -ChangePath $ChangePath -CompletedStep 5
    } else {
        Write-Info "[DRY RUN] Would create: $testPlanPath"
    }
    
    return $true
}

# Step 6: Script & Tooling
function Invoke-Step6 {
    param([string]$ChangePath)
    
    Write-Step 6 "Script & Tooling"
    
    Write-Info "Check if any scripts need to be created or updated:"
    Write-Info "  - setup.ps1, setup.sh"
    Write-Info "  - scripts/ directory"
    Write-Info "  - CI/CD configurations"
    Write-Info ""
    Write-Info "If no scripts are needed for this change, you can skip this step."
    
    $response = Read-Host "Have you created/updated necessary scripts? (y/n/skip)"
    if ($response -eq 'y' -or $response -eq 'skip') {
        if ($response -eq 'skip') {
            Write-Info "Skipped: No scripts required for this change"
        }
        Write-Success "Script & tooling step completed"
        if (!$DryRun) {
            Update-TodoFile -ChangePath $ChangePath -CompletedStep 6
        }
        return $true
    }
    
    Write-Error "Scripts not confirmed. Update scripts before proceeding or choose 'skip'."
    return $false
}

# Step 7: Implementation
function Invoke-Step7 {
    param([string]$ChangePath)
    
    Write-Step 7 "Implementation"
    
    Write-Info "Implement the changes as defined in spec and tasks"
    Write-Info "Areas to consider:"
    Write-Info "  - backend/ (Python code)"
    Write-Info "  - plugin/ (JavaScript code)"
    Write-Info "  - tests/ (Test code)"
    Write-Info "  - docs/ (Documentation)"
    Write-Info ""
    Write-Info "Verify your implementation matches the specification and tasks."
    
    # Check if tasks.md exists and validate completion
    $tasksPath = Join-Path $ChangePath "tasks.md"
    if (Test-Path $tasksPath) {
        $tasksContent = Get-Content $tasksPath -Raw
        
        # Count total tasks and completed tasks
        $totalTasks = ([regex]::Matches($tasksContent, '- \[[ x]\]')).Count
        $completedTasks = ([regex]::Matches($tasksContent, '- \[x\]')).Count
        
        if ($totalTasks -gt 0) {
            $percentComplete = [math]::Round(($completedTasks / $totalTasks) * 100)
            Write-Info "Tasks progress: $completedTasks/$totalTasks completed ($percentComplete%)"
            
            if ($completedTasks -eq 0) {
                Write-Warning "No tasks marked as complete in tasks.md"
                Write-Info "Consider marking completed implementation tasks before proceeding"
            }
        }
    }
    
    # Check for uncommitted changes
    $gitStatus = git status --porcelain 2>&1
    if ($LASTEXITCODE -eq 0 -and $gitStatus) {
        $changedFiles = ($gitStatus | Measure-Object).Count
        Write-Info "Detected $changedFiles uncommitted file(s)"
        
        # Parse affected files from proposal
        $proposalPath = Join-Path $ChangePath "proposal.md"
        if (Test-Path $proposalPath) {
            $proposalContent = Get-Content $proposalPath -Raw
            
            # Look for affected files in Impact section
            if ($proposalContent -match '(?m)^-\s*\*\*Affected files\*\*:\s*(.+)') {
                $affectedFiles = $matches[1]
                Write-Info "Expected affected files: $affectedFiles"
            }
            if ($proposalContent -match '(?m)^-\s*\*\*Affected code\*\*:\s*(.+)') {
                $affectedCode = $matches[1]
                Write-Info "Expected affected code: $affectedCode"
            }
        }
    } else {
        Write-Warning "No uncommitted changes detected"
        Write-Info "If you've already committed changes, you can proceed"
        Write-Info "Otherwise, ensure implementation changes are made"
    }
    
    Write-Info ""
    $response = Read-Host "Have you completed the implementation? (y/n/skip)"
    
    if ($response -eq 'y') {
        Write-Success "Implementation completed"
        if (!$DryRun) {
            Update-TodoFile -ChangePath $ChangePath -CompletedStep 7
        }
        return $true
    } elseif ($response -eq 'skip') {
        Write-Warning "Skipping implementation validation"
        Write-Info "Note: This may cause issues in later steps (testing, git operations)"
        $confirm = Read-Host "Are you sure you want to skip? (yes/no)"
        if ($confirm -eq 'yes') {
            if (!$DryRun) {
                Update-TodoFile -ChangePath $ChangePath -CompletedStep 7
            }
            return $true
        }
    }
    
    Write-Error "Implementation not complete. Continue implementation before proceeding."
    Write-Info "Re-run with -Step 7 when ready"
    return $false
}

# Step 8: Test Run & Validation
function Invoke-Step8 {
    param([string]$ChangePath)
    
    Write-Step 8 "Test Run & Validation"
    
    $changeId = Split-Path $ChangePath -Leaf
    
    Write-Info "Running tests for change: $changeId"
    
    if (!$DryRun) {
        # Run pytest with change-specific filter
        Write-Info "Running: pytest -k $changeId -q"
        & pytest -k $changeId -q
        
        $testExitCode = $LASTEXITCODE
        
        if ($testExitCode -eq 0) {
            Write-Success "Tests passed"
            if (!$DryRun) {
                Update-TodoFile -ChangePath $ChangePath -CompletedStep 8
            }
            return $true
        } else {
            Write-Error "Tests failed with exit code: $testExitCode"
            return $false
        }
    } else {
        Write-Info "[DRY RUN] Would run: pytest -k $changeId -q"
        return $true
    }
}

# Step 9: Documentation Update
function Invoke-Step9 {
    param([string]$ChangePath)
    
    Write-Step 9 "Documentation Update"
    
    Write-Info "Update documentation to reflect changes:"
    Write-Info "  - README.md"
    Write-Info "  - docs/ directory files"
    Write-Info "  - CHANGELOG.md"
    Write-Info "  - API documentation"
    Write-Info "  - openspec/ documentation"
    Write-Info ""
    Write-Info "Ensure all changes are documented appropriately."
    
    $response = Read-Host "Have you updated all relevant documentation? (y/n)"
    if ($response -eq 'y') {
        Write-Success "Documentation updated"
        if (!$DryRun) {
            Update-TodoFile -ChangePath $ChangePath -CompletedStep 9
        }
        return $true
    }
    
    Write-Error "Documentation not updated. Complete documentation before proceeding."
    Write-Info "Re-run with -Step 9 when ready"
    return $false
}

# Step 10: Git Operations
function Invoke-Step10 {
    param([string]$ChangePath)
    
    Write-Step 10 "Git Operations"
    
    $changeId = Split-Path $ChangePath -Leaf
    
    Write-Info "Performing git operations..."
    
    if (!$DryRun) {
        # Stage changes
        Write-Info "Staging changes..."
        git add .
        
        # Commit
        git commit -m $autoMsg
        
        # Push
        $branch = git rev-parse --abbrev-ref HEAD
        Write-Info "Pushing to branch: $branch"
        git push origin $branch
        
        Write-Success "Git operations completed"
        Update-TodoFile -ChangePath $ChangePath -CompletedStep 10
        return $true
    } else {
        Write-Info "[DRY RUN] Would perform: git add, commit, push"
        return $true
    }
}

# Step 11: Archive Completed Change
function Invoke-Step11 {
    param([string]$ChangePath)
    
    Write-Step 11 "Archive Completed Change"
    
    $changeId = Split-Path $ChangePath -Leaf
    $archivePath = Join-Path $ArchiveDir $changeId
    
    Write-Info "Archiving change: $changeId"
    Write-Info "From: $ChangePath"
    Write-Info "To: $archivePath"
    
    if (!$DryRun) {
        # Create archive directory
        if (!(Test-Path $ArchiveDir)) {
            New-Item -ItemType Directory -Path $ArchiveDir -Force | Out-Null
        }
        
        # Copy to archive
        Copy-Item -Path $ChangePath -Destination $archivePath -Recurse -Force
        Write-Success "Copied to archive"
        
        # Remove from changes
        Remove-Item -Path $ChangePath -Recurse -Force
        Write-Success "Removed from active changes"
        
    # Commit archive operation (auto-generate from docs)
    git add .
    $doc = Get-ChangeDocInfo -ChangePath $archivePath
    $archiveMsg = New-CommitMessageFromDocs -ChangeId $changeId -DocInfo $doc -Archive
    git commit -m $archiveMsg
        
        $branch = git rev-parse --abbrev-ref HEAD
        git push origin $branch
        
        Write-Success "Archive operation completed and pushed"
        Update-TodoFile -ChangePath $archivePath -CompletedStep 11
        return $true
    } else {
        Write-Info "[DRY RUN] Would archive to: $archivePath"
        Write-Info "[DRY RUN] Would remove: $ChangePath"
        return $true
    }
}

# Step 12: Create Pull Request
function Invoke-Step12 {
    param([string]$ChangePath)
    
    Write-Step 12 "Create Pull Request (PR)"
    
    $changeId = Split-Path $ChangePath -Leaf
    $branch = git rev-parse --abbrev-ref HEAD
    
    Write-Info "Creating Pull Request for change: $changeId"
    Write-Info "Current branch: $branch"
    Write-Info ""
    Write-Info "PR Checklist:"
    Write-Info "  - Title should reference the change"
    Write-Info "  - Description should link to openspec/archive/$changeId/"
    Write-Info "  - All CI checks should pass"
    Write-Info "  - Request appropriate reviewers"
    
    Write-Warning "This step requires manual action on GitHub"
    Write-Info "Visit: https://github.com/UndiFineD/obsidian-AI-assistant/compare/$branch?expand=1"
    
    Read-Host "Press Enter when PR has been created" | Out-Null
    Write-Success "Pull Request step completed"
    
    if (!$DryRun) {
        Update-TodoFile -ChangePath $ChangePath -CompletedStep 12
    }
    
    return $true
}

# Update TODO markdown file
function Update-TodoFile {
    param(
        [string]$ChangePath,
        [int]$CompletedStep
    )
    
    $todoPath = Join-Path $ChangePath "todo.md"
    if (!(Test-Path $todoPath)) {
        Write-Warning "todo.md not found at $todoPath"
        return
    }
    
    $content = Get-Content $todoPath -Raw
    
    # Update workflow progress
    $stepPattern = "\[\s\]\s\*\*$CompletedStep\."
    $content = $content -replace $stepPattern, "[x] **$CompletedStep."
    
    Set-Content -Path $todoPath -Value $content -Encoding UTF8
    Write-Success "Updated todo.md for step $CompletedStep"
}

# Extract metadata from change documentation (proposal.md, etc.)
function Get-ChangeDocInfo {
    param(
        [string]$ChangePath
    )

    $doc = [pscustomobject]@{
        Title         = $null
        Why           = $null
        AffectedSpecs = $null
        AffectedFiles = $null
        AffectedCode  = $null
        ProposalPath  = $null
    }

    try {
        $proposalPath = Join-Path $ChangePath "proposal.md"
        $doc.ProposalPath = $proposalPath
        if (Test-Path $proposalPath) {
            $content = Get-Content $proposalPath -Raw

            # Title: from "# Proposal: <Title>" or "# Change Proposal: <Title>"
            $m = [regex]::Match($content, '(?m)^#\s*(?:Change\s+)?Proposal:\s*(.+)')
            if ($m.Success) { $doc.Title = $m.Groups[1].Value.Trim() }

            # Why: text under "## Why" until next heading
            $m = [regex]::Match($content, '(?s)##\s*Why\s*(.+?)(?:\r?\n##\s|\Z)')
            if ($m.Success) { $doc.Why = ($m.Groups[1].Value.Trim() -replace '\r?\n', ' ') }

            # Affected specs/files (if present in Impact section)
            $m = [regex]::Match($content, '(?m)^-\s*\*\*Affected specs\*\*:\s*(.+)')
            if ($m.Success) { $doc.AffectedSpecs = $m.Groups[1].Value.Trim() }

            $m = [regex]::Match($content, '(?m)^-\s*\*\*Affected files\*\*:\s*(.+)')
            if ($m.Success) { $doc.AffectedFiles = $m.Groups[1].Value.Trim() }

            # Some proposals may use "Affected code" instead of "Affected files"
            $m = [regex]::Match($content, '(?m)^-\s*\*\*Affected code\*\*:\s*(.+)')
            if ($m.Success) { $doc.AffectedCode = $m.Groups[1].Value.Trim() }
        }
    } catch {
        Write-Warning "Unable to parse proposal.md for commit message generation: $_"
    }

    return $doc
}

# Build a commit message from documentation metadata
function New-CommitMessageFromDocs {
    param(
        [string]$ChangeId,
        [psobject]$DocInfo,
        [switch]$Archive
    )

    $titlePart = if ($DocInfo.Title) { $DocInfo.Title } else { "Complete workflow for $ChangeId" }
    $firstLine = "chore(openspec): $titlePart ($ChangeId)"

    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add($firstLine) | Out-Null
    $lines.Add("") | Out-Null
    $lines.Add("OpenSpec Change: $ChangeId") | Out-Null

    if ($DocInfo.Why) {
        $why = $DocInfo.Why
        if ($why.Length -gt 240) { $why = $why.Substring(0, 237) + '...' }
        $lines.Add("Why: $why") | Out-Null
    }

    if ($DocInfo.AffectedSpecs) { $lines.Add("Affected specs: $($DocInfo.AffectedSpecs)") | Out-Null }
    if ($DocInfo.AffectedFiles) { $lines.Add("Affected files: $($DocInfo.AffectedFiles)") | Out-Null }
    if ($DocInfo.AffectedCode)  { $lines.Add("Affected code: $($DocInfo.AffectedCode)")   | Out-Null }

    # Doc links
    $relativePath = if ($Archive) { "openspec/archive/$ChangeId/proposal.md" } else { "openspec/changes/$ChangeId/proposal.md" }
    if ($DocInfo.ProposalPath) { $lines.Add("Docs: $relativePath") | Out-Null }

    if ($Archive) { $lines.Add("Action: Archive completed change") | Out-Null }

    $lines.Add("") | Out-Null
    $lines.Add("Ref: openspec/PROJECT_WORKFLOW.md") | Out-Null

    return ($lines -join "`n")
}

# Main workflow execution
function Invoke-Workflow {
    param(
        [string]$ChangeId,
        [string]$Title,
        [string]$Owner,
        [int]$StartStep = 0,
        [int]$EndStep = 12
    )
    
    $changePath = Join-Path $ChangesDir $ChangeId
    
    # If change doesn't exist and we're starting from step 0, create it
    if (!(Test-Path $changePath) -and $StartStep -eq 0) {
        $changePath = New-ChangeDirectory -Id $ChangeId -Title $Title -Owner $Owner
        if ($null -eq $changePath) {
            return $false
        }
    } elseif (!(Test-Path $changePath)) {
        Write-Error "Change not found: $ChangeId"
        Write-Info "Create the change first with step 0"
        return $false
    }
    
    # Enforce sequential execution: Check that previous steps are complete
    if ($StartStep -gt 0 -and !$DryRun) {
        $todoPath = Join-Path $changePath "todo.md"
        if (Test-Path $todoPath) {
            $todoContent = Get-Content $todoPath -Raw
            
            # Check that all previous steps are marked complete
            for ($prev = 0; $prev -lt $StartStep; $prev++) {
                # Match both simple and detailed formats
                $simplePattern = "- \[x\] $prev\."
                $detailedPattern = "- \[x\] \*\*$prev\."
                
                if (($todoContent -notmatch [regex]::Escape($simplePattern)) -and
                    ($todoContent -notmatch [regex]::Escape($detailedPattern))) {
                    Write-Error "Cannot execute Step $StartStep - Step $prev is not complete"
                    Write-Info "Steps must be executed in order: 0 → 1 → 2 → ... → 12"
                    Write-Info "Complete Step $prev first, then re-run"
                    return $false
                }
            }
        }
    }
    
    # Execute workflow steps
    for ($i = $StartStep; $i -le $EndStep; $i++) {
        $success = switch ($i) {
            0 { Invoke-Step0 -ChangePath $changePath -Title $Title -Owner $Owner }
            1 { Invoke-Step1 -ChangePath $changePath }
            2 { Invoke-Step2 -ChangePath $changePath -Title $Title }
            3 { Invoke-Step3 -ChangePath $changePath -Title $Title }
            4 { Invoke-Step4 -ChangePath $changePath -Title $Title }
            5 { Invoke-Step5 -ChangePath $changePath -Title $Title }
            6 { Invoke-Step6 -ChangePath $changePath }
            7 { Invoke-Step7 -ChangePath $changePath }
            8 { Invoke-Step8 -ChangePath $changePath }
            9 { Invoke-Step9 -ChangePath $changePath }
            10 { Invoke-Step10 -ChangePath $changePath }
            11 { Invoke-Step11 -ChangePath $changePath }
            12 { Invoke-Step12 -ChangePath $changePath }
        }
        
        if ($success -and !$DryRun) {
            Update-TodoFile -ChangePath $changePath -CompletedStep $i
        }
        
        if (!$success) {
            Write-Error "Step $i failed. Workflow halted."
            Write-Info "Fix the issues and re-run with: .\scripts\workflow.ps1 -ChangeId '$ChangeId' -Step $i"
            return $false
        }
        
        # If running specific step, exit after completion
        if ($PSCmdlet.ParameterSetName -eq 'Step') {
            break
        }
        
        # Ask to continue to next step (except for last step)
        if ($i -lt $EndStep -and $PSCmdlet.ParameterSetName -eq 'Interactive') {
            $response = Read-Host "`nContinue to next step? (y/n)"
            if ($response -ne 'y') {
                Write-Info "Workflow paused. Resume with: .\scripts\workflow.ps1 -ChangeId '$ChangeId' -Step $($i + 1)"
                return $true
            }
        }
    }
    
    Write-Success "`n🎉 Workflow completed for change: $ChangeId"
    return $true
}

# Main script execution
try {
    Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║   OpenSpec Workflow Automation v1.0    ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Cyan
    
    switch ($PSCmdlet.ParameterSetName) {
        'List' {
            Show-Changes
        }
        'Validate' {
            $changePath = Join-Path $ChangesDir $ChangeId
            if (!(Test-Path $changePath)) {
                Write-Error "Change not found: $ChangeId"
                exit 1
            }
            $valid = Test-ChangeStructure -ChangePath $changePath
            if ($valid) {
                Write-Success "Change structure is valid"
                exit 0
            } else {
                Write-Error "Change structure is invalid"
                exit 1
            }
        }
        'Archive' {
            $changePath = Join-Path $ChangesDir $ChangeId
            if (!(Test-Path $changePath)) {
                Write-Error "Change not found: $ChangeId"
                exit 1
            }
            $success = Invoke-Step11 -ChangePath $changePath
            exit ($success ? 0 : 1)
        }
        'Step' {
            if ([string]::IsNullOrWhiteSpace($ChangeId)) {
                Write-Error "ChangeId is required when using -Step"
                exit 1
            }
            $success = Invoke-Workflow -ChangeId $ChangeId -Title "" -Owner "" -StartStep $Step -EndStep $Step
            exit ($success ? 0 : 1)
        }
        'Interactive' {
            if ([string]::IsNullOrWhiteSpace($ChangeId)) {
                Write-Error "ChangeId is required"
                Write-Info "Usage: .\scripts\workflow.ps1 -ChangeId 'my-change' -Title 'My Change' -Owner '@me'"
                exit 1
            }
            
            # Provide defaults for Title and Owner if not specified
            if ([string]::IsNullOrWhiteSpace($Title)) {
                $Title = $ChangeId -replace '-', ' ' | ForEach-Object { $_.Substring(0,1).ToUpper() + $_.Substring(1) }
            }
            if ([string]::IsNullOrWhiteSpace($Owner)) {
                $gitUser = git config user.name
                $Owner = if ($gitUser) { "@$gitUser" } else { "@unknown" }
            }
            
            $success = Invoke-Workflow -ChangeId $ChangeId -Title $Title -Owner $Owner
            exit ($success ? 0 : 1)
        }
    }
}
catch {
    Write-Error "An error occurred: $_"
    Write-Error $_.ScriptStackTrace
    exit 1
}

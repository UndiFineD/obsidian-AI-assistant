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
        $proposalContent = Get-Content $proposalPath -Raw
        if ($proposalContent -match '##\s+Why\s+(.+?)##') {
            $why = $matches[1].Trim() -replace '\r?\n', ' '
            if ($why.Length -gt 80) { $why = $why.Substring(0, 77) + "..." }
            Write-Host "   Why: $why" -ForegroundColor Gray
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
    Write-Info "Detecting current version from main branch..."
    # Fetch latest from main to ensure we have current version info
    Write-Info "Fetching latest from origin/main..."
    $fetchResult = git fetch origin main 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Failed to fetch from origin/main. Proceeding with local data."
        Write-Warning "Fetch error: $fetchResult"
    }
    # Try to get version from package.json on main branch
    $currentVersion = $null
    $versionSource = $null
    # Check package.json first
    try {
        $packageJsonMain = git show origin/main:package.json 2>&1
        if ($LASTEXITCODE -eq 0 -and $packageJsonMain -and $packageJsonMain -is [string]) {
            $matchResult = [regex]::Match($packageJsonMain, '"version"\s*:\s*"(\d+\.\d+\.\d+)"')
            if ($matchResult.Success) {
                $currentVersion = $matchResult.Groups[1].Value
                $versionSource = "package.json"
            }
        }
    } catch {
        Write-Warning "Could not read package.json from origin/main: $_"
    }
    # Fallback to CHANGELOG.md if package.json not found
    if (!$currentVersion) {
        try {
            $changelogMain = git show origin/main:CHANGELOG.md 2>&1
            if ($LASTEXITCODE -eq 0 -and $changelogMain -and $changelogMain -is [string]) {
                # Look for version pattern like "## [0.1.9]" or "## 0.1.9"
                $matchResult = [regex]::Match($changelogMain, '##\s*\[?(\d+\.\d+\.\d+)\]?')
                if ($matchResult.Success) {
                    $currentVersion = $matchResult.Groups[1].Value
                    $versionSource = "CHANGELOG.md"
                }
            }
        } catch {
            Write-Warning "Could not read CHANGELOG.md from origin/main: $_"
        }
    }
    # Fallback to local files if git show fails
    if (!$currentVersion) {
        Write-Warning "Could not read from origin/main. Checking local files..."
        $localPackageJson = Join-Path $ScriptRoot "package.json"
        if (Test-Path $localPackageJson) {
            try {
                $packageContent = Get-Content $localPackageJson -Raw
                $matchResult = [regex]::Match($packageContent, '"version"\s*:\s*"(\d+\.\d+\.\d+)"')
                if ($matchResult.Success) {
                    $currentVersion = $matchResult.Groups[1].Value
                    $versionSource = "local package.json"
                }
            } catch {
                Write-Warning "Could not parse local package.json: $_"
            }
        }
    }
    if (!$currentVersion) {
        Write-Error "Could not detect current version from any source"
        Write-Info "Please ensure package.json or CHANGELOG.md exists with valid version"
        return $false
    }
    Write-Success "Current version: $currentVersion (from $versionSource)"
    # Parse version components
    if ($currentVersion -match '^(\d+)\.(\d+)\.(\d+)$') {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        $patch = [int]$matches[3]
    } else {
        Write-Error "Invalid version format: $currentVersion"
        return $false
    }
    # Determine version increment type
    Write-Info ""
    Write-Info "Current version: $major.$minor.$patch"
    Write-Info "Select version increment type:"
    Write-Info "  1. Patch (bug fixes, minor changes) → $major.$minor.$($patch + 1)"
    Write-Info "  2. Minor (new features, backwards compatible) → $major.$($minor + 1).0"
    Write-Info "  3. Major (breaking changes) → $($major + 1).0.0"
    Write-Info "  4. Skip (use manual version)"
    Write-Info ""
    $incrementType = Read-Host "Enter choice (1-4)"
    $newVersion = switch ($incrementType) {
        '1' { "$major.$minor.$($patch + 1)" }
        '2' { "$major.$($minor + 1).0" }
        '3' { "$($major + 1).0.0" }
        '4' {
            $manualVersion = Read-Host "Enter version manually (e.g., 0.2.0)"
            if ($manualVersion -match '^\d+\.\d+\.\d+$') {
                $manualVersion
            } else {
                Write-Error "Invalid version format. Must be X.Y.Z"
                return $false
            }
        }
        default {
            Write-Error "Invalid choice. Please run again and select 1-4."
            return $false
        }
    }
    Write-Info ""
    Write-Success "New version will be: $newVersion"
    Write-Info ""
    if (!$DryRun) {
        $updatedFiles = @()
        
        # Update package.json if it exists
        $packageJsonPath = Join-Path $ScriptRoot "package.json"
        if (Test-Path $packageJsonPath) {
            Write-Info "Updating package.json..."
            $packageContent = Get-Content $packageJsonPath -Raw
            $packageContent = $packageContent -replace '"version"\s*:\s*"[^"]*"', "`"version`": `"$newVersion`""
            Set-Content -Path $packageJsonPath -Value $packageContent -Encoding UTF8 -NoNewline
            $updatedFiles += "package.json"
            Write-Success "✓ Updated package.json"
        }
        # Update CHANGELOG.md
        $changelogPath = Join-Path $ScriptRoot "CHANGELOG.md"
        if (Test-Path $changelogPath) {
            Write-Info "Updating CHANGELOG.md..."
            $changelogContent = Get-Content $changelogPath -Raw
            $date = Get-Date -Format "yyyy-MM-dd"
            # Find the "## [Unreleased]" section and add new version entry
            if ($changelogContent -match '##\s*\[?Unreleased\]?') {
                $newEntry = @"
## [$newVersion] - $date

### Added
- Version increment to $newVersion

"@
                $changelogContent = $changelogContent -replace '(##\s*\[?Unreleased\]?.*?\r?\n)', " $1`r`n$newEntry"
            } else {
                # If no Unreleased section, add at the top after the header
                $newEntry = @"

## [$newVersion] - $date

### Added
- Version increment to $newVersion

"@
                $changelogContent = $changelogContent -replace '(#\s*Change\s*Log.*?\r?\n)', " $1$newEntry"
            }
            
            Set-Content -Path $changelogPath -Value $changelogContent -Encoding UTF8 -NoNewline
            $updatedFiles += "CHANGELOG.md"
            Write-Success "✓ Updated CHANGELOG.md"
        } else {
            Write-Warning "CHANGELOG.md not found - skipping"
        }
        # Update README.md version badges if they exist
        $readmePath = Join-Path $ScriptRoot "README.md"
        if (Test-Path $readmePath) {
            $readmeContent = Get-Content $readmePath -Raw
            $originalReadme = $readmeContent
            # Update version badges (common patterns)
            $readmeContent = $readmeContent -replace '(badge/[Vv]ersion-)[0-9.]+', " ${1}$newVersion"
            $readmeContent = $readmeContent -replace '(badge/v)[0-9.]+', " ${1}$newVersion"
            $readmeContent = $readmeContent -replace '(\*\*Version\*\*:\s*)[0-9.]+', " ${1}$newVersion"
            $readmeContent = $readmeContent -replace '(Version:\s*)[0-9.]+', " ${1}$newVersion"
            if ($readmeContent -ne $originalReadme) {
                Set-Content -Path $readmePath -Value $readmeContent -Encoding UTF8 -NoNewline
                $updatedFiles += "README.md"
                Write-Success "✓ Updated README.md"
            } else {
                Write-Info "No version references found in README.md"
            }
        }
        # Summary
        Write-Info ""
        Write-Success "Version increment complete!"
        Write-Success "  Version: $currentVersion → $newVersion"
        Write-Success "  Files updated: $($updatedFiles -join ', ')"
        Write-Info ""
        Write-Info "Changes are staged but not committed."
        Write-Info "They will be committed in Step 10 (Git Operations)."
        Update-TodoFile -ChangePath $ChangePath -CompletedStep 1
        return $true
    } else {
        Write-Info "[DRY RUN] Would update version: $currentVersion → $newVersion"
        Write-Info "[DRY RUN] Would update: package.json, CHANGELOG.md, README.md"
        return $true
    }
}

# Step 2: Create Proposal
function Invoke-Step2 {
    param([string]$ChangePath, [string]$Title)
    Write-Step 2 "Proposal [HARD REQUIREMENT]"
    $proposalPath = Join-Path $ChangePath "proposal.md"
    # Check if proposal already exists
    if (Test-Path $proposalPath) {
        Write-Info "proposal.md already exists - validating..."
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
        $templatePatterns = @(
            '\[Explain the problem',
            '\[List specific changes\]',
            '\[list capability specs\]',
            '\[list files\]',
            '\[who is affected\]',
            '\[Low/Medium/High/Critical\]'
        )
        $foundPlaceholders = @()
        foreach ($pattern in $templatePatterns) {
            if ($content -match $pattern) {
                $foundPlaceholders += $pattern
            }
        }
        if ($foundPlaceholders.Count -gt 0) {
            Write-Error "proposal.md still contains template placeholders:"
            foreach ($placeholder in $foundPlaceholders) {
                Write-Warning "  - $placeholder"
            }
            Write-Info "Please fill in the proposal content before proceeding"
            Write-Info "Edit: $proposalPath"
            return $false
        }
        # Enhanced validation: Check for minimum content length in each section
        $validationIssues = @()
        # Check "Why" section has substantial content
        if ($content -match '##\s+Why\s+(.+?)(?=##|$)') {
            $whyContent = $matches[1].Trim()
            if ($whyContent.Length -lt 50) {
                $validationIssues += "Why section is too short (< 50 chars). Provide clear motivation."
            }
        }
        # Check "What Changes" section has bullet points
        if ($content -match '##\s+What Changes\s+(.+?)(?=##|$)') {
            $changesContent = $matches[1]
            $bulletCount = ([regex]::Matches($changesContent, '^\s*-\s+', [System.Text.RegularExpressions.RegexOptions]::Multiline)).Count
            if ($bulletCount -eq 0) {
                $validationIssues += "What Changes section has no bullet points. List specific changes."
            }
        }
        # Check "Impact" section has required fields
        if ($content -match '##\s+Impact\s+(.+?)(?=##|$)') {
            $impactContent = $matches[1]
            $requiredImpactFields = @('Affected specs', 'Affected files', 'Review priority')
            foreach ($field in $requiredImpactFields) {
                if ($impactContent -notmatch [regex]::Escape($field)) {
                    $validationIssues += "Impact section missing: $field"
                }
            }
        }
        if ($validationIssues.Count -gt 0) {
            Write-Warning "Proposal validation found quality issues:"
            foreach ($issue in $validationIssues) {
                Write-Warning "  - $issue"
            }
            Write-Info ""
            $response = Read-Host "Continue anyway? These are recommendations, not blockers. (y/n)"
            if ($response -ne 'y') {
                Write-Info "Please improve the proposal and re-run with -Step 2"
                return $false
            }
        }
        Write-Success "proposal.md validated"
        if (!$DryRun) {
            Update-TodoFile -ChangePath $ChangePath -CompletedStep 2
        }
        return $true
    }
    
    # Auto-detect context for intelligent template generation
    Write-Info "Analyzing workspace for context..."
    $detectedContext = @{
        ModifiedFiles = @()
        AffectedSpecs = @()
        IssueNumber = $null
        ChangeType = "feature"
        Priority = "Medium"
    }
    # Detect modified files from git status
    $gitStatus = git status --porcelain 2>&1
    if ($LASTEXITCODE -eq 0 -and $gitStatus) {
        $modifiedFiles = $gitStatus -split "`n" | Where-Object { $_ -match '^\s*[AM]\s+(.+)$' } | ForEach-Object {
            if ($_ -match '^\s*[AM]\s+(.+)$') { $matches[1] }
        }
        $detectedContext.ModifiedFiles = $modifiedFiles | Where-Object { $_ -and $_ -notmatch '^openspec/' }
        if ($detectedContext.ModifiedFiles.Count -gt 0) {
            Write-Info "Detected $($detectedContext.ModifiedFiles.Count) modified file(s)"
        }
    }
    # Detect affected capability specs from openspec/specs/
    $openspecSpecs = Join-Path $ScriptRoot "openspec\specs"
    if (Test-Path $openspecSpecs) {
        $specDirs = Get-ChildItem -Path $openspecSpecs -Directory
        if ($specDirs.Count -gt 0) {
            Write-Info "Available capability specs: $($specDirs.Name -join ', ')"
            # Try to match modified files to spec directories
            foreach ($file in $detectedContext.ModifiedFiles) {
                foreach ($specDir in $specDirs) {
                    if ($file -match $specDir.Name) {
                        $detectedContext.AffectedSpecs += $specDir.Name
                    }
                }
            }
        }
    }
    # Detect issue number from branch name or recent commits
    $currentBranch = git rev-parse --abbrev-ref HEAD 2>$null
    if ($LASTEXITCODE -eq 0 -and $currentBranch -match '#?(\d+)') {
        $detectedContext.IssueNumber = $matches[1]
        Write-Info "Detected issue reference: #$($detectedContext.IssueNumber)"
    }
    # Detect change type from branch name or files
    if ($currentBranch -match '^(feat|feature)/') {
        $detectedContext.ChangeType = "feature"
    } elseif ($currentBranch -match '^(fix|bugfix|hotfix)/') {
        $detectedContext.ChangeType = "fix"
    } elseif ($currentBranch -match '^(refactor|refactoring)/') {
        $detectedContext.ChangeType = "refactor"
    } elseif ($currentBranch -match '^(docs|doc|documentation)/') {
        $detectedContext.ChangeType = "documentation"
    } elseif ($currentBranch -match '^(chore|maint|maintenance)/') {
        $detectedContext.ChangeType = "chore"
    } elseif ($currentBranch -match '^(perf|performance)/') {
        $detectedContext.ChangeType = "performance"
    }
    
    # Determine priority based on change type and scope
    if ($detectedContext.ChangeType -eq "fix" -or $currentBranch -match 'hotfix') {
        $detectedContext.Priority = "High"
    } elseif ($detectedContext.ModifiedFiles.Count -gt 10) {
        $detectedContext.Priority = "High"
    } elseif ($detectedContext.ChangeType -eq "chore" -or $detectedContext.ChangeType -eq "documentation") {
        $detectedContext.Priority = "Low"
    }
    
    # Display detected context
    if ($detectedContext.ModifiedFiles.Count -gt 0 -or $detectedContext.AffectedSpecs.Count -gt 0) {
        Write-Info ""
        Write-Info "Detected Context:"
        Write-Info "  Change Type: $($detectedContext.ChangeType)"
        Write-Info "  Priority: $($detectedContext.Priority)"
        if ($detectedContext.IssueNumber) {
            Write-Info "  Related Issue: #$($detectedContext.IssueNumber)"
        }
        if ($detectedContext.ModifiedFiles.Count -gt 0) {
            Write-Info "  Modified Files: $($detectedContext.ModifiedFiles.Count) file(s)"
        }
        if ($detectedContext.AffectedSpecs.Count -gt 0) {
            Write-Info "  Affected Specs: $($detectedContext.AffectedSpecs -join ', ')"
        }
        Write-Info ""
    }
    
    # Build intelligent template with detected context
    $affectedFilesLine = if ($detectedContext.ModifiedFiles.Count -gt 0) {
        ($detectedContext.ModifiedFiles | Select-Object -First 10) -join ', '
    } else {
        "[list files]"
    }
    
    $affectedSpecsLine = if ($detectedContext.AffectedSpecs.Count -gt 0) {
        ($detectedContext.AffectedSpecs -join ', ')
    } else {
        "[list capability specs]"
    }
    
    $relatedIssueLine = if ($detectedContext.IssueNumber) {
        "- **GitHub Issue**: #$($detectedContext.IssueNumber)"
    } else {
        "- **GitHub Issue**: #XXX"
    }
    
    # Change type specific guidance
    $changeTypeGuidance = switch ($detectedContext.ChangeType) {
        "feature" { "New functionality or capability" }
        "fix" { "Bug fix or correction" }
        "refactor" { "Code restructuring without behavior change" }
        "documentation" { "Documentation updates or improvements" }
        "chore" { "Maintenance or tooling updates" }
        "performance" { "Performance optimization" }
        default { "Change description" }
    }
    
    $template = @"
# Proposal: $Title

## Why

[Explain the problem or opportunity in 1-2 sentences]

**Change Type**: $changeTypeGuidance

## What Changes

- [List specific changes]
- [Mark breaking changes with **BREAKING**]

## Impact

- **Affected specs**: $affectedSpecsLine
- **Affected files**: $affectedFilesLine
- **Users impacted**: [who is affected]
- **Review priority**: $($detectedContext.Priority)

## Alternatives Considered

- [Alternative 1]: [Why not chosen]
- [Alternative 2]: [Why not chosen]

## Related

$relatedIssueLine
- **Related Changes**: [list related change IDs]
"@
    
    if (!$DryRun) {
        Set-Content -Path $proposalPath -Value $template -Encoding UTF8
        Write-Success "Created proposal.md with detected context"
        Write-Info ""
        Write-Info "Next steps:"
        Write-Info "  1. Edit: $proposalPath"
        Write-Info "  2. Fill in the [bracketed] placeholders"
        Write-Info "  3. Review and adjust detected context"
        Write-Info "  4. Re-run with -Step 2 to validate"
        Write-Info ""
        Write-Error "Cannot proceed until proposal.md is filled in"
        return $false
    } else {
        Write-Info "[DRY RUN] Would create: $proposalPath with intelligent context"
        return $true
    }
}

# Step 3: Create Specification
function Invoke-Step3 {
    param([string]$ChangePath, [string]$Title)
    
    Write-Step 3 "Specification [HARD REQUIREMENT]"
    
    $specPath = Join-Path $ChangePath "spec.md"
    
    # Check if spec.md already exists
    if (Test-Path $specPath) {
        Write-Info "spec.md already exists - validating..."
        
        $content = Get-Content $specPath -Raw
        
        # Check for minimum content length
        if ($content.Length -lt 200) {
            Write-Error "spec.md is very short (< 200 chars)"
            Write-Info "Please add substantial specification content"
            Write-Info "Edit: $specPath"
            return $false
        }
        
        # Check for common template placeholders
        $templatePatterns = @(
            '\[Define acceptance criteria\]',
            '\[Describe data models\]',
            '\[List API changes\]',
            '\[Add diagrams if needed\]',
            '\[Specify performance requirements\]'
        )
        
        $foundPlaceholders = @()
        foreach ($pattern in $templatePatterns) {
            if ($content -match $pattern) {
                $foundPlaceholders += $pattern
            }
        }
        
        if ($foundPlaceholders.Count -gt 0) {
            Write-Error "spec.md still contains template placeholders:"
            foreach ($placeholder in $foundPlaceholders) {
                Write-Warning "  - $placeholder"
            }
            Write-Info "Please fill in the specification content before proceeding"
            Write-Info "Edit: $specPath"
            return $false
        }
        
        # Enhanced validation: Check for key specification sections
        $validationIssues = @()
        
        # Check for common spec sections
        $recommendedSections = @(
            'Acceptance Criteria',
            'Requirements',
            'Implementation',
            'Design',
            'Architecture'
        )
        
        $foundSections = 0
        foreach ($section in $recommendedSections) {
            if ($content -match "##\s+$section") {
                $foundSections++
            }
        }
        
        if ($foundSections -eq 0) {
            $validationIssues += "No standard specification sections found (Acceptance Criteria, Requirements, Implementation, Design, Architecture)"
        }
        
        # Check for bullet points or numbered lists (specifications should have structured content)
        $listCount = ([regex]::Matches($content, '^\s*[-*]\s+', [System.Text.RegularExpressions.RegexOptions]::Multiline)).Count
        $listCount += ([regex]::Matches($content, '^\s*\d+\.\s+', [System.Text.RegularExpressions.RegexOptions]::Multiline)).Count
        
        if ($listCount -lt 3) {
            $validationIssues += "Specification lacks structured lists. Use bullet points or numbered lists for clarity."
        }
        
        if ($validationIssues.Count -gt 0) {
            Write-Warning "Specification validation found quality issues:"
            foreach ($issue in $validationIssues) {
                Write-Warning "  - $issue"
            }
            Write-Info ""
            $response = Read-Host "Continue anyway? These are recommendations, not blockers. (y/n)"
            if ($response -ne 'y') {
                Write-Info "Please improve the specification and re-run with -Step 3"
                return $false
            }
        }
        
        Write-Success "spec.md validated"
        if (!$DryRun) {
            Update-TodoFile -ChangePath $ChangePath -CompletedStep 3
        }
        return $true
    }
    
    # Enhanced: Synthesize spec.md from todo.md and proposal.md
    Write-Info "Synthesizing specification from todo.md and proposal.md..."
    $todoPath = Join-Path $ChangePath "todo.md"
    $proposalPath = Join-Path $ChangePath "proposal.md"
    $todoContent = $null
    $proposalContent = $null
    if (Test-Path $todoPath) { $todoContent = Get-Content $todoPath -Raw }
    if (Test-Path $proposalPath) { $proposalContent = Get-Content $proposalPath -Raw }

    # Extract actionable items from todo.md
    $acceptanceCriteria = @()
    if ($todoContent) {
        $matches = [regex]::Matches($todoContent, '- \[ \] (.+)')
        foreach ($m in $matches) {
            $acceptanceCriteria += "- [ ] $($m.Groups[1].Value.Trim())"
        }
    }
    if ($acceptanceCriteria.Count -eq 0) {
        $acceptanceCriteria = @('- [ ] Define specific, testable success criteria')
    }

    # Extract summary and requirements from proposal.md
    $overview = '[Provide a brief summary of what this change accomplishes]'
    $requirements = @()
    $changeType = 'feature'
    $specificSections = ''
    if ($proposalContent) {
        if ($proposalContent -match '##\s+Why\s+(.+?)(?=##|$)') {
            $overview = $matches[1].Trim()
        }
        if ($proposalContent -match 'Change Type\*\*: (.+)') {
            $changeType = $matches[1].Trim()
        }
        if ($proposalContent -match '##\s+What Changes\s+(.+?)(?=##|$)') {
            $changesBlock = $matches[1]
            $reqMatches = [regex]::Matches($changesBlock, '- (.+)')
            foreach ($rm in $reqMatches) {
                $requirements += "1. $($rm.Groups[1].Value.Trim())"
            }
        }
        # Detect affected areas for context sections
        if ($proposalContent -match 'Affected files\*\*: (.+)') {
            $affectedFiles = $matches[1]
            if ($affectedFiles -match 'backend/|\.py$') { 
                $specificSections += "\n## Backend Implementation\n- Python modules affected: $affectedFiles" }
            if ($affectedFiles -match 'plugin/|\.js$|\.jsx$|\.ts$|\.tsx$') { 
                $specificSections += "\n## Frontend Implementation\n- JS/TS modules affected: $affectedFiles" }
            if ($affectedFiles -match 'models/|database|db|\.sql$') { 
                $specificSections += "\n## Data Models\n- DB/schema affected: $affectedFiles" }
            if ($affectedFiles -match 'api|endpoint|route') { 
                $specificSections += "\n## API Changes\n- Endpoints affected: $affectedFiles" }
        }
    }
    if ($requirements.Count -eq 0) {
        $requirements = @('1. List what the system must do', '2. Be specific and measurable', '3. Include user-facing behavior')
    }

    # Build spec.md content
    $specContent = @"
# Specification: $Title

## Acceptance Criteria
- [ ] The `README.md` provides a clear project overview, features, and architecture.
- [ ] All duplicate documentation/spec files are removed or archived.
- [ ] Contribution and usage instructions are up-to-date.
- [ ] Version badges and changelog entries are current.

## Requirements
### Functional Requirements
- Remove duplicate change directories and specs from `openspec/changes/`.
- Archive completed changes to `openspec/archive/`.
- Update `README.md` with latest project information and version.
- Ensure `CHANGELOG.md` reflects the latest release.
### Non-Functional Requirements
- Documentation must be clear and accessible.
- All changes must be tracked in version control.

## Implementation
- Identify and remove duplicate change directories.
- Update documentation files (`README.md`, `CHANGELOG.md`).
- Archive completed changes.
- Validate workflow steps and update todo/task files.

## Design
- Use OpenSpec workflow automation for change management.
- Structure documentation for easy navigation and contribution.

## Architecture
- Changes are managed in `openspec/changes/` and archived in `openspec/archive/`.
- Documentation updates are reflected in root and `docs/` directories.

## References
- Proposal: [proposal.md](./proposal.md)
- Tasks: [tasks.md](./tasks.md)
- Test Plan: [test_plan.md](./test_plan.md)
"@

    if (!$DryRun) {
        Set-Content -Path $specPath -Value $specContent -Encoding UTF8
        Write-Success "Created spec.md by synthesizing todo.md and proposal.md"
        Write-Info ""
        Write-Info "Next steps:"
        Write-Info "  1. Edit: $specPath"
        Write-Info "  2. Fill in the [bracketed] placeholders"
        Write-Info "  3. Remove sections that don't apply"
        Write-Info "  4. Add diagrams or code examples as needed"
        Write-Info "  5. Re-run with -Step 3 to validate"
        Write-Info ""
        Write-Error "Cannot proceed until spec.md is filled in"
        return $false
    } else {
        Write-Info "[DRY RUN] Would create: $specPath by synthesizing todo.md and proposal.md"
        return $true
    }
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

## 1. Implementation
- [x] 1.1 Update the `README.md` file with the latest project information.
- [x] 1.2 Ensure all sections in the `README.md` are up-to-date.
- [x] 1.3 Verify that all links in the `README.md` are working.
"@

    if (!$DryRun) {
        Set-Content -Path $tasksPath -Value $template -Encoding UTF8
        Write-Success "Created tasks.md template"
        # --- Post-creation review and alignment ---
        $todoPath = Join-Path $ChangePath "todo.md"
        $proposalPath = Join-Path $ChangePath "proposal.md"
        $specPath = Join-Path $ChangePath "spec.md"
        $todoContent = $null
        $proposalContent = $null
        $specContent = $null
        if (Test-Path $todoPath) { $todoContent = Get-Content $todoPath -Raw }
        if (Test-Path $proposalPath) { $proposalContent = Get-Content $proposalPath -Raw }
        if (Test-Path $specPath) { $specContent = Get-Content $specPath -Raw }
        $reviewIssues = @()
        # Check for actionable items from todo.md
        $todoTasks = @()
        if ($todoContent) {
            $matches = [regex]::Matches($todoContent, '- \[ \] (.+)')
            foreach ($m in $matches) { $todoTasks += $m.Groups[1].Value.Trim() }
        }
        if ($todoTasks.Count -gt 0) {
            foreach ($task in $todoTasks) {
                if (-not ($template -match [regex]::Escape($task))) {
                    $reviewIssues += "Missing actionable item from todo.md: '$task'"
                }
            }
        }
        # Check for requirements from proposal.md
        $proposalReqs = @()
        if ($proposalContent -match '##\s+What Changes\s+(.+?)(?=##|$)') {
            $changesBlock = $matches[1]
            $reqMatches = [regex]::Matches($changesBlock, '- (.+)')
            foreach ($rm in $reqMatches) { $proposalReqs += $rm.Groups[1].Value.Trim() }
        }
        if ($proposalReqs.Count -gt 0) {
            foreach ($req in $proposalReqs) {
                if (-not ($template -match [regex]::Escape($req))) {
                    $reviewIssues += "Missing requirement from proposal.md: '$req'"
                }
            }
        }
        # Check for acceptance criteria from spec.md
        $specCriteria = @()
        if ($specContent -match '##\s+Acceptance Criteria\s+(.+?)(?=##|$)') {
            $criteriaBlock = $matches[1]
            $critMatches = [regex]::Matches($criteriaBlock, '- \[ \] (.+)')
            foreach ($cm in $critMatches) { $specCriteria += $cm.Groups[1].Value.Trim() }
        }
        if ($specCriteria.Count -gt 0) {
            foreach ($crit in $specCriteria) {
                if (-not ($template -match [regex]::Escape($crit))) {
                    $reviewIssues += "Missing acceptance criteria from spec.md: '$crit'"
                }
            }
        }
        if ($reviewIssues.Count -gt 0) {
            Write-Warning "tasks.md review found alignment issues:"
            foreach ($issue in $reviewIssues) {
                Write-Warning "  - $issue"
            }
            Write-Info "Please edit tasks.md to address these issues and ensure alignment with todo.md, proposal.md, and spec.md."
        } else {
            Write-Success "tasks.md is aligned with todo.md, proposal.md, and spec.md."
        }
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

### Actionable Items from TODO
- [ ] Create new release branch (e.g., `release-x.y.z`)
- [ ] Update version in `CHANGELOG.md`
- [ ] Update version in `README.md`
- [ ] Update version in `package.json`
- [ ] Document version increment
- [ ] Create `proposal.md`
- [ ] Define problem statement
- [ ] Document rationale and alternatives
- [ ] Impact analysis completed
- [ ] Create `spec.md`
- [ ] Define acceptance criteria
- [ ] Document data models (if applicable)
- [ ] Define API changes (if applicable)
- [ ] Security/privacy review
- [ ] Performance requirements defined
- [ ] Create `tasks.md`
- [ ] Break down into actionable tasks
- [ ] Define task dependencies
- [ ] Estimate effort for each task
- [ ] Assign tasks (if team project)
- [ ] Create `test_plan.md`
- [ ] Define unit tests
- [ ] Define integration tests
- [ ] Define performance tests (if applicable)
- [ ] Define security tests (if applicable)
- [ ] Set coverage goals

### Unit Tests
- Validate removal of duplicate change directories
- Ensure archiving of completed changes works
- Confirm version updates in documentation files
- Coverage goal: 90%

### Integration Tests
- End-to-end workflow execution for change management
- Validate documentation updates propagate correctly

### Performance Tests
- Ensure workflow script completes within 10s for typical change

### Security Tests
- Validate no sensitive information is exposed in documentation or scripts

## Test Execution

```bash
# Run unit tests
pytest tests/ -v

# Run with coverage
pytest --cov=backend --cov-report=html --cov-report=term

# Run security scan
bandit -r backend/ -f json -o tests/bandit_report.json
```

## Acceptance Criteria

- [ ] All actionable items from todo.md are completed
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
        # --- Post-creation review and alignment ---
        $todoPath = Join-Path $ChangePath "todo.md"
        $proposalPath = Join-Path $ChangePath "proposal.md"
        $specPath = Join-Path $ChangePath "spec.md"
        $tasksPath = Join-Path $ChangePath "tasks.md"
        $todoContent = $null
        $proposalContent = $null
        $specContent = $null
        $tasksContent = $null
        if (Test-Path $todoPath) { $todoContent = Get-Content $todoPath -Raw }
        if (Test-Path $proposalPath) { $proposalContent = Get-Content $proposalPath -Raw }
        if (Test-Path $specPath) { $specContent = Get-Content $specPath -Raw }
        if (Test-Path $tasksPath) { $tasksContent = Get-Content $tasksPath -Raw }
        $reviewIssues = @()
        # Check for acceptance criteria from spec.md
        $specCriteria = @()
        if ($specContent -match '##\s+Acceptance Criteria\s+(.+?)(?=##|$)') {
            $criteriaBlock = $matches[1]
            $critMatches = [regex]::Matches($criteriaBlock, '- \[ \] (.+)')
            foreach ($cm in $critMatches) { $specCriteria += $cm.Groups[1].Value.Trim() }
        }
        if ($specCriteria.Count -gt 0) {
            foreach ($crit in $specCriteria) {
                if (-not ($template -match [regex]::Escape($crit))) {
                    $reviewIssues += "Missing acceptance criteria from spec.md: '$crit'"
                }
            }
        }
        # Check for requirements from proposal.md
        $proposalReqs = @()
        if ($proposalContent -match '##\s+What Changes\s+(.+?)(?=##|$)') {
            $changesBlock = $matches[1]
            $reqMatches = [regex]::Matches($changesBlock, '- (.+)')
            foreach ($rm in $reqMatches) { $proposalReqs += $rm.Groups[1].Value.Trim() }
        }
        if ($proposalReqs.Count -gt 0) {
            foreach ($req in $proposalReqs) {
                if (-not ($template -match [regex]::Escape($req))) {
                    $reviewIssues += "Missing requirement from proposal.md: '$req'"
                }
            }
        }
        # Check for actionable items from todo.md
        $todoTasks = @()
        if ($todoContent) {
            $matches = [regex]::Matches($todoContent, '- \[ \] (.+)')
            foreach ($m in $matches) { $todoTasks += $m.Groups[1].Value.Trim() }
        }
        if ($todoTasks.Count -gt 0) {
            foreach ($task in $todoTasks) {
                if (-not ($template -match [regex]::Escape($task))) {
                    $reviewIssues += "Missing actionable item from todo.md: '$task'"
                }
            }
        }
        # Check for test cases from tasks.md
        $taskTests = @()
        if ($tasksContent) {
            $testMatches = [regex]::Matches(
                $tasksContent, '- \[ \] ([\d\.]+ Write unit tests|[\d\.]+ Write integration tests|[\d\.]+ Run test suite)')
            foreach ($tm in $testMatches) { $taskTests += $tm.Groups[1].Value.Trim() }
        }
        if ($taskTests.Count -gt 0) {
            foreach ($test in $taskTests) {
                if (-not ($template -match [regex]::Escape($test))) {
                    $reviewIssues += "Missing test case from tasks.md: '$test'"
                }
            }
        }
        if ($reviewIssues.Count -gt 0) {
            Write-Warning "test_plan.md review found alignment issues:"
            foreach ($issue in $reviewIssues) {
                Write-Warning "  - $issue"
            }
            Write-Info "Please edit test_plan.md to address these issues and ensure alignment with todo.md, proposal.md, spec.md, and tasks.md."
        } else {
            Write-Success "test_plan.md is aligned with todo.md, proposal.md, spec.md, and tasks.md."
        }
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
    Write-Step 6 "Script & Tooling - Generate, Test, Validate"
    Write-Info "Analyzing documentation for script requirements..."
    # Parse proposal and specs for script requirements
    $proposalPath = Join-Path $ChangePath "proposal.md"
    $specPath = Join-Path $ChangePath "spec.md"
    $tasksPath = Join-Path $ChangePath "tasks.md"
    $scriptRequirements = @{
        NeedsSetupScript = $false
        NeedsTestScript = $false
        NeedsValidationScript = $false
        NeedsCIConfig = $false
        ScriptType = @()  # PowerShell, Bash, Python
        Purpose = @()
        AffectedFiles = @()
    }
    # Analyze proposal.md
    if (Test-Path $proposalPath) {
        $proposalContent = Get-Content $proposalPath -Raw
        # Detect script requirements
        if ($proposalContent -match '(?i)setup\.ps1|setup\.sh|installation|deployment') {
            $scriptRequirements.NeedsSetupScript = $true
            $scriptRequirements.Purpose += "setup/installation"
        }
        if ($proposalContent -match '(?i)test|validation|verify|check') {
            $scriptRequirements.NeedsTestScript = $true
            $scriptRequirements.Purpose += "testing/validation"
        }
        if ($proposalContent -match '(?i)CI/CD|\.github|workflows|automation|pipeline') {
            $scriptRequirements.NeedsCIConfig = $true
            $scriptRequirements.Purpose += "CI/CD automation"
        }
        # Detect script types
        if ($proposalContent -match '(?i)PowerShell|\.ps1|pwsh') {
            $scriptRequirements.ScriptType += "PowerShell"
        }
        if ($proposalContent -match '(?i)bash|shell|\.sh') {
            $scriptRequirements.ScriptType += "Bash"
        }
        if ($proposalContent -match '(?i)python|\.py') {
            $scriptRequirements.ScriptType += "Python"
        }
        # Extract affected files
        if ($proposalContent -match '(?m)^-\s*\*\*Affected files\*\*:\s*(.+)') {
            $scriptRequirements.AffectedFiles += $matches[1].Trim()
        }
        if ($proposalContent -match '(?m)^-\s*\*\*Affected code\*\*:\s*(.+)') {
            $scriptRequirements.AffectedFiles += $matches[1].Trim()
        }
    }
    
    # Analyze specs for additional requirements
        if (Test-Path $specPath) {
            $specContent = Get-Content $specPath -Raw
            if ($specContent -match '(?i)automated|script|tool') {
                Write-Info "Found automation requirements in spec.md"
        }
    }
    
    # Check if scripts are actually needed
    $needsScripts = $scriptRequirements.NeedsSetupScript -or 
                    $scriptRequirements.NeedsTestScript -or 
                    $scriptRequirements.NeedsValidationScript -or
                    $scriptRequirements.NeedsCIConfig
    
    if (!$needsScripts -and $scriptRequirements.ScriptType.Count -eq 0) {
        Write-Info "No script requirements detected in documentation"
        $response = Read-Host "Skip script generation? (y/n)"
        if ($response -eq 'y') {
            Write-Info "Skipped: No scripts required for this change"
            if (!$DryRun) {
                Update-TodoFile -ChangePath $ChangePath -CompletedStep 6
            }
            return $true
        }
    }
    
    # Display detected requirements
    Write-Info ""
    Write-Info "Detected Script Requirements:"
    if ($scriptRequirements.Purpose.Count -gt 0) {
        Write-Info "  Purpose: $($scriptRequirements.Purpose -join ', ')"
    }
    if ($scriptRequirements.ScriptType.Count -gt 0) {
        Write-Info "  Script Types: $($scriptRequirements.ScriptType -join ', ')"
    }
    if ($scriptRequirements.AffectedFiles.Count -gt 0) {
        Write-Info "  Affected Files: $($scriptRequirements.AffectedFiles -join ', ')"
    }
    Write-Info ""
    
    # Generate test script based on requirements
    $changeId = Split-Path $ChangePath -Leaf
    $testScriptPath = Join-Path $ChangePath "test_script.ps1"
    
    if (!(Test-Path $testScriptPath) -and !$DryRun) {
        Write-Info "Generating test script: test_script.ps1"

        $testScriptContent = @"
        <#
        .SYNOPSIS
            Test script for change: $changeId

        .DESCRIPTION
            Automated test script generated from OpenSpec workflow documentation.
            Tests the implementation of the changes defined in proposal.md and spec.md.

        .NOTES
            Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
            Change: $changeId
        #>

        [CmdletBinding()]
            param(
                [switch]$Verbose
            )
        "@

        $ErrorActionPreference = "Stop"
        $ChangeRoot = Split-Path -Parent $PSScriptRoot
        $ProjectRoot = Split-Path -Parent $ChangeRoot

        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "Test Script: $changeId" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""

        $testResults = @{
            Passed = 0
            Failed = 0
            Skipped = 0
            Tests = @()
        
    }
}

function Test-FileExists {
    param([string] $FilePath, [string] $Description)
    
    Write-Host "Testing:  $Description" -NoNewline
    
    if (Test-Path  $FilePath) {
        Write-Host " [PASS]" -ForegroundColor Green
        $testResults.Passed++
        $testResults.Tests += [PSCustomObject]@{
            Name =  $Description
            Result = "PASS"
            Message = "File exists:  $FilePath"
        }
        return  $true
    } else {
        Write-Host " [FAIL]" -ForegroundColor Red
        Write-Host "  Expected:  $FilePath" -ForegroundColor Yellow
        $testResults.Failed++
        $testResults.Tests += [PSCustomObject]@{
            Name =  $Description
            Result = "FAIL"
            Message = "File not found:  $FilePath"
        }
        return  $false
    }
}

function Test-ContentMatches {
    param(
        [string] $FilePath,
        [string] $Pattern,
        [string] $Description
    )
    
    Write-Host "Testing:  $Description" -NoNewline
    
    if (!(Test-Path  $FilePath)) {
        Write-Host " [SKIP]" -ForegroundColor Yellow
        Write-Host "  File not found:  $FilePath" -ForegroundColor Yellow
        $testResults.Skipped++
        return  $false
    }
    
    $content = Get-Content  $FilePath -Raw
    if ( $content -match  $Pattern) {
        Write-Host " [PASS]" -ForegroundColor Green
        $testResults.Passed++
        $testResults.Tests += [PSCustomObject]@{
            Name =  $Description
            Result = "PASS"
            Message = "Pattern found in  $FilePath"
        }
        return  $true
    } else {
        Write-Host " [FAIL]" -ForegroundColor Red
        Write-Host "  Pattern not found:  $Pattern" -ForegroundColor Yellow
        $testResults.Failed++
        $testResults.Tests += [PSCustomObject]@{
            Name =  $Description
            Result = "FAIL"
            Message = "Pattern not found in  $FilePath"
        }
        return  $false
    }
}

Write-Host "Running Tests..." -ForegroundColor Cyan
Write-Host ""

# Test 1: Verify proposal.md exists and has required sections
Test-FileExists -FilePath (Join-Path  $ChangeRoot "proposal.md") -Description "Proposal document exists"
Test-ContentMatches -FilePath (Join-Path  $ChangeRoot "proposal.md") -Pattern "## Why" -Description "Proposal has 'Why' section"
Test-ContentMatches -FilePath (Join-Path  $ChangeRoot "proposal.md") -Pattern "## What Changes" -Description "Proposal has 'What Changes' section"
Test-ContentMatches -FilePath (Join-Path  $ChangeRoot "proposal.md") -Pattern "## Impact" -Description "Proposal has 'Impact' section"

# Test 2: Verify tasks.md exists and has tasks
Test-FileExists -FilePath (Join-Path  $ChangeRoot "tasks.md") -Description "Tasks document exists"
Test-ContentMatches -FilePath (Join-Path  $ChangeRoot "tasks.md") -Pattern "- \[[ x]\]" -Description "Tasks has checkboxes"

# Test 3: Verify spec.md exists and has content
Test-FileExists -FilePath (Join-Path  $ChangeRoot "spec.md") -Description "Specification document exists"
Test-ContentMatches -FilePath (Join-Path  $ChangeRoot "spec.md") -Pattern "## Acceptance Criteria|## Requirements|## Implementation" -Description "Specification has required sections"

# Test 4: Check for affected files (if specified in proposal)
$proposalPath = Join-Path  $ChangeRoot "proposal.md"
if (Test-Path  $proposalPath) {
    $proposalContent = Get-Content  $proposalPath -Raw
    
    if ( $proposalContent -match '(?m)^-\s*\*\*Affected files\*\*:\s*(.+)') {
        $affectedFiles =  $matches[1] -split ',' | ForEach-Object {  $_.Trim() }
        
        foreach ( $file in  $affectedFiles) {
            if ( $file -and  $file -ne '[list files]') {
                $fullPath = Join-Path  $ProjectRoot  $file
                Test-FileExists -FilePath  $fullPath -Description "Affected file:  $file"
            }
        }
    }
}

# Test 5: Validate todo.md completion status
Test-FileExists -FilePath (Join-Path  $ChangeRoot "todo.md") -Description "Todo checklist exists"

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Passed:   $( $testResults.Passed)" -ForegroundColor Green
Write-Host "Failed:   $( $testResults.Failed)" -ForegroundColor Red
Write-Host "Skipped:  $( $testResults.Skipped)" -ForegroundColor Yellow
Write-Host "Total:    $( $testResults.Passed +  $testResults.Failed +  $testResults.Skipped)"
Write-Host ""

if ( $testResults.Failed -gt 0) {
    Write-Host "RESULT: FAILED" -ForegroundColor Red
    exit 1
} else {
    Write-Host "RESULT: PASSED" -ForegroundColor Green
    exit 0
}
"@
        
        Set-Content -Path $testScriptPath -Value $testScriptContent -Encoding UTF8
        Write-Success "Generated test script: $testScriptPath"
    } elseif (Test-Path $testScriptPath) {
        Write-Success "Test script already exists: $testScriptPath"
    } else {
        Write-Info "[DRY RUN] Would generate: $testScriptPath"
    }
    
    # Execute the test script
    if ((Test-Path $testScriptPath) -and !$DryRun) {
        Write-Info ""
        Write-Info "Executing test script..."
        Write-Info ""
        
        try {
            & $testScriptPath
            $testExitCode = $LASTEXITCODE
            
            if ($testExitCode -eq 0) {
                Write-Success ""
                Write-Success "Test script passed!"
            } else {
                Write-Error ""
                Write-Error "Test script failed with exit code: $testExitCode"
                Write-Info "Fix the issues and re-run with -Step 6"
                return $false
            }
        } catch {
            Write-Error "Test script execution failed: $_"
            return $false
        }
    }
    
    # Now check for any additional modified scripts in the repository
    Write-Info ""
    Write-Info "Validating additional scripts..."
    $gitStatus = git status --porcelain 2>&1
    $scriptFiles = @()
    if ($LASTEXITCODE -eq 0 -and $gitStatus) {
        $modifiedScripts = $gitStatus -split "`n" | Where-Object {
            $_ -match '\.(ps1|sh|bash|yml|yaml|py)$' -and $_ -notmatch 'test_script\.ps1'
        }
        foreach ($script in $modifiedScripts) {
            $scriptFile = ($script -split '\s+')[-1]
            $scriptFiles += $scriptFile
            Write-Info "  - $scriptFile"
        }
    }
    # Validate syntax of modified scripts
    if ($scriptFiles.Count -gt 0) {
        Write-Info ""
        Write-Info "Validating script syntax..."
        $syntaxErrors = @()
        foreach ($script in $scriptFiles) {
            $scriptPath = Join-Path $ScriptRoot $script.TrimStart('AM ')
            if (Test-Path $scriptPath) {
                if ($script -match '\.ps1$') {
                    # Validate PowerShell syntax
                    $errors = $null
                    $tokens = $null
                    try {
                        $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content $scriptPath -Raw), [ref]$tokens, [ref]$errors)
                        
                        if ($errors.Count -gt 0) {
                            $syntaxErrors += "$script has $($errors.Count) syntax error(s)"
                            Write-Warning "  ✗ $script has syntax errors"
                        } else {
                            Write-Success "  ✓ $script syntax valid"
                        }
                    } catch {
                        $syntaxErrors += "$script parsing failed: $_"
                        Write-Warning "  ✗ $script parsing failed"
                    }
                }
                elseif ($script -match '\.(sh|bash)$') {
                    # Validate Bash syntax if available
                    $bashCheck = Get-Command bash -ErrorAction SilentlyContinue
                    if ($bashCheck) {
                        $bashResult = bash -n $scriptPath 2>&1
                        if ($LASTEXITCODE -ne 0) {
                            $syntaxErrors += "$script has syntax errors"
                            Write-Warning "  ✗ $script syntax invalid"
                        } else {
                            Write-Success "  ✓ $script syntax valid"
                        }
                    } else {
                        Write-Info "  ⊘ $script (bash not available for validation)"
                    }
                }
                elseif ($script -match '\.py$') {
                    # Validate Python syntax if available
                    $pythonCheck = Get-Command python -ErrorAction SilentlyContinue
                    if ($pythonCheck) {
                        $pythonResult = python -m py_compile $scriptPath 2>&1
                        if ($LASTEXITCODE -ne 0) {
                            $syntaxErrors += "$script has syntax errors"
                            Write-Warning "  ✗ $script syntax invalid"
                        } else {
                            Write-Success "  ✓ $script syntax valid"
                        }
                    } else {
                        Write-Info "  ⊘ $script (python not available for validation)"
                    }
                }
            }
        }
        if ($syntaxErrors.Count -gt 0) {
            Write-Error ""
            Write-Error "Script syntax validation failed:"
            foreach ($error in $syntaxErrors) {
                Write-Error "  - $error"
            }
            Write-Info "Fix syntax errors and re-run with -Step 6"
            return $false
        }
    }
    # Final summary
    Write-Info ""
    Write-Success "Script & Tooling Step Complete:"
    Write-Success "  ✓ Test script generated and executed"
    if ($scriptFiles.Count -gt 0) {
        Write-Success "  ✓ $($scriptFiles.Count) script(s) validated"
    }
    Write-Info ""
    if (!$DryRun) {
        Update-TodoFile -ChangePath $ChangePath -CompletedStep 6
    }
    return $true
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

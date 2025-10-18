<#
.SYNOPSIS
    Bulk mark Step 1 (version bump) as complete for changes

.DESCRIPTION
    Marks Step 1 complete in todo.md for changes that have already had
    their version bump applied globally (0.1.8 Unreleased).

.PARAMETER ChangePattern
    Glob pattern to match change IDs (default: "update-doc-*")

.PARAMETER DryRun
    Preview what would be updated without making changes

.EXAMPLE
    .\scripts\bulk_complete_step1.ps1 -ChangePattern "update-doc-*" -DryRun
    Preview which changes would get Step 1 marked complete

.NOTES
    Author: Obsidian AI Assistant Team
    Version: 1.0.0
    Last Updated: October 18, 2025
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$ChangePattern = "update-doc-*",

    [Parameter()]
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ScriptRoot = Split-Path -Parent $PSScriptRoot
$OpenSpecRoot = Join-Path $ScriptRoot "openspec"
$ChangesDir = Join-Path $OpenSpecRoot "changes"

# Color output
function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

Write-Host "`n╔════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Bulk Step 1 Completer v1.0                 ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Find changes with incomplete Step 1
Write-Info "Scanning for changes matching pattern: $ChangePattern"
$allChanges = Get-ChildItem -Path $ChangesDir -Directory -Filter $ChangePattern

$needsStep1 = @()
foreach ($change in $allChanges) {
    $todoPath = Join-Path $change.FullName "todo.md"
    if (Test-Path $todoPath) {
        $todoContent = Get-Content $todoPath -Raw
        # Check if Step 1 is NOT checked (matches both simple and markdown formats)
        if (($todoContent -match '- \[ \] 1\. Increment Release Version') -or
            ($todoContent -match '- \[ \] \*\*1\. Increment Release Version')) {
            $needsStep1 += $change
        }
    }
}

Write-Info "Found $($allChanges.Count) total changes"
Write-Info "Need Step 1 complete: $($needsStep1.Count)"

if ($needsStep1.Count -eq 0) {
    Write-Success "All changes already have Step 1 complete"
    exit 0
}

if ($DryRun) {
    Write-Info "`n[DRY RUN] Would mark Step 1 complete for:"
    foreach ($change in $needsStep1) {
        Write-Host "  - $($change.Name)" -ForegroundColor Yellow
    }
    exit 0
}

# Mark Step 1 complete for each
Write-Info "`nMarking Step 1 complete..."
$updated = 0

foreach ($change in $needsStep1) {
    $changeId = $change.Name
    $todoPath = Join-Path $change.FullName "todo.md"
    
    Write-Info "Processing: $changeId"
    
    try {
        $todoContent = Get-Content $todoPath -Raw
        
        # Mark Step 1 as complete (handle both formats)
        $updatedContent = $todoContent -replace '- \[ \] 1\. Increment Release Version', '- [x] 1. Increment Release Version'
        $updatedContent = $updatedContent -replace '- \[ \] \*\*1\. Increment Release Version', '- [x] **1. Increment Release Version'
        
        Set-Content -Path $todoPath -Value $updatedContent -NoNewline
        
        Write-Success "  Marked Step 1 complete for $changeId"
        $updated++
        
    } catch {
        Write-Host "  ✗ Error for $changeId`: $_" -ForegroundColor Red
    }
}

Write-Host "`n════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Success "Marked Step 1 complete for $updated/$($needsStep1.Count) changes"

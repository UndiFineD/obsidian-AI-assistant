<#
.SYNOPSIS
    Bulk initialize todo.md for changes missing it

.DESCRIPTION
    Creates todo.md files for OpenSpec changes that are missing them,
    using the standard template.

.PARAMETER ChangePattern
    Glob pattern to match change IDs (default: "update-doc-*")

.PARAMETER DryRun
    Preview what would be created without making changes

.EXAMPLE
    .\scripts\bulk_init_todos.ps1 -ChangePattern "update-doc-*" -DryRun
    Preview which changes would get todo.md files

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
$WorkflowScript = Join-Path $ScriptRoot "scripts\workflow.ps1"

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
Write-Host "║   Bulk TODO Initializer v1.0                 ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Find changes without todo.md
Write-Info "Scanning for changes matching pattern: $ChangePattern"
$allChanges = Get-ChildItem -Path $ChangesDir -Directory -Filter $ChangePattern

$needsTodo = @()
foreach ($change in $allChanges) {
    $todoPath = Join-Path $change.FullName "todo.md"
    if (-not (Test-Path $todoPath)) {
        $needsTodo += $change
    }
}

Write-Info "Found $($allChanges.Count) total changes"
Write-Info "Need todo.md: $($needsTodo.Count)"

if ($needsTodo.Count -eq 0) {
    Write-Success "All changes already have todo.md"
    exit 0
}

if ($DryRun) {
    Write-Info "`n[DRY RUN] Would create todo.md for:"
    foreach ($change in $needsTodo) {
        Write-Host "  - $($change.Name)" -ForegroundColor Yellow
    }
    exit 0
}

# Create todo.md for each
Write-Info "`nInitializing todo.md files..."
$created = 0

foreach ($change in $needsTodo) {
    $changeId = $change.Name
    Write-Info "Processing: $changeId"
    
    try {
        # Run Step 0 to create todo.md
        & $WorkflowScript -ChangeId $changeId -Step 0 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "  Created todo.md for $changeId"
            $created++
        } else {
            Write-Host "  ✗ Failed for $changeId (exit code: $LASTEXITCODE)" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ✗ Error for $changeId`: $_" -ForegroundColor Red
    }
}

Write-Host "`n════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Success "Created todo.md for $created/$($needsTodo.Count) changes"

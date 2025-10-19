<#
.SYNOPSIS
    Applies an OpenSpec change to the baseline specification.

.DESCRIPTION
    Wrapper around `openspec apply` that provides enhanced feedback and validation.
    Automatically validates before and after applying changes.

.PARAMETER ChangeId
    Unique identifier for the change to apply (e.g., "add-api-governance").
    Can also use full path like "changes/add-api-governance".

.PARAMETER Force
    Skip pre-validation and apply immediately.

.PARAMETER DryRun
    Show what would be applied without making changes.

.EXAMPLE
    .\apply-change.ps1 -ChangeId "add-api-governance"
    # Validates and applies the change

.EXAMPLE
    .\apply-change.ps1 -ChangeId "add-api-governance" -DryRun
    # Shows what would change without applying

.EXAMPLE
    .\apply-change.ps1 -ChangeId "add-api-governance" -Force
    # Skips validation and applies immediately
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$ChangeId,

    [Parameter()]
    [switch]$Force,

    [Parameter()]
    [switch]$DryRun
)

$syntaxErrorActionPreference = "Stop"

# Determine script root (openspec directory)
$OpenSpecRoot = Split-Path -Parent $PSScriptRoot

# Normalize change path
if ($ChangeId.StartsWith("changes/")) {
    $ChangePath = $ChangeId
}
else {
    $ChangePath = "changes/$ChangeId"
}

$FullChangePath = Join-Path $OpenSpecRoot $ChangePath

# Validate change exists
if (-not (Test-Path $FullChangePath)) {
    Write-Error "Change not found: $ChangePath"
    exit 1
}

Write-Host "=== Apply OpenSpec Change ===" -ForegroundColor Cyan
Write-Host "Change: $ChangePath" -ForegroundColor White
Write-Host ""

# Pre-validation unless forced
if (-not $Force) {
    Write-Host "🔍 Validating change..." -ForegroundColor Yellow

    Push-Location $OpenSpecRoot
    try {
        $validationOutput = & openspec validate --strict $ChangePath 2>&1
        $validationExitCode = $LASTEXITCODE

        if ($validationExitCode -ne 0) {
            Write-Host "❌ Validation failed!" -ForegroundColor Red
            Write-Host $validationOutput -ForegroundColor DarkRed
            Write-Host ""
            Write-Host "💡 Fix validation errors before applying, or use -Force to skip validation" -ForegroundColor Yellow
            exit 1
        }

        Write-Host "✅ Validation passed" -ForegroundColor Green
        Write-Host ""
    }
    finally {
        Pop-Location
    }
}

# Dry run mode
if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE - Showing proposed changes:" -ForegroundColor Magenta
    Write-Host ""

    # Read and display deltas
    $specsPath = Join-Path $FullChangePath "specs"
    if (Test-Path $specsPath) {
        $capabilityDirs = Get-ChildItem -Path $specsPath -Directory
        foreach ($capDir in $capabilityDirs) {
            $specFile = Join-Path $capDir.FullName "spec.md"
            if (Test-Path $specFile) {
                Write-Host "Capability: $($capDir.Name)" -ForegroundColor Cyan
                Write-Host "---" -ForegroundColor Gray
                Get-Content $specFile | Select-String -Pattern "^## (ADDED|MODIFIED|REMOVED|RENAMED)" -Context 0, 5 | ForEach-Object {
                    Write-Host $_.Line -ForegroundColor Yellow
                    foreach ($contextLine in $_.Context.PostContext) {
                        Write-Host "  $contextLine" -ForegroundColor Gray
                    }
                }
                Write-Host ""
            }
        }
    }

    Write-Host "ℹ️  This was a dry run. No changes were applied." -ForegroundColor Cyan
    Write-Host "   Remove -DryRun flag to apply changes." -ForegroundColor Gray
    exit 0
}

# Apply change
Write-Host "📝 Applying change to baseline spec..." -ForegroundColor Yellow

Push-Location $OpenSpecRoot
try {
    $applyOutput = & openspec apply $ChangePath 2>&1
    $applyExitCode = $LASTEXITCODE

    if ($applyExitCode -ne 0) {
        Write-Host "❌ Apply failed!" -ForegroundColor Red
        Write-Host $applyOutput -ForegroundColor DarkRed
        exit 1
    }

    Write-Host "✅ Change applied successfully" -ForegroundColor Green
    Write-Host ""
}
finally {
    Pop-Location
}

# Post-validation
Write-Host "🔍 Validating updated baseline spec..." -ForegroundColor Yellow

Push-Location $OpenSpecRoot
try {
    $postValidationOutput = & openspec validate --strict specs 2>&1
    $postValidationExitCode = $LASTEXITCODE

    if ($postValidationExitCode -ne 0) {
        Write-Host "⚠️  Warning: Baseline spec validation failed after apply!" -ForegroundColor Yellow
        Write-Host $postValidationOutput -ForegroundColor DarkYellow
        Write-Host ""
        Write-Host "💡 You may need to fix the baseline spec or revert the change" -ForegroundColor Yellow
        exit 1
    }

    Write-Host "✅ Baseline spec is valid" -ForegroundColor Green
    Write-Host ""
}
finally {
    Pop-Location
}

# Success summary
Write-Host "🎉 Change applied successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Review updated baseline spec in specs/"
Write-Host "  2. Commit updated baseline to version control"
Write-Host "  3. Archive change: .\archive-change.ps1 -ChangeId $ChangeId"
Write-Host ""

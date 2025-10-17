<#
.SYNOPSIS
    Validates all OpenSpec changes and specs in the repository.

.DESCRIPTION
    Runs `openspec validate --strict` on all changes and baseline specs.
    Provides summary report with pass/fail counts and detailed error output.

.PARAMETER ChangesOnly
    Only validate changes, skip baseline specs.

.PARAMETER SpecsOnly
    Only validate baseline specs, skip changes.

.PARAMETER ChangeId
    Validate a specific change by ID (e.g., "add-api-governance").

.PARAMETER Json
    Output results in JSON format for CI/CD integration.

.PARAMETER Quiet
    Suppress detailed output, only show summary.

.EXAMPLE
    .\validate-all.ps1
    # Validates all changes and specs

.EXAMPLE
    .\validate-all.ps1 -ChangesOnly
    # Only validates pending changes

.EXAMPLE
    .\validate-all.ps1 -ChangeId "add-api-governance"
    # Validates a specific change

.EXAMPLE
    .\validate-all.ps1 -Json
    # Outputs JSON for CI/CD pipelines
#>

[CmdletBinding()]
param(
    [Parameter()]
    [switch]$ChangesOnly,

    [Parameter()]
    [switch]$SpecsOnly,

    [Parameter()]
    [string]$ChangeId,

    [Parameter()]
    [switch]$Json,

    [Parameter()]
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"

# Determine script root (openspec directory)
$OpenSpecRoot = Split-Path -Parent $PSScriptRoot

# Change to OpenSpec root for validation
Push-Location $OpenSpecRoot

try {
    # Check if openspec CLI is available
    if (-not (Get-Command openspec -ErrorAction SilentlyContinue)) {
        Write-Error "openspec CLI not found. Please ensure OpenSpec is installed and in PATH."
        exit 1
    }

    if (-not $Quiet) {
        Write-Host "=== OpenSpec Validation ===" -ForegroundColor Cyan
        Write-Host ""
    }

    # Decide validation mode
    $validateWholeRepo = -not $ChangeId -and -not $SpecsOnly -and -not $ChangesOnly

    # Run validation
    $results = @{
        total = 1
        passed = 0
        failed = 0
        errors = @()
    }

    # Build command
    $output = ""
    $exitCode = 0

    try {
        if ($validateWholeRepo) {
            if (-not $Quiet) { Write-Host "Validating entire OpenSpec repository" -ForegroundColor Gray }
            $output = if ($Json) { (& openspec validate --strict --json 2>&1) } else { (& openspec validate --strict 2>&1) }
        }
        elseif ($ChangeId) {
            $changePath = "changes/$ChangeId"
            if (-not (Test-Path $changePath)) { Write-Error "Change not found: $changePath"; exit 1 }
            if (-not $Quiet) { Write-Host "Validating change: $changePath" -ForegroundColor Gray }
            $output = if ($Json) { (& openspec validate --strict --json $changePath 2>&1) } else { (& openspec validate --strict $changePath 2>&1) }
        }
        elseif ($SpecsOnly) {
            if (-not $Quiet) { Write-Host "Validating baseline specs" -ForegroundColor Gray }
            # Many OpenSpec CLIs validate baseline with no path; fall back to whole repo
            $output = if ($Json) { (& openspec validate --strict --json 2>&1) } else { (& openspec validate --strict 2>&1) }
        }
        elseif ($ChangesOnly) {
            if (-not $Quiet) { Write-Host "Validating all pending changes" -ForegroundColor Gray }
            # Fall back to whole repo; validator will include changes
            $output = if ($Json) { (& openspec validate --strict --json 2>&1) } else { (& openspec validate --strict 2>&1) }
        }
        $exitCode = $LASTEXITCODE
    }
    catch {
        $exitCode = 1
        $output = $_.Exception.Message
    }

    if ($exitCode -eq 0) {
        $results.passed = 1
    }
    else {
        $results.failed = 1
        $results.errors += @{ target = if ($validateWholeRepo) { "." } elseif ($ChangeId) { "changes/$ChangeId" } elseif ($SpecsOnly) { "specs" } else { "changes/*" }; output = $output }
        if (-not $Quiet -and -not $Json) { Write-Host $output -ForegroundColor DarkRed }
    }

    # Summary
    if ($Json) {
        $jsonOutput = @{
            summary = @{
                total = $results.total
                passed = $results.passed
                failed = $results.failed
            }
            errors = $results.errors
        } | ConvertTo-Json -Depth 10
        Write-Output $jsonOutput
    }
    else {
        Write-Host ""
        Write-Host "=== Validation Summary ===" -ForegroundColor Cyan
    Write-Host "Total:  $($results.total)" -ForegroundColor White
    Write-Host "Passed: $($results.passed)" -ForegroundColor Green
    Write-Host "Failed: $($results.failed)" -ForegroundColor $(if ($results.failed -gt 0) { "Red" } else { "White" })
        Write-Host ""

        if ($results.failed -gt 0) {
            Write-Host "❌ Validation failed. See errors above." -ForegroundColor Red
            Write-Host ""
            Write-Host "💡 Troubleshooting tips:" -ForegroundColor Yellow
            Write-Host "  - Run: openspec validate --strict changes/<id> (for specific change)"
            Write-Host "  - Check: docs/change-patterns.md (for delta examples)"
            Write-Host "  - See: docs/troubleshooting.md (for common errors)"
            exit 1
        }
        else {
            Write-Host "✅ All validations passed!" -ForegroundColor Green
        }
    }
}
finally {
    Pop-Location
}

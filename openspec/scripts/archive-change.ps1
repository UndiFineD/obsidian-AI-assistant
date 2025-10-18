<#
.SYNOPSIS
    Archives an applied OpenSpec change with validation and backup.

.DESCRIPTION
    Wrapper around `openspec archive` that provides enhanced feedback and safety.
    Validates that the change has been applied before archiving.

.PARAMETER ChangeId
    Unique identifier for the change to archive (e.g., "add-api-governance").
    Can also use full path like "changes/add-api-governance".

.PARAMETER Force
    Skip validation and archive immediately.

.PARAMETER KeepOriginal
    Keep the original change directory after archiving.

.EXAMPLE
    .\archive-change.ps1 -ChangeId "add-api-governance"
    # Validates and archives the change

.EXAMPLE
    .\archive-change.ps1 -ChangeId "add-api-governance" -KeepOriginal
    # Archives but keeps original in openspec/changes/

.EXAMPLE
    .\archive-change.ps1 -ChangeId "add-api-governance" -Force
    # Skips validation and archives immediately
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$ChangeId,

    [Parameter()]
    [switch]$Force,

    [Parameter()]
    [switch]$KeepOriginal
)

$ErrorActionPreference = "Stop"

# Determine script root (openspec directory)
$OpenSpecRoot = Split-Path -Parent $PSScriptRoot

# Normalize change path
if ($ChangeId.StartsWith("changes/")) {
    $ChangePath = $ChangeId
    $ChangeId = $ChangeId.Replace("changes/", "")
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

Write-Host "=== Archive OpenSpec Change ===" -ForegroundColor Cyan
Write-Host "Change: $ChangePath" -ForegroundColor White
Write-Host ""

# Check if change has been applied (unless forced)
if (-not $Force) {
    Write-Host "🔍 Verifying change has been applied..." -ForegroundColor Yellow

    # Check if baseline spec exists
    $specsPath = Join-Path $FullChangePath "specs"
    if (Test-Path $specsPath) {
        $capabilityDirs = Get-ChildItem -Path $specsPath -Directory
        $allApplied = $true

        foreach ($capDir in $capabilityDirs) {
            $baselineSpec = Join-Path $OpenSpecRoot "specs" $capDir.Name "spec.md"
            if (-not (Test-Path $baselineSpec)) {
                Write-Host "⚠️  Warning: Baseline spec not found for capability: $($capDir.Name)" -ForegroundColor Yellow
                $allApplied = $false
            }
        }

        if (-not $allApplied) {
            Write-Host ""
            Write-Host "❌ Change may not have been applied yet!" -ForegroundColor Red
            Write-Host "💡 Apply first with: .\apply-change.ps1 -ChangeId $ChangeId" -ForegroundColor Yellow
            Write-Host "   Or use -Force to archive anyway" -ForegroundColor Gray
            exit 1
        }
    }

    Write-Host "✅ Change appears to have been applied" -ForegroundColor Green
    Write-Host ""
}

# Backup change before archiving
Write-Host "💾 Creating backup..." -ForegroundColor Yellow
$backupDir = Join-Path $OpenSpecRoot "backups"
$backupPath = Join-Path $backupDir "$ChangeId-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
}

Copy-Item -Path $FullChangePath -Destination $backupPath -Recurse -Force
Write-Host "✅ Backup created: $backupPath" -ForegroundColor Green
Write-Host ""

# Archive change
Write-Host "📦 Archiving change..." -ForegroundColor Yellow

Push-Location $OpenSpecRoot
try {
    $archiveOutput = & openspec archive $ChangePath 2>&1
    $archiveExitCode = $LASTEXITCODE

    if ($archiveExitCode -ne 0) {
        Write-Host "❌ Archive failed!" -ForegroundColor Red
        Write-Host $archiveOutput -ForegroundColor DarkRed
        Write-Host ""
        Write-Host "💡 Backup preserved at: $backupPath" -ForegroundColor Yellow
        exit 1
    }

    Write-Host "✅ Change archived successfully" -ForegroundColor Green
    Write-Host ""
}
finally {
    Pop-Location
}

# Remove original if not keeping
if (-not $KeepOriginal) {
    Write-Host "🗑️  Removing original change directory..." -ForegroundColor Yellow
    Remove-Item -Path $FullChangePath -Recurse -Force
    Write-Host "✅ Original change removed" -ForegroundColor Green
    Write-Host ""
}

# Verify archive
$archivePath = Join-Path $OpenSpecRoot "archive" $ChangeId
if (Test-Path $archivePath) {
    Write-Host "✅ Verified: Change exists in archive/" -ForegroundColor Green
}
else {
    Write-Host "⚠️  Warning: Archive directory not found at expected location" -ForegroundColor Yellow
    Write-Host "   Expected: $archivePath" -ForegroundColor Gray
}

# Success summary
Write-Host ""
Write-Host "🎉 Change archived successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "  Archive location: archive/$ChangeId"
Write-Host "  Backup location: $backupPath"
if (-not $KeepOriginal) {
    Write-Host "  Original removed: changes/$ChangeId (deleted)"
}
else {
    Write-Host "  Original kept: changes/$ChangeId"
}
Write-Host ""
Write-Host "💡 Tip: Commit the updated archive/ directory to version control" -ForegroundColor Gray
Write-Host ""

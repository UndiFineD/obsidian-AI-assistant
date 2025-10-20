<#
.SYNOPSIS
    Test script for change: 2025-10-19-workflow-improvements

.DESCRIPTION
    Automated test script generated from OpenSpec workflow documentation.
    Tests the implementation of the changes defined in proposal.md and spec.md.

.NOTES
    Generated: 2025-10-20 00:23:24
    Change: 2025-10-19-workflow-improvements
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ChangeRoot = $PSScriptRoot
$ProjectRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $ChangeRoot))

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Script: 2025-10-19-workflow-improvements" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$testResults = @{
    Passed = 0
    Failed = 0
    Skipped = 0
    Tests = @()
}

function Test-FileExists {
    param([string]$FilePath, [string]$Description)

    Write-Host "Testing: $Description" -NoNewline

    if (Test-Path $FilePath) {
        Write-Host " [PASS]" -ForegroundColor Green
        $testResults.Passed++
        $testResults.Tests += [PSCustomObject]@{
            Name = $Description
            Result = "PASS"
            Message = "File exists: $FilePath"
        }
        return $true
    } else {
        Write-Host " [FAIL]" -ForegroundColor Red
        Write-Host "  Expected: $FilePath" -ForegroundColor Yellow
        $testResults.Failed++
        $testResults.Tests += [PSCustomObject]@{
            Name = $Description
            Result = "FAIL"
            Message = "File not found: $FilePath"
        }
        return $false
    }
}

function Test-ContentMatches {
    param(
        [string]$FilePath,
        [string]$Pattern,
        [string]$Description
    )

    Write-Host "Testing: $Description" -NoNewline

    if (!(Test-Path $FilePath)) {
        Write-Host " [SKIP]" -ForegroundColor Yellow
        Write-Host "  File not found: $FilePath" -ForegroundColor Yellow
        $testResults.Skipped++
        return $false
    }

    $content = Get-Content $FilePath -Raw
    if ($content -match $Pattern) {
        Write-Host " [PASS]" -ForegroundColor Green
        $testResults.Passed++
        $testResults.Tests += [PSCustomObject]@{
            Name = $Description
            Result = "PASS"
            Message = "Pattern found in $FilePath"
        }
        return $true
    } else {
        Write-Host " [FAIL]" -ForegroundColor Red
        Write-Host "  Pattern not found: $Pattern" -ForegroundColor Yellow
        $testResults.Failed++
        $testResults.Tests += [PSCustomObject]@{
            Name = $Description
            Result = "FAIL"
            Message = "Pattern not found in $FilePath"
        }
        return $false
    }
}

Write-Host "Running Tests..." -ForegroundColor Cyan
Write-Host ""

# Test 1: Verify proposal.md exists and has required sections
Test-FileExists -FilePath (Join-Path $ChangeRoot "proposal.md") -Description "Proposal document exists"
Test-ContentMatches -FilePath (Join-Path $ChangeRoot "proposal.md") -Pattern "## Why" -Description "Proposal has 'Why' section"
Test-ContentMatches -FilePath (Join-Path $ChangeRoot "proposal.md") -Pattern "## What Changes" -Description "Proposal has 'What Changes' section"
Test-ContentMatches -FilePath (Join-Path $ChangeRoot "proposal.md") -Pattern "## Impact" -Description "Proposal has 'Impact' section"

# Test 2: Verify tasks.md exists and has tasks
Test-FileExists -FilePath (Join-Path $ChangeRoot "tasks.md") -Description "Tasks document exists"
Test-ContentMatches -FilePath (Join-Path $ChangeRoot "tasks.md") -Pattern "- \[[ x]\]" -Description "Tasks has checkboxes"

# Test 3: Verify spec.md exists and has content
Test-FileExists -FilePath (Join-Path $ChangeRoot "spec.md") -Description "Specification document exists"
Test-ContentMatches -FilePath (Join-Path $ChangeRoot "spec.md") -Pattern "## Acceptance Criteria|## Requirements|## Implementation" -Description "Specification has required sections"

# Test 4: Check for affected files (if specified in proposal)
$proposalPath = Join-Path $ChangeRoot "proposal.md"
if (Test-Path $proposalPath) {
    $proposalContent = Get-Content $proposalPath -Raw

    if ($proposalContent -match '(?m)^-\s*\*\*Affected files\*\*:\s*(.+)') {
        $affectedFiles = $Matches[1] -split ',' | ForEach-Object { $_.Trim() }
    
        foreach ($file in $affectedFiles) {
            if ($file -and $file -ne '[list files]') {
                $fullPath = Join-Path $ProjectRoot $file
                Test-FileExists -FilePath $fullPath -Description "Affected file: $file"
            }
        }
    }
}

# Test 5: Validate todo.md completion status
Test-FileExists -FilePath (Join-Path $ChangeRoot "todo.md") -Description "Todo checklist exists"

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Passed: $($testResults.Passed)" -ForegroundColor Green
Write-Host "Failed: $($testResults.Failed)" -ForegroundColor Red
Write-Host "Skipped: $($testResults.Skipped)" -ForegroundColor Yellow
Write-Host "Total: $($testResults.Passed + $testResults.Failed + $testResults.Skipped)"
Write-Host ""

if ($testResults.Failed -gt 0) {
    Write-Host "RESULT: FAILED" -ForegroundColor Red
    exit 1
} else {
    Write-Host "RESULT: PASSED" -ForegroundColor Green
    exit 0
}

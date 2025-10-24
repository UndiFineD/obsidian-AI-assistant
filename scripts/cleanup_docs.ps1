#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Cleanup and organize documentation files to appropriate directories

.DESCRIPTION
    Moves documentation files from root to docs/ subdirectories based on content type

.EXAMPLE
    .\scripts\cleanup_docs.ps1
#>

param(
    [switch]$Dry = $false
)

$ErrorActionPreference = "Stop"

# Define file mappings: filename pattern -> target directory
$fileMap = @{
    # Getting Started / Overview
    'README_*.md' = 'docs/getting-started'
    'STEP_*.md' = 'docs/getting-started'
    'MILESTONE_*.md' = 'docs/getting-started'
    
    # Guides / How-to
    'WORKFLOW_*.md' = 'docs/guides'
    'RESTORATION_*.txt' = 'docs/guides'
    'The_Workflow_Process.md' = 'docs/guides'
    
    # Reference / Documentation
    'VERIFICATION_*.txt' = 'docs/reference'
    'COMPLETION_*.txt' = 'docs/reference'
    '*REPORT*.md' = 'docs/reference'
    '*REPORT*.txt' = 'docs/reference'
    '*SUMMARY*.md' = 'docs/reference'
    '*SUMMARY*.txt' = 'docs/reference'
    '*INDEX*.md' = 'docs/reference'
    '*ANALYSIS*.txt' = 'docs/reference'
    '*COMPARISON*.md' = 'docs/reference'
    '*MANIFEST*.txt' = 'docs/reference'
    'TEST_FIX_*.md' = 'docs/reference'
    'IMPORT_PATH_*.md' = 'docs/reference'
    'CHANGED_FILES.txt' = 'docs/reference'
}

# Root directory
$root = Get-Location

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         DOCUMENTATION CLEANUP & ORGANIZATION SCRIPT        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Count files before
$filesBefore = @(Get-ChildItem -Path $root -File).Count
Write-Host "📊 ROOT DIRECTORY STATUS" -ForegroundColor Green
Write-Host "  Files in root before: $filesBefore"
Write-Host ""

# Collect files to move
$filesToMove = @()

foreach ($pattern in $fileMap.Keys) {
    $targetDir = $fileMap[$pattern]
    $files = Get-ChildItem -Path $root -File -Filter $pattern -ErrorAction SilentlyContinue
    
    if ($files) {
        foreach ($file in $files) {
            $filesToMove += @{
                File = $file
                Source = $file.FullName
                Target = Join-Path $targetDir $file.Name
                TargetDir = $targetDir
            }
        }
    }
}

Write-Host "📦 FILES TO MOVE: $(($filesToMove).Count)" -ForegroundColor Yellow
Write-Host ""

# Show what will be moved
foreach ($item in $filesToMove) {
    $relTarget = $item.Target.Replace((Get-Location).Path + '\', '')
    Write-Host "  ➜ $(Split-Path $item.Source -Leaf) → $relTarget"
}

if ($Dry) {
    Write-Host ""
    Write-Host "🔍 DRY RUN: No changes made" -ForegroundColor Cyan
    exit 0
}

Write-Host ""
Write-Host "⚠️  ABOUT TO MOVE $(($filesToMove).Count) FILES" -ForegroundColor Yellow
Read-Host "Press Enter to continue or Ctrl+C to cancel"

# Ensure target directories exist
$targetDirs = ($filesToMove | Select-Object -ExpandProperty TargetDir -Unique)
foreach ($dir in $targetDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✓ Created directory: $dir"
    }
}

# Move files
$moved = 0
foreach ($item in $filesToMove) {
    try {
        Move-Item -Path $item.Source -Destination $item.Target -Force
        Write-Host "  ✓ Moved: $(Split-Path $item.Source -Leaf)"
        $moved++
    }
    catch {
        Write-Host "  ✗ Failed: $(Split-Path $item.Source -Leaf) - $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "✅ CLEANUP COMPLETE" -ForegroundColor Green
Write-Host "  Files moved: $moved"

# Count files after
$filesAfter = @(Get-ChildItem -Path $root -File).Count
Write-Host "  Files in root after: $filesAfter"
Write-Host "  Reduction: $($filesBefore - $filesAfter) files"
Write-Host ""

if ($filesAfter -le 20) {
    Write-Host "✅ Root directory now meets target (<= 20 files)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Root directory still has $filesAfter files (target: <= 20)" -ForegroundColor Yellow
}

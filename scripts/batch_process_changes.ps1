<#
.SYNOPSIS
    Batch process multiple OpenSpec changes through the workflow

.DESCRIPTION
    Analyzes and processes multiple OpenSpec changes efficiently, especially
    documentation governance changes that follow similar patterns.

.PARAMETER ChangePattern
    Glob pattern to match change IDs (default: "update-doc-*")

.PARAMETER DryRun
    Preview what would be processed without making changes

.PARAMETER SkipArchive
    Process through Step 10 but don't archive (for review)

.PARAMETER Force
    Skip confirmations and process all matches

.EXAMPLE
    .\scripts\batch_process_changes.ps1 -ChangePattern "update-doc-docs-*" -DryRun
    Preview what would be processed for all docs/* governance changes

.EXAMPLE
    .\scripts\batch_process_changes.ps1 -ChangePattern "update-doc-*" -SkipArchive
    Process all update-doc-* changes but don't archive yet

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
    [switch]$DryRun,

    [Parameter()]
    [switch]$SkipArchive,

    [Parameter()]
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ScriptRoot = Split-Path -Parent $PSScriptRoot
$OpenSpecRoot = Join-Path $ScriptRoot "openspec"
$ChangesDir = Join-Path $OpenSpecRoot "changes"
$WorkflowScript = Join-Path $ScriptRoot "scripts\workflow.ps1"

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

# Analyze a change's readiness for processing
function Test-ChangeReadiness {
    param([string]$ChangePath)
    
    $changeId = Split-Path $ChangePath -Leaf
    $readiness = [pscustomobject]@{
        ChangeId = $changeId
        HasProposal = $false
        HasSpec = $false
        HasTasks = $false
        HasTodo = $false
        TodoProgress = "0/0"
        IsReady = $false
        Reason = ""
    }
    
    # Check required files
    $readiness.HasProposal = Test-Path (Join-Path $ChangePath "proposal.md")
    $readiness.HasTasks = Test-Path (Join-Path $ChangePath "tasks.md")
    $readiness.HasTodo = Test-Path (Join-Path $ChangePath "todo.md")
    
    # Check for spec delta
    $specsDir = Join-Path $ChangePath "specs"
    if (Test-Path $specsDir) {
        $specFiles = Get-ChildItem -Path $specsDir -Filter "spec.md" -Recurse
        $readiness.HasSpec = $specFiles.Count -gt 0
    }
    
    # Check todo progress if it exists
    if ($readiness.HasTodo) {
        $todoPath = Join-Path $ChangePath "todo.md"
        $todoContent = Get-Content $todoPath -Raw
        $completedSteps = ([regex]::Matches($todoContent, '\[x\]')).Count
        $totalSteps = ([regex]::Matches($todoContent, '\[[ x]\]')).Count
        $readiness.TodoProgress = "$completedSteps/$totalSteps"
        
        # Check if Step 1 is present and completed
        if ($todoContent -notmatch '\[\s*x\s*\].*1\.\s*Increment Release Version') {
            $readiness.Reason = "Step 1 not completed (version bump required)"
        }
    }
    
    # Determine if ready
    if ($readiness.HasProposal -and $readiness.HasSpec -and $readiness.HasTasks -and $readiness.HasTodo) {
        if ([string]::IsNullOrEmpty($readiness.Reason)) {
            $readiness.IsReady = $true
            $readiness.Reason = "Ready for processing"
        }
    } else {
        $missing = @()
        if (-not $readiness.HasProposal) { $missing += "proposal.md" }
        if (-not $readiness.HasSpec) { $missing += "spec delta" }
        if (-not $readiness.HasTasks) { $missing += "tasks.md" }
        if (-not $readiness.HasTodo) { $missing += "todo.md" }
        $readiness.Reason = "Missing: " + ($missing -join ", ")
    }
    
    return $readiness
}

# Main batch processing logic
function Invoke-BatchProcessing {
    Write-Host "`n╔════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║   OpenSpec Batch Change Processor v1.0       ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
    
    # Find matching changes
    Write-Info "Scanning for changes matching pattern: $ChangePattern"
    $allChanges = Get-ChildItem -Path $ChangesDir -Directory -Filter $ChangePattern
    
    if ($allChanges.Count -eq 0) {
        Write-Warning "No changes found matching pattern: $ChangePattern"
        return
    }
    
    Write-Info "Found $($allChanges.Count) changes matching pattern"
    
    # Analyze readiness
    Write-Info "`nAnalyzing change readiness..."
    $analysis = @()
    foreach ($change in $allChanges) {
        $readiness = Test-ChangeReadiness -ChangePath $change.FullName
        $analysis += $readiness
    }
    
    # Group by readiness
    $ready = $analysis | Where-Object { $_.IsReady -eq $true }
    $notReady = $analysis | Where-Object { $_.IsReady -eq $false }
    
    # Display analysis
    Write-Host "`n════════════════════════════════════════════════" -ForegroundColor Magenta
    Write-Host "READINESS ANALYSIS" -ForegroundColor Magenta
    Write-Host "════════════════════════════════════════════════" -ForegroundColor Magenta
    
    Write-Success "Ready for processing: $($ready.Count)"
    foreach ($r in $ready) {
        Write-Host "  ✓ $($r.ChangeId) ($($r.TodoProgress))" -ForegroundColor Green
    }
    
    if ($notReady.Count -gt 0) {
        Write-Warning "`nNot ready: $($notReady.Count)"
        foreach ($nr in $notReady) {
            Write-Host "  ✗ $($nr.ChangeId) - $($nr.Reason)" -ForegroundColor Yellow
        }
    }
    
    if ($ready.Count -eq 0) {
        Write-Warning "`nNo changes are ready for processing."
        return
    }
    
    # Confirm processing
    if (-not $Force -and -not $DryRun) {
        Write-Host "`n════════════════════════════════════════════════" -ForegroundColor Magenta
        $response = Read-Host "`nProcess $($ready.Count) ready changes? (y/n)"
        if ($response -ne 'y') {
            Write-Info "Processing cancelled."
            return
        }
    }
    
    if ($DryRun) {
        Write-Info "`n[DRY RUN] Would process $($ready.Count) changes"
        return
    }
    
    # Process each ready change
    Write-Host "`n════════════════════════════════════════════════" -ForegroundColor Magenta
    Write-Host "PROCESSING CHANGES" -ForegroundColor Magenta
    Write-Host "════════════════════════════════════════════════" -ForegroundColor Magenta
    
    $processed = 0
    $failed = 0
    
    foreach ($change in $ready) {
        Write-Host "`n📁 Processing: $($change.ChangeId)" -ForegroundColor Yellow
        
        try {
            # Run workflow steps 5-10 (assuming 0-4 already done based on todo)
            $steps = 5..10
            if (-not $SkipArchive) {
                $steps += 11
            }
            
            foreach ($step in $steps) {
                Write-Info "  Step $step..."
                & $WorkflowScript -ChangeId $change.ChangeId -Step $step
                
                if ($LASTEXITCODE -ne 0) {
                    Write-Error "  Step $step failed with exit code: $LASTEXITCODE"
                    $failed++
                    break
                }
            }
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "✓ Completed: $($change.ChangeId)"
                $processed++
            }
            
        } catch {
            Write-Error "✗ Failed: $($change.ChangeId) - $_"
            $failed++
        }
    }
    
    # Summary
    Write-Host "`n════════════════════════════════════════════════" -ForegroundColor Magenta
    Write-Host "BATCH PROCESSING COMPLETE" -ForegroundColor Magenta
    Write-Host "════════════════════════════════════════════════" -ForegroundColor Magenta
    Write-Success "Successfully processed: $processed"
    if ($failed -gt 0) {
        Write-Error "Failed: $failed"
    }
    Write-Info "Total analyzed: $($analysis.Count)"
}

# Execute
try {
    Invoke-BatchProcessing
} catch {
    Write-Error "Batch processing error: $_"
    Write-Error $_.ScriptStackTrace
    exit 1
}

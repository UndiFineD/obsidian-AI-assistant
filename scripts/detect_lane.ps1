#!/usr/bin/env pwsh

<#
.SYNOPSIS
CI/CD Lane Detection Automation Script (PowerShell)

.DESCRIPTION
Automatically detect which workflow lane to use based on changed files.
Provides cross-platform support for Windows developers using PowerShell.

.PARAMETER BaseRef
Base git reference to compare against (default: main or origin/main)

.PARAMETER HeadRef
Head git reference to compare (default: HEAD)

.PARAMETER Verbose
Enable verbose output

.PARAMETER JsonOutput
Output results in JSON format

.PARAMETER SkipVerification
Skip validation (for testing only)

.EXAMPLE
.\detect_lane.ps1 -BaseRef main -HeadRef HEAD

.EXAMPLE
.\detect_lane.ps1  # Auto-detect base and head

.OUTPUTS
String: Lane name (docs, standard, heavy) or JSON object

.EXIT CODES
0 - Success
1 - Error
2 - No changes detected

.DETECTED LANES
docs:     Only documentation, config, or markdown changes (~5 minutes)
standard: Mixed changes (code + docs, single feature) (~15 minutes)
heavy:    Complex changes (multiple features, large refactors) (~20 minutes)

#>

param(
    [string]$BaseRef = "",
    [string]$HeadRef = "HEAD",
    [switch]$Verbose,
    [switch]$JsonOutput,
    [switch]$SkipVerification
)

# Configuration
$ErrorActionPreference = "Stop"
$VerbosePreference = if ($Verbose) { "Continue" } else { "SilentlyContinue" }

# Colors
$Colors = @{
    Green  = "`e[0;32m"
    Red    = "`e[0;31m"
    Yellow = "`e[1;33m"
    Blue   = "`e[0;34m"
    Reset  = "`e[0m"
}

###############################################################################
# Logging Functions
###############################################################################

function Write-Info {
    param([string]$Message)
    Write-Host "$($Colors.Blue)ℹ$($Colors.Reset) $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "$($Colors.Green)✓$($Colors.Reset) $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "$($Colors.Yellow)⚠$($Colors.Reset) $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "$($Colors.Red)✗$($Colors.Reset) $Message" -ForegroundColor Red
    exit 1
}

function Write-Debug {
    param([string]$Message)
    if ($Verbose) {
        Write-Host "$($Colors.Blue)DEBUG:$($Colors.Reset) $Message" -ForegroundColor DarkCyan
    }
}

###############################################################################
# Git Operations
###############################################################################

function Determine-BaseRef {
    if ($BaseRef) {
        Write-Debug "Using provided base reference: $BaseRef"
        return $BaseRef
    }
    
    # Try to find an appropriate base reference
    $candidates = @("main", "origin/main", "master")
    
    foreach ($ref in $candidates) {
        try {
            $null = git rev-parse --verify $ref 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Debug "Using base reference: $ref"
                return $ref
            }
        }
        catch {}
    }
    
    Write-Error "Could not determine base reference. Set -BaseRef parameter or ensure main/master branch exists."
}

function Get-ChangedFiles {
    param(
        [string]$Base,
        [string]$Head
    )
    
    try {
        $files = git diff --name-status $Base $Head 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to get changed files between $Base and $Head"
        }
        return $files
    }
    catch {
        Write-Error "Git diff failed: $_"
    }
}

###############################################################################
# File Categorization
###############################################################################

function Categorize-Files {
    param(
        [string[]]$FileList
    )
    
    $categories = @{
        docs       = 0
        code       = 0
        tests      = 0
        config     = 0
        infra      = 0
        security   = 0
        other      = 0
    }
    
    foreach ($line in $FileList) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        
        $parts = $line -split "`t"
        if ($parts.Count -lt 2) { continue }
        
        $status = $parts[0]
        $file = $parts[1]
        
        # Skip deleted files
        if ($status -eq "D") { continue }
        
        # Categorize by extension and path
        switch -Regex ($file) {
            '\.md$|\.txt$|\.rst$|README|CHANGELOG|^docs/' {
                $categories.docs++
            }
            '\.github/workflows|Makefile|\.yml$|\.yaml$' {
                $categories.infra++
            }
            '^tests/|\.test\.(py|js|ts)$|\.spec\.(py|js|ts)$' {
                $categories.tests++
            }
            '(security|auth|crypto|vault|encrypt)' {
                $categories.security++
            }
            '\.(py|js|ts|jsx|tsx)$' {
                $categories.code++
            }
            '^(setup|requirements|pyproject|package\.json|tsconfig|\.eslintrc)|\.(json|toml|ini|conf)$' {
                $categories.config++
            }
            default {
                $categories.other++
            }
        }
    }
    
    return $categories
}

###############################################################################
# Commit Message Analysis
###############################################################################

function Analyze-CommitMessages {
    param(
        [string]$Base,
        [string]$Head
    )
    
    $patterns = @{
        breaking = 0
        security = 0
        refactor = 0
        feat     = 0
        fix      = 0
    }
    
    try {
        $messages = git log --pretty="%B" "$Base..$Head" 2>$null
        $fullText = $messages -join "`n"
        
        if ($fullText -match "BREAKING|breaking change|^!") {
            $patterns.breaking = 1
        }
        
        if ($fullText -match "security|vulnerability|cve") {
            $patterns.security = 1
        }
        
        if ($fullText -match "^refactor:|^refactor\s") {
            $patterns.refactor = 1
        }
        
        if ($fullText -match "^feat:|^feat\s") {
            $patterns.feat = 1
        }
        
        if ($fullText -match "^fix:|^fix\s") {
            $patterns.fix = 1
        }
    }
    catch {
        Write-Debug "Failed to analyze commit messages: $_"
    }
    
    return $patterns
}

###############################################################################
# File Impact Detection
###############################################################################

function Detect-FileImpact {
    param(
        [string]$Base,
        [string]$Head
    )
    
    $impact = @{
        adds = 0
        dels = 0
    }
    
    try {
        $stats = git diff --stat $Base $Head 2>$null
        
        foreach ($line in $stats) {
            if ($line -match '\|\s+(\d+)\s+(.+)$') {
                $changes = $matches[2]
                $impact.adds += ($changes | Select-String -AllMatches -Pattern '\+' | Measure-Object).Count
                $impact.dels += ($changes | Select-String -AllMatches -Pattern '\-' | Measure-Object).Count
            }
        }
    }
    catch {
        Write-Debug "Failed to detect file impact: $_"
    }
    
    return $impact
}

###############################################################################
# Lane Decision Logic
###############################################################################

function Decide-Lane {
    param(
        [hashtable]$Categories,
        [hashtable]$Patterns,
        [hashtable]$Impact
    )
    
    $totalCode = $Categories.code + $Categories.tests
    $totalChanges = $Categories.docs + $Categories.code + $Categories.tests + `
                    $Categories.config + $Categories.infra + $Categories.other
    
    Write-Debug "File counts: docs=$($Categories.docs) code=$($Categories.code) tests=$($Categories.tests) config=$($Categories.config) infra=$($Categories.infra)"
    Write-Debug "Patterns: breaking=$($Patterns.breaking) security=$($Patterns.security) refactor=$($Patterns.refactor)"
    Write-Debug "Impact: adds=$($Impact.adds) dels=$($Impact.dels) total_changes=$totalChanges"
    
    # HEAVY LANE: Critical changes requiring full validation
    if ($Patterns.breaking -eq 1 -or $Patterns.security -eq 1) {
        return "heavy"
    }
    
    if ($Patterns.refactor -eq 1 -and $totalCode -gt 10) {
        return "heavy"
    }
    
    if ($Categories.infra -gt 0 -and $totalCode -gt 5) {
        return "heavy"
    }
    
    # Large changes warrant heavy lane
    if ($totalChanges -gt 20 -or $Impact.adds -gt 500) {
        return "heavy"
    }
    
    # DOCS LANE: Only documentation changes
    if ($Categories.code -eq 0 -and $Categories.tests -eq 0 -and `
        $Categories.config -eq 0 -and $Categories.infra -eq 0 -and `
        $Categories.security -eq 0 -and $totalChanges -gt 0) {
        return "docs"
    }
    
    # STANDARD LANE: Default for all other cases
    return "standard"
}

###############################################################################
# Validation
###############################################################################

function Validate-Lane {
    param([string]$Lane)
    
    if ($Lane -notin @("docs", "standard", "heavy")) {
        Write-Error "Invalid lane detected: $Lane"
        return $false
    }
    
    return $true
}

###############################################################################
# Output
###############################################################################

function Out-Result {
    param(
        [string]$Lane,
        [bool]$AsJson = $false
    )
    
    if ($AsJson) {
        $result = @{
            lane        = $Lane
            timestamp   = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
            confidence  = "high"
            method      = "automatic_detection"
        }
        
        return $result | ConvertTo-Json
    }
    else {
        return $Lane
    }
}

###############################################################################
# Main
###############################################################################

function Main {
    Write-Info "Starting lane detection..."
    
    # Verify we're in a git repository
    try {
        $null = git rev-parse --git-dir 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Not in a git repository"
        }
    }
    catch {
        Write-Error "Git verification failed: $_"
    }
    
    # Determine base reference
    $base = Determine-BaseRef
    Write-Debug "Base ref: $base, Head ref: $HeadRef"
    
    # Get changed files
    Write-Debug "Analyzing changes..."
    $changedFiles = Get-ChangedFiles -Base $base -Head $HeadRef
    
    if (-not $changedFiles) {
        Write-Warning "No changes detected between $base and $HeadRef"
        $output = Out-Result -Lane "standard" -AsJson $JsonOutput
        Write-Output $output
        exit 2
    }
    
    Write-Debug "Changed files count: $($changedFiles.Count)"
    
    # Categorize files
    Write-Debug "Categorizing files..."
    $categories = Categorize-Files -FileList $changedFiles
    
    # Analyze commit messages
    Write-Debug "Analyzing commit messages..."
    $patterns = Analyze-CommitMessages -Base $base -Head $HeadRef
    
    # Detect file impact
    Write-Debug "Detecting file impact..."
    $impact = Detect-FileImpact -Base $base -Head $HeadRef
    
    # Decide lane
    Write-Debug "Applying decision logic..."
    $lane = Decide-Lane -Categories $categories -Patterns $patterns -Impact $impact
    
    # Validate
    if (-not (Validate-Lane -Lane $lane)) {
        exit 1
    }
    
    Write-Success "Lane detected: $lane"
    
    # Output result
    $output = Out-Result -Lane $lane -AsJson $JsonOutput
    Write-Output $output
    exit 0
}

# Execute main function
Main

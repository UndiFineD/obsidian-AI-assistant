<#
.SYNOPSIS
    Scaffolds a new OpenSpec change proposal with standard structure.

.DESCRIPTION
    Creates a new change directory with proposal.md, tasks.md, and capability spec templates.
    Provides interactive prompts for change details and generates starter content.

.PARAMETER ChangeId
    Unique identifier for the change (e.g., "add-api-governance", "fix-validation-bug").
    If not provided, will prompt for input.

.PARAMETER Capability
    Capability specification to modify (default: "project-documentation").
    Options: project-documentation, backend-api, plugin-features, etc.

.PARAMETER Title
    Short title for the change proposal.

.PARAMETER Description
    Detailed description of the change.

.PARAMETER Interactive
    Run in interactive mode with prompts (default: true if parameters missing).

.EXAMPLE
    .\create-change.ps1 -ChangeId "add-api-docs-governance" -Capability "project-documentation" -Title "Add governance for API documentation" -Description "Govern API_REFERENCE.md changes via OpenSpec"

.EXAMPLE
    .\create-change.ps1
    # Interactive mode - will prompt for all inputs
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$ChangeId,

    [Parameter()]
    [string]$Capability = "project-documentation",

    [Parameter()]
    [string]$Title,

    [Parameter()]
    [string]$Description,

    [Parameter()]
    [switch]$Interactive = $false
)

$ErrorActionPreference = "Stop"

# Determine script root (openspec directory)
$OpenSpecRoot = Split-Path -Parent $PSScriptRoot

# Function to prompt for input if not provided
function Get-ParameterOrPrompt {
    param(
        [string]$Value,
        [string]$PromptMessage,
        [string]$DefaultValue = ""
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        $userInput = Read-Host -Prompt $PromptMessage
        if ([string]::IsNullOrWhiteSpace($userInput) -and -not [string]::IsNullOrWhiteSpace($DefaultValue)) {
            return $DefaultValue
        }
        return $userInput
    }
    return $Value
}

# Interactive mode if parameters not fully provided
if ([string]::IsNullOrWhiteSpace($ChangeId) -or [string]::IsNullOrWhiteSpace($Title)) {
    Write-Host "=== OpenSpec Change Scaffold ===" -ForegroundColor Cyan
    Write-Host ""

    $ChangeId = Get-ParameterOrPrompt -Value $ChangeId -PromptMessage "Change ID (e.g., 'add-api-docs-governance')"
    $Title = Get-ParameterOrPrompt -Value $Title -PromptMessage "Change Title"
    $Description = Get-ParameterOrPrompt -Value $Description -PromptMessage "Change Description" -DefaultValue "TODO: Add description"
    $Capability = Get-ParameterOrPrompt -Value $Capability -PromptMessage "Capability (default: project-documentation)" -DefaultValue "project-documentation"
}

# Validate change ID format (kebab-case)
if ($ChangeId -notmatch '^[a-z0-9-]+$') {
    Write-Error "Change ID must be kebab-case (lowercase letters, numbers, and hyphens only)"
    exit 1
}

# Create directory structure
$ChangeDir = Join-Path $OpenSpecRoot "changes" $ChangeId
$SpecsDir = Join-Path $ChangeDir "specs"
$CapabilityDir = Join-Path $SpecsDir $Capability

if (Test-Path $ChangeDir) {
    Write-Error "Change directory already exists: $ChangeDir"
    exit 1
}

Write-Host "Creating change structure..." -ForegroundColor Green
New-Item -ItemType Directory -Path $CapabilityDir -Force | Out-Null

# Generate proposal.md
$ProposalContent = @"
# Proposal: $Title

## Why

<!-- Explain the problem or opportunity this change addresses -->

$Description

## What

<!-- Describe the changes being proposed -->

This change proposes to:

- [ ] TODO: List specific changes
- [ ] TODO: Add more items as needed

## Impact

<!-- Describe who is affected and how -->

**Affected users**: TODO: Describe who this impacts

**Benefits**:
- TODO: List benefits
- TODO: Add more benefits

**Risks**:
- TODO: List potential risks
- TODO: Add mitigation strategies

## Implementation Notes

<!-- Technical details, references, or constraints -->

- Related changes: TODO
- Dependencies: TODO
- Rollback plan: TODO

---

**Created**: $(Get-Date -Format "yyyy-MM-dd")
**Author**: TODO
**Status**: Draft
"@

# Generate tasks.md
$TasksContent = @"
# Implementation Tasks: $Title

## 1. Documentation Updates

- [ ] 1.1 Update capability spec with deltas (ADDED/MODIFIED/REMOVED)
- [ ] 1.2 Update related documentation references
- [ ] 1.3 Add examples or clarifications as needed

## 2. Capability Spec Changes

- [ ] 2.1 Create or update spec.md in ``specs/$Capability/``
- [ ] 2.2 Add ADDED/MODIFIED/REMOVED requirements
- [ ] 2.3 Include scenarios for each requirement (``#### Scenario:``)
- [ ] 2.4 Use SHALL or MUST in normative statements

## 3. Validation

- [ ] 3.1 Run ``openspec validate --strict`` locally
- [ ] 3.2 Fix all validation errors
- [ ] 3.3 Verify markdown formatting passes linter
- [ ] 3.4 Test scenarios for completeness

## 4. Review

- [ ] 4.1 Self-review proposal.md for clarity
- [ ] 4.2 Self-review tasks.md for completeness
- [ ] 4.3 Self-review spec.md for correctness
- [ ] 4.4 Request peer review
- [ ] 4.5 Address all review feedback

## 5. Submission

- [ ] 5.1 Commit changes to feature branch
- [ ] 5.2 Create pull request with proposal summary
- [ ] 5.3 Link to this proposal in PR description
- [ ] 5.4 Await approval and merge

## 6. Post-Merge

- [ ] 6.1 Apply changes with ``openspec apply $ChangeId``
- [ ] 6.2 Validate baseline spec with ``openspec validate --strict``
- [ ] 6.3 Archive change with ``openspec archive $ChangeId``
- [ ] 6.4 Verify archive in ``archive/$ChangeId/``

---

**Progress**: 0/21 tasks completed
**Last updated**: $(Get-Date -Format "yyyy-MM-dd")
"@

# Generate spec.md template
$SpecContent = @"
# Capability: $Capability

**Change ID**: $ChangeId

---

## ADDED Requirements

<!-- Add new requirements that don't exist in the baseline spec -->

### Requirement: TODO - Add requirement name

The [subject] SHALL [normative statement].

#### Scenario: TODO - Add scenario name

- **WHEN** [trigger condition]
- **THEN** [expected outcome]

---

## MODIFIED Requirements

<!-- Update existing requirements (include COMPLETE requirement text) -->

### Requirement: TODO - Exact name from baseline spec

[COMPLETE requirement text with all changes incorporated]

The [subject] SHALL [updated normative statement].

#### Scenario: TODO - Updated or new scenario

- **WHEN** [condition]
- **THEN** [outcome]

#### Scenario: TODO - Existing scenario if still relevant

- **WHEN** [condition]
- **THEN** [outcome]

---

## REMOVED Requirements

<!-- Delete requirements that are no longer applicable -->

### Requirement: TODO - Name of requirement being removed

#### Reason

[Explain why this requirement is being removed]

#### Migration

[Explain how to handle existing usage, if applicable]

---

## RENAMED Requirements

<!-- Change requirement names without altering behavior -->

- FROM: ``### Requirement: TODO - Old name``
- TO: ``### Requirement: TODO - New name``

---

**Notes**:
- Delete unused sections (ADDED, MODIFIED, REMOVED, RENAMED) if not applicable
- Every requirement MUST have ≥1 scenario
- Scenarios MUST use ``#### Scenario:`` heading (4 hashes)
- Requirements MUST contain SHALL or MUST
- MODIFIED deltas MUST include complete requirement text, not just changes

**See also**:
- [change-patterns.md](../../docs/change-patterns.md) - Delta pattern reference
- [AGENTS.md](../../AGENTS.md) - Complete governance workflow
"@

# Write files
$ProposalPath = Join-Path $ChangeDir "proposal.md"
$TasksPath = Join-Path $ChangeDir "tasks.md"
$SpecPath = Join-Path $CapabilityDir "spec.md"

Set-Content -Path $ProposalPath -Value $ProposalContent -Encoding UTF8
Set-Content -Path $TasksPath -Value $TasksContent -Encoding UTF8
Set-Content -Path $SpecPath -Value $SpecContent -Encoding UTF8

# Success message
Write-Host ""
Write-Host "✅ Change scaffolded successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Location: $ChangeDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Yellow
Write-Host "  1. Edit $ChangeId\proposal.md (Why/What/Impact)"
Write-Host "  2. Edit $ChangeId\specs\$Capability\spec.md (ADDED/MODIFIED/REMOVED)"
Write-Host "  3. Run: openspec validate --strict"
Write-Host "  4. Check tasks in $ChangeId\tasks.md"
Write-Host ""
Write-Host "💡 Tip: See docs/change-patterns.md for delta examples" -ForegroundColor Gray
Write-Host ""

# Open files in VS Code if available
if (Get-Command code -ErrorAction SilentlyContinue) {
    $openFiles = Read-Host "Open files in VS Code? (y/N)"
    if ($openFiles -eq 'y' -or $openFiles -eq 'Y') {
        code $ProposalPath
        code $TasksPath
        code $SpecPath
    }
}

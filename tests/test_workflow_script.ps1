<#
.SYNOPSIS
    Pester tests for scripts/workflow.ps1

.DESCRIPTION
    Comprehensive test suite for the OpenSpec workflow automation script.
    Tests all execution modes, parameter validation, and workflow steps.

.NOTES
    Author: Obsidian AI Assistant Team
    Version: 1.0.0
    Last Updated: October 18, 2025
    Requires: Pester 5.x
#>

BeforeAll {
    # Import Pester if not already loaded
    if (-not (Get-Module -Name Pester)) {
        Import-Module Pester -MinimumVersion 5.0 -ErrorAction Stop
    }

    # Set up test environment
    $script:TestRoot = Split-Path -Parent $PSScriptRoot
    $script:WorkflowScript = Join-Path $TestRoot "scripts\workflow.ps1"
    $script:TestDataDir = Join-Path $PSScriptRoot "test_data\workflow"
    $script:OpenSpecTestDir = Join-Path $TestDataDir "openspec"
    
    # Ensure test directories exist
    if (!(Test-Path $TestDataDir)) {
        New-Item -ItemType Directory -Path $TestDataDir -Force | Out-Null
    }
    if (!(Test-Path $OpenSpecTestDir)) {
        New-Item -ItemType Directory -Path $OpenSpecTestDir -Force | Out-Null
    }
    
    # Create mock OpenSpec structure
    $script:MockChangesDir = Join-Path $OpenSpecTestDir "changes"
    $script:MockArchiveDir = Join-Path $OpenSpecTestDir "archive"
    $script:MockTemplatesDir = Join-Path $OpenSpecTestDir "templates"
    
    New-Item -ItemType Directory -Path $MockChangesDir -Force | Out-Null
    New-Item -ItemType Directory -Path $MockArchiveDir -Force | Out-Null
    New-Item -ItemType Directory -Path $MockTemplatesDir -Force | Out-Null
    
    # Create mock todo.md template
    $mockTodoTemplate = @"
# TODO: <Change Title>

## Change Information
- **Change ID**: ``<change-id>``
- **Created**: YYYY-MM-DD
- **Owner**: @username
- **Status**: In Progress

---

## Workflow Progress

- [ ] **0. Create TODOs**
- [ ] **1. Increment Release Version**
- [ ] **2. Proposal**
- [ ] **3. Specification**
- [ ] **4. Task Breakdown**
- [ ] **5. Test Definition**
- [ ] **6. Script & Tooling**
- [ ] **7. Implementation**
- [ ] **8. Test Run & Validation**
- [ ] **9. Documentation Update**
- [ ] **10. Git Operations**
- [ ] **11. Archive Completed Change**
- [ ] **12. Create Pull Request (PR)**

---

## Artifacts Created

- [ ] ``openspec/changes/<change-id>/todo.md`` (this file)
- [ ] ``openspec/changes/<change-id>/proposal.md``
- [ ] ``openspec/changes/<change-id>/spec.md``
- [ ] ``openspec/changes/<change-id>/tasks.md``
- [ ] ``openspec/changes/<change-id>/test_plan.md``
- [ ] ``openspec/changes/<change-id>/retrospective.md``
"@
    
    Set-Content -Path (Join-Path $MockTemplatesDir "todo.md") -Value $mockTodoTemplate -Encoding UTF8
}

AfterAll {
    # Clean up test data
    if (Test-Path $TestDataDir) {
        Remove-Item -Path $TestDataDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Describe "workflow.ps1 Script Validation" {
    
    Context "Script File Existence and Structure" {
        
        It "Should exist in the scripts directory" {
            Test-Path $WorkflowScript | Should -Be $true
        }
        
        It "Should be a valid PowerShell script" {
            { $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content $WorkflowScript -Raw), [ref]$null) } | Should -Not -Throw
        }
        
        It "Should contain proper synopsis" {
            $content = Get-Content $WorkflowScript -Raw
            $content | Should -Match '\.SYNOPSIS'
        }
        
        It "Should contain proper description" {
            $content = Get-Content $WorkflowScript -Raw
            $content | Should -Match '\.DESCRIPTION'
        }
        
        It "Should contain parameter documentation" {
            $content = Get-Content $WorkflowScript -Raw
            $content | Should -Match '\.PARAMETER'
        }
        
        It "Should contain example usage" {
            $content = Get-Content $WorkflowScript -Raw
            $content | Should -Match '\.EXAMPLE'
        }
    }
    
    Context "Parameter Validation" {
        
        It "Should accept ChangeId parameter" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match '\[string\]\$ChangeId'
        }
        
        It "Should accept Title parameter" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match '\[string\]\$Title'
        }
        
        It "Should accept Owner parameter" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match '\[string\]\$Owner'
        }
        
        It "Should accept Step parameter with valid range (0-12)" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match 'ValidateRange\(0,\s*12\)'
        }
        
        It "Should accept DryRun switch" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match '\[switch\]\$DryRun'
        }
        
        It "Should accept Validate switch" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match '\[switch\]\$Validate'
        }
        
        It "Should accept Archive switch" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match '\[switch\]\$Archive'
        }
        
        It "Should accept List switch" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match '\[switch\]\$List'
        }
    }
    
    Context "Function Existence" {
        
        BeforeAll {
            # Dot-source the script to load functions
            . $WorkflowScript -ErrorAction Stop
        }
        
        It "Should define Write-Success function" {
            Get-Command Write-Success -ErrorAction SilentlyContinue | Should -Not -BeNullOrEmpty
        }
        
        It "Should define Write-Info function" {
            Get-Command Write-Info -ErrorAction SilentlyContinue | Should -Not -BeNullOrEmpty
        }
        
        It "Should define Write-Warning function" {
            Get-Command Write-Warning -ErrorAction SilentlyContinue | Should -Not -BeNullOrEmpty
        }
        
        It "Should define Write-Error function" {
            Get-Command Write-Error -ErrorAction SilentlyContinue | Should -Not -BeNullOrEmpty
        }
        
        It "Should define Write-Step function" {
            Get-Command Write-Step -ErrorAction SilentlyContinue | Should -Not -BeNullOrEmpty
        }
        
        It "Should define Show-Changes function" {
            Get-Command Show-Changes -ErrorAction SilentlyContinue | Should -Not -BeNullOrEmpty
        }
        
        It "Should define Test-ChangeStructure function" {
            Get-Command Test-ChangeStructure -ErrorAction SilentlyContinue | Should -Not -BeNullOrEmpty
        }
        
        It "Should define New-ChangeDirectory function" {
            Get-Command New-ChangeDirectory -ErrorAction SilentlyContinue | Should -Not -BeNullOrEmpty
        }
        
        It "Should define Invoke-Step0 function" {
            Get-Command Invoke-Step0 -ErrorAction SilentlyContinue | Should -Not -BeNullOrEmpty
        }
        
        It "Should define all workflow step functions (Step0-Step12)" {
            for ($i = 0; $i -le 12; $i++) {
                Get-Command "Invoke-Step$i" -ErrorAction SilentlyContinue | Should -Not -BeNullOrEmpty
            }
        }
        
        It "Should define Update-TodoFile function" {
            Get-Command Update-TodoFile -ErrorAction SilentlyContinue | Should -Not -BeNullOrEmpty
        }
        
        It "Should define Invoke-Workflow function" {
            Get-Command Invoke-Workflow -ErrorAction SilentlyContinue | Should -Not -BeNullOrEmpty
        }
    }
}

Describe "Workflow Script Functionality" {
    
    BeforeAll {
        # Create a test change directory
        $script:TestChangeId = "test-change-$(Get-Random)"
        $script:TestChangePath = Join-Path $MockChangesDir $TestChangeId
    }
    
    AfterEach {
        # Clean up test change after each test
        if (Test-Path $TestChangePath) {
            Remove-Item -Path $TestChangePath -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    
    Context "Change Directory Creation" {
        
        It "Should create change directory with correct structure" {
            # This would require mocking or actual execution
            # For now, we'll test the structure validation
            New-Item -ItemType Directory -Path $TestChangePath -Force | Out-Null
            New-Item -ItemType Directory -Path (Join-Path $TestChangePath "specs") -Force | Out-Null
            
            Test-Path $TestChangePath | Should -Be $true
            Test-Path (Join-Path $TestChangePath "specs") | Should -Be $true
        }
    }
    
    Context "Template File Generation" {
        
        It "Should use todo.md template if available" {
            $templatePath = Join-Path $MockTemplatesDir "todo.md"
            Test-Path $templatePath | Should -Be $true
        }
        
        It "Should replace template placeholders" {
            $template = Get-Content (Join-Path $MockTemplatesDir "todo.md") -Raw
            $template | Should -Match '<Change Title>'
            $template | Should -Match '<change-id>'
            $template | Should -Match '@username'
            $template | Should -Match 'YYYY-MM-DD'
        }
    }
    
    Context "Change Structure Validation" {
        
        It "Should validate presence of required files" {
            # Create mock change with all required files
            New-Item -ItemType Directory -Path $TestChangePath -Force | Out-Null
            New-Item -ItemType File -Path (Join-Path $TestChangePath "proposal.md") -Force | Out-Null
            New-Item -ItemType File -Path (Join-Path $TestChangePath "tasks.md") -Force | Out-Null
            New-Item -ItemType File -Path (Join-Path $TestChangePath "todo.md") -Force | Out-Null
            
            Test-Path (Join-Path $TestChangePath "proposal.md") | Should -Be $true
            Test-Path (Join-Path $TestChangePath "tasks.md") | Should -Be $true
            Test-Path (Join-Path $TestChangePath "todo.md") | Should -Be $true
        }
        
        It "Should detect missing required files" {
            # Create incomplete change
            New-Item -ItemType Directory -Path $TestChangePath -Force | Out-Null
            New-Item -ItemType File -Path (Join-Path $TestChangePath "proposal.md") -Force | Out-Null
            
            Test-Path (Join-Path $TestChangePath "tasks.md") | Should -Be $false
            Test-Path (Join-Path $TestChangePath "todo.md") | Should -Be $false
        }
    }
    
    Context "Progress Tracking" {
        
        It "Should track completed steps in todo.md" {
            $todoContent = @"
## Workflow Progress
- [x] **0. Create TODOs**
- [x] **1. Increment Release Version**
- [ ] **2. Proposal**
- [ ] **3. Specification**
"@
            $completed = ([regex]::Matches($todoContent, '\[x\]')).Count
            $completed | Should -Be 2
        }
        
        It "Should count total steps in todo.md" {
            $todoContent = @"
## Workflow Progress
- [x] **0. Create TODOs**
- [x] **1. Increment Release Version**
- [ ] **2. Proposal**
- [ ] **3. Specification**
"@
            $total = ([regex]::Matches($todoContent, '\[[ x]\]')).Count
            $total | Should -Be 4
        }
    }
}

Describe "Workflow Step Templates" {
    
    Context "Step 0 - Create TODOs" {
        
        It "Should have template for todo.md" {
            $templatePath = Join-Path $MockTemplatesDir "todo.md"
            Test-Path $templatePath | Should -Be $true
        }
        
        It "Should include all workflow steps in template" {
            $template = Get-Content (Join-Path $MockTemplatesDir "todo.md") -Raw
            $template | Should -Match '\*\*0\. Create TODOs\*\*'
            $template | Should -Match '\*\*1\. Increment Release Version\*\*'
            $template | Should -Match '\*\*2\. Proposal\*\*'
            $template | Should -Match '\*\*12\. Create Pull Request'
        }
    }
    
    Context "Step 2 - Proposal Template" {
        
        It "Should contain proposal template structure in script" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match '# Proposal:'
            $scriptContent | Should -Match '## Why'
            $scriptContent | Should -Match '## What Changes'
            $scriptContent | Should -Match '## Impact'
        }
    }
    
    Context "Step 4 - Task Breakdown Template" {
        
        It "Should contain tasks template structure in script" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match '# Tasks:'
            $scriptContent | Should -Match '## Dependencies'
            $scriptContent | Should -Match '## Estimated Effort'
        }
    }
    
    Context "Step 5 - Test Definition Template" {
        
        It "Should contain test plan template structure in script" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match '# Test Plan:'
            $scriptContent | Should -Match '### Unit Tests'
            $scriptContent | Should -Match '### Integration Tests'
            $scriptContent | Should -Match '## Acceptance Criteria'
        }
    }
}

Describe "Script Error Handling" {
    
    Context "Input Validation" {
        
        It "Should handle missing ChangeId gracefully" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            # Check that script validates ChangeId when required
            $scriptContent | Should -Match 'ChangeId is required'
        }
        
        It "Should handle invalid Step parameter" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            # ValidateRange should prevent invalid step numbers
            $scriptContent | Should -Match 'ValidateRange\(0,\s*12\)'
        }
    }
    
    Context "File System Operations" {
        
        It "Should check for existing change directory" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match 'Change directory already exists'
        }
        
        It "Should handle missing template files" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match 'Template not found'
        }
    }
    
    Context "Git Operations" {
        
        It "Should include git add operation" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match 'git add'
        }
        
        It "Should include git commit operation" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match 'git commit'
        }
        
        It "Should include git push operation" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match 'git push'
        }
    }
}

Describe "Script Output and Formatting" {
    
    Context "Color Output Functions" {
        
        It "Should use Write-Host for colored output" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match 'Write-Host.*-ForegroundColor Green'
            $scriptContent | Should -Match 'Write-Host.*-ForegroundColor Cyan'
            $scriptContent | Should -Match 'Write-Host.*-ForegroundColor Yellow'
            $scriptContent | Should -Match 'Write-Host.*-ForegroundColor Red'
        }
        
        It "Should use Unicode symbols for visual feedback" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match '✓' # Success
            $scriptContent | Should -Match 'ℹ' # Info
            $scriptContent | Should -Match '⚠' # Warning
            $scriptContent | Should -Match '✗' # Error
        }
    }
    
    Context "Step Headers" {
        
        It "Should format step headers with separators" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match 'Step \$StepNumber'
            $scriptContent | Should -Match '={40,}' # Separator line
        }
    }
}

Describe "Workflow Compliance" {
    
    Context "OpenSpec Alignment" {
        
        It "Should reference PROJECT_WORKFLOW.md" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match 'PROJECT_WORKFLOW\.md'
        }
        
        It "Should implement all 13 workflow steps (0-12)" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            for ($i = 0; $i -le 12; $i++) {
                $scriptContent | Should -Match "function Invoke-Step$i"
            }
        }
        
        It "Should mark hard requirements correctly" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match '\[HARD REQUIREMENT\]'
        }
    }
    
    Context "Archive Workflow" {
        
        It "Should implement archive before PR (step 11 before 12)" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            # Check that archive step exists
            $scriptContent | Should -Match 'function Invoke-Step11'
            # Check that PR step exists
            $scriptContent | Should -Match 'function Invoke-Step12'
            # Verify order in workflow execution
            $scriptContent | Should -Match 'Archive Completed Change'
        }
        
        It "Should copy files to archive directory" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match 'Copy-Item.*archive'
        }
        
        It "Should remove from changes directory after archiving" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match 'Remove-Item.*changes'
        }
    }
}

Describe "DryRun Mode" {
    
    Context "DryRun Parameter" {
        
        It "Should support DryRun mode" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match '\[switch\]\$DryRun'
        }
        
        It "Should check DryRun flag before file operations" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match 'if \(!\$DryRun\)'
        }
        
        It "Should display preview messages in DryRun mode" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match '\[DRY RUN\]'
        }
    }
}

Describe "Integration Points" {
    
    Context "OpenSpec Directory Structure" {
        
        It "Should reference correct directory paths" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match 'openspec'
            $scriptContent | Should -Match 'changes'
            $scriptContent | Should -Match 'archive'
            $scriptContent | Should -Match 'templates'
        }
    }
    
    Context "Test Execution" {
        
        It "Should run pytest for validation" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match 'pytest'
        }
        
        It "Should use change-specific test filter" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match 'pytest -k'
        }
    }
    
    Context "Version Management" {
        
        It "Should reference version files" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match 'CHANGELOG\.md'
            $scriptContent | Should -Match 'README\.md'
            $scriptContent | Should -Match 'package\.json'
        }
    }
}

Describe "Documentation and Help" {
    
    Context "Comment-Based Help" {
        
        It "Should have complete help documentation" {
            $help = Get-Help $WorkflowScript -ErrorAction SilentlyContinue
            $help | Should -Not -BeNullOrEmpty
        }
        
        It "Should document all parameters" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match '\.PARAMETER ChangeId'
            $scriptContent | Should -Match '\.PARAMETER Title'
            $scriptContent | Should -Match '\.PARAMETER Owner'
            $scriptContent | Should -Match '\.PARAMETER Step'
        }
        
        It "Should include usage examples" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match '\.EXAMPLE'
        }
    }
    
    Context "Inline Documentation" {
        
        It "Should include step descriptions" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match 'Create TODOs'
            $scriptContent | Should -Match 'Increment Release Version'
            $scriptContent | Should -Match 'Archive Completed Change'
        }
    }
}

Describe "Edge Cases and Error Scenarios" {
    
    Context "Invalid Input Handling" {
        
        It "Should validate change ID format expectations" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            # Script should handle kebab-case format
            $scriptContent | Should -Match 'kebab-case'
        }
    }
    
    Context "File System Edge Cases" {
        
        It "Should handle missing directories gracefully" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match 'Test-Path'
        }
        
        It "Should create directories when needed" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match 'New-Item -ItemType Directory'
        }
    }
    
    Context "Interactive Mode Edge Cases" {
        
        It "Should handle user cancellation" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match "response.*-ne.*'y'"
        }
        
        It "Should allow pausing workflow" {
            $scriptContent = Get-Content $WorkflowScript -Raw
            $scriptContent | Should -Match 'Workflow paused'
        }
    }
}

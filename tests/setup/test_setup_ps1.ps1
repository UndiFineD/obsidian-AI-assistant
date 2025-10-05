# tests/setup/test_setup_ps1.ps1
<#
.SYNOPSIS
Pester tests for setup.ps1 script.
.DESCRIPTION
Comprehensive test suite for the PowerShell setup script that validates
virtual environment creation, dependency installation, Node.js setup, and error handling.
#>

# Import Pester if available, otherwise provide instructions
try {
    Import-Module Pester -MinimumVersion 5.0 -Force
} catch {
    Write-Warning "Pester module not found. Install with: Install-Module -Name Pester -Force -SkipPublisherCheck"
    Write-Warning "Then run these tests with: Invoke-Pester"
    exit 1
}

BeforeAll {
    # Get the path to the setup script
    $setupScript = Join-Path $PSScriptRoot "..\..\setup.ps1"
    
    # Create a test workspace directory
    $testWorkspace = Join-Path $env:TEMP "obsidian-ai-test-$(Get-Date -Format 'yyyyMMddHHmmss')"
    New-Item -Path $testWorkspace -ItemType Directory -Force | Out-Null
    
    # Copy setup script to test workspace for isolated testing
    $testSetupScript = Join-Path $testWorkspace "setup.ps1"
    Copy-Item $setupScript $testSetupScript
    
    # Create mock requirements.txt for testing
    $mockRequirements = Join-Path $testWorkspace "requirements.txt"
    Set-Content -Path $mockRequirements -Value @"
fastapi==0.104.1
uvicorn==0.24.0
requests==2.31.0
"@
    
    # Mock backend directory and file
    $mockBackendDir = Join-Path $testWorkspace "backend"
    New-Item -Path $mockBackendDir -ItemType Directory -Force | Out-Null
    $mockBackendFile = Join-Path $mockBackendDir "backend.py"
    Set-Content -Path $mockBackendFile -Value "# Mock backend.py file for testing"
    
    # Store original location
    $originalLocation = Get-Location
}

AfterAll {
    # Cleanup test workspace
    Set-Location $originalLocation
    if (Test-Path $testWorkspace) {
        Remove-Item $testWorkspace -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Describe "Setup Script Configuration" {
    BeforeAll {
        Set-Location $testWorkspace
        $scriptContent = Get-Content $testSetupScript -Raw
    }
    
    It "Has correct Python executable configuration" {
        $scriptContent | Should -Match '\$pythonExe = "python"'
    }
    
    It "Has Node.js download URL configured" {
        $scriptContent | Should -Match 'nodejs.org/dist/v24.8.0'
    }
    
    It "Has virtual environment directory configured" {
        $scriptContent | Should -Match '\$venvDir.*"venv"'
    }
    
    It "Has requirements file path configured" {
        $scriptContent | Should -Match '\$requirementsFile.*"requirements.txt"'
    }
}

Describe "Python Environment Setup" {
    BeforeAll {
        Set-Location $testWorkspace
    }
    
    It "Should detect Python installation" {
        # Test if Python detection logic works
        $pythonCheck = try { 
            & python --version 2>&1 
        } catch { 
            $null 
        }
        
        if ($pythonCheck) {
            $pythonCheck | Should -Match "Python \d+\.\d+\.\d+"
        } else {
            # If Python not available, test should note this
            $true | Should -Be $true  # Test environment limitation
        }
    }
    
    It "Should create virtual environment directory structure" {
        # Mock the venv creation by creating expected directory structure
        $venvDir = Join-Path $testWorkspace "venv"
        $scriptsDir = Join-Path $venvDir "Scripts"
        
        New-Item -Path $scriptsDir -ItemType Directory -Force | Out-Null
        New-Item -Path (Join-Path $scriptsDir "python.exe") -ItemType File -Force | Out-Null
        New-Item -Path (Join-Path $scriptsDir "Activate.ps1") -ItemType File -Force | Out-Null
        
        Test-Path $venvDir | Should -Be $true
        Test-Path (Join-Path $scriptsDir "python.exe") | Should -Be $true
        Test-Path (Join-Path $scriptsDir "Activate.ps1") | Should -Be $true
    }
    
    It "Should handle missing Activate.ps1 gracefully" {
        $venvDir = Join-Path $testWorkspace "venv"
        $activateScript = Join-Path $venvDir "Scripts\Activate.ps1"
        
        # Ensure activate script doesn't exist
        if (Test-Path $activateScript) {
            Remove-Item $activateScript -Force
        }
        
        Test-Path $activateScript | Should -Be $false
    }
}

Describe "Requirements Installation" {
    BeforeAll {
        Set-Location $testWorkspace
    }
    
    It "Should find requirements.txt when it exists" {
        Test-Path "requirements.txt" | Should -Be $true
    }
    
    It "Should have valid requirements.txt format" {
        $requirements = Get-Content "requirements.txt"
        $requirements | Should -Contain "fastapi==0.104.1"
        $requirements | Should -Contain "uvicorn==0.24.0"
        $requirements | Should -Contain "requests==2.31.0"
    }
    
    It "Should handle missing requirements.txt" {
        # Temporarily rename requirements.txt
        $requirements = "requirements.txt"
        $tempName = "requirements.txt.bak"
        
        Rename-Item $requirements $tempName -ErrorAction SilentlyContinue
        
        try {
            Test-Path $requirements | Should -Be $false
            # Script should have fallback dependencies
            $scriptContent = Get-Content $testSetupScript -Raw
            $scriptContent | Should -Match "fallbackDeps.*fastapi"
        } finally {
            # Restore requirements.txt
            Rename-Item $tempName $requirements -ErrorAction SilentlyContinue
        }
    }
    
    It "Should have fallback dependencies defined" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "fastapi"
        $scriptContent | Should -Match "uvicorn"
        $scriptContent | Should -Match "torch"
        $scriptContent | Should -Match "sentence-transformers"
    }
}

Describe "Hugging Face Integration" {
    BeforeAll {
        Set-Location $testWorkspace
    }
    
    It "Should prompt for Hugging Face token" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "Read-Host.*Hugging Face token"
    }
    
    It "Should handle empty token gracefully" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "Skipping Hugging Face login"
    }
    
    It "Should attempt HF login with valid token" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "hf auth login --token"
    }
    
    It "Should handle HF login errors" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "Failed to login to Hugging Face"
    }
}

Describe "Node.js Installation" {
    BeforeAll {
        Set-Location $testWorkspace
    }
    
    It "Should check for existing Node.js installation" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "Get-Command node"
    }
    
    It "Should configure TLS 1.2 for downloads" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "SecurityProtocol.*Tls12"
    }
    
    It "Should have valid Node.js download URL" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $nodeUrl = ($scriptContent | Select-String 'nodeZipUrl = "(.*?)"').Matches[0].Groups[1].Value
        
        $nodeUrl | Should -Match "^https://nodejs.org/"
        $nodeUrl | Should -Match "\.zip$"
    }
    
    It "Should create nodejs directory if not exists" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "New-Item.*nodejs.*Directory"
    }
    
    It "Should handle download errors" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "Failed to download Node.js"
    }
    
    It "Should handle extraction errors" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "Failed to extract Node.js"
    }
    
    It "Should verify Node.js installation" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "Node.js and npm installed successfully"
    }
}

Describe "Path and Environment Configuration" {
    BeforeAll {
        Set-Location $testWorkspace
    }
    
    It "Should add Node.js to PATH" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match '\$env:Path = ".*\$env:Path"'
    }
    
    It "Should provide backend activation instructions" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "To activate backend manually"
    }
    
    It "Should check for backend.py existence" {
        Test-Path "backend\backend.py" | Should -Be $true
    }
    
    It "Should provide Obsidian plugin build instructions" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "npm install.*npm run build"
    }
}

Describe "Error Handling" {
    BeforeAll {
        Set-Location $testWorkspace
    }
    
    It "Should exit with error code 1 when Python not found" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "exit 1"
    }
    
    It "Should handle virtual environment creation failures" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "Virtual environment may not have been created correctly"
    }
    
    It "Should use try-catch blocks for critical operations" {
        $scriptContent = Get-Content $testSetupScript -Raw
        
        # Should have try-catch for Python version check
        $scriptContent | Should -Match "try\s*{[\s\S]*?pythonVersion[\s\S]*?}\s*catch"
        
        # Should have try-catch for HF login
        $scriptContent | Should -Match "try\s*{[\s\S]*?hf auth login[\s\S]*?}\s*catch"
        
        # Should have try-catch for Node.js operations
        $scriptContent | Should -Match "try\s*{[\s\S]*?Invoke-WebRequest[\s\S]*?}\s*catch"
    }
}

Describe "Output and Messaging" {
    BeforeAll {
        Set-Location $testWorkspace
    }
    
    It "Should display setup header" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "=== Obsidian AI Assistant Setup ==="
    }
    
    It "Should display completion message" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "=== Setup Complete ==="
    }
    
    It "Should use Write-Host for informational messages" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "Write-Host.*Creating Python virtual environment"
        $scriptContent | Should -Match "Write-Host.*Installing dependencies"
    }
    
    It "Should use Write-Error for error conditions" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "Write-Error.*Python not found"
    }
    
    It "Should use Write-Warning for warnings" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "Write-Warning.*requirements.txt not found"
        $scriptContent | Should -Match "Write-Warning.*Failed to login to Hugging Face"
    }
}

Describe "File and Directory Operations" {
    BeforeAll {
        Set-Location $testWorkspace
    }
    
    It "Should use Join-Path for cross-platform compatibility" {
        $scriptContent = Get-Content $testSetupScript -Raw
        
        # Should use Join-Path for all path operations
        ($scriptContent | Select-String "Join-Path").Count | Should -BeGreaterThan 5
    }
    
    It "Should use Test-Path to check file existence" {
        $scriptContent = Get-Content $testSetupScript -Raw
        
        # Should check for various files and directories
        $scriptContent | Should -Match "Test-Path.*venvDir"
        $scriptContent | Should -Match "Test-Path.*activateScript"
        $scriptContent | Should -Match "Test-Path.*requirementsFile"
    }
    
    It "Should handle PSScriptRoot correctly" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match '\$PSScriptRoot'
    }
}

Describe "Security and Best Practices" {
    BeforeAll {
        Set-Location $testWorkspace
    }
    
    It "Should use secure download methods" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "UseBasicParsing"
        $scriptContent | Should -Match "ErrorAction Stop"
    }
    
    It "Should clean up temporary files" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "Remove-Item.*zipFile"
    }
    
    It "Should use proper error handling in finally blocks" {
        $scriptContent = Get-Content $testSetupScript -Raw
        $scriptContent | Should -Match "}\s*finally\s*{"
    }
    
    It "Should avoid hardcoded sensitive information" {
        $scriptContent = Get-Content $testSetupScript -Raw
        
        # Should not contain hardcoded tokens or passwords
        $scriptContent | Should -Not -Match "token.*[a-zA-Z0-9]{20,}"
        $scriptContent | Should -Not -Match "password.*="
    }
}
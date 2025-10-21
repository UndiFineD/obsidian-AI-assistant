#Requires -Version 5.1
<#
.SYNOPSIS
    Obsidian AI Agent Plugin Setup Script
.DESCRIPTION
    Automates the complete setup process for the Obsidian AI Agent plugin including:
    - Plugin directory creation
    - File copying and verification
    - Backend server configuration
    - Dependency checking
    - Plugin enablement guidance
.PARAMETER VaultPath
    Path to your Obsidian vault directory. If not specified, will prompt for selection.
.PARAMETER BackendOnly
    Only start the backend server without installing plugin files
.PARAMETER PluginOnly
    Only install plugin files without starting backend server
.PARAMETER Force
    Overwrite existing plugin installation without prompting
.EXAMPLE
    .\setup-plugin.ps1
    Interactive setup with vault selection
.EXAMPLE
    .\setup-plugin.ps1 -VaultPath "C:\Users\kdejo\DEV\Vault"
    Direct setup to specified vault
.EXAMPLE
    .\setup-plugin.ps1 -BackendOnly
    Only start the backend server
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$VaultPath,
    
    [Parameter(Mandatory = $false)]
    [switch]$BackendOnly,
    
    [Parameter(Mandatory = $false)]
    [switch]$PluginOnly,
    
    [Parameter(Mandatory = $false)]
    [switch]$Force
)

# Source the configuration file
$ConfigPath = Join-Path $PSScriptRoot "setup-config.ps1"
if (Test-Path $ConfigPath) {
    . $ConfigPath
}

# Sensible defaults if not provided by setup-config.ps1
if (-not $global:SERVER_START_TIMEOUT) { $global:SERVER_START_TIMEOUT = 3 }
if (-not $global:HEALTH_CHECK_TIMEOUT) { $global:HEALTH_CHECK_TIMEOUT = 5 }
if (-not $global:BACKEND_HOST) { $global:BACKEND_HOST = "127.0.0.1" }
if (-not $global:BACKEND_PORT) { $global:BACKEND_PORT = 8000 }
if (-not $global:BACKEND_RELOAD) { $global:BACKEND_RELOAD = $false }

# IMPORTANT: Folder name must match manifest.json id ("obsidian-ai-agent")
if (-not $global:PLUGIN_NAME) { $global:PLUGIN_NAME = "obsidian-ai-agent" }

# Color functions for better output
function Write-ColorOutput {
    param([string]$Text, [string]$Color = "White")
    switch ($Color) {
        "Red" { Write-Host $Text -ForegroundColor Red }
        "Green" { Write-Host $Text -ForegroundColor Green }
        "Yellow" { Write-Host $Text -ForegroundColor Yellow }
        "Cyan" { Write-Host $Text -ForegroundColor Cyan }
        "Magenta" { Write-Host $Text -ForegroundColor Magenta }
        default { Write-Host $Text -ForegroundColor White }
    }
}

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-ColorOutput "═══════════════════════════════════════════════════════════" "Cyan"
    Write-ColorOutput "  $Title" "Cyan"
    Write-ColorOutput "═══════════════════════════════════════════════════════════" "Cyan"
    Write-Host ""
}

function Write-Step {
    param([string]$Step, [int]$Number)
    Write-ColorOutput "[$Number] $Step" "Yellow"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✅ $Message" "Green"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "❌ $Message" "Red"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠️  $Message" "Yellow"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "ℹ️  $Message" "Cyan"
}

# Check prerequisites
function Test-Prerequisites {
    Write-Step "Checking Prerequisites" 1
    
    # Check PowerShell version
    if ($PSVersionTable.PSVersion.Major -lt 5) {
        Write-Error "PowerShell 5.1 or higher is required"
        return $false
    }
    Write-Success "PowerShell version: $($PSVersionTable.PSVersion)"
    
    # Check Python installation
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python found: $pythonVersion"
        } else {
            Write-Error "Python not found in PATH. Please install Python 3.8+"
            return $false
        }
    } catch {
        Write-Error "Python not found. Please install Python 3.8+"
        return $false
    }
    
    # Check if we're in the correct directory
    # Removed unused variable $currentDir
    $expectedFiles = @("backend", "plugin", "package.json", "README.md")
    $missingFiles = @()
    
    foreach ($file in $expectedFiles) {
        if (-not (Test-Path $file)) {
            $missingFiles += $file
        }
    }
    
    if ($missingFiles.Count -gt 0) {
        Write-Error "Missing expected files/directories: $($missingFiles -join ', ')"
        Write-Error "Please run this script from the obsidian-ai-agent directory"
        return $false
    }
    
    Write-Success "All prerequisites met"
    return $true
}

# Get or validate vault path
function Get-VaultPath {
    if ($VaultPath) {
        if (Test-Path $VaultPath) {
            Write-Success "Using specified vault: $VaultPath"
            return $VaultPath
        } else {
            Write-Error "Specified vault path does not exist: $VaultPath"
            return $null
        }
    }
    
    # Interactive vault selection
    Write-Info "Please select your Obsidian vault directory"
    
    # Common vault locations
    $commonPaths = @(
        "$env:USERPROFILE\Documents\Obsidian Vault",
        "$env:USERPROFILE\DEV\Vault",
        "$env:USERPROFILE\Obsidian",
        "$env:USERPROFILE\Documents\vault"
    )
    
    Write-Host ""
    Write-Host "Common vault locations:"
    for ($i = 0; $i -lt $commonPaths.Count; $i++) {
        $exists = Test-Path $commonPaths[$i]
        $status = if ($exists) { "✅" } else { "❌" }
        Write-Host "  [$($i + 1)] $status $($commonPaths[$i])"
    }
    Write-Host "  [0] Enter custom path"
    Write-Host ""
    
    do {
        $choice = Read-Host "Enter choice (0-$($commonPaths.Count))"
        
        if ($choice -eq "0") {
            do {
                $customPath = Read-Host "Enter full path to your Obsidian vault"
                if (Test-Path $customPath) {
                    Write-Success "Vault found: $customPath"
                    return $customPath
                } else {
                    Write-Error "Path does not exist: $customPath"
                }
            } while ($true)
        } elseif ($choice -ge 1 -and $choice -le $commonPaths.Count) {
            $selectedPath = $commonPaths[$choice - 1]
            if (Test-Path $selectedPath) {
                Write-Success "Selected vault: $selectedPath"
                return $selectedPath
            } else {
                Write-Error "Selected path does not exist: $selectedPath"
            }
        } else {
            Write-Error "Invalid choice. Please enter a number between 0 and $($commonPaths.Count)"
        }
    } while ($true)
}

# Install plugin files
function Install-PluginFiles {
    param([string]$VaultPath)
    
    Write-Step "Installing Plugin Files" 2
    
    $sourceDir = Join-Path $PSScriptRoot "plugin"

    # Prefer manifest.json id for folder name; fallback to PLUGIN_NAME
    $manifestId = $null
    $manifestPath = Join-Path $sourceDir "manifest.json"
    if (Test-Path $manifestPath) {
        try {
            $manifest = Get-Content -Raw -Path $manifestPath | ConvertFrom-Json
            if ($manifest.id) { $manifestId = $manifest.id }
        } catch {}
    }
    $folderName = if ($manifestId) { $manifestId } else { $PLUGIN_NAME }
    $pluginDir = Join-Path $VaultPath ".obsidian\plugins\$folderName"
    
    # Check if plugin already exists
    if ((Test-Path $pluginDir) -and -not $Force) {
        Write-Warning "Plugin directory already exists: $pluginDir"
        $overwrite = Read-Host "Overwrite existing installation? (y/N)"
        if ($overwrite -notmatch "^[Yy]") {
            Write-Info "Skipping plugin installation"
            return $pluginDir
        }
    }
    
    # Create plugin directory
    try {
        if (Test-Path $pluginDir) {
            Write-Info "Removing existing plugin directory"
            Remove-Item $pluginDir -Recurse -Force
        }
        
        Write-Info "Creating plugin directory: $pluginDir"
        New-Item -ItemType Directory -Path $pluginDir -Force | Out-Null
        
    # Recursively copy all files and subfolders from .obsidian/plugins/obsidian-ai-agent/ to the vault plugin directory
        Write-Info "Recursively copying all plugin files and folders..."
        Copy-Item -Path $sourceDir\* -Destination $pluginDir -Recurse -Force
        # Count files and total size for summary
        $allFiles = Get-ChildItem -Path $sourceDir -Recurse -File
        $copiedCount = $allFiles.Count
        $totalSize = ($allFiles | Measure-Object -Property Length -Sum).Sum
        foreach ($fileObj in $allFiles) {
            Write-Info "Copied: $($fileObj.FullName.Substring($sourceDir.Length+1)) ($([math]::Round($fileObj.Length / 1024, 1)) KB)"
        }
        
        # Create setup instructions
        $readmeContent = @"
# Obsidian AI Agent Plugin - Installation Complete

## 🎯 Plugin Successfully Installed!
Installation Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Files Copied: $copiedCount
Total Size: $([math]::Round($totalSize / 1024, 1)) KB

## 🚀 Next Steps to Enable Plugin:

### 1. Enable Community Plugins in Obsidian
1. Open Obsidian
2. Go to Settings (⚙️) → Community plugins
3. Turn OFF "Safe mode" if it's enabled
4. Click "Refresh" (re-scan plugins)
5. Find "$PLUGIN_NAME" in the installed plugins list
6. Toggle the switch to enable it

### 2. Backend Server Information
- Server URL: http://$BACKEND_HOST`:$BACKEND_PORT
- Status: Use this script to start the server
- Health Check: http://$BACKEND_HOST`:$BACKEND_PORT/health

### 3. Plugin Features
- 🧠 AI Question Answering
- 📋 Task Queue Management
- 🎤 Voice Input (if supported)
- 📊 Analytics Dashboard
- 🔄 Vault Reindexing

## 🆘 Troubleshooting
- Plugin not visible: Ensure Community plugins are enabled
- Connection errors: Start the backend server first
- Voice issues: Check browser microphone permissions

Generated by setup-plugin.ps1 on $(Get-Date)
"@
        
        $readmePath = Join-Path $pluginDir "SETUP_COMPLETE.md"
        Set-Content -Path $readmePath -Value $readmeContent -Encoding UTF8
        
        # Post-copy verification of critical files
        $required = @(
            "main.js",
            "manifest.json",
            "rightPane.js",
            "backendClient.js"
        )
        $missing = @()
        foreach ($req in $required) {
            if (-not (Test-Path (Join-Path $pluginDir $req))) {
                $missing += $req
            }
        }
        if ($missing.Count -gt 0) {
            Write-Error "Missing required plugin files after copy: $($missing -join ', ')"
            Write-Error "Please ensure these files exist under '$sourceDir' and re-run with -Force."
            return $null
        }

        Write-Success "Plugin files installed successfully"
        Write-Success "Files copied: $copiedCount"
        Write-Success "Total size: $([math]::Round($totalSize / 1024, 1)) KB"
        Write-Success "Location: $pluginDir"
        
        return $pluginDir
        
    } catch {
        Write-Error "Failed to install plugin files: $($_.Exception.Message)"
        return $null
    }
}

# Test backend dependencies
function Test-BackendDependencies {
    Write-Step "Checking Backend Dependencies" 3
    
    try {
        # Test Python imports
        $testScript = @"
try:
    import fastapi
    import uvicorn
    print(f"FastAPI: {fastapi.__version__}")
    print(f"Uvicorn: {uvicorn.__version__}")
    print("DEPENDENCIES_OK")
except ImportError as e:
    print(f"MISSING_DEPENDENCY: {e}")
    exit(1)
"@
        
        $result = python -c $testScript 2>&1
        
        if ($LASTEXITCODE -eq 0 -and $result -match "DEPENDENCIES_OK") {
            Write-Success "Backend dependencies available"
            $result | Where-Object { $_ -notmatch "DEPENDENCIES_OK" } | ForEach-Object {
                Write-Info $_
            }
            return $true
        } else {
            Write-Error "Missing backend dependencies"
            Write-Info "Install with: pip install fastapi uvicorn"
            return $false
        }
    } catch {
        Write-Error "Failed to check dependencies: $($_.Exception.Message)"
        return $false
    }
}

# Start backend server
function Start-BackendServer {
    Write-Step "Starting Backend Server" 4
    
    if (-not (Test-BackendDependencies)) {
        Write-Error "Cannot start backend - missing dependencies"
        return $false
    }
    
    # Check if server is already running
    try {
        $response = Invoke-RestMethod -Uri "http://$BACKEND_HOST`:$BACKEND_PORT/health" -TimeoutSec $HEALTH_CHECK_TIMEOUT -ErrorAction SilentlyContinue
        if ($response) {
            Write-Success "Backend server already running at http://$BackendHost`:$BackendPort"
            return $true
        }
    } catch {
        # Server not running, continue with startup
    }
    
    Write-Info "Starting FastAPI backend server..."
    Write-Info "URL: http://$BACKEND_HOST`:$BACKEND_PORT"
    Write-Info "Press Ctrl+C to stop the server"
    Write-Warning "Keep this terminal open while using the plugin"
    
    try {
        # Ensure working directory is the repo root where backend/ exists
        $repoRoot = $PSScriptRoot
        if (-not $repoRoot) { $repoRoot = (Get-Location).Path }
        Write-Info "Setting working directory: $repoRoot"
        # Start server in background job for quick health probe
        $serverJob = Start-Job -ScriptBlock {
            param($RepoRoot, $BackendHost, $Port, $Reload)
            try {
                Set-Location $RepoRoot
                $env:FAST_STARTUP = '1'
                $env:SKIP_MODEL_DOWNLOADS = '1'
                python -m uvicorn backend.backend:app --host $BackendHost --port $Port $(if($Reload){'--reload'})
            } catch {
                Write-Output "UVICORN_START_ERROR: $($_.Exception.Message)"
            }
        } -ArgumentList $repoRoot, $BACKEND_HOST, $BACKEND_PORT, $BACKEND_RELOAD
        
        # Poll health for up to ~10 seconds
        $deadline = (Get-Date).AddSeconds([Math]::Max(5, [int]$SERVER_START_TIMEOUT))
        $healthy = $false
        while ((Get-Date) -lt $deadline) {
            try {
                $response = Invoke-RestMethod -Uri "http://$BACKEND_HOST`:$BACKEND_PORT/health" -TimeoutSec $HEALTH_CHECK_TIMEOUT -ErrorAction Stop
                if ($response) { $healthy = $true; break }
            } catch {
                Start-Sleep -Milliseconds 500
            }
        }
        
        # Test server health
        try {
            if (-not $healthy) { throw "Health endpoint not responding" }
            Write-Success "Backend server started successfully"
            Write-Success "Health check responded"
            
            # Stop the job since we just wanted to test startup
            Stop-Job $serverJob -ErrorAction SilentlyContinue
            Remove-Job $serverJob -ErrorAction SilentlyContinue
            
            # Now start interactively with correct working directory
            Write-Info "Starting server in interactive mode..."
            Push-Location $repoRoot
            try {
                $env:FAST_STARTUP = '1'
                $env:SKIP_MODEL_DOWNLOADS = '1'
                python -m uvicorn backend.backend:app --host $BACKEND_HOST --port $BACKEND_PORT $(if($BACKEND_RELOAD){'--reload'})
            } finally {
                Pop-Location
            }
            
        } catch {
            Write-Error "Server health check failed"
            # Surface any startup errors from the background job
            try {
                $jobOut = Receive-Job -Job $serverJob -Keep -ErrorAction SilentlyContinue
                if ($jobOut) { Write-Info ($jobOut | Out-String) }
            } catch {}
            Stop-Job $serverJob -ErrorAction SilentlyContinue
            Remove-Job $serverJob -ErrorAction SilentlyContinue
            return $false
        }
        
    } catch {
        Write-Error "Failed to start backend server: $($_.Exception.Message)"
        return $false
    }
}

# Show completion summary
function Show-CompletionSummary {
    param([string]$PluginDir)
    
    Write-Header "🎉 Setup Complete!"
    
    Write-ColorOutput "Plugin Location:" "Green"
    Write-Host "  $PluginDir"
    Write-Host ""
    
    Write-ColorOutput "Next Steps:" "Yellow"
    Write-Host "  1. Open Obsidian"
    Write-Host "  2. Go to Settings → Community plugins"
    Write-Host "  3. Turn OFF 'Safe mode'"
    Write-Host "  4. Click 'Refresh' to detect the plugin"
    Write-Host "  5. Enable 'AI Assistant' plugin"
    Write-Host "  6. Look for the 🧠 brain icon in the ribbon"
    Write-Host ""
    
    Write-ColorOutput "Backend Server:" "Cyan"
    Write-Host "  URL: http://$BACKEND_HOST`:$BACKEND_PORT"
    Write-Host "  Health: http://$BACKEND_HOST`:$BACKEND_PORT/health"
    Write-Host "  Start with: .\setup-plugin.ps1 -BackendOnly"
    Write-Host ""
    
    Write-ColorOutput "Troubleshooting:" "Magenta"
    Write-Host "  • Plugin not visible? Enable Community plugins in Obsidian"
    Write-Host "  • Connection errors? Start the backend server"
    Write-Host "  • Voice not working? Check browser microphone permissions"
    Write-Host ""
    
    Write-Success "Ready to use your AI Assistant in Obsidian!"
}

# Main execution
function Main {
    try {
        Write-Header "Obsidian AI Agent Setup"
        Write-Info "Setup Mode: $(if ($BackendOnly) { "Backend Only" } elseif ($PluginOnly) { "Plugin Only" } else { "Full Setup" })"
        
        # Check prerequisites
        if (-not (Test-Prerequisites)) {
            Write-Error "Prerequisites not met. Please resolve issues and try again."
            exit 1
        }
        
        $pluginDir = $null
        
        # Install plugin files (unless BackendOnly mode)
        if (-not $BackendOnly) {
            $vault = Get-VaultPath
            if (-not $vault) {
                Write-Error "Could not determine vault path"
                exit 1
            }
            
            $pluginDir = Install-PluginFiles -VaultPath $vault
            if (-not $pluginDir) {
                Write-Error "Plugin installation failed"
                exit 1
            }
        }
        
        # Start backend server (unless PluginOnly mode)
        if (-not $PluginOnly) {
            if (-not (Start-BackendServer)) {
                Write-Warning "Backend server startup failed or was interrupted"
                if ($pluginDir) {
                    Write-Info "Plugin files were installed successfully at: $pluginDir"
                    Write-Info "You can start the backend later with: .\setup-plugin.ps1 -BackendOnly"
                }
            }
        } else {
            # Show completion summary for plugin-only installation
            if ($pluginDir) {
                Show-CompletionSummary -PluginDir $pluginDir
            }
        }
        
    } catch {
        Write-Error "Setup failed: $($_.Exception.Message)"
        Write-Error "Stack trace: $($_.Exception.StackTrace)"
        exit 1
    }
}

# Execute main function
Main


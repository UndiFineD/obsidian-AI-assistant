#Requires -Version 5.1
<#
.SYNOPSIS
    Obsidian AI Assistant Plugin Setup Script
.DESCRIPTION
    Automates the complete setup process for the Obsidian AI Assistant plugin including:
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
    $currentDir = Get-Location
    $expectedFiles = @("backend", "plugin", "package.json", "README.md")
    $missingFiles = @()
    
    foreach ($file in $expectedFiles) {
        if (-not (Test-Path $file)) {
            $missingFiles += $file
        }
    }
    
    if ($missingFiles.Count -gt 0) {
        Write-Error "Missing expected files/directories: $($missingFiles -join ', ')"
        Write-Error "Please run this script from the obsidian-AI-assistant directory"
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
    
    $pluginDir = Join-Path $VaultPath ".obsidian\plugins\$PLUGIN_NAME"
    $sourceDir = "plugin"
    
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
        
        # Define essential plugin files
        # Copy plugin files
        $copiedCount = 0
        $totalSize = 0
        
        foreach ($file in $REQUIRED_PLUGIN_FILES) {
            $sourcePath = Join-Path $sourceDir $file
            $destPath = Join-Path $pluginDir $file
            
            if (Test-Path $sourcePath) {
                Copy-Item $sourcePath $destPath -Force
                $fileInfo = Get-Item $destPath
                $totalSize += $fileInfo.Length
                $copiedCount++
                Write-Info "Copied: $file ($([math]::Round($fileInfo.Length / 1024, 1)) KB)"
            } else {
                Write-Warning "Source file not found: $sourcePath"
            }
        }
        
        # Create setup instructions
        $readmeContent = @"
# Obsidian AI Assistant Plugin - Installation Complete

## 🎯 Plugin Successfully Installed
Installation Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Files Copied: $copiedCount
Total Size: $([math]::Round($totalSize / 1024, 1)) KB

## 🚀 Next Steps to Enable Plugin:

### 1. Enable Community Plugins in Obsidian
1. Open Obsidian
2. Go to Settings (⚙️) → Community plugins
3. Turn OFF "Safe mode" if it's enabled
4. Click "Refresh" to detect new plugins
5. Find "AI Assistant" in the installed plugins list
6. Toggle the switch to enable it

### 2. Backend Server Information
- Server URL: http://$BackendHost`:$BackendPort
- Status: Use the setup script to start the server
- Health Check: http://$BackendHost`:$BackendPort/health

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
        # Start server in background job for testing, or directly for production
        $serverJob = Start-Job -ScriptBlock {
            param($Host, $Port, $Reload)
            Set-Location $using:PWD
            python -m uvicorn backend.backend:app --host $Host --port $Port $(if($Reload){'--reload'})
        } -ArgumentList $BACKEND_HOST, $BACKEND_PORT, $BACKEND_RELOAD
        
        # Wait a moment for server to start
        Start-Sleep -Seconds $SERVER_START_TIMEOUT
        
        # Test server health
        try {
            $response = Invoke-RestMethod -Uri "http://$BACKEND_HOST`:$BACKEND_PORT/health" -TimeoutSec $HEALTH_CHECK_TIMEOUT
            Write-Success "Backend server started successfully"
            Write-Success "Health check: $($response.status)"
            
            # Stop the job since we just wanted to test startup
            Stop-Job $serverJob -ErrorAction SilentlyContinue
            Remove-Job $serverJob -ErrorAction SilentlyContinue
            
            # Now start interactively
            Write-Info "Starting server in interactive mode..."
            python -m uvicorn backend.backend:app --host $BACKEND_HOST --port $BACKEND_PORT $(if($BACKEND_RELOAD){'--reload'})
            
        } catch {
            Write-Error "Server health check failed"
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
    Write-Host "  URL: http://$BackendHost`:$BackendPort"
    Write-Host "  Health: http://$BackendHost`:$BackendPort/health"
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
        Write-Header "Obsidian AI Assistant Setup"
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
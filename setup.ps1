<#
.SYNOPSIS
Setup script for Obsidian AI Assistant project.
.DESCRIPTION
Sets up Python virtual environment, installs dependencies, optional Hugging Face login,
installs Node.js/npm locally for Obsidian plugin, and provides correct backend activation path.
#>

# ----- CONFIG -----
$venvDir = Join-Path $PSScriptRoot "venv"
$pythonExe = "python"  # or "python3"
$requirementsFile = Join-Path $PSScriptRoot "requirements.txt"
$nodeZipUrl = "https://nodejs.org/dist/v24.8.0/node-v24.8.0-win-x64.zip"
$nodeDir = Join-Path $PSScriptRoot "nodejs"
$obsidianPluginDir = Join-Path $PSScriptRoot "obsidian-plugin"
$backendFile = Join-Path $PSScriptRoot "backend\backend.py"

Write-Host "=== Obsidian AI Assistant Setup ===`n"

# ----- 1. Check Python -----
try {
    $pythonVersion = & $pythonExe --version 2>&1
    Write-Host "Detected Python version: $pythonVersion"
} catch {
    Write-Error "Python not found. Please install Python 3.11+ and ensure it's in your PATH."
    exit 1
}

# ----- 2. Create virtual environment -----
if (-Not (Test-Path $venvDir)) {
    Write-Host "Creating Python virtual environment..."
    & $pythonExe -m venv $venvDir
} else {
    Write-Host "Python virtual environment already exists."
}

$venvPython = Join-Path $venvDir "Scripts\python.exe"
$activateScript = Join-Path $venvDir "Scripts\Activate.ps1"

if (-Not (Test-Path $activateScript)) {
    Write-Error "Activate.ps1 not found. Virtual environment may not have been created correctly."
    exit 1
}

# ----- 3. Activate virtual environment -----
Write-Host "Activating virtual environment..."
. $activateScript

# ----- 4. Upgrade pip -----
Write-Host "Upgrading pip..."
& $venvPython -m pip install --upgrade pip

# ----- 5. Install Python dependencies -----
if (Test-Path $requirementsFile) {
    Write-Host "Installing dependencies from requirements.txt..."
    & $venvPython -m pip install -r $requirementsFile
} else {
    Write-Warning "requirements.txt not found. Installing fallback dependencies..."
    $fallbackDeps = @(
        "fastapi","uvicorn","torch","sentence-transformers","chromadb","llama-cpp-python",
		"gpt4all","requests","beautifulsoup4","PyPDF2","huggingface_hub","accelerate",
		"transformers","bitsandbytes","readability-lxml","hf_xet","huggingface_hub"
    )
    foreach ($dep in $fallbackDeps) {
        & $venvPython -m pip install $dep
    }
}

# ----- 6. Hugging Face login -----
$hfToken = Read-Host "Enter your Hugging Face token (leave blank to skip)"
if ($hfToken -ne "") {
    Write-Host "Logging into Hugging Face..."
    try {
        & hf auth login --token $hfToken
        Write-Host "✅ Hugging Face login successful"
    } catch {
        Write-Warning "Failed to login to Hugging Face. Check your token and internet connection."
    }
} else {
    Write-Host "Skipping Hugging Face login..."
}

# ----- 7. Install Node.js/npm locally -----
function Install-NodeLocal {
    param($zipUrl, $targetDir)

    if (Get-Command node -ErrorAction SilentlyContinue) {
        Write-Host "Node.js already installed. Skipping installation."
        return
    }

    Write-Host "Ensuring TLS 1.2 is used for downloads..."
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

    if (-Not (Test-Path $targetDir)) {
        New-Item -Path $targetDir -ItemType Directory -Force | Out-Null
    }

    $zipFile = Join-Path $env:TEMP "nodejs.zip"

    Write-Host "Downloading Node.js ZIP..."
    try {
        Invoke-WebRequest -Uri $zipUrl -OutFile $zipFile -UseBasicParsing -ErrorAction Stop
    } catch {
        throw "Failed to download Node.js ZIP: $_"
    }

    Write-Host "Extracting Node.js..."
    try {
        Expand-Archive -LiteralPath $zipFile -DestinationPath $targetDir -Force
    } catch {
        throw "Failed to extract Node.js ZIP: $_"
    } finally {
        Remove-Item $zipFile -Force
    }

    # Determine extracted folder
    $extractedNode = Get-ChildItem -Path $targetDir | Where-Object { $_.PSIsContainer } | Select-Object -First 1
    if (-Not $extractedNode) { $extractedNode = $targetDir }

    $nodeBin = $extractedNode.FullName
    $env:Path = "$nodeBin;$env:Path"

    # Verify node/npm
    if ((Get-Command node -ErrorAction SilentlyContinue) -and (Get-Command npm -ErrorAction SilentlyContinue)) {
        Write-Host "✅ Node.js and npm installed successfully (local)"
    } else {
        throw "Node.js/npm installation failed. Please install manually from https://nodejs.org/"
    }
}

try {
    Install-NodeLocal $nodeZipUrl $nodeDir
} catch {
    Write-Warning $_
}

# ----- 8. Obsidian plugin info -----
if ((Test-Path $obsidianPluginDir) -and (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "Obsidian plugin directory exists. To build plugin, run:"
    Write-Host "Push-Location $obsidianPluginDir; npm install; npm run build; Pop-Location"
}

# ----- 9. Backend activation info -----
if (Test-Path $backendFile) {
    Write-Host "`nTo activate backend manually, run:"
    Write-Host ". $activateScript; python $backendFile"
} else {
    Write-Warning "backend.py not found in ./backend. Update the path before running."
}

Write-Host "`n=== Setup Complete ==="

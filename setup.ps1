param(
    [string]$VaultPath
)

<#
.SYNOPSIS
Windows setup # ----- 4. Node.js dependencies removed -----
# Project now uses only Python dependenciesI Assistant
.DESCRIPTION
- Creates Python venv and installs Python deps
- Runs Python (pytest) tests
- Installs Obsidian (winget) if missing
- Installs/updates the plugin in the specified Obsidian vault
#>

Write-Host "=== Obsidian AI Assistant Setup (Windows) ===`n"

# ----- Resolve repo root -----
$RepoRoot = $PSScriptRoot
$PluginDir = Join-Path $RepoRoot "plugin"
$BackendDir = Join-Path $RepoRoot "backend"
$BackendEntry = Join-Path $BackendDir "backend.py"
$VenvDir = Join-Path $RepoRoot "venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"

# ----- 0. Node.js dependencies removed -----
# This project now uses only Python dependencies

# ----- 1. Ensure Python -----
$pythonExe = "python"
try {
    $null = & $pythonExe --version
} catch {
    Write-Error "Python not found. Install Python 3.11+ and re-run."
    exit 1
}

# ----- 2. Create and activate venv -----
if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating Python virtual environment..."
    & $pythonExe -m venv $VenvDir
}
if (-not (Test-Path $ActivateScript)) {
    Write-Error "Virtualenv activation script missing: $ActivateScript"
    exit 1
}
Write-Host "Activating virtual environment..."
. $ActivateScript
Write-Host "Upgrading pip..."
& $VenvPython -m pip install --upgrade pip

# ----- 3. Install Python dependencies -----
$Requirements = Join-Path $RepoRoot "requirements.txt"
if (Test-Path $Requirements) {
    Write-Host "Installing Python deps from requirements.txt..."
    & $VenvPython -m pip install -r $Requirements
} else {
    Write-Host "Installing baseline Python deps (no requirements.txt found)..."
    $deps = @(
    "fastapi","uvicorn","python-dotenv","requests","beautifulsoup4","readability-lxml","pypdf",
        "cryptography","vosk","sentence-transformers","chromadb","huggingface_hub","accelerate","transformers",
        "pydantic","pytest-asyncio"
    )
    foreach ($d in $deps) { & $VenvPython -m pip install $d }
}

# ----- 3.5 Ensure required directories exist -----
try {
    $dirs = @(
        (Join-Path $RepoRoot "backend\cache"),
        (Join-Path $RepoRoot "backend\models"),
        (Join-Path $RepoRoot "vector_db"),
        (Join-Path $RepoRoot "logs")
    )
    foreach ($d in $dirs) {
        if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
    }
    Write-Host "Ensured backend/cache, backend/models, vector_db, logs directories exist."
} catch {
    Write-Warning "Failed to create required directories: $($_.Exception.Message)"
}

# ----- 4. Node dependencies via package-lock (npm ci) -----
## Node.js and npm installation steps removed; only Python dependencies are installed

# ----- 5. Optional: Hugging Face login -----
if (-not $env:HUGGINGFACE_TOKEN) {
    $hfToken = Read-Host "Enter your Hugging Face token (leave blank to skip)"
    if ($hfToken) {
        $env:HUGGINGFACE_TOKEN = $hfToken
    }
}

# ----- 6. Run tests (non-blocking) -----
Write-Host "Running Python tests (pytest)..."
try {
    & $VenvPython -m pytest --maxfail=1 --durations=5
} catch { Write-Warning "Pytest reported failures. Review output above." }

# ----- 7. Ensure Obsidian is installed (winget) -----
if (-not (Get-Command obsidian -ErrorAction SilentlyContinue)) {
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "Attempting to install Obsidian via winget..."
        try { winget install --id Obsidian.Obsidian -e --source winget --accept-package-agreements --accept-source-agreements } catch { Write-Warning "Failed to install Obsidian via winget." }
    } else {
        Write-Warning "winget not available. Install Obsidian manually from https://obsidian.md/download"
    }
}

# ----- 8. Install plugin to vault -----
if (-not $VaultPath) {
    $VaultPath = Read-Host "Enter the full path to your Obsidian vault"
}
if ($VaultPath -and (Test-Path $VaultPath)) {
    $manifestPath = Join-Path $PluginDir "manifest.json"
    if (-not (Test-Path $manifestPath)) {
        Write-Warning "Plugin manifest not found at $manifestPath. Skipping plugin install."
    } else {
        try {
            $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
            $pluginId = $manifest.id
            if (-not $pluginId) { throw "manifest.json missing 'id' field" }
            $TargetDir = Join-Path (Join-Path $VaultPath ".obsidian\plugins") $pluginId
            New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
            Write-Host "Installing plugin '$pluginId' to $TargetDir ..."
            Copy-Item -Path (Join-Path $PluginDir "*") -Destination $TargetDir -Recurse -Force
            Write-Host "✅ Plugin installed. If this is a fresh install, enable it in Obsidian Settings → Community plugins."
            if (-not (Test-Path (Join-Path $TargetDir "main.js"))) {
                Write-Warning "main.js not found in plugin output."
            }
        } catch {
            Write-Warning "Failed to install plugin: $_"
        }
    }
} else {
    Write-Warning "Vault path not provided or not found; skipping plugin installation."
}

# ----- 9. Backend run hint -----
if (Test-Path $BackendEntry) {
    Write-Host "`nTo run backend:"
    Write-Host ". $ActivateScript; python `"$BackendEntry`""
}

Write-Host "`n=== Setup Complete ==="

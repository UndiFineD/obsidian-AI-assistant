# PowerShell script to create and activate Python 3.11 venv, then install requirements

# Check for Python 3.11
$python311 = Get-Command python3.11 -ErrorAction SilentlyContinue
if (-not $python311) {
    Write-Host "Python 3.11 not found. Please install Python 3.11 and try again."
    exit 1
}

# Create venv
python3.11 -m venv .venv
Write-Host "Virtual environment .venv created with Python 3.11."

# Activate venv
$activateScript = ".venv\\Scripts\\Activate.ps1"
if (Test-Path $activateScript) {
    Write-Host "Activating .venv..."
    & $activateScript
} else {
    Write-Host "Activation script not found. Please activate manually."
}

# Upgrade pip and install requirements
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "All requirements installed."

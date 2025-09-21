Write-Host "=== Obsidian LLM Assistant Setup (Windows) ==="

# --- 1. Create Python virtual environment ---
$envDir = "venv"
if (-not (Test-Path $envDir)) {
    Write-Host "[*] Creating Python virtual environment..."
    python -m venv $envDir
}

# --- 2. Activate virtual environment ---
& "$envDir\Scripts\Activate.ps1"

# --- 3. Upgrade pip ---
python -m pip install --upgrade pip

# --- 4. Install Python dependencies ---
Write-Host "[*] Installing Python dependencies..."
pip install fastapi uvicorn torch sentence-transformers chromadb llama-cpp-python gpt4all `
    requests beautifulsoup4 readability-lxml PyPDF2 `
    huggingface_hub accelerate transformers bitsandbytes python-dotenv

# --- 5. Detect GPU / CPU ---
Write-Host "[*] Detecting GPU availability..."
python - << EOF
import torch
if torch.cuda.is_available():
    print("✅ GPU detected. Using CUDA.")
else:
    print("⚠️ No GPU detected. Using CPU.")
EOF

# --- 6. Ask for Hugging Face token ---
$hfToken = Read-Host "Enter your Hugging Face token (leave blank to skip)"
if ($hfToken -ne "") {
    "HUGGINGFACE_TOKEN=$hfToken" | Out-File -Encoding utf8 .env
    $env:HUGGINGFACE_TOKEN = $hfToken
    Write-Host "✅ Hugging Face token saved to .env"
} else {
    Write-Host "⚠️ No Hugging Face token provided. Some models (e.g. LLaMA) may not be accessible."
}

# --- 7. Prepare directories ---
Write-Host "[*] Creating necessary directories..."
$dirs = @("cache", "vector_db", "vault", "models")
foreach ($d in $dirs) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d | Out-Null }
}

# --- 8. Build Obsidian plugin ---
$pluginDir = ".\plugin"
if (Test-Path $pluginDir) {
    Write-Host "[*] Building Obsidian plugin..."
    cd $pluginDir
    npm install
    npm run build
    cd ..
} else {
    Write-Host "⚠️ Plugin directory '$pluginDir' not found!"
}

Write-Host "=== Setup Complete ==="
Write-Host "Activate backend with:"
Write-Host "  & $envDir\Scripts\Activate.ps1; uvicorn backend:app --reload"

Write-Host "=== Obsidian LLM Assistant Setup (Windows) ==="

# --- 1. Create Python virtual environment ---
$envDir = "venv"
if (-not (Test-Path $envDir)) {
    Write-Host "Creating Python virtual environment..."
    python -m venv $envDir
}

# --- 2. Activate virtual environment ---
& "$envDir\Scripts\Activate.ps1"

# --- 3. Upgrade pip ---
python -m pip install --upgrade pip

# --- 4. Install Python dependencies ---
Write-Host "Installing Python dependencies..."
pip install fastapi uvicorn torch sentence-transformers chromadb llama-cpp-python gpt4all requests beautifulsoup4 readability-lxml PyPDF2

# --- 5. Detect GPU / CPU ---
python - << EOF
import torch
if torch.cuda.is_available():
    print("GPU detected. Using CUDA.")
else:
    print("No GPU detected. Using CPU.")
EOF

# --- 6. Download default models ---
$modelsDir = ".\models"
if (-not (Test-Path $modelsDir)) { New-Item -ItemType Directory -Path $modelsDir }

# LLaMA 7B Q4
$llamaModel = "$modelsDir\llama-7b-q4.bin"
if (-not (Test-Path $llamaModel)) {
    Write-Host "Downloading LLaMA 7B Q4 model..."
    Invoke-WebRequest -Uri "https://huggingface.co/NousResearch/LLaMA-2-7b-Q4/resolve/main/llama-7b-q4.bin" -OutFile $llamaModel
}

# GPT4All Lora
$gpt4allModel = "$modelsDir\gpt4all-lora.bin"
if (-not (Test-Path $gpt4allModel)) {
    Write-Host "Downloading GPT4All Lora model..."
    Invoke-WebRequest -Uri "https://huggingface.co/nomic-ai/gpt4all-lora/resolve/main/gpt4all-lora.bin" -OutFile $gpt4allModel
}

# --- 7. Build Obsidian plugin ---
$pluginDir = ".\plugin"
if (Test-Path $pluginDir) {
    Write-Host "Building Obsidian plugin..."
    cd $pluginDir
    npm install
    npm run build
    cd ..
} else {
    Write-Host "Plugin directory '$pluginDir' not found!"
}

Write-Host "=== Setup Complete ==="
Write-Host "Activate backend with: & $envDir\Scripts\Activate.ps1; python backend.py"

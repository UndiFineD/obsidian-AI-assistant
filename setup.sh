#!/bin/bash
set -e

echo "=== Obsidian LLM Assistant Setup (Linux/macOS) ==="

# --- 1. Create Python virtual environment ---
PYTHON_ENV_DIR="venv"
if [ ! -d "$PYTHON_ENV_DIR" ]; then
    echo "[*] Creating Python virtual environment..."
    python3 -m venv "$PYTHON_ENV_DIR"
fi

source "$PYTHON_ENV_DIR/bin/activate"

# --- 2. Upgrade pip ---
pip install --upgrade pip

# --- 3. Install Python dependencies ---
echo "[*] Installing Python dependencies..."
pip install fastapi uvicorn torch sentence-transformers chromadb llama-cpp-python gpt4all \
    requests beautifulsoup4 readability-lxml PyPDF2 \
    huggingface_hub accelerate transformers bitsandbytes python-dotenv

# --- 4. Detect GPU / CPU for PyTorch ---
echo "[*] Detecting GPU availability..."
python3 - << EOF
import torch
if torch.cuda.is_available():
    print("✅ GPU detected. Using CUDA.")
else:
    print("⚠️ No GPU detected. Using CPU.")
EOF

# --- 5. Ask for Hugging Face token ---
echo
read -p "Enter your Hugging Face token (leave blank to skip): " HF_TOKEN

if [ -n "$HF_TOKEN" ]; then
    echo "HUGGINGFACE_TOKEN=$HF_TOKEN" > .env
    export HUGGINGFACE_TOKEN="$HF_TOKEN"
    echo "✅ Hugging Face token saved to .env"
else
    echo "⚠️ No Hugging Face token provided. You may not be able to download gated models (e.g. LLaMA)."
fi

# --- 6. Prepare directories ---
echo "[*] Creating necessary directories..."
mkdir -p cache vector_db vault models

# --- 7. Build Obsidian plugin ---
PLUGIN_DIR="./plugin"
if [ -d "$PLUGIN_DIR" ]; then
    echo "[*] Building Obsidian plugin..."
    cd "$PLUGIN_DIR"
    npm install
    npm run build
    cd ..
else
    echo "⚠️ Plugin directory '$PLUGIN_DIR' not found!"
fi

echo "=== Setup Complete ==="
echo "Activate backend with:"
echo "  source $PYTHON_ENV_DIR/bin/activate && uvicorn backend:app --reload"

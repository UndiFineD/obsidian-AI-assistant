#!/bin/bash
set -e

echo "=== Obsidian LLM Assistant Setup (Linux/macOS) ==="

# --- 1. Create Python virtual environment ---
PYTHON_ENV_DIR="venv"
if [ ! -d "$PYTHON_ENV_DIR" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$PYTHON_ENV_DIR"
fi

source "$PYTHON_ENV_DIR/bin/activate"

# --- 2. Upgrade pip ---
pip install --upgrade pip

# --- 3. Install Python dependencies ---
echo "Installing Python dependencies..."
pip install fastapi uvicorn torch sentence-transformers chromadb llama-cpp-python gpt4all requests beautifulsoup4 readability-lxml PyPDF2

# --- 4. Detect GPU / CPU for PyTorch ---
echo "Detecting GPU availability..."
python3 - << EOF
import torch
if torch.cuda.is_available():
    print("GPU detected. Using CUDA.")
else:
    print("No GPU detected. Using CPU.")
EOF

# --- 5. Download default LLaMA / GPT4All models if missing ---
MODELS_DIR="./models"
mkdir -p $MODELS_DIR

# LLaMA 7B Q4
LLAMA_MODEL="$MODELS_DIR/llama-7b-q4.bin"
if [ ! -f "$LLAMA_MODEL" ]; then
    echo "Downloading LLaMA 7B Q4 model..."
    wget -O "$LLAMA_MODEL" "https://huggingface.co/NousResearch/LLaMA-2-7b-Q4/resolve/main/llama-7b-q4.bin"
fi

# GPT4All Lora
GPT4ALL_MODEL="$MODELS_DIR/gpt4all-lora.bin"
if [ ! -f "$GPT4ALL_MODEL" ]; then
    echo "Downloading GPT4All Lora model..."
    wget -O "$GPT4ALL_MODEL" "https://huggingface.co/nomic-ai/gpt4all-lora/resolve/main/gpt4all-lora.bin"
fi

# --- 6. Build Obsidian plugin ---
PLUGIN_DIR="./plugin"
if [ -d "$PLUGIN_DIR" ]; then
    echo "Building Obsidian plugin..."
    cd "$PLUGIN_DIR"
    npm install
    npm run build
    cd ..
else
    echo "Plugin directory '$PLUGIN_DIR' not found!"
fi

echo "=== Setup Complete ==="
echo "Activate backend with: source $PYTHON_ENV_DIR/bin/activate && python backend.py"

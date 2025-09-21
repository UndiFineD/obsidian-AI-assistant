#!/usr/bin/env bash
set -e  # exit on error
echo "=== Obsidian LLM Assistant Setup (Linux/macOS) ==="

# --- 1. Create Python virtual environment ---
ENV_DIR="venv"
if [ ! -d "$ENV_DIR" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$ENV_DIR"
fi

# --- 2. Activate virtual environment ---
source "$ENV_DIR/bin/activate"

# --- 3. Upgrade pip ---
pip install --upgrade pip

# --- 4. Install Python dependencies ---
echo "Installing Python dependencies..."
pip install fastapi uvicorn torch sentence-transformers chromadb llama-cpp-python gpt4all requests beautifulsoup4 readability-lxml PyPDF2 huggingface_hub accelerate transformers bitsandbytes

# --- 5. Detect GPU / CPU ---
python3 << EOF
import torch
if torch.cuda.is_available():
    print("GPU detected. Using CUDA.")
else:
    print("No GPU detected. Using CPU.")
EOF

# --- 6. Ask for Hugging Face token ---
read -p "Enter your Hugging Face token (leave blank to skip): " HF_TOKEN
if [ -n "$HF_TOKEN" ]; then
    ENV_FILE=".env"
    if [ ! -f "$ENV_FILE" ]; then
        touch "$ENV_FILE"
    fi
    echo "HF_TOKEN=$HF_TOKEN" > "$ENV_FILE"
    echo "Saved Hugging Face token to $ENV_FILE"
fi

# --- 7. Download default models ---
MODELS_DIR="./models"
mkdir -p "$MODELS_DIR"

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

# --- 8. Build Obsidian plugin ---
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
echo "Activate backend with: source $ENV_DIR/bin/activate && python backend.py"

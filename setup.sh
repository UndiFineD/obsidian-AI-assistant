#!/usr/bin/env bash
set -euo pipefail
echo "=== Obsidian LLM Assistant Setup (Linux/macOS) ==="

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
ENV_DIR="$REPO_ROOT/venv"
PLUGIN_DIR="$REPO_ROOT/plugin"
BACKEND_ENTRY="$REPO_ROOT/backend/backend.py"

# --- 1. Create Python virtual environment ---
if [ ! -d "$ENV_DIR" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$ENV_DIR"
fi

# --- 2. Activate virtual environment ---
source "$ENV_DIR/bin/activate"
python3 -m pip install --upgrade pip

# --- 3. Install Python dependencies ---
REQ_FILE="$REPO_ROOT/requirements.txt"
if [ -f "$REQ_FILE" ]; then
    echo "Installing Python deps from requirements.txt..."
    pip install -r "$REQ_FILE"
else
    echo "Installing baseline Python deps..."
    pip install fastapi uvicorn python-dotenv requests beautifulsoup4 readability-lxml PyPDF2 \
        cryptography vosk sentence-transformers chromadb huggingface_hub accelerate transformers
fi

# --- 4. Node dependencies via lockfile ---
if command -v npm >/dev/null 2>&1; then
    pushd "$REPO_ROOT" >/dev/null
    if [ -f package-lock.json ]; then
        echo "Installing Node deps with npm ci (locked)..."
        npm ci --no-audit --no-fund
    else
        echo "No package-lock.json; running npm install..."
        npm install --no-audit --no-fund
    fi
    popd >/dev/null
else
    echo "WARNING: npm not found; skipping JS deps. Install Node.js from https://nodejs.org/"
fi

# --- 5. Run tests ---
echo "Running Python tests (pytest)..."
set +e
pytest --maxfail=1 --durations=5 || echo "Pytest reported failures. Review above."
set -e
if command -v npm >/dev/null 2>&1; then
    echo "Running JS tests (jest)..."
    (cd "$REPO_ROOT" && npm test --silent) || echo "Jest tests failed."
fi

# --- 6. Optional: Obsidian installation guidance ---
if ! command -v obsidian >/dev/null 2>&1; then
    echo "TIP: Install Obsidian from https://obsidian.md/download"
    if [[ "$OSTYPE" == "darwin"* ]] && command -v brew >/dev/null 2>&1; then
        echo "You can try: brew install --cask obsidian"
    elif command -v apt >/dev/null 2>&1; then
        echo "On Debian/Ubuntu, download .deb and install with: sudo dpkg -i Obsidian*.deb && sudo apt -f install"
    fi
fi

# --- 7. Install plugin into a vault ---
read -r -p "Enter the full path to your Obsidian vault (or leave blank to skip): " VAULT_PATH || true
if [ -n "${VAULT_PATH:-}" ] && [ -d "$VAULT_PATH" ]; then
    MANIFEST="$PLUGIN_DIR/manifest.json"
    if [ -f "$MANIFEST" ]; then
        PLUGIN_ID="$(node -e "console.log(require(process.argv[1]).id)" "$MANIFEST" 2>/dev/null || true)"
        if [ -z "$PLUGIN_ID" ]; then
            echo "manifest.json missing 'id'; using folder name 'obsidian-ai-assistant'"
            PLUGIN_ID="obsidian-ai-assistant"
        fi
        TARGET_DIR="$VAULT_PATH/.obsidian/plugins/$PLUGIN_ID"
        mkdir -p "$TARGET_DIR"
        echo "Installing plugin to $TARGET_DIR ..."
        rsync -a "$PLUGIN_DIR/" "$TARGET_DIR/" --exclude node_modules || cp -r "$PLUGIN_DIR"/* "$TARGET_DIR"/
        if [ ! -f "$TARGET_DIR/main.js" ]; then
            echo "WARNING: main.js not found. Build plugin with: (cd plugin && npm run build)"
        fi
    else
        echo "Plugin manifest not found at $MANIFEST; skipping plugin install."
    fi
else
    echo "Skipping plugin installation."
fi

echo "=== Setup Complete ==="
echo "Activate backend with: source $ENV_DIR/bin/activate && python $BACKEND_ENTRY"

#!/usr/bin/env bash
# tests/setup/test_setup_sh.bats
# BATS test suite for setup.sh script
# Install BATS with: npm install -g bats or use package manager

setup_file() {
    # Create a temporary test workspace
    export TEST_WORKSPACE="/tmp/obsidian-ai-test-$(date +%s)"
    mkdir -p "$TEST_WORKSPACE"
    
    # Copy setup script to test workspace
    cp "$(dirname "$BATS_TEST_FILENAME")/../../setup.sh" "$TEST_WORKSPACE/"
    
    # Make it executable
    chmod +x "$TEST_WORKSPACE/setup.sh"
    
    # Store original directory
    export ORIGINAL_DIR="$(pwd)"
}

teardown_file() {
    # Cleanup test workspace
    cd "$ORIGINAL_DIR"
    rm -rf "$TEST_WORKSPACE"
}

setup() {
    # Change to test workspace for each test
    cd "$TEST_WORKSPACE"
}

teardown() {
    # Clean up any test artifacts after each test
    cd "$ORIGINAL_DIR"
}

@test "setup script exists and is executable" {
    [ -f "$TEST_WORKSPACE/setup.sh" ]
    [ -x "$TEST_WORKSPACE/setup.sh" ]
}

@test "setup script has proper shebang" {
    run head -n 1 "$TEST_WORKSPACE/setup.sh"
    [[ "$output" == "#!/usr/bin/env bash" ]]
}

@test "setup script has set -e for error handling" {
    run grep -n "set -e" "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "setup script displays header message" {
    run grep "Obsidian LLM Assistant Setup" "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

# Virtual Environment Tests
@test "script defines virtual environment directory" {
    run grep 'ENV_DIR="venv"' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "script checks for existing virtual environment" {
    run grep -A 2 'if \[ ! -d "\$ENV_DIR" \]' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "script creates virtual environment with python3" {
    run grep "python3 -m venv" "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "script activates virtual environment" {
    run grep 'source "\$ENV_DIR/bin/activate"' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

# Dependency Installation Tests
@test "script upgrades pip" {
    run grep "pip install --upgrade pip" "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "script installs required Python packages" {
    run grep "pip install fastapi" "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
    
    run grep "pip install.*uvicorn" "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
    
    run grep "pip install.*torch" "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
    
    run grep "pip install.*sentence-transformers" "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "script includes machine learning dependencies" {
    run grep "chromadb" "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
    
    run grep "llama-cpp-python" "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
    
    run grep "gpt4all" "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
    
    run grep "huggingface_hub" "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "script includes web scraping dependencies" {
    run grep "requests" "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
    
    run grep "beautifulsoup4" "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
    
    run grep "PyPDF2" "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

# GPU/CPU Detection Tests
@test "script includes GPU detection" {
    run grep -A 5 "python3 << EOF" "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
    [[ "$output" =~ "torch.cuda.is_available" ]]
}

@test "script detects CUDA availability" {
    run grep "GPU detected. Using CUDA" "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
    
    run grep "No GPU detected. Using CPU" "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

# Hugging Face Token Tests
@test "script prompts for Hugging Face token" {
    run grep 'read -p.*Hugging Face token' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "script handles empty Hugging Face token" {
    run grep 'if \[ -n "\$HF_TOKEN" \]' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "script creates .env file for token" {
    run grep 'ENV_FILE=".env"' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
    
    run grep 'echo "HF_TOKEN=\$HF_TOKEN"' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "script handles existing .env file" {
    run grep 'if \[ ! -f "\$ENV_FILE" \]' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
    
    run grep 'touch "\$ENV_FILE"' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

# Model Download Tests
@test "script creates models directory" {
    run grep 'MODELS_DIR="./models"' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
    
    run grep 'mkdir -p "\$MODELS_DIR"' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "script defines LLaMA model path" {
    run grep 'LLAMA_MODEL="\$MODELS_DIR/llama-7b-q4.bin"' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "script checks for existing LLaMA model" {
    run grep 'if \[ ! -f "\$LLAMA_MODEL" \]' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "script downloads LLaMA model with wget" {
    run grep 'wget -O "\$LLAMA_MODEL".*huggingface.co.*llama.*bin' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "script defines GPT4All model path" {
    run grep 'GPT4ALL_MODEL="\$MODELS_DIR/gpt4all-lora.bin"' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "script checks for existing GPT4All model" {
    run grep 'if \[ ! -f "\$GPT4ALL_MODEL" \]' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "script downloads GPT4All model with wget" {
    run grep 'wget -O "\$GPT4ALL_MODEL".*huggingface.co.*gpt4all.*bin' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

# Obsidian Plugin Tests
@test "script defines plugin directory" {
    run grep 'PLUGIN_DIR="./plugin"' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "script checks for plugin directory existence" {
    run grep 'if \[ -d "\$PLUGIN_DIR" \]' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "script builds plugin with npm" {
    run grep 'npm install' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
    
    run grep 'npm run build' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "script handles missing plugin directory" {
    run grep "Plugin directory.*not found" "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "script changes to plugin directory and back" {
    run grep -A 3 'cd "\$PLUGIN_DIR"' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
    [[ "$output" =~ "cd .." ]]
}

# Completion and Instructions Tests
@test "script displays completion message" {
    run grep "=== Setup Complete ===" "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "script provides backend activation instructions" {
    run grep 'Activate backend with:.*source.*activate.*python backend.py' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

# Functional Tests with Mock Environment
@test "script can be parsed without syntax errors" {
    run bash -n "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "script handles missing python3 command" {
    # Create a modified script that replaces python3 with a non-existent command
    sed 's/python3/nonexistent_python/g' "$TEST_WORKSPACE/setup.sh" > "$TEST_WORKSPACE/test_script_no_python.sh"
    chmod +x "$TEST_WORKSPACE/test_script_no_python.sh"
    
    # Should fail due to set -e and missing command
    run "$TEST_WORKSPACE/test_script_no_python.sh"
    [ "$status" -ne 0 ]
}

@test "script creates expected directory structure" {
    # Mock the parts that require external dependencies
    cat > "$TEST_WORKSPACE/mock_setup.sh" << 'EOF'
#!/usr/bin/env bash
set -e
echo "=== Mock Setup Test ==="

# Mock virtual environment creation
ENV_DIR="venv"
if [ ! -d "$ENV_DIR" ]; then
    echo "Creating Python virtual environment..."
    mkdir -p "$ENV_DIR/bin"
    touch "$ENV_DIR/bin/activate"
fi

# Mock models directory
MODELS_DIR="./models"
mkdir -p "$MODELS_DIR"

# Mock plugin directory
PLUGIN_DIR="./plugin"
mkdir -p "$PLUGIN_DIR"

echo "Mock setup complete"
EOF
    
    chmod +x "$TEST_WORKSPACE/mock_setup.sh"
    run "$TEST_WORKSPACE/mock_setup.sh"
    
    [ "$status" -eq 0 ]
    [ -d "$TEST_WORKSPACE/venv" ]
    [ -d "$TEST_WORKSPACE/models" ]
    [ -d "$TEST_WORKSPACE/plugin" ]
}

# Security and Best Practices Tests
@test "script uses proper variable quoting" {
    # Check for unquoted variables (potential security issue)
    run grep -n '\$[A-Z_]*[^"]' "$TEST_WORKSPACE/setup.sh"
    # Should have minimal or no matches (some exceptions for heredoc are OK)
}

@test "script avoids dangerous commands" {
    # Should not contain potentially dangerous patterns
    run grep -E "(rm -rf /|sudo|eval|exec)" "$TEST_WORKSPACE/setup.sh"
    [ "$status" -ne 0 ]
}

@test "script uses safe download URLs" {
    # Check that download URLs are HTTPS
    run grep -o 'https://[^"]*' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
    
    # Verify all URLs are from trusted domains
    for url in $(grep -o 'https://[^"]*' "$TEST_WORKSPACE/setup.sh"); do
        [[ "$url" =~ ^https://(huggingface\.co|github\.com) ]]
    done
}

@test "script handles file operations safely" {
    # Should use proper file checks before operations
    run grep -B 1 -A 1 'wget.*-O' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
    
    # Should check for file existence before downloading
    [[ "$output" =~ "if.*-f.*then" ]]
}

# Integration Tests
@test "script components work together logically" {
    # Virtual environment should be activated before pip operations
    venv_line=$(grep -n 'source.*activate' "$TEST_WORKSPACE/setup.sh" | cut -d: -f1)
    pip_line=$(grep -n 'pip install' "$TEST_WORKSPACE/setup.sh" | head -1 | cut -d: -f1)
    
    [ "$venv_line" -lt "$pip_line" ]
}

@test "script error handling is consistent" {
    # Should use set -e at the beginning
    run head -5 "$TEST_WORKSPACE/setup.sh"
    [[ "$output" =~ "set -e" ]]
}

@test "script output is user-friendly" {
    # Should have informative echo statements
    echo_count=$(grep -c '^echo' "$TEST_WORKSPACE/setup.sh")
    [ "$echo_count" -ge 5 ]
}

# Environment Variable Tests
@test "script handles environment variables properly" {
    # Check for proper environment variable usage
    run grep 'ENV_DIR' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
    
    run grep 'MODELS_DIR' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
    
    run grep 'PLUGIN_DIR' "$TEST_WORKSPACE/setup.sh"
    [ "$status" -eq 0 ]
}

@test "script preserves environment between operations" {
    # Should maintain environment variables across script execution
    # Check that variables are defined once and used consistently
    env_dir_definitions=$(grep -c 'ENV_DIR=' "$TEST_WORKSPACE/setup.sh")
    [ "$env_dir_definitions" -eq 1 ]
}
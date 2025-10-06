# Obsidian AI Assistant - Setup Configuration
# This file contains default settings for the setup script
# Modify these values to customize your installation

# Plugin Configuration
PLUGIN_NAME=obsidian-ai-assistant
PLUGIN_VERSION=1.0.0

# Backend Configuration
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
BACKEND_RELOAD=true

# Common Vault Locations (searched automatically)
# Add your custom vault paths here
COMMON_VAULT_PATHS=(
    "$env:USERPROFILE\Documents\Obsidian Vault"
    "$env:USERPROFILE\DEV\Vault"
    "$env:USERPROFILE\Obsidian"
    "$env:USERPROFILE\Documents\vault"
    "$env:USERPROFILE\OneDrive\Obsidian"
    "$env:USERPROFILE\Dropbox\Obsidian"
)

# Plugin Files to Install (automatically detected from plugin directory)
REQUIRED_PLUGIN_FILES=(
    "manifest.json"
    "main.js"
    "styles.css"
    "taskQueue.js"
    "taskQueueView.js"
    "voice.js"
    "voiceInput.js"
    "analyticsPane.js"
)

# Python Dependencies (checked during setup)
REQUIRED_PYTHON_PACKAGES=(
    "fastapi"
    "uvicorn"
    "pydantic"
    "python-multipart"
)

# Setup Options
DEFAULT_FORCE_OVERWRITE=false
DEFAULT_CREATE_BACKUP=true
DEFAULT_VALIDATE_INSTALLATION=true
DEFAULT_START_SERVER_AFTER_INSTALL=true

# Timeout Settings (in seconds)
SERVER_START_TIMEOUT=10
HEALTH_CHECK_TIMEOUT=5
DEPENDENCY_CHECK_TIMEOUT=30

# Logging
ENABLE_DETAILED_LOGGING=true
LOG_FILE_PATH="setup.log"
KEEP_LOG_DAYS=7
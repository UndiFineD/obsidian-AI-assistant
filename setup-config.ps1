# Obsidian AI Agent - Setup Configuration
# This file contains default settings for the setup script
# Modify these values to customize your installation
# Note: Variables defined here are intended to be sourced by other PowerShell scripts

# Plugin Files to Install (automatically detected from plugin directory)

# Logging
# $ENABLE_DETAILED_LOGGING = $true
# $LOG_FILE_PATH = "setup.log"
# $KEEP_LOG_DAYS = 7

# Backend server configuration (defaults)
if (-not $global:SERVER_START_TIMEOUT) { $global:SERVER_START_TIMEOUT = 3 }
if (-not $global:HEALTH_CHECK_TIMEOUT) { $global:HEALTH_CHECK_TIMEOUT = 5 }
if (-not $global:BACKEND_HOST) { $global:BACKEND_HOST = "127.0.0.1" }
if (-not $global:BACKEND_PORT) { $global:BACKEND_PORT = 8000 }
if (-not $global:BACKEND_RELOAD) { $global:BACKEND_RELOAD = $false }

# Plugin configuration
# Must match manifest.json "id": "obsidian-ai-agent"
if (-not $global:PLUGIN_NAME) { $global:PLUGIN_NAME = "obsidian-ai-agent" }


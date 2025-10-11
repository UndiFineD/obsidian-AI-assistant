# Obsidian AI Assistant - Setup Configuration
# This file contains default settings for the setup script
# Modify these values to customize your installation
# Note: Variables defined here are intended to be sourced by other PowerShell scripts

# Plugin Files to Install (automatically detected from plugin directory)

# Logging
# $ENABLE_DETAILED_LOGGING = $true
# $LOG_FILE_PATH = "setup.log"
# $KEEP_LOG_DAYS = 7

# Backend server configuration (defaults)
$global:SERVER_START_TIMEOUT = 3           # Seconds to wait for backend server to start
$global:HEALTH_CHECK_TIMEOUT = 5           # Seconds to wait for health check response
$global:BACKEND_HOST = "127.0.0.1"         # Host for backend server
$global:BACKEND_PORT = 8000                # Port for backend server
$global:BACKEND_RELOAD = $false            # Enable auto-reload for backend server

# Plugin configuration
$global:PLUGIN_NAME = "AI Assistant"       # Name of the plugin directory
$global:REQUIRED_PLUGIN_FILES = @(
    # Core
    "main.js",
    "manifest.json",
    "styles.css",
    # Views and client
    "rightPane.js",
    "backendClient.js",
    # Optional features (present in repo; safe to copy if exist)
    "voice.js",
    "voiceInput.js",
    "taskQueue.js",
    "taskQueueView.js",
    "analyticsPane.js",
    # Enterprise (loaded conditionally in try/catch)
    "enterpriseAuth.js",
    "enterpriseConfig.js",
    "adminDashboard.js"
)                                    # List of plugin files to copy if present

# Backend server configuration
$global:SERVER_START_TIMEOUT = 3
$global:HEALTH_CHECK_TIMEOUT = 5
$global:BACKEND_HOST = "127.0.0.1"
$global:BACKEND_PORT = 8000
$global:BACKEND_RELOAD = $false

# Plugin configuration
$global:PLUGIN_NAME = "AI Assistant"
$global:REQUIRED_PLUGIN_FILES = @(
    "main.js",
    "manifest.json",
    "styles.css"
)

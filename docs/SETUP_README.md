# 🚀 Obsidian AI Assistant - Complete Setup Guide

This guide provides comprehensive setup instructions for the Obsidian AI Assistant, including automated scripts, manual installation, and advanced configuration options.

## 🎯 Quick Start Options

### Option A: Automated Setup (Recommended)

**Windows:**

```powershell
# Run the main setup script
./setup.ps1
```

**Linux/macOS:**

```bash
# Run the cross-platform setup script
bash setup.sh
```

### Option B: Manual Step-by-Step Setup

For users who prefer full control over the installation process.

## 📋 Setup Components

### **Core Setup Scripts**

#### `setup.ps1` / `setup.sh` - Primary Installation

##### Comprehensive setup script for complete automation

#### What it does

- ✅ Creates Python virtual environment with all dependencies
- ✅ Installs AI models (GPT4All, LLaMA, embedding models)
- ✅ Sets up ChromaDB vector database
- ✅ Configures FastAPI backend server
- ✅ Installs and validates Obsidian plugin files
- ✅ Performs comprehensive system testing (498 tests)
- ✅ Provides post-installation validation

### **Modern Installation Methods**

#### Method 1: Full Automated Setup

```powershell
# Windows - Complete environment setup
./setup.ps1

# This creates everything you need:
# - Python virtual environment
# - AI model downloads (GPT4All, embeddings)
# - FastAPI backend server
# - Obsidian plugin installation
# - Comprehensive testing validation (458 tests)
```

#### Method 2: Advanced Model Support (Optional)

```bash
# Install llama.cpp for advanced model management
# Windows
winget install llama.cpp

# macOS
brew install llama.cpp

# Or manual download from: https://github.com/ggml-org/llama.cpp/releases
```

#### Method 3: Manual Component Installation

```bash
# 1. Python environment setup
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\Activate.ps1  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Backend server
cd backend
python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload
```

### `setup-plugin.bat` - Simple Launcher

#### Easy-to-use batch file for double-click execution

**Features:**

- 🖱️ Double-click to run
- 📋 Menu-driven interface
- ⚡ Quick setup options
- 🔧 Advanced parameter input

**Usage:**

1. Double-click `setup-plugin.bat`
2. Choose your setup option (1-4)
3. Follow the prompts

### `setup-config.ps1` - Configuration File

#### Customizable settings for the setup process

**Contains:**

- Default vault locations
- Backend server configuration
- Plugin file specifications
- Timeout and retry settings
- Logging configuration

## 🎯 Quick Start Guide

### For Beginners (Recommended)

1. **Double-click** `setup-plugin.bat`
2. **Choose option 1** (Full Setup)
3. **Select your vault** from the list or enter custom path
4. **Wait for completion** - the script handles everything!

### For Advanced Users

```powershell
# Run with specific parameters
.\setup-plugin.ps1 -VaultPath "C:\MyVault" -Force

# Plugin-only installation
.\setup-plugin.ps1 -PluginOnly -VaultPath "C:\MyVault"

# Backend-only startup
.\setup-plugin.ps1 -BackendOnly
```

## 📊 What the Setup Does

### Step 1: Prerequisites Check

- ✅ PowerShell 5.1+ availability
- ✅ Python installation and version
- ✅ Required files and directories
- ✅ Backend dependencies (FastAPI, Uvicorn)

### Step 2: Vault Detection

- 🔍 Scans common Obsidian vault locations
- 📂 Interactive vault selection menu
- ✏️ Custom path input option
- ✅ Vault validation and confirmation

### Step 3: Plugin Installation

- 📁 Creates `.obsidian/plugins/obsidian-ai-assistant/` directory
- 📄 Copies 8 essential plugin files (25+ KB total)
- 🔍 Verifies file integrity and sizes
- 📋 Creates setup completion documentation

### Step 4: Backend Server

- 🔧 Validates Python dependencies
- 🌐 Starts FastAPI server on `http://127.0.0.1:8000`
- ❤️ Performs health check validation
- 📊 Displays server status and URLs

## 📁 Files Installed

The setup script installs these files to your vault:

```text
.obsidian/plugins/obsidian-ai-assistant/
├── manifest.json          (306 bytes)   - Plugin metadata
├── main.js                (7.4 KB)      - Core plugin logic
├── styles.css             (3.0 KB)      - Plugin styling
├── taskQueue.js           (3.4 KB)      - Task management
├── taskQueueView.js       (3.1 KB)      - Task UI components
├── voice.js               (1.3 KB)      - Voice processing
├── voiceInput.js          (902 bytes)   - Voice input handling
├── analyticsPane.js       (2.9 KB)      - Analytics dashboard
└── SETUP_COMPLETE.md                    - Installation summary
```

## 🔧 Configuration Options

### Backend Server Settings

```powershell
# Default: http://127.0.0.1:8000
$BackendHost = "127.0.0.1"
$BackendPort = 8000
```

### Common Vault Locations

The script automatically searches these locations:

- `%USERPROFILE%\Documents\Obsidian Vault`
- `%USERPROFILE%\DEV\Vault`
- `%USERPROFILE%\Obsidian`
- `%USERPROFILE%\Documents\vault`

## 🆘 Troubleshooting

### Script Won't Run

```powershell
# Check execution policy
Get-ExecutionPolicy

# If restricted, temporarily allow:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run with bypass:
powershell -ExecutionPolicy Bypass -File setup-plugin.ps1
```

### Python Not Found

```bash
# Install Python 3.8+ from python.org
# Or use chocolatey:
choco install python

# Verify installation:
python --version
```

### Missing Dependencies

```bash
# Install required packages:
pip install fastapi uvicorn python-multipart
```

### Plugin Not Visible in Obsidian

1. Open Obsidian Settings
2. Go to Community Plugins
3. Turn OFF "Safe mode"
4. Click "Refresh"
5. Enable "AI Assistant" plugin

### Backend Connection Issues

- ✅ Ensure backend server is running
- ✅ Check firewall settings
- ✅ Verify port 8000 is not blocked
- ✅ Test health endpoint: `http://127.0.0.1:8000/health`
- 🪟 Windows: If you see WinError 10013 when starting Uvicorn on port 8000, try a different port (e.g., 8001), remove `--reload`, check conflicts with `netstat -ano | findstr :8000`, or run PowerShell as Administrator.

## 🔄 Re-running Setup

### Update Plugin Files

```powershell
# Force overwrite existing installation
.\setup-plugin.ps1 -PluginOnly -Force
```

### Restart Backend Server

```powershell
# Backend only mode
.\setup-plugin.ps1 -BackendOnly
```

### Complete Reinstallation

```powershell
# Full reinstall with force overwrite
.\setup-plugin.ps1 -Force
```

## 📝 Logs and Output

### Setup Logs

- Colorized console output with status indicators
- Detailed error messages and stack traces
- File operation confirmations and sizes
- Server startup and health check results

### Generated Files

- `SETUP_COMPLETE.md` - Installation summary in plugin directory
- Setup logs with timestamps and operation details

## 🎉 After Setup

### Enable Plugin in Obsidian

1. Open Obsidian
2. Settings → Community Plugins
3. Turn OFF "Safe mode"
4. Click "Refresh"
5. Enable "AI Assistant"
6. Look for 🧠 brain icon in ribbon

### Test the Plugin

1. Click the brain icon (🧠)
2. Ask a question
3. Check task queue in right panel
4. Try voice input (if supported)

### Backend Server Management

```powershell
# Start server manually
python -m uvicorn backend.backend:app --host 127.0.0.1 --port 8000 --reload

# Test health endpoint
Invoke-RestMethod http://127.0.0.1:8000/health
```

---

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the setup logs for error details
3. Verify all prerequisites are met
4. Try running setup with `-Force` parameter

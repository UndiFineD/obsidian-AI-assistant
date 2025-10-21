# WSL Debian Setup Guide - October 2025

**Created**: October 21, 2025  
**Purpose**: Post-installation setup for WSL Debian with Obsidian AI Assistant development environment  
**Status**: Ready for use after system reboot

## Prerequisites

✅ WSL 2 installed (version 2.6.1+)  
✅ Debian distribution queued  
✅ System reboot completed  
✅ Administrator privileges available

## Initial Setup After Reboot

### Step 1: Launch WSL Debian

```powershell
# From PowerShell
wsl -d Debian
```

Or simply:
```powershell
wsl
```

### Step 2: First-Time Configuration

When Debian launches for the first time:

1. **Create Username**
   ```
   Enter new UNIX username: kdejo
   ```

2. **Create Password**
   ```
   New password: [enter secure password]
   Retype new password: [confirm password]
   ```

3. **Wait for Initialization**
   - System will complete setup (~2-3 minutes)
   - You'll see the bash prompt: `kdejo@hostname:~$`

## Essential Setup Commands

Run these commands in WSL Debian after first login:

### Step 3: Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
```

### Step 4: Install Development Tools

```bash
# Essential build tools
sudo apt install -y build-essential git curl wget nano vim

# Git configuration
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Step 5: Install Python 3.11

```bash
# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Verify installation
python3 --version
pip3 --version

# Create symlink for 'python' command
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1
```

### Step 6: Install Node.js (Optional)

```bash
# Install Node.js and npm
sudo apt install -y nodejs npm

# Verify installation
node --version
npm --version
```

### Step 7: Install Docker CLI (Optional)

```bash
# Install Docker CLI (without Docker daemon)
sudo apt install -y docker.io

# Add user to docker group (optional)
sudo usermod -aG docker $USER
```

## Accessing Obsidian AI Assistant Project

### Step 8: Navigate to Project

```bash
# Access Windows files from WSL
cd /mnt/c/Users/kdejo/DEV/obsidian-llm-assistant/obsidian-AI-assistant

# Or create a convenient symlink
mkdir -p ~/workspace
ln -s /mnt/c/Users/kdejo/DEV/obsidian-llm-assistant/obsidian-AI-assistant ~/workspace/obsidian-ai

# Then access it simply as:
cd ~/workspace/obsidian-ai
```

### Step 9: Set Up Python Virtual Environment

```bash
# Navigate to project
cd ~/workspace/obsidian-ai

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install project dependencies
pip install -r requirements.txt
```

## Running the Backend

### Step 10: Start Backend Server

```bash
# From project directory with venv activated
cd ~/workspace/obsidian-ai/agent

# Start uvicorn with hot reload
python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload
```

### Step 11: Verify Backend Health

From another WSL terminal or Windows PowerShell:

```bash
# Check health endpoint
curl http://localhost:8000/health

# Or from PowerShell:
Invoke-WebRequest http://localhost:8000/health

# View API docs
# Open browser to: http://localhost:8000/docs
```

## Git Integration

### Step 12: Clone/Update Repository

```bash
# Navigate to workspace
cd ~/workspace/obsidian-ai

# Check git status
git status

# Pull latest changes
git pull origin main

# Create new branch for development
git checkout -b feature/my-feature

# Commit and push
git add .
git commit -m "feat: description"
git push origin feature/my-feature
```

## Running Tests

### Step 13: Execute Test Suite

```bash
# Activate virtual environment first
source ~/workspace/obsidian-ai/venv/bin/activate

# Run all tests
pytest tests/ -v

# Run backend tests only
pytest tests/backend/ -v

# Run with coverage
pytest --cov=agent --cov-report=html tests/

# Run specific test file
pytest tests/backend/test_embeddings.py -v
```

## Code Quality Tools

### Step 14: Validate Code Quality

```bash
# Activate venv
source ~/workspace/obsidian-ai/venv/bin/activate

# Run linter
ruff check agent/

# Security scan
bandit -r agent/

# Type checking
mypy agent/ --ignore-missing-imports

# Format check (dry run)
black --check agent/

# Format code
black agent/
```

## Advanced Setup

### Step 15: Configure bash Profile (Optional)

Create `~/.bashrc` additions:

```bash
# Add to ~/.bashrc
cat >> ~/.bashrc << 'EOF'

# Obsidian AI Assistant aliases
alias ai-workspace="cd ~/workspace/obsidian-ai"
alias ai-venv="source ~/workspace/obsidian-ai/venv/bin/activate"
alias ai-backend="cd ~/workspace/obsidian-ai/agent && python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload"
alias ai-tests="pytest ~/workspace/obsidian-ai/tests/ -v"
alias ai-quality="cd ~/workspace/obsidian-ai && ruff check agent/ && bandit -r agent/"

EOF

# Reload bash configuration
source ~/.bashrc
```

Then you can simply run:
```bash
ai-workspace    # Navigate to project
ai-venv        # Activate virtual environment
ai-backend     # Start backend
ai-tests       # Run tests
ai-quality     # Check code quality
```

### Step 16: VS Code Integration (Optional)

```bash
# Install Remote - WSL extension in VS Code:
# 1. Open VS Code
# 2. Press Ctrl+Shift+X
# 3. Search for "Remote - WSL"
# 4. Install the extension
# 5. Click "Reopen in WSL" when prompted

# Or open project in WSL from terminal:
code ~/workspace/obsidian-ai
```

## File System Optimization

### Step 17: Performance Tips

```bash
# WSL file access from Windows is slower
# For better performance, keep projects in WSL filesystem:

# Create dedicated project directory in WSL
mkdir -p ~/projects
cd ~/projects

# Clone repository here instead
git clone https://github.com/UndiFineD/obsidian-AI-assistant.git

# This is faster than accessing /mnt/c files
```

## Troubleshooting

### Issue: WSL not found after reboot

```powershell
# Reinstall WSL
wsl --install

# Or update WSL
wsl --update
```

### Issue: Permission denied errors

```bash
# Fix file permissions
sudo chown -R $USER:$USER ~/workspace

# Or for git repositories
git config --global --add safe.directory /mnt/c/Users/kdejo/DEV/obsidian-llm-assistant/obsidian-AI-assistant
```

### Issue: Virtual environment not activating

```bash
# Check if venv exists
ls -la ~/workspace/obsidian-ai/venv/

# Recreate if needed
python3 -m venv ~/workspace/obsidian-ai/venv
source ~/workspace/obsidian-ai/venv/bin/activate
```

### Issue: Backend port already in use

```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process (replace PID with actual number)
sudo kill -9 PID

# Or use different port
python -m uvicorn agent.backend:app --port 8001
```

### Issue: Slow file access on /mnt/c

**Solution**: Store projects in WSL filesystem (~10x faster)

```bash
# Copy project to WSL
cp -r /mnt/c/Users/kdejo/DEV/obsidian-llm-assistant/obsidian-AI-assistant ~/projects/

# Work from WSL location
cd ~/projects/obsidian-AI-assistant
```

## Useful WSL Commands

```bash
# From PowerShell/CMD:

# List all WSL distributions
wsl --list --verbose

# Set Debian as default
wsl --set-default Debian

# Update WSL
wsl --update

# Shutdown WSL
wsl --shutdown

# Check WSL version
wsl --version

# Run specific command
wsl -d Debian -u kdejo -e bash

# Mount external drives (if needed)
wsl --mount D:
```

## Integration with Windows

### Accessing WSL Files from Windows

```powershell
# From PowerShell, access WSL files via:
\\wsl$\Debian\home\kdejo\workspace\obsidian-ai

# Or in File Explorer, type in address bar:
\\wsl$\Debian
```

### Running WSL Commands from Windows

```powershell
# Execute WSL command from PowerShell
wsl python3 --version

# Run python script
wsl python3 ~/workspace/obsidian-ai/tests/test_example.py
```

## Environment Variables

### Set Up Development Environment

```bash
# Add to ~/.bashrc
cat >> ~/.bashrc << 'EOF'

# Development environment variables
export PYTHONUNBUFFERED=1
export PROJECT_ROOT=~/workspace/obsidian-ai
export DEBUG=true
export LOG_LEVEL=debug

EOF

source ~/.bashrc
```

## Security Considerations

### Step 18: Basic Security Setup

```bash
# Update all packages
sudo apt update && sudo apt upgrade -y

# Enable UFW firewall (optional)
sudo apt install -y ufw
sudo ufw allow 22
sudo ufw enable

# Install security tools
sudo apt install -y fail2ban

# Start fail2ban
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
```

## Summary - Quick Start After Reboot

```bash
# 1. Launch WSL
wsl -d Debian

# 2. Setup project symlink
mkdir -p ~/workspace
ln -s /mnt/c/Users/kdejo/DEV/obsidian-llm-assistant/obsidian-AI-assistant ~/workspace/obsidian-ai

# 3. Create Python environment
cd ~/workspace/obsidian-ai
python3 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start backend
cd agent
python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload

# 6. In another terminal, run tests
source ~/workspace/obsidian-ai/venv/bin/activate
pytest ~/workspace/obsidian-ai/tests/ -v
```

## Next Steps

1. ✅ Reboot system
2. ✅ Follow setup steps 1-14
3. ✅ Test backend connectivity
4. ✅ Run test suite
5. ✅ Create development alias shortcuts (Step 15)
6. ✅ Integrate with VS Code (Step 16)

## Support Resources

- **WSL Documentation**: https://learn.microsoft.com/en-us/windows/wsl/
- **Debian Package Manager**: https://www.debian.org/
- **Python Virtual Environments**: https://docs.python.org/3/tutorial/venv.html
- **Git Documentation**: https://git-scm.com/doc
- **Project Repository**: https://github.com/UndiFineD/obsidian-AI-assistant

## Tips for Success

✅ Keep projects in WSL filesystem for better performance  
✅ Use VS Code with Remote - WSL extension  
✅ Set up bash aliases for common commands  
✅ Regularly update packages: `sudo apt update && sudo apt upgrade`  
✅ Back up important work regularly  
✅ Use virtual environments for project isolation  
✅ Monitor disk space in WSL: `df -h`  

---

**Installation Status**: ✅ Ready for Post-Reboot Setup  
**Estimated Setup Time**: 15-30 minutes  
**Difficulty Level**: Beginner-Friendly  

Once you complete these steps, you'll have a fully functional Linux development environment integrated with your Windows system, perfect for developing the Obsidian AI Assistant!

# WSL Debian Quick Reference - October 2025

## Installation Status
- ✅ WSL 2.6.1 installed
- ✅ Virtual Machine Platform enabled
- ⏳ Debian queued for installation after reboot
- ⏳ **System reboot required**

## Immediate Next Steps

### 1. Restart Computer
```powershell
Restart-Computer
```

### 2. Launch Debian (After Reboot)
```powershell
wsl -d Debian
```

### 3. Initial Setup
- Enter username: `kdejo`
- Create password (secure)
- Wait for initialization (~2-3 minutes)

## Essential Commands (Copy-Paste Ready)

### Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### Install Development Tools
```bash
sudo apt install -y build-essential git curl wget python3 python3-pip python3-venv
```

### Setup Project Access
```bash
mkdir -p ~/workspace
ln -s /mnt/c/Users/kdejo/DEV/obsidian-llm-assistant/obsidian-AI-assistant ~/workspace/obsidian-ai
cd ~/workspace/obsidian-ai
```

### Create Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Start Backend
```bash
cd agent
python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload
```

### Run Tests
```bash
pytest tests/ -v
```

### Code Quality Checks
```bash
ruff check agent/
bandit -r agent/
mypy agent/ --ignore-missing-imports
```

## Useful WSL Commands

| Command | Purpose |
|---------|---------|
| `wsl` | Launch default WSL distribution |
| `wsl -d Debian` | Launch Debian specifically |
| `wsl --list --verbose` | List all WSL distributions |
| `wsl --shutdown` | Shutdown WSL (frees resources) |
| `wsl --update` | Update WSL components |
| `wsl --version` | Check WSL version |

## Bash Aliases Setup

Add to `~/.bashrc`:
```bash
alias ai-workspace="cd ~/workspace/obsidian-ai"
alias ai-venv="source ~/workspace/obsidian-ai/venv/bin/activate"
alias ai-backend="cd ~/workspace/obsidian-ai/agent && python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload"
alias ai-tests="pytest ~/workspace/obsidian-ai/tests/ -v"
alias ai-quality="cd ~/workspace/obsidian-ai && ruff check agent/"
```

Then reload:
```bash
source ~/.bashrc
```

## Access Project Files from Windows

**From File Explorer:**
```
\\wsl$\Debian\home\kdejo\workspace\obsidian-ai
```

**From PowerShell:**
```powershell
wsl ls ~/workspace/obsidian-ai
wsl python3 --version
```

## Common Issues & Quick Fixes

### WSL not starting
```powershell
wsl --update
Restart-Computer
```

### Permission denied
```bash
sudo chown -R $USER:$USER ~/workspace
```

### Port 8000 already in use
```bash
sudo lsof -i :8000
sudo kill -9 PID
```

### Virtual environment not working
```bash
python3 -m venv ~/workspace/obsidian-ai/venv
source ~/workspace/obsidian-ai/venv/bin/activate
```

### Slow file access on /mnt/c
**Solution**: Copy project to WSL filesystem
```bash
cp -r /mnt/c/Users/kdejo/DEV/obsidian-llm-assistant ~/projects/
cd ~/projects/obsidian-AI-assistant
```

## Development Workflow

### Daily Startup
```bash
# Terminal 1: Launch WSL and start backend
wsl -d Debian
ai-venv
ai-backend

# Terminal 2: Run tests/development
wsl -d Debian
ai-venv
ai-tests
```

### Git Operations
```bash
cd ~/workspace/obsidian-ai

# Check status
git status

# Pull latest
git pull origin main

# Create feature branch
git checkout -b feature/my-feature

# Commit changes
git add .
git commit -m "feat: description"
git push origin feature/my-feature
```

## VS Code Integration

**In VS Code:**
1. Install "Remote - WSL" extension (search Extensions)
2. Click "Reopen in WSL" when prompted
3. Or run: `code ~/workspace/obsidian-ai`

This opens VS Code inside WSL for native performance.

## Performance Tips

| Action | Benefit |
|--------|---------|
| Store projects in WSL `~` | ~10x faster than `/mnt/c` |
| Use WSL filesystem for git | Proper file permissions |
| Close WSL when not in use | Frees Windows resources |
| Use `wsl --shutdown` | Clean resource release |
| Enable NTFS in WSL | Better Windows interop |

## File Size Comparison

- **Windows `/mnt/c` access**: ~200-500 ms operations
- **WSL `~/` filesystem**: ~10-50 ms operations
- **Reason**: Native Linux filesystem vs NTFS through WSL bridge

## Estimated Times

| Task | Time |
|------|------|
| System reboot | 2-5 minutes |
| Debian initialization | 2-3 minutes |
| Package updates | 3-5 minutes |
| Python environment setup | 2-3 minutes |
| Initial test run | 1-2 minutes |
| **Total first setup** | **~15-30 minutes** |

## System Requirements Check

```bash
# Check CPU
lscpu

# Check RAM
free -h

# Check Disk
df -h

# Check Linux version
uname -a

# Check Debian version
cat /etc/os-release
```

## Environment Variables

Set in `~/.bashrc`:
```bash
export PYTHONUNBUFFERED=1
export PROJECT_ROOT=~/workspace/obsidian-ai
export DEBUG=true
export LOG_LEVEL=debug
```

## Uninstall WSL (If Needed)

```powershell
# Remove Debian
wsl --unregister Debian

# Remove WSL entirely (not recommended during setup)
wsl --uninstall
```

## Documentation Links

- Full Setup Guide: `docs/WSL_DEBIAN_SETUP_GUIDE.md`
- Project Instructions: `.github/copilot-instructions.md`
- Test Documentation: `docs/TESTING_GUIDE.md`
- Contributing Guide: `docs/CONTRIBUTING.md`

## Quick Checklist

### Before Reboot
- [ ] Noted this quick reference
- [ ] Printed setup guide (optional)
- [ ] Backed up important files
- [ ] Closed all applications

### After Reboot
- [ ] WSL launched successfully
- [ ] Created username/password
- [ ] System initialized
- [ ] Ran `apt update`
- [ ] Installed development tools
- [ ] Set up project symlink
- [ ] Created Python venv
- [ ] Installed dependencies
- [ ] Started backend successfully
- [ ] Ran test suite
- [ ] All tests passing ✅

## Need Help?

**WSL Documentation**: microsoft.com/windows/wsl  
**Debian Help**: debian.org  
**Project Issues**: github.com/UndiFineD/obsidian-AI-assistant/issues  

---

**Status**: Ready for immediate deployment after system reboot  
**Difficulty**: Beginner-Friendly  
**Estimated Total Time**: 30 minutes from reboot to working development environment

Good luck! 🚀

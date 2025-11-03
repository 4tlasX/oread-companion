# Oread Scripts Guide

This document explains all the helper scripts included with Oread.

---

## ⚠️ Important: Script Safety

**These scripts modify your system.** Please read before running:

### What Installation Scripts Do:
- **Install software** on your system (Node.js, Python, build tools)
- **Modify system PATH** to make commands available globally
- **Download files** from the internet (models, dependencies)
- **Create files and directories** in your home folder

### Your Responsibility:
- ✅ **Read the script** before running it (they're just text files!)
- ✅ **Understand what it does** to your system
- ✅ **Back up important data** before major changes
- ✅ **Use at your own risk** - we can't support every system configuration

### What "Installing Python" Means:
When scripts install Python 3.11:
- A programming language runtime is added to your system
- Python packages (libraries) are downloaded and installed
- Takes ~500MB of disk space
- Will be used system-wide (other apps can use it too)
- Can be uninstalled later through your system's package manager

### What "Installing Node.js" Means:
When scripts install Node.js 18:
- A JavaScript runtime is added to your system
- NPM (package manager) is included
- Takes ~200MB of disk space
- Will be used system-wide
- Can be uninstalled later

### Security Considerations:
- Scripts download from official sources (nodejs.org, python.org, Hugging Face)
- All downloads happen over HTTPS
- You can inspect any script before running: `cat install-macos.sh`
- **If you're uncomfortable, don't run installation scripts** - follow [INSTALLATION.md](INSTALLATION.md) for manual installation instead

---

## Installation Scripts

### `install-macos.sh`
**Platform:** macOS only  
**Purpose:** Fully automated installation for macOS users  
**What it does:**
- ✅ Installs Homebrew (if needed)
- ✅ Installs Node.js 18
- ✅ Installs Python 3.11
- ✅ Installs Xcode Command Line Tools
- ✅ Installs all Oread dependencies (backend, frontend, inference)
- ✅ Downloads emotion detection model
- ✅ Creates configuration files
- ✅ Optionally downloads AI model (4-5GB)

**Usage:**
```bash
./install-macos.sh
```

**Time:** 15-30 minutes (depending on internet speed)

---

### `install-linux.sh`
**Platform:** Linux (Ubuntu, Debian, Fedora, Arch)  
**Purpose:** Fully automated installation for Linux users  
**What it does:**
- ✅ Detects Linux distribution
- ✅ Installs Node.js 18
- ✅ Installs Python 3.11
- ✅ Installs build tools (gcc, cmake, etc.)
- ✅ Detects NVIDIA GPU and offers CUDA installation
- ✅ Installs all Oread dependencies
- ✅ Downloads emotion detection model
- ✅ Creates configuration files
- ✅ Optionally downloads AI model

**Usage:**
```bash
./install-linux.sh
```

**Time:** 15-30 minutes

---

## Runtime Scripts

### `start-oread.sh`
**Purpose:** Start Oread services  
**What it does:**
- ✅ Checks if ports 9000/9001 are available
- ✅ Starts inference service (Python)
- ✅ Waits for inference to be ready
- ✅ Starts backend server (Node.js)
- ✅ Waits for backend to be ready
- ✅ Opens browser automatically
- ✅ Captures Ctrl+C to stop gracefully

**Usage:**
```bash
./start-oread.sh
```

**Logs:**
- Backend: `logs/backend.log`
- Inference: `logs/inference.log`

**To stop:** Press `Ctrl+C` or run `./stop-oread.sh`

---

### `stop-oread.sh`
**Purpose:** Stop all Oread processes  
**What it does:**
- ✅ Finds processes using port 9000 (backend)
- ✅ Finds processes using port 9001 (inference)
- ✅ Gracefully terminates them
- ✅ Force-kills if graceful shutdown fails

**Usage:**
```bash
./stop-oread.sh
```

**When to use:**
- Before updating Oread
- Before changing configuration
- If Oread becomes unresponsive
- To free up system resources

---

## Maintenance Scripts

### `update-oread.sh`
**Purpose:** Update Oread to the latest version  
**What it does:**
- ✅ Stops Oread if running
- ✅ Creates backup of user data
- ✅ Fetches latest code from GitHub
- ✅ Shows what will be updated
- ✅ Asks for confirmation
- ✅ Updates all dependencies (Node.js + Python)
- ✅ Rebuilds frontend

**Usage:**
```bash
./update-oread.sh
```

**Safety:**
- Creates timestamped backup before updating
- Shows git diff before applying
- Can be cancelled at any time

---

## Typical Workflows

### First-Time Setup
```bash
# 1. Install Oread
./install-macos.sh  # or install-linux.sh

# 2. Start Oread
./start-oread.sh

# 3. Open browser to https://localhost:9000
# 4. Login with password: oread
# 5. Change password in Settings
```

---

### Daily Use
```bash
# Start
./start-oread.sh

# When done, press Ctrl+C
# or
./stop-oread.sh
```

---

### Trying Different Models
```bash
# Stop Oread first
./stop-oread.sh

# Download a different model
# See INSTALLATION.md for model recommendations
cd models/
wget https://huggingface.co/PATH/TO/MODEL.gguf

# Update inference/.env to point to new model
# LLM_MODEL_PATH=models/YOUR_NEW_MODEL.gguf

# Start with new model
./start-oread.sh
```

---

### Updating Oread
```bash
# Check for updates
git fetch

# Apply updates
./update-oread.sh

# Start updated version
./start-oread.sh
```

---

### Troubleshooting "Stuck" State
```bash
# Force stop everything
./stop-oread.sh

# Clear logs
rm logs/*.log

# Restart fresh
./start-oread.sh
```

---

## Script Permissions

All scripts should have execute permissions. If you get "Permission denied":

```bash
chmod +x *.sh
```

---

## Platform Compatibility

| Script | macOS | Linux | Windows (WSL) |
|--------|-------|-------|---------------|
| `install-macos.sh` | ✅ | ❌ | ❌ |
| `install-linux.sh` | ❌ | ✅ | ✅ |
| `start-oread.sh` | ✅ | ✅ | ✅ |
| `stop-oread.sh` | ✅ | ✅ | ✅ |
| `update-oread.sh` | ✅ | ✅ | ✅ |

---

## Environment Variables

Scripts respect these environment variables:

**For `start-oread.sh`:**
```bash
# Use different ports
export PORT=9000  # Backend
export INFERENCE_PORT=9001  # Inference
./start-oread.sh
```

**For all scripts:**
```bash
# Disable colors
export NO_COLOR=1
./install-macos.sh
```

---

## Logging

Scripts log to:
- **Standard output:** Info, success, warning messages
- **Log files:** Runtime logs (backend, inference)

**View logs in real-time:**
```bash
tail -f logs/backend.log
tail -f logs/inference.log
```

**Search for errors:**
```bash
grep -i error logs/*.log
```

---

## Common Issues

### "Address already in use"
**Cause:** Oread is already running or another service is using port 9000/9001

**Fix:**
```bash
./stop-oread.sh
# Wait 5 seconds
./start-oread.sh
```

---

### "Model not found"
**Cause:** No AI model downloaded

**Fix:**
Download a model manually. See [INSTALLATION.md](INSTALLATION.md) for recommendations.

---

### "npm: command not found"
**Cause:** Node.js not installed

**Fix:**
```bash
# macOS
./install-macos.sh

# Linux
./install-linux.sh
```

---

### "python3: command not found"
**Cause:** Python not installed

**Fix:**
Run the installation script for your platform.

---

## Manual Installation Alternative

**Don't trust automated scripts?** That's smart!

You can install Oread manually by following [INSTALLATION.md](INSTALLATION.md). It takes longer but gives you complete control over every step.

---

## Getting Help

- **General questions:** [FAQ.md](FAQ.md)
- **Installation issues:** [INSTALLATION.md](INSTALLATION.md)
- **Bug reports:** [GitHub Issues](https://github.com/sleddd/oread/issues)

---

## Contributing

Found a bug in a script? Want to add a new one?

1. Fork the repository
2. Make your changes
3. Test on your platform
4. Submit a pull request

**Script guidelines:**
- Use bash (not sh)
- Include colored output for readability
- Add error handling (`set -e`)
- Include help messages
- Test on multiple platforms if possible
- Document what the script modifies

---

## Disclaimer

**Use these scripts at your own risk.** While we've tested them extensively, we can't guarantee they'll work perfectly on every system configuration. Always:

- Read scripts before running them
- Back up important data
- Understand what will be installed
- Know how to uninstall if needed

**You're responsible for your system.** These scripts are provided as-is to make installation easier, but manual installation is always an option if you prefer complete control.

---

**Scripts are designed to be user-friendly, but transparency about system changes is important!** 🛡️
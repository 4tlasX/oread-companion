cluade# Installation Guide

This guide provides step-by-step instructions for installing and running Oread on macOS, Linux, and Windows.

---

## Table of Contents
- [System Requirements](#system-requirements)
- [Quick Start (Recommended)](#quick-start-recommended)
- [Manual Installation](#manual-installation)
  - [macOS](#macos)
  - [Linux](#linux)
  - [Windows](#windows-wsl)
- [Downloading Models](#downloading-models)
- [Configuration](#configuration)
- [Running Oread](#running-oread)
- [First-Time Setup](#first-time-setup)
- [Troubleshooting](#troubleshooting)
- [Updating](#updating)
- [Uninstalling](#uninstalling)

---

## System Requirements

### Minimum
- **OS:** macOS 11+, Linux (Ubuntu 20.04+, Debian 11+, etc.), Windows 10+ (with WSL2)
- **RAM:** 16GB (8GB might work with small models, but not recommended)
- **Storage:** 15GB free space (10GB for model + 5GB for application)
- **CPU:** Modern multi-core processor (Intel/AMD x86_64 or Apple Silicon)
- **Internet:** Required for initial setup and optional web search

### Recommended
- **RAM:** 32GB (for 12B+ models)
- **GPU:** 
  - Apple Silicon (M1/M2/M3) with Metal support
  - NVIDIA GPU with 8GB+ VRAM and CUDA support
  - AMD GPU with ROCm support (Linux only)
- **Storage:** SSD (significantly faster model loading and generation)

### Software Prerequisites
- **Node.js:** 18+ (LTS recommended)
- **Python:** 3.10, 3.11, or 3.12
- **Git:** Latest version
- **C++ compiler:** Required for llama-cpp-python compilation
  - macOS: Xcode Command Line Tools
  - Linux: GCC/G++
  - Windows: Visual Studio Build Tools or WSL

---

## Quick Start (Recommended)

If you're comfortable with the command line and have all prerequisites installed, here's the fastest way to get started:

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/oread.git
cd oread

# 2. Install dependencies
cd backend && npm install && cd ..
cd frontend && npm install && cd ..
cd inference && pip install -r requirements.txt && cd ..

# 3. Download a model (example - MN-Violet-Lotus-12B)
mkdir -p models
cd models
# Download from Hugging Face (see "Downloading Models" section below)
cd ..

# 4. Configure environment (copy examples and edit as needed)
cp backend/.env.example backend/.env
cp inference/.env.example inference/.env
# Edit inference/.env to point to your downloaded model

# 5. Start Oread
./start-oread.sh

# 6. Open browser
# Navigate to https://localhost:9000
# Accept the self-signed certificate warning
# Default password: oread
```

If this worked, skip to [First-Time Setup](#first-time-setup).

If you encountered issues or want detailed instructions, continue reading.

---

## Manual Installation

### macOS

#### Step 1: Install Homebrew (if not already installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Step 2: Install Prerequisites

```bash
# Install Node.js (using Homebrew)
brew install node@18

# Install Python 3.10+ (if not already installed)
brew install python@3.11

# Install Git (usually pre-installed)
brew install git

# Install Xcode Command Line Tools (for compiling llama-cpp-python)
xcode-select --install
```

#### Step 3: Verify Installations

```bash
node --version    # Should show v18.x or higher
npm --version     # Should show 9.x or higher
python3 --version # Should show 3.10, 3.11, or 3.12
git --version     # Should show 2.x
```

#### Step 4: Clone Repository

```bash
cd ~  # Or wherever you want to install
git clone https://github.com/YOUR_USERNAME/oread.git
cd oread
```

#### Step 5: Install Node.js Dependencies

```bash
# Backend
cd backend
npm install
cd ..

# Frontend
cd frontend
npm install
cd ..
```

#### Step 6: Install Python Dependencies

```bash
cd inference

# Optional but recommended: use a virtual environment
python3 -m venv venv
source venv/bin/activate  # Activate virtual environment

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# This will take several minutes (compiling llama-cpp-python with Metal support)
# If you have Apple Silicon, it will automatically use Metal acceleration
```

**Troubleshooting Metal compilation:**
If `llama-cpp-python` fails to compile with Metal:

```bash
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
```

#### Step 7: Download Model (see [Downloading Models](#downloading-models))

#### Step 8: Configure (see [Configuration](#configuration))

#### Step 9: Run (see [Running Oread](#running-oread))

---

### Linux

#### Step 1: Update Package Manager

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt upgrade -y
```

**Fedora:**
```bash
sudo dnf update -y
```

**Arch:**
```bash
sudo pacman -Syu
```

#### Step 2: Install Prerequisites

**Ubuntu/Debian:**
```bash
# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install Git and build tools
sudo apt install -y git build-essential cmake
```

**Fedora:**
```bash
sudo dnf install -y nodejs python3.11 python3-pip git gcc-c++ cmake
```

**Arch:**
```bash
sudo pacman -S nodejs python python-pip git base-devel cmake
```

#### Step 3: (Optional) Install CUDA for NVIDIA GPUs

**If you have an NVIDIA GPU and want GPU acceleration:**

```bash
# Check if you have an NVIDIA GPU
nvidia-smi

# Install CUDA Toolkit (version 11.8 or 12.x)
# Follow instructions at: https://developer.nvidia.com/cuda-downloads

# Verify CUDA installation
nvcc --version
```

#### Step 4: Install ROCm for AMD GPUs (Advanced)

**If you have an AMD GPU and want GPU acceleration:**

Follow AMD's official ROCm installation guide:
https://docs.amd.com/

Note: ROCm support is experimental and may not work on all systems.

#### Step 5: Clone Repository

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/oread.git
cd oread
```

#### Step 6: Install Node.js Dependencies

```bash
cd backend && npm install && cd ..
cd frontend && npm install && cd ..
```

#### Step 7: Install Python Dependencies

```bash
cd inference

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

**For CUDA support:**
```bash
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
```

**For ROCm support:**
```bash
CMAKE_ARGS="-DLLAMA_HIPBLAS=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
```

#### Step 8: Download Model (see [Downloading Models](#downloading-models))

#### Step 9: Configure (see [Configuration](#configuration))

#### Step 10: Run (see [Running Oread](#running-oread))

---

### Windows (WSL)

**Recommended:** Use Windows Subsystem for Linux (WSL2) for best compatibility.

#### Step 1: Install WSL2

```powershell
# Run in PowerShell as Administrator
wsl --install

# This installs Ubuntu by default
# Restart your computer when prompted
```

After restart, open "Ubuntu" from Start Menu.

#### Step 2: Update Ubuntu

```bash
sudo apt update && sudo apt upgrade -y
```

#### Step 3: Install Prerequisites

```bash
# Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Git and build tools
sudo apt install -y git build-essential cmake
```

#### Step 4: Clone Repository

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/oread.git
cd oread
```

#### Step 5: Install Node.js Dependencies

```bash
cd backend && npm install && cd ..
cd frontend && npm install && cd ..
```

#### Step 6: Install Python Dependencies

```bash
cd inference
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** CUDA support in WSL2 is possible but complex. See:
https://docs.nvidia.com/cuda/wsl-user-guide/index.html

#### Step 7: Download Model (see [Downloading Models](#downloading-models))

#### Step 8: Configure (see [Configuration](#configuration))

#### Step 9: Run (see [Running Oread](#running-oread))

---

## Downloading Models

**IMPORTANT:** Oread does NOT automatically download models. You are responsible for obtaining and using models legally.

Oread requires a **GGUF format LLM model**. You must download one yourself before using Oread.

### Choosing a Model

**What was Oread tested with?**
Oread was primarily tested with **MN-Violet-Lotus-12B** (an uncensored model). However, this does NOT mean you should use it. The choice of model is entirely yours and should align with your values and intended use.

**Censored vs Uncensored Models:**
- **Censored models** have built-in content filters and refusals
- **Uncensored models** have fewer restrictions but require more user responsibility
- **Your choice should reflect your comfort level and ethical stance**

---

### Model Options

Choose the model that best fits your needs and values:

#### Option 1: Censored, General Purpose (Recommended for Most Users)

**Llama-3.1-8B-Instruct (Q4_K_M)** - Strong reasoning, built-in safety guardrails

- Link: https://huggingface.co/lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF
- Size: ~4.9GB
- Censorship: Yes (built-in content moderation)
- Best for: General use, safer interactions

```bash
cd /path/to/oread/models/
wget https://huggingface.co/lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
```

#### Option 2: Balanced Roleplay Model

**Nous-Hermes-3-Llama-3.1-8B (Q4_K_M)** - Good balance of capability and safety

- Link: https://huggingface.co/NousResearch/Hermes-3-Llama-3.1-8B-GGUF
- Size: ~4.9GB
- Censorship: Moderate
- Best for: Roleplay with some guardrails

```bash
cd /path/to/oread/models/
wget https://huggingface.co/NousResearch/Hermes-3-Llama-3.1-8B-GGUF/resolve/main/Hermes-3-Llama-3.1-8B.Q4_K_M.gguf
```

#### Option 3: Uncensored Roleplay (Tested Model - Requires User Responsibility)

**MN-Violet-Lotus-12B (Q4_K_M)** - Uncensored, excellent creative writing

⚠️ **Warning:** This is an uncensored model. It has no built-in content restrictions.

- Link: https://huggingface.co/MaziyarPanahi/MN-Violet-Lotus-12B-v1.1-GGUF
- Size: ~4.3GB
- Censorship: None
- Best for: Users who want maximum creative freedom and understand the responsibility

```bash
cd /path/to/oread/models/
wget https://huggingface.co/MaziyarPanahi/MN-Violet-Lotus-12B-v1.1-GGUF/resolve/main/MN-Violet-Lotus-12B-v1.1.Q4_K_M.gguf
```

#### Option 4: Low-End Hardware (8GB RAM)

**Phi-3-Mini-4K (Q4_K_M)** - Smallest but still functional

- Link: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf
- Size: ~2.3GB
- Censorship: Yes
- Best for: Systems with limited RAM

```bash
cd /path/to/oread/models/
wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf
```

---

### After Downloading

Once you've downloaded a model:

1. Ensure it's in the `models/` directory
2. Edit `inference/.env` and set:
   ```
   LLM_MODEL_PATH=models/YOUR_MODEL_NAME.gguf
   ```
3. Replace `YOUR_MODEL_NAME.gguf` with your actual model filename

### Where to Find More Models

- **Hugging Face:** https://huggingface.co/models?library=gguf
- Search for "GGUF" models
- Ensure the model has an appropriate license for your use case
- **You are responsible for complying with model licenses**

### Quantization Guide

| Quantization | Size (12B model) | Quality | RAM Required |
|--------------|------------------|---------|--------------|
| Q4_K_M       | ~4GB            | Good    | 8GB          |
| Q5_K_M       | ~5GB            | Better  | 10GB         |
| Q6_K         | ~6GB            | Great   | 12GB         |
| Q8_0         | ~8GB            | Excellent | 14GB       |

**Recommendation:** Q4_K_M for best balance of quality and performance.

---

## Configuration

### Backend Configuration

Copy the example `.env` file:

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env`:

```bash
# Server Configuration
PORT=9000
HOST=127.0.0.1

# Inference Service URL
INFERENCE_URL=http://127.0.0.1:9001

# Session Secret (change this to a random string)
SESSION_SECRET=your-random-secret-here-change-this

# CORS Origins
ALLOWED_ORIGINS=https://localhost:9000,https://127.0.0.1:9000

# Data Directory (relative to backend/)
DATA_DIR=../data
```

**Important:** Change `SESSION_SECRET` to a random string. Generate one:

```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

---

### Inference Service Configuration

Copy the example `.env` file:

```bash
cd inference
cp .env.example .env
```

Edit `inference/.env`:

```bash
# Server Configuration
INFERENCE_HOST=127.0.0.1
INFERENCE_PORT=9001
RELOAD=false
LOG_LEVEL=info

# Model Paths (IMPORTANT: Update these!)
LLM_MODEL_PATH=models/MN-Violet-Lotus-12B-v1.1.Q4_K_M.gguf
EMOTION_MODEL_PATH=models/roberta_emotions_onnx

# GPU Acceleration
# -1 = All layers on GPU (fastest, recommended if you have GPU)
# 0 = CPU only
# 20 = First 20 layers on GPU (hybrid)
LLM_N_GPU_LAYERS=-1

# Context Size
LLM_N_CTX=4096

# Batch Size
LLM_N_BATCH=512

# CPU Threads (adjust based on your CPU cores)
LLM_N_THREADS=8

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:9000,http://127.0.0.1:9000,https://localhost:9000,https://127.0.0.1:9000
```

**Key settings to adjust:**

1. **LLM_MODEL_PATH:** Change to match your downloaded model filename
2. **LLM_N_GPU_LAYERS:** 
   - Apple Silicon (Metal): `-1` (all layers on GPU)
   - NVIDIA CUDA: `-1` (all layers on GPU)
   - CPU only: `0`
   - Hybrid: `20` (first 20 layers on GPU, rest on CPU)
3. **LLM_N_THREADS:** Set to your CPU core count (check with `sysctl -n hw.ncpu` on macOS or `nproc` on Linux)

---

### Download Emotion Model

The emotion detection model is separate from the LLM. Download it:

```bash
cd models

# Option 1: Use the provided script (if available)
# (Check if there's a download script in the repo)

# Option 2: Manual download from Hugging Face
git clone https://huggingface.co/arpanghoshal/roberta-base-emotion-classifier-onnx roberta_emotions_onnx

# Or download just the necessary files
wget -P roberta_emotions_onnx https://huggingface.co/arpanghoshal/roberta-base-emotion-classifier-onnx/resolve/main/config.json
wget -P roberta_emotions_onnx https://huggingface.co/arpanghoshal/roberta-base-emotion-classifier-onnx/resolve/main/model.onnx
wget -P roberta_emotions_onnx https://huggingface.co/arpanghoshal/roberta-base-emotion-classifier-onnx/resolve/main/tokenizer.json
wget -P roberta_emotions_onnx https://huggingface.co/arpanghoshal/roberta-base-emotion-classifier-onnx/resolve/main/tokenizer_config.json
```

Verify the structure:

```bash
ls models/roberta_emotions_onnx/
# Should show: config.json, model.onnx, tokenizer.json, tokenizer_config.json
```

---

## Running Oread

### Option 1: Automated Startup Script (Recommended)

```bash
cd /path/to/oread
./start-oread.sh
```

This script:
1. Starts the inference service (Python)
2. Waits for it to be ready
3. Starts the backend (Node.js)
4. Opens your browser to https://localhost:9000

**Stop Oread:**
Press `Ctrl+C` in the terminal where you ran the script.

---

### Option 2: Manual Startup (Two Terminals)

**Terminal 1: Start Inference Service**

```bash
cd /path/to/oread/inference

# If using virtual environment:
source venv/bin/activate

# Start inference service
python main.py
```

Wait for: `✅ Inference service ready`

**Terminal 2: Start Backend**

```bash
cd /path/to/oread/backend
npm start
```

Wait for: `✅ Backend server running on https://localhost:9000`

**Open Browser:**

Navigate to: `https://localhost:9000`

Accept the self-signed certificate warning (click "Advanced" → "Proceed to localhost").

---

### Option 3: Run as Background Services (Advanced)

**Using systemd (Linux):**

Create service files in `/etc/systemd/system/`:

**`oread-inference.service`:**
```ini
[Unit]
Description=Oread Inference Service
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/oread/inference
ExecStart=/path/to/python3 main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**`oread-backend.service`:**
```ini
[Unit]
Description=Oread Backend Service
After=network.target oread-inference.service

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/oread/backend
ExecStart=/usr/bin/npm start
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable oread-inference oread-backend
sudo systemctl start oread-inference oread-backend

# Check status
sudo systemctl status oread-inference oread-backend
```

---

## First-Time Setup

### 1. Access Oread

Open your browser to: `https://localhost:9000`

Accept the self-signed certificate warning.

### 2. Login

**Default password:** `oread`

**IMPORTANT:** Change this immediately after first login!

### 3. Accept Terms of Service

You'll be prompted to review and accept the Terms of Service and Safety Protocol.

Read carefully and check all boxes to agree.

### 4. Change Password

1. Click **Settings** (gear icon)
2. Scroll to "Change Password"
3. Enter:
   - Current password: `oread`
   - New password: (your secure password)
   - Confirm new password
4. Click "Change Password"

**This will re-encrypt all profiles with your new password.**

### 5. Configure Your Profile (Optional but Recommended)

1. In Settings, fill out "All about you / Memory Notes"
   - Your name
   - Gender
   - Species (for fantasy/sci-fi roleplay)
   - Timezone
   - Backstory
   - Preferences
2. Click "Save Settings"

### 6. Customize Default Character or Create New

**Option A: Edit Default Character (Echo/Kairos)**
1. In Settings, select "Echo" or "Kairos"
2. Edit character details
3. Save

**Option B: Create New Character**
1. Click "➕ New"
2. Fill in character profile (see [FAQ - How do I create a custom character?](FAQ.md#how-do-i-create-a-custom-character))
3. Save and set as active

### 7. Optional: Enable Memory and Web Search

**Memory (ChromaDB):**
- Toggle "Enable Memory" in Settings
- Allows semantic search across past conversations
- Requires 1-2GB additional RAM

**Web Search (Brave API):**
- Toggle "Enable Web Search"
- Get API key from https://brave.com/search/api/
- Paste key in "Web Search API Key" field
- Allows real-time fact-checking

### 8. Start Chatting!

Return to main chat page and start a conversation.

---

## Troubleshooting

### Model Not Loading

**Error:** "Failed to load model" or "Model file not found"

**Solutions:**
1. Check model path in `inference/.env` matches actual filename
2. Ensure model is in `models/` directory
3. Verify file isn't corrupted (check file size matches expected)
4. Check permissions: `chmod 644 models/*.gguf`

---

### Inference Service Won't Start

**Error:** "Address already in use" or port 9001 conflict

**Solution:**
```bash
# Find what's using port 9001
lsof -i :9001

# Kill the process (replace PID with actual number)
kill -9 PID

# Or change port in inference/.env
INFERENCE_PORT=9002
```

---

### Backend Server Won't Start

**Error:** "EADDRINUSE: address already in use :::9000"

**Solution:**
```bash
# Find what's using port 9000
lsof -i :9000

# Kill the process or change port in backend/.env
PORT=9005
```

---

### "Module not found" Errors

**Error:** "Cannot find module 'express'" or similar

**Solution:**
```bash
# Re-install dependencies
cd backend
rm -rf node_modules package-lock.json
npm install

cd ../frontend
rm -rf node_modules package-lock.json
npm install
```

---

### Python Dependency Errors

**Error:** "No module named 'fastapi'" or similar

**Solution:**
```bash
cd inference

# If using virtual environment, activate it first
source venv/bin/activate

# Re-install dependencies
pip install -r requirements.txt
```

---

### llama-cpp-python Compilation Fails

**Error:** "Failed building wheel for llama-cpp-python"

**macOS Solution:**
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Force reinstall with Metal support
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
```

**Linux Solution (CUDA):**
```bash
# Ensure CUDA is installed
nvcc --version

# Force reinstall with CUDA support
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
```

**Linux Solution (CPU only):**
```bash
pip install llama-cpp-python --force-reinstall --no-cache-dir
```

---

### Self-Signed Certificate Errors

**Error:** Browser blocks access due to invalid certificate

**Solution:**
Click "Advanced" → "Proceed to localhost (unsafe)"

This is safe because the certificate is for localhost only (no external traffic).

---

### Slow Generation

**Symptom:** Responses take 30+ seconds

**Solutions:**
1. Enable GPU acceleration:
   - Edit `inference/.env`
   - Set `LLM_N_GPU_LAYERS=-1`
   - Restart inference service
2. Use a smaller model (7B instead of 12B)
3. Reduce context size: `LLM_N_CTX=2048`
4. Disable memory and web search (Settings)

---

### "Encryption Error" or "Wrong Password"

**Symptom:** Can't decrypt profiles after password change

**Solutions:**
1. Ensure you're using the correct new password
2. If password change failed partway, some files may still use old password
3. Restore from backup (Settings → Download Backup from before password change)
4. As last resort, delete `data/profiles/*.json` and start fresh (loses characters)

---

## Updating

To update Oread to the latest version:

```bash
cd /path/to/oread

# Stop services first (Ctrl+C if using start script)

# Pull latest changes
git pull origin main

# Update dependencies
cd backend && npm install && cd ..
cd frontend && npm install && cd ..
cd inference && pip install -r requirements.txt && cd ..

# Restart services
./start-oread.sh
```

**Note:** Check release notes for breaking changes or migration steps.

---

## Uninstalling

To completely remove Oread:

```bash
# 1. Stop services (Ctrl+C if running)

# 2. Optionally export your data first
# Go to Settings → Download Backup

# 3. Delete the repository
cd ~
rm -rf /path/to/oread

# 4. Remove Python virtual environment (if created)
# (Already deleted with repo)

# 5. Optionally remove Node.js/Python if only installed for Oread
# (Use Homebrew uninstall commands or system package manager)
```

**Your data is deleted with the repository.** Make sure to export if you want to keep it!

---

## Need More Help?

- **FAQ:** [FAQ.md](FAQ.md)
- **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Security:** [SECURITY_ETHICS_SAFETY.md](SECURITY_ETHICS_SAFETY.md)
- **Bug Reports:** [GitHub Issues](https://github.com/YOUR_USERNAME/oread/issues)
- **Discussions:** [GitHub Discussions](https://github.com/YOUR_USERNAME/oread/discussions)

---

**Welcome to Oread! Enjoy your privacy-first AI companion.**

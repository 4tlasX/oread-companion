# Quick Start Guide

**Never used a command line before? No problem!** This guide walks you through everything.

---

## What You Need

1. A computer (Mac, Linux, or Windows)
2. Internet connection (for initial setup)
3. 30 minutes of time
4. At least 16GB RAM (8GB might work with smaller models)

---

## Installation (Choose Your System)

### 🍎 macOS

**Step 1: Open Terminal**
- Press `Cmd + Space`
- Type "Terminal"
- Press Enter

**Step 2: Navigate to Downloads**
```bash
cd ~/Downloads
```

**Step 3: Download Oread**
```bash
git clone https://github.com/sleddd/oread.git
cd oread
```

**Step 4: Run Installer**
```bash
./install-macos.sh
```

Follow the prompts. The script will:
- Install required software
- Download dependencies
- Optionally download an AI model (4-5GB)
- Take about 15-30 minutes total

---

### 🐧 Linux

**Step 1: Open Terminal**
- Press `Ctrl + Alt + T`

**Step 2: Navigate to Home**
```bash
cd ~
```

**Step 3: Download Oread**
```bash
git clone https://github.com/sleddd/oread.git
cd oread
```

**Step 4: Run Installer**
```bash
./install-linux.sh
```

Follow the prompts. The script will:
- Detect your Linux distribution
- Install required software
- Download dependencies
- Optionally download an AI model
- Take about 15-30 minutes total

---

### 🪟 Windows

**Step 1: Install WSL (Windows Subsystem for Linux)**
- Open PowerShell as Administrator
- Run: `wsl --install`
- Restart your computer when prompted

**Step 2: Open Ubuntu**
- Search for "Ubuntu" in Start Menu
- Open it (this is your Linux terminal)

**Step 3: Follow Linux Instructions Above**
```bash
cd ~
git clone https://github.com/sleddd/oread.git
cd oread
./install-linux.sh
```

---

## Starting Oread

After installation, run:

```bash
./start-oread.sh
```

This will:
1. Start the inference service (Python)
2. Start the backend server (Node.js)
3. Open your browser automatically

**If your browser doesn't open:**
1. Open any web browser
2. Go to: `https://localhost:9000`
3. Click "Advanced" → "Proceed to localhost" (the security warning is normal)

---

## First-Time Login

**Default password:** `oread`

⚠️ **CHANGE THIS IMMEDIATELY!**

1. Click Settings (gear icon)
2. Scroll to "Change Password"
3. Enter:
   - Current: `oread`
   - New: (your secure password)
4. Click "Change Password"

---

## Stopping Oread

**Option 1: Press `Ctrl+C` in the terminal where it's running**

**Option 2: Run the stop script:**
```bash
./stop-oread.sh
```

---

## Troubleshooting

### "Command not found: git"

**macOS:**
```bash
xcode-select --install
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install git
```

---

### "Model not found" error

You need to download an AI model. See [INSTALLATION.md](INSTALLATION.md) for detailed recommendations.

**Quick options:**

**For most users (balanced):**
```bash
cd models/
wget https://huggingface.co/lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
```

**For lower-end hardware:**
```bash
cd models/
wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf
```

**For better quality (needs more RAM/GPU):**
```bash
cd models/
wget https://huggingface.co/NousResearch/Hermes-3-Llama-3.1-8B-GGUF/resolve/main/Hermes-3-Llama-3.1-8B.Q4_K_M.gguf
```

⚠️ **Important:** Research any model before downloading. Some are trained without content filters. Choose what aligns with your values and intended use.

---

### "Port already in use"

Something is already running on port 9000 or 9001.

**Fix:**
```bash
./stop-oread.sh
./start-oread.sh
```

---

### Responses are very slow

**Try these:**

1. **Enable GPU acceleration** (if you have one):
   - Edit `inference/.env`
   - Change `LLM_N_GPU_LAYERS=0` to `LLM_N_GPU_LAYERS=-1`
   - Restart Oread

2. **Use a smaller model** - Download a 7B model instead of 12B+

3. **Disable memory and web search**:
   - Go to Settings
   - Turn off "Enable Memory"
   - Turn off "Enable Web Search"

---

## Common Questions

**Q: Is this safe?**  
A: Yes! Everything runs on your computer. No data leaves your machine (except optional web search).

**Q: Will this use a lot of disk space?**  
A: The AI model is 4-5GB. The application itself is under 1GB.

**Q: Can I use this on multiple computers?**  
A: Yes! Install on each computer, or copy the entire `oread/` folder.

**Q: Can I delete it later?**  
A: Yes. Just delete the `oread/` folder. Export your data first if you want to keep it (Settings → Download Backup).

**Q: Do I need to be connected to the internet?**  
A: Only for initial setup and optional web search. After that, Oread works 100% offline.

---

## Next Steps

- **Read the full docs:** [README.md](README.md)
- **Learn about AI:** [FAQ.md](FAQ.md)
- **Understand safety:** [SECURITY_ETHICS_SAFETY.md](SECURITY_ETHICS_SAFETY.md)
- **Get help:** [GitHub Issues](https://github.com/sleddd/oread/issues)

---

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `install-macos.sh` | Install Oread on macOS |
| `install-linux.sh` | Install Oread on Linux |
| `start-oread.sh` | Start Oread |
| `stop-oread.sh` | Stop Oread |
| `update-oread.sh` | Update to latest version |

---

**Welcome to Oread! Enjoy your privacy-first AI companion.** 🎉
#!/bin/bash

# Oread - Linux Installation Script
# This script automates the installation process for non-technical users
# Supports: Ubuntu/Debian, Fedora, Arch Linux

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo "========================================="
    echo "$1"
    echo "========================================="
    echo ""
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get user confirmation
confirm() {
    read -p "$1 (y/n): " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

# Detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        DISTRO=$DISTRIB_ID
    else
        DISTRO="unknown"
    fi
    
    echo "$DISTRO" | tr '[:upper:]' '[:lower:]'
}

# Clear screen and show welcome
clear
print_header "🌟 Welcome to Oread Installation (Linux)"

echo "This script will install Oread and all required dependencies."
echo "It will:"
echo "  • Detect your Linux distribution"
echo "  • Install Node.js 18"
echo "  • Install Python 3.11"
echo "  • Install build tools"
echo "  • Install all Oread dependencies"
echo "  • Help you download an AI model"
echo ""
echo "⏱️  Estimated time: 15-30 minutes (depending on internet speed)"
echo ""

if ! confirm "Do you want to continue?"; then
    print_error "Installation cancelled by user."
    exit 1
fi

# Store the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Detect distribution
print_header "Step 1/9: Detecting Linux Distribution"
DISTRO=$(detect_distro)
print_status "Detected distribution: $DISTRO"

case "$DISTRO" in
    ubuntu|debian|pop|linuxmint)
        PKG_MANAGER="apt"
        print_success "Using APT package manager"
        ;;
    fedora|rhel|centos)
        PKG_MANAGER="dnf"
        print_success "Using DNF package manager"
        ;;
    arch|manjaro)
        PKG_MANAGER="pacman"
        print_success "Using Pacman package manager"
        ;;
    *)
        print_error "Unsupported distribution: $DISTRO"
        print_error "This script supports: Ubuntu, Debian, Fedora, Arch Linux"
        print_error "You'll need to install dependencies manually."
        exit 1
        ;;
esac

# Step 2: Update package manager
print_header "Step 2/9: Updating Package Manager"

print_status "Updating package lists (requires sudo)..."
case "$PKG_MANAGER" in
    apt)
        sudo apt update
        ;;
    dnf)
        sudo dnf check-update || true
        ;;
    pacman)
        sudo pacman -Sy
        ;;
esac
print_success "Package lists updated"

# Step 3: Install Node.js
print_header "Step 3/9: Installing Node.js"

if command_exists node; then
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -ge 18 ]; then
        print_success "Node.js $(node --version) is already installed"
        SKIP_NODE=true
    else
        print_warning "Node.js version is too old. Will install v18..."
        SKIP_NODE=false
    fi
else
    SKIP_NODE=false
fi

if [ "$SKIP_NODE" = false ]; then
    case "$PKG_MANAGER" in
        apt)
            print_status "Installing Node.js 18 via NodeSource repository..."
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
            sudo apt install -y nodejs
            ;;
        dnf)
            print_status "Installing Node.js 18..."
            sudo dnf install -y nodejs
            ;;
        pacman)
            print_status "Installing Node.js..."
            sudo pacman -S --noconfirm nodejs npm
            ;;
    esac
    print_success "Node.js installed successfully"
fi

# Step 4: Install Python
print_header "Step 4/9: Installing Python 3.11"

if command_exists python3.11; then
    print_success "Python 3.11 is already installed"
elif command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
        print_success "Python $(python3 --version) is already installed"
    else
        print_status "Installing Python 3.11..."
        case "$PKG_MANAGER" in
            apt)
                sudo apt install -y python3.11 python3.11-venv python3-pip
                ;;
            dnf)
                sudo dnf install -y python3.11 python3-pip
                ;;
            pacman)
                sudo pacman -S --noconfirm python python-pip
                ;;
        esac
        print_success "Python installed successfully"
    fi
else
    print_status "Installing Python 3.11..."
    case "$PKG_MANAGER" in
        apt)
            sudo apt install -y python3.11 python3.11-venv python3-pip
            ;;
        dnf)
            sudo dnf install -y python3.11 python3-pip
            ;;
        pacman)
            sudo pacman -S --noconfirm python python-pip
            ;;
    esac
    print_success "Python installed successfully"
fi

# Step 5: Install Build Tools
print_header "Step 5/9: Installing Build Tools"

print_status "Installing build essentials..."
case "$PKG_MANAGER" in
    apt)
        sudo apt install -y build-essential cmake git curl
        ;;
    dnf)
        sudo dnf groupinstall -y "Development Tools"
        sudo dnf install -y cmake git curl
        ;;
    pacman)
        sudo pacman -S --noconfirm base-devel cmake git curl
        ;;
esac
print_success "Build tools installed"

# Step 6: Check for GPU Support
print_header "Step 6/9: Checking GPU Support"

if command_exists nvidia-smi && nvidia-smi &>/dev/null; then
    print_success "NVIDIA GPU detected!"
    print_status "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader)"
    
    if confirm "Do you want to install CUDA support for faster inference?"; then
        GPU_SUPPORT="cuda"
        print_warning "CUDA installation can be complex. We'll try, but it may fail."
        print_status "Installing CUDA toolkit..."
        
        case "$PKG_MANAGER" in
            apt)
                sudo apt install -y nvidia-cuda-toolkit
                ;;
            dnf)
                sudo dnf install -y cuda
                ;;
            pacman)
                sudo pacman -S --noconfirm cuda
                ;;
        esac
    else
        GPU_SUPPORT="none"
        print_status "Will use CPU-only mode"
    fi
else
    GPU_SUPPORT="none"
    print_status "No NVIDIA GPU detected. Using CPU mode."
fi

# Step 7: Install Node.js Dependencies
print_header "Step 7/9: Installing Node.js Dependencies"

print_status "Installing backend dependencies..."
cd "$SCRIPT_DIR/backend"
npm install
print_success "Backend dependencies installed"

print_status "Installing frontend dependencies..."
cd "$SCRIPT_DIR/frontend"
npm install
npm run build
print_success "Frontend dependencies installed and built"

# Step 8: Install Python Dependencies
print_header "Step 8/9: Installing Python Dependencies"

cd "$SCRIPT_DIR/inference"

# Determine which Python command to use
if command_exists python3.11; then
    PYTHON_CMD="python3.11"
elif command_exists python3; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

print_status "Creating Python virtual environment..."
$PYTHON_CMD -m venv venv
source venv/bin/activate

print_status "Upgrading pip..."
pip install --upgrade pip

print_status "Installing Python packages (this may take 5-10 minutes)..."

if [ "$GPU_SUPPORT" = "cuda" ]; then
    print_status "Installing with CUDA support..."
    CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --no-cache-dir
    pip install -r requirements.txt
    
    if python3 -c "import llama_cpp; print('CUDA' if llama_cpp.llama_supports_gpu_offload() else 'CPU')" 2>/dev/null | grep -q "CUDA"; then
        print_success "Python dependencies installed with CUDA GPU support!"
    else
        print_warning "CUDA compilation may have failed. Using CPU mode."
    fi
else
    pip install -r requirements.txt
    print_success "Python dependencies installed (CPU mode)"
fi

deactivate

# Step 9: Download Emotion Model
print_header "Step 9/9: Downloading Emotion Detection Model"

cd "$SCRIPT_DIR/models"

if [ -d "roberta_emotions_onnx" ] && [ -f "roberta_emotions_onnx/model.onnx" ]; then
    print_success "Emotion model already downloaded"
else
    print_status "Downloading emotion detection model..."
    
    mkdir -p roberta_emotions_onnx
    cd roberta_emotions_onnx
    
    curl -L -o config.json https://huggingface.co/arpanghoshal/roberta-base-emotion-classifier-onnx/resolve/main/config.json
    curl -L -o model.onnx https://huggingface.co/arpanghoshal/roberta-base-emotion-classifier-onnx/resolve/main/model.onnx
    curl -L -o tokenizer.json https://huggingface.co/arpanghoshal/roberta-base-emotion-classifier-onnx/resolve/main/tokenizer.json
    curl -L -o tokenizer_config.json https://huggingface.co/arpanghoshal/roberta-base-emotion-classifier-onnx/resolve/main/tokenizer_config.json
    
    print_success "Emotion model downloaded"
fi

# Configure Environment Files
print_header "Configuring Environment Files"

cd "$SCRIPT_DIR"

# Backend .env
if [ ! -f "backend/.env" ]; then
    print_status "Creating backend configuration..."
    cp backend/.env.example backend/.env
    
    SESSION_SECRET=$(openssl rand -hex 32)
    sed -i "s/your-random-secret-here-change-this/$SESSION_SECRET/" backend/.env
    
    print_success "Backend configuration created"
else
    print_success "Backend configuration already exists"
fi

# Inference .env
if [ ! -f "inference/.env" ]; then
    print_status "Creating inference configuration..."
    cp inference/.env.example inference/.env
    
    # Set GPU layers based on detection
    if [ "$GPU_SUPPORT" = "cuda" ]; then
        sed -i "s/LLM_N_GPU_LAYERS=.*/LLM_N_GPU_LAYERS=-1/" inference/.env
    else
        sed -i "s/LLM_N_GPU_LAYERS=.*/LLM_N_GPU_LAYERS=0/" inference/.env
    fi
    
    print_success "Inference configuration created"
else
    print_success "Inference configuration already exists"
fi

# Check if model exists
cd "$SCRIPT_DIR/models"
MODEL_COUNT=$(ls -1 *.gguf 2>/dev/null | wc -l)

if [ "$MODEL_COUNT" -eq 0 ]; then
    print_header "⚠️  AI Model Required - YOU MUST DOWNLOAD"
    print_warning "Oread does NOT automatically download models."
    print_warning "You are responsible for obtaining and legally using models."
    echo ""
    echo "MODEL OPTIONS:"
    echo ""
    echo "1. Llama-3.1-8B-Instruct (Censored, Recommended for Most Users)"
    echo "   - Size: 4.9GB"
    echo "   - Built-in safety guardrails"
    echo "   - Link: https://huggingface.co/lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF"
    echo ""
    echo "2. Nous-Hermes-3-Llama-3.1-8B (Moderate Censorship)"
    echo "   - Size: 4.9GB"
    echo "   - Balanced for roleplay"
    echo "   - Link: https://huggingface.co/NousResearch/Hermes-3-Llama-3.1-8B-GGUF"
    echo ""
    echo "3. MN-Violet-Lotus-12B (Uncensored - Tested Model)"
    echo "   - Size: 4.3GB"
    echo "   - NO content restrictions - requires user responsibility"
    echo "   - Link: https://huggingface.co/MaziyarPanahi/MN-Violet-Lotus-12B-v1.1-GGUF"
    echo ""
    echo "4. Phi-3-Mini-4K (Low-End Hardware, Censored)"
    echo "   - Size: 2.3GB"
    echo "   - For systems with limited RAM"
    echo "   - Link: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf"
    echo ""
    echo "CHOOSE A MODEL THAT ALIGNS WITH YOUR VALUES!"
    echo ""
    echo "After downloading, edit inference/.env and set:"
    echo "  LLM_MODEL_PATH=models/YOUR_MODEL_NAME.gguf"
    echo ""
    print_warning "YOU are responsible for model choice and licensing compliance!"
    print_warning "Oread will NOT work until you download a model!"
    echo ""
    echo "See INSTALLATION.md for full download commands and more details."
else
    FIRST_MODEL=$(ls -1 *.gguf | head -1)
    print_success "Found model: $FIRST_MODEL"

    MODEL_PATH="models/$FIRST_MODEL"
    cd "$SCRIPT_DIR"
    sed -i "s|LLM_MODEL_PATH=.*|LLM_MODEL_PATH=$MODEL_PATH|" inference/.env
fi

# Final success message
cd "$SCRIPT_DIR"
print_header "✅ Installation Complete!"

echo "Oread has been successfully installed!"
echo ""
echo "Next steps:"
echo "  1. Start Oread:"
echo "     ./start-oread.sh"
echo ""
echo "  2. Open your browser to:"
echo "     https://localhost:9000"
echo ""
echo "  3. Login with default password: oread"
echo "     (Change it immediately in Settings!)"
echo ""
echo "  4. Accept the Terms of Service"
echo ""
echo "  5. Start chatting!"
echo ""
print_status "For help, see: README.md or visit GitHub Issues"
echo ""

if confirm "Would you like to start Oread now?"; then
    print_status "Starting Oread..."
    ./start-oread.sh
else
    print_success "Installation complete. Run ./start-oread.sh when ready."
fi

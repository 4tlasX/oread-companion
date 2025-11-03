#!/bin/bash

# Oread - macOS Installation Script
# This script automates the installation process for non-technical users

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

# Clear screen and show welcome
clear
print_header "🌟 Welcome to Oread Installation (macOS)"

echo "This script will install Oread and all required dependencies."
echo "It will:"
echo "  • Install Homebrew (if not present)"
echo "  • Install Node.js 18"
echo "  • Install Python 3.11"
echo "  • Install Xcode Command Line Tools"
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

# Step 1: Check/Install Homebrew
print_header "Step 1/8: Checking Homebrew"

if command_exists brew; then
    print_success "Homebrew is already installed"
    print_status "Updating Homebrew..."
    brew update
else
    print_status "Homebrew not found. Installing..."
    echo "You may be prompted for your password."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for Apple Silicon Macs
    if [[ $(uname -m) == 'arm64' ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    
    print_success "Homebrew installed successfully"
fi

# Step 2: Install/Check Node.js
print_header "Step 2/8: Checking Node.js"

if command_exists node; then
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -ge 18 ]; then
        print_success "Node.js $(node --version) is already installed"
    else
        print_warning "Node.js version is too old. Upgrading to v18..."
        brew upgrade node@18
    fi
else
    print_status "Installing Node.js 18..."
    brew install node@18
    print_success "Node.js installed successfully"
fi

# Step 3: Install/Check Python
print_header "Step 3/8: Checking Python"

if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
        print_success "Python $(python3 --version) is already installed"
    else
        print_warning "Python version is too old. Installing Python 3.11..."
        brew install python@3.11
    fi
else
    print_status "Installing Python 3.11..."
    brew install python@3.11
    print_success "Python installed successfully"
fi

# Step 4: Install Xcode Command Line Tools
print_header "Step 4/8: Checking Xcode Command Line Tools"

if xcode-select -p &>/dev/null; then
    print_success "Xcode Command Line Tools are already installed"
else
    print_status "Installing Xcode Command Line Tools..."
    print_warning "A popup will appear. Click 'Install' and wait for it to complete."
    xcode-select --install
    
    print_status "Waiting for Xcode installation to complete..."
    echo "Press ENTER when installation is finished..."
    read
    
    print_success "Xcode Command Line Tools installed"
fi

# Step 5: Install Node.js Dependencies
print_header "Step 5/8: Installing Node.js Dependencies"

print_status "Installing backend dependencies..."
cd "$SCRIPT_DIR/backend"
npm install
print_success "Backend dependencies installed"

print_status "Installing frontend dependencies..."
cd "$SCRIPT_DIR/frontend"
npm install
npm run build
print_success "Frontend dependencies installed and built"

# Step 6: Install Python Dependencies
print_header "Step 6/8: Installing Python Dependencies"

cd "$SCRIPT_DIR/inference"

print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

print_status "Upgrading pip..."
pip install --upgrade pip

print_status "Installing Python packages (this may take 5-10 minutes)..."
pip install -r requirements.txt

# Check if Metal compilation succeeded
if python3 -c "import llama_cpp; print('Metal' if llama_cpp.llama_supports_gpu_offload() else 'CPU')" 2>/dev/null | grep -q "Metal"; then
    print_success "Python dependencies installed with Metal GPU support!"
else
    print_warning "Python dependencies installed (CPU mode)"
    print_warning "Metal GPU acceleration may not be available"
fi

deactivate

# Step 7: Download Emotion Model
print_header "Step 7/8: Downloading Emotion Detection Model"

cd "$SCRIPT_DIR/models"

if [ -d "roberta_emotions_onnx" ] && [ -f "roberta_emotions_onnx/model.onnx" ]; then
    print_success "Emotion model already downloaded"
else
    print_status "Downloading emotion detection model..."
    
    # Create directory
    mkdir -p roberta_emotions_onnx
    cd roberta_emotions_onnx
    
    # Download files
    curl -L -o config.json https://huggingface.co/arpanghoshal/roberta-base-emotion-classifier-onnx/resolve/main/config.json
    curl -L -o model.onnx https://huggingface.co/arpanghoshal/roberta-base-emotion-classifier-onnx/resolve/main/model.onnx
    curl -L -o tokenizer.json https://huggingface.co/arpanghoshal/roberta-base-emotion-classifier-onnx/resolve/main/tokenizer.json
    curl -L -o tokenizer_config.json https://huggingface.co/arpanghoshal/roberta-base-emotion-classifier-onnx/resolve/main/tokenizer_config.json
    
    print_success "Emotion model downloaded"
fi

# Step 8: Configure Environment Files
print_header "Step 8/8: Configuring Environment Files"

cd "$SCRIPT_DIR"

# Backend .env
if [ ! -f "backend/.env" ]; then
    print_status "Creating backend configuration..."
    cp backend/.env.example backend/.env
    
    # Generate random session secret
    SESSION_SECRET=$(openssl rand -hex 32)
    
    # Update .env with generated secret
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/your-random-secret-here-change-this/$SESSION_SECRET/" backend/.env
    else
        sed -i "s/your-random-secret-here-change-this/$SESSION_SECRET/" backend/.env
    fi
    
    print_success "Backend configuration created"
else
    print_success "Backend configuration already exists"
fi

# Inference .env
if [ ! -f "inference/.env" ]; then
    print_status "Creating inference configuration..."
    cp inference/.env.example inference/.env
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
    # Model exists, update .env
    FIRST_MODEL=$(ls -1 *.gguf | head -1)
    print_success "Found model: $FIRST_MODEL"

    MODEL_PATH="models/$FIRST_MODEL"
    cd "$SCRIPT_DIR"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|LLM_MODEL_PATH=.*|LLM_MODEL_PATH=$MODEL_PATH|" inference/.env
    else
        sed -i "s|LLM_MODEL_PATH=.*|LLM_MODEL_PATH=$MODEL_PATH|" inference/.env
    fi
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

# Ask if user wants to start now
if confirm "Would you like to start Oread now?"; then
    print_status "Starting Oread..."
    ./start-oread.sh
else
    print_success "Installation complete. Run ./start-oread.sh when ready."
fi

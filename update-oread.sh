#!/bin/bash

# Oread Update Script
# Updates Oread to the latest version

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

confirm() {
    read -p "$1 (y/n): " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

clear
echo "========================================="
echo "🔄 Oread Update Script"
echo "========================================="
echo ""

# Check if Oread is running
if lsof -Pi :9000 -sTCP:LISTEN -t >/dev/null 2>&1 || lsof -Pi :9001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_warning "Oread is currently running"
    if confirm "Stop Oread before updating?"; then
        ./stop-oread.sh
        sleep 2
    else
        print_error "Cannot update while Oread is running"
        exit 1
    fi
fi

# Backup user data
print_status "Creating backup of user data..."
BACKUP_DIR="backups/update-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -d "data" ]; then
    cp -r data "$BACKUP_DIR/"
    print_success "Backup created: $BACKUP_DIR"
else
    print_warning "No data directory found, skipping backup"
fi

# Check git status
print_status "Checking for local changes..."
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    print_warning "You have uncommitted changes"
    print_warning "These will be overwritten by the update"
    
    if ! confirm "Continue anyway?"; then
        print_error "Update cancelled"
        exit 1
    fi
fi

# Fetch updates
print_status "Fetching updates from GitHub..."
git fetch origin

# Check if updates available
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u} 2>/dev/null || echo "")

if [ -z "$REMOTE" ]; then
    print_error "Could not find remote branch"
    print_error "Are you connected to the internet?"
    exit 1
fi

if [ "$LOCAL" = "$REMOTE" ]; then
    print_success "Oread is already up to date!"
    exit 0
fi

# Show what will be updated
print_status "Updates available:"
echo ""
git log --oneline --graph HEAD..@{u}
echo ""

if ! confirm "Apply these updates?"; then
    print_error "Update cancelled"
    exit 1
fi

# Pull updates
print_status "Downloading updates..."
git pull origin main

# Update Node.js dependencies
print_status "Updating backend dependencies..."
cd "$SCRIPT_DIR/backend"
npm install

print_status "Updating frontend dependencies..."
cd "$SCRIPT_DIR/frontend"
npm install
npm run build

# Update Python dependencies
print_status "Updating Python dependencies..."
cd "$SCRIPT_DIR/inference"

if [ -d "venv" ]; then
    source venv/bin/activate
fi

pip install --upgrade pip
pip install -r requirements.txt

if [ -d "venv" ]; then
    deactivate
fi

# Success
cd "$SCRIPT_DIR"
echo ""
echo "========================================="
print_success "✅ Oread updated successfully!"
echo "========================================="
echo ""
print_status "Backup saved to: $BACKUP_DIR"
echo ""
print_status "To start Oread: ./start-oread.sh"
echo ""

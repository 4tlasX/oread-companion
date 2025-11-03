#!/bin/bash

# Oread Stop Script
# Stops all Oread processes

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

echo "========================================="
echo "⏹️  Stopping Oread"
echo "========================================="
echo ""

# Stop processes listening on port 9000 (backend)
if lsof -Pi :9000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_status "Stopping backend server (port 9000)..."
    BACKEND_PID=$(lsof -Pi :9000 -sTCP:LISTEN -t)
    kill $BACKEND_PID 2>/dev/null
    sleep 2
    
    # Force kill if still running
    if kill -0 $BACKEND_PID 2>/dev/null; then
        print_warning "Backend didn't stop gracefully, force killing..."
        kill -9 $BACKEND_PID 2>/dev/null
    fi
    
    print_success "Backend stopped"
else
    print_status "Backend not running"
fi

# Stop processes listening on port 9001 (inference)
if lsof -Pi :9001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_status "Stopping inference service (port 9001)..."
    INFERENCE_PID=$(lsof -Pi :9001 -sTCP:LISTEN -t)
    kill $INFERENCE_PID 2>/dev/null
    sleep 2
    
    # Force kill if still running
    if kill -0 $INFERENCE_PID 2>/dev/null; then
        print_warning "Inference didn't stop gracefully, force killing..."
        kill -9 $INFERENCE_PID 2>/dev/null
    fi
    
    print_success "Inference service stopped"
else
    print_status "Inference service not running"
fi

echo ""
print_success "✅ Oread stopped"
echo ""

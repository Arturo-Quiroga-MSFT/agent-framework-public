#!/bin/bash

# RDBMS Assistant UI - Quick Start Script
# This script helps you get the Tauri app running quickly

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        RDBMS Assistant - Tauri UI Setup                     ║"
echo "║        Quick Start Script                                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the UI directory
if [ ! -f "package.json" ]; then
    echo "${RED}❌ Error: Please run this script from the UI directory${NC}"
    echo "   cd DBMS-ASSISTANT/UI"
    exit 1
fi

echo "🔍 Checking prerequisites..."
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "${RED}❌ Node.js not found${NC}"
    echo "   Install from: https://nodejs.org/"
    exit 1
else
    NODE_VERSION=$(node --version)
    echo "${GREEN}✓${NC} Node.js: $NODE_VERSION"
fi

# Check npm
if ! command -v npm &> /dev/null; then
    echo "${RED}❌ npm not found${NC}"
    exit 1
else
    NPM_VERSION=$(npm --version)
    echo "${GREEN}✓${NC} npm: $NPM_VERSION"
fi

# Check Rust
if ! command -v rustc &> /dev/null; then
    echo "${YELLOW}⚠️  Rust not found${NC}"
    echo "   Install with: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    echo ""
    read -p "Continue anyway? (not recommended) [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    RUST_VERSION=$(rustc --version)
    echo "${GREEN}✓${NC} Rust: $RUST_VERSION"
fi

# Check Cargo
if ! command -v cargo &> /dev/null; then
    echo "${YELLOW}⚠️  Cargo not found${NC}"
else
    CARGO_VERSION=$(cargo --version)
    echo "${GREEN}✓${NC} Cargo: $CARGO_VERSION"
fi

echo ""
echo "📦 Checking dependencies..."
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install
    echo "${GREEN}✓${NC} Node dependencies installed"
else
    echo "${GREEN}✓${NC} Node dependencies already installed"
fi

echo ""
echo "🚀 Starting development server..."
echo ""
echo "   This will:"
echo "   1. Start Vite frontend dev server"
echo "   2. Compile Rust backend (first time may take 5-10 minutes)"
echo "   3. Launch Tauri app window"
echo ""
echo "   Press Ctrl+C to stop"
echo ""

# Wait a moment
sleep 2

# Run Tauri dev
npm run tauri dev

# RDBMS Assistant UI - Setup Guide

Complete setup instructions for the Tauri-based desktop UI.

---

## 📋 Prerequisites

### 1. System Requirements

**Operating System:**
- macOS 10.15+ (Catalina or later)
- Windows 10+ (64-bit)
- Linux (Ubuntu 22.04+, Fedora 32+, or equivalent)

**Hardware:**
- 4 GB RAM minimum (8 GB recommended)
- 500 MB free disk space
- Internet connection for initial setup

### 2. Required Software

#### A. Rust (1.70 or later)

**macOS/Linux:**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

**Windows:**
Download and run: https://rustup.rs/

**Verify installation:**
```bash
rustc --version
cargo --version
```

#### B. Node.js (18 or later)

**macOS (with Homebrew):**
```bash
brew install node
```

**Windows:**
Download from: https://nodejs.org/

**Linux:**
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Verify installation:**
```bash
node --version  # Should be v18.x or higher
npm --version
```

#### C. System-Specific Dependencies

**macOS:**
```bash
# Xcode Command Line Tools (if not already installed)
xcode-select --install

# WebKit dependencies (usually pre-installed)
```

**Windows:**
```powershell
# Microsoft C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Install "Desktop development with C++" workload
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install -y \
  libwebkit2gtk-4.1-dev \
  build-essential \
  curl \
  wget \
  file \
  libxdo-dev \
  libssl-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev
```

**Linux (Fedora):**
```bash
sudo dnf install \
  webkit2gtk4.1-devel \
  openssl-devel \
  curl \
  wget \
  file \
  libappindicator-gtk3-devel \
  librsvg2-devel
```

### 3. Python Environment

The UI integrates with the existing Python agent. Ensure you have:

```bash
# Navigate to repository root
cd /Users/arturoquiroga/GITHUB/agent-framework-public

# Verify Python virtual environment exists
ls .venv/

# Activate virtual environment
source .venv/bin/activate

# Verify agent framework is installed
python -c "import agent_framework; print('✓ Agent Framework installed')"
```

---

## 🚀 Installation Steps

### Step 1: Navigate to UI Directory

```bash
cd /Users/arturoquiroga/GITHUB/agent-framework-public/DBMS-ASSISTANT/UI
```

### Step 2: Install Node Dependencies

```bash
npm install
```

This will install:
- Tauri CLI
- React and React DOM
- Vite (build tool)
- TypeScript
- Lucide React (icons)
- All development dependencies

**Expected output:**
```
added 300+ packages in 30s
```

### Step 3: Verify Installation

```bash
# Check Tauri CLI
npm run tauri -- --version

# Should output: tauri-cli 2.x.x
```

### Step 4: Build Rust Backend (First Time)

```bash
# This will download and compile Rust dependencies
# First build takes 5-10 minutes
npm run tauri build --debug
```

**Expected output:**
```
   Compiling tauri v2.0.0
   Compiling rdbms-assistant v1.0.0
    Finished dev [unoptimized + debuginfo] target(s) in 8m 23s
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file in the UI directory:

```bash
# Python Agent Configuration
PYTHON_EXECUTABLE=/Users/arturoquiroga/GITHUB/agent-framework-public/.venv/bin/python
PYTHON_AGENT_PATH=../dba_assistant.py

# Development
RUST_LOG=info
TAURI_DEBUG=true
```

### Database Connection

Connection details are inherited from the parent directory's `.env` file:
```
../. env → Contains SERVER_NAME, DATABASE_NAME, etc.
```

No additional configuration needed!

---

## ▶️ Running the Application

### Development Mode (with Hot Reload)

```bash
npm run tauri dev
```

**What happens:**
1. Vite starts frontend dev server on `http://localhost:1420`
2. Rust backend compiles (if needed)
3. Tauri app window opens
4. Changes to frontend auto-reload
5. Changes to Rust require restart

**Keyboard shortcuts in dev mode:**
- **Cmd/Ctrl + R**: Reload frontend
- **Cmd/Ctrl + Shift + I**: Open DevTools
- **Cmd/Ctrl + Q**: Quit app

### Production Build

```bash
# Build optimized production app
npm run tauri build
```

**Output locations:**

**macOS:**
```
src-tauri/target/release/bundle/macos/RDBMS Assistant.app
src-tauri/target/release/bundle/dmg/RDBMS Assistant_1.0.0_universal.dmg
```

**Windows:**
```
src-tauri\target\release\bundle\msi\RDBMS Assistant_1.0.0_x64_en-US.msi
```

**Linux:**
```
src-tauri/target/release/bundle/appimage/rdbms-assistant_1.0.0_amd64.AppImage
src-tauri/target/release/bundle/deb/rdbms-assistant_1.0.0_amd64.deb
```

---

## 🧪 Testing the Setup

### 1. Test Frontend Only

```bash
# Start Vite dev server without Tauri
npm run dev

# Open browser to http://localhost:1420
```

### 2. Test Rust Backend

```bash
# Run Rust tests
cd src-tauri
cargo test
```

### 3. Test Python Integration

```bash
# From UI directory
cd src-tauri
cargo test python_bridge::tests --  --nocapture
```

### 4. Full Integration Test

```bash
# Run the complete app
npm run tauri dev

# In the app:
# 1. Type a question: "How many tables are in the database?"
# 2. Click "Send Query"
# 3. Verify response appears
```

---

## 🐛 Troubleshooting

### Issue: "rustc not found"

**Solution:**
```bash
# Ensure Rust is in PATH
source $HOME/.cargo/env

# Or restart terminal
```

### Issue: "tauri command not found"

**Solution:**
```bash
# Install dependencies again
npm install

# Or run directly
npx tauri --version
```

### Issue: "webkit2gtk not found" (Linux)

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install libwebkit2gtk-4.1-dev

# Fedora
sudo dnf install webkit2gtk4.1-devel
```

### Issue: "Python module not found"

**Solution:**
```bash
# Activate virtual environment
cd ../../
source .venv/bin/activate

# Install missing modules
pip install -r DBMS-ASSISTANT/requirements.txt

# Return to UI directory
cd DBMS-ASSISTANT/UI
```

### Issue: Build fails with "linker error"

**Solution:**
```bash
# Clean and rebuild
npm run clean
npm install
npm run tauri dev
```

### Issue: "Port 1420 already in use"

**Solution:**
```bash
# Kill process using port 1420
lsof -ti:1420 | xargs kill -9

# Or change port in vite.config.ts
```

---

## 📦 Building for Distribution

### macOS

```bash
# Build universal binary (Intel + Apple Silicon)
npm run tauri build -- --target universal-apple-darwin

# Sign and notarize (requires Apple Developer account)
# See: https://v2.tauri.app/distribute/sign/macos/
```

### Windows

```bash
# Build MSI installer
npm run tauri build -- --target x86_64-pc-windows-msvc

# Code signing (optional, requires certificate)
# See: https://v2.tauri.app/distribute/sign/windows/
```

### Linux

```bash
# Build AppImage and DEB
npm run tauri build -- --target x86_64-unknown-linux-gnu

# RPM (Fedora/RHEL)
npm run tauri build -- --bundles rpm
```

---

## 🔄 Updating Dependencies

### Update Node Packages

```bash
# Check for updates
npm outdated

# Update all packages
npm update

# Update specific package
npm install @tauri-apps/api@latest
```

### Update Rust Crates

```bash
cd src-tauri

# Check for updates
cargo outdated

# Update Cargo.lock
cargo update

# Update specific crate
cargo update -p tauri
```

---

## 📚 Next Steps

1. **Read Development Guide**: [DEVELOPMENT.md](DEVELOPMENT.md)
2. **Understand Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
3. **Review Main README**: [../README.md](../README.md)
4. **Try Example Queries**: See parent directory's documentation

---

## ✅ Setup Checklist

- [ ] Rust installed and in PATH
- [ ] Node.js 18+ installed
- [ ] System dependencies installed
- [ ] Python virtual environment activated
- [ ] Node packages installed (`npm install`)
- [ ] First build completed (`npm run tauri build --debug`)
- [ ] Dev mode works (`npm run tauri dev`)
- [ ] App window opens successfully
- [ ] Can send test query and see response

---

**Setup Issues?** Check the [Troubleshooting](#-troubleshooting) section or open an issue on GitHub.

**Ready to develop?** Continue to [DEVELOPMENT.md](DEVELOPMENT.md) for the development workflow guide.

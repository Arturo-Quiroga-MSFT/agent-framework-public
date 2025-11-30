# RDBMS Assistant - Tauri Desktop UI

> Modern, lightweight, secure desktop interface for the RDBMS Database Assistant

**Framework**: Tauri 2.0  
**Backend**: Rust + Python (via Pyo3)  
**Frontend**: React + TypeScript  
**Status**: 🚧 In Development

---

## 🎯 Why Tauri?

Based on comprehensive analysis (see [TAURI-ELECTRON-COMPARISON.md](TAURI-ELECTRON-COMPARISON.md)):

✅ **96% smaller bundle size** (3-15 MB vs 100-150 MB)  
✅ **58% less memory usage** (30-40 MB vs 200-300 MB)  
✅ **2-4x faster startup** (<0.5s vs 1-2s)  
✅ **Superior security** (Rust memory safety + restricted permissions)  
✅ **Native Python integration** (via Pyo3 FFI)  
✅ **Modern architecture** (future-proof)  

Perfect for DBAs who need fast, secure, lightweight tools for database administration.

---

## 📁 Project Structure

```
UI/
├── README.md                    # This file
├── TAURI-ELECTRON-COMPARISON.md # Framework comparison analysis
├── package.json                 # Node.js dependencies
├── tsconfig.json               # TypeScript configuration
├── vite.config.ts              # Vite build configuration
├── index.html                  # Entry HTML
│
├── src/                        # React frontend source
│   ├── main.tsx               # React entry point
│   ├── App.tsx                # Main App component
│   ├── App.css                # Styling
│   ├── components/            # React components
│   │   ├── QueryInput.tsx
│   │   ├── ResultsDisplay.tsx
│   │   ├── ConnectionPanel.tsx
│   │   └── StatusBar.tsx
│   ├── services/              # Frontend services
│   │   └── tauri-api.ts      # Tauri IPC wrapper
│   └── types/                 # TypeScript types
│       └── index.ts
│
├── src-tauri/                  # Rust backend source
│   ├── Cargo.toml             # Rust dependencies
│   ├── tauri.conf.json        # Tauri configuration
│   ├── build.rs               # Build script
│   ├── icons/                 # App icons
│   └── src/
│       ├── main.rs            # Rust entry point
│       ├── commands.rs        # Tauri commands (IPC)
│       ├── python_bridge.rs   # Pyo3 integration
│       └── lib.rs             # Library exports
│
└── docs/                       # Documentation
    ├── SETUP.md               # Setup instructions
    ├── DEVELOPMENT.md         # Development guide
    └── ARCHITECTURE.md        # Technical architecture
```

---

## 🚀 Quick Start

### Prerequisites

1. **Rust** (1.70+)
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. **Node.js** (18+)
   ```bash
   # Already available in your system
   node --version
   ```

3. **System Dependencies** (macOS)
   ```bash
   # Xcode Command Line Tools (if not installed)
   xcode-select --install
   ```

### Installation

```bash
# Navigate to UI directory
cd DBMS-ASSISTANT/UI

# Install Node dependencies
npm install

# Install Rust dependencies (automatic on first build)
# Will be triggered by npm run tauri dev
```

### Development

```bash
# Start development server with hot reload
npm run tauri dev

# This will:
# 1. Start Vite dev server (frontend with hot reload)
# 2. Compile Rust backend
# 3. Launch Tauri app window
```

### Build

```bash
# Build production app
npm run tauri build

# Output will be in:
# src-tauri/target/release/bundle/
# - .app (macOS)
# - .dmg (macOS installer)
# - .exe (Windows)
# - .deb/.appimage (Linux)
```

---

## 🏗️ Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Tauri Desktop App                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           React Frontend (TypeScript)                │  │
│  │  - Modern UI components                              │  │
│  │  - Real-time query input                            │  │
│  │  - Results visualization                             │  │
│  │  - Connection management                             │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│                       │ Tauri IPC                          │
│                       │ (JSON-RPC via WebSocket)           │
│                       ↓                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Rust Backend (Tauri Commands)                │  │
│  │  - Command handlers                                  │  │
│  │  - State management                                  │  │
│  │  - Security layer                                    │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│                       │ Pyo3 FFI                           │
│                       │ (Native Rust-Python calls)         │
│                       ↓                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Python Agent (dba_assistant.py)              │  │
│  │  - Agent Framework orchestration                     │  │
│  │  - MCP Server integration                            │  │
│  │  - Azure OpenAI client                               │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
└───────────────────────┼─────────────────────────────────────┘
                        │
                        │ MCP Protocol
                        ↓
               ┌────────────────────┐
               │   MSSQL MCP Server │
               │   (Node.js)        │
               └────────┬───────────┘
                        │
                        ↓
               ┌────────────────────┐
               │  Azure SQL Database│
               └────────────────────┘
```

### Key Components

1. **Frontend (React + TypeScript)**
   - Modern, responsive UI
   - Real-time query interface
   - Connection management panel
   - Results display with formatting
   - Status indicators and notifications

2. **Rust Backend (Tauri)**
   - Secure command handlers
   - Python bridge via Pyo3
   - State management
   - File system operations
   - System integrations

3. **Python Agent Integration**
   - Direct FFI calls (no IPC overhead)
   - Reuse existing `dba_assistant.py`
   - Agent Framework orchestration
   - MCP Server communication

---

## 🔧 Configuration

### Tauri Configuration (`src-tauri/tauri.conf.json`)

Key settings:
- **App name**: "RDBMS Assistant"
- **Window size**: 1200x800 (default)
- **Permissions**: File system, process, database
- **Security**: CSP enabled, dangerous-disable-asset-csp-modification disabled
- **Updates**: Built-in updater support

### Environment Variables

Create `.env` in UI directory:
```env
# Python Backend
PYTHON_PATH=../dba_assistant.py
VENV_PATH=../../.venv

# Azure Configuration (inherited from parent)
# Uses parent's .env file
```

---

## 🎨 UI Features

### Planned Components

1. **Connection Panel**
   - Server selection dropdown
   - Database selection
   - Connection status indicator
   - Quick connect button

2. **Query Input**
   - Natural language text input
   - Syntax highlighting
   - Query history
   - Suggestions/autocomplete

3. **Results Display**
   - Tabular data view
   - JSON viewer for complex results
   - Export options (CSV, JSON)
   - Copy to clipboard

4. **Status Bar**
   - Connection status
   - Last query execution time
   - Memory usage
   - Agent status

5. **Settings Panel**
   - Azure OpenAI configuration
   - MCP Server settings
   - UI preferences
   - Keyboard shortcuts

---

## 🔒 Security Features

### Tauri Security Model

✅ **Restricted Permissions**: Explicit allowlist for system access  
✅ **CSP Enforcement**: Content Security Policy prevents XSS  
✅ **Process Isolation**: Frontend and backend run in separate contexts  
✅ **Rust Memory Safety**: No buffer overflows or memory corruption  
✅ **Secure Storage**: Credentials stored in OS keychain  

### Python Integration Security

✅ **No Shell Execution**: Direct FFI calls, no subprocess spawning  
✅ **Type Safety**: Strong typing at Rust-Python boundary  
✅ **Error Isolation**: Python exceptions don't crash Rust  
✅ **Resource Limits**: Python GIL managed by Pyo3  

---

## 📊 Performance

### Expected Metrics

| Metric | Target | Notes |
|--------|--------|-------|
| **Bundle Size** | <10 MB | Excluding Python runtime |
| **Memory Usage** | 40-60 MB | With Python agent loaded |
| **Startup Time** | <500ms | Cold start |
| **Query Latency** | <50ms | IPC + FFI overhead |
| **Python Call** | <10ms | Direct FFI (no IPC) |

### Benchmarks vs Electron

- **96% smaller** bundle
- **58% less** memory
- **2-4x faster** startup

---

## 🧪 Testing

### Development Testing

```bash
# Run Tauri app in dev mode
npm run tauri dev

# Test Python integration
cargo test --manifest-path src-tauri/Cargo.toml

# Frontend tests
npm test
```

### Production Testing

```bash
# Build and test production bundle
npm run tauri build

# Install and test on macOS
open src-tauri/target/release/bundle/macos/RDBMS\ Assistant.app
```

---

## 📦 Distribution

### macOS

```bash
# Build DMG installer
npm run tauri build -- --target universal-apple-darwin

# Output: src-tauri/target/release/bundle/dmg/
# - RDBMS Assistant_1.0.0_universal.dmg
```

### Windows

```bash
# Build MSI installer
npm run tauri build -- --target x86_64-pc-windows-msvc

# Output: src-tauri/target/release/bundle/msi/
# - RDBMS Assistant_1.0.0_x64_en-US.msi
```

### Linux

```bash
# Build AppImage and DEB
npm run tauri build -- --target x86_64-unknown-linux-gnu

# Output: src-tauri/target/release/bundle/
# - appimage/rdbms-assistant_1.0.0_amd64.AppImage
# - deb/rdbms-assistant_1.0.0_amd64.deb
```

---

## 🔄 Updates

Tauri includes built-in auto-updater:

```rust
// Configured in tauri.conf.json
"updater": {
  "active": true,
  "endpoints": ["https://your-update-server.com/releases"],
  "dialog": true,
  "pubkey": "YOUR_PUBLIC_KEY"
}
```

---

## 🐛 Troubleshooting

### Rust Compilation Errors

```bash
# Clear Rust cache
cargo clean --manifest-path src-tauri/Cargo.toml

# Update Rust toolchain
rustup update
```

### Python Integration Issues

```bash
# Verify Python environment
python --version  # Should be 3.10+

# Activate venv
source ../../.venv/bin/activate

# Test Python imports
python -c "import agent_framework; print('OK')"
```

### Node/NPM Issues

```bash
# Clear npm cache
rm -rf node_modules package-lock.json
npm install
```

---

## 📚 Documentation

- **[SETUP.md](docs/SETUP.md)** - Detailed setup instructions
- **[DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Development workflow guide
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Technical architecture details
- **[TAURI-ELECTRON-COMPARISON.md](TAURI-ELECTRON-COMPARISON.md)** - Framework comparison

### External Resources

- **[Tauri Documentation](https://v2.tauri.app/)** - Official Tauri docs
- **[Pyo3 Guide](https://pyo3.rs/)** - Rust-Python integration
- **[React Docs](https://react.dev/)** - React documentation
- **[Vite Guide](https://vitejs.dev/)** - Vite build tool

---

## 🤝 Contributing

This UI is part of the RDBMS Assistant project. See main [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT (following workspace conventions)

---

## 🎯 Next Steps

1. ✅ Create project structure
2. ⏳ Set up Rust backend with Pyo3
3. ⏳ Build React frontend
4. ⏳ Integrate with Python agent
5. ⏳ Add query interface
6. ⏳ Implement connection management
7. ⏳ Add settings panel
8. ⏳ Create installers

---

**Status**: 🚧 In Active Development  
**Target Release**: Q1 2026  
**Framework**: Tauri 2.0 + React + Rust + Python (Pyo3)

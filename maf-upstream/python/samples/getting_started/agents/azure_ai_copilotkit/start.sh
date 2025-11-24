#!/bin/bash
set -euo pipefail

# Azure AI Weather Agent - CopilotKit Demo Startup Script
# Starts backend (FastAPI) and frontend (Next.js) with log files + PID tracking

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../../.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$REPO_ROOT/.venv/bin/python}"
[ -x "$PYTHON_BIN" ] || PYTHON_BIN="$(command -v python3)"

LOG_DIR="$SCRIPT_DIR/logs"
BACKEND_PID_FILE="$SCRIPT_DIR/.backend.pid"
FRONTEND_PID_FILE="$SCRIPT_DIR/.frontend.pid"

mkdir -p "$LOG_DIR"

info() { echo -e "\033[0;34m$1\033[0m"; }
success() { echo -e "\033[0;32m$1\033[0m"; }
warn() { echo -e "\033[1;33m$1\033[0m"; }
error() { echo -e "\033[0;31m$1\033[0m"; }

echo "🚀 Starting Azure AI Weather Agent - CopilotKit Demo"
echo "=================================================="
echo ""

# Always stop previous processes to avoid port conflicts
if [ -x "$SCRIPT_DIR/stop.sh" ]; then
    "$SCRIPT_DIR/stop.sh" --quiet || true
fi

# Ensure dependencies exist (install only if missing)
if [ ! -f "$SCRIPT_DIR/agent/.installed" ]; then
    info "📦 Installing backend dependencies (one-time)..."
    (cd "$SCRIPT_DIR/agent" && "$PYTHON_BIN" -m pip install -e . && touch .installed)
fi

if [ ! -d "$SCRIPT_DIR/ui/node_modules" ]; then
    info "📦 Installing frontend dependencies (one-time)..."
    (cd "$SCRIPT_DIR/ui" && npm install)
fi

# Start backend
info "🔧 Starting Backend (FastAPI on port 8200)..."
(cd "$SCRIPT_DIR/agent" && nohup "$PYTHON_BIN" src/main.py > "$LOG_DIR/backend.log" 2>&1 & echo $! > "$BACKEND_PID_FILE")

for i in {1..20}; do
    sleep 1
    if curl -s http://localhost:8200/docs > /dev/null 2>&1; then
        success "✅ Backend running at http://localhost:8200"
        break
    fi
    if [ $i -eq 20 ]; then
        error "❌ Backend failed to start. Check $LOG_DIR/backend.log"
        exit 1
    fi
done

# Start frontend
info "🎨 Starting Frontend (Next.js on port 3200)..."
(cd "$SCRIPT_DIR/ui" && nohup npm run dev > "$LOG_DIR/frontend.log" 2>&1 & echo $! > "$FRONTEND_PID_FILE")

for i in {1..40}; do
    sleep 1
    if curl -s http://localhost:3200 > /dev/null 2>&1; then
        success "✅ Frontend running at http://localhost:3200"
        break
    fi
    if [ $i -eq 40 ]; then
        warn "⚠️  Frontend still starting. Tail $LOG_DIR/frontend.log for details."
    fi
done

echo ""
echo "=================================================="
success "🎉 All services are running!"
echo "📡 Backend API: http://localhost:8200"
echo "📖 API Docs: http://localhost:8200/docs"
echo "🌐 Frontend UI: http://localhost:3200"
echo "📜 Logs: $LOG_DIR/backend.log | $LOG_DIR/frontend.log"
echo ""
echo "💡 Try these queries in the sidebar:"
echo "   - What's the weather in Toronto?"
echo "   - How's the weather in Mexico City?"
echo "   - Compare weather in Guadalajara and Monterrey"
echo ""
warn "Stop servers with ./stop.sh"
echo ""

#!/usr/bin/env bash
# start.sh — Launch PPTX Agents (backend + frontend)
#
# Usage:
#   ./start.sh           # kill old instances, start both
#   ./start.sh backend   # backend only
#   ./start.sh frontend  # frontend only
#   ./start.sh stop      # kill everything on :8000 and :3000

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
VENV_ACTIVATE="$ROOT/.venv/bin/activate"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ── Kill any process listening on a given port ────────────────────────────────
kill_port() {
  local port="$1"
  local pids
  pids=$(lsof -ti tcp:"$port" 2>/dev/null || true)
  if [[ -n "$pids" ]]; then
    echo -e "${YELLOW}⚡ Killing existing process(es) on port $port: $pids${NC}"
    echo "$pids" | xargs kill -9 2>/dev/null || true
    sleep 0.5
  fi
}

# ── Activate the PPTX-AGENTS local venv ──────────────────────────────────────
activate_venv() {
  if [ -f "$VENV_ACTIVATE" ]; then
    # shellcheck source=/dev/null
    source "$VENV_ACTIVATE"
  else
    echo -e "${RED}❌ No .venv found.${NC}"
    echo "   Run:  python3 -m venv .venv && source .venv/bin/activate && pip install -r backend/requirements.txt"
    exit 1
  fi
}

MODE="${1:-both}"

start_backend() {
  kill_port 8000
  activate_venv

  echo -e "${BLUE}▶ Starting FastAPI backend on http://localhost:8000${NC}"

  if [ ! -f "$BACKEND/.env" ]; then
    echo -e "${YELLOW}⚠  No .env found — copying from .env.example${NC}"
    cp "$BACKEND/.env.example" "$BACKEND/.env"
    echo -e "${YELLOW}   Edit $BACKEND/.env and re-run.${NC}"
    exit 1
  fi

  pip install -q -r "$BACKEND/requirements.txt"

  cd "$BACKEND"
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
  BACKEND_PID=$!
  echo -e "${GREEN}✓ Backend PID $BACKEND_PID${NC}"
  cd "$ROOT"
}

start_frontend() {
  kill_port 3000

  if ! command -v node &>/dev/null; then
    echo -e "${RED}❌ Node.js is required. Install from https://nodejs.org${NC}"
    exit 1
  fi

  echo -e "${BLUE}▶ Starting React frontend on http://localhost:3000${NC}"

  cd "$FRONTEND"
  if [ ! -d node_modules ]; then
    echo "📦 Installing npm packages..."
    npm install
  fi

  npm start &
  FRONTEND_PID=$!
  echo -e "${GREEN}✓ Frontend PID $FRONTEND_PID${NC}"
  cd "$ROOT"
}

case "$MODE" in
  stop)
    echo -e "${YELLOW}Stopping PPTX Agents…${NC}"
    kill_port 8000
    kill_port 3000
    echo -e "${GREEN}✓ Ports 8000 and 3000 cleared.${NC}"
    ;;
  backend)  start_backend; wait ;;
  frontend) start_frontend; wait ;;
  both)
    start_backend
    sleep 1
    start_frontend
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}  PPTX Agents running${NC}"
    echo -e "  Backend:   http://localhost:8000"
    echo -e "  Frontend:  http://localhost:3000"
    echo -e "  API docs:  http://localhost:8000/docs"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "  Press ${YELLOW}Ctrl-C${NC} to stop both."
    wait
    ;;
  *)
    echo "Usage: $0 [both|backend|frontend|stop]"
    exit 1
    ;;
esac

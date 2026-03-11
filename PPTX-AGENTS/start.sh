#!/usr/bin/env bash
# start.sh — Launch PPTX Agents (backend + frontend)
#
# Usage:
#   ./start.sh           # start both backend and frontend
#   ./start.sh backend   # backend only
#   ./start.sh frontend  # frontend only

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
VENV="$ROOT/../.venv/bin/python"  # use repo-root venv

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

MODE="${1:-both}"

start_backend() {
  echo -e "${BLUE}▶ Starting FastAPI backend on http://localhost:8000${NC}"

  if [ ! -f "$BACKEND/.env" ]; then
    echo -e "${YELLOW}⚠  No .env found — copying from .env.example${NC}"
    cp "$BACKEND/.env.example" "$BACKEND/.env"
    echo -e "${YELLOW}   Edit $BACKEND/.env and re-run.${NC}"
    exit 1
  fi

  cd "$BACKEND"
  pip install -q -r requirements.txt

  uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
  BACKEND_PID=$!
  echo -e "${GREEN}✓ Backend PID $BACKEND_PID${NC}"
}

start_frontend() {
  echo -e "${BLUE}▶ Starting React frontend on http://localhost:3000${NC}"

  if ! command -v node &>/dev/null; then
    echo "❌ Node.js is required. Install from https://nodejs.org"
    exit 1
  fi

  cd "$FRONTEND"
  if [ ! -d node_modules ]; then
    echo "📦 Installing npm packages..."
    npm install
  fi

  npm start &
  FRONTEND_PID=$!
  echo -e "${GREEN}✓ Frontend PID $FRONTEND_PID${NC}"
}

case "$MODE" in
  backend)  start_backend ;;
  frontend) start_frontend ;;
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
    wait
    ;;
  *)
    echo "Usage: $0 [both|backend|frontend]"
    exit 1
    ;;
esac

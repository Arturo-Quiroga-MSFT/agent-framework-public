#!/bin/bash
set -euo pipefail

# Azure AI Weather Agent - Stop Script
# Stops backend + frontend using PID files, with optional --quiet flag

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PID_FILE="$SCRIPT_DIR/.backend.pid"
FRONTEND_PID_FILE="$SCRIPT_DIR/.frontend.pid"
QUIET=false

if [ "${1:-}" = "--quiet" ]; then
	QUIET=true
fi

log() {
	$QUIET && return
	echo -e "$1"
}

stop_pid() {
	local pid_file="$1"
	local name="$2"
	if [ -f "$pid_file" ]; then
		local pid
		pid=$(cat "$pid_file")
		if ps -p "$pid" > /dev/null 2>&1; then
			kill "$pid" 2>/dev/null || true
			wait "$pid" 2>/dev/null || true
			log "✅ Stopped $name (PID $pid)"
		else
			log "ℹ️  $name PID file found but process already stopped"
		fi
		rm -f "$pid_file"
	else
		log "ℹ️  No PID file for $name"
	fi
}

log "🛑 Stopping Azure AI Weather Agent servers..."

stop_pid "$BACKEND_PID_FILE" "backend"
stop_pid "$FRONTEND_PID_FILE" "frontend"

# Fallback: kill ports if still busy
lsof -ti:8200 | xargs kill -9 2>/dev/null && log "✅ Cleared port 8200" || true
lsof -ti:3200 | xargs kill -9 2>/dev/null && log "✅ Cleared port 3200" || true

log ""
log "✅ All servers stopped"

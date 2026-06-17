#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
BACKEND_PORT="${BACKEND_PORT:-8765}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

find_free_port() {
  python - "$1" <<'PY'
import socket
import sys

start = int(sys.argv[1])
for port in range(start, start + 100):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            continue
        print(port)
        raise SystemExit(0)
raise SystemExit(f"no free localhost port found from {start} to {start + 99}")
PY
}

wait_for_backend() {
  local port="$1"
  for _ in {1..30}; do
    if python - "$port" <<'PY'
import json
import sys
import urllib.request

port = int(sys.argv[1])
try:
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=1) as response:
        payload = json.loads(response.read().decode("utf-8"))
    raise SystemExit(0 if payload.get("ok") is True else 1)
except Exception:
    raise SystemExit(1)
PY
    then
      return 0
    fi
    sleep 1
  done
  echo "FastAPI backend did not become healthy on http://127.0.0.1:${port}" >&2
  return 1
}

if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
fi

. .venv/bin/activate
python -m pip install -e ".[dev]"

if [ ! -d "frontend/node_modules" ]; then
  npm --prefix frontend install
fi

BACKEND_PORT="$(find_free_port "$BACKEND_PORT")"
FRONTEND_PORT="$(find_free_port "$FRONTEND_PORT")"

echo "Backend API: http://127.0.0.1:${BACKEND_PORT}"
echo "Frontend GUI: http://127.0.0.1:${FRONTEND_PORT}"

cleanup() {
  if [ -n "${BACKEND_PID:-}" ]; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi
  if [ -n "${FRONTEND_PID:-}" ]; then
    kill "$FRONTEND_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

python -m desaparecidos serve --host 127.0.0.1 --port "$BACKEND_PORT" &
BACKEND_PID=$!

wait_for_backend "$BACKEND_PORT"

VITE_API_BASE="http://127.0.0.1:${BACKEND_PORT}" npm --prefix frontend run dev -- --host 127.0.0.1 --port "$FRONTEND_PORT" --strictPort &
FRONTEND_PID=$!

sleep 3
open "http://127.0.0.1:${FRONTEND_PORT}"

wait "$FRONTEND_PID"

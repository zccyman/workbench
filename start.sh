#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"

START_THIRD_PARTY=false

for arg in "$@"; do
  case "$arg" in
    --third-party|--tp) START_THIRD_PARTY=true ;;
    --help|-h)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --third-party, --tp    Also start third-party OpenClaw dashboards"
      echo "  --help, -h             Show this help"
      exit 0
      ;;
  esac
done

echo "🛠️ Starting Workbench..."

# Workbench backend
cd "$ROOT/backend"
pip install -q -r requirements.txt 2>/dev/null
python -m uvicorn main:app --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!

# Workbench frontend
cd "$ROOT/frontend"
npm install --silent 2>/dev/null
npx vite --host &
FRONTEND_PID=$!

echo "✅ Workbench started!"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8001"

if [ "$START_THIRD_PARTY" = true ]; then
  echo ""
  echo "🔄 Starting third-party OpenClaw dashboards..."

  # control-center (port 4310)
  cd "$ROOT/third-party/control-center"
  npm install --silent 2>/dev/null || true
  UI_MODE=true UI_PORT=4310 npm run dev --silent &
  CONTROL_CENTER_PID=$!
  echo "   Control Center: http://localhost:4310"

  # command-center (port 3333)
  cd "$ROOT/third-party/command-center"
  npm install --silent 2>/dev/null || true
  PORT=3333 npm start &
  COMMAND_CENTER_PID=$!
  echo "   Command Center: http://localhost:3333"

  # mission-control (docker compose, ports 8000 + 3000)
  cd "$ROOT/third-party/mission-control"
  if command -v docker &>/dev/null && docker compose version &>/dev/null 2>&1; then
    docker compose up -d 2>/dev/null &
    MISSION_CONTROL_PID=$!
    echo "   Mission Control: http://localhost:3000 (backend: 8000)"
  else
    echo "   ⚠️  Mission Control skipped (docker not available)"
    MISSION_CONTROL_PID=""
  fi
fi

echo ""
echo "Press Ctrl+C to stop"

if [ "$START_THIRD_PARTY" = true ]; then
  trap "kill $BACKEND_PID $FRONTEND_PID $CONTROL_CENTER_PID $COMMAND_CENTER_PID ${MISSION_CONTROL_PID:-} 2>/dev/null" EXIT
else
  trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
fi

wait

#!/bin/bash
# Workbench 启动脚本

echo "🛠️ Starting Workbench..."

# 启动后端
ROOT="$(cd "$(dirname "$0")" && pwd)"

cd "$ROOT/backend"
pip install -q -r requirements.txt 2>/dev/null
python -m uvicorn main:app --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!

# 启动前端
cd "$ROOT/frontend"
npm install --silent 2>/dev/null
npx vite --host &
FRONTEND_PID=$!

echo "✅ Workbench started!"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8001"
echo ""
echo "Press Ctrl+C to stop"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait

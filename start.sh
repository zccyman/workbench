#!/bin/bash
# Workbench 启动脚本

echo "🛠️ Starting Workbench..."

# 启动后端
cd "$(dirname "$0")/backend"
pip install -q -r requirements.txt 2>/dev/null
python main.py &
BACKEND_PID=$!

# 启动前端
cd "$(dirname "$0")/frontend"
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

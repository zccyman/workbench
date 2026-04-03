#!/usr/bin/env bash
# Start Mission Control in local mode (SQLite + Redis)
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
BACKEND_DIR="$SCRIPT_DIR/third-party/mission-control/backend"
FRONTEND_DIR="$SCRIPT_DIR/third-party/mission-control/frontend"
BACKEND_PORT="${MISSION_CONTROL_BACKEND_PORT:-8000}"
FRONTEND_PORT="${MISSION_CONTROL_FRONTEND_PORT:-3000}"
CONDA_ENV="stock"

info() { printf '[INFO] %s\n' "$*"; }
error() { printf '[ERROR] %s\n' "$*" >&2; }

# Check if Redis is running
check_redis() {
    if ! redis-cli -p 6379 ping >/dev/null 2>&1; then
        # Try conda env redis
        if command -v conda >/dev/null 2>&1; then
            REDIS_SERVER="$(conda run -n stock which redis-server 2>/dev/null || true)"
            if [[ -n "$REDIS_SERVER" ]]; then
                info "Starting Redis on port 6379..."
                "$REDIS_SERVER" --port 6379 --daemonize yes
                sleep 1
            fi
        fi
        if ! redis-cli -p 6379 ping >/dev/null 2>&1; then
            error "Redis is not running on port 6379"
            return 1
        fi
    fi
    info "Redis OK"
}

# Check if backend .env exists
check_env() {
    if [[ ! -f "$BACKEND_DIR/.env" ]]; then
        error "Backend .env not found at $BACKEND_DIR/.env"
        error "Copy .env.example and configure, or run: cp $BACKEND_DIR/.env.example $BACKEND_DIR/.env"
        return 1
    fi
    info "Backend .env OK"
}

# Install backend dependencies if needed
install_backend_deps() {
    if ! conda run -n stock python -c "import sqlmodel" 2>/dev/null; then
        info "Installing backend Python dependencies..."
        conda run -n stock pip install -e "$BACKEND_DIR" 2>&1 | tail -5
    fi
    info "Backend dependencies OK"
}

# Install frontend dependencies if needed
install_frontend_deps() {
    if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
        info "Installing frontend dependencies..."
        (cd "$FRONTEND_DIR" && npm install)
    fi
    info "Frontend dependencies OK"
}

# Start backend
start_backend() {
    info "Starting Mission Control backend on port $BACKEND_PORT..."
    cd "$BACKEND_DIR"
    conda run -n stock uvicorn app.main:app \
        --host 0.0.0.0 \
        --port "$BACKEND_PORT" \
        --reload &
    BACKEND_PID=$!
    info "Backend PID: $BACKEND_PID"
}

# Start frontend
start_frontend() {
    info "Starting Mission Control frontend on port $FRONTEND_PORT..."
    cd "$FRONTEND_DIR"
    PORT="$FRONTEND_PORT" npm run dev -- --port "$FRONTEND_PORT" &
    FRONTEND_PID=$!
    info "Frontend PID: $FRONTEND_PID"
}

# Wait for services to be ready
wait_for_services() {
    info "Waiting for services to start..."
    for i in $(seq 1 30); do
        if curl -sf "http://localhost:$BACKEND_PORT/health" >/dev/null 2>&1; then
            info "Backend ready on port $BACKEND_PORT"
            break
        fi
        if [[ $i -eq 30 ]]; then
            error "Backend failed to start on port $BACKEND_PORT"
            return 1
        fi
        sleep 1
    done
}

# Main
main() {
    info "=== Mission Control Local Startup ==="
    check_redis
    check_env
    install_backend_deps
    install_frontend_deps
    start_backend
    start_frontend
    wait_for_services
    info ""
    info "Mission Control started successfully!"
    info "  Backend:  http://localhost:$BACKEND_PORT"
    info "  Frontend: http://localhost:$FRONTEND_PORT"
    info ""
    info "Press Ctrl+C to stop"
    wait
}

main "$@"

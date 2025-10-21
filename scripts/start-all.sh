#!/bin/bash

# Start All Services Script
# Launches both backend and frontend servers for Madrid Airbnb ML Demo
# Uses the new root-level startup scripts

set -e  # Exit on error

# Get the project root directory (parent of scripts/)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Madrid Airbnb ML Demo - Starting All Services           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Cleanup function for graceful shutdown
cleanup() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🛑 Shutting down services..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [ ! -z "$BACKEND_PID" ]; then
        echo "   Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
        wait $BACKEND_PID 2>/dev/null || true
        echo "   ✓ Backend stopped"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "   Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
        wait $FRONTEND_PID 2>/dev/null || true
        echo "   ✓ Frontend stopped"
    fi
    
    echo ""
    echo "👋 Goodbye!"
    exit 0
}

# Set up trap for graceful shutdown
trap cleanup SIGINT SIGTERM

# Check if setup has been run
if [ ! -d "$PROJECT_ROOT/backend/venv" ]; then
    echo "❌ Setup not complete!"
    echo "Run ./scripts/setup.sh first to initialize the project."
    exit 1
fi

# ===== Start Backend =====
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐍 Starting Backend..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$PROJECT_ROOT/backend"

# Activate venv and start backend
source venv/bin/activate

echo "Starting FastAPI server..."
# Use explicit path to ensure we use venv's uvicorn
"$PROJECT_ROOT/backend/venv/bin/python" -m uvicorn main:app --host 0.0.0.0 --port 8000 > "$PROJECT_ROOT/backend/backend.log" 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend to initialize..."
sleep 3

# Check if backend is running
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo "✓ Backend is ready!"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo "❌ Backend failed to start. Check backend/backend.log for details."
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    
    sleep 1
    echo -n "."
done
echo ""
echo ""

# ===== Start Frontend =====
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚛️  Starting Frontend..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$PROJECT_ROOT/frontend"

echo "Starting Vite dev server..."
echo ""

# Start frontend (in background)
npm run dev &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 2

# ===== Summary =====
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Services Running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 Frontend:     http://localhost:8080"
echo "🔌 Backend API:  http://localhost:8000"
echo "📚 API Docs:     http://localhost:8000/docs"
echo ""
echo "💡 Tip: You can also run services separately using:"
echo "   ./scripts/start-backend.sh"
echo "   ./scripts/start-frontend.sh"
echo ""
echo "Press Ctrl+C to stop all services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Wait for both processes
wait


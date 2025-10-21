#!/bin/bash

# Start Backend Script
# Launches the FastAPI backend server for Madrid Airbnb ML Demo

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Starting Backend Server                                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Get the project root directory (parent of scripts/)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

cd "$BACKEND_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run the setup script first:"
    echo "   ./scripts/setup.sh"
    exit 1
fi

# Check if database exists
if [ ! -f "data/airbnb.db" ]; then
    echo "❌ Database not found!"
    echo "Please run the setup script first:"
    echo "   ./scripts/setup.sh"
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Creating .env from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ Created .env file"
        echo ""
        echo "⚠️  Important: Edit backend/.env and add your OPENAI_API_KEY"
        echo "   (Required for RAG chat feature, other features work without it)"
        echo ""
    else
        echo "❌ .env.example not found. Creating basic .env..."
        echo "OPENAI_API_KEY=sk-your-key-here" > .env
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

echo "✓ Environment ready"
echo ""
echo "Starting FastAPI server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Backend API:  http://localhost:8000"
echo "📚 API Docs:     http://localhost:8000/docs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start server with reload for development
# Use explicit path to ensure we use venv's uvicorn
"$BACKEND_DIR/venv/bin/python" -m uvicorn main:app --reload --host 0.0.0.0 --port 8000


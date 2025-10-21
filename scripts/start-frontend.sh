#!/bin/bash

# Start Frontend Script
# Launches the React/Vite development server for Madrid Airbnb ML Demo

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Starting Frontend Server                                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Get the project root directory (parent of scripts/)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ Node modules not found!"
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
    fi
    echo ""
fi

echo "Starting Vite development server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Frontend:     http://localhost:8080"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Vite dev server
npm run dev


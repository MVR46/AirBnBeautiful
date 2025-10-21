#!/bin/bash

# Setup script for Madrid Airbnb ML Demo
# Initializes both backend and frontend for first-time use

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Madrid Airbnb ML Demo - Initial Setup                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Get the project root directory (parent of scripts/)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Project root: $PROJECT_ROOT"
echo ""

# ===== Backend Setup =====
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐍 BACKEND SETUP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$PROJECT_ROOT/backend"

# Check Python version
echo "1. Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "   ✓ Found Python $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "2. Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "   ⚠️  venv already exists, skipping..."
else
    python3 -m venv venv
    echo "   ✓ Virtual environment created"
fi
echo ""

# Activate venv
echo "3. Activating virtual environment..."
source venv/bin/activate
echo "   ✓ Virtual environment activated"
echo ""

# Install dependencies
echo "4. Installing Python dependencies..."
echo "   (This may take a few minutes...)"
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "   ✓ Dependencies installed"
echo ""

# Download spaCy model
echo "5. Downloading spaCy language model..."
python -m spacy download en_core_web_sm
echo "   ✓ spaCy model downloaded"
echo ""

# Prepare data
echo "6. Preparing database..."
if [ -f "data/airbnb.db" ]; then
    echo "   ⚠️  Database already exists, skipping..."
else
    python prepare_data.py
    echo "   ✓ Database prepared"
fi
echo ""

# Create .env file
echo "7. Setting up environment configuration..."
if [ -f ".env" ]; then
    echo "   ⚠️  .env already exists, skipping..."
else
    cp .env.example .env
    echo "   ✓ Created .env from template"
    echo "   ⚠️  IMPORTANT: Edit backend/.env and add your OPENAI_API_KEY"
    echo "      (Required for RAG chat feature, other features work without it)"
fi
echo ""

# ===== Frontend Setup =====
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚛️  FRONTEND SETUP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$PROJECT_ROOT/frontend"

# Check Node.js
echo "1. Checking Node.js version..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18 or higher."
    exit 1
fi

NODE_VERSION=$(node --version)
echo "   ✓ Found Node $NODE_VERSION"
echo ""

# Check npm
echo "2. Checking npm version..."
NPM_VERSION=$(npm --version)
echo "   ✓ Found npm $NPM_VERSION"
echo ""

# Install dependencies
echo "3. Installing Node.js dependencies..."
echo "   (This may take a few minutes...)"
npm install
echo "   ✓ Dependencies installed"
echo ""

# Create .env file
echo "4. Setting up environment configuration..."
if [ -f ".env" ]; then
    echo "   ⚠️  .env already exists, skipping..."
else
    cp .env.example .env
    echo "   ✓ Created .env from template"
fi
echo ""

# ===== Summary =====
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ SETUP COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Configure backend/.env with your OPENAI_API_KEY (optional)"
echo "   - Required only for RAG neighborhood chat feature"
echo "   - Other features work without it"
echo ""
echo "2. Start the application:"
echo "   ./scripts/start-all.sh"
echo ""
echo "   Or start services separately:"
echo "   Backend:  cd backend && ./start.sh"
echo "   Frontend: cd frontend && npm run dev"
echo ""
echo "3. Access the application:"
echo "   Frontend: http://localhost:8080"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""


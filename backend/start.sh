#!/bin/bash

# Startup script for Railway/Docker deployment
# Ensures database is prepared before starting the server

set -e  # Exit on error

echo "============================================================"
echo "🚀 Starting Airbnb ML Backend"
echo "============================================================"

# Create data directory if it doesn't exist
mkdir -p data

# Check if database exists
if [ ! -f "data/airbnb.db" ]; then
    echo ""
    echo "⚠️  Database not found at data/airbnb.db"
    echo "📦 Preparing data (this may take 2-3 minutes on first deployment)..."
    echo ""
    
    # Run data preparation with timeout (10 minutes max)
    timeout 600 python prepare_data.py || {
        echo ""
        echo "❌ Error: Data preparation failed or timed out"
        echo "Please check the logs above for details"
        exit 1
    }
    
    echo ""
    echo "✅ Data preparation completed successfully!"
    echo ""
else
    echo "✅ Database found at data/airbnb.db"
fi

# Verify database file exists before starting server
if [ ! -f "data/airbnb.db" ]; then
    echo "❌ Error: Database file still not found after preparation"
    exit 1
fi

echo "============================================================"
echo "🌐 Starting FastAPI server on port ${PORT:-8000}"
echo "============================================================"
echo ""

# Start the server with Railway-optimized settings
# --workers 1: Single worker to minimize memory usage on free tier
# --timeout-keep-alive 20: Keep alive under Railway's 30s timeout
# --limit-max-requests 100: Recycle worker to prevent memory leaks
# --timeout-graceful-shutdown 60: Allow time for cleanup
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} \
    --workers 1 \
    --timeout-keep-alive 20 \
    --limit-max-requests 100 \
    --timeout-graceful-shutdown 60


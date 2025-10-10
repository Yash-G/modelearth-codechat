#!/bin/bash
# Local Testing Script for CodeChat

echo "🚀 Starting CodeChat Local Testing Environment"
echo "=============================================="
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Start the local server
echo "🌐 Starting local development server..."
echo "📱 Open http://localhost:8000 in your browser"
echo "🛑 Press Ctrl+C to stop the server"
echo

python local_server.py
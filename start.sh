#!/bin/bash

# Application Share Startup Script

echo "🚀 Starting Application Share..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration before running again."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data logs client/build/static

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install -r requirements.txt

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd client
npm install
cd ..

# Check for X11 utilities
echo "🔧 Checking for X11 utilities..."
missing_tools=()
for tool in xwininfo xdotool import; do
    if ! command -v $tool &> /dev/null; then
        missing_tools+=($tool)
    fi
done

if [ ${#missing_tools[@]} -ne 0 ]; then
    echo "⚠️  Missing X11 utilities: ${missing_tools[*]}"
    echo "   Install with: sudo apt-get install x11-utils xdotool imagemagick"
    echo "   Or equivalent for your distribution."
fi

# Set up environment
export DISPLAY=${DISPLAY:-:0}

echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "1. Backend: python3 main.py"
echo "2. Frontend: cd client && npm start"
echo ""
echo "Or run both with: python3 main.py & cd client && npm start"
echo ""
echo "Access the application at: http://localhost:3000"

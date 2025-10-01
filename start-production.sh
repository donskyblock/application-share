#!/bin/bash

# Application Share Multi-Distribution Production Startup Script

set -e

echo "🚀 Starting Application Share in Multi-Distribution Production Mode..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_distro() {
    echo -e "${PURPLE}[DISTRO]${NC} $1"
}

# Function to detect Linux distribution
detect_distribution() {
    print_status "Detecting Linux distribution..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO_ID=$ID
        DISTRO_VERSION=$VERSION_ID
        DISTRO_NAME=$NAME
    elif [ -f /etc/arch-release ]; then
        DISTRO_ID="arch"
        DISTRO_VERSION="rolling"
        DISTRO_NAME="Arch Linux"
    elif [ -f /etc/debian_version ]; then
        DISTRO_ID="debian"
        DISTRO_VERSION=$(cat /etc/debian_version)
        DISTRO_NAME="Debian"
    else
        DISTRO_ID="unknown"
        DISTRO_VERSION="unknown"
        DISTRO_NAME="Unknown"
    fi
    
    print_distro "Detected: $DISTRO_NAME ($DISTRO_ID $DISTRO_VERSION)"
}

# Detect distribution first
detect_distribution

# Function to handle shutdown gracefully
cleanup() {
    echo "🛑 Shutting down Application Share..."
    # Kill any running processes
    pkill -f "python.*main.py" || true
    pkill -f "Xvfb" || true
    pkill -f "x11vnc" || true
    pkill -f "fluxbox" || true
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "🐳 Running in Docker container"
    DOCKER_MODE=true
else
    echo "🖥️  Running on host system"
    DOCKER_MODE=false
fi

# Set up environment variables
export PORT=${PORT:-3000}
export NODE_ENV=${NODE_ENV:-production}
export JWT_SECRET=${JWT_SECRET:-$(openssl rand -hex 32)}
export SESSION_SECRET=${SESSION_SECRET:-$(openssl rand -hex 32)}
export ADMIN_USERNAME=${ADMIN_USERNAME:-admin}
export ADMIN_PASSWORD=${ADMIN_PASSWORD:-$(openssl rand -base64 32)}
export DISPLAY=${DISPLAY:-:99}
export MAX_CONCURRENT_APPS=${MAX_CONCURRENT_APPS:-10}
export ALLOWED_APPLICATIONS=${ALLOWED_APPLICATIONS:-firefox,code,cursor,gedit,libreoffice,gnome-terminal}
export TEMP_DIR=${TEMP_DIR:-/tmp/appshare}
export USER_HOME_DIR=${USER_HOME_DIR:-/home/$(whoami)}

# Create necessary directories
mkdir -p data logs client/build/static $TEMP_DIR

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
PORT=${PORT}
NODE_ENV=${NODE_ENV}
JWT_SECRET=${JWT_SECRET}
SESSION_SECRET=${SESSION_SECRET}
ADMIN_USERNAME=${ADMIN_USERNAME}
ADMIN_PASSWORD=${ADMIN_PASSWORD}
DISPLAY=${DISPLAY}
MAX_CONCURRENT_APPS=${MAX_CONCURRENT_APPS}
ALLOWED_APPLICATIONS=${ALLOWED_APPLICATIONS}
TEMP_DIR=${TEMP_DIR}
USER_HOME_DIR=${USER_HOME_DIR}
EOF
fi

# Set up X11 display
if [ "$DISPLAY" = ":99" ]; then
    echo "🖥️  Setting up virtual display..."
    
    # Start Xvfb if not already running
    if ! pgrep -f "Xvfb.*:99" > /dev/null; then
        Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
        sleep 3
    fi
    
    # Start window manager
    if ! pgrep -f "fluxbox" > /dev/null; then
        fluxbox &
        sleep 2
    fi
    
    # Start VNC server if enabled
    if [ "${ENABLE_VNC:-false}" = "true" ]; then
        echo "📺 Starting VNC server..."
        if ! pgrep -f "x11vnc.*:99" > /dev/null; then
            x11vnc -display :99 -nopw -listen 0.0.0.0 -xkb -rfbport 5900 &
            sleep 2
        fi
    fi
    
    # Wait for display to be ready
    echo "⏳ Waiting for display to be ready..."
    timeout=30
    while [ $timeout -gt 0 ]; do
        if xdpyinfo -display :99 >/dev/null 2>&1; then
            echo "✅ Display is ready"
            break
        fi
        sleep 1
        timeout=$((timeout - 1))
    done
    
    if [ $timeout -eq 0 ]; then
        echo "❌ Display failed to start"
        exit 1
    fi
else
    echo "🖥️  Using existing display: $DISPLAY"
    
    # Check if display is accessible
    if ! xdpyinfo -display $DISPLAY >/dev/null 2>&1; then
        echo "❌ Display $DISPLAY is not accessible"
        exit 1
    fi
fi

# Print startup information
echo "🔧 Configuration:"
echo "   Port: ${PORT}"
echo "   Display: ${DISPLAY}"
echo "   Admin Username: ${ADMIN_USERNAME}"
echo "   Admin Password: ${ADMIN_PASSWORD}"
echo "   VNC Enabled: ${ENABLE_VNC:-false}"
if [ "${ENABLE_VNC:-false}" = "true" ]; then
    echo "   VNC Port: 5900"
fi
echo "   Max Concurrent Apps: ${MAX_CONCURRENT_APPS}"
echo "   Allowed Applications: ${ALLOWED_APPLICATIONS}"

# Start the Python application
echo "🐍 Starting Application Share server..."
cd "$(dirname "$0")"
exec python main.py

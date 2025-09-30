#!/bin/bash

# Application Share Docker Startup Script

set -e

echo "🚀 Starting Application Share in Docker..."

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

# Set up X11 display
export DISPLAY=${DISPLAY:-:99}

# Start Xvfb (virtual display)
echo "🖥️  Starting virtual display..."
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
XVFB_PID=$!

# Wait for Xvfb to start
sleep 2

# Start window manager
echo "🪟 Starting window manager..."
fluxbox &
FLUXBOX_PID=$!

# Start VNC server (optional, for debugging)
if [ "${ENABLE_VNC:-false}" = "true" ]; then
    echo "📺 Starting VNC server..."
    x11vnc -display :99 -nopw -listen localhost -xkb -rfbport 5900 &
    VNC_PID=$!
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

# Set up environment
export DISPLAY=:99

# Create necessary directories
mkdir -p /app/data /app/logs /app/client/build/static

# Set up environment variables with defaults
export PORT=${PORT:-3000}
export NODE_ENV=${NODE_ENV:-production}
export JWT_SECRET=${JWT_SECRET:-$(openssl rand -hex 32)}
export SESSION_SECRET=${SESSION_SECRET:-$(openssl rand -hex 32)}
export ADMIN_USERNAME=${ADMIN_USERNAME:-admin}
export ADMIN_PASSWORD=${ADMIN_PASSWORD:-$(openssl rand -base64 32)}
export DISPLAY=:99
export MAX_CONCURRENT_APPS=${MAX_CONCURRENT_APPS:-10}
export ALLOWED_APPLICATIONS=${ALLOWED_APPLICATIONS:-firefox,code,cursor,gedit,libreoffice,gnome-terminal}
export TEMP_DIR=${TEMP_DIR:-/tmp/appshare}
export USER_HOME_DIR=${USER_HOME_DIR:-/home/appuser}

# Create .env file if it doesn't exist
if [ ! -f /app/.env ]; then
    echo "📝 Creating .env file..."
    cat > /app/.env << EOF
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

# Start the Python application
echo "🐍 Starting Application Share server..."
cd /app
exec python main.py

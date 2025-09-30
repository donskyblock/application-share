#!/bin/bash

# Application Share Docker Entrypoint
# This script runs before the main application starts

set -e

echo "🔧 Application Share Docker Entrypoint"

# Function to wait for a service to be ready
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local timeout=${4:-30}
    
    echo "⏳ Waiting for $service_name to be ready..."
    local count=0
    while [ $count -lt $timeout ]; do
        if nc -z $host $port 2>/dev/null; then
            echo "✅ $service_name is ready"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done
    
    echo "❌ $service_name failed to start within ${timeout}s"
    return 1
}

# Function to check if running in Docker
is_docker() {
    [ -f /.dockerenv ]
}

# Function to setup X11 forwarding
setup_x11_forwarding() {
    if [ -n "$DISPLAY" ] && [ "$DISPLAY" != ":99" ]; then
        echo "🖥️  Setting up X11 forwarding..."
        
        # Allow X11 connections
        xhost +local:docker 2>/dev/null || true
        
        # Set up authentication
        if [ -n "$XAUTHORITY" ]; then
            export XAUTHORITY
        else
            export XAUTHORITY=/tmp/.X11-unix/X0
        fi
    fi
}

# Function to setup virtual display
setup_virtual_display() {
    if [ "$DISPLAY" = ":99" ] || [ -z "$DISPLAY" ]; then
        echo "🖥️  Setting up virtual display..."
        export DISPLAY=:99
        
        # Start Xvfb if not already running
        if ! pgrep -f "Xvfb.*:99" > /dev/null; then
            Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
            sleep 2
        fi
        
        # Start window manager
        if ! pgrep -f "fluxbox" > /dev/null; then
            fluxbox &
            sleep 1
        fi
    fi
}

# Function to setup VNC (optional)
setup_vnc() {
    if [ "${ENABLE_VNC:-false}" = "true" ]; then
        echo "📺 Setting up VNC server..."
        
        # Start VNC server
        if ! pgrep -f "x11vnc.*:99" > /dev/null; then
            x11vnc -display :99 -nopw -listen 0.0.0.0 -xkb -rfbport 5900 &
            sleep 2
        fi
        
        echo "📺 VNC server running on port 5900"
    fi
}

# Function to setup environment
setup_environment() {
    echo "🔧 Setting up environment..."
    
    # Create necessary directories
    mkdir -p /app/data /app/logs /app/client/build/static /tmp/appshare
    
    # Set permissions
    chown -R appuser:appuser /app/data /app/logs /tmp/appshare 2>/dev/null || true
    
    # Set up environment variables with defaults
    export PORT=${PORT:-3000}
    export NODE_ENV=${NODE_ENV:-production}
    export JWT_SECRET=${JWT_SECRET:-$(openssl rand -hex 32)}
    export SESSION_SECRET=${SESSION_SECRET:-$(openssl rand -hex 32)}
    export ADMIN_USERNAME=${ADMIN_USERNAME:-admin}
    export ADMIN_PASSWORD=${ADMIN_PASSWORD:-$(openssl rand -base64 32)}
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
}

# Function to print startup information
print_startup_info() {
    echo "🚀 Application Share Starting..."
    echo "=================================="
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
    echo "=================================="
}

# Main entrypoint logic
main() {
    # Check if running in Docker
    if is_docker; then
        echo "🐳 Running in Docker container"
    else
        echo "🖥️  Running on host system"
    fi
    
    # Setup environment
    setup_environment
    
    # Setup display
    if [ -n "$DISPLAY" ] && [ "$DISPLAY" != ":99" ]; then
        setup_x11_forwarding
    else
        setup_virtual_display
    fi
    
    # Setup VNC if enabled
    setup_vnc
    
    # Print startup information
    print_startup_info
    
    # Wait for display to be ready
    if ! xdpyinfo -display $DISPLAY >/dev/null 2>&1; then
        echo "❌ Display is not ready"
        exit 1
    fi
    
    echo "✅ Environment setup complete"
}

# Run main function
main

# Execute the main command
exec "$@"

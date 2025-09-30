#!/bin/bash

# Application Share Installation Script

set -e

echo "🚀 Installing Application Share..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    if command_exists apt-get; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y \
            python3 \
            python3-pip \
            python3-venv \
            nodejs \
            npm \
            x11-utils \
            xdotool \
            imagemagick \
            xvfb \
            x11vnc \
            fluxbox \
            procps \
            curl \
            openssl
    elif command_exists yum; then
        # CentOS/RHEL
        sudo yum update -y
        sudo yum install -y \
            python3 \
            python3-pip \
            nodejs \
            npm \
            xorg-x11-utils \
            xdotool \
            ImageMagick \
            xorg-x11-server-Xvfb \
            x11vnc \
            fluxbox \
            procps-ng \
            curl \
            openssl
    elif command_exists pacman; then
        # Arch Linux
        sudo pacman -Syu --noconfirm \
            python \
            python-pip \
            nodejs \
            npm \
            xorg-xwininfo \
            xdotool \
            imagemagick \
            xorg-server-xvfb \
            x11vnc \
            fluxbox \
            procps-ng \
            curl \
            openssl
    else
        print_error "Unsupported package manager. Please install dependencies manually."
        exit 1
    fi
    
    print_success "System dependencies installed"
}

# Function to create application user
create_app_user() {
    print_status "Creating application user..."
    
    if ! id "appshare" &>/dev/null; then
        sudo useradd -m -s /bin/bash appshare
        print_success "Created appshare user"
    else
        print_warning "appshare user already exists"
    fi
}

# Function to install application
install_application() {
    print_status "Installing Application Share..."
    
    # Create application directory
    sudo mkdir -p /opt/application-share
    sudo chown appshare:appshare /opt/application-share
    
    # Copy application files
    sudo cp -r . /opt/application-share/
    sudo chown -R appshare:appshare /opt/application-share
    
    # Create necessary directories
    sudo mkdir -p /opt/application-share/data
    sudo mkdir -p /opt/application-share/logs
    sudo mkdir -p /opt/application-share/client/build/static
    sudo chown -R appshare:appshare /opt/application-share/data
    sudo chown -R appshare:appshare /opt/application-share/logs
    
    # Make scripts executable
    sudo chmod +x /opt/application-share/start-production.sh
    sudo chmod +x /opt/application-share/docker/start.sh
    sudo chmod +x /opt/application-share/docker/entrypoint.sh
    
    print_success "Application installed to /opt/application-share"
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    cd /opt/application-share
    sudo -u appshare python3 -m pip install --user -r requirements.txt
    
    print_success "Python dependencies installed"
}

# Function to build frontend
build_frontend() {
    print_status "Building frontend..."
    
    cd /opt/application-share/client
    sudo -u appshare npm install
    sudo -u appshare npm run build
    
    print_success "Frontend built"
}

# Function to install systemd service
install_systemd_service() {
    print_status "Installing systemd service..."
    
    sudo cp application-share.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable application-share
    
    print_success "Systemd service installed and enabled"
}

# Function to setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    # Create .env file
    sudo -u appshare tee /opt/application-share/.env > /dev/null << EOF
PORT=3000
NODE_ENV=production
JWT_SECRET=$(openssl rand -hex 32)
SESSION_SECRET=$(openssl rand -hex 32)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=$(openssl rand -base64 32)
DISPLAY=:99
MAX_CONCURRENT_APPS=10
ALLOWED_APPLICATIONS=firefox,code,cursor,gedit,libreoffice,gnome-terminal
TEMP_DIR=/tmp/appshare
USER_HOME_DIR=/home/appshare
EOF
    
    print_success "Environment configured"
    print_warning "Admin password: $(sudo -u appshare cat /opt/application-share/.env | grep ADMIN_PASSWORD | cut -d'=' -f2)"
}

# Function to start service
start_service() {
    print_status "Starting Application Share service..."
    
    sudo systemctl start application-share
    sleep 5
    
    if sudo systemctl is-active --quiet application-share; then
        print_success "Application Share is running"
        print_status "Access the application at: http://localhost:3000"
    else
        print_error "Failed to start Application Share"
        print_status "Check logs with: sudo journalctl -u application-share -f"
    fi
}

# Main installation function
main() {
    echo "🔧 Application Share Installation Script"
    echo "========================================"
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        print_error "Please do not run this script as root"
        exit 1
    fi
    
    # Check if sudo is available
    if ! command_exists sudo; then
        print_error "sudo is required but not installed"
        exit 1
    fi
    
    # Install system dependencies
    install_system_deps
    
    # Create application user
    create_app_user
    
    # Install application
    install_application
    
    # Install Python dependencies
    install_python_deps
    
    # Build frontend
    build_frontend
    
    # Install systemd service
    install_systemd_service
    
    # Setup environment
    setup_environment
    
    # Start service
    start_service
    
    echo ""
    echo "🎉 Installation complete!"
    echo "========================="
    echo "Application Share is now running at: http://localhost:3000"
    echo "Admin username: admin"
    echo "Admin password: $(sudo -u appshare cat /opt/application-share/.env | grep ADMIN_PASSWORD | cut -d'=' -f2)"
    echo ""
    echo "Useful commands:"
    echo "  sudo systemctl status application-share    # Check status"
    echo "  sudo systemctl restart application-share   # Restart service"
    echo "  sudo systemctl stop application-share      # Stop service"
    echo "  sudo journalctl -u application-share -f    # View logs"
}

# Run main function
main "$@"

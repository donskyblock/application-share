#!/bin/bash

# Application Share Docker Deployment Script

set -e

echo "🐳 Deploying Application Share with Docker..."

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

# Function to check Docker installation
check_docker() {
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are available"
}

# Function to create environment file
create_env_file() {
    print_status "Creating environment file..."
    
    if [ ! -f .env ]; then
        cat > .env << EOF
# Server Configuration
PORT=3000
NODE_ENV=production

# Authentication (CHANGE THESE!)
JWT_SECRET=$(openssl rand -hex 32)
SESSION_SECRET=$(openssl rand -hex 32)

# Admin User (CHANGE THESE!)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=$(openssl rand -base64 32)

# X11/VNC Configuration
DISPLAY=:99
ENABLE_VNC=false

# Security
MAX_CONCURRENT_APPS=10
ALLOWED_APPLICATIONS=firefox,code,cursor,gedit,libreoffice,gnome-terminal

# File System
TEMP_DIR=/tmp/appshare
USER_HOME_DIR=/home/appuser
EOF
        print_success "Environment file created"
        print_warning "Please review and update .env file with your settings"
    else
        print_warning "Environment file already exists"
    fi
}

# Function to create data directories
create_directories() {
    print_status "Creating data directories..."
    
    mkdir -p data logs
    print_success "Data directories created"
}

# Function to build Docker image
build_image() {
    print_status "Building Docker image..."
    
    docker build -t application-share:latest .
    print_success "Docker image built"
}

# Function to start with Docker Compose
start_with_compose() {
    print_status "Starting with Docker Compose..."
    
    docker-compose up -d
    print_success "Application started with Docker Compose"
}

# Function to start with Docker run
start_with_docker() {
    print_status "Starting with Docker run..."
    
    # Stop existing container if running
    docker stop application-share 2>/dev/null || true
    docker rm application-share 2>/dev/null || true
    
    # Run container
    docker run -d \
        --name application-share \
        --restart unless-stopped \
        -p 3000:3000 \
        -p 5900:5900 \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/logs:/app/logs" \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
        --device /dev/dri:/dev/dri \
        --privileged \
        -e ADMIN_USERNAME=admin \
        -e ADMIN_PASSWORD=$(openssl rand -base64 32) \
        -e ENABLE_VNC=false \
        application-share:latest
    
    print_success "Application started with Docker run"
}

# Function to show status
show_status() {
    print_status "Checking application status..."
    
    sleep 5
    
    if docker ps | grep -q application-share; then
        print_success "Application Share is running"
        print_status "Access the application at: http://localhost:3000"
        
        # Get admin password
        ADMIN_PASSWORD=$(docker exec application-share printenv ADMIN_PASSWORD 2>/dev/null || echo "check logs")
        print_status "Admin username: admin"
        print_status "Admin password: $ADMIN_PASSWORD"
    else
        print_error "Application failed to start"
        print_status "Check logs with: docker logs application-share"
    fi
}

# Function to show help
show_help() {
    echo "Application Share Docker Deployment Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --compose    Use Docker Compose (default)"
    echo "  --docker     Use Docker run"
    echo "  --build      Build Docker image only"
    echo "  --stop       Stop running containers"
    echo "  --logs       Show application logs"
    echo "  --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Deploy with Docker Compose"
    echo "  $0 --docker          # Deploy with Docker run"
    echo "  $0 --build           # Build image only"
    echo "  $0 --stop            # Stop containers"
    echo "  $0 --logs            # Show logs"
}

# Function to stop containers
stop_containers() {
    print_status "Stopping containers..."
    
    if command_exists docker-compose; then
        docker-compose down 2>/dev/null || true
    fi
    
    docker stop application-share 2>/dev/null || true
    docker rm application-share 2>/dev/null || true
    
    print_success "Containers stopped"
}

# Function to show logs
show_logs() {
    print_status "Showing application logs..."
    
    if docker ps | grep -q application-share; then
        docker logs -f application-share
    else
        print_error "No running container found"
    fi
}

# Main function
main() {
    local mode="compose"
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --compose)
                mode="compose"
                shift
                ;;
            --docker)
                mode="docker"
                shift
                ;;
            --build)
                mode="build"
                shift
                ;;
            --stop)
                stop_containers
                exit 0
                ;;
            --logs)
                show_logs
                exit 0
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    echo "🐳 Application Share Docker Deployment"
    echo "======================================"
    
    # Check Docker installation
    check_docker
    
    # Create environment file
    create_env_file
    
    # Create data directories
    create_directories
    
    # Build Docker image
    build_image
    
    if [ "$mode" = "build" ]; then
        print_success "Docker image built successfully"
        exit 0
    fi
    
    # Start application
    if [ "$mode" = "compose" ]; then
        start_with_compose
    else
        start_with_docker
    fi
    
    # Show status
    show_status
    
    echo ""
    echo "🎉 Deployment complete!"
    echo "======================"
    echo "Application Share is running at: http://localhost:3000"
    echo ""
    echo "Useful commands:"
    echo "  $0 --stop           # Stop containers"
    echo "  $0 --logs           # View logs"
    echo "  docker ps           # List containers"
    echo "  docker logs application-share  # View logs"
}

# Run main function
main "$@"

#!/bin/bash

# Application Share Docker Deployment Script
# This script helps deploy Application Share using the published Docker image

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="ghcr.io/donskyblock/application-share"
CONTAINER_NAME="application-share"
COMPOSE_FILE="docker-compose.prod.yml"

echo -e "${BLUE}🐳 Application Share Docker Deployment${NC}"
echo "================================================"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

# Function to get the latest image
pull_latest() {
    echo "📥 Pulling latest image..."
    docker pull ${IMAGE_NAME}:latest
    print_status "Latest image pulled successfully"
}

# Function to stop existing container
stop_existing() {
    if docker ps -q -f name=${CONTAINER_NAME} | grep -q .; then
        echo "🛑 Stopping existing container..."
        docker stop ${CONTAINER_NAME}
        print_status "Container stopped"
    fi
    
    if docker ps -aq -f name=${CONTAINER_NAME} | grep -q .; then
        echo "🗑️  Removing existing container..."
        docker rm ${CONTAINER_NAME}
        print_status "Container removed"
    fi
}

# Function to run with Docker Compose
deploy_compose() {
    if [ -f "${COMPOSE_FILE}" ]; then
        echo "🚀 Deploying with Docker Compose..."
        
        # Check if .env file exists
        if [ ! -f ".env" ]; then
            print_warning "No .env file found. Creating from example..."
            if [ -f "env.production.example" ]; then
                cp env.production.example .env
                print_warning "Please edit .env file with your configuration before continuing."
                read -p "Press Enter to continue after editing .env file..."
            else
                print_error "No environment file found. Please create .env file manually."
                exit 1
            fi
        fi
        
        # Use docker-compose or docker compose
        if command -v docker-compose &> /dev/null; then
            docker-compose -f ${COMPOSE_FILE} up -d
        else
            docker compose -f ${COMPOSE_FILE} up -d
        fi
        
        print_status "Deployed with Docker Compose"
    else
        print_error "Docker Compose file not found: ${COMPOSE_FILE}"
        exit 1
    fi
}

# Function to run with Docker run
deploy_docker() {
    echo "🚀 Deploying with Docker run..."
    
    # Create necessary directories
    mkdir -p data logs recordings uploads
    
    # Run the container
    docker run -d \
        --name ${CONTAINER_NAME} \
        --restart unless-stopped \
        -p 3000:3000 \
        -p 5900:5900 \
        -p 3389:3389 \
        -e ADMIN_PASSWORD=${ADMIN_PASSWORD:-changeme123} \
        -e VNC_PASSWORD=${VNC_PASSWORD:-vncpass123} \
        -e RDP_PASSWORD=${RDP_PASSWORD:-rdppass123} \
        -e JWT_SECRET=${JWT_SECRET:-$(openssl rand -hex 32)} \
        -e SESSION_SECRET=${SESSION_SECRET:-$(openssl rand -hex 32)} \
        -v $(pwd)/data:/app/data \
        -v $(pwd)/logs:/app/logs \
        -v $(pwd)/recordings:/app/recordings \
        -v $(pwd)/uploads:/app/uploads \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
        --device /dev/dri:/dev/dri \
        --cap-add SYS_ADMIN \
        --cap-add DAC_OVERRIDE \
        --security-opt seccomp:unconfined \
        ${IMAGE_NAME}:latest
    
    print_status "Deployed with Docker run"
}

# Function to show status
show_status() {
    echo ""
    echo "📊 Deployment Status:"
    echo "===================="
    
    if docker ps -q -f name=${CONTAINER_NAME} | grep -q .; then
        print_status "Container is running"
        echo ""
        echo "🌐 Access URLs:"
        echo "  - Web Interface: http://localhost:3000"
        echo "  - VNC: localhost:5900 (password: ${VNC_PASSWORD:-vncpass123})"
        echo "  - RDP: localhost:3389 (password: ${RDP_PASSWORD:-rdppass123})"
        echo ""
        echo "📋 Container Info:"
        docker ps -f name=${CONTAINER_NAME} --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        print_error "Container is not running"
    fi
}

# Function to show logs
show_logs() {
    echo "📋 Container Logs:"
    echo "=================="
    docker logs ${CONTAINER_NAME} --tail 50 -f
}

# Function to update container
update_container() {
    echo "🔄 Updating container..."
    stop_existing
    pull_latest
    deploy_docker
    print_status "Container updated successfully"
}

# Main menu
show_menu() {
    echo ""
    echo "Choose deployment method:"
    echo "1) Deploy with Docker Compose (recommended for production)"
    echo "2) Deploy with Docker run (simple deployment)"
    echo "3) Pull latest image only"
    echo "4) Stop and remove container"
    echo "5) Show container status"
    echo "6) Show container logs"
    echo "7) Update container"
    echo "8) Exit"
    echo ""
    read -p "Enter your choice (1-8): " choice
    
    case $choice in
        1)
            pull_latest
            deploy_compose
            show_status
            ;;
        2)
            pull_latest
            stop_existing
            deploy_docker
            show_status
            ;;
        3)
            pull_latest
            ;;
        4)
            stop_existing
            print_status "Container stopped and removed"
            ;;
        5)
            show_status
            ;;
        6)
            show_logs
            ;;
        7)
            update_container
            show_status
            ;;
        8)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please try again."
            show_menu
            ;;
    esac
}

# Check if running in non-interactive mode
if [ "$1" = "--non-interactive" ]; then
    case "$2" in
        "compose")
            pull_latest
            deploy_compose
            show_status
            ;;
        "docker")
            pull_latest
            stop_existing
            deploy_docker
            show_status
            ;;
        "update")
            update_container
            show_status
            ;;
        "stop")
            stop_existing
            print_status "Container stopped and removed"
            ;;
        "status")
            show_status
            ;;
        *)
            echo "Usage: $0 --non-interactive {compose|docker|update|stop|status}"
            exit 1
            ;;
    esac
else
    show_menu
fi

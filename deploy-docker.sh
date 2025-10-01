#!/bin/bash

# Application Share Multi-Distribution Docker Deployment Script
# This script helps deploy Application Share using multi-distribution Docker images

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
REGISTRY="ghcr.io/donskyblock"
IMAGE_NAME="application-share"
CONTAINER_NAME="application-share"
COMPOSE_FILE="docker-compose.prod.yml"
MULTI_COMPOSE_FILE="docker-compose.multi-prod.yml"

# Available distributions
DISTROS=("arch" "debian" "ubuntu" "alpine")

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

print_distro() {
    echo -e "${PURPLE}🐧 $1${NC}"
}

print_feature() {
    echo -e "${CYAN}✨ $1${NC}"
}

# Function to detect Linux distribution
detect_distribution() {
    print_status "Detecting host distribution..."
    
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
    
    print_distro "Host: $DISTRO_NAME ($DISTRO_ID $DISTRO_VERSION)"
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

# Function to get the latest images
pull_latest() {
    echo "📥 Pulling latest images..."
    
    # Pull basic image
    docker pull ${REGISTRY}/${IMAGE_NAME}:latest
    print_status "Basic image pulled successfully"
    
    # Pull multi-distro images
    for distro in "${DISTROS[@]}"; do
        print_feature "Pulling ${distro} image..."
        docker pull ${REGISTRY}/${IMAGE_NAME}-${distro}:latest || print_warning "Failed to pull ${distro} image"
    done
    
    print_status "All images pulled successfully"
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

# Function to deploy multi-distro with Docker Compose
deploy_multi_compose() {
    if [ -f "${MULTI_COMPOSE_FILE}" ]; then
        print_feature "Deploying multi-distribution setup..."
        
        # Use docker-compose or docker compose
        if command -v docker-compose &> /dev/null; then
            docker-compose -f ${MULTI_COMPOSE_FILE} up -d
        else
            docker compose -f ${MULTI_COMPOSE_FILE} up -d
        fi
        
        print_status "Multi-distribution deployment complete"
    else
        print_error "Multi-distro Docker Compose file not found: ${MULTI_COMPOSE_FILE}"
        exit 1
    fi
}

# Function to deploy specific distribution
deploy_distro() {
    local distro=$1
    local port_offset=${2:-0}
    local image_tag="${REGISTRY}/${IMAGE_NAME}-${distro}:latest"
    
    local web_port=$((3000 + port_offset))
    local vnc_port=$((5900 + port_offset))
    local rdp_port=$((3389 + port_offset))
    
    print_feature "Deploying ${distro} distribution..."
    
    # Stop existing container if running
    docker stop "application-share-${distro}" 2>/dev/null || true
    docker rm "application-share-${distro}" 2>/dev/null || true
    
    # Create environment file
    cat > .env.${distro} <<EOF
PORT=${web_port}
DISPLAY=:99
ADMIN_USERNAME=admin
ADMIN_PASSWORD=${ADMIN_PASSWORD:-yourpassword123}
VNC_ENABLED=true
RDP_ENABLED=true
AUDIO_ENABLED=true
RECORDING_ENABLED=true
MARKETPLACE_ENABLED=true
CUSTOM_LAUNCHERS_ENABLED=true
DISTRO=${distro}
EOF
    
    # Run the container
    docker run -d \
        --name "application-share-${distro}" \
        --restart unless-stopped \
        -p "${web_port}:3000" \
        -p "${vnc_port}:5900" \
        -p "${rdp_port}:3389" \
        --env-file .env.${distro} \
        -v $(pwd)/data:/app/data \
        -v $(pwd)/logs:/app/logs \
        -v $(pwd)/recordings:/app/recordings \
        -v $(pwd)/marketplace:/app/marketplace \
        -v $(pwd)/launchers:/app/launchers \
        -v $(pwd)/templates:/app/templates \
        -v $(pwd)/presets:/app/presets \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
        --device /dev/dri:/dev/dri \
        --cap-add SYS_ADMIN \
        --cap-add DAC_OVERRIDE \
        --security-opt seccomp:unconfined \
        "$image_tag"
    
    if [ $? -eq 0 ]; then
        print_success "Successfully deployed ${distro} container"
        print_status "Access at: http://localhost:${web_port}"
        print_status "VNC port: ${vnc_port}"
        print_status "RDP port: ${rdp_port}"
    else
        print_error "Failed to deploy ${distro} container"
        return 1
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
    echo "1) Deploy with Docker Compose (single distribution)"
    echo "2) Deploy with Docker run (simple deployment)"
    echo "3) Deploy multi-distribution setup (all distributions)"
    echo "4) Deploy specific distribution (arch/debian/ubuntu/alpine)"
    echo "5) Pull latest images only"
    echo "6) Stop and remove containers"
    echo "7) Show container status"
    echo "8) Show container logs"
    echo "9) Update containers"
    echo "10) Exit"
    echo ""
    read -p "Enter your choice (1-10): " choice
    
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
            deploy_multi_compose
            show_status
            ;;
        4)
            echo ""
            echo "Available distributions:"
            for i in "${!DISTROS[@]}"; do
                echo "$((i+1))) ${DISTROS[$i]}"
            done
            echo ""
            read -p "Select distribution (1-${#DISTROS[@]}): " distro_choice
            
            if [[ $distro_choice -ge 1 && $distro_choice -le ${#DISTROS[@]} ]]; then
                selected_distro=${DISTROS[$((distro_choice-1))]}
                pull_latest
                deploy_distro "$selected_distro" 0
                show_status
            else
                print_error "Invalid distribution choice"
                show_menu
            fi
            ;;
        5)
            pull_latest
            ;;
        6)
            stop_existing
            # Also stop multi-distro containers
            for distro in "${DISTROS[@]}"; do
                docker stop "application-share-${distro}" 2>/dev/null || true
                docker rm "application-share-${distro}" 2>/dev/null || true
            done
            docker stop application-share-nginx 2>/dev/null || true
            docker rm application-share-nginx 2>/dev/null || true
            print_status "All containers stopped and removed"
            ;;
        7)
            show_status
            ;;
        8)
            show_logs
            ;;
        9)
            update_container
            show_status
            ;;
        10)
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

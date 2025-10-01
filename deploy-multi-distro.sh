#!/bin/bash

# Multi-Distribution Deployment Script for Application Share
# Automatically detects the host distribution and deploys accordingly

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
VERSION=${1:-latest}
DEPLOY_MODE=${2:-auto}  # auto, arch, debian, ubuntu, alpine, all

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

print_feature() {
    echo -e "${CYAN}[FEATURE]${NC} $1"
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
    elif [ -f /etc/redhat-release ]; then
        DISTRO_ID="rhel"
        DISTRO_VERSION=$(cat /etc/redhat-release | grep -oE '[0-9]+' | head -1)
        DISTRO_NAME="Red Hat Enterprise Linux"
    elif [ -f /etc/SuSE-release ]; then
        DISTRO_ID="suse"
        DISTRO_VERSION=$(cat /etc/SuSE-release | grep VERSION | cut -d' ' -f3)
        DISTRO_NAME="SUSE Linux"
    else
        DISTRO_ID="unknown"
        DISTRO_VERSION="unknown"
        DISTRO_NAME="Unknown"
    fi
    
    print_distro "Detected: $DISTRO_NAME ($DISTRO_ID $DISTRO_VERSION)"
    
    # Map to supported distributions
    case $DISTRO_ID in
        "arch"|"archlinux")
            DOCKERFILE="Dockerfile.arch"
            DISTRO_TAG="arch"
            ;;
        "debian")
            DOCKERFILE="Dockerfile.debian"
            DISTRO_TAG="debian"
            ;;
        "ubuntu")
            DOCKERFILE="Dockerfile.ubuntu"
            DISTRO_TAG="ubuntu"
            ;;
        "alpine")
            DOCKERFILE="Dockerfile.alpine"
            DISTRO_TAG="alpine"
            ;;
        "rhel"|"centos"|"fedora")
            DOCKERFILE="Dockerfile.debian"  # Use Debian as fallback
            DISTRO_TAG="debian"
            print_warning "RHEL/CentOS/Fedora detected, using Debian-based container"
            ;;
        "suse"|"opensuse")
            DOCKERFILE="Dockerfile.debian"  # Use Debian as fallback
            DISTRO_TAG="debian"
            print_warning "SUSE detected, using Debian-based container"
            ;;
        *)
            DOCKERFILE="Dockerfile.debian"  # Default to Debian
            DISTRO_TAG="debian"
            print_warning "Unknown distribution, using Debian-based container"
            ;;
    esac
    
    print_distro "Using Dockerfile: $DOCKERFILE"
    print_distro "Distribution tag: $DISTRO_TAG"
}

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root for security reasons"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        print_status "Installation commands:"
        case $DISTRO_ID in
            "arch"|"archlinux")
                echo "  sudo pacman -S docker docker-compose"
                ;;
            "debian"|"ubuntu")
                echo "  curl -fsSL https://get.docker.com -o get-docker.sh"
                echo "  sudo sh get-docker.sh"
                echo "  sudo usermod -aG docker $USER"
                ;;
            "alpine")
                echo "  apk add docker docker-compose"
                ;;
        esac
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    
    # Check if user is in docker group
    if ! groups $USER | grep -q docker; then
        print_warning "User $USER is not in docker group. Adding user to docker group..."
        sudo usermod -aG docker $USER
        print_warning "Please log out and log back in for changes to take effect."
        print_warning "Then run this script again."
        exit 1
    fi
    
    print_success "System requirements check passed"
}

# Function to install distribution-specific dependencies
install_dependencies() {
    print_status "Installing distribution-specific dependencies..."
    
    case $DISTRO_ID in
        "arch"|"archlinux")
            print_feature "Installing Arch Linux dependencies..."
            sudo pacman -Syu --noconfirm
            
            # Core packages
            sudo pacman -S --noconfirm \
                docker \
                docker-compose \
                git \
                curl \
                wget \
                jq \
                htop
            
            # Optional packages with fallbacks
            if pacman -Si neofetch &>/dev/null; then
                sudo pacman -S --noconfirm neofetch
            elif pacman -Si fastfetch &>/dev/null; then
                sudo pacman -S --noconfirm fastfetch
            else
                print_warning "neofetch not available, using basic system info"
            fi
            ;;
        "debian"|"ubuntu")
            print_feature "Installing Debian/Ubuntu dependencies..."
            sudo apt-get update
            
            # Core packages
            sudo apt-get install -y \
                docker.io \
                docker-compose \
                git \
                curl \
                wget \
                jq \
                htop \
                ca-certificates \
                gnupg \
                lsb-release
            
            # Optional packages with fallbacks
            if apt-cache show neofetch &>/dev/null; then
                sudo apt-get install -y neofetch
            elif apt-cache show fastfetch &>/dev/null; then
                sudo apt-get install -y fastfetch
            else
                print_warning "neofetch not available, using basic system info"
            fi
            ;;
        "alpine")
            print_feature "Installing Alpine Linux dependencies..."
            
            # Core packages
            sudo apk add --no-cache \
                docker \
                docker-compose \
                git \
                curl \
                wget \
                jq \
                htop
            
            # Optional packages with fallbacks
            if apk search -q neofetch &>/dev/null; then
                sudo apk add --no-cache neofetch
            elif apk search -q fastfetch &>/dev/null; then
                sudo apk add --no-cache fastfetch
            else
                print_warning "neofetch not available, using basic system info"
            fi
            ;;
        *)
            print_warning "Unknown distribution, skipping dependency installation"
            ;;
    esac
    
    print_success "Dependencies installed"
}

# Function to create application directories
create_directories() {
    print_status "Creating application directories..."
    
    mkdir -p /home/$USER/application-share/{data,logs,temp,recordings,marketplace,launchers,templates,presets}
    mkdir -p /home/$USER/application-share/client/build
    mkdir -p /home/$USER/application-share/k8s
    mkdir -p /home/$USER/application-share/nginx/ssl
    
    # Set permissions
    chmod 755 /home/$USER/application-share
    chmod 755 /home/$USER/application-share/{data,logs,temp,recordings,marketplace,launchers,templates,presets}
    
    print_success "Directories created"
}

# Function to build Docker image
build_image() {
    local distro=$1
    local dockerfile="Dockerfile.${distro}"
    local image_tag="${REGISTRY}/${IMAGE_NAME}-${distro}:${VERSION}"
    
    print_status "Building ${distro} Docker image..."
    
    if [ ! -f "$dockerfile" ]; then
        print_error "Dockerfile not found: $dockerfile"
        return 1
    fi
    
    # Ensure requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        print_warning "requirements.txt not found, creating basic one..."
        cat > requirements.txt <<EOF
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-socketio>=5.10.0
python-multipart>=0.0.6
python-dotenv>=1.0.0
passlib[bcrypt]>=1.7.4
python-jose[cryptography]>=3.3.0
websockets>=12.0
opencv-python-headless>=4.8.0
Pillow>=10.0.0
numpy>=1.24.0
pyaudio>=0.2.11
psutil>=5.9.0
aiofiles>=23.2.0
requests>=2.31.0
httpx>=0.25.0
aiortc>=1.6.0
pydantic>=2.5.0
Jinja2>=3.1.0
EOF
    fi
    
    # Build the image
    if docker build -f "$dockerfile" -t "$image_tag" .; then
        print_success "Successfully built ${distro} image: $image_tag"
        
        # Tag as latest for the distro
        docker tag "$image_tag" "${REGISTRY}/${IMAGE_NAME}-${distro}:latest"
        
        return 0
    else
        print_error "Failed to build ${distro} image"
        return 1
    fi
}

# Function to deploy single distribution
deploy_single() {
    local distro=$1
    local port_offset=${2:-0}
    local image_tag="${REGISTRY}/${IMAGE_NAME}-${distro}:latest"
    
    local web_port=$((3000 + port_offset))
    local vnc_port=$((5900 + port_offset))
    local rdp_port=$((3389 + port_offset))
    
    print_status "Deploying ${distro} distribution..."
    
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

# Function to deploy all distributions
deploy_all() {
    print_status "Deploying all distributions..."
    
    local distros=("arch" "debian" "ubuntu" "alpine")
    
    for i in "${!distros[@]}"; do
        deploy_single "${distros[$i]}" "$i"
    done
    
    # Deploy nginx load balancer
    deploy_nginx
}

# Function to deploy nginx load balancer
deploy_nginx() {
    print_status "Deploying nginx load balancer..."
    
    # Create nginx configuration
    cat > nginx/nginx.conf <<EOF
events {
    worker_connections 1024;
}

http {
    upstream application_share {
        server application-share-arch:3000 weight=1;
        server application-share-debian:3000 weight=1;
        server application-share-ubuntu:3000 weight=1;
        server application-share-alpine:3000 weight=1;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://application_share;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
EOF
    
    # Run nginx container
    docker run -d \
        --name application-share-nginx \
        --restart unless-stopped \
        -p 80:80 \
        -v $(pwd)/nginx/nginx.conf:/etc/nginx/nginx.conf:ro \
        nginx:alpine
    
    print_success "Nginx load balancer deployed"
}

# Function to create systemd service
create_systemd_service() {
    local distro=$1
    
    print_status "Creating systemd service for ${distro}..."
    
    sudo tee /etc/systemd/system/application-share-${distro}.service > /dev/null <<EOF
[Unit]
Description=Application Share Service (${distro})
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/docker start application-share-${distro}
ExecStop=/usr/bin/docker stop application-share-${distro}
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable application-share-${distro}.service
    
    print_success "Systemd service created for ${distro}"
}

# Function to show deployment status
show_status() {
    print_status "Deployment Status:"
    echo ""
    
    local distros=("arch" "debian" "ubuntu" "alpine")
    
    for distro in "${distros[@]}"; do
        if docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -q "application-share-${distro}"; then
            echo "=== ${distro^^} ==="
            docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "application-share-${distro}"
            echo ""
        fi
    done
    
    if docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -q "application-share-nginx"; then
        echo "=== NGINX LOAD BALANCER ==="
        docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "application-share-nginx"
        echo ""
    fi
}

# Function to show access information
show_access_info() {
    print_success "🎉 Deployment Complete!"
    echo ""
    echo "🌐 Access Information:"
    echo "====================="
    echo ""
    echo "Load Balancer (All Distributions):"
    echo "  - Web Interface: http://localhost"
    echo ""
    echo "Individual Distributions:"
    echo "  - Arch Linux:    http://localhost:3000"
    echo "  - Debian:        http://localhost:3001"
    echo "  - Ubuntu:        http://localhost:3002"
    echo "  - Alpine:        http://localhost:3003"
    echo ""
    echo "VNC Access:"
    echo "  - Arch Linux:    localhost:5900"
    echo "  - Debian:        localhost:5901"
    echo "  - Ubuntu:        localhost:5902"
    echo "  - Alpine:        localhost:5903"
    echo ""
    echo "RDP Access:"
    echo "  - Arch Linux:    localhost:3389"
    echo "  - Debian:        localhost:3390"
    echo "  - Ubuntu:        localhost:3391"
    echo "  - Alpine:        localhost:3392"
    echo ""
    echo "🔧 Management Commands:"
    echo "  - View logs:     docker logs application-share-<distro>"
    echo "  - Stop service:  docker stop application-share-<distro>"
    echo "  - Start service: docker start application-share-<distro>"
    echo "  - Remove:        docker rm application-share-<distro>"
    echo ""
    echo "📊 Status Check:"
    echo "  - ./build-multi-distro.sh status"
    echo "  - ./deploy-multi-distro.sh status"
}

# Function to show help
show_help() {
    echo "Multi-Distribution Deployment Script for Application Share"
    echo "========================================================="
    echo ""
    echo "Usage: $0 [VERSION] [MODE]"
    echo ""
    echo "Arguments:"
    echo "  VERSION    Docker image version (default: latest)"
    echo "  MODE       Deployment mode (default: auto)"
    echo ""
    echo "Deployment Modes:"
    echo "  auto       Automatically detect host distribution and deploy"
    echo "  arch       Deploy Arch Linux container"
    echo "  debian     Deploy Debian container"
    echo "  ubuntu     Deploy Ubuntu container"
    echo "  alpine     Deploy Alpine container"
    echo "  all        Deploy all distributions with load balancer"
    echo ""
    echo "Examples:"
    echo "  $0                    # Auto-detect and deploy"
    echo "  $0 latest arch        # Deploy Arch Linux"
    echo "  $0 v1.0.0 all         # Deploy all distributions"
    echo ""
    echo "Commands:"
    echo "  $0 status             # Show deployment status"
    echo "  $0 help               # Show this help"
}

# Main deployment logic
main() {
    case "$1" in
        "help"|"-h"|"--help")
            show_help
            exit 0
            ;;
        "status")
            show_status
            exit 0
            ;;
    esac
    
    echo -e "${BLUE}🐳 Multi-Distribution Deployment Script${NC}"
    echo "=============================================="
    echo ""
    
    # Detect distribution
    detect_distribution
    
    # Check requirements
    check_requirements
    
    # Create directories
    create_directories
    
    # Install dependencies if needed
    if [ "$INSTALL_DEPS" = "true" ]; then
        install_dependencies
    fi
    
    # Deploy based on mode
    case "$DEPLOY_MODE" in
        "auto")
            print_status "Auto-deploying based on detected distribution..."
            build_image "$DISTRO_TAG"
            deploy_single "$DISTRO_TAG" 0
            create_systemd_service "$DISTRO_TAG"
            ;;
        "arch"|"debian"|"ubuntu"|"alpine")
            print_status "Deploying $DEPLOY_MODE distribution..."
            build_image "$DEPLOY_MODE"
            deploy_single "$DEPLOY_MODE" 0
            create_systemd_service "$DEPLOY_MODE"
            ;;
        "all")
            print_status "Deploying all distributions..."
            for distro in arch debian ubuntu alpine; do
                build_image "$distro"
            done
            deploy_all
            for distro in arch debian ubuntu alpine; do
                create_systemd_service "$distro"
            done
            ;;
        *)
            print_error "Unknown deployment mode: $DEPLOY_MODE"
            show_help
            exit 1
            ;;
    esac
    
    # Show status and access info
    show_status
    show_access_info
}

# Run main function
main "$@"

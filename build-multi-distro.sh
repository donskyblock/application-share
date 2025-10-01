#!/bin/bash

# Multi-Distro Build Script for Application Share
# Supports Arch, Debian, Ubuntu, and Alpine Linux

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REGISTRY="ghcr.io/donskyblock"
IMAGE_NAME="application-share"
VERSION=${1:-latest}

# Available distributions
DISTROS=("arch" "debian" "ubuntu" "alpine")

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

# Function to build a specific distribution
build_distro() {
    local distro=$1
    local dockerfile="Dockerfile.${distro}"
    local image_tag="${REGISTRY}/${IMAGE_NAME}-${distro}:${VERSION}"
    
    print_status "Building ${distro} distribution..."
    
    if [ ! -f "$dockerfile" ]; then
        print_error "Dockerfile not found: $dockerfile"
        return 1
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

# Function to push images
push_images() {
    local distro=$1
    local image_tag="${REGISTRY}/${IMAGE_NAME}-${distro}:${VERSION}"
    
    print_status "Pushing ${distro} image..."
    
    if docker push "$image_tag"; then
        print_success "Successfully pushed ${distro} image"
        docker push "${REGISTRY}/${IMAGE_NAME}-${distro}:latest"
        return 0
    else
        print_error "Failed to push ${distro} image"
        return 1
    fi
}

# Function to run a specific distribution
run_distro() {
    local distro=$1
    local port_offset=$2
    local image_tag="${REGISTRY}/${IMAGE_NAME}-${distro}:latest"
    
    local web_port=$((3000 + port_offset))
    local vnc_port=$((5900 + port_offset))
    local rdp_port=$((3389 + port_offset))
    
    print_status "Running ${distro} distribution on ports ${web_port}, ${vnc_port}, ${rdp_port}"
    
    # Stop existing container if running
    docker stop "application-share-${distro}" 2>/dev/null || true
    docker rm "application-share-${distro}" 2>/dev/null || true
    
    # Run the container
    docker run -d \
        --name "application-share-${distro}" \
        -p "${web_port}:3000" \
        -p "${vnc_port}:5900" \
        -p "${rdp_port}:3389" \
        -e ADMIN_PASSWORD=yourpassword123 \
        "$image_tag"
    
    if [ $? -eq 0 ]; then
        print_success "Successfully started ${distro} container"
        print_status "Access at: http://localhost:${web_port}"
        print_status "VNC port: ${vnc_port}"
        print_status "RDP port: ${rdp_port}"
    else
        print_error "Failed to start ${distro} container"
        return 1
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [DISTRO] [VERSION]"
    echo ""
    echo "Commands:"
    echo "  build [distro] [version]  - Build specific distro or all distros"
    echo "  push [distro] [version]   - Push specific distro or all distros"
    echo "  run [distro] [port_offset] - Run specific distro"
    echo "  run-all [version]         - Run all distros"
    echo "  stop-all                  - Stop all running containers"
    echo "  clean                     - Clean up unused images"
    echo "  status                    - Show status of all containers"
    echo ""
    echo "Available distros: ${DISTROS[*]}"
    echo "Default version: latest"
    echo ""
    echo "Examples:"
    echo "  $0 build arch latest"
    echo "  $0 build all"
    echo "  $0 run arch 0"
    echo "  $0 run-all"
    echo "  $0 stop-all"
}

# Function to show status
show_status() {
    print_status "Container Status:"
    echo ""
    for distro in "${DISTROS[@]}"; do
        if docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -q "application-share-${distro}"; then
            docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "application-share-${distro}"
        else
            echo "application-share-${distro} - Not running"
        fi
    done
}

# Function to stop all containers
stop_all() {
    print_status "Stopping all Application Share containers..."
    for distro in "${DISTROS[@]}"; do
        if docker ps -q -f name="application-share-${distro}" | grep -q .; then
            docker stop "application-share-${distro}"
            docker rm "application-share-${distro}"
            print_success "Stopped ${distro} container"
        fi
    done
}

# Function to clean up
clean_up() {
    print_status "Cleaning up unused images..."
    docker image prune -f
    docker system prune -f
    print_success "Cleanup completed"
}

# Main script logic
case "${1:-build}" in
    "build")
        if [ "$2" = "all" ] || [ -z "$2" ]; then
            print_status "Building all distributions..."
            for distro in "${DISTROS[@]}"; do
                build_distro "$distro"
            done
        else
            if [[ " ${DISTROS[*]} " =~ " $2 " ]]; then
                build_distro "$2"
            else
                print_error "Unknown distribution: $2"
                print_error "Available distributions: ${DISTROS[*]}"
                exit 1
            fi
        fi
        ;;
    "push")
        if [ "$2" = "all" ] || [ -z "$2" ]; then
            print_status "Pushing all distributions..."
            for distro in "${DISTROS[@]}"; do
                push_images "$distro"
            done
        else
            if [[ " ${DISTROS[*]} " =~ " $2 " ]]; then
                push_images "$2"
            else
                print_error "Unknown distribution: $2"
                print_error "Available distributions: ${DISTROS[*]}"
                exit 1
            fi
        fi
        ;;
    "run")
        if [ -z "$2" ]; then
            print_error "Please specify a distribution to run"
            print_error "Available distributions: ${DISTROS[*]}"
            exit 1
        fi
        
        if [[ " ${DISTROS[*]} " =~ " $2 " ]]; then
            run_distro "$2" "${3:-0}"
        else
            print_error "Unknown distribution: $2"
            print_error "Available distributions: ${DISTROS[*]}"
            exit 1
        fi
        ;;
    "run-all")
        print_status "Running all distributions..."
        for i in "${!DISTROS[@]}"; do
            run_distro "${DISTROS[$i]}" "$i"
        done
        ;;
    "stop-all")
        stop_all
        ;;
    "clean")
        clean_up
        ;;
    "status")
        show_status
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac

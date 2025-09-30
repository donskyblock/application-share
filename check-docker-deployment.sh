#!/bin/bash

# Application Share Docker Deployment Checker
# This script verifies if the Docker image was properly pushed

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="ghcr.io/donskyblock/application-share"
REPO_URL="https://github.com/donskyblock/application-share"

echo -e "${BLUE}🔍 Checking Docker Deployment Status${NC}"
echo "=============================================="

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    exit 1
fi

# Check if GitHub CLI is installed
if command -v gh &> /dev/null; then
    HAS_GH_CLI=true
else
    HAS_GH_CLI=false
    print_warning "GitHub CLI not found. Some checks will be skipped."
fi

echo ""
print_info "1. Checking GitHub Container Registry..."

# Check if image exists in registry
if curl -s -f "https://ghcr.io/v2/donskyblock/application-share/tags/list" > /dev/null 2>&1; then
    print_success "Image exists in GitHub Container Registry"
    
    # Get available tags
    TAGS=$(curl -s "https://ghcr.io/v2/donskyblock/application-share/tags/list" | jq -r '.tags[]' 2>/dev/null || echo "Unable to parse tags")
    if [ "$TAGS" != "Unable to parse tags" ]; then
        echo "Available tags:"
        echo "$TAGS" | sed 's/^/  - /'
    fi
else
    print_error "Image not found in GitHub Container Registry"
    print_info "This might mean:"
    echo "  - The workflow hasn't run yet"
    echo "  - The workflow failed"
    echo "  - The image name is incorrect"
fi

echo ""
print_info "2. Testing Docker pull..."

# Try to pull the image
if docker pull ${IMAGE_NAME}:latest > /dev/null 2>&1; then
    print_success "Successfully pulled latest image"
    
    # Check image details
    IMAGE_ID=$(docker images --format "table {{.ID}}" ${IMAGE_NAME}:latest | tail -n +2)
    IMAGE_SIZE=$(docker images --format "table {{.Size}}" ${IMAGE_NAME}:latest | tail -n +2)
    CREATED=$(docker images --format "table {{.CreatedAt}}" ${IMAGE_NAME}:latest | tail -n +2)
    
    echo "Image details:"
    echo "  - ID: $IMAGE_ID"
    echo "  - Size: $IMAGE_SIZE"
    echo "  - Created: $CREATED"
else
    print_error "Failed to pull latest image"
    print_info "This might mean:"
    echo "  - Image doesn't exist yet"
    echo "  - Authentication issues"
    echo "  - Network connectivity problems"
fi

echo ""
print_info "3. Testing image functionality..."

# Test if the image can run
if docker run --rm ${IMAGE_NAME}:latest --help > /dev/null 2>&1; then
    print_success "Image runs successfully"
else
    print_warning "Image might have issues running"
    print_info "Trying to run with basic configuration..."
    
    # Try running with basic config
    if timeout 10s docker run --rm \
        -e ADMIN_PASSWORD=test123 \
        ${IMAGE_NAME}:latest > /dev/null 2>&1; then
        print_success "Image runs with basic configuration"
    else
        print_error "Image fails to run even with basic configuration"
    fi
fi

echo ""
print_info "4. Checking GitHub Actions workflow..."

if [ "$HAS_GH_CLI" = true ]; then
    # Check if we're in a git repository
    if [ -d ".git" ]; then
        # Get latest workflow run
        LATEST_RUN=$(gh run list --workflow="Build and Push Docker Image" --limit=1 --json status,conclusion,createdAt --jq '.[0]')
        
        if [ "$LATEST_RUN" != "null" ]; then
            STATUS=$(echo "$LATEST_RUN" | jq -r '.status')
            CONCLUSION=$(echo "$LATEST_RUN" | jq -r '.conclusion')
            CREATED=$(echo "$LATEST_RUN" | jq -r '.createdAt')
            
            echo "Latest workflow run:"
            echo "  - Status: $STATUS"
            echo "  - Conclusion: $CONCLUSION"
            echo "  - Created: $CREATED"
            
            if [ "$STATUS" = "completed" ] && [ "$CONCLUSION" = "success" ]; then
                print_success "Latest workflow completed successfully"
            elif [ "$STATUS" = "completed" ] && [ "$CONCLUSION" = "failure" ]; then
                print_error "Latest workflow failed"
                print_info "Run 'gh run view' to see logs"
            else
                print_warning "Workflow is still running or has issues"
            fi
        else
            print_warning "No workflow runs found"
        fi
    else
        print_warning "Not in a git repository, skipping workflow check"
    fi
else
    print_info "Install GitHub CLI to check workflow status:"
    echo "  - Ubuntu/Debian: sudo apt install gh"
    echo "  - macOS: brew install gh"
    echo "  - Or visit: https://cli.github.com/"
fi

echo ""
print_info "5. Quick deployment test..."

# Test if we can run the application
if docker run -d --name test-app-share \
    -p 3001:3000 \
    -e ADMIN_PASSWORD=test123 \
    ${IMAGE_NAME}:latest > /dev/null 2>&1; then
    
    print_success "Test container started successfully"
    
    # Wait a moment for the app to start
    sleep 5
    
    # Check if the web interface is responding
    if curl -s -f http://localhost:3001/health > /dev/null 2>&1; then
        print_success "Web interface is responding"
    else
        print_warning "Web interface not responding (might still be starting)"
    fi
    
    # Clean up
    docker stop test-app-share > /dev/null 2>&1
    docker rm test-app-share > /dev/null 2>&1
    print_info "Test container cleaned up"
else
    print_error "Failed to start test container"
fi

echo ""
echo "=============================================="
print_info "Summary:"
echo ""

# Final status check
if docker images | grep -q "application-share"; then
    print_success "✅ Docker image is available locally"
else
    print_error "❌ Docker image not found locally"
fi

if curl -s -f "https://ghcr.io/v2/donskyblock/application-share/tags/list" > /dev/null 2>&1; then
    print_success "✅ Image is available in GitHub Container Registry"
else
    print_error "❌ Image not found in GitHub Container Registry"
fi

echo ""
print_info "Next steps:"
echo "1. If image is available, you can deploy with:"
echo "   docker run -d --name application-share -p 3000:3000 -e ADMIN_PASSWORD=yourpass ${IMAGE_NAME}:latest"
echo ""
echo "2. If image is not available, check:"
echo "   - GitHub Actions workflow status"
echo "   - Repository permissions"
echo "   - Container registry settings"
echo ""
echo "3. For more deployment options, see:"
echo "   - docs/deployment/docker-hub.md"
echo "   - docker-compose.prod.yml"
echo "   - deploy-docker.sh"

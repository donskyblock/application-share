#!/bin/bash

# Comprehensive Deployment Script for Application Share
# Deploys all features including the new enhancements

set -e

echo "🚀 Starting comprehensive deployment of Application Share..."

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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Create necessary directories
print_status "Creating application directories..."
mkdir -p /home/$USER/application-share/{data,logs,temp,recordings,marketplace,launchers,templates,presets}
mkdir -p /home/$USER/application-share/client/build
mkdir -p /home/$USER/application-share/k8s

# Set permissions
chmod 755 /home/$USER/application-share
chmod 755 /home/$USER/application-share/{data,logs,temp,recordings,marketplace,launchers,templates,presets}

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    git \
    curl \
    wget \
    unzip \
    x11-utils \
    xdotool \
    imagemagick \
    xvfb \
    x11vnc \
    xrdp \
    fluxbox \
    procps \
    netcat-openbsd \
    pulseaudio \
    pulseaudio-utils \
    alsa-utils \
    ffmpeg \
    vlc \
    firefox \
    libreoffice \
    gimp \
    code \
    steam \
    lutris \
    audacity \
    gparted \
    filezilla \
    thunderbird \
    gedit \
    gnome-terminal \
    htop \
    neofetch \
    tree \
    jq \
    rsync \
    ssh \
    openssh-server \
    ufw \
    fail2ban \
    logrotate \
    cron \
    systemd \
    docker.io \
    docker-compose \
    kubectl \
    helm

# Install Python dependencies
print_status "Installing Python dependencies..."
cd /home/$USER/application-share
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
cd client
npm install
npm run build
cd ..

# Create systemd service
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/application-share.service > /dev/null <<EOF
[Unit]
Description=Application Share Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/application-share
Environment=PATH=/home/$USER/application-share/venv/bin
ExecStart=/home/$USER/application-share/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable application-share.service

# Create environment file
print_status "Creating environment configuration..."
if [ ! -f .env ]; then
    cp env.example .env
    print_warning "Please edit .env file with your configuration before starting the service"
fi

# Setup X11 virtual display
print_status "Setting up X11 virtual display..."
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &
sleep 2

# Setup PulseAudio
print_status "Setting up PulseAudio..."
pulseaudio --start --exit-idle-time=-1

# Create Docker image
print_status "Building Docker image..."
docker build -t application-share:latest .

# Create Docker Compose override for production
print_status "Creating production Docker Compose configuration..."
cat > docker-compose.prod.yml <<EOF
version: '3.8'

services:
  application-share:
    image: application-share:latest
    container_name: application-share-prod
    restart: unless-stopped
    ports:
      - "3000:3000"
      - "5900:5900"
      - "3389:3389"
      - "8765:8765"
      - "8766:8766"
      - "8767:8767"
      - "8768:8768"
    environment:
      - NODE_ENV=production
      - DISPLAY=:99
      - ENABLE_VNC=true
      - ENABLE_RDP=true
      - ENABLE_AUDIO=true
      - ENABLE_WEBRTC=true
      - ENABLE_RECORDING=true
      - ENABLE_MARKETPLACE=true
      - ENABLE_CUSTOM_LAUNCHERS=true
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./recordings:/app/recordings
      - ./marketplace:/app/marketplace
      - ./launchers:/app/launchers
      - ./templates:/app/templates
      - ./presets:/app/presets
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
    devices:
      - /dev/snd:/dev/snd
    privileged: true
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
EOF

# Create Kubernetes deployment script
print_status "Creating Kubernetes deployment script..."
cat > k8s/deploy.sh <<EOF
#!/bin/bash

# Deploy Application Share to Kubernetes
echo "Deploying Application Share to Kubernetes..."

# Create namespace
kubectl apply -f namespace.yaml

# Create secrets (update with your values)
kubectl create secret generic application-share-secrets \\
  --from-literal=JWT_SECRET=\$(openssl rand -base64 32) \\
  --from-literal=SESSION_SECRET=\$(openssl rand -base64 32) \\
  --from-literal=ADMIN_USERNAME=admin \\
  --from-literal=ADMIN_PASSWORD=\$(openssl rand -base64 16) \\
  --from-literal=VNC_PASSWORD=\$(openssl rand -base64 16) \\
  --from-literal=RDP_PASSWORD=\$(openssl rand -base64 16) \\
  --namespace=application-share

# Apply configurations
kubectl apply -f configmap.yaml
kubectl apply -f pvc.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# Wait for deployment
kubectl rollout status deployment/application-share -n application-share

echo "Application Share deployed to Kubernetes!"
echo "Access via: http://application-share.local"
EOF

chmod +x k8s/deploy.sh

# Create comprehensive startup script
print_status "Creating comprehensive startup script..."
cat > start-all.sh <<EOF
#!/bin/bash

# Comprehensive startup script for Application Share
echo "🚀 Starting Application Share with all features..."

# Set environment variables
export DISPLAY=:99
export PULSE_RUNTIME_PATH=/tmp/pulse

# Start X11 virtual display
echo "Starting X11 virtual display..."
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
XVFB_PID=\$!

# Wait for X11 to start
sleep 3

# Start window manager
echo "Starting window manager..."
fluxbox &
FLUXBOX_PID=\$!

# Start PulseAudio
echo "Starting PulseAudio..."
pulseaudio --start --exit-idle-time=-1 &
PULSE_PID=\$!

# Start VNC server
echo "Starting VNC server..."
x11vnc -display :99 -nopw -listen localhost -xkb -rfbport 5900 &
VNC_PID=\$!

# Start RDP server
echo "Starting RDP server..."
xrdp &
XRDP_PID=\$!

# Start main application
echo "Starting Application Share..."
cd /home/$USER/application-share
source venv/bin/activate
python main.py &
APP_PID=\$!

# Function to cleanup on exit
cleanup() {
    echo "Shutting down Application Share..."
    kill \$APP_PID \$VNC_PID \$XRDP_PID \$PULSE_PID \$FLUXBOX_PID \$XVFB_PID 2>/dev/null
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

echo "Application Share started with all features!"
echo "Web interface: http://localhost:3000"
echo "VNC: localhost:5900"
echo "RDP: localhost:3389"
echo "Press Ctrl+C to stop"

# Wait for processes
wait
EOF

chmod +x start-all.sh

# Create health check script
print_status "Creating health check script..."
cat > health-check.sh <<EOF
#!/bin/bash

# Health check script for Application Share
echo "🔍 Checking Application Share health..."

# Check if main process is running
if pgrep -f "python main.py" > /dev/null; then
    echo "✅ Main application: Running"
else
    echo "❌ Main application: Not running"
fi

# Check if X11 is running
if pgrep -f "Xvfb :99" > /dev/null; then
    echo "✅ X11 virtual display: Running"
else
    echo "❌ X11 virtual display: Not running"
fi

# Check if VNC is running
if pgrep -f "x11vnc" > /dev/null; then
    echo "✅ VNC server: Running"
else
    echo "❌ VNC server: Not running"
fi

# Check if RDP is running
if pgrep -f "xrdp" > /dev/null; then
    echo "✅ RDP server: Running"
else
    echo "❌ RDP server: Not running"
fi

# Check if PulseAudio is running
if pgrep -f "pulseaudio" > /dev/null; then
    echo "✅ PulseAudio: Running"
else
    echo "❌ PulseAudio: Not running"
fi

# Check web interface
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Web interface: Accessible"
else
    echo "❌ Web interface: Not accessible"
fi

echo "Health check complete!"
EOF

chmod +x health-check.sh

# Create backup script
print_status "Creating backup script..."
cat > backup.sh <<EOF
#!/bin/bash

# Backup script for Application Share
BACKUP_DIR="/home/$USER/application-share-backups"
TIMESTAMP=\$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="application-share-backup-\$TIMESTAMP"

echo "📦 Creating backup: \$BACKUP_NAME"

mkdir -p \$BACKUP_DIR
cd /home/$USER/application-share

# Create backup
tar -czf "\$BACKUP_DIR/\$BACKUP_NAME.tar.gz" \\
    --exclude=venv \\
    --exclude=node_modules \\
    --exclude=client/build \\
    --exclude=.git \\
    .

echo "✅ Backup created: \$BACKUP_DIR/\$BACKUP_NAME.tar.gz"
EOF

chmod +x backup.sh

# Create restore script
print_status "Creating restore script..."
cat > restore.sh <<EOF
#!/bin/bash

# Restore script for Application Share
BACKUP_DIR="/home/$USER/application-share-backups"

if [ \$# -eq 0 ]; then
    echo "Available backups:"
    ls -la \$BACKUP_DIR/*.tar.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="\$1"
if [ ! -f "\$BACKUP_FILE" ]; then
    echo "Backup file not found: \$BACKUP_FILE"
    exit 1
fi

echo "🔄 Restoring from: \$BACKUP_FILE"

# Stop service if running
sudo systemctl stop application-share.service 2>/dev/null || true

# Extract backup
cd /home/$USER
tar -xzf "\$BACKUP_FILE"

# Restart service
sudo systemctl start application-share.service

echo "✅ Restore complete!"
EOF

chmod +x restore.sh

# Create monitoring script
print_status "Creating monitoring script..."
cat > monitor.sh <<EOF
#!/bin/bash

# Monitoring script for Application Share
echo "📊 Application Share Monitoring Dashboard"
echo "========================================"

while true; do
    clear
    echo "📊 Application Share Monitoring Dashboard"
    echo "========================================"
    echo "Time: \$(date)"
    echo ""
    
    # System resources
    echo "🖥️  System Resources:"
    echo "CPU: \$(top -bn1 | grep "Cpu(s)" | awk '{print \$2}' | cut -d'%' -f1)%"
    echo "Memory: \$(free | grep Mem | awk '{printf "%.1f%%", \$3/\$2 * 100.0}')"
    echo "Disk: \$(df -h / | awk 'NR==2{printf "%s", \$5}')"
    echo ""
    
    # Application status
    echo "🚀 Application Status:"
    if pgrep -f "python main.py" > /dev/null; then
        echo "Main App: ✅ Running"
    else
        echo "Main App: ❌ Stopped"
    fi
    
    if pgrep -f "Xvfb :99" > /dev/null; then
        echo "X11 Display: ✅ Running"
    else
        echo "X11 Display: ❌ Stopped"
    fi
    
    if pgrep -f "x11vnc" > /dev/null; then
        echo "VNC Server: ✅ Running"
    else
        echo "VNC Server: ❌ Stopped"
    fi
    
    if pgrep -f "xrdp" > /dev/null; then
        echo "RDP Server: ✅ Running"
    else
        echo "RDP Server: ❌ Stopped"
    fi
    
    echo ""
    echo "Press Ctrl+C to exit monitoring"
    sleep 5
done
EOF

chmod +x monitor.sh

# Create uninstall script
print_status "Creating uninstall script..."
cat > uninstall.sh <<EOF
#!/bin/bash

# Uninstall script for Application Share
echo "🗑️  Uninstalling Application Share..."

# Stop and disable service
sudo systemctl stop application-share.service 2>/dev/null || true
sudo systemctl disable application-share.service 2>/dev/null || true

# Remove service file
sudo rm -f /etc/systemd/system/application-share.service
sudo systemctl daemon-reload

# Kill any running processes
pkill -f "python main.py" 2>/dev/null || true
pkill -f "Xvfb :99" 2>/dev/null || true
pkill -f "x11vnc" 2>/dev/null || true
pkill -f "xrdp" 2>/dev/null || true
pkill -f "pulseaudio" 2>/dev/null || true
pkill -f "fluxbox" 2>/dev/null || true

# Remove Docker containers and images
docker stop application-share 2>/dev/null || true
docker rm application-share 2>/dev/null || true
docker rmi application-share:latest 2>/dev/null || true

# Remove application directory
read -p "Remove application directory? (y/N): " -n 1 -r
echo
if [[ \$REPLY =~ ^[Yy]$ ]]; then
    rm -rf /home/$USER/application-share
    echo "✅ Application directory removed"
fi

echo "✅ Uninstall complete!"
EOF

chmod +x uninstall.sh

# Create comprehensive README
print_status "Creating comprehensive documentation..."
cat > FEATURES.md <<EOF
# Application Share - Complete Feature List

## 🚀 Core Features
- **Web-based Remote Desktop**: Access server applications through a web browser
- **Real-time Screen Sharing**: Live streaming of desktop with WebSocket support
- **Multi-protocol Support**: VNC, RDP, and custom WebSocket streaming
- **Single Admin Account**: Secure single-user authentication system
- **Docker Support**: Complete containerization with Docker Compose
- **Kubernetes Ready**: Full K8s deployment configurations

## 🎵 Audio Features
- **Audio Forwarding**: Real-time audio streaming for VNC/RDP sessions
- **PulseAudio Integration**: System-wide audio management
- **Multi-client Audio**: Support for multiple audio clients
- **Audio Recording**: Capture and stream system audio

## 📁 File Management
- **File Upload/Download**: Transfer files between client and server
- **File Browser**: Web-based file management interface
- **File Sharing**: Share files across sessions
- **Clipboard Sync**: Synchronize clipboard between client and server
- **File History**: Track file operations and changes

## 👥 Session Management
- **Multi-user Sessions**: Collaborative session support
- **Session Sharing**: Share sessions with multiple users
- **Session Templates**: Pre-configured session setups
- **Session Recording**: Record and playback sessions
- **Session Analytics**: Track session usage and performance

## 🎨 Advanced Window Management
- **Tiling Support**: Automatic window tiling (like Hyprland)
- **Window Snapping**: Snap windows to predefined zones
- **Grid Layouts**: Organize windows in grid patterns
- **Cascade Layouts**: Overlapping window arrangements
- **Custom Layouts**: Create and save custom window arrangements
- **Window Focus**: Advanced focus management

## 🏪 Application Marketplace
- **App Discovery**: Browse and search available applications
- **One-click Install**: Install applications with a single click
- **App Categories**: Organized by development, productivity, multimedia, etc.
- **Featured Apps**: Curated selection of popular applications
- **App Ratings**: User ratings and reviews
- **Dependency Management**: Automatic dependency resolution

## 🚀 Custom Launchers
- **Custom App Launchers**: Create custom application launchers
- **Template System**: Pre-built launcher templates
- **Environment Configuration**: Custom environment variables
- **Resource Limits**: Set CPU and memory limits
- **Health Checks**: Monitor application health
- **Auto-restart**: Automatic restart on crashes

## 📱 Mobile Support
- **Responsive Design**: Mobile-optimized interface
- **Touch Support**: Touch-friendly controls
- **Mobile Navigation**: Bottom navigation bar
- **Gesture Support**: Swipe and pinch gestures
- **Offline Mode**: Basic offline functionality

## 🔧 Development Features
- **API Documentation**: Complete REST API documentation
- **WebSocket Events**: Real-time communication
- **Plugin System**: Extensible architecture
- **Logging**: Comprehensive logging system
- **Health Monitoring**: System health checks
- **Performance Metrics**: Detailed performance tracking

## 🐳 Deployment Options
- **Docker**: Single container deployment
- **Docker Compose**: Multi-service orchestration
- **Kubernetes**: Production-ready K8s deployment
- **Systemd Service**: Native Linux service
- **Manual Installation**: Step-by-step manual setup

## 🔒 Security Features
- **JWT Authentication**: Secure token-based authentication
- **HTTPS Support**: Encrypted communication
- **Firewall Rules**: Automatic firewall configuration
- **Process Isolation**: Isolated application processes
- **Resource Limits**: Prevent resource abuse
- **Audit Logging**: Security event logging

## 📊 Monitoring & Analytics
- **Real-time Monitoring**: Live system monitoring
- **Performance Metrics**: CPU, memory, disk usage
- **Session Analytics**: User behavior tracking
- **Error Tracking**: Automatic error detection
- **Health Checks**: Automated health monitoring
- **Alerting**: Configurable alerts and notifications

## 🌐 Integration Features
- **WebRTC Support**: High-performance real-time communication
- **REST API**: Complete RESTful API
- **WebSocket API**: Real-time WebSocket communication
- **CLI Tools**: Command-line interface tools
- **SDK Support**: Software development kit
- **Third-party Integrations**: External service integrations

## 📈 Scalability Features
- **Horizontal Scaling**: Scale across multiple servers
- **Load Balancing**: Distribute load across instances
- **Session Persistence**: Maintain sessions across restarts
- **Resource Optimization**: Automatic resource management
- **Caching**: Intelligent caching system
- **CDN Support**: Content delivery network support

## 🛠️ Management Features
- **Backup & Restore**: Automated backup system
- **Update Management**: Easy updates and upgrades
- **Configuration Management**: Centralized configuration
- **User Management**: User account management
- **Permission System**: Role-based access control
- **Audit Trail**: Complete audit logging

## 🎯 Use Cases
- **Remote Development**: Develop on remote servers
- **Application Testing**: Test applications remotely
- **Training & Education**: Remote training sessions
- **Support & Troubleshooting**: Remote support sessions
- **Collaboration**: Team collaboration on projects
- **Gaming**: Remote gaming sessions
- **Content Creation**: Remote content creation
- **Data Analysis**: Remote data analysis

## 🔮 Future Roadmap
- **AI Integration**: AI-powered features
- **VR/AR Support**: Virtual and augmented reality
- **Blockchain Integration**: Decentralized features
- **Edge Computing**: Edge deployment support
- **5G Optimization**: 5G network optimization
- **Quantum Computing**: Quantum-ready features
EOF

# Final setup
print_status "Setting up final configurations..."

# Make all scripts executable
chmod +x *.sh
chmod +x k8s/*.sh

# Create desktop shortcut
cat > ~/Desktop/Application-Share.desktop <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Application Share
Comment=Start Application Share
Exec=/home/$USER/application-share/start-all.sh
Icon=applications-internet
Terminal=true
Categories=Network;
EOF

chmod +x ~/Desktop/Application-Share.desktop

print_success "🎉 Comprehensive deployment complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run: ./start-all.sh to start all services"
echo "3. Access web interface at: http://localhost:3000"
echo "4. Use ./health-check.sh to monitor status"
echo "5. Use ./monitor.sh for real-time monitoring"
echo ""
echo "🔧 Available Commands:"
echo "  ./start-all.sh     - Start all services"
echo "  ./health-check.sh  - Check system health"
echo "  ./monitor.sh       - Real-time monitoring"
echo "  ./backup.sh        - Create backup"
echo "  ./restore.sh       - Restore from backup"
echo "  ./uninstall.sh     - Uninstall everything"
echo ""
echo "🐳 Docker Commands:"
echo "  docker-compose -f docker-compose.prod.yml up -d"
echo "  docker-compose -f docker-compose.prod.yml down"
echo ""
echo "☸️  Kubernetes Commands:"
echo "  ./k8s/deploy.sh    - Deploy to Kubernetes"
echo "  kubectl get pods -n application-share"
echo ""
echo "📚 Documentation:"
echo "  README.md          - Main documentation"
echo "  FEATURES.md        - Complete feature list"
echo "  k8s/               - Kubernetes configurations"
echo ""
print_success "Application Share is ready to use! 🚀"

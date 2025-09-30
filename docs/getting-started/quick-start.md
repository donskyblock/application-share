# Quick Start Guide

Get Application Share up and running in minutes!

## 🚀 Prerequisites

- Linux system with X11 support
- Python 3.8+ and Node.js 16+
- Docker (optional, for containerized deployment)

## ⚡ 5-Minute Setup

### Option 1: Complete Deployment (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/application-share.git
cd application-share

# Run the complete deployment script
chmod +x deploy-all.sh
./deploy-all.sh

# Start all services
./start-all.sh
```

### Option 2: Docker Deployment

```bash
# Clone and deploy with Docker
git clone https://github.com/your-org/application-share.git
cd application-share

# Deploy with Docker Compose
docker-compose up -d

# Or use the deployment script
./docker-deploy.sh
```

### Option 3: Manual Installation

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip nodejs npm x11-utils xdotool imagemagick xvfb

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
cd client && npm install && npm run build && cd ..

# Configure environment
cp env.example .env
# Edit .env with your settings

# Start the application
python main.py
```

## 🌐 Access the Application

Once deployed, access Application Share at:

- **Web Interface**: http://localhost:3000
- **VNC**: localhost:5900
- **RDP**: localhost:3389
- **Live Stream**: http://localhost:3000/live

## 🔐 First Login

1. Open your browser to http://localhost:3000
2. The admin account is automatically created
3. Default credentials (check deployment output):
   - Username: `admin`
   - Password: (generated automatically)

## 🎯 First Steps

### 1. Launch an Application

1. Click "Launch Application" on the dashboard
2. Select an application (e.g., Firefox, VS Code)
3. The application will open in a tiled window
4. Interact with it using mouse and keyboard

### 2. Try Advanced Features

- **File Transfer**: Upload/download files
- **Audio Streaming**: Enable audio for multimedia apps
- **Session Recording**: Record your sessions
- **Window Management**: Use tiling and snapping features

### 3. Mobile Access

- Open the web interface on your mobile device
- Use touch controls for interaction
- Access all features through the mobile interface

## 🔧 Quick Configuration

Edit `.env` file for basic configuration:

```env
# Server settings
PORT=3000
NODE_ENV=production

# Admin credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password

# VNC settings
ENABLE_VNC=true
VNC_PASSWORD=your-vnc-password

# RDP settings
ENABLE_RDP=true
RDP_PASSWORD=your-rdp-password
```

## 🚨 Troubleshooting

### Common Issues

**Application won't start:**
```bash
# Check if X11 is running
echo $DISPLAY

# Start X11 virtual display
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
```

**Port already in use:**
```bash
# Check what's using the port
sudo netstat -tulpn | grep :3000

# Kill the process or change port in .env
```

**Permission denied:**
```bash
# Make scripts executable
chmod +x *.sh

# Check file permissions
ls -la *.sh
```

### Health Check

```bash
# Check system health
./health-check.sh

# View real-time monitoring
./monitor.sh

# Check logs
tail -f logs/application.log
```

## 📱 Mobile Setup

1. Ensure your server is accessible from mobile devices
2. Open the web interface in your mobile browser
3. The interface will automatically adapt to mobile
4. Use touch gestures for interaction

## 🔒 Security Notes

- Change default passwords immediately
- Use HTTPS in production
- Configure firewall rules
- Enable authentication

## 🆘 Need Help?

- **Documentation**: [Full Documentation](../README.md)
- **Issues**: [GitHub Issues](https://github.com/your-org/application-share/issues)
- **Community**: [Discord Server](https://discord.gg/application-share)

## 🎉 Next Steps

Now that you have Application Share running:

1. **Explore Features**: Try all the advanced features
2. **Configure**: Set up your preferred settings
3. **Deploy**: Move to production deployment
4. **Customize**: Create custom launchers and templates
5. **Scale**: Deploy to Kubernetes for enterprise use

---

**Congratulations!** You now have a fully functional remote desktop platform running! 🚀

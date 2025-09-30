# Docker Hub Deployment

Deploy Application Share using the pre-built Docker image from GitHub Container Registry.

## 🚀 Quick Start

### Pull and Run

```bash
# Pull the latest image
docker pull ghcr.io/donskyblock/application-share:latest

# Run with default settings
docker run -d \
  --name application-share \
  -p 3000:3000 \
  -p 5900:5900 \
  -p 3389:3389 \
  -e ADMIN_PASSWORD=yourpassword123 \
  ghcr.io/donskyblock/application-share:latest
```

### Using Docker Compose

```bash
# Clone the repository
git clone https://github.com/donskyblock/application-share.git
cd application-share

# Copy environment file
cp env.production.example .env

# Edit configuration
nano .env

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

## 📦 Available Images

| Tag | Description |
|-----|-------------|
| `latest` | Latest stable release |
| `v1.0.0` | Specific version |
| `main` | Latest from main branch |
| `develop` | Development branch |

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ADMIN_PASSWORD` | `changeme123` | Admin user password |
| `VNC_PASSWORD` | `vncpass123` | VNC server password |
| `RDP_PASSWORD` | `rdppass123` | RDP server password |
| `JWT_SECRET` | Random | JWT signing secret |
| `SESSION_SECRET` | Random | Session secret |
| `MAX_CONCURRENT_APPS` | `10` | Max running applications |
| `ENABLE_VNC` | `true` | Enable VNC server |
| `ENABLE_RDP` | `true` | Enable RDP server |
| `ENABLE_AUDIO` | `true` | Enable audio forwarding |

### Ports

| Port | Service | Description |
|------|---------|-------------|
| 3000 | Web Interface | Main web application |
| 5900 | VNC | VNC server for remote desktop |
| 3389 | RDP | RDP server for Windows clients |

## 🛠️ Deployment Methods

### Method 1: Docker Run (Simple)

```bash
# Basic deployment
docker run -d \
  --name application-share \
  --restart unless-stopped \
  -p 3000:3000 \
  -p 5900:5900 \
  -p 3389:3389 \
  -e ADMIN_PASSWORD=yourpassword123 \
  -e VNC_PASSWORD=vncpass123 \
  -e RDP_PASSWORD=rdppass123 \
  -v app_data:/app/data \
  -v app_logs:/app/logs \
  ghcr.io/donskyblock/application-share:latest
```

### Method 2: Docker Compose (Recommended)

```yaml
version: '3.8'
services:
  application-share:
    image: ghcr.io/donskyblock/application-share:latest
    container_name: application-share
    restart: unless-stopped
    ports:
      - "3000:3000"
      - "5900:5900"
      - "3389:3389"
    environment:
      - ADMIN_PASSWORD=yourpassword123
      - VNC_PASSWORD=vncpass123
      - RDP_PASSWORD=rdppass123
    volumes:
      - app_data:/app/data
      - app_logs:/app/logs
```

### Method 3: Deployment Script

```bash
# Interactive deployment
./deploy-docker.sh

# Non-interactive deployment
./deploy-docker.sh --non-interactive compose
./deploy-docker.sh --non-interactive docker
```

## 🔒 Security Considerations

### Change Default Passwords

```bash
# Generate secure passwords
openssl rand -hex 16  # For JWT_SECRET
openssl rand -hex 16  # For SESSION_SECRET

# Set environment variables
export ADMIN_PASSWORD="your-secure-password"
export VNC_PASSWORD="your-vnc-password"
export RDP_PASSWORD="your-rdp-password"
```

### Network Security

```bash
# Run with custom network
docker network create app_network

docker run -d \
  --name application-share \
  --network app_network \
  -p 127.0.0.1:3000:3000 \
  ghcr.io/donskyblock/application-share:latest
```

### SSL/TLS Setup

```bash
# With SSL certificates
docker run -d \
  --name application-share \
  -p 443:443 \
  -v /path/to/cert.pem:/app/cert.pem:ro \
  -v /path/to/key.pem:/app/key.pem:ro \
  -e SSL_CERT_PATH=/app/cert.pem \
  -e SSL_KEY_PATH=/app/key.pem \
  ghcr.io/donskyblock/application-share:latest
```

## 📊 Monitoring

### Health Check

```bash
# Check container health
docker ps -f name=application-share

# Check logs
docker logs application-share

# Check resource usage
docker stats application-share
```

### Logs

```bash
# Follow logs
docker logs -f application-share

# Save logs to file
docker logs application-share > app.log 2>&1
```

## 🔄 Updates

### Update to Latest Version

```bash
# Pull latest image
docker pull ghcr.io/donskyblock/application-share:latest

# Stop and remove old container
docker stop application-share
docker rm application-share

# Run new container
docker run -d \
  --name application-share \
  --restart unless-stopped \
  -p 3000:3000 \
  -p 5900:5900 \
  -p 3389:3389 \
  -e ADMIN_PASSWORD=yourpassword123 \
  ghcr.io/donskyblock/application-share:latest
```

### Using Deployment Script

```bash
# Update container
./deploy-docker.sh --non-interactive update
```

## 🐛 Troubleshooting

### Common Issues

**Container won't start:**
```bash
# Check logs
docker logs application-share

# Check if ports are available
netstat -tulpn | grep :3000
```

**VNC/RDP not working:**
```bash
# Check if X11 is running
docker exec application-share ps aux | grep X

# Check VNC server
docker exec application-share netstat -tulpn | grep :5900
```

**Permission issues:**
```bash
# Fix volume permissions
sudo chown -R 1000:1000 ./data ./logs
```

### Debug Mode

```bash
# Run in debug mode
docker run -it \
  --name application-share-debug \
  -p 3000:3000 \
  -e DEBUG=true \
  -e LOG_LEVEL=DEBUG \
  ghcr.io/donskyblock/application-share:latest
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Application Share GitHub](https://github.com/donskyblock/application-share)

---

**Need help?** Check our [troubleshooting guide](../user-guide/troubleshooting.md) or open an [issue](https://github.com/donskyblock/application-share/issues)!

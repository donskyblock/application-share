# Docker Deployment

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/application-share.git
cd application-share

# Deploy with Docker Compose
docker-compose up -d

# Or use the deployment script
./docker-deploy.sh
```

## Configuration

Edit `docker-compose.yml` to customize your deployment:

```yaml
version: '3.8'
services:
  application-share:
    image: application-share:latest
    ports:
      - "3000:3000"
      - "5900:5900"
      - "3389:3389"
    environment:
      - ADMIN_USERNAME=admin
      - ADMIN_PASSWORD=your-password
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
```

## Production Deployment

For production, use the production configuration:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Monitoring

```bash
# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Restart services
docker-compose restart
```

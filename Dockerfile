# Multi-stage build for Application Share
FROM node:18-alpine AS frontend-builder

# Set working directory
WORKDIR /app/client

# Copy package files
COPY client/package.json ./

# Install dependencies with legacy peer deps to avoid conflicts
RUN npm install --legacy-peer-deps --verbose || (echo "npm install failed, trying with --force" && npm install --force --verbose)

# Copy source code
COPY client/ ./

# Debug: Show what files we have
RUN ls -la

# Build the frontend
RUN npm run build || (echo "Build failed, showing error details" && cat package.json && exit 1)

# Python backend stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    x11-utils \
    xdotool \
    imagemagick \
    xvfb \
    x11vnc \
    xrdp \
    fluxbox \
    procps \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -s /bin/bash appuser

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/client/build ./client/build

# Create necessary directories
RUN mkdir -p data logs client/build/static && \
    chown -R appuser:appuser /app

# Create startup script
COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

# Switch to app user
USER appuser

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Start the application
CMD ["/start.sh"]

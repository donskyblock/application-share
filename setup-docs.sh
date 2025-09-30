#!/bin/bash

# Setup Documentation for Application Share
echo "🚀 Setting up comprehensive documentation for Application Share..."

# Install documentation dependencies
echo "📦 Installing documentation dependencies..."
pip install mkdocs mkdocs-material mkdocs-swagger-ui-tag mkdocs-mermaid2-plugin

# Generate documentation
echo "📚 Generating documentation..."
python scripts/generate-docs.py

# Build documentation
echo "🔨 Building documentation..."
mkdocs build --clean --site-dir ./site

echo "✅ Documentation setup complete!"
echo ""
echo "📖 Available documentation:"
echo "  - Main docs: docs/"
echo "  - Built site: site/"
echo "  - API docs: docs/api/"
echo "  - Code docs: docs/api/code/"
echo ""
echo "🌐 GitHub Pages deployment:"
echo "  - Local preview: mkdocs serve"
echo "  - Deploy to GitHub: mkdocs gh-deploy"
echo "  - Live docs: https://donskyblock.github.io/application-share"

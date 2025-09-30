#!/bin/bash

# Setup Documentation for Application Share
echo "🚀 Setting up comprehensive documentation for Application Share..."

# Check if virtual environment exists, create if not
if [ ! -d "docs-env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv docs-env
fi

# Install documentation dependencies
echo "📦 Installing documentation dependencies..."
./docs-env/bin/pip install mkdocs mkdocs-material mkdocs-swagger-ui-tag mkdocs-mermaid2-plugin

# Generate documentation
echo "📚 Generating documentation..."
./docs-env/bin/python scripts/generate-docs.py

# Build documentation
echo "🔨 Building documentation..."
./docs-env/bin/mkdocs build --clean --site-dir ./site

echo "✅ Documentation setup complete!"
echo ""
echo "📖 Available documentation:"
echo "  - Main docs: docs/"
echo "  - Built site: site/"
echo "  - API docs: docs/api/"
echo "  - Code docs: docs/api/code/"
echo ""
echo "🌐 GitHub Pages deployment:"
echo "  - Local preview: ./docs-env/bin/mkdocs serve"
echo "  - Deploy to GitHub: ./docs-env/bin/mkdocs gh-deploy"
echo "  - Live docs: https://donskyblock.github.io/application-share"

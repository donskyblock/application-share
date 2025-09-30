#!/usr/bin/env python3
"""
Documentation Generator for Application Share
Automatically generates and updates documentation from code
"""

import os
import json
import ast
import inspect
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def extract_docstrings(file_path: str) -> Dict[str, str]:
    """Extract docstrings from Python files"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        docstrings = {}
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                if node.docstring:
                    docstrings[node.name] = node.docstring
        
        return docstrings
    except Exception as e:
        print(f"Error extracting docstrings from {file_path}: {e}")
        return {}

def generate_api_docs():
    """Generate API documentation from FastAPI app"""
    try:
        # Import the FastAPI app
        import sys
        sys.path.append('.')
        from main import app
        
        # Generate OpenAPI schema
        openapi_schema = app.openapi()
        
        # Save OpenAPI spec
        os.makedirs('docs/api', exist_ok=True)
        with open('docs/api/openapi.json', 'w') as f:
            json.dump(openapi_schema, f, indent=2)
        
        print("✅ Generated OpenAPI specification")
        
        # Generate endpoint documentation
        endpoints = []
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                for method in route.methods:
                    if method != 'HEAD':
                        endpoints.append({
                            'method': method,
                            'path': route.path,
                            'name': getattr(route, 'name', ''),
                            'summary': getattr(route, 'summary', ''),
                            'description': getattr(route, 'description', '')
                        })
        
        # Generate API reference markdown
        api_content = f"""# API Reference

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

## Endpoints

"""
        
        for endpoint in sorted(endpoints, key=lambda x: x['path']):
            api_content += f"""### {endpoint['method'].upper()} {endpoint['path']}

**Name**: {endpoint['name']}
**Summary**: {endpoint['summary']}
**Description**: {endpoint['description']}

---

"""
        
        with open('docs/api/endpoints.md', 'w') as f:
            f.write(api_content)
        
        print("✅ Generated API endpoints documentation")
        
    except Exception as e:
        print(f"❌ Error generating API docs: {e}")

def generate_code_docs():
    """Generate code documentation from Python modules"""
    try:
        os.makedirs('docs/api/code', exist_ok=True)
        
        # Process server modules
        for root, dirs, files in os.walk('server'):
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    file_path = os.path.join(root, file)
                    docstrings = extract_docstrings(file_path)
                    
                    if docstrings:
                        # Generate markdown documentation
                        module_name = file.replace('.py', '')
                        doc_content = f"""# {module_name}

Generated from `{file_path}` on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

## Functions and Classes

"""
                        
                        for name, docstring in docstrings.items():
                            doc_content += f"""### {name}

```python
{docstring}
```

---
"""
                        
                        output_path = f'docs/api/code/{module_name}.md'
                        with open(output_path, 'w') as f:
                            f.write(doc_content)
        
        print("✅ Generated code documentation")
        
    except Exception as e:
        print(f"❌ Error generating code docs: {e}")

def generate_feature_matrix():
    """Generate feature matrix documentation"""
    try:
        features = {
            "Core Features": [
                "Web-based Remote Desktop",
                "Real-time Screen Sharing", 
                "Multi-protocol Support",
                "Single Admin Account",
                "Docker Support",
                "Kubernetes Ready"
            ],
            "Audio & Media": [
                "Audio Forwarding",
                "PulseAudio Integration",
                "Multi-client Audio",
                "Audio Recording"
            ],
            "File Management": [
                "File Upload/Download",
                "File Browser",
                "File Sharing",
                "Clipboard Sync",
                "File History"
            ],
            "Session Management": [
                "Multi-user Sessions",
                "Session Sharing",
                "Session Templates",
                "Session Recording",
                "Session Analytics"
            ],
            "Window Management": [
                "Tiling Support",
                "Window Snapping",
                "Grid Layouts",
                "Cascade Layouts",
                "Custom Layouts",
                "Window Focus"
            ],
            "Application Marketplace": [
                "App Discovery",
                "One-click Install",
                "App Categories",
                "Featured Apps",
                "App Ratings",
                "Dependency Management"
            ],
            "Custom Launchers": [
                "Custom App Launchers",
                "Template System",
                "Environment Configuration",
                "Resource Limits",
                "Health Checks",
                "Auto-restart"
            ],
            "Mobile & Responsive": [
                "Responsive Design",
                "Touch Support",
                "Mobile Navigation",
                "Gesture Support",
                "Offline Mode"
            ],
            "Security & Monitoring": [
                "JWT Authentication",
                "HTTPS Support",
                "Firewall Rules",
                "Process Isolation",
                "Resource Limits",
                "Audit Logging",
                "Real-time Monitoring",
                "Performance Metrics",
                "Session Analytics",
                "Error Tracking",
                "Health Checks",
                "Alerting"
            ]
        }
        
        # Generate feature matrix markdown
        matrix_content = f"""# Feature Matrix

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

## Complete Feature Overview

"""
        
        for category, feature_list in features.items():
            matrix_content += f"""### {category}

"""
            for feature in feature_list:
                matrix_content += f"- [x] **{feature}** ✅\n"
            matrix_content += "\n"
        
        with open('docs/features/matrix.md', 'w') as f:
            f.write(matrix_content)
        
        print("✅ Generated feature matrix")
        
    except Exception as e:
        print(f"❌ Error generating feature matrix: {e}")

def generate_deployment_guides():
    """Generate deployment guides"""
    try:
        os.makedirs('docs/deployment', exist_ok=True)
        
        # Docker deployment guide
        docker_content = """# Docker Deployment

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
"""
        
        with open('docs/deployment/docker.md', 'w') as f:
            f.write(docker_content)
        
        print("✅ Generated deployment guides")
        
    except Exception as e:
        print(f"❌ Error generating deployment guides: {e}")

def update_readme_stats():
    """Update README with latest statistics"""
    try:
        # Count files and lines
        python_files = list(Path('.').rglob('*.py'))
        js_files = list(Path('.').rglob('*.js'))
        md_files = list(Path('.').rglob('*.md'))
        
        total_lines = 0
        for file in python_files + js_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    total_lines += len(f.readlines())
            except:
                pass
        
        stats = {
            'python_files': len(python_files),
            'js_files': len(js_files),
            'md_files': len(md_files),
            'total_lines': total_lines,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        }
        
        # Update stats in README
        readme_path = 'README.md'
        if os.path.exists(readme_path):
            with open(readme_path, 'r') as f:
                content = f.read()
            
            # Add stats section if not exists
            if '## 📊 Project Statistics' not in content:
                stats_section = f"""

## 📊 Project Statistics

- **Python Files**: {stats['python_files']}
- **JavaScript Files**: {stats['js_files']}
- **Documentation Files**: {stats['md_files']}
- **Total Lines of Code**: {stats['total_lines']:,}
- **Last Updated**: {stats['last_updated']}

"""
                content += stats_section
                
                with open(readme_path, 'w') as f:
                    f.write(content)
        
        print("✅ Updated README statistics")
        
    except Exception as e:
        print(f"❌ Error updating README stats: {e}")

def main():
    """Main documentation generation function"""
    print("🚀 Generating Application Share documentation...")
    
    # Create necessary directories
    os.makedirs('docs/api', exist_ok=True)
    os.makedirs('docs/api/code', exist_ok=True)
    os.makedirs('docs/features', exist_ok=True)
    os.makedirs('docs/deployment', exist_ok=True)
    
    # Generate documentation
    generate_api_docs()
    generate_code_docs()
    generate_feature_matrix()
    generate_deployment_guides()
    update_readme_stats()
    
    print("✅ Documentation generation complete!")
    print("\n📚 Generated documentation:")
    print("  - API Reference: docs/api/")
    print("  - Code Documentation: docs/api/code/")
    print("  - Feature Matrix: docs/features/matrix.md")
    print("  - Deployment Guides: docs/deployment/")
    print("  - Updated README with statistics")
    print("\n🌐 GitHub Pages deployment:")
    print("  - Documentation will be available at: https://donskyblock.github.io/application-share")
    print("  - Deploy with: mkdocs gh-deploy")

if __name__ == "__main__":
    main()

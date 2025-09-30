# GitHub Pages Setup

This guide explains how to set up GitHub Pages for the Application Share documentation.

## 🚀 Quick Setup

### 1. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under **Source**, select **GitHub Actions**
4. Save the settings

### 2. Deploy Documentation

The documentation will automatically deploy when you push to the `main` branch thanks to the GitHub Actions workflow.

**Manual deployment:**
```bash
# Install MkDocs
pip install mkdocs mkdocs-material

# Deploy to GitHub Pages
mkdocs gh-deploy
```

### 3. Access Your Documentation

Once deployed, your documentation will be available at:
```
https://donskyblock.github.io/application-share
```

## 📁 Repository Structure

```
application-share/
├── docs/                    # Documentation source
│   ├── index.md            # Homepage
│   ├── getting-started/    # Getting started guides
│   ├── api/               # API documentation
│   └── ...
├── .github/
│   └── workflows/
│       └── docs.yml       # Auto-deployment workflow
├── mkdocs.yml             # MkDocs configuration
└── scripts/
    └── generate-docs.py   # Documentation generator
```

## 🔄 Automatic Updates

The documentation automatically updates when:

- You push changes to the `main` branch
- You merge a pull request
- The GitHub Actions workflow runs

## 🛠️ Local Development

**Preview locally:**
```bash
# Install dependencies
pip install mkdocs mkdocs-material

# Serve locally
mkdocs serve

# Open http://localhost:8000
```

**Build documentation:**
```bash
# Generate docs from code
python scripts/generate-docs.py

# Build static site
mkdocs build
```

## 📝 Customization

### Update Repository URLs

Edit `mkdocs.yml`:
```yaml
site_url: https://donskyblock.github.io/application-share
repo_url: https://github.com/donskyblock/application-share
repo_name: donskyblock/application-share
```

### Add Custom Content

- **Homepage**: Edit `docs/index.md`
- **API Docs**: Auto-generated from code
- **Guides**: Add to `docs/getting-started/`
- **Features**: Add to `docs/features/`

## 🎨 Styling

Custom styles are in `docs/stylesheets/extra.css`:
- Brand colors
- Feature cards
- API endpoint styling
- Status badges

## 🔧 Troubleshooting

### Documentation Not Updating

1. Check GitHub Actions workflow status
2. Verify GitHub Pages is enabled
3. Check for build errors in the Actions tab

### Local Build Issues

```bash
# Clean build
rm -rf site/
mkdocs build --clean

# Check for errors
mkdocs build --verbose
```

### Missing Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt
pip install mkdocs mkdocs-material mkdocs-swagger-ui-tag
```

## 📊 Analytics (Optional)

To add analytics, edit `mkdocs.yml`:
```yaml
extra:
  analytics:
    provider: google
    property: G-XXXXXXXXXX
```

## 🔒 Security

- Documentation is public by default
- No sensitive information should be in docs
- Use environment variables for secrets
- Review all content before pushing

## 🎯 Best Practices

1. **Keep docs up-to-date** with code changes
2. **Use clear, concise language**
3. **Include code examples**
4. **Test locally** before pushing
5. **Use descriptive commit messages**

---

**Need help?** Check the [GitHub Pages documentation](https://docs.github.com/en/pages) or open an issue!

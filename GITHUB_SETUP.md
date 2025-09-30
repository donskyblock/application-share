# GitHub Repository Setup for Docker Workflow

## 🔧 Required Repository Settings

### 1. Enable GitHub Actions
1. Go to your repository: `https://github.com/donskyblock/application-share`
2. Click **Settings** → **Actions** → **General**
3. Under **Workflow permissions**, select:
   - ✅ **Read and write permissions**
   - ✅ **Allow GitHub Actions to create and approve pull requests**
4. Click **Save**

### 2. Enable GitHub Container Registry
1. Go to **Settings** → **Actions** → **General**
2. Scroll down to **Workflow permissions**
3. Make sure **Read and write permissions** is selected
4. Click **Save**

### 3. Check Package Visibility
1. Go to your repository
2. Click **Packages** tab (next to Code, Issues, etc.)
3. If you see the `application-share` package, click on it
4. Go to **Package settings**
5. Change visibility to **Public** (if not already)

### 4. Verify Workflow Permissions
The workflow now has these permissions:
```yaml
permissions:
  contents: read
  packages: write
  id-token: write
```

## 🚀 Test the Workflow

### Manual Trigger
1. Go to **Actions** tab
2. Click **Build and Push Docker Image**
3. Click **Run workflow**
4. Select branch: `master`
5. Click **Run workflow**

### Check Build Status
- **Green checkmark** ✅ = Success
- **Red X** ❌ = Failed (check logs)
- **Yellow circle** ⏳ = Running

## 🔍 Troubleshooting

### If Build Still Fails
1. **Check workflow logs** - Click on the failed run to see detailed error messages
2. **Verify permissions** - Make sure the repository has the correct settings
3. **Check package creation** - The workflow now tries to create the package automatically

### Common Issues
- **Permission denied**: Check repository settings
- **Package not found**: The workflow will create it automatically
- **Authentication failed**: Verify GitHub token permissions

## 📦 Expected Result

Once successful, you should see:
- **Docker image**: `ghcr.io/donskyblock/application-share:latest`
- **Available tags**: `latest`, `master`, version tags
- **Package visibility**: Public

## 🐳 Test the Image

```bash
# Pull the image
docker pull ghcr.io/donskyblock/application-share:latest

# Run the container
docker run -d \
  --name application-share \
  -p 3000:3000 \
  -e ADMIN_PASSWORD=yourpassword123 \
  ghcr.io/donskyblock/application-share:latest

# Check if running
docker ps | grep application-share
```

---

**Need help?** Check the workflow logs in the Actions tab for detailed error messages!

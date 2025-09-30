"""
Application Marketplace for Application Share
Provides application discovery, installation, and management
"""

import asyncio
import os
import json
import time
import subprocess
from typing import Dict, List, Optional, Any
from pathlib import Path
import requests

class AppMarketplace:
    def __init__(self):
        self.marketplace_dir = os.getenv("MARKETPLACE_DIR", "/app/marketplace")
        self.apps_dir = os.getenv("APPS_DIR", "/app/apps")
        self.installed_apps: Dict[str, Dict[str, Any]] = {}
        self.available_apps: Dict[str, Dict[str, Any]] = {}
        
        # Create directories
        os.makedirs(self.marketplace_dir, exist_ok=True)
        os.makedirs(self.apps_dir, exist_ok=True)
        
        # Load installed apps
        self._load_installed_apps()
        
        # Initialize marketplace
        self._initialize_marketplace()
    
    def _load_installed_apps(self):
        """Load installed applications"""
        try:
            installed_file = os.path.join(self.marketplace_dir, "installed.json")
            if os.path.exists(installed_file):
                with open(installed_file, 'r') as f:
                    self.installed_apps = json.load(f)
        except Exception as e:
            print(f"Error loading installed apps: {e}")
            self.installed_apps = {}
    
    def _save_installed_apps(self):
        """Save installed applications"""
        try:
            installed_file = os.path.join(self.marketplace_dir, "installed.json")
            with open(installed_file, 'w') as f:
                json.dump(self.installed_apps, f, indent=2)
        except Exception as e:
            print(f"Error saving installed apps: {e}")
    
    def _initialize_marketplace(self):
        """Initialize marketplace with default applications"""
        default_apps = {
            "firefox": {
                "id": "firefox",
                "name": "Mozilla Firefox",
                "description": "Web browser for browsing the internet",
                "version": "latest",
                "category": "internet",
                "icon": "🌐",
                "author": "Mozilla",
                "license": "MPL 2.0",
                "size": "100MB",
                "dependencies": [],
                "install_command": "apt-get install -y firefox",
                "uninstall_command": "apt-get remove -y firefox",
                "executable": "firefox",
                "args": [],
                "env": {"DISPLAY": ":99"},
                "tags": ["browser", "web", "internet"],
                "rating": 4.5,
                "downloads": 1000000,
                "featured": True
            },
            "code": {
                "id": "code",
                "name": "Visual Studio Code",
                "description": "Code editor for development",
                "version": "latest",
                "category": "development",
                "icon": "💻",
                "author": "Microsoft",
                "license": "MIT",
                "size": "200MB",
                "dependencies": ["curl", "wget"],
                "install_command": "curl -fsSL https://code-server.dev/install.sh | sh",
                "uninstall_command": "apt-get remove -y code-server",
                "executable": "code-server",
                "args": ["--bind-addr", "0.0.0.0:8080"],
                "env": {"DISPLAY": ":99"},
                "tags": ["editor", "development", "ide"],
                "rating": 4.8,
                "downloads": 500000,
                "featured": True
            },
            "libreoffice": {
                "id": "libreoffice",
                "name": "LibreOffice",
                "description": "Office productivity suite",
                "version": "latest",
                "category": "productivity",
                "icon": "📊",
                "author": "The Document Foundation",
                "license": "MPL 2.0",
                "size": "300MB",
                "dependencies": [],
                "install_command": "apt-get install -y libreoffice",
                "uninstall_command": "apt-get remove -y libreoffice",
                "executable": "libreoffice",
                "args": [],
                "env": {"DISPLAY": ":99"},
                "tags": ["office", "productivity", "documents"],
                "rating": 4.3,
                "downloads": 800000,
                "featured": True
            },
            "gimp": {
                "id": "gimp",
                "name": "GIMP",
                "description": "Image manipulation program",
                "version": "latest",
                "category": "graphics",
                "icon": "🎨",
                "author": "GIMP Team",
                "license": "GPL",
                "size": "150MB",
                "dependencies": [],
                "install_command": "apt-get install -y gimp",
                "uninstall_command": "apt-get remove -y gimp",
                "executable": "gimp",
                "args": [],
                "env": {"DISPLAY": ":99"},
                "tags": ["graphics", "image", "photo"],
                "rating": 4.2,
                "downloads": 600000,
                "featured": False
            },
            "vlc": {
                "id": "vlc",
                "name": "VLC Media Player",
                "description": "Media player for audio and video",
                "version": "latest",
                "category": "multimedia",
                "icon": "🎬",
                "author": "VideoLAN",
                "license": "GPL",
                "size": "80MB",
                "dependencies": [],
                "install_command": "apt-get install -y vlc",
                "uninstall_command": "apt-get remove -y vlc",
                "executable": "vlc",
                "args": [],
                "env": {"DISPLAY": ":99"},
                "tags": ["media", "video", "audio"],
                "rating": 4.6,
                "downloads": 1200000,
                "featured": True
            }
        }
        
        # Save default apps
        for app_id, app_info in default_apps.items():
            self.available_apps[app_id] = app_info
            self._save_app_info(app_id, app_info)
    
    def _save_app_info(self, app_id: str, app_info: Dict[str, Any]):
        """Save application information"""
        try:
            app_file = os.path.join(self.marketplace_dir, f"{app_id}.json")
            with open(app_file, 'w') as f:
                json.dump(app_info, f, indent=2)
        except Exception as e:
            print(f"Error saving app info for {app_id}: {e}")
    
    async def search_apps(self, query: str = "", category: str = "", featured: bool = None) -> List[Dict[str, Any]]:
        """Search for applications"""
        try:
            results = []
            
            for app_id, app_info in self.available_apps.items():
                # Filter by query
                if query and query.lower() not in app_info.get("name", "").lower() and query.lower() not in app_info.get("description", "").lower():
                    continue
                
                # Filter by category
                if category and app_info.get("category") != category:
                    continue
                
                # Filter by featured
                if featured is not None and app_info.get("featured") != featured:
                    continue
                
                # Add installation status
                app_info["installed"] = app_id in self.installed_apps
                if app_id in self.installed_apps:
                    app_info["installed_version"] = self.installed_apps[app_id].get("version")
                
                results.append(app_info)
            
            # Sort by rating and downloads
            results.sort(key=lambda x: (x.get("rating", 0), x.get("downloads", 0)), reverse=True)
            
            return results
            
        except Exception as e:
            print(f"Error searching apps: {e}")
            return []
    
    async def get_app(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Get application information"""
        try:
            if app_id in self.available_apps:
                app_info = self.available_apps[app_id].copy()
                app_info["installed"] = app_id in self.installed_apps
                if app_id in self.installed_apps:
                    app_info["installed_version"] = self.installed_apps[app_id].get("version")
                return app_info
            return None
            
        except Exception as e:
            print(f"Error getting app {app_id}: {e}")
            return None
    
    async def install_app(self, app_id: str) -> bool:
        """Install an application"""
        try:
            if app_id not in self.available_apps:
                return False
            
            app_info = self.available_apps[app_id]
            
            # Check if already installed
            if app_id in self.installed_apps:
                return True
            
            # Install dependencies
            for dep in app_info.get("dependencies", []):
                subprocess.run([
                    "apt-get", "install", "-y", dep
                ], check=True)
            
            # Install application
            install_command = app_info.get("install_command", "")
            if install_command:
                subprocess.run(install_command.split(), check=True)
            
            # Add to installed apps
            self.installed_apps[app_id] = {
                "version": app_info.get("version", "latest"),
                "installed_at": time.time(),
                "status": "installed"
            }
            
            self._save_installed_apps()
            
            print(f"✅ Installed {app_info['name']}")
            return True
            
        except Exception as e:
            print(f"Error installing app {app_id}: {e}")
            return False
    
    async def uninstall_app(self, app_id: str) -> bool:
        """Uninstall an application"""
        try:
            if app_id not in self.installed_apps:
                return False
            
            app_info = self.available_apps.get(app_id, {})
            
            # Uninstall application
            uninstall_command = app_info.get("uninstall_command", "")
            if uninstall_command:
                subprocess.run(uninstall_command.split(), check=True)
            
            # Remove from installed apps
            del self.installed_apps[app_id]
            self._save_installed_apps()
            
            print(f"✅ Uninstalled {app_info.get('name', app_id)}")
            return True
            
        except Exception as e:
            print(f"Error uninstalling app {app_id}: {e}")
            return False
    
    async def update_app(self, app_id: str) -> bool:
        """Update an application"""
        try:
            if app_id not in self.installed_apps:
                return False
            
            # Uninstall and reinstall
            await self.uninstall_app(app_id)
            return await self.install_app(app_id)
            
        except Exception as e:
            print(f"Error updating app {app_id}: {e}")
            return False
    
    async def get_installed_apps(self) -> List[Dict[str, Any]]:
        """Get installed applications"""
        try:
            installed = []
            for app_id in self.installed_apps:
                app_info = await self.get_app(app_id)
                if app_info:
                    installed.append(app_info)
            return installed
            
        except Exception as e:
            print(f"Error getting installed apps: {e}")
            return []
    
    async def get_categories(self) -> List[str]:
        """Get available categories"""
        try:
            categories = set()
            for app_info in self.available_apps.values():
                if app_info.get("category"):
                    categories.add(app_info["category"])
            return sorted(list(categories))
            
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
    
    async def get_featured_apps(self) -> List[Dict[str, Any]]:
        """Get featured applications"""
        try:
            return await self.search_apps(featured=True)
            
        except Exception as e:
            print(f"Error getting featured apps: {e}")
            return []
    
    async def get_popular_apps(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get popular applications"""
        try:
            apps = await self.search_apps()
            return apps[:limit]
            
        except Exception as e:
            print(f"Error getting popular apps: {e}")
            return []
    
    async def add_custom_app(self, app_info: Dict[str, Any]) -> bool:
        """Add a custom application to marketplace"""
        try:
            app_id = app_info.get("id")
            if not app_id:
                return False
            
            self.available_apps[app_id] = app_info
            self._save_app_info(app_id, app_info)
            
            print(f"✅ Added custom app {app_info['name']}")
            return True
            
        except Exception as e:
            print(f"Error adding custom app: {e}")
            return False
    
    async def remove_custom_app(self, app_id: str) -> bool:
        """Remove a custom application from marketplace"""
        try:
            if app_id in self.available_apps:
                del self.available_apps[app_id]
                
                # Remove file
                app_file = os.path.join(self.marketplace_dir, f"{app_id}.json")
                if os.path.exists(app_file):
                    os.remove(app_file)
                
                print(f"✅ Removed custom app {app_id}")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error removing custom app: {e}")
            return False
    
    async def get_marketplace_stats(self) -> Dict[str, Any]:
        """Get marketplace statistics"""
        try:
            return {
                "total_apps": len(self.available_apps),
                "installed_apps": len(self.installed_apps),
                "categories": len(await self.get_categories()),
                "featured_apps": len(await self.get_featured_apps())
            }
            
        except Exception as e:
            print(f"Error getting marketplace stats: {e}")
            return {
                "total_apps": 0,
                "installed_apps": 0,
                "categories": 0,
                "featured_apps": 0
            }

"""
Custom Application Launchers for Application Share
Provides custom launcher creation and management
"""

import asyncio
import os
import json
import time
import subprocess
from typing import Dict, List, Optional, Any
from pathlib import Path

class CustomLauncherManager:
    def __init__(self):
        self.launchers_dir = os.getenv("LAUNCHERS_DIR", "/app/launchers")
        self.custom_launchers: Dict[str, Dict[str, Any]] = {}
        
        # Create directory
        os.makedirs(self.launchers_dir, exist_ok=True)
        
        # Load existing launchers
        self._load_launchers()
    
    def _load_launchers(self):
        """Load existing custom launchers"""
        try:
            for filename in os.listdir(self.launchers_dir):
                if filename.endswith('.json'):
                    launcher_id = filename[:-5]
                    launcher_file = os.path.join(self.launchers_dir, filename)
                    with open(launcher_file, 'r') as f:
                        self.custom_launchers[launcher_id] = json.load(f)
        except Exception as e:
            print(f"Error loading launchers: {e}")
    
    def _save_launcher(self, launcher_id: str, launcher_info: Dict[str, Any]):
        """Save launcher information"""
        try:
            launcher_file = os.path.join(self.launchers_dir, f"{launcher_id}.json")
            with open(launcher_file, 'w') as f:
                json.dump(launcher_info, f, indent=2)
        except Exception as e:
            print(f"Error saving launcher {launcher_id}: {e}")
    
    async def create_launcher(self, launcher_config: Dict[str, Any]) -> Optional[str]:
        """Create a custom launcher"""
        try:
            launcher_id = launcher_config.get("id")
            if not launcher_id:
                launcher_id = f"launcher_{int(time.time())}"
            
            # Validate required fields
            required_fields = ["name", "command", "executable"]
            for field in required_fields:
                if field not in launcher_config:
                    return None
            
            # Create launcher info
            launcher_info = {
                "id": launcher_id,
                "name": launcher_config["name"],
                "description": launcher_config.get("description", ""),
                "command": launcher_config["command"],
                "executable": launcher_config["executable"],
                "args": launcher_config.get("args", []),
                "env": launcher_config.get("env", {}),
                "working_directory": launcher_config.get("working_directory", ""),
                "icon": launcher_config.get("icon", "🚀"),
                "category": launcher_config.get("category", "custom"),
                "tags": launcher_config.get("tags", []),
                "created_at": time.time(),
                "created_by": launcher_config.get("created_by", "system"),
                "enabled": launcher_config.get("enabled", True),
                "auto_start": launcher_config.get("auto_start", False),
                "restart_on_crash": launcher_config.get("restart_on_crash", False),
                "max_restarts": launcher_config.get("max_restarts", 3),
                "timeout": launcher_config.get("timeout", 30),
                "resource_limits": launcher_config.get("resource_limits", {}),
                "dependencies": launcher_config.get("dependencies", []),
                "pre_launch_script": launcher_config.get("pre_launch_script", ""),
                "post_launch_script": launcher_config.get("post_launch_script", ""),
                "health_check": launcher_config.get("health_check", {}),
                "logging": launcher_config.get("logging", {
                    "enabled": True,
                    "level": "INFO",
                    "file": f"/app/logs/{launcher_id}.log"
                })
            }
            
            # Save launcher
            self.custom_launchers[launcher_id] = launcher_info
            self._save_launcher(launcher_id, launcher_info)
            
            print(f"✅ Created custom launcher: {launcher_info['name']}")
            return launcher_id
            
        except Exception as e:
            print(f"Error creating launcher: {e}")
            return None
    
    async def update_launcher(self, launcher_id: str, updates: Dict[str, Any]) -> bool:
        """Update a custom launcher"""
        try:
            if launcher_id not in self.custom_launchers:
                return False
            
            # Update launcher info
            self.custom_launchers[launcher_id].update(updates)
            self.custom_launchers[launcher_id]["updated_at"] = time.time()
            
            # Save updated launcher
            self._save_launcher(launcher_id, self.custom_launchers[launcher_id])
            
            print(f"✅ Updated launcher: {launcher_id}")
            return True
            
        except Exception as e:
            print(f"Error updating launcher: {e}")
            return False
    
    async def delete_launcher(self, launcher_id: str) -> bool:
        """Delete a custom launcher"""
        try:
            if launcher_id not in self.custom_launchers:
                return False
            
            # Remove from memory
            del self.custom_launchers[launcher_id]
            
            # Remove file
            launcher_file = os.path.join(self.launchers_dir, f"{launcher_id}.json")
            if os.path.exists(launcher_file):
                os.remove(launcher_file)
            
            print(f"✅ Deleted launcher: {launcher_id}")
            return True
            
        except Exception as e:
            print(f"Error deleting launcher: {e}")
            return False
    
    async def get_launcher(self, launcher_id: str) -> Optional[Dict[str, Any]]:
        """Get launcher information"""
        try:
            return self.custom_launchers.get(launcher_id)
        except Exception as e:
            print(f"Error getting launcher {launcher_id}: {e}")
            return None
    
    async def list_launchers(self, category: str = None, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """List custom launchers"""
        try:
            launchers = []
            for launcher_id, launcher_info in self.custom_launchers.items():
                # Filter by category
                if category and launcher_info.get("category") != category:
                    continue
                
                # Filter by enabled status
                if enabled_only and not launcher_info.get("enabled", True):
                    continue
                
                launchers.append(launcher_info)
            
            return launchers
            
        except Exception as e:
            print(f"Error listing launchers: {e}")
            return []
    
    async def launch_application(self, launcher_id: str, user_id: str = None) -> Optional[Dict[str, Any]]:
        """Launch an application using a custom launcher"""
        try:
            if launcher_id not in self.custom_launchers:
                return None
            
            launcher = self.custom_launchers[launcher_id]
            if not launcher.get("enabled", True):
                return None
            
            # Run pre-launch script
            if launcher.get("pre_launch_script"):
                await self._run_script(launcher["pre_launch_script"])
            
            # Prepare environment
            env = os.environ.copy()
            env.update(launcher.get("env", {}))
            env["DISPLAY"] = env.get("DISPLAY", ":99")
            
            # Prepare command
            command = launcher["command"]
            if launcher.get("args"):
                command += " " + " ".join(launcher["args"])
            
            # Set working directory
            working_dir = launcher.get("working_directory", "")
            if not working_dir:
                working_dir = None
            
            # Launch application
            process = await asyncio.create_subprocess_exec(
                *command.split(),
                env=env,
                cwd=working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Store process info
            process_info = {
                "launcher_id": launcher_id,
                "process_id": process.pid,
                "started_at": time.time(),
                "user_id": user_id,
                "status": "running",
                "restart_count": 0
            }
            
            # Run post-launch script
            if launcher.get("post_launch_script"):
                await self._run_script(launcher["post_launch_script"])
            
            print(f"✅ Launched application: {launcher['name']} (PID: {process.pid})")
            return process_info
            
        except Exception as e:
            print(f"Error launching application: {e}")
            return None
    
    async def _run_script(self, script: str):
        """Run a script"""
        try:
            if script:
                subprocess.run(script, shell=True, check=True)
        except Exception as e:
            print(f"Error running script: {e}")
    
    async def stop_application(self, process_id: int) -> bool:
        """Stop a running application"""
        try:
            subprocess.run(["kill", str(process_id)], check=True)
            print(f"✅ Stopped application (PID: {process_id})")
            return True
        except Exception as e:
            print(f"Error stopping application: {e}")
            return False
    
    async def get_launcher_categories(self) -> List[str]:
        """Get launcher categories"""
        try:
            categories = set()
            for launcher_info in self.custom_launchers.values():
                if launcher_info.get("category"):
                    categories.add(launcher_info["category"])
            return sorted(list(categories))
        except Exception as e:
            print(f"Error getting launcher categories: {e}")
            return []
    
    async def create_launcher_template(self, template_type: str) -> Dict[str, Any]:
        """Create a launcher template"""
        try:
            templates = {
                "web_app": {
                    "name": "Web Application",
                    "description": "Launch a web application",
                    "command": "python -m http.server",
                    "executable": "python",
                    "args": ["-m", "http.server", "8000"],
                    "env": {"DISPLAY": ":99"},
                    "category": "web",
                    "tags": ["web", "http", "server"]
                },
                "desktop_app": {
                    "name": "Desktop Application",
                    "description": "Launch a desktop application",
                    "command": "application",
                    "executable": "application",
                    "args": [],
                    "env": {"DISPLAY": ":99"},
                    "category": "desktop",
                    "tags": ["desktop", "gui"]
                },
                "service": {
                    "name": "Background Service",
                    "description": "Launch a background service",
                    "command": "service",
                    "executable": "service",
                    "args": [],
                    "env": {},
                    "category": "service",
                    "tags": ["service", "background"],
                    "auto_start": True
                },
                "development": {
                    "name": "Development Environment",
                    "description": "Launch development tools",
                    "command": "code",
                    "executable": "code",
                    "args": ["--new-window"],
                    "env": {"DISPLAY": ":99"},
                    "category": "development",
                    "tags": ["development", "ide", "editor"]
                }
            }
            
            return templates.get(template_type, {})
            
        except Exception as e:
            print(f"Error creating launcher template: {e}")
            return {}
    
    async def export_launcher(self, launcher_id: str) -> Optional[Dict[str, Any]]:
        """Export launcher configuration"""
        try:
            if launcher_id not in self.custom_launchers:
                return None
            
            launcher = self.custom_launchers[launcher_id].copy()
            # Remove sensitive information
            launcher.pop("created_at", None)
            launcher.pop("updated_at", None)
            launcher.pop("created_by", None)
            
            return launcher
            
        except Exception as e:
            print(f"Error exporting launcher: {e}")
            return None
    
    async def import_launcher(self, launcher_config: Dict[str, Any]) -> Optional[str]:
        """Import launcher configuration"""
        try:
            return await self.create_launcher(launcher_config)
        except Exception as e:
            print(f"Error importing launcher: {e}")
            return None

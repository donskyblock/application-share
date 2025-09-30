"""
Application Manager for Application Share
Handles starting, stopping, and managing GUI applications
"""

import os
import asyncio
import subprocess
import psutil
import secrets
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

class ApplicationManager:
    def __init__(self):
        self.running_apps: Dict[str, Dict[str, Any]] = {}
        self.allowed_apps = os.getenv("ALLOWED_APPLICATIONS", "firefox,code,cursor,gedit,libreoffice").split(",")
        self.max_concurrent = int(os.getenv("MAX_CONCURRENT_APPS", "10"))
        self.display = os.getenv("DISPLAY", ":0")
        self.temp_dir = os.getenv("TEMP_DIR", "/tmp/appshare")
        
        # Ensure temp directory exists
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def initialize(self):
        """Initialize the application manager"""
        print("🔧 Initializing Application Manager...")
        # Clean up any orphaned processes
        await self._cleanup_orphaned_processes()
        print("✅ Application Manager initialized")
    
    async def cleanup(self):
        """Cleanup running applications"""
        print("🧹 Cleaning up running applications...")
        for app_id in list(self.running_apps.keys()):
            await self.stop_application(app_id, None)
        print("✅ Application Manager cleanup complete")
    
    async def _cleanup_orphaned_processes(self):
        """Clean up any orphaned application processes"""
        try:
            # This is a simplified cleanup - in production you'd want more sophisticated process tracking
            pass
        except Exception as e:
            print(f"Warning: Error during orphaned process cleanup: {e}")
    
    async def get_available_applications(self) -> List[Dict[str, str]]:
        """Get list of available applications"""
        available_apps = []
        
        for app_name in self.allowed_apps:
            app_name = app_name.strip()
            if await self._is_application_available(app_name):
                available_apps.append({
                    "name": app_name,
                    "display_name": app_name.title(),
                    "description": f"Run {app_name} application",
                    "icon": f"/static/icons/{app_name}.png"  # Placeholder for icons
                })
        
        return available_apps
    
    async def _is_application_available(self, app_name: str) -> bool:
        """Check if an application is available in the system"""
        try:
            # Check if the application exists in PATH
            result = subprocess.run(
                ["which", app_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    async def start_application(self, app_name: str, user_id: str) -> Dict[str, Any]:
        """Start a GUI application"""
        if app_name not in self.allowed_apps:
            raise ValueError(f"Application '{app_name}' is not allowed")
        
        if len(self.running_apps) >= self.max_concurrent:
            raise ValueError(f"Maximum concurrent applications ({self.max_concurrent}) reached")
        
        app_id = secrets.token_urlsafe(16)
        
        try:
            # Set up environment for the application
            env = os.environ.copy()
            env["DISPLAY"] = self.display
            env["HOME"] = os.path.expanduser("~")
            
            # Start the application process
            process = await asyncio.create_subprocess_exec(
                app_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=os.path.expanduser("~")
            )
            
            # Store application info
            app_info = {
                "id": app_id,
                "name": app_name,
                "user_id": user_id,
                "process": process,
                "pid": process.pid,
                "started_at": datetime.utcnow().isoformat(),
                "status": "running"
            }
            
            self.running_apps[app_id] = app_info
            
            # Start monitoring task
            asyncio.create_task(self._monitor_application(app_id))
            
            return app_info
            
        except Exception as e:
            raise Exception(f"Failed to start application '{app_name}': {str(e)}")
    
    async def stop_application(self, app_id: str, user_id: Optional[str]) -> bool:
        """Stop a running application"""
        if app_id not in self.running_apps:
            raise ValueError(f"Application '{app_id}' is not running")
        
        app_info = self.running_apps[app_id]
        
        # Check if user has permission to stop this app
        if user_id and app_info["user_id"] != user_id:
            raise PermissionError("You don't have permission to stop this application")
        
        try:
            process = app_info["process"]
            
            # Terminate the process
            if process.returncode is None:
                process.terminate()
                
                # Wait for graceful termination
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    # Force kill if it doesn't terminate gracefully
                    process.kill()
                    await process.wait()
            
            # Remove from running apps
            del self.running_apps[app_id]
            
            return True
            
        except Exception as e:
            print(f"Error stopping application {app_id}: {e}")
            return False
    
    async def get_application_status(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a running application"""
        if app_id not in self.running_apps:
            return None
        
        app_info = self.running_apps[app_id]
        process = app_info["process"]
        
        # Check if process is still running
        if process.returncode is not None:
            app_info["status"] = "stopped"
            app_info["stopped_at"] = datetime.utcnow().isoformat()
        
        return {
            "id": app_info["id"],
            "name": app_info["name"],
            "status": app_info["status"],
            "pid": app_info["pid"],
            "started_at": app_info["started_at"],
            "stopped_at": app_info.get("stopped_at")
        }
    
    async def list_running_applications(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all running applications, optionally filtered by user"""
        apps = []
        for app_id, app_info in self.running_apps.items():
            if user_id is None or app_info["user_id"] == user_id:
                status = await self.get_application_status(app_id)
                if status:
                    apps.append(status)
        return apps
    
    async def _monitor_application(self, app_id: str):
        """Monitor an application process"""
        try:
            app_info = self.running_apps.get(app_id)
            if not app_info:
                return
            
            process = app_info["process"]
            
            # Wait for process to complete
            await process.wait()
            
            # Update status
            app_info["status"] = "stopped"
            app_info["stopped_at"] = datetime.utcnow().isoformat()
            
            print(f"Application {app_id} ({app_info['name']}) has stopped")
            
        except Exception as e:
            print(f"Error monitoring application {app_id}: {e}")
        finally:
            # Clean up if still in running apps
            if app_id in self.running_apps:
                del self.running_apps[app_id]

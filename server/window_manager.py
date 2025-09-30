"""
Window Manager for Application Share
Handles window detection, screenshots, and input forwarding for GUI applications
"""

import os
import asyncio
import subprocess
import json
import base64
from typing import Dict, List, Optional, Any, Tuple
import cv2
import numpy as np
from PIL import Image
import io

class WindowManager:
    def __init__(self):
        self.display = os.getenv("DISPLAY", ":0")
        self.temp_dir = os.getenv("TEMP_DIR", "/tmp/appshare")
        self.window_cache: Dict[str, Dict[str, Any]] = {}
        
        # Ensure temp directory exists
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def initialize(self):
        """Initialize the window manager"""
        print("🪟 Initializing Window Manager...")
        # Check if X11 tools are available
        await self._check_x11_tools()
        print("✅ Window Manager initialized")
    
    async def cleanup(self):
        """Cleanup window manager resources"""
        print("🧹 Cleaning up Window Manager...")
        self.window_cache.clear()
        print("✅ Window Manager cleanup complete")
    
    async def _check_x11_tools(self):
        """Check if required X11 tools are available"""
        required_tools = ["xwininfo", "xdotool", "import"]
        missing_tools = []
        
        for tool in required_tools:
            try:
                result = subprocess.run(
                    ["which", tool],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    missing_tools.append(tool)
            except Exception:
                missing_tools.append(tool)
        
        if missing_tools:
            print(f"Warning: Missing X11 tools: {', '.join(missing_tools)}")
            print("Some features may not work properly. Install with: sudo apt-get install x11-utils xdotool imagemagick")
    
    async def get_application_windows(self, app_id: str) -> List[Dict[str, Any]]:
        """Get all windows for a specific application"""
        try:
            # Get process ID for the application
            pid = await self._get_app_pid(app_id)
            if not pid:
                return []
            
            # Get windows for this PID
            windows = await self._get_windows_by_pid(pid)
            
            # Cache window information
            self.window_cache[app_id] = {
                "pid": pid,
                "windows": windows,
                "last_updated": asyncio.get_event_loop().time()
            }
            
            return windows
            
        except Exception as e:
            print(f"Error getting windows for app {app_id}: {e}")
            return []
    
    async def _get_app_pid(self, app_id: str) -> Optional[int]:
        """Get process ID for an application"""
        try:
            # This would typically come from the app manager
            # For now, we'll try to find it by process name
            result = subprocess.run(
                ["pgrep", "-f", app_id],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return int(result.stdout.strip().split('\n')[0])
            
            return None
            
        except Exception as e:
            print(f"Error getting PID for app {app_id}: {e}")
            return None
    
    async def _get_windows_by_pid(self, pid: int) -> List[Dict[str, Any]]:
        """Get all windows for a specific process ID"""
        try:
            # Use xwininfo to find windows
            result = subprocess.run(
                ["xwininfo", "-tree", "-root"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return []
            
            windows = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                if f"pid {pid}" in line or f"pid: {pid}" in line:
                    # Extract window ID and title
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        window_id = parts[0]
                        title = ' '.join(parts[1:]) if len(parts) > 1 else "Unknown"
                        
                        # Get window geometry
                        geometry = await self._get_window_geometry(window_id)
                        
                        windows.append({
                            "id": window_id,
                            "title": title,
                            "geometry": geometry,
                            "visible": True
                        })
            
            return windows
            
        except Exception as e:
            print(f"Error getting windows for PID {pid}: {e}")
            return []
    
    async def _get_window_geometry(self, window_id: str) -> Dict[str, int]:
        """Get geometry information for a window"""
        try:
            result = subprocess.run(
                ["xwininfo", "-id", window_id],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return {"x": 0, "y": 0, "width": 0, "height": 0}
            
            geometry = {"x": 0, "y": 0, "width": 0, "height": 0}
            
            for line in result.stdout.split('\n'):
                if 'Absolute upper-left X:' in line:
                    geometry["x"] = int(line.split(':')[1].strip())
                elif 'Absolute upper-left Y:' in line:
                    geometry["y"] = int(line.split(':')[1].strip())
                elif 'Width:' in line:
                    geometry["width"] = int(line.split(':')[1].strip())
                elif 'Height:' in line:
                    geometry["height"] = int(line.split(':')[1].strip())
            
            return geometry
            
        except Exception as e:
            print(f"Error getting geometry for window {window_id}: {e}")
            return {"x": 0, "y": 0, "width": 0, "height": 0}
    
    async def capture_screenshot(self, app_id: str, window_id: Optional[str] = None) -> str:
        """Capture screenshot of application or specific window"""
        try:
            if window_id:
                # Capture specific window
                screenshot_path = os.path.join(self.temp_dir, f"screenshot_{app_id}_{window_id}.png")
                result = subprocess.run(
                    ["import", "-window", window_id, screenshot_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            else:
                # Capture entire screen (fallback)
                screenshot_path = os.path.join(self.temp_dir, f"screenshot_{app_id}_screen.png")
                result = subprocess.run(
                    ["import", "-window", "root", screenshot_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            
            if result.returncode != 0:
                raise Exception(f"Screenshot failed: {result.stderr}")
            
            # Convert to base64
            with open(screenshot_path, "rb") as f:
                image_data = f.read()
            
            # Clean up temporary file
            os.remove(screenshot_path)
            
            # Convert to base64
            base64_data = base64.b64encode(image_data).decode('utf-8')
            return f"data:image/png;base64,{base64_data}"
            
        except Exception as e:
            print(f"Error capturing screenshot for app {app_id}: {e}")
            return ""
    
    async def send_mouse_event(self, window_id: str, event_type: str, x: int, y: int, button: int = 1):
        """Send mouse event to a window"""
        try:
            if event_type == "click":
                subprocess.run([
                    "xdotool", "mousemove", "--window", window_id, str(x), str(y),
                    "click", str(button)
                ], timeout=5)
            elif event_type == "mousemove":
                subprocess.run([
                    "xdotool", "mousemove", "--window", window_id, str(x), str(y)
                ], timeout=5)
            elif event_type == "mousedown":
                subprocess.run([
                    "xdotool", "mousedown", "--window", window_id, str(button)
                ], timeout=5)
            elif event_type == "mouseup":
                subprocess.run([
                    "xdotool", "mouseup", "--window", window_id, str(button)
                ], timeout=5)
                
        except Exception as e:
            print(f"Error sending mouse event: {e}")
    
    async def send_keyboard_event(self, window_id: str, key: str, modifiers: List[str] = None):
        """Send keyboard event to a window"""
        try:
            cmd = ["xdotool", "key", "--window", window_id]
            
            if modifiers:
                for mod in modifiers:
                    cmd.append(f"{mod}+")
            
            cmd.append(key)
            
            subprocess.run(cmd, timeout=5)
            
        except Exception as e:
            print(f"Error sending keyboard event: {e}")
    
    async def resize_window(self, window_id: str, width: int, height: int):
        """Resize a window"""
        try:
            subprocess.run([
                "xdotool", "windowsize", "--sync", window_id, str(width), str(height)
            ], timeout=5)
        except Exception as e:
            print(f"Error resizing window: {e}")
    
    async def move_window(self, window_id: str, x: int, y: int):
        """Move a window"""
        try:
            subprocess.run([
                "xdotool", "windowmove", "--sync", window_id, str(x), str(y)
            ], timeout=5)
        except Exception as e:
            print(f"Error moving window: {e}")
    
    async def focus_window(self, window_id: str):
        """Focus a window"""
        try:
            subprocess.run([
                "xdotool", "windowactivate", "--sync", window_id
            ], timeout=5)
        except Exception as e:
            print(f"Error focusing window: {e}")

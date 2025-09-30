"""
Advanced Window Manager for Application Share
Provides tiling, snapping, and advanced window management features
"""

import asyncio
import subprocess
import os
import json
import time
from typing import Dict, List, Optional, Any, Tuple
import math

class AdvancedWindowManager:
    def __init__(self):
        self.display = os.getenv("DISPLAY", ":99")
        self.screen_width = 1920
        self.screen_height = 1080
        self.window_layouts: Dict[str, Dict[str, Any]] = {}
        self.tiling_enabled = True
        self.snap_zones = {
            "left": {"x": 0, "y": 0, "width": 0.5, "height": 1.0},
            "right": {"x": 0.5, "y": 0, "width": 0.5, "height": 1.0},
            "top": {"x": 0, "y": 0, "width": 1.0, "height": 0.5},
            "bottom": {"x": 0, "y": 0.5, "width": 1.0, "height": 0.5},
            "top-left": {"x": 0, "y": 0, "width": 0.5, "height": 0.5},
            "top-right": {"x": 0.5, "y": 0, "width": 0.5, "height": 0.5},
            "bottom-left": {"x": 0, "y": 0.5, "width": 0.5, "height": 0.5},
            "bottom-right": {"x": 0.5, "y": 0.5, "width": 0.5, "height": 0.5}
        }
    
    async def get_screen_info(self) -> Dict[str, Any]:
        """Get screen information"""
        try:
            result = subprocess.run([
                "xrandr", "--query"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if ' connected' in line and 'primary' in line:
                        parts = line.split()
                        resolution = parts[3]
                        if 'x' in resolution:
                            width, height = resolution.split('x')
                            self.screen_width = int(width)
                            self.screen_height = int(height)
                            break
            
            return {
                "width": self.screen_width,
                "height": self.screen_height,
                "display": self.display
            }
            
        except Exception as e:
            print(f"Error getting screen info: {e}")
            return {"width": 1920, "height": 1080, "display": self.display}
    
    async def get_window_info(self, window_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed window information"""
        try:
            result = subprocess.run([
                "xwininfo", "-id", window_id
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                return None
            
            window_info = {
                "id": window_id,
                "x": 0, "y": 0, "width": 0, "height": 0,
                "title": "",
                "class": "",
                "state": "normal"
            }
            
            for line in result.stdout.split('\n'):
                if 'Absolute upper-left X:' in line:
                    window_info["x"] = int(line.split(':')[1].strip())
                elif 'Absolute upper-left Y:' in line:
                    window_info["y"] = int(line.split(':')[1].strip())
                elif 'Width:' in line:
                    window_info["width"] = int(line.split(':')[1].strip())
                elif 'Height:' in line:
                    window_info["height"] = int(line.split(':')[1].strip())
                elif 'xwininfo: Window id:' in line:
                    window_info["title"] = line.split('"')[1] if '"' in line else ""
            
            # Get window class
            class_result = subprocess.run([
                "xprop", "-id", window_id, "WM_CLASS"
            ], capture_output=True, text=True, timeout=5)
            
            if class_result.returncode == 0:
                class_line = class_result.stdout.strip()
                if '=' in class_line:
                    window_info["class"] = class_line.split('=')[1].strip().strip('"')
            
            return window_info
            
        except Exception as e:
            print(f"Error getting window info: {e}")
            return None
    
    async def tile_windows(self, layout_type: str = "tiled") -> bool:
        """Tile all windows"""
        try:
            if not self.tiling_enabled:
                return False
            
            # Get all windows
            windows = await self.get_all_windows()
            if not windows:
                return False
            
            # Apply tiling layout
            if layout_type == "tiled":
                await self._apply_tiled_layout(windows)
            elif layout_type == "cascade":
                await self._apply_cascade_layout(windows)
            elif layout_type == "grid":
                await self._apply_grid_layout(windows)
            elif layout_type == "maximize":
                await self._apply_maximize_layout(windows)
            
            return True
            
        except Exception as e:
            print(f"Error tiling windows: {e}")
            return False
    
    async def _apply_tiled_layout(self, windows: List[Dict[str, Any]]):
        """Apply tiled layout to windows"""
        try:
            if not windows:
                return
            
            # Calculate tile dimensions
            num_windows = len(windows)
            cols = math.ceil(math.sqrt(num_windows))
            rows = math.ceil(num_windows / cols)
            
            tile_width = self.screen_width // cols
            tile_height = self.screen_height // rows
            
            for i, window in enumerate(windows):
                row = i // cols
                col = i % cols
                
                x = col * tile_width
                y = row * tile_height
                width = tile_width
                height = tile_height
                
                # Adjust for last row
                if row == rows - 1 and i == num_windows - 1:
                    width = self.screen_width - x
                
                await self.resize_window(window["id"], x, y, width, height)
                
        except Exception as e:
            print(f"Error applying tiled layout: {e}")
    
    async def _apply_cascade_layout(self, windows: List[Dict[str, Any]]):
        """Apply cascade layout to windows"""
        try:
            if not windows:
                return
            
            cascade_offset = 30
            window_width = self.screen_width // 2
            window_height = self.screen_height // 2
            
            for i, window in enumerate(windows):
                x = i * cascade_offset
                y = i * cascade_offset
                width = window_width
                height = window_height
                
                # Ensure windows don't go off screen
                if x + width > self.screen_width:
                    x = self.screen_width - width
                if y + height > self.screen_height:
                    y = self.screen_height - height
                
                await self.resize_window(window["id"], x, y, width, height)
                
        except Exception as e:
            print(f"Error applying cascade layout: {e}")
    
    async def _apply_grid_layout(self, windows: List[Dict[str, Any]]):
        """Apply grid layout to windows"""
        try:
            if not windows:
                return
            
            # Calculate grid dimensions
            num_windows = len(windows)
            cols = math.ceil(math.sqrt(num_windows))
            rows = math.ceil(num_windows / cols)
            
            # Add gaps between windows
            gap = 10
            tile_width = (self.screen_width - (cols - 1) * gap) // cols
            tile_height = (self.screen_height - (rows - 1) * gap) // rows
            
            for i, window in enumerate(windows):
                row = i // cols
                col = i % cols
                
                x = col * (tile_width + gap)
                y = row * (tile_height + gap)
                width = tile_width
                height = tile_height
                
                await self.resize_window(window["id"], x, y, width, height)
                
        except Exception as e:
            print(f"Error applying grid layout: {e}")
    
    async def _apply_maximize_layout(self, windows: List[Dict[str, Any]]):
        """Apply maximize layout to windows"""
        try:
            if not windows:
                return
            
            # Maximize all windows
            for window in windows:
                await self.maximize_window(window["id"])
                
        except Exception as e:
            print(f"Error applying maximize layout: {e}")
    
    async def snap_window(self, window_id: str, snap_zone: str) -> bool:
        """Snap window to a specific zone"""
        try:
            if snap_zone not in self.snap_zones:
                return False
            
            zone = self.snap_zones[snap_zone]
            x = int(zone["x"] * self.screen_width)
            y = int(zone["y"] * self.screen_height)
            width = int(zone["width"] * self.screen_width)
            height = int(zone["height"] * self.screen_height)
            
            await self.resize_window(window_id, x, y, width, height)
            return True
            
        except Exception as e:
            print(f"Error snapping window: {e}")
            return False
    
    async def resize_window(self, window_id: str, x: int, y: int, width: int, height: int):
        """Resize and move window"""
        try:
            # Move window
            subprocess.run([
                "xdotool", "windowmove", "--sync", window_id, str(x), str(y)
            ], timeout=5)
            
            # Resize window
            subprocess.run([
                "xdotool", "windowsize", "--sync", window_id, str(width), str(height)
            ], timeout=5)
            
        except Exception as e:
            print(f"Error resizing window: {e}")
    
    async def maximize_window(self, window_id: str):
        """Maximize window"""
        try:
            subprocess.run([
                "xdotool", "windowmove", window_id, "0", "0"
            ], timeout=5)
            
            subprocess.run([
                "xdotool", "windowsize", window_id, str(self.screen_width), str(self.screen_height)
            ], timeout=5)
            
        except Exception as e:
            print(f"Error maximizing window: {e}")
    
    async def minimize_window(self, window_id: str):
        """Minimize window"""
        try:
            subprocess.run([
                "xdotool", "windowminimize", window_id
            ], timeout=5)
            
        except Exception as e:
            print(f"Error minimizing window: {e}")
    
    async def close_window(self, window_id: str):
        """Close window"""
        try:
            subprocess.run([
                "xdotool", "windowclose", window_id
            ], timeout=5)
            
        except Exception as e:
            print(f"Error closing window: {e}")
    
    async def focus_window(self, window_id: str):
        """Focus window"""
        try:
            subprocess.run([
                "xdotool", "windowactivate", "--sync", window_id
            ], timeout=5)
            
        except Exception as e:
            print(f"Error focusing window: {e}")
    
    async def get_all_windows(self) -> List[Dict[str, Any]]:
        """Get all visible windows"""
        try:
            result = subprocess.run([
                "xwininfo", "-tree", "-root"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return []
            
            windows = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                if '0x' in line and 'pid' in line:
                    # Extract window ID
                    parts = line.strip().split()
                    if parts:
                        window_id = parts[0]
                        window_info = await self.get_window_info(window_id)
                        if window_info and window_info["width"] > 0 and window_info["height"] > 0:
                            windows.append(window_info)
            
            return windows
            
        except Exception as e:
            print(f"Error getting all windows: {e}")
            return []
    
    async def create_layout(self, layout_name: str, layout_config: Dict[str, Any]) -> bool:
        """Create a custom window layout"""
        try:
            self.window_layouts[layout_name] = {
                "name": layout_name,
                "config": layout_config,
                "created_at": time.time()
            }
            return True
            
        except Exception as e:
            print(f"Error creating layout: {e}")
            return False
    
    async def apply_layout(self, layout_name: str) -> bool:
        """Apply a custom window layout"""
        try:
            if layout_name not in self.window_layouts:
                return False
            
            layout = self.window_layouts[layout_name]
            config = layout["config"]
            
            # Apply layout configuration
            if "tiling" in config:
                await self.tile_windows(config["tiling"])
            
            if "snap_zones" in config:
                for window_id, snap_zone in config["snap_zones"].items():
                    await self.snap_window(window_id, snap_zone)
            
            return True
            
        except Exception as e:
            print(f"Error applying layout: {e}")
            return False
    
    async def get_layouts(self) -> List[Dict[str, Any]]:
        """Get available layouts"""
        return list(self.window_layouts.values())
    
    async def delete_layout(self, layout_name: str) -> bool:
        """Delete a layout"""
        try:
            if layout_name in self.window_layouts:
                del self.window_layouts[layout_name]
                return True
            return False
            
        except Exception as e:
            print(f"Error deleting layout: {e}")
            return False
    
    async def toggle_tiling(self) -> bool:
        """Toggle tiling mode"""
        try:
            self.tiling_enabled = not self.tiling_enabled
            return self.tiling_enabled
            
        except Exception as e:
            print(f"Error toggling tiling: {e}")
            return False
    
    async def get_window_manager_info(self) -> Dict[str, Any]:
        """Get window manager information"""
        try:
            screen_info = await self.get_screen_info()
            windows = await self.get_all_windows()
            
            return {
                "tiling_enabled": self.tiling_enabled,
                "screen": screen_info,
                "window_count": len(windows),
                "layouts": list(self.window_layouts.keys()),
                "snap_zones": list(self.snap_zones.keys())
            }
            
        except Exception as e:
            print(f"Error getting window manager info: {e}")
            return {
                "tiling_enabled": False,
                "screen": {"width": 1920, "height": 1080},
                "window_count": 0,
                "layouts": [],
                "snap_zones": []
            }

"""
VNC Server Integration for Application Share
Provides VNC server management and WebSocket streaming
"""

import asyncio
import subprocess
import os
import json
import base64
import time
from typing import Dict, Optional, Any
import websockets
from PIL import Image
import io

class VNCServer:
    def __init__(self):
        self.vnc_process = None
        self.vnc_port = int(os.getenv("VNC_PORT", "5900"))
        self.vnc_password = os.getenv("VNC_PASSWORD", "")
        self.display = os.getenv("DISPLAY", ":99")
        self.is_running = False
        self.websocket_clients = set()
        
    async def start_vnc_server(self) -> bool:
        """Start VNC server"""
        try:
            if self.is_running:
                return True
                
            # Kill any existing VNC processes
            subprocess.run(["pkill", "-f", "x11vnc"], capture_output=True)
            
            # Start VNC server
            cmd = [
                "x11vnc",
                "-display", self.display,
                "-rfbport", str(self.vnc_port),
                "-forever",
                "-shared",
                "-nopw" if not self.vnc_password else f"-passwd {self.vnc_password}",
                "-xkb",
                "-noxrecord",
                "-noxfixes",
                "-noxdamage",
                "-listen", "0.0.0.0"
            ]
            
            self.vnc_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for VNC to start
            await asyncio.sleep(2)
            
            if self.vnc_process.poll() is None:
                self.is_running = True
                print(f"✅ VNC server started on port {self.vnc_port}")
                return True
            else:
                print("❌ Failed to start VNC server")
                return False
                
        except Exception as e:
            print(f"❌ Error starting VNC server: {e}")
            return False
    
    async def stop_vnc_server(self):
        """Stop VNC server"""
        if self.vnc_process:
            self.vnc_process.terminate()
            self.vnc_process.wait()
            self.vnc_process = None
        self.is_running = False
        print("🛑 VNC server stopped")
    
    async def get_vnc_info(self) -> Dict[str, Any]:
        """Get VNC server information"""
        return {
            "running": self.is_running,
            "port": self.vnc_port,
            "display": self.display,
            "password_required": bool(self.vnc_password)
        }
    
    async def capture_screen(self) -> str:
        """Capture screen and return base64 encoded image"""
        try:
            # Use ImageMagick to capture screen
            result = subprocess.run([
                "import", "-window", "root", "-"
            ], capture_output=True, timeout=5)
            
            if result.returncode == 0:
                # Convert to base64
                image_data = result.stdout
                base64_data = base64.b64encode(image_data).decode('utf-8')
                return f"data:image/png;base64,{base64_data}"
            else:
                return ""
                
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return ""
    
    async def start_websocket_server(self, port: int = 8765):
        """Start WebSocket server for live streaming"""
        async def handle_client(websocket, path):
            self.websocket_clients.add(websocket)
            print(f"Client connected: {websocket.remote_address}")
            
            try:
                while True:
                    # Send screen capture
                    screenshot = await self.capture_screen()
                    if screenshot:
                        await websocket.send(json.dumps({
                            "type": "screenshot",
                            "data": screenshot,
                            "timestamp": time.time()
                        }))
                    
                    await asyncio.sleep(0.1)  # 10 FPS
                    
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                self.websocket_clients.discard(websocket)
                print(f"Client disconnected: {websocket.remote_address}")
        
        # Start WebSocket server
        server = await websockets.serve(handle_client, "0.0.0.0", port)
        print(f"✅ WebSocket server started on port {port}")
        return server

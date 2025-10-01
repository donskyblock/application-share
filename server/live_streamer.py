"""
Live Streaming Server for Application Share
Provides real-time screen streaming and input forwarding
"""

import asyncio
import os
import subprocess
import base64
import json
import time
import cv2
import numpy as np
from typing import Dict, Set, Any, Optional
import websockets
from PIL import Image
import io

class LiveStreamer:
    def __init__(self):
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.is_streaming = False
        self.display = os.getenv("DISPLAY", ":99")
        self.frame_rate = 30
        self.quality = 80
        
    async def start_streaming(self, port: int = 8765):
        """Start live streaming server"""
        async def handle_client(websocket, path):
            self.clients.add(websocket)
            print(f"Live client connected: {websocket.remote_address}")
            
            try:
                # Send initial configuration
                await websocket.send(json.dumps({
                    "type": "config",
                    "frame_rate": self.frame_rate,
                    "quality": self.quality
                }))
                
                # Keep connection alive
                while True:
                    await websocket.ping()
                    await asyncio.sleep(1)
                    
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                self.clients.discard(websocket)
                print(f"Live client disconnected: {websocket.remote_address}")
        
        # Start WebSocket server
        server = await websockets.serve(handle_client, "0.0.0.0", port)
        self.is_streaming = True
        print(f"✅ Live streaming server started on port {port}")
        return server
    
    async def capture_and_stream(self):
        """Capture screen and stream to all clients"""
        while self.is_streaming:
            try:
                # Capture screen
                screenshot = await self.capture_screen()
                
                if screenshot and self.clients:
                    # Send to all connected clients
                    message = json.dumps({
                        "type": "frame",
                        "data": screenshot,
                        "timestamp": time.time()
                    })
                    
                    # Send to all clients concurrently
                    if self.clients:
                        await asyncio.gather(
                            *[client.send(message) for client in self.clients],
                            return_exceptions=True
                        )
                
                await asyncio.sleep(1.0 / self.frame_rate)
                
            except Exception as e:
                print(f"Error in streaming loop: {e}")
                await asyncio.sleep(0.1)
    
    async def capture_screen(self) -> Optional[str]:
        """Capture screen with OpenCV for better performance"""
        try:
            # Use xwininfo to get screen dimensions
            result = subprocess.run([
                "xwininfo", "-root", "-tree"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                return None
            
            # Capture screen with ImageMagick
            img_result = subprocess.run([
                "import", "-window", "root", "-"
            ], capture_output=True, timeout=5)
            
            if img_result.returncode != 0:
                return None
            
            # Convert to OpenCV format
            nparr = np.frombuffer(img_result.stdout, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return None
            
            # Resize for better performance
            height, width = img.shape[:2]
            if width > 1920:
                scale = 1920 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                img = cv2.resize(img, (new_width, new_height))
            
            # Encode as JPEG
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
            _, buffer = cv2.imencode('.jpg', img, encode_param)
            
            # Convert to base64
            base64_data = base64.b64encode(buffer).decode('utf-8')
            return f"data:image/jpeg;base64,{base64_data}"
            
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return None
    
    async def handle_input(self, websocket, message: Dict[str, Any]):
        """Handle input events from clients"""
        try:
            event_type = message.get("type")
            
            if event_type == "mouse":
                await self.handle_mouse_event(message)
            elif event_type == "keyboard":
                await self.handle_keyboard_event(message)
            elif event_type == "scroll":
                await self.handle_scroll_event(message)
                
        except Exception as e:
            print(f"Error handling input: {e}")
    
    async def handle_mouse_event(self, message: Dict[str, Any]):
        """Handle mouse events"""
        try:
            x = message.get("x", 0)
            y = message.get("y", 0)
            button = message.get("button", 1)
            action = message.get("action", "click")
            
            if action == "click":
                subprocess.run([
                    "xdotool", "mousemove", str(x), str(y),
                    "click", str(button)
                ], timeout=5)
            elif action == "mousemove":
                subprocess.run([
                    "xdotool", "mousemove", str(x), str(y)
                ], timeout=5)
            elif action == "mousedown":
                subprocess.run([
                    "xdotool", "mousedown", str(button)
                ], timeout=5)
            elif action == "mouseup":
                subprocess.run([
                    "xdotool", "mouseup", str(button)
                ], timeout=5)
                
        except Exception as e:
            print(f"Error handling mouse event: {e}")
    
    async def handle_keyboard_event(self, message: Dict[str, Any]):
        """Handle keyboard events"""
        try:
            key = message.get("key")
            modifiers = message.get("modifiers", [])
            
            if not key:
                return
            
            cmd = ["xdotool", "key"]
            
            # Add modifiers
            for mod in modifiers:
                cmd.append(f"{mod}+")
            
            cmd.append(key)
            
            subprocess.run(cmd, timeout=5)
            
        except Exception as e:
            print(f"Error handling keyboard event: {e}")
    
    async def handle_scroll_event(self, message: Dict[str, Any]):
        """Handle scroll events"""
        try:
            x = message.get("x", 0)
            y = message.get("y", 0)
            direction = message.get("direction", "up")
            
            # Move mouse to position
            subprocess.run([
                "xdotool", "mousemove", str(x), str(y)
            ], timeout=5)
            
            # Scroll
            if direction == "up":
                subprocess.run(["xdotool", "click", "4"], timeout=5)
            else:
                subprocess.run(["xdotool", "click", "5"], timeout=5)
                
        except Exception as e:
            print(f"Error handling scroll event: {e}")
    
    async def stop_streaming(self):
        """Stop live streaming"""
        self.is_streaming = False
        
        # Close all client connections
        for client in self.clients.copy():
            await client.close()
        
        self.clients.clear()
        print("🛑 Live streaming stopped")

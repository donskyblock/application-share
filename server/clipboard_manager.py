"""
Clipboard Manager for Application Share
Handles clipboard synchronization between client and server
"""

import asyncio
import subprocess
import os
import json
import base64
from typing import Dict, List, Optional, Any
import websockets

class ClipboardManager:
    def __init__(self):
        self.clipboard_data: Dict[str, Any] = {}
        self.clipboard_clients: List[websockets.WebSocketServerProtocol] = []
        self.sync_enabled = True
        
    async def start_clipboard_server(self, port: int = 8768):
        """Start clipboard synchronization server"""
        async def handle_clipboard_client(websocket, path):
            self.clipboard_clients.append(websocket)
            print(f"Clipboard client connected: {websocket.remote_address}")
            
            try:
                # Send current clipboard data
                if self.clipboard_data:
                    await websocket.send(json.dumps({
                        "type": "clipboard_data",
                        "data": self.clipboard_data
                    }))
                
                async for message in websocket:
                    data = json.loads(message)
                    await self.handle_clipboard_message(data)
                    
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                self.clipboard_clients.remove(websocket)
                print(f"Clipboard client disconnected: {websocket.remote_address}")
        
        # Start WebSocket server
        server = await websockets.serve(handle_clipboard_client, "0.0.0.0", port)
        print(f"✅ Clipboard server started on port {port}")
        return server
    
    async def handle_clipboard_message(self, data: Dict[str, Any]):
        """Handle clipboard message from client"""
        try:
            message_type = data.get("type")
            
            if message_type == "clipboard_data":
                await self.update_clipboard(data["data"])
            elif message_type == "get_clipboard":
                await self.send_clipboard_to_client(data.get("client_id"))
            elif message_type == "clear_clipboard":
                await self.clear_clipboard()
                
        except Exception as e:
            print(f"Error handling clipboard message: {e}")
    
    async def update_clipboard(self, clipboard_data: Dict[str, Any]):
        """Update clipboard data and sync to system"""
        try:
            self.clipboard_data = clipboard_data
            
            # Update system clipboard
            if clipboard_data.get("text"):
                await self.set_system_clipboard_text(clipboard_data["text"])
            
            if clipboard_data.get("image"):
                await self.set_system_clipboard_image(clipboard_data["image"])
            
            # Broadcast to all connected clients
            await self.broadcast_clipboard()
            
        except Exception as e:
            print(f"Error updating clipboard: {e}")
    
    async def set_system_clipboard_text(self, text: str):
        """Set system clipboard text"""
        try:
            # Use xclip to set clipboard text
            process = await asyncio.create_subprocess_exec(
                "xclip", "-selection", "clipboard",
                stdin=asyncio.subprocess.PIPE
            )
            await process.communicate(input=text.encode())
            
        except Exception as e:
            print(f"Error setting clipboard text: {e}")
    
    async def set_system_clipboard_image(self, image_data: str):
        """Set system clipboard image"""
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data.split(',')[1])
            
            # Save to temporary file
            temp_file = "/tmp/clipboard_image.png"
            with open(temp_file, 'wb') as f:
                f.write(image_bytes)
            
            # Use xclip to set clipboard image
            subprocess.run([
                "xclip", "-selection", "clipboard", "-t", "image/png", "-i", temp_file
            ], check=True)
            
            # Clean up
            os.remove(temp_file)
            
        except Exception as e:
            print(f"Error setting clipboard image: {e}")
    
    async def get_system_clipboard_text(self) -> Optional[str]:
        """Get system clipboard text"""
        try:
            process = await asyncio.create_subprocess_exec(
                "xclip", "-selection", "clipboard", "-o",
                stdout=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            return stdout.decode().strip()
            
        except Exception as e:
            print(f"Error getting clipboard text: {e}")
            return None
    
    async def get_system_clipboard_image(self) -> Optional[str]:
        """Get system clipboard image"""
        try:
            # Check if clipboard contains image
            process = await asyncio.create_subprocess_exec(
                "xclip", "-selection", "clipboard", "-t", "image/png", "-o",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0 and stdout:
                # Convert to base64
                image_data = base64.b64encode(stdout).decode('utf-8')
                return f"data:image/png;base64,{image_data}"
            
            return None
            
        except Exception as e:
            print(f"Error getting clipboard image: {e}")
            return None
    
    async def sync_from_system(self):
        """Sync clipboard from system to clients"""
        try:
            # Get system clipboard
            text = await self.get_system_clipboard_text()
            image = await self.get_system_clipboard_image()
            
            # Update clipboard data
            new_data = {}
            if text:
                new_data["text"] = text
            if image:
                new_data["image"] = image
            
            if new_data:
                await self.update_clipboard(new_data)
                
        except Exception as e:
            print(f"Error syncing from system: {e}")
    
    async def broadcast_clipboard(self):
        """Broadcast clipboard data to all clients"""
        if not self.clipboard_clients:
            return
        
        message = json.dumps({
            "type": "clipboard_data",
            "data": self.clipboard_data
        })
        
        # Send to all clients concurrently
        await asyncio.gather(
            *[client.send(message) for client in self.clipboard_clients],
            return_exceptions=True
        )
    
    async def send_clipboard_to_client(self, client_id: str):
        """Send clipboard data to specific client"""
        # This would be implemented based on your client identification system
        pass
    
    async def clear_clipboard(self):
        """Clear clipboard data"""
        try:
            self.clipboard_data = {}
            
            # Clear system clipboard
            subprocess.run([
                "xclip", "-selection", "clipboard", "/dev/null"
            ], check=True)
            
            # Broadcast to clients
            await self.broadcast_clipboard()
            
        except Exception as e:
            print(f"Error clearing clipboard: {e}")
    
    async def start_clipboard_monitoring(self):
        """Start monitoring system clipboard for changes"""
        try:
            while self.sync_enabled:
                await self.sync_from_system()
                await asyncio.sleep(1)  # Check every second
                
        except Exception as e:
            print(f"Error in clipboard monitoring: {e}")
    
    async def stop_clipboard_monitoring(self):
        """Stop clipboard monitoring"""
        self.sync_enabled = False
    
    async def get_clipboard_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get clipboard history"""
        # This would be implemented with a persistent storage system
        return []
    
    async def cleanup(self):
        """Cleanup clipboard manager"""
        await self.stop_clipboard_monitoring()
        
        # Close all client connections
        for client in self.clipboard_clients.copy():
            await client.close()
        
        self.clipboard_clients.clear()
        print("🧹 Clipboard manager cleaned up")

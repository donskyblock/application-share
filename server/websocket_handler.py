"""
WebSocket Handler for Application Share
Handles real-time communication between clients and the server
"""

import asyncio
import json
from typing import Dict, Set, Optional, Any
from datetime import datetime

class WebSocketHandler:
    def __init__(self):
        self.connected_clients: Set[str] = set()
        self.app_sessions: Dict[str, Set[str]] = {}  # app_id -> set of client_ids
        self.client_apps: Dict[str, str] = {}  # client_id -> app_id
        
    async def handle_connect(self, client_id: str):
        """Handle client connection"""
        self.connected_clients.add(client_id)
        print(f"Client {client_id} connected. Total clients: {len(self.connected_clients)}")
    
    async def handle_disconnect(self, client_id: str):
        """Handle client disconnection"""
        self.connected_clients.discard(client_id)
        
        # Remove from app sessions
        if client_id in self.client_apps:
            app_id = self.client_apps[client_id]
            if app_id in self.app_sessions:
                self.app_sessions[app_id].discard(client_id)
                if not self.app_sessions[app_id]:
                    del self.app_sessions[app_id]
            del self.client_apps[client_id]
        
        print(f"Client {client_id} disconnected. Total clients: {len(self.connected_clients)}")
    
    async def join_application(self, client_id: str, app_id: str):
        """Client joins an application session"""
        try:
            # Leave current app if any
            if client_id in self.client_apps:
                await self.leave_application(client_id)
            
            # Join new app
            if app_id not in self.app_sessions:
                self.app_sessions[app_id] = set()
            
            self.app_sessions[app_id].add(client_id)
            self.client_apps[client_id] = app_id
            
            print(f"Client {client_id} joined application {app_id}")
            
            # Send confirmation to client
            await self.send_to_client(client_id, {
                "type": "app_joined",
                "app_id": app_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            print(f"Error joining application: {e}")
            await self.send_to_client(client_id, {
                "type": "error",
                "message": f"Failed to join application: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def leave_application(self, client_id: str):
        """Client leaves current application session"""
        if client_id in self.client_apps:
            app_id = self.client_apps[client_id]
            
            if app_id in self.app_sessions:
                self.app_sessions[app_id].discard(client_id)
                if not self.app_sessions[app_id]:
                    del self.app_sessions[app_id]
            
            del self.client_apps[client_id]
            
            print(f"Client {client_id} left application {app_id}")
    
    async def handle_mouse_event(self, client_id: str, data: Dict[str, Any]):
        """Handle mouse event from client"""
        try:
            app_id = self.client_apps.get(client_id)
            if not app_id:
                return
            
            event_type = data.get("type")
            x = data.get("x", 0)
            y = data.get("y", 0)
            button = data.get("button", 1)
            
            # Forward to window manager
            from .window_manager import WindowManager
            window_manager = WindowManager()
            
            # Get the main window for the app
            windows = await window_manager.get_application_windows(app_id)
            if windows:
                main_window = windows[0]  # Use first window
                await window_manager.send_mouse_event(
                    main_window["id"], event_type, x, y, button
                )
            
            # Broadcast to other clients in the same app session
            await self.broadcast_to_app(app_id, {
                "type": "mouse_event",
                "client_id": client_id,
                "event_type": event_type,
                "x": x,
                "y": y,
                "button": button,
                "timestamp": datetime.utcnow().isoformat()
            }, exclude_client=client_id)
            
        except Exception as e:
            print(f"Error handling mouse event: {e}")
    
    async def handle_keyboard_event(self, client_id: str, data: Dict[str, Any]):
        """Handle keyboard event from client"""
        try:
            app_id = self.client_apps.get(client_id)
            if not app_id:
                return
            
            key = data.get("key")
            modifiers = data.get("modifiers", [])
            
            # Forward to window manager
            from .window_manager import WindowManager
            window_manager = WindowManager()
            
            # Get the main window for the app
            windows = await window_manager.get_application_windows(app_id)
            if windows:
                main_window = windows[0]  # Use first window
                await window_manager.send_keyboard_event(
                    main_window["id"], key, modifiers
                )
            
            # Broadcast to other clients in the same app session
            await self.broadcast_to_app(app_id, {
                "type": "keyboard_event",
                "client_id": client_id,
                "key": key,
                "modifiers": modifiers,
                "timestamp": datetime.utcnow().isoformat()
            }, exclude_client=client_id)
            
        except Exception as e:
            print(f"Error handling keyboard event: {e}")
    
    async def send_to_client(self, client_id: str, data: Dict[str, Any]):
        """Send data to a specific client"""
        try:
            # This would be implemented with the actual socket.io instance
            # For now, we'll just log it
            print(f"Sending to client {client_id}: {data}")
        except Exception as e:
            print(f"Error sending to client {client_id}: {e}")
    
    async def broadcast_to_app(self, app_id: str, data: Dict[str, Any], exclude_client: Optional[str] = None):
        """Broadcast data to all clients in an application session"""
        try:
            if app_id not in self.app_sessions:
                return
            
            for client_id in self.app_sessions[app_id]:
                if client_id != exclude_client:
                    await self.send_to_client(client_id, data)
                    
        except Exception as e:
            print(f"Error broadcasting to app {app_id}: {e}")
    
    async def broadcast_to_all(self, data: Dict[str, Any], exclude_client: Optional[str] = None):
        """Broadcast data to all connected clients"""
        try:
            for client_id in self.connected_clients:
                if client_id != exclude_client:
                    await self.send_to_client(client_id, data)
                    
        except Exception as e:
            print(f"Error broadcasting to all clients: {e}")
    
    async def send_app_update(self, app_id: str, update_type: str, data: Dict[str, Any]):
        """Send application update to all clients in the session"""
        await self.broadcast_to_app(app_id, {
            "type": "app_update",
            "update_type": update_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def send_window_update(self, app_id: str, window_data: Dict[str, Any]):
        """Send window update to all clients in the session"""
        await self.broadcast_to_app(app_id, {
            "type": "window_update",
            "window": window_data,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def send_screenshot_update(self, app_id: str, screenshot_data: str):
        """Send screenshot update to all clients in the session"""
        await self.broadcast_to_app(app_id, {
            "type": "screenshot_update",
            "screenshot": screenshot_data,
            "timestamp": datetime.utcnow().isoformat()
        })

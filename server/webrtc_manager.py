"""
WebRTC Manager for Application Share
Provides WebRTC-based real-time communication for better performance
"""

import asyncio
import json
import base64
import cv2
import numpy as np
from typing import Dict, List, Optional, Any, Set
import websockets
import aiortc
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.signaling import TcpSocketSignaling
import logging

logger = logging.getLogger(__name__)

class ScreenVideoTrack(VideoStreamTrack):
    """Custom video track for screen sharing"""
    
    def __init__(self, screen_capture_callback):
        super().__init__()
        self.screen_capture_callback = screen_capture_callback
        self.frame_count = 0
    
    async def recv(self):
        """Receive next video frame"""
        try:
            # Get screen capture
            frame_data = await self.screen_capture_callback()
            if not frame_data:
                return None
            
            # Convert base64 to OpenCV frame
            img_data = base64.b64decode(frame_data.split(',')[1])
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return None
            
            # Convert BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Create video frame
            pts = self.frame_count * 1000 // 30  # 30 FPS
            video_frame = aiortc.VideoFrame.from_ndarray(frame, format="rgb24")
            video_frame.pts = pts
            video_frame.time_base = aiortc.Rational(1, 1000)
            
            self.frame_count += 1
            return video_frame
            
        except Exception as e:
            logger.error(f"Error in video track: {e}")
            return None

class WebRTCManager:
    def __init__(self):
        self.peer_connections: Dict[str, RTCPeerConnection] = {}
        self.video_tracks: Dict[str, ScreenVideoTrack] = {}
        self.audio_tracks: Dict[str, Any] = {}
        self.signaling_server = None
        self.screen_capture_callback = None
        
    async def start_signaling_server(self, host: str = "0.0.0.0", port: int = 8767):
        """Start WebRTC signaling server"""
        try:
            self.signaling_server = TcpSocketSignaling(host, port)
            await self.signaling_server.start()
            logger.info(f"✅ WebRTC signaling server started on {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"Error starting signaling server: {e}")
            return False
    
    async def create_peer_connection(self, client_id: str) -> RTCPeerConnection:
        """Create a new WebRTC peer connection"""
        try:
            pc = RTCPeerConnection()
            self.peer_connections[client_id] = pc
            
            # Add video track
            if self.screen_capture_callback:
                video_track = ScreenVideoTrack(self.screen_capture_callback)
                self.video_tracks[client_id] = video_track
                pc.addTrack(video_track)
            
            # Handle connection state changes
            @pc.on("connectionstatechange")
            def on_connectionstatechange():
                logger.info(f"Connection state for {client_id}: {pc.connectionState}")
                if pc.connectionState == "closed":
                    self.cleanup_connection(client_id)
            
            # Handle ICE candidates
            @pc.on("icecandidate")
            def on_icecandidate(candidate):
                if candidate:
                    asyncio.create_task(self.send_ice_candidate(client_id, candidate))
            
            logger.info(f"✅ Peer connection created for {client_id}")
            return pc
            
        except Exception as e:
            logger.error(f"Error creating peer connection: {e}")
            return None
    
    async def handle_offer(self, client_id: str, offer_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle incoming WebRTC offer"""
        try:
            pc = await self.create_peer_connection(client_id)
            if not pc:
                return None
            
            # Create offer from data
            offer = RTCSessionDescription(
                sdp=offer_data["sdp"],
                type=offer_data["type"]
            )
            
            # Set remote description
            await pc.setRemoteDescription(offer)
            
            # Create answer
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            
            return {
                "type": "answer",
                "sdp": answer.sdp,
                "type": answer.type
            }
            
        except Exception as e:
            logger.error(f"Error handling offer: {e}")
            return None
    
    async def handle_ice_candidate(self, client_id: str, candidate_data: Dict[str, Any]):
        """Handle incoming ICE candidate"""
        try:
            if client_id not in self.peer_connections:
                return
            
            pc = self.peer_connections[client_id]
            candidate = aiortc.RTCIceCandidate(
                candidate=candidate_data["candidate"],
                sdpMid=candidate_data["sdpMid"],
                sdpMLineIndex=candidate_data["sdpMLineIndex"]
            )
            
            await pc.addIceCandidate(candidate)
            
        except Exception as e:
            logger.error(f"Error handling ICE candidate: {e}")
    
    async def send_ice_candidate(self, client_id: str, candidate: aiortc.RTCIceCandidate):
        """Send ICE candidate to client"""
        try:
            # This would typically send the candidate to the client via WebSocket
            # Implementation depends on your WebSocket setup
            pass
        except Exception as e:
            logger.error(f"Error sending ICE candidate: {e}")
    
    async def cleanup_connection(self, client_id: str):
        """Cleanup peer connection"""
        try:
            if client_id in self.peer_connections:
                pc = self.peer_connections[client_id]
                await pc.close()
                del self.peer_connections[client_id]
            
            if client_id in self.video_tracks:
                del self.video_tracks[client_id]
            
            if client_id in self.audio_tracks:
                del self.audio_tracks[client_id]
            
            logger.info(f"✅ Cleaned up connection for {client_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up connection: {e}")
    
    async def set_screen_capture_callback(self, callback):
        """Set the screen capture callback"""
        self.screen_capture_callback = callback
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebRTC connection statistics"""
        try:
            stats = {
                "active_connections": len(self.peer_connections),
                "video_tracks": len(self.video_tracks),
                "audio_tracks": len(self.audio_tracks)
            }
            
            # Get detailed stats for each connection
            for client_id, pc in self.peer_connections.items():
                try:
                    connection_stats = await pc.getStats()
                    stats[f"connection_{client_id}"] = {
                        "connection_state": pc.connectionState,
                        "ice_connection_state": pc.iceConnectionState,
                        "stats": connection_stats
                    }
                except Exception as e:
                    logger.error(f"Error getting stats for {client_id}: {e}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting connection stats: {e}")
            return {"active_connections": 0, "video_tracks": 0, "audio_tracks": 0}
    
    async def start_webrtc_server(self, port: int = 8767):
        """Start WebRTC server with WebSocket signaling"""
        async def handle_webrtc_client(websocket, path):
            client_id = f"client_{len(self.peer_connections)}"
            logger.info(f"WebRTC client connected: {client_id}")
            
            try:
                async for message in websocket:
                    data = json.loads(message)
                    
                    if data.get("type") == "offer":
                        answer = await self.handle_offer(client_id, data)
                        if answer:
                            await websocket.send(json.dumps(answer))
                    
                    elif data.get("type") == "ice_candidate":
                        await self.handle_ice_candidate(client_id, data)
                    
                    elif data.get("type") == "stats_request":
                        stats = await self.get_connection_stats()
                        await websocket.send(json.dumps({
                            "type": "stats",
                            "data": stats
                        }))
                        
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                await self.cleanup_connection(client_id)
                logger.info(f"WebRTC client disconnected: {client_id}")
        
        # Start WebRTC WebSocket server
        server = await websockets.serve(handle_webrtc_client, "0.0.0.0", port)
        logger.info(f"✅ WebRTC server started on port {port}")
        return server
    
    async def stop_webrtc_server(self):
        """Stop WebRTC server"""
        try:
            # Close all peer connections
            for client_id in list(self.peer_connections.keys()):
                await self.cleanup_connection(client_id)
            
            # Stop signaling server
            if self.signaling_server:
                await self.signaling_server.close()
            
            logger.info("🛑 WebRTC server stopped")
            
        except Exception as e:
            logger.error(f"Error stopping WebRTC server: {e}")

"""
Audio Manager for Application Share
Handles audio forwarding for VNC/RDP sessions
"""

import asyncio
import subprocess
import os
import json
import base64
import wave
import pyaudio
import threading
from typing import Dict, Optional, Any, List
import websockets

class AudioManager:
    def __init__(self):
        self.is_recording = False
        self.is_playing = False
        self.audio_clients: List[websockets.WebSocketServerProtocol] = []
        self.audio_format = pyaudio.paInt16
        self.channels = 2
        self.rate = 44100
        self.chunk = 1024
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.recording_thread = None
        
    async def start_audio_server(self, port: int = 8766):
        """Start audio WebSocket server"""
        async def handle_audio_client(websocket, path):
            self.audio_clients.append(websocket)
            print(f"Audio client connected: {websocket.remote_address}")
            
            try:
                # Send audio configuration
                await websocket.send(json.dumps({
                    "type": "audio_config",
                    "channels": self.channels,
                    "rate": self.rate,
                    "format": self.audio_format
                }))
                
                # Handle audio data
                async for message in websocket:
                    data = json.loads(message)
                    if data.get("type") == "audio_data":
                        await self.broadcast_audio(data["data"])
                    elif data.get("type") == "start_recording":
                        await self.start_recording()
                    elif data.get("type") == "stop_recording":
                        await self.stop_recording()
                        
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                self.audio_clients.remove(websocket)
                print(f"Audio client disconnected: {websocket.remote_address}")
        
        # Start WebSocket server
        server = await websockets.serve(handle_audio_client, "0.0.0.0", port)
        print(f"✅ Audio server started on port {port}")
        return server
    
    async def start_recording(self):
        """Start audio recording from system"""
        if self.is_recording:
            return
        
        try:
            self.is_recording = True
            self.stream = self.audio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            # Start recording thread
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recording_thread.start()
            
            print("🎤 Audio recording started")
            
        except Exception as e:
            print(f"Error starting audio recording: {e}")
            self.is_recording = False
    
    async def stop_recording(self):
        """Stop audio recording"""
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        if self.recording_thread:
            self.recording_thread.join()
        
        print("🛑 Audio recording stopped")
    
    def _record_audio(self):
        """Record audio in separate thread"""
        while self.is_recording and self.stream:
            try:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                # Convert to base64 for WebSocket transmission
                audio_data = base64.b64encode(data).decode('utf-8')
                
                # Send to all connected clients
                if self.audio_clients:
                    message = json.dumps({
                        "type": "audio_data",
                        "data": audio_data,
                        "timestamp": asyncio.get_event_loop().time()
                    })
                    
                    # Send to all clients (non-blocking)
                    for client in self.audio_clients.copy():
                        try:
                            asyncio.run_coroutine_threadsafe(
                                client.send(message), 
                                asyncio.get_event_loop()
                            )
                        except:
                            self.audio_clients.remove(client)
                            
            except Exception as e:
                print(f"Error recording audio: {e}")
                break
    
    async def broadcast_audio(self, audio_data: str):
        """Broadcast audio data to all clients"""
        if not self.audio_clients:
            return
        
        message = json.dumps({
            "type": "audio_data",
            "data": audio_data,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Send to all clients concurrently
        await asyncio.gather(
            *[client.send(message) for client in self.audio_clients],
            return_exceptions=True
        )
    
    async def play_audio(self, audio_data: str):
        """Play audio data"""
        try:
            # Decode base64 audio data
            audio_bytes = base64.b64decode(audio_data)
            
            # Create temporary WAV file
            temp_file = "/tmp/temp_audio.wav"
            with wave.open(temp_file, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(self.audio.get_sample_size(self.audio_format))
                wav_file.setframerate(self.rate)
                wav_file.writeframes(audio_bytes)
            
            # Play audio using system player
            subprocess.run(["aplay", temp_file], check=True)
            
            # Clean up
            os.remove(temp_file)
            
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    async def setup_pulseaudio(self):
        """Setup PulseAudio for audio forwarding"""
        try:
            # Install PulseAudio if not available
            subprocess.run([
                "apt-get", "update"
            ], check=True)
            
            subprocess.run([
                "apt-get", "install", "-y", "pulseaudio", "pulseaudio-utils"
            ], check=True)
            
            # Configure PulseAudio for VNC/RDP
            subprocess.run([
                "pulseaudio", "--start", "--exit-idle-time=-1"
            ], check=True)
            
            print("✅ PulseAudio configured for audio forwarding")
            
        except Exception as e:
            print(f"Error setting up PulseAudio: {e}")
    
    async def cleanup(self):
        """Cleanup audio resources"""
        await self.stop_recording()
        
        if self.audio:
            self.audio.terminate()
        
        print("🧹 Audio manager cleaned up")

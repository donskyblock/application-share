"""
Recording Manager for Application Share
Handles session recording and playback
"""

import asyncio
import os
import json
import time
import base64
import cv2
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime
import wave
import pyaudio

class SessionRecorder:
    def __init__(self, session_id: str, recording_dir: str = "recordings"):
        self.session_id = session_id
        self.recording_dir = recording_dir
        self.is_recording = False
        self.recording_data = []
        self.video_writer = None
        self.audio_writer = None
        self.start_time = None
        
        # Create recording directory
        os.makedirs(recording_dir, exist_ok=True)
        
    async def start_recording(self, width: int = 1920, height: int = 1080, fps: int = 30):
        """Start recording session"""
        try:
            if self.is_recording:
                return False
            
            self.is_recording = True
            self.start_time = time.time()
            self.recording_data = []
            
            # Setup video recording
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_path = os.path.join(self.recording_dir, f"{self.session_id}.mp4")
            self.video_writer = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
            
            # Setup audio recording
            audio_path = os.path.join(self.recording_dir, f"{self.session_id}.wav")
            self.audio_writer = wave.open(audio_path, 'wb')
            self.audio_writer.setnchannels(2)
            self.audio_writer.setsampwidth(2)
            self.audio_writer.setframerate(44100)
            
            print(f"✅ Started recording session {self.session_id}")
            return True
            
        except Exception as e:
            print(f"Error starting recording: {e}")
            return False
    
    async def stop_recording(self) -> Optional[str]:
        """Stop recording and return file path"""
        try:
            if not self.is_recording:
                return None
            
            self.is_recording = False
            
            # Close video writer
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            
            # Close audio writer
            if self.audio_writer:
                self.audio_writer.close()
                self.audio_writer = None
            
            # Save metadata
            metadata = {
                "session_id": self.session_id,
                "start_time": self.start_time,
                "end_time": time.time(),
                "duration": time.time() - self.start_time,
                "frames": len(self.recording_data),
                "created_at": datetime.now().isoformat()
            }
            
            metadata_path = os.path.join(self.recording_dir, f"{self.session_id}_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✅ Stopped recording session {self.session_id}")
            return os.path.join(self.recording_dir, f"{self.session_id}.mp4")
            
        except Exception as e:
            print(f"Error stopping recording: {e}")
            return None
    
    async def record_frame(self, frame_data: str, timestamp: float = None):
        """Record a video frame"""
        try:
            if not self.is_recording or not self.video_writer:
                return
            
            # Decode base64 frame
            img_data = base64.b64decode(frame_data.split(',')[1])
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is not None:
                self.video_writer.write(frame)
                
                # Store frame data for playback
                self.recording_data.append({
                    "timestamp": timestamp or time.time(),
                    "frame_data": frame_data,
                    "type": "video"
                })
                
        except Exception as e:
            print(f"Error recording frame: {e}")
    
    async def record_audio(self, audio_data: str, timestamp: float = None):
        """Record audio data"""
        try:
            if not self.is_recording or not self.audio_writer:
                return
            
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_data)
            self.audio_writer.writeframes(audio_bytes)
            
            # Store audio data for playback
            self.recording_data.append({
                "timestamp": timestamp or time.time(),
                "audio_data": audio_data,
                "type": "audio"
            })
            
        except Exception as e:
            print(f"Error recording audio: {e}")
    
    async def record_event(self, event_type: str, event_data: Dict[str, Any], timestamp: float = None):
        """Record an event (mouse, keyboard, etc.)"""
        try:
            if not self.is_recording:
                return
            
            self.recording_data.append({
                "timestamp": timestamp or time.time(),
                "event_type": event_type,
                "event_data": event_data,
                "type": "event"
            })
            
        except Exception as e:
            print(f"Error recording event: {e}")

class RecordingManager:
    def __init__(self):
        self.active_recordings: Dict[str, SessionRecorder] = {}
        self.recording_dir = os.getenv("RECORDING_DIR", "recordings")
        self.max_recordings = int(os.getenv("MAX_RECORDINGS", "100"))
        
        # Create recording directory
        os.makedirs(self.recording_dir, exist_ok=True)
    
    async def start_session_recording(self, session_id: str) -> bool:
        """Start recording a session"""
        try:
            if session_id in self.active_recordings:
                return False
            
            recorder = SessionRecorder(session_id, self.recording_dir)
            success = await recorder.start_recording()
            
            if success:
                self.active_recordings[session_id] = recorder
                return True
            
            return False
            
        except Exception as e:
            print(f"Error starting session recording: {e}")
            return False
    
    async def stop_session_recording(self, session_id: str) -> Optional[str]:
        """Stop recording a session"""
        try:
            if session_id not in self.active_recordings:
                return None
            
            recorder = self.active_recordings[session_id]
            file_path = await recorder.stop_recording()
            
            del self.active_recordings[session_id]
            return file_path
            
        except Exception as e:
            print(f"Error stopping session recording: {e}")
            return None
    
    async def record_session_frame(self, session_id: str, frame_data: str, timestamp: float = None):
        """Record a frame for a session"""
        try:
            if session_id in self.active_recordings:
                await self.active_recordings[session_id].record_frame(frame_data, timestamp)
        except Exception as e:
            print(f"Error recording session frame: {e}")
    
    async def record_session_audio(self, session_id: str, audio_data: str, timestamp: float = None):
        """Record audio for a session"""
        try:
            if session_id in self.active_recordings:
                await self.active_recordings[session_id].record_audio(audio_data, timestamp)
        except Exception as e:
            print(f"Error recording session audio: {e}")
    
    async def record_session_event(self, session_id: str, event_type: str, event_data: Dict[str, Any], timestamp: float = None):
        """Record an event for a session"""
        try:
            if session_id in self.active_recordings:
                await self.active_recordings[session_id].record_event(event_type, event_data, timestamp)
        except Exception as e:
            print(f"Error recording session event: {e}")
    
    async def list_recordings(self) -> List[Dict[str, Any]]:
        """List available recordings"""
        try:
            recordings = []
            
            for filename in os.listdir(self.recording_dir):
                if filename.endswith('_metadata.json'):
                    metadata_path = os.path.join(self.recording_dir, filename)
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    
                    recordings.append({
                        "session_id": metadata["session_id"],
                        "duration": metadata["duration"],
                        "created_at": metadata["created_at"],
                        "frames": metadata["frames"],
                        "file_path": os.path.join(self.recording_dir, f"{metadata['session_id']}.mp4")
                    })
            
            return sorted(recordings, key=lambda x: x["created_at"], reverse=True)
            
        except Exception as e:
            print(f"Error listing recordings: {e}")
            return []
    
    async def get_recording(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get recording information"""
        try:
            metadata_path = os.path.join(self.recording_dir, f"{session_id}_metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                metadata["file_path"] = os.path.join(self.recording_dir, f"{session_id}.mp4")
                return metadata
            
            return None
            
        except Exception as e:
            print(f"Error getting recording: {e}")
            return None
    
    async def delete_recording(self, session_id: str) -> bool:
        """Delete a recording"""
        try:
            # Delete video file
            video_path = os.path.join(self.recording_dir, f"{session_id}.mp4")
            if os.path.exists(video_path):
                os.remove(video_path)
            
            # Delete audio file
            audio_path = os.path.join(self.recording_dir, f"{session_id}.wav")
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            # Delete metadata file
            metadata_path = os.path.join(self.recording_dir, f"{session_id}_metadata.json")
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            return True
            
        except Exception as e:
            print(f"Error deleting recording: {e}")
            return False
    
    async def cleanup_old_recordings(self):
        """Clean up old recordings to stay within limits"""
        try:
            recordings = await self.list_recordings()
            
            if len(recordings) > self.max_recordings:
                # Delete oldest recordings
                recordings_to_delete = recordings[self.max_recordings:]
                for recording in recordings_to_delete:
                    await self.delete_recording(recording["session_id"])
                    print(f"🧹 Deleted old recording: {recording['session_id']}")
                    
        except Exception as e:
            print(f"Error cleaning up recordings: {e}")
    
    async def cleanup(self):
        """Cleanup recording manager"""
        try:
            # Stop all active recordings
            for session_id in list(self.active_recordings.keys()):
                await self.stop_session_recording(session_id)
            
            print("🧹 Recording manager cleaned up")
            
        except Exception as e:
            print(f"Error cleaning up recording manager: {e}")

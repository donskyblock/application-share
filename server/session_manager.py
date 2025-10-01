"""
Session Manager for Application Share
Handles multi-user session management and collaboration
"""

import asyncio
import os
import time
import json
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
import uuid

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
        self.session_participants: Dict[str, Set[str]] = {}  # session_id -> set of user_ids
        self.session_timeout = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 1 hour default
        
    async def create_session(self, owner_id: str, session_name: str = None) -> Dict[str, Any]:
        """Create a new collaborative session"""
        try:
            session_id = str(uuid.uuid4())
            session_name = session_name or f"Session {session_id[:8]}"
            
            session = {
                "id": session_id,
                "name": session_name,
                "owner_id": owner_id,
                "created_at": time.time(),
                "last_activity": time.time(),
                "status": "active",
                "participants": {owner_id},
                "applications": {},
                "settings": {
                    "allow_guests": True,
                    "max_participants": 10,
                    "recording_enabled": False,
                    "chat_enabled": True
                }
            }
            
            self.sessions[session_id] = session
            self.user_sessions[owner_id] = session_id
            self.session_participants[session_id] = {owner_id}
            
            print(f"✅ Session created: {session_id} by {owner_id}")
            return session
            
        except Exception as e:
            print(f"Error creating session: {e}")
            return None
    
    async def join_session(self, session_id: str, user_id: str) -> bool:
        """Join an existing session"""
        try:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            
            # Check if session is active
            if session["status"] != "active":
                return False
            
            # Check participant limit
            if len(session["participants"]) >= session["settings"]["max_participants"]:
                return False
            
            # Add user to session
            session["participants"].add(user_id)
            self.user_sessions[user_id] = session_id
            self.session_participants[session_id].add(user_id)
            session["last_activity"] = time.time()
            
            print(f"✅ User {user_id} joined session {session_id}")
            return True
            
        except Exception as e:
            print(f"Error joining session: {e}")
            return False
    
    async def leave_session(self, user_id: str) -> bool:
        """Leave current session"""
        try:
            if user_id not in self.user_sessions:
                return False
            
            session_id = self.user_sessions[user_id]
            session = self.sessions[session_id]
            
            # Remove user from session
            session["participants"].discard(user_id)
            self.session_participants[session_id].discard(user_id)
            del self.user_sessions[user_id]
            session["last_activity"] = time.time()
            
            # If owner leaves, transfer ownership or close session
            if session["owner_id"] == user_id:
                if session["participants"]:
                    # Transfer ownership to first participant
                    new_owner = next(iter(session["participants"]))
                    session["owner_id"] = new_owner
                    print(f"✅ Ownership transferred to {new_owner}")
                else:
                    # Close session if no participants left
                    await self.close_session(session_id)
            
            print(f"✅ User {user_id} left session {session_id}")
            return True
            
        except Exception as e:
            print(f"Error leaving session: {e}")
            return False
    
    async def close_session(self, session_id: str) -> bool:
        """Close a session"""
        try:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            session["status"] = "closed"
            session["closed_at"] = time.time()
            
            # Remove all participants
            for user_id in session["participants"]:
                if user_id in self.user_sessions:
                    del self.user_sessions[user_id]
            
            self.session_participants[session_id] = set()
            
            print(f"✅ Session {session_id} closed")
            return True
            
        except Exception as e:
            print(f"Error closing session: {e}")
            return False
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        return self.sessions.get(session_id)
    
    async def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's current session"""
        if user_id not in self.user_sessions:
            return None
        
        session_id = self.user_sessions[user_id]
        return self.sessions.get(session_id)
    
    async def list_sessions(self, user_id: str = None) -> List[Dict[str, Any]]:
        """List available sessions"""
        try:
            sessions = []
            for session in self.sessions.values():
                if session["status"] == "active":
                    # Check if user can join
                    can_join = (
                        user_id in session["participants"] or
                        session["settings"]["allow_guests"]
                    )
                    
                    sessions.append({
                        "id": session["id"],
                        "name": session["name"],
                        "owner_id": session["owner_id"],
                        "participant_count": len(session["participants"]),
                        "max_participants": session["settings"]["max_participants"],
                        "created_at": session["created_at"],
                        "can_join": can_join
                    })
            
            return sessions
            
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []
    
    async def update_session_settings(self, session_id: str, user_id: str, settings: Dict[str, Any]) -> bool:
        """Update session settings (owner only)"""
        try:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            if session["owner_id"] != user_id:
                return False
            
            # Update settings
            session["settings"].update(settings)
            session["last_activity"] = time.time()
            
            print(f"✅ Session {session_id} settings updated by {user_id}")
            return True
            
        except Exception as e:
            print(f"Error updating session settings: {e}")
            return False
    
    async def add_application_to_session(self, session_id: str, app_id: str, user_id: str) -> bool:
        """Add application to session"""
        try:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            if user_id not in session["participants"]:
                return False
            
            session["applications"][app_id] = {
                "added_by": user_id,
                "added_at": time.time(),
                "shared": True
            }
            session["last_activity"] = time.time()
            
            print(f"✅ Application {app_id} added to session {session_id}")
            return True
            
        except Exception as e:
            print(f"Error adding application to session: {e}")
            return False
    
    async def remove_application_from_session(self, session_id: str, app_id: str, user_id: str) -> bool:
        """Remove application from session"""
        try:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            if user_id not in session["participants"]:
                return False
            
            if app_id in session["applications"]:
                del session["applications"][app_id]
                session["last_activity"] = time.time()
                
                print(f"✅ Application {app_id} removed from session {session_id}")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error removing application from session: {e}")
            return False
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            current_time = time.time()
            expired_sessions = []
            
            for session_id, session in self.sessions.items():
                if (current_time - session["last_activity"]) > self.session_timeout:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                await self.close_session(session_id)
                print(f"🧹 Cleaned up expired session: {session_id}")
                
        except Exception as e:
            print(f"Error cleaning up sessions: {e}")
    
    async def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        try:
            active_sessions = sum(1 for s in self.sessions.values() if s["status"] == "active")
            total_participants = sum(len(s["participants"]) for s in self.sessions.values() if s["status"] == "active")
            
            return {
                "active_sessions": active_sessions,
                "total_participants": total_participants,
                "total_sessions": len(self.sessions)
            }
            
        except Exception as e:
            print(f"Error getting session stats: {e}")
            return {
                "active_sessions": 0,
                "total_participants": 0,
                "total_sessions": 0
            }

"""
Authentication manager for Application Share
Handles user authentication, JWT tokens, and user management
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import json

class AuthManager:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.getenv("JWT_SECRET", "your-secret-key-here")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        
        # In-memory user storage (replace with database in production)
        self.users_file = "data/users.json"
        self.users = self._load_users()
    
    def _load_users(self) -> Dict[str, Dict[str, Any]]:
        """Load users from file"""
        try:
            os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading users: {e}")
        return {}
    
    def _save_users(self):
        """Save users to file"""
        try:
            os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def _get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    async def create_admin_user(self, username: str, password: str) -> Dict[str, Any]:
        """Create the admin user (only one allowed)"""
        if self.users:
            # Admin user already exists
            return None
        
        user_id = "admin"
        user = {
            "id": user_id,
            "username": username,
            "hashed_password": self._get_password_hash(password),
            "created_at": datetime.utcnow().isoformat(),
            "is_active": True,
            "is_admin": True
        }
        
        self.users[username] = user
        self._save_users()
        
        return {
            "id": user["id"],
            "username": user["username"],
            "created_at": user["created_at"],
            "is_admin": True
        }
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user"""
        user = self.users.get(username)
        if not user or not self._verify_password(password, user["hashed_password"]):
            return None
        
        if not user.get("is_active", True):
            return None
        
        return {
            "id": user["id"],
            "username": user["username"],
            "created_at": user["created_at"],
            "is_admin": user.get("is_admin", False)
        }
    
    async def create_access_token(self, user: Dict[str, Any]) -> str:
        """Create a JWT access token"""
        to_encode = {
            "sub": user["id"],
            "username": user["username"],
            "exp": datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        }
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify a JWT token and return user info"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get("sub")
            username = payload.get("username")
            
            if user_id is None or username is None:
                return None
            
            # Find user by ID
            for user in self.users.values():
                if user["id"] == user_id and user["username"] == username:
                    return {
                        "id": user["id"],
                        "username": user["username"],
                        "created_at": user["created_at"],
                        "is_admin": user.get("is_admin", False)
                    }
            
            return None
        except JWTError:
            return None

"""
File Manager for Application Share
Handles file transfer between client and server
"""

import os
import asyncio
import aiofiles
import hashlib
import mimetypes
from typing import Dict, List, Optional, Any
from pathlib import Path
import zipfile
import tempfile
import shutil

class FileManager:
    def __init__(self):
        self.upload_dir = os.getenv("UPLOAD_DIR", "/tmp/appshare/uploads")
        self.download_dir = os.getenv("DOWNLOAD_DIR", "/tmp/appshare/downloads")
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", "100")) * 1024 * 1024  # 100MB default
        self.allowed_extensions = os.getenv("ALLOWED_EXTENSIONS", 
            "txt,pdf,doc,docx,xls,xlsx,ppt,pptx,jpg,jpeg,png,gif,mp4,mp3,zip,tar,gz").split(",")
        
        # Create directories
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.download_dir, exist_ok=True)
    
    async def upload_file(self, filename: str, file_data: bytes, user_id: str) -> Dict[str, Any]:
        """Upload a file to the server"""
        try:
            # Validate file size
            if len(file_data) > self.max_file_size:
                raise ValueError(f"File too large. Maximum size: {self.max_file_size / (1024*1024):.1f}MB")
            
            # Validate file extension
            file_ext = Path(filename).suffix.lower().lstrip('.')
            if file_ext not in self.allowed_extensions:
                raise ValueError(f"File type not allowed. Allowed: {', '.join(self.allowed_extensions)}")
            
            # Create user-specific directory
            user_dir = os.path.join(self.upload_dir, user_id)
            os.makedirs(user_dir, exist_ok=True)
            
            # Generate unique filename
            file_hash = hashlib.md5(file_data).hexdigest()
            safe_filename = f"{file_hash}_{filename}"
            file_path = os.path.join(user_dir, safe_filename)
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_data)
            
            # Get file info
            file_info = await self.get_file_info(file_path)
            file_info.update({
                "original_name": filename,
                "user_id": user_id,
                "uploaded_at": asyncio.get_event_loop().time()
            })
            
            return {
                "success": True,
                "file_id": file_hash,
                "filename": safe_filename,
                "path": file_path,
                "info": file_info
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def download_file(self, file_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Download a file from the server"""
        try:
            # Find file in user directory
            user_dir = os.path.join(self.upload_dir, user_id)
            if not os.path.exists(user_dir):
                return None
            
            # Look for file with matching hash
            for filename in os.listdir(user_dir):
                if filename.startswith(file_id):
                    file_path = os.path.join(user_dir, filename)
                    
                    # Read file
                    async with aiofiles.open(file_path, 'rb') as f:
                        file_data = await f.read()
                    
                    # Get file info
                    file_info = await self.get_file_info(file_path)
                    
                    return {
                        "success": True,
                        "filename": filename,
                        "data": file_data,
                        "info": file_info
                    }
            
            return None
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_files(self, user_id: str) -> List[Dict[str, Any]]:
        """List files for a user"""
        try:
            user_dir = os.path.join(self.upload_dir, user_id)
            if not os.path.exists(user_dir):
                return []
            
            files = []
            for filename in os.listdir(user_dir):
                file_path = os.path.join(user_dir, filename)
                if os.path.isfile(file_path):
                    file_info = await self.get_file_info(file_path)
                    files.append({
                        "filename": filename,
                        "file_id": filename.split('_')[0],
                        "info": file_info
                    })
            
            return files
            
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    async def delete_file(self, file_id: str, user_id: str) -> bool:
        """Delete a file"""
        try:
            user_dir = os.path.join(self.upload_dir, user_id)
            if not os.path.exists(user_dir):
                return False
            
            # Find and delete file
            for filename in os.listdir(user_dir):
                if filename.startswith(file_id):
                    file_path = os.path.join(user_dir, filename)
                    os.remove(file_path)
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    async def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information"""
        try:
            stat = os.stat(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            
            return {
                "size": stat.st_size,
                "mime_type": mime_type or "application/octet-stream",
                "modified": stat.st_mtime,
                "created": stat.st_ctime
            }
            
        except Exception as e:
            return {
                "size": 0,
                "mime_type": "application/octet-stream",
                "modified": 0,
                "created": 0
            }
    
    async def create_zip_archive(self, file_ids: List[str], user_id: str) -> Optional[str]:
        """Create a ZIP archive of multiple files"""
        try:
            user_dir = os.path.join(self.upload_dir, user_id)
            if not os.path.exists(user_dir):
                return None
            
            # Create temporary ZIP file
            zip_path = os.path.join(self.download_dir, f"{user_id}_archive.zip")
            
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                for file_id in file_ids:
                    for filename in os.listdir(user_dir):
                        if filename.startswith(file_id):
                            file_path = os.path.join(user_dir, filename)
                            zip_file.write(file_path, filename)
                            break
            
            return zip_path
            
        except Exception as e:
            print(f"Error creating ZIP archive: {e}")
            return None
    
    async def sync_clipboard(self, clipboard_data: str, user_id: str) -> bool:
        """Sync clipboard data"""
        try:
            # Save clipboard data to file
            clipboard_file = os.path.join(self.upload_dir, f"{user_id}_clipboard.txt")
            async with aiofiles.open(clipboard_file, 'w') as f:
                await f.write(clipboard_data)
            
            return True
            
        except Exception as e:
            print(f"Error syncing clipboard: {e}")
            return False
    
    async def get_clipboard(self, user_id: str) -> Optional[str]:
        """Get clipboard data"""
        try:
            clipboard_file = os.path.join(self.upload_dir, f"{user_id}_clipboard.txt")
            if os.path.exists(clipboard_file):
                async with aiofiles.open(clipboard_file, 'r') as f:
                    return await f.read()
            return None
            
        except Exception as e:
            print(f"Error getting clipboard: {e}")
            return None

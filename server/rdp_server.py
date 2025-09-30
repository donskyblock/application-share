"""
RDP Server Integration for Application Share
Provides RDP server management using xrdp
"""

import asyncio
import subprocess
import os
import json
import time
from typing import Dict, Optional, Any

class RDPServer:
    def __init__(self):
        self.rdp_process = None
        self.rdp_port = int(os.getenv("RDP_PORT", "3389"))
        self.rdp_password = os.getenv("RDP_PASSWORD", "")
        self.display = os.getenv("DISPLAY", ":99")
        self.is_running = False
        
    async def start_rdp_server(self) -> bool:
        """Start RDP server using xrdp"""
        try:
            if self.is_running:
                return True
                
            # Install xrdp if not available
            await self._install_xrdp()
            
            # Configure xrdp
            await self._configure_xrdp()
            
            # Start xrdp service
            subprocess.run(["systemctl", "start", "xrdp"], check=True)
            subprocess.run(["systemctl", "enable", "xrdp"], check=True)
            
            self.is_running = True
            print(f"✅ RDP server started on port {self.rdp_port}")
            return True
            
        except Exception as e:
            print(f"❌ Error starting RDP server: {e}")
            return False
    
    async def stop_rdp_server(self):
        """Stop RDP server"""
        try:
            subprocess.run(["systemctl", "stop", "xrdp"], check=True)
            self.is_running = False
            print("🛑 RDP server stopped")
        except Exception as e:
            print(f"Error stopping RDP server: {e}")
    
    async def _install_xrdp(self):
        """Install xrdp package"""
        try:
            subprocess.run([
                "apt-get", "update"
            ], check=True)
            
            subprocess.run([
                "apt-get", "install", "-y", "xrdp"
            ], check=True)
        except subprocess.CalledProcessError:
            print("xrdp installation failed or already installed")
    
    async def _configure_xrdp(self):
        """Configure xrdp for the display"""
        try:
            # Create xrdp configuration
            config = f"""
[globals]
bitmap_cache=true
bitmap_compression=true
port={self.rdp_port}
crypt_level=low
channel_code=1
max_bpp=24
new_cursors=true
use_fastpath=both

[xrdp1]
name=Application Share
lib=libvnc.so
username=ask
password=ask
ip=127.0.0.1
port=5900
"""
            
            with open("/etc/xrdp/xrdp.ini", "w") as f:
                f.write(config)
                
            # Set up VNC for RDP
            subprocess.run([
                "x11vnc", "-display", self.display, "-nopw", "-forever", "-shared",
                "-rfbport", "5900", "-bg"
            ], check=True)
            
        except Exception as e:
            print(f"Error configuring xrdp: {e}")
    
    async def get_rdp_info(self) -> Dict[str, Any]:
        """Get RDP server information"""
        return {
            "running": self.is_running,
            "port": self.rdp_port,
            "display": self.display,
            "password_required": bool(self.rdp_password)
        }

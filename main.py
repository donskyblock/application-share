"""
Application Share - Main FastAPI Application
A web-based platform for running GUI applications on a server and displaying them in a browser.
"""

import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import socketio
from dotenv import load_dotenv

from server.auth import AuthManager
from server.app_manager import ApplicationManager
from server.window_manager import WindowManager
from server.websocket_handler import WebSocketHandler
from server.vnc_server import VNCServer
from server.live_streamer import LiveStreamer
from server.rdp_server import RDPServer
from server.audio_manager import AudioManager
from server.file_manager import FileManager
from server.session_manager import SessionManager
from server.app_templates import AppTemplateManager
from server.webrtc_manager import WebRTCManager
from server.clipboard_manager import ClipboardManager
from server.recording_manager import RecordingManager
from server.advanced_window_manager import AdvancedWindowManager
from server.app_marketplace import AppMarketplace
from server.custom_launchers import CustomLauncherManager

# Load environment variables
load_dotenv()

# Initialize managers
auth_manager = AuthManager()
app_manager = ApplicationManager()
window_manager = WindowManager()
websocket_handler = WebSocketHandler()
vnc_server = VNCServer()
live_streamer = LiveStreamer()
rdp_server = RDPServer()
audio_manager = AudioManager()
file_manager = FileManager()
session_manager = SessionManager()
app_template_manager = AppTemplateManager()
webrtc_manager = WebRTCManager()
clipboard_manager = ClipboardManager()
recording_manager = RecordingManager()
advanced_window_manager = AdvancedWindowManager()
app_marketplace = AppMarketplace()
custom_launcher_manager = CustomLauncherManager()

# Socket.IO server
sio = socketio.AsyncServer(
    cors_allowed_origins="*",
    async_mode='asgi'
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting Application Share Server...")
    
    # Initialize admin user if needed
    await initialize_admin_user()
    
    await app_manager.initialize()
    await window_manager.initialize()
    
    # Start VNC server if enabled
    if os.getenv("ENABLE_VNC", "false").lower() == "true":
        await vnc_server.start_vnc_server()
    
    # Start RDP server if enabled
    if os.getenv("ENABLE_RDP", "false").lower() == "true":
        await rdp_server.start_rdp_server()
    
    # Start live streaming
    await live_streamer.start_streaming()
    asyncio.create_task(live_streamer.capture_and_stream())
    
    print("✅ Server initialized successfully")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Application Share Server...")
    await app_manager.cleanup()
    await window_manager.cleanup()
    await vnc_server.stop_vnc_server()
    await rdp_server.stop_rdp_server()
    await live_streamer.stop_streaming()
    print("✅ Server shutdown complete")

async def initialize_admin_user():
    """Initialize admin user if none exists"""
    try:
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD")
        
        if admin_password:
            # Check if any users exist
            if not auth_manager.users:
                print(f"🔐 Creating admin user: {admin_username}")
                user = await auth_manager.create_admin_user(admin_username, admin_password)
                if user:
                    print("✅ Admin user created successfully")
                else:
                    print("⚠️  Admin user already exists")
            else:
                print("✅ Admin user already exists")
        else:
            print("⚠️  No admin password set in environment variables")
            print("   Set ADMIN_PASSWORD in .env file or initialize manually via web interface")
    except Exception as e:
        print(f"❌ Error initializing admin user: {e}")

# Create FastAPI app
app = FastAPI(
    title="Application Share",
    description="A platform for running GUI applications on a server and displaying them in a browser",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Mount static files
app.mount("/static", StaticFiles(directory="client/build/static"), name="static")

# Socket.IO integration
socket_app = socketio.ASGIApp(sio, app)
app.mount("/socket.io", socket_app)

# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    token = credentials.credentials
    user = await auth_manager.verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# API Routes
@app.get("/")
async def root():
    """Root endpoint - serve the main application"""
    return {"message": "Application Share API", "status": "running"}

@app.post("/api/auth/login")
async def login(credentials: dict):
    """User login endpoint"""
    username = credentials.get("username")
    password = credentials.get("password")
    
    user = await auth_manager.authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    token = await auth_manager.create_access_token(user)
    return {"access_token": token, "token_type": "bearer", "user": user}

@app.post("/api/auth/init-admin")
async def init_admin(admin_data: dict):
    """Initialize admin user (only works if no users exist)"""
    username = admin_data.get("username", "admin")
    password = admin_data.get("password")
    
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required"
        )
    
    user = await auth_manager.create_admin_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin user already exists"
        )
    
    token = await auth_manager.create_access_token(user)
    return {"access_token": token, "token_type": "bearer", "user": user}

@app.get("/api/applications")
async def get_applications(current_user: dict = Depends(get_current_user)):
    """Get list of available applications"""
    return await app_manager.get_available_applications()

@app.post("/api/applications/{app_name}/start")
async def start_application(app_name: str, current_user: dict = Depends(get_current_user)):
    """Start a GUI application"""
    try:
        app_instance = await app_manager.start_application(app_name, current_user["id"])
        return {
            "app_id": app_instance["id"],
            "status": "started",
            "message": f"Application {app_name} started successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start application: {str(e)}"
        )

@app.post("/api/applications/{app_id}/stop")
async def stop_application(app_id: str, current_user: dict = Depends(get_current_user)):
    """Stop a running application"""
    try:
        await app_manager.stop_application(app_id, current_user["id"])
        return {"status": "stopped", "message": f"Application {app_id} stopped successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop application: {str(e)}"
        )

@app.get("/api/applications/{app_id}/windows")
async def get_application_windows(app_id: str, current_user: dict = Depends(get_current_user)):
    """Get windows for a running application"""
    try:
        windows = await window_manager.get_application_windows(app_id)
        return {"windows": windows}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get windows: {str(e)}"
        )

@app.get("/api/applications/{app_id}/screenshot")
async def get_application_screenshot(app_id: str, current_user: dict = Depends(get_current_user)):
    """Get screenshot of application window"""
    try:
        screenshot_data = await window_manager.capture_screenshot(app_id)
        return {"screenshot": screenshot_data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to capture screenshot: {str(e)}"
        )

@app.get("/api/vnc/info")
async def get_vnc_info(current_user: dict = Depends(get_current_user)):
    """Get VNC server information"""
    try:
        vnc_info = await vnc_server.get_vnc_info()
        return vnc_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get VNC info: {str(e)}"
        )

@app.post("/api/vnc/start")
async def start_vnc_server(current_user: dict = Depends(get_current_user)):
    """Start VNC server"""
    try:
        success = await vnc_server.start_vnc_server()
        if success:
            return {"status": "started", "message": "VNC server started successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to start VNC server"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start VNC server: {str(e)}"
        )

@app.post("/api/vnc/stop")
async def stop_vnc_server(current_user: dict = Depends(get_current_user)):
    """Stop VNC server"""
    try:
        await vnc_server.stop_vnc_server()
        return {"status": "stopped", "message": "VNC server stopped successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop VNC server: {str(e)}"
        )

@app.get("/api/stream/info")
async def get_stream_info(current_user: dict = Depends(get_current_user)):
    """Get live streaming information"""
    try:
        return {
            "streaming": live_streamer.is_streaming,
            "clients": len(live_streamer.clients),
            "frame_rate": live_streamer.frame_rate,
            "quality": live_streamer.quality
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stream info: {str(e)}"
        )

@app.get("/api/rdp/info")
async def get_rdp_info(current_user: dict = Depends(get_current_user)):
    """Get RDP server information"""
    try:
        rdp_info = await rdp_server.get_rdp_info()
        return rdp_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get RDP info: {str(e)}"
        )

@app.post("/api/rdp/start")
async def start_rdp_server(current_user: dict = Depends(get_current_user)):
    """Start RDP server"""
    try:
        success = await rdp_server.start_rdp_server()
        if success:
            return {"status": "started", "message": "RDP server started successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to start RDP server"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start RDP server: {str(e)}"
        )

@app.post("/api/rdp/stop")
async def stop_rdp_server(current_user: dict = Depends(get_current_user)):
    """Stop RDP server"""
    try:
        await rdp_server.stop_rdp_server()
        return {"status": "stopped", "message": "RDP server stopped successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop RDP server: {str(e)}"
        )

# Socket.IO events
@sio.event
async def connect(sid, environ, auth):
    """Handle client connection"""
    print(f"Client {sid} connected")
    await websocket_handler.handle_connect(sid)

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    print(f"Client {sid} disconnected")
    await websocket_handler.handle_disconnect(sid)

@sio.event
async def join_application(sid, data):
    """Client joins an application session"""
    app_id = data.get("app_id")
    await websocket_handler.join_application(sid, app_id)

@sio.event
async def mouse_event(sid, data):
    """Handle mouse events from client"""
    await websocket_handler.handle_mouse_event(sid, data)
    # Also forward to live streamer
    await live_streamer.handle_input(websocket_handler.socket, data)

@sio.event
async def keyboard_event(sid, data):
    """Handle keyboard events from client"""
    await websocket_handler.handle_keyboard_event(sid, data)
    # Also forward to live streamer
    await live_streamer.handle_input(websocket_handler.socket, data)

@sio.event
async def scroll_event(sid, data):
    """Handle scroll events from client"""
    await live_streamer.handle_input(websocket_handler.socket, data)

@sio.event
async def join_live_stream(sid, data):
    """Client joins live stream"""
    await websocket_handler.join_application(sid, "live_stream")

@sio.event
async def leave_live_stream(sid, data):
    """Client leaves live stream"""
    await websocket_handler.leave_application(sid)

# Audio Management Endpoints
@app.get("/api/audio/info")
async def get_audio_info(current_user: dict = Depends(get_current_user)):
    """Get audio server information"""
    try:
        return {
            "enabled": True,
            "clients": len(audio_manager.audio_clients),
            "recording": audio_manager.is_recording
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audio info: {str(e)}"
        )

@app.post("/api/audio/start")
async def start_audio(current_user: dict = Depends(get_current_user)):
    """Start audio recording"""
    try:
        await audio_manager.start_recording()
        return {"success": True, "message": "Audio recording started"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start audio recording: {str(e)}"
        )

@app.post("/api/audio/stop")
async def stop_audio(current_user: dict = Depends(get_current_user)):
    """Stop audio recording"""
    try:
        await audio_manager.stop_recording()
        return {"success": True, "message": "Audio recording stopped"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop audio recording: {str(e)}"
        )

# File Management Endpoints
@app.post("/api/files/upload")
async def upload_file(file: UploadFile, current_user: dict = Depends(get_current_user)):
    """Upload a file"""
    try:
        file_data = await file.read()
        result = await file_manager.upload_file(file.filename, file_data, current_user["username"])
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

@app.get("/api/files/{file_id}")
async def download_file(file_id: str, current_user: dict = Depends(get_current_user)):
    """Download a file"""
    try:
        result = await file_manager.download_file(file_id, current_user["username"])
        if result and result.get("success"):
            return Response(
                content=result["data"],
                media_type="application/octet-stream",
                headers={"Content-Disposition": f"attachment; filename={result['filename']}"}
            )
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download file: {str(e)}"
        )

@app.get("/api/files")
async def list_files(current_user: dict = Depends(get_current_user)):
    """List user files"""
    try:
        files = await file_manager.list_files(current_user["username"])
        return {"files": files}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}"
        )

@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a file"""
    try:
        success = await file_manager.delete_file(file_id, current_user["username"])
        return {"success": success}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )

# Session Management Endpoints
@app.post("/api/sessions")
async def create_session(session_data: dict, current_user: dict = Depends(get_current_user)):
    """Create a new session"""
    try:
        session = await session_manager.create_session(
            current_user["username"],
            session_data.get("name")
        )
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )

@app.get("/api/sessions")
async def list_sessions(current_user: dict = Depends(get_current_user)):
    """List available sessions"""
    try:
        sessions = await session_manager.list_sessions(current_user["username"])
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}"
        )

@app.post("/api/sessions/{session_id}/join")
async def join_session(session_id: str, current_user: dict = Depends(get_current_user)):
    """Join a session"""
    try:
        success = await session_manager.join_session(session_id, current_user["username"])
        return {"success": success}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to join session: {str(e)}"
        )

@app.post("/api/sessions/{session_id}/leave")
async def leave_session(session_id: str, current_user: dict = Depends(get_current_user)):
    """Leave a session"""
    try:
        success = await session_manager.leave_session(current_user["username"])
        return {"success": success}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to leave session: {str(e)}"
        )

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str, current_user: dict = Depends(get_current_user)):
    """Get session information"""
    try:
        session = await session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session: {str(e)}"
        )

# Application Templates Endpoints
@app.get("/api/templates")
async def list_templates(category: str = None, current_user: dict = Depends(get_current_user)):
    """List application templates"""
    try:
        templates = app_template_manager.list_templates(category)
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list templates: {str(e)}"
        )

@app.get("/api/templates/{template_id}")
async def get_template(template_id: str, current_user: dict = Depends(get_current_user)):
    """Get template information"""
    try:
        template = app_template_manager.load_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template: {str(e)}"
        )

@app.post("/api/templates/{template_id}/launch")
async def launch_template(template_id: str, current_user: dict = Depends(get_current_user)):
    """Launch applications from template"""
    try:
        template = app_template_manager.load_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        launched_apps = []
        for app_config in template.get("applications", []):
            result = await app_manager.start_application(
                app_config["name"],
                app_config.get("args", []),
                app_config.get("env", {})
            )
            if result:
                launched_apps.append(app_config["name"])
        
        return {"success": True, "launched_apps": launched_apps}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to launch template: {str(e)}"
        )

# WebRTC Endpoints
@app.get("/api/webrtc/info")
async def get_webrtc_info(current_user: dict = Depends(get_current_user)):
    """Get WebRTC server information"""
    try:
        stats = await webrtc_manager.get_connection_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get WebRTC info: {str(e)}"
        )

# Clipboard Endpoints
@app.get("/api/clipboard")
async def get_clipboard(current_user: dict = Depends(get_current_user)):
    """Get clipboard data"""
    try:
        data = await clipboard_manager.get_clipboard(current_user["username"])
        return {"data": data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get clipboard: {str(e)}"
        )

@app.post("/api/clipboard")
async def set_clipboard(clipboard_data: dict, current_user: dict = Depends(get_current_user)):
    """Set clipboard data"""
    try:
        success = await clipboard_manager.sync_clipboard(clipboard_data.get("data", ""), current_user["username"])
        return {"success": success}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set clipboard: {str(e)}"
        )

# Recording Endpoints
@app.post("/api/recordings/{session_id}/start")
async def start_recording(session_id: str, current_user: dict = Depends(get_current_user)):
    """Start session recording"""
    try:
        success = await recording_manager.start_session_recording(session_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start recording: {str(e)}"
        )

@app.post("/api/recordings/{session_id}/stop")
async def stop_recording(session_id: str, current_user: dict = Depends(get_current_user)):
    """Stop session recording"""
    try:
        file_path = await recording_manager.stop_session_recording(session_id)
        return {"success": file_path is not None, "file_path": file_path}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop recording: {str(e)}"
        )

@app.get("/api/recordings")
async def list_recordings(current_user: dict = Depends(get_current_user)):
    """List available recordings"""
    try:
        recordings = await recording_manager.list_recordings()
        return {"recordings": recordings}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list recordings: {str(e)}"
        )

@app.get("/api/recordings/{session_id}")
async def get_recording(session_id: str, current_user: dict = Depends(get_current_user)):
    """Get recording information"""
    try:
        recording = await recording_manager.get_recording(session_id)
        if not recording:
            raise HTTPException(status_code=404, detail="Recording not found")
        return recording
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recording: {str(e)}"
        )

# Advanced Window Management Endpoints
@app.get("/api/windows/info")
async def get_window_info(current_user: dict = Depends(get_current_user)):
    """Get window manager information"""
    try:
        info = await advanced_window_manager.get_window_manager_info()
        return info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get window info: {str(e)}"
        )

@app.post("/api/windows/tile")
async def tile_windows(layout: str = "tiled", current_user: dict = Depends(get_current_user)):
    """Tile all windows"""
    try:
        success = await advanced_window_manager.tile_windows(layout)
        return {"success": success}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to tile windows: {str(e)}"
        )

@app.post("/api/windows/{window_id}/snap")
async def snap_window(window_id: str, snap_zone: str, current_user: dict = Depends(get_current_user)):
    """Snap window to zone"""
    try:
        success = await advanced_window_manager.snap_window(window_id, snap_zone)
        return {"success": success}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to snap window: {str(e)}"
        )

@app.get("/api/windows")
async def list_windows(current_user: dict = Depends(get_current_user)):
    """List all windows"""
    try:
        windows = await advanced_window_manager.get_all_windows()
        return {"windows": windows}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list windows: {str(e)}"
        )

# Application Marketplace Endpoints
@app.get("/api/marketplace/apps")
async def search_marketplace_apps(query: str = "", category: str = "", featured: bool = None, current_user: dict = Depends(get_current_user)):
    """Search marketplace applications"""
    try:
        apps = await app_marketplace.search_apps(query, category, featured)
        return {"apps": apps}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search apps: {str(e)}"
        )

@app.get("/api/marketplace/apps/{app_id}")
async def get_marketplace_app(app_id: str, current_user: dict = Depends(get_current_user)):
    """Get marketplace application"""
    try:
        app = await app_marketplace.get_app(app_id)
        if not app:
            raise HTTPException(status_code=404, detail="App not found")
        return app
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get app: {str(e)}"
        )

@app.post("/api/marketplace/apps/{app_id}/install")
async def install_marketplace_app(app_id: str, current_user: dict = Depends(get_current_user)):
    """Install marketplace application"""
    try:
        success = await app_marketplace.install_app(app_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to install app: {str(e)}"
        )

@app.post("/api/marketplace/apps/{app_id}/uninstall")
async def uninstall_marketplace_app(app_id: str, current_user: dict = Depends(get_current_user)):
    """Uninstall marketplace application"""
    try:
        success = await app_marketplace.uninstall_app(app_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to uninstall app: {str(e)}"
        )

@app.get("/api/marketplace/categories")
async def get_marketplace_categories(current_user: dict = Depends(get_current_user)):
    """Get marketplace categories"""
    try:
        categories = await app_marketplace.get_categories()
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get categories: {str(e)}"
        )

@app.get("/api/marketplace/featured")
async def get_featured_apps(current_user: dict = Depends(get_current_user)):
    """Get featured applications"""
    try:
        apps = await app_marketplace.get_featured_apps()
        return {"apps": apps}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get featured apps: {str(e)}"
        )

# Custom Launchers Endpoints
@app.post("/api/launchers")
async def create_launcher(launcher_config: dict, current_user: dict = Depends(get_current_user)):
    """Create custom launcher"""
    try:
        launcher_id = await custom_launcher_manager.create_launcher(launcher_config)
        return {"success": launcher_id is not None, "launcher_id": launcher_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create launcher: {str(e)}"
        )

@app.get("/api/launchers")
async def list_launchers(category: str = None, enabled_only: bool = False, current_user: dict = Depends(get_current_user)):
    """List custom launchers"""
    try:
        launchers = await custom_launcher_manager.list_launchers(category, enabled_only)
        return {"launchers": launchers}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list launchers: {str(e)}"
        )

@app.get("/api/launchers/{launcher_id}")
async def get_launcher(launcher_id: str, current_user: dict = Depends(get_current_user)):
    """Get launcher information"""
    try:
        launcher = await custom_launcher_manager.get_launcher(launcher_id)
        if not launcher:
            raise HTTPException(status_code=404, detail="Launcher not found")
        return launcher
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get launcher: {str(e)}"
        )

@app.post("/api/launchers/{launcher_id}/launch")
async def launch_custom_app(launcher_id: str, current_user: dict = Depends(get_current_user)):
    """Launch application with custom launcher"""
    try:
        result = await custom_launcher_manager.launch_application(launcher_id, current_user["username"])
        return {"success": result is not None, "process_info": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to launch app: {str(e)}"
        )

@app.delete("/api/launchers/{launcher_id}")
async def delete_launcher(launcher_id: str, current_user: dict = Depends(get_current_user)):
    """Delete custom launcher"""
    try:
        success = await custom_launcher_manager.delete_launcher(launcher_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete launcher: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 3000)),
        reload=True
    )

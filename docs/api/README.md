# API Reference

Complete API documentation for Application Share.

## 🔗 Base URL

```
http://localhost:3000/api
```

## 🔐 Authentication

All API endpoints require authentication using JWT tokens.

### Getting a Token

```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'
```

### Using the Token

Include the token in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:3000/api/applications
```

## 📚 API Endpoints

### Authentication

#### POST /api/auth/login
Login and get JWT token.

**Request:**
```json
{
  "username": "admin",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "username": "admin",
    "is_admin": true
  }
}
```

#### POST /api/auth/init-admin
Initialize admin account (first time setup).

**Request:**
```json
{
  "username": "admin",
  "password": "new-password"
}
```

### Applications

#### GET /api/applications
List available applications.

**Response:**
```json
[
  {
    "name": "firefox",
    "display_name": "Mozilla Firefox",
    "description": "Web browser",
    "icon": "🌐",
    "running": false
  }
]
```

#### POST /api/applications/{app_name}/start
Start an application.

**Response:**
```json
{
  "success": true,
  "process_id": 12345,
  "message": "Application started successfully"
}
```

#### POST /api/applications/{app_name}/stop
Stop an application.

**Response:**
```json
{
  "success": true,
  "message": "Application stopped successfully"
}
```

### VNC Server

#### GET /api/vnc/info
Get VNC server information.

**Response:**
```json
{
  "enabled": true,
  "running": true,
  "port": 5900,
  "password": "vnc-password",
  "clients": 2
}
```

#### POST /api/vnc/start
Start VNC server.

#### POST /api/vnc/stop
Stop VNC server.

### RDP Server

#### GET /api/rdp/info
Get RDP server information.

**Response:**
```json
{
  "enabled": true,
  "running": true,
  "port": 3389,
  "password": "rdp-password"
}
```

#### POST /api/rdp/start
Start RDP server.

#### POST /api/rdp/stop
Stop RDP server.

### Live Streaming

#### GET /api/stream/info
Get live stream information.

**Response:**
```json
{
  "streaming": true,
  "clients": 3,
  "frame_rate": 30,
  "quality": 80
}
```

### Audio Management

#### GET /api/audio/info
Get audio server information.

**Response:**
```json
{
  "enabled": true,
  "clients": 2,
  "recording": false
}
```

#### POST /api/audio/start
Start audio recording.

#### POST /api/audio/stop
Stop audio recording.

### File Management

#### POST /api/files/upload
Upload a file.

**Request:** Multipart form data with file

**Response:**
```json
{
  "success": true,
  "file_id": "abc123",
  "filename": "document.pdf",
  "path": "/tmp/appshare/uploads/admin/document.pdf",
  "info": {
    "size": 1024000,
    "mime_type": "application/pdf",
    "modified": 1640995200
  }
}
```

#### GET /api/files/{file_id}
Download a file.

**Response:** File content with appropriate headers

#### GET /api/files
List user files.

**Response:**
```json
{
  "files": [
    {
      "filename": "document.pdf",
      "file_id": "abc123",
      "info": {
        "size": 1024000,
        "mime_type": "application/pdf",
        "modified": 1640995200
      }
    }
  ]
}
```

#### DELETE /api/files/{file_id}
Delete a file.

**Response:**
```json
{
  "success": true
}
```

### Session Management

#### POST /api/sessions
Create a new session.

**Request:**
```json
{
  "name": "My Session"
}
```

**Response:**
```json
{
  "id": "session-uuid",
  "name": "My Session",
  "owner_id": "admin",
  "created_at": 1640995200,
  "status": "active",
  "participants": ["admin"],
  "settings": {
    "allow_guests": true,
    "max_participants": 10,
    "recording_enabled": false,
    "chat_enabled": true
  }
}
```

#### GET /api/sessions
List available sessions.

**Response:**
```json
{
  "sessions": [
    {
      "id": "session-uuid",
      "name": "My Session",
      "owner_id": "admin",
      "participant_count": 2,
      "max_participants": 10,
      "created_at": 1640995200,
      "can_join": true
    }
  ]
}
```

#### POST /api/sessions/{session_id}/join
Join a session.

#### POST /api/sessions/{session_id}/leave
Leave a session.

#### GET /api/sessions/{session_id}
Get session information.

### Application Templates

#### GET /api/templates
List application templates.

**Query Parameters:**
- `category` (optional): Filter by category

**Response:**
```json
{
  "templates": [
    {
      "id": "development",
      "name": "Development Environment",
      "description": "Complete development setup",
      "icon": "💻",
      "category": "development",
      "app_count": 3
    }
  ]
}
```

#### GET /api/templates/{template_id}
Get template information.

#### POST /api/templates/{template_id}/launch
Launch applications from template.

### WebRTC

#### GET /api/webrtc/info
Get WebRTC server information.

**Response:**
```json
{
  "active_connections": 2,
  "video_tracks": 2,
  "audio_tracks": 1
}
```

### Clipboard

#### GET /api/clipboard
Get clipboard data.

**Response:**
```json
{
  "data": "Clipboard content"
}
```

#### POST /api/clipboard
Set clipboard data.

**Request:**
```json
{
  "data": "New clipboard content"
}
```

### Recording

#### POST /api/recordings/{session_id}/start
Start session recording.

#### POST /api/recordings/{session_id}/stop
Stop session recording.

#### GET /api/recordings
List available recordings.

#### GET /api/recordings/{session_id}
Get recording information.

### Window Management

#### GET /api/windows/info
Get window manager information.

**Response:**
```json
{
  "tiling_enabled": true,
  "screen": {
    "width": 1920,
    "height": 1080,
    "display": ":99"
  },
  "window_count": 3,
  "layouts": ["tiled", "cascade", "grid"],
  "snap_zones": ["left", "right", "top", "bottom"]
}
```

#### POST /api/windows/tile
Tile all windows.

**Query Parameters:**
- `layout` (optional): Layout type (tiled, cascade, grid, maximize)

#### POST /api/windows/{window_id}/snap
Snap window to zone.

**Request:**
```json
{
  "snap_zone": "left"
}
```

#### GET /api/windows
List all windows.

### Application Marketplace

#### GET /api/marketplace/apps
Search marketplace applications.

**Query Parameters:**
- `query` (optional): Search query
- `category` (optional): Filter by category
- `featured` (optional): Show only featured apps

#### GET /api/marketplace/apps/{app_id}
Get marketplace application.

#### POST /api/marketplace/apps/{app_id}/install
Install marketplace application.

#### POST /api/marketplace/apps/{app_id}/uninstall
Uninstall marketplace application.

#### GET /api/marketplace/categories
Get marketplace categories.

#### GET /api/marketplace/featured
Get featured applications.

### Custom Launchers

#### POST /api/launchers
Create custom launcher.

**Request:**
```json
{
  "name": "My Custom App",
  "command": "my-app",
  "executable": "my-app",
  "args": ["--option"],
  "env": {"CUSTOM_VAR": "value"},
  "category": "custom"
}
```

#### GET /api/launchers
List custom launchers.

#### GET /api/launchers/{launcher_id}
Get launcher information.

#### POST /api/launchers/{launcher_id}/launch
Launch application with custom launcher.

#### DELETE /api/launchers/{launcher_id}
Delete custom launcher.

## 🔌 WebSocket Events

### Connection

Connect to WebSocket at `ws://localhost:3000/socket.io/`

### Events

#### Client to Server

**join_application**
```json
{
  "app_name": "firefox"
}
```

**leave_application**
```json
{}
```

**mouse_event**
```json
{
  "type": "click",
  "x": 100,
  "y": 200,
  "button": "left"
}
```

**keyboard_event**
```json
{
  "type": "keydown",
  "key": "Enter",
  "code": "Enter"
}
```

**scroll_event**
```json
{
  "deltaX": 0,
  "deltaY": 100
}
```

**join_live_stream**
```json
{}
```

**leave_live_stream**
```json
{}
```

#### Server to Client

**application_started**
```json
{
  "app_name": "firefox",
  "process_id": 12345
}
```

**application_stopped**
```json
{
  "app_name": "firefox",
  "process_id": 12345
}
```

**screenshot_update**
```json
{
  "app_name": "firefox",
  "image_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

**live_stream_frame**
```json
{
  "frame_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
}
```

**audio_data**
```json
{
  "audio_data": "base64-encoded-audio-data",
  "timestamp": 1640995200.123
}
```

## 📊 Response Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## 🔒 Rate Limiting

API requests are rate limited to prevent abuse:

- **Authentication**: 5 requests per minute
- **General API**: 100 requests per minute
- **File Upload**: 10 requests per minute
- **WebSocket**: No rate limiting

## 📝 Error Handling

All errors follow this format:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

## 🧪 Testing

Use the interactive API documentation at:
- **Swagger UI**: http://localhost:3000/docs
- **ReDoc**: http://localhost:3000/redoc

## 📚 SDKs

- **Python**: `pip install application-share-sdk`
- **JavaScript**: `npm install @application-share/sdk`
- **Go**: `go get github.com/application-share/sdk-go`
- **Rust**: Add to Cargo.toml: `application-share-sdk = "1.0"`

## 🔄 Webhooks

Configure webhooks for real-time notifications:

```json
{
  "url": "https://your-server.com/webhook",
  "events": ["application.started", "application.stopped"],
  "secret": "webhook-secret"
}
```

## 📈 Analytics

Track API usage with built-in analytics:

- Request counts per endpoint
- Response times
- Error rates
- User activity patterns

---

For more detailed information, see the [Complete API Documentation](complete-api.md).

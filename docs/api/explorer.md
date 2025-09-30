# API Explorer

Interactive API documentation and testing interface for Application Share.

## 🚀 Quick Access

- **Swagger UI**: [Interactive API Explorer](https://donskyblock.github.io/application-share/api/swagger/)
- **ReDoc**: [Alternative API Docs](https://donskyblock.github.io/application-share/api/redoc/)
- **OpenAPI Spec**: [Raw OpenAPI JSON](https://donskyblock.github.io/application-share/api/openapi.json)

## 📋 Available Endpoints

### Authentication
- `POST /api/auth/login` - Admin login
- `POST /api/auth/init-admin` - Initialize admin account
- `POST /api/auth/refresh` - Refresh JWT token

### Application Management
- `GET /api/apps` - List available applications
- `POST /api/apps/start` - Start an application
- `POST /api/apps/stop` - Stop an application
- `GET /api/apps/{app_id}/status` - Get application status
- `GET /api/apps/{app_id}/screenshot` - Get application screenshot

### VNC Server
- `GET /api/vnc/info` - Get VNC server information
- `POST /api/vnc/start` - Start VNC server
- `POST /api/vnc/stop` - Stop VNC server

### RDP Server
- `GET /api/rdp/info` - Get RDP server information
- `POST /api/rdp/start` - Start RDP server
- `POST /api/rdp/stop` - Stop RDP server

### Live Streaming
- `GET /api/stream/info` - Get streaming information
- `POST /api/stream/start` - Start live stream
- `POST /api/stream/stop` - Stop live stream

### Audio Management
- `GET /api/audio/info` - Get audio configuration
- `POST /api/audio/start` - Start audio forwarding
- `POST /api/audio/stop` - Stop audio forwarding

### File Transfer
- `GET /api/files/list` - List files in directory
- `POST /api/files/upload` - Upload file
- `GET /api/files/download/{file_id}` - Download file
- `DELETE /api/files/{file_id}` - Delete file

### Session Management
- `GET /api/sessions` - List active sessions
- `POST /api/sessions/create` - Create new session
- `POST /api/sessions/{session_id}/join` - Join session
- `POST /api/sessions/{session_id}/leave` - Leave session

### Application Templates
- `GET /api/templates` - List available templates
- `POST /api/templates` - Create new template
- `GET /api/templates/{template_id}` - Get template details
- `PUT /api/templates/{template_id}` - Update template
- `DELETE /api/templates/{template_id}` - Delete template

### WebRTC
- `GET /api/webrtc/info` - Get WebRTC configuration
- `POST /api/webrtc/offer` - Create WebRTC offer
- `POST /api/webrtc/answer` - Create WebRTC answer

### Clipboard
- `GET /api/clipboard` - Get clipboard content
- `POST /api/clipboard` - Set clipboard content

### Recording
- `GET /api/recording/info` - Get recording status
- `POST /api/recording/start` - Start recording
- `POST /api/recording/stop` - Stop recording
- `GET /api/recording/download/{recording_id}` - Download recording

### Advanced Window Management
- `GET /api/windows` - List all windows
- `POST /api/windows/tile` - Tile windows
- `POST /api/windows/snap` - Snap window to edge
- `POST /api/windows/focus` - Focus window

### Application Marketplace
- `GET /api/marketplace/apps` - List marketplace apps
- `POST /api/marketplace/install` - Install app from marketplace
- `GET /api/marketplace/categories` - List app categories

### Custom Launchers
- `GET /api/launchers` - List custom launchers
- `POST /api/launchers` - Create custom launcher
- `PUT /api/launchers/{launcher_id}` - Update launcher
- `DELETE /api/launchers/{launcher_id}` - Delete launcher

## 🔌 WebSocket Events

### Connection
- `connect` - Connect to WebSocket
- `disconnect` - Disconnect from WebSocket

### Application Events
- `app_started` - Application started
- `app_stopped` - Application stopped
- `app_error` - Application error

### Input Events
- `mouse_event` - Mouse input
- `keyboard_event` - Keyboard input
- `scroll_event` - Scroll input

### Live Stream Events
- `join_live_stream` - Join live stream
- `leave_live_stream` - Leave live stream
- `stream_frame` - New frame data

### Session Events
- `session_created` - Session created
- `session_joined` - User joined session
- `session_left` - User left session

## 🧪 Testing API

### Using curl

```bash
# Login
curl -X POST "http://localhost:3000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'

# Start application
curl -X POST "http://localhost:3000/api/apps/start" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"app_name": "firefox"}'

# Get VNC info
curl -X GET "http://localhost:3000/api/vnc/info" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Using JavaScript

```javascript
// Login
const loginResponse = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'password' })
});
const { access_token } = await loginResponse.json();

// Start application
const appResponse = await fetch('/api/apps/start', {
  method: 'POST',
  headers: { 
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ app_name: 'firefox' })
});
```

### Using Python

```python
import requests

# Login
login_data = {"username": "admin", "password": "password"}
response = requests.post("http://localhost:3000/api/auth/login", json=login_data)
token = response.json()["access_token"]

# Start application
headers = {"Authorization": f"Bearer {token}"}
app_data = {"app_name": "firefox"}
response = requests.post("http://localhost:3000/api/apps/start", 
                        json=app_data, headers=headers)
```

## 📊 Response Formats

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "details": { ... }
}
```

### Application Status
```json
{
  "app_id": "firefox_123",
  "name": "firefox",
  "status": "running",
  "pid": 12345,
  "window_id": "0x123456",
  "created_at": "2024-01-01T12:00:00Z"
}
```

## 🔐 Authentication

All API endpoints (except login and init-admin) require JWT authentication:

```http
Authorization: Bearer YOUR_JWT_TOKEN
```

JWT tokens expire after 24 hours. Use the refresh endpoint to get a new token.

## 📝 Rate Limiting

- **Login attempts**: 5 per minute per IP
- **API calls**: 1000 per hour per user
- **File uploads**: 10MB per request
- **WebSocket connections**: 10 per user

## 🚨 Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 429 | Rate Limited |
| 500 | Internal Server Error |

---

**Need help?** Check the [API Reference](README.md) or open an [issue](https://github.com/donskyblock/application-share/issues)!

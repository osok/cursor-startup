# WebSocket Conventions

## Environment Variables
```bash
WEBSOCKET_URL=ws://localhost:8000/ws
REDIS_URL=redis://localhost:6379
MAX_CONNECTIONS_PER_USER=5
MESSAGE_RATE_LIMIT=100
```

## Project Structure
```
src/websocket/
├── connection_manager.py
├── handlers/
└── auth.py
```

## Core Patterns

### WebSocket Endpoint
```python
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, user = Depends(get_current_user_ws)):
    await connection_manager.connect(websocket, client_id, user)
    try:
        while True:
            data = await websocket.receive_json()
            await route_message(data, client_id, user)
    except WebSocketDisconnect:
        await connection_manager.disconnect(client_id)
```

### Connection Manager
```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[int, Set[str]] = {}
        self.room_connections: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str, user): ...
    async def disconnect(self, client_id: str): ...
    async def send_personal_message(self, message: dict, client_id: str): ...
    async def send_room_message(self, message: dict, room_id: str, exclude_client: str = None): ...
    async def join_room(self, client_id: str, room_id: str): ...
    async def leave_room(self, client_id: str, room_id: str): ...
```

### Authentication
```python
async def get_current_user_ws(websocket: WebSocket, token: str = Query(...)):
    # Decode JWT, validate user, close on auth failure
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    # Return user or None
```

### Message Handler Pattern
```python
class ChatHandler:
    async def handle_message(self, data: dict, client_id: str, user): ...
    async def handle_send_message(self, data: dict, client_id: str, user): ...
    async def handle_join_room(self, data: dict, client_id: str, user): ...
```

### JavaScript Client
```javascript
class WebSocketClient {
    constructor(url, token) { ... }
    connect() { ... }
    send(message) { ... }
    on(messageType, handler) { ... }
    joinRoom(roomId) { ... }
    sendMessage(roomId, message) { ... }
}
```

### React Hook
```javascript
export const useWebSocket = (url, token) => {
    // Returns: { isConnected, messages, sendMessage, subscribe }
}
```

## Message Format
```javascript
// Client to Server
{
    "type": "chat",
    "action": "send_message",
    "room_id": "room123",
    "message": "Hello"
}

// Server to Client
{
    "type": "chat_message",
    "room_id": "room123",
    "user_id": 1,
    "username": "John",
    "content": "Hello",
    "timestamp": "2024-01-01T12:00:00Z"
}
```

## Best Practices
- **Auth**: JWT token via query parameter
- **Rate Limiting**: Per-client message limits
- **Connection Limits**: Max connections per user
- **Error Handling**: Graceful disconnect cleanup
- **Scaling**: Redis pub/sub for multi-instance
- **Security**: WSS in production, validate inputs
- **Reconnection**: Exponential backoff client-side
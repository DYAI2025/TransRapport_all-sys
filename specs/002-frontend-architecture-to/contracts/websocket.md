# WebSocket Contract: Real-Time Communication

**Endpoint**: `ws://localhost:8000/ws/{userId}`  
**Protocol**: WebSocket  
**Message Format**: JSON

## Connection Management

### Connection Establishment
```
GET /ws/{userId}
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: [client-generated]
Sec-WebSocket-Version: 13
```

**Response**: HTTP 101 Switching Protocols

### Authentication
- User ID in URL path for session association
- Optional API key in query parameters: `?api_key=xxx`
- Connection rejected with HTTP 403 if invalid user

### Heartbeat
- Client sends `{"type": "ping", "timestamp": 1234567890}` every 30 seconds
- Server responds with `{"type": "pong", "timestamp": 1234567890}`
- Connection assumed dead after 3 missed heartbeats

## Message Schema

### Base Message Interface
```typescript
interface BaseMessage {
  type: string;
  sessionId?: string;
  timestamp: number;
  [key: string]: any;
}
```

### Client → Server Messages

#### Start Validation
```json
{
  "type": "start_validation",
  "command": "transrapport-docs validate --strict",
  "workdir": "/path/to/docs",
  "settings": {
    "strict": true,
    "format": "json",
    "filePatterns": ["**/*.md"],
    "excludePatterns": ["node_modules/**"]
  },
  "timestamp": 1699123456789
}
```

#### Cancel Validation
```json
{
  "type": "cancel_validation",
  "sessionId": "uuid-session-id",
  "timestamp": 1699123456789
}
```

#### Pause/Resume Validation
```json
{
  "type": "pause_validation",
  "sessionId": "uuid-session-id", 
  "timestamp": 1699123456789
}
```

```json
{
  "type": "resume_validation",
  "sessionId": "uuid-session-id",
  "timestamp": 1699123456789
}
```

#### Client Heartbeat
```json
{
  "type": "ping",
  "timestamp": 1699123456789
}
```

### Server → Client Messages

#### Session Lifecycle

**Session Start**
```json
{
  "type": "session_start",
  "sessionId": "uuid-session-id",
  "command": "transrapport-docs validate --strict",
  "workdir": "/path/to/docs",
  "timestamp": 1699123456789
}
```

**Session End**
```json
{
  "type": "session_end",
  "sessionId": "uuid-session-id",
  "status": "completed",
  "exitCode": 0,
  "duration": 15.6,
  "timestamp": 1699123456789
}
```

#### Progress Updates

**Stage Progress**
```json
{
  "type": "progress",
  "sessionId": "uuid-session-id",
  "stage": "parsing",
  "percentage": 45.0,
  "currentFile": "docs/architecture.md",
  "totalFiles": 25,
  "processedFiles": 11,
  "errorsFound": 2,
  "warningsFound": 7,
  "timestamp": 1699123456789
}
```

**File Processing**
```json
{
  "type": "file_start",
  "sessionId": "uuid-session-id",
  "file": "docs/terminologie.md",
  "fileIndex": 12,
  "totalFiles": 25,
  "timestamp": 1699123456789
}
```

```json
{
  "type": "file_complete",
  "sessionId": "uuid-session-id", 
  "file": "docs/terminologie.md",
  "duration": 0.8,
  "issuesFound": 3,
  "timestamp": 1699123456789
}
```

#### Real-Time Output

**Standard Output**
```json
{
  "type": "output",
  "sessionId": "uuid-session-id",
  "stream": "stdout",
  "content": "✓ Validating terminologie.md...",
  "lineNumber": 1,
  "timestamp": 1699123456789
}
```

**Error Output**  
```json
{
  "type": "output",
  "sessionId": "uuid-session-id",
  "stream": "stderr", 
  "content": "Warning: Missing cross-reference to marker.md",
  "lineNumber": 2,
  "timestamp": 1699123456789
}
```

#### Results and Data

**Validation Result**
```json
{
  "type": "result",
  "sessionId": "uuid-session-id",
  "result": {
    "id": "uuid-result-id",
    "file": "docs/terminologie.md",
    "rule": "terminology_completeness",
    "severity": "warning",
    "lineNumber": 15,
    "message": "Missing key marker terms: MEMA",
    "suggestion": "Add definitions for all marker levels (ATO, SEM, CLU, MEMA)",
    "context": "**CLU** · Cluster markers...",
    "validatedAt": "2025-09-09T10:30:45.123Z"
  },
  "timestamp": 1699123456789
}
```

**Batch Results** (for performance)
```json
{
  "type": "batch_results",
  "sessionId": "uuid-session-id",
  "results": [
    {
      "id": "uuid-result-1",
      "file": "docs/file1.md",
      "rule": "markdown_structure",
      "severity": "error",
      "message": "Missing main title",
      "suggestion": "Add # Title at document start"
    },
    {
      "id": "uuid-result-2", 
      "file": "docs/file2.md",
      "rule": "content_completeness",
      "severity": "warning",
      "message": "Document too short",
      "suggestion": "Add more content"
    }
  ],
  "timestamp": 1699123456789
}
```

#### Error Handling

**Validation Error**
```json
{
  "type": "error",
  "sessionId": "uuid-session-id",
  "code": "VALIDATION_FAILED",
  "message": "CLI process exited with code 2",
  "details": {
    "exitCode": 2,
    "stderr": "transrapport-docs: command not found"
  },
  "timestamp": 1699123456789
}
```

**System Error**
```json
{
  "type": "error",
  "code": "INTERNAL_ERROR",
  "message": "Failed to start validation process",
  "details": {
    "reason": "Permission denied accessing /path/to/docs"
  },
  "timestamp": 1699123456789
}
```

#### Server Heartbeat
```json
{
  "type": "pong",
  "timestamp": 1699123456789
}
```

## Connection States

### Client States
- **CONNECTING**: Initial WebSocket connection
- **CONNECTED**: Ready to send/receive messages  
- **VALIDATING**: Active validation session running
- **DISCONNECTED**: Connection lost, attempting reconnect
- **FAILED**: Max reconnection attempts exceeded

### Server States  
- **IDLE**: Connection established, no active validation
- **PROCESSING**: Validation command executing
- **STREAMING**: Actively streaming output to client
- **COMPLETE**: Validation finished, results available
- **ERROR**: Validation failed or system error occurred

## Error Codes

### Client Error Codes
- **INVALID_MESSAGE**: Malformed JSON or missing required fields
- **UNKNOWN_COMMAND**: Unsupported message type
- **SESSION_NOT_FOUND**: Referenced session ID doesn't exist
- **VALIDATION_IN_PROGRESS**: Cannot start new validation during active session

### Server Error Codes
- **CLI_NOT_FOUND**: TransRapport CLI not available  
- **PERMISSION_DENIED**: Access denied to working directory
- **VALIDATION_FAILED**: CLI process exited with error
- **TIMEOUT**: Validation exceeded configured time limit
- **INTERNAL_ERROR**: Server-side processing error
- **RATE_LIMITED**: Too many concurrent validations

## Performance Considerations

### Message Throttling
- Output messages batched if frequency > 10/second
- Progress updates maximum 1/second per session
- Result batching when > 100 results found quickly

### Connection Limits
- Maximum 10 concurrent sessions per user
- Maximum 100 concurrent connections per server instance
- Idle connections closed after 1 hour

### Resource Management
- Validation processes killed after 10 minute timeout
- Output buffers limited to 10,000 lines per session
- Results limited to 50,000 per session (with truncation)

## Example Usage Flow

```
1. Client connects: ws://localhost:8000/ws/user123
2. Server accepts connection
3. Client sends: {"type": "start_validation", "command": "..."}  
4. Server responds: {"type": "session_start", "sessionId": "..."}
5. Server streams: {"type": "progress", ...}, {"type": "output", ...}
6. Server sends results: {"type": "result", ...}
7. Server completes: {"type": "session_end", "status": "completed"}
8. Connection remains open for future validations
```

## Testing Contract

### Unit Test Coverage
- Message serialization/deserialization
- Connection state transitions
- Error handling and recovery
- Heartbeat mechanism

### Integration Test Scenarios
- Complete validation workflow
- Connection drop and recovery
- Multiple concurrent sessions
- Large output handling
- Error conditions and edge cases

---

**WebSocket Contract Status**: Complete  
**Message Types**: 15 client→server, 20 server→client  
**Error Handling**: Comprehensive error codes and recovery  
**Ready for**: Implementation and contract testing
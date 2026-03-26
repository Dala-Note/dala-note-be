# Collaboration Service

A real-time collaboration service built with Node.js, Express, Socket.IO, and Redis for enabling multiple users to edit notes simultaneously.

## Features

- **Real-time Collaboration**: Multiple users can edit the same note simultaneously
- **Socket.IO Integration**: WebSocket-based real-time communication
- **Redis Pub/Sub**: Scalable message broadcasting across service instances
- **Input Validation**: Comprehensive validation using Joi schemas
- **Error Handling**: Robust error handling with detailed logging
- **Rate Limiting**: Protection against abuse with configurable limits
- **Health Monitoring**: Health check endpoints for service monitoring
- **Graceful Shutdown**: Proper cleanup on service termination

## Prerequisites

- Node.js (v14 or higher)
- Redis server
- Environment variables configured

## Installation

1. Install dependencies:
```bash
npm install express socket.io redis joi express-rate-limit
```

2. Set up environment variables:
```bash
export REDISURL="redis://localhost:6379"
export PORT=3001
export NODE_ENV="development"
```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `REDISURL` | Redis connection URL | Yes | - |
| `PORT` | Server port | No | 3001 |
| `NODE_ENV` | Environment (development/production) | No | development |

## API Endpoints

### Health Check
- **GET** `/` - Basic service status
- **GET** `/health` - Detailed health check with Redis connectivity

## Socket.IO Events

### Client → Server Events

#### `join_note`
Join a note's editing session.

**Parameters:**
- `noteId` (string): Note identifier (1-100 chars, alphanumeric + underscore/hyphen)

**Rate Limit:** 10 requests per minute per socket

**Response Events:**
- `join_success`: Confirmation of successful join
- `error`: Error message if join fails

#### `edit_note`
Send content updates to other users editing the same note.

**Parameters:**
```javascript
{
  noteId: string,    // Note identifier
  content: string    // Note content (max 1MB)
}
```

**Rate Limit:** 30 requests per minute per socket

**Validation:**
- User must be in the note room
- Content size limited to 1MB
- Note ID must be valid format

**Response Events:**
- `note_updated`: Broadcast to other users in the room
- `error`: Error message if edit fails

#### `leave_note`
Leave a note's editing session.

**Parameters:**
- `noteId` (string): Note identifier

**Rate Limit:** 10 requests per minute per socket

**Response Events:**
- `leave_success`: Confirmation of successful leave
- `error`: Error message if leave fails

### Server → Client Events

#### `note_updated`
Broadcasted when a note is updated by another user.

**Parameters:**
```javascript
{
  content: string,      // Updated content
  noteId: string,       // Note identifier
  timestamp: string,    // ISO timestamp
  userId: string        // Socket ID of the user who made the change
}
```

#### `error`
Error messages for various failure scenarios.

**Parameters:**
```javascript
{
  message: string,      // Error description
  code: string,        // Error code (VALIDATION_ERROR, RATE_LIMIT_EXCEEDED, etc.)
  timestamp: string     // ISO timestamp
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `NOT_IN_ROOM` | User not in note room for editing |
| `REDIS_ERROR` | Redis operation failed |
| `UNKNOWN_ERROR` | Unexpected error |

## Rate Limiting

### HTTP Endpoints
- **General API**: 100 requests per 15 minutes per IP
- **Socket Events**: 60 requests per minute per IP

### Socket.IO Events
- **join_note**: 10 requests per minute per socket
- **edit_note**: 30 requests per minute per socket  
- **leave_note**: 10 requests per minute per socket

## Input Validation

### Note ID Validation
- **Format**: Alphanumeric characters, underscores, and hyphens only
- **Length**: 1-100 characters
- **Required**: Yes

### Content Validation
- **Type**: String
- **Max Size**: 1MB
- **Required**: Yes

## Error Handling

The service includes comprehensive error handling for:

- **Validation Errors**: Invalid input data
- **Rate Limiting**: Too many requests
- **Redis Errors**: Connection and operation failures
- **Socket Errors**: WebSocket communication issues
- **Room Validation**: Users must be in note rooms to edit

## Redis Integration

### Channels
- `note_updates`: Published when notes are updated

### Message Format
```javascript
{
  noteId: string,
  content: string,
  timestamp: string,
  userId: string
}
```

## Monitoring

### Health Check Response
```javascript
{
  "success": true,
  "status": "healthy",
  "redis": "connected",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

### Error Response Format
```javascript
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

## Development

### Running the Service
```bash
npm start
```

### Environment Setup
```bash
# Development
export NODE_ENV=development
export REDISURL=redis://localhost:6379
export PORT=3001

# Production
export NODE_ENV=production
export REDISURL=redis://your-redis-instance:6379
export PORT=3001
```

## Production Considerations

1. **CORS Configuration**: Update CORS settings for production domains
2. **Redis Security**: Use Redis AUTH and TLS in production
3. **Rate Limiting**: Adjust limits based on expected load
4. **Monitoring**: Set up proper logging and monitoring
5. **Scaling**: Consider Redis clustering for high availability

## Graceful Shutdown

The service handles graceful shutdown on:
- `SIGTERM` signal
- `SIGINT` signal (Ctrl+C)

Shutdown process:
1. Stop accepting new connections
2. Close Redis connections
3. Clean up rate limiting data
4. Exit process

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   - Check `REDISURL` environment variable
   - Verify Redis server is running
   - Check network connectivity

2. **Rate Limiting Issues**
   - Adjust rate limits in `middleware/rateLimiter.js`
   - Check for client-side request batching

3. **Validation Errors**
   - Review input format requirements
   - Check note ID format (alphanumeric + underscore/hyphen only)

### Logs

The service logs:
- Connection events
- Error details with context
- Rate limiting violations
- Redis connection status
- Graceful shutdown events

## License

[Add your license information here]

// =============================================================================
// Dependencies
// =============================================================================

const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const redis = require('redis');
const rateLimit = require('express-rate-limit');

// =============================================================================
// Server Setup
// =============================================================================

// Initialize an Express application
const app = express();
// Create an HTTP server from the Express app
const server = http.createServer(app);
// Initialize a new instance of socket.io by passing the HTTP server object
// and configuring CORS to allow connections from any origin.
const io = new Server(server, {
  cors: {
    origin: '*', // In a production environment, you should restrict this to your frontend's domain.
  },
});

// Define the port the server will listen on.
const PORT = process.env.PORT || 3001;

// =============================================================================
// Redis Client Configuration
// =============================================================================

// Create a Redis client. The client will connect to the Redis Cloud instance
// using the provided connection string.
const redisClient = redis.createClient({
  url: process.env.REDISURL,
});

// Listen for errors on the Redis client and log them to the console.
redisClient.on('error', (err) => console.log('Redis Client Error', err));

// Connect to the Redis server.
redisClient.connect();

// Duplicate the Redis client to create a dedicated publisher for Pub/Sub.
const publisher = redisClient.duplicate();
// Connect the publisher client to Redis.
publisher.connect();

const { asyncHandler, errorHandler, rateLimitErrorHandler, socketErrorHandler } = require('./middleware/errorMiddleware');
const { generalLimiter, socketEventLimiter, noteEditLimiter, SocketRateLimiter } = require('./middleware/rateLimiter');

// =============================================================================
// Environment Validation
// =============================================================================

// Validate required environment variables
const requiredEnvVars = ['REDISURL'];
const missingEnvVars = requiredEnvVars.filter(envVar => !process.env[envVar]);

if (missingEnvVars.length > 0) {
  console.error('Missing required environment variables:', missingEnvVars);
  process.exit(1);
}

// =============================================================================
// Middleware Setup
// =============================================================================

// Apply rate limiting
app.use(generalLimiter);

// =============================================================================
// Routes
// =============================================================================

// A simple health-check route to confirm the service is running.
app.get('/', asyncHandler((req, res) => {
  res.json({
    success: true,
    message: 'Collab service is running',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
}));

// Health check route with Redis connectivity
app.get('/health', asyncHandler(async (req, res) => {
  try {
    // Test Redis connection
    await redisClient.ping();
    res.json({
      success: true,
      status: 'healthy',
      redis: 'connected',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(503).json({
      success: false,
      status: 'unhealthy',
      redis: 'disconnected',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
}));

// =============================================================================
// Socket.IO Connection Handling
// =============================================================================

const { noteIdSchema, editNoteSchema, socketConnectionSchema, rateLimitSchema } = require('./validation');

// Initialize rate limiter for socket events
const socketRateLimiter = new SocketRateLimiter();

// This event is fired upon a new connection from a client.
io.on('connection', (socket) => {
  console.log(`User connected: ${socket.id}`);

  // Enhanced connection handling with error catching
  socket.on('error', (error) => {
    socketErrorHandler(socket, error);
  });

  // Event listener for when a user wants to join a specific note's editing session.
  socket.on('join_note', (noteId) => {
    try {
      // Rate limiting check
      if (!socketRateLimiter.isAllowed(socket.id, 'join_note', 10, 60000)) {
        socket.emit('error', { 
          message: 'Too many join requests. Please slow down.',
          code: 'RATE_LIMIT_EXCEEDED'
        });
        return;
      }

      const { error } = noteIdSchema.validate(noteId);
      if (error) {
        console.error('Invalid noteId received for join_note:', noteId, error.details);
        socket.emit('error', { 
          message: error.details[0].message,
          code: 'VALIDATION_ERROR'
        });
        return;
      }

      // The user's socket joins a "room" that is identified by the noteId.
      // This allows for broadcasting messages to only the users editing the same note.
      socket.join(noteId);
      console.log(`User ${socket.id} joined note ${noteId}`);
      
      // Acknowledge successful join
      socket.emit('join_success', { noteId, timestamp: new Date().toISOString() });
    } catch (error) {
      socketErrorHandler(socket, error);
    }
  });

  // Event listener for when a user sends an edit to a note.
  socket.on('edit_note', async (data) => {
    try {
      // Rate limiting check for edit events
      if (!socketRateLimiter.isAllowed(socket.id, 'edit_note', 30, 60000)) {
        socket.emit('error', { 
          message: 'Too many edit requests. Please slow down.',
          code: 'RATE_LIMIT_EXCEEDED'
        });
        return;
      }

      const { error } = editNoteSchema.validate(data);
      if (error) {
        console.error('Invalid data received for edit_note:', data, error.details);
        socket.emit('error', { 
          message: error.details[0].message,
          code: 'VALIDATION_ERROR'
        });
        return;
      }

      const { noteId, content } = data;
      
      // Validate that the socket is in the note room
      if (!socket.rooms.has(noteId)) {
        socket.emit('error', { 
          message: 'You must join the note before editing.',
          code: 'NOT_IN_ROOM'
        });
        return;
      }

      // Broadcast the updated content to all other users in the same note room.
      // The current user's socket is excluded from the broadcast.
      socket.to(noteId).emit('note_updated', {
        content,
        noteId,
        timestamp: new Date().toISOString(),
        userId: socket.id
      });

      // Publish the note update to the 'note_updates' Redis channel.
      // This allows other services in the system to be notified of the change.
      try {
        await publisher.publish('note_updates', JSON.stringify({ 
          noteId, 
          content,
          timestamp: new Date().toISOString(),
          userId: socket.id
        }));
        console.log(`Note ${noteId} updated by ${socket.id}`);
      } catch (err) {
        console.error('Failed to publish note update to Redis:', err);
        socket.emit('error', { 
          message: 'Failed to save changes. Please try again.',
          code: 'REDIS_ERROR'
        });
      }
    } catch (error) {
      socketErrorHandler(socket, error);
    }
  });

  // Event listener for when a user leaves a note's editing session.
  socket.on('leave_note', (noteId) => {
    try {
      // Rate limiting check
      if (!socketRateLimiter.isAllowed(socket.id, 'leave_note', 10, 60000)) {
        socket.emit('error', { 
          message: 'Too many leave requests. Please slow down.',
          code: 'RATE_LIMIT_EXCEEDED'
        });
        return;
      }

      const { error } = noteIdSchema.validate(noteId);
      if (error) {
        console.error('Invalid noteId received for leave_note:', noteId, error.details);
        socket.emit('error', { 
          message: error.details[0].message,
          code: 'VALIDATION_ERROR'
        });
        return;
      }
      
      socket.leave(noteId);
      console.log(`User ${socket.id} left note ${noteId}`);
      
      // Acknowledge successful leave
      socket.emit('leave_success', { noteId, timestamp: new Date().toISOString() });
    } catch (error) {
      socketErrorHandler(socket, error);
    }
  });

  // Event listener for when a user disconnects from the server.
  socket.on('disconnect', (reason) => {
    console.log(`User disconnected: ${socket.id}, reason: ${reason}`);
    
    // Clean up any rate limiting data for this socket
    socketRateLimiter.cleanup();
  });
});

// =============================================================================
// Error Handling Middleware
// =============================================================================

// Apply error handlers
app.use(rateLimitErrorHandler);
app.use(errorHandler);

// =============================================================================
// Redis Error Handling
// =============================================================================

// Enhanced Redis error handling
redisClient.on('error', (err) => {
  console.error('Redis Client Error:', {
    message: err.message,
    code: err.code,
    timestamp: new Date().toISOString()
  });
});

redisClient.on('connect', () => {
  console.log('Redis client connected successfully');
});

redisClient.on('reconnecting', () => {
  console.log('Redis client reconnecting...');
});

publisher.on('error', (err) => {
  console.error('Redis Publisher Error:', {
    message: err.message,
    code: err.code,
    timestamp: new Date().toISOString()
  });
});

// =============================================================================
// Graceful Shutdown
// =============================================================================

const gracefulShutdown = (signal) => {
  console.log(`Received ${signal}. Starting graceful shutdown...`);
  
  server.close(() => {
    console.log('HTTP server closed');
    
    // Close Redis connections
    redisClient.quit().then(() => {
      console.log('Redis client closed');
    }).catch((err) => {
      console.error('Error closing Redis client:', err);
    });
    
    publisher.quit().then(() => {
      console.log('Redis publisher closed');
    }).catch((err) => {
      console.error('Error closing Redis publisher:', err);
    });
    
    // Clean up rate limiter
    socketRateLimiter.destroy();
    
    console.log('Graceful shutdown completed');
    process.exit(0);
  });
  
  // Force close after 10 seconds
  setTimeout(() => {
    console.error('Forced shutdown after timeout');
    process.exit(1);
  }, 10000);
};

// Handle shutdown signals
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// =============================================================================
// Start Server
// =============================================================================

// Start the HTTP server and have it listen on the specified port.
server.listen(PORT, () => {
  console.log(`Collab service listening on *:${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`Rate limiting enabled: General API, Socket.IO events`);
});

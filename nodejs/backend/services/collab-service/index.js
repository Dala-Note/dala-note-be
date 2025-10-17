// =============================================================================
// Dependencies
// =============================================================================

const express = require('express');
const http = require('http');
const { Server } = require("socket.io");
const redis = require('redis');

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
    origin: "*", // In a production environment, you should restrict this to your frontend's domain.
  }
});

// Define the port the server will listen on.
const PORT = process.env.PORT || 3001;

// =============================================================================
// Redis Client Configuration
// =============================================================================

// Create a Redis client. The client will connect to the Redis Cloud instance
// using the provided connection string.
const redisClient = redis.createClient({
  url: 'redis://default:qQ3L0tbeKlbWeljmvST0mKPYdQmKmujY@redis-10558.c62.us-east-1-4.ec2.redns.redis-cloud.com:10558'
});

// Listen for errors on the Redis client and log them to the console.
redisClient.on('error', (err) => console.log('Redis Client Error', err));

// Connect to the Redis server.
redisClient.connect();

// Duplicate the Redis client to create a dedicated publisher for Pub/Sub.
const publisher = redisClient.duplicate();
// Connect the publisher client to Redis.
publisher.connect();

// =============================================================================
// Routes
// =============================================================================

// A simple health-check route to confirm the service is running.
app.get('/', (req, res) => {
  res.send('Collab service is running');
});

// =============================================================================
// Socket.IO Connection Handling
// =============================================================================

// This event is fired upon a new connection from a client.
io.on('connection', (socket) => {
  console.log(`User connected: ${socket.id}`);

  // Event listener for when a user wants to join a specific note's editing session.
  socket.on('join_note', (noteId) => {
    // The user's socket joins a "room" that is identified by the noteId.
    // This allows for broadcasting messages to only the users editing the same note.
    socket.join(noteId);
    console.log(`User ${socket.id} joined note ${noteId}`);
  });

  // Event listener for when a user sends an edit to a note.
  socket.on('edit_note', (data) => {
    const { noteId, content } = data;
    // Broadcast the updated content to all other users in the same note room.
    // The current user's socket is excluded from the broadcast.
    socket.to(noteId).emit('note_updated', content);

    // Publish the note update to the 'note_updates' Redis channel.
    // This allows other services in the system to be notified of the change.
    publisher.publish('note_updates', JSON.stringify({ noteId, content }));
  });

  // Event listener for when a user leaves a note's editing session.
  socket.on('leave_note', (noteId) => {
    socket.leave(noteId);
    console.log(`User ${socket.id} left note ${noteId}`);
  });

  // Event listener for when a user disconnects from the server.
  socket.on('disconnect', () => {
    console.log(`User disconnected: ${socket.id}`);
  });
});

// =============================================================================
// Start Server
// =============================================================================

// Start the HTTP server and have it listen on the specified port.
server.listen(PORT, () => {
  console.log(`Collab service listening on *:${PORT}`);
});

# Dala Note - Collaboration Service

This service provides real-time collaboration features for the Dala Note application. It allows multiple users to edit the same note simultaneously and see each other's changes in real-time.

## Overview

-   **Framework:** Node.js with Express
-   **Real-time Communication:** Socket.IO
-   **Inter-service Communication:** Redis Pub/Sub

## Getting Started

### Prerequisites

-   [Node.js](https://nodejs.org/) (v14 or later)
-   A running [Redis](https://redis.io/) instance (local or cloud).

### Installation

1.  Navigate to the `collab-service` directory:
    ```bash
    cd backend/services/collab-service
    ```
2.  Install the dependencies:
    ```bash
    npm install
    ```

### Configuration

The service connects to a Redis instance using a connection string defined in `index.js`. Make sure to update this with your Redis credentials:

```javascript
// in index.js
const redisClient = redis.createClient({
  url: 'your_redis_connection_string'
});
```

### Running the Service

To start the service, run the following command from the root of the project:

```bash
node backend/services/collab-service/index.js
```

The service will start and listen on port `3001`.

## Socket.IO Events

The service uses the following Socket.IO events for real-time collaboration:

-   **`join_note` (client to server):** Allows a user to join a specific note's editing session.
    -   **Payload:** `noteId` (string)
-   **`edit_note` (client to server):** Sent when a user edits a note. The server then broadcasts the changes to other users in the same session.
    -   **Payload:** `{ noteId: string, content: any }`
-   **`leave_note` (client to server):** Allows a user to leave a note's editing session.
    -   **Payload:** `noteId` (string)
-   **`note_updated` (server to client):** Broadcasts the updated content of a note to all users in the session.
    -   **Payload:** `content` (any)

## Inter-service Communication

When a note is edited, the `collab-service` publishes a message to the `note_updates` channel in Redis. Other services can subscribe to this channel to receive notifications of note changes.

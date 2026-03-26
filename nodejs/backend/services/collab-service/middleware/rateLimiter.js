const rateLimit = require('express-rate-limit');

// Rate limiting for general API endpoints
const generalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: {
    success: false,
    error: 'Too many requests from this IP, please try again later.',
    retryAfter: '15 minutes'
  },
  standardHeaders: true,
  legacyHeaders: false,
});

// Stricter rate limiting for Socket.IO events
const socketEventLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute
  max: 60, // limit each IP to 60 requests per minute
  message: {
    success: false,
    error: 'Too many socket events from this IP, please slow down.',
    retryAfter: '1 minute'
  },
  standardHeaders: true,
  legacyHeaders: false,
});

// Rate limiting for note editing events
const noteEditLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute
  max: 30, // limit each IP to 30 edit requests per minute
  message: {
    success: false,
    error: 'Too many note edits from this IP, please slow down.',
    retryAfter: '1 minute'
  },
  standardHeaders: true,
  legacyHeaders: false,
});

// In-memory rate limiting for Socket.IO events
class SocketRateLimiter {
  constructor() {
    this.requests = new Map();
    this.cleanupInterval = setInterval(() => this.cleanup(), 60000); // Clean up every minute
  }

  isAllowed(socketId, eventType, maxRequests = 60, windowMs = 60000) {
    const now = Date.now();
    const key = `${socketId}:${eventType}`;
    
    if (!this.requests.has(key)) {
      this.requests.set(key, []);
    }
    
    const requests = this.requests.get(key);
    
    // Remove old requests outside the window
    const validRequests = requests.filter(timestamp => now - timestamp < windowMs);
    this.requests.set(key, validRequests);
    
    if (validRequests.length >= maxRequests) {
      return false;
    }
    
    validRequests.push(now);
    return true;
  }

  cleanup() {
    const now = Date.now();
    for (const [key, requests] of this.requests.entries()) {
      const validRequests = requests.filter(timestamp => now - timestamp < 300000); // 5 minutes
      if (validRequests.length === 0) {
        this.requests.delete(key);
      } else {
        this.requests.set(key, validRequests);
      }
    }
  }

  destroy() {
    clearInterval(this.cleanupInterval);
    this.requests.clear();
  }
}

module.exports = {
  generalLimiter,
  socketEventLimiter,
  noteEditLimiter,
  SocketRateLimiter
};

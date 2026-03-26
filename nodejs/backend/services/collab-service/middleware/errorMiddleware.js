const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

// Enhanced error handler for different types of errors
const errorHandler = (err, req, res, next) => {
  let error = { ...err };
  error.message = err.message;

  // Log error details
  console.error('Error occurred:', {
    message: err.message,
    stack: err.stack,
    url: req.url,
    method: req.method,
    timestamp: new Date().toISOString()
  });

  // Mongoose bad ObjectId
  if (err.name === 'CastError') {
    const message = 'Resource not found';
    error = { message, statusCode: 404 };
  }

  // Mongoose duplicate key
  if (err.code === 11000) {
    const message = 'Duplicate field value entered';
    error = { message, statusCode: 400 };
  }

  // Mongoose validation error
  if (err.name === 'ValidationError') {
    const message = Object.values(err.errors).map(val => val.message).join(', ');
    error = { message, statusCode: 400 };
  }

  // Joi validation error
  if (err.isJoi) {
    const message = err.details.map(detail => detail.message).join(', ');
    error = { message, statusCode: 400 };
  }

  // Redis connection error
  if (err.code === 'ECONNREFUSED' || err.code === 'ENOTFOUND') {
    const message = 'Database connection failed';
    error = { message, statusCode: 503 };
  }

  // Socket.IO errors
  if (err.name === 'SocketError') {
    const message = 'Socket connection error';
    error = { message, statusCode: 400 };
  }

  res.status(error.statusCode || 500).json({
    success: false,
    error: error.message || 'Server Error',
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
};

// Rate limiting error handler
const rateLimitErrorHandler = (err, req, res, next) => {
  if (err.status === 429) {
    return res.status(429).json({
      success: false,
      error: 'Too many requests, please try again later',
      retryAfter: err.retryAfter
    });
  }
  next(err);
};

// Socket.IO error handler
const socketErrorHandler = (socket, error) => {
  console.error('Socket error:', {
    socketId: socket.id,
    error: error.message,
    timestamp: new Date().toISOString()
  });
  
  socket.emit('error', {
    message: 'An error occurred',
    code: error.code || 'UNKNOWN_ERROR',
    timestamp: new Date().toISOString()
  });
};

module.exports = {
  asyncHandler,
  errorHandler,
  rateLimitErrorHandler,
  socketErrorHandler
};

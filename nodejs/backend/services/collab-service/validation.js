const Joi = require('joi');

// Enhanced noteId validation with specific format requirements
const noteIdSchema = Joi.string()
  .min(1)
  .max(100)
  .pattern(/^[a-zA-Z0-9_-]+$/)
  .required()
  .messages({
    'string.empty': 'Note ID cannot be empty',
    'string.min': 'Note ID must be at least 1 character long',
    'string.max': 'Note ID cannot exceed 100 characters',
    'string.pattern.base': 'Note ID can only contain letters, numbers, underscores, and hyphens',
    'any.required': 'Note ID is required'
  });

// Enhanced edit note schema with content validation
const editNoteSchema = Joi.object({
  noteId: Joi.string()
    .min(1)
    .max(100)
    .pattern(/^[a-zA-Z0-9_-]+$/)
    .required()
    .messages({
      'string.empty': 'Note ID cannot be empty',
      'string.min': 'Note ID must be at least 1 character long',
      'string.max': 'Note ID cannot exceed 100 characters',
      'string.pattern.base': 'Note ID can only contain letters, numbers, underscores, and hyphens',
      'any.required': 'Note ID is required'
    }),
  content: Joi.string()
    .max(1000000) // 1MB limit for content
    .required()
    .messages({
      'string.empty': 'Content cannot be empty',
      'string.max': 'Content cannot exceed 1MB',
      'any.required': 'Content is required'
    })
});

// Schema for validating socket connection data
const socketConnectionSchema = Joi.object({
  userId: Joi.string().optional(),
  userAgent: Joi.string().optional(),
  timestamp: Joi.date().optional()
});

// Schema for rate limiting validation
const rateLimitSchema = Joi.object({
  eventType: Joi.string().valid('join_note', 'edit_note', 'leave_note').required(),
  socketId: Joi.string().required(),
  timestamp: Joi.date().required()
});

module.exports = {
  noteIdSchema,
  editNoteSchema,
  socketConnectionSchema,
  rateLimitSchema,
};

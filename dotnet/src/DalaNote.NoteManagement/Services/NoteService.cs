using Microsoft.EntityFrameworkCore;
using DalaNote.Data.Context;
using DalaNote.Common.Models;
using Microsoft.Extensions.Logging;
using System.Threading.Tasks;
using System.Collections.Generic;
using System;
using System.Linq;

namespace DalaNote.NoteManagement.Services;

public class NoteService : INoteService
{
    private readonly DalaNoteDbContext _context;
    private readonly ILogger<NoteService> _logger;

    public NoteService(DalaNoteDbContext context, ILogger<NoteService> logger)
    {
        _context = context;
        _logger = logger;
    }

    public async Task<ApiResponse<List<Note>>> GetUserNotesAsync(Guid userId)
    {
        try
        {
            var notes = await _context.Notes
                .Where(n => n.UserId == userId)
                .OrderByDescending(n => n.UpdatedAt)
                .ToListAsync();

            return new ApiResponse<List<Note>> 
            { 
                Success = true, 
                Message = "Notes retrieved successfully",
                Data = notes 
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving notes for user {UserId}", userId);
            return new ApiResponse<List<Note>> 
            { 
                Success = false, 
                Message = "Failed to retrieve notes" 
            };
        }
    }

    public async Task<ApiResponse<Note>> GetNoteAsync(Guid id, Guid userId)
    {
        try
        {
            var note = await _context.Notes
                .FirstOrDefaultAsync(n => n.Id == id && n.UserId == userId);

            if (note == null)
            {
                return new ApiResponse<Note> 
                { 
                    Success = false, 
                    Message = "Note not found" 
                };
            }

            return new ApiResponse<Note> 
            { 
                Success = true, 
                Message = "Note retrieved successfully",
                Data = note 
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving note {NoteId}", id);
            return new ApiResponse<Note> 
            { 
                Success = false, 
                Message = "Failed to retrieve note" 
            };
        }
    }

    public async Task<ApiResponse<Note>> CreateNoteAsync(CreateNoteRequest request, Guid userId)
    {
        try
        {
            // Basic validation using your request model
            if (string.IsNullOrWhiteSpace(request.Title))
            {
                return new ApiResponse<Note> 
                { 
                    Success = false, 
                    Message = "Note title is required" 
                };
            }

            var note = new Note
            {
                Id = Guid.NewGuid(),
                Title = request.Title,
                Content = request.Content,
                UserId = userId,
                Category = request.Category,
                Tags = request.Tags,
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            };

            _context.Notes.Add(note);
            await _context.SaveChangesAsync();
            
            return new ApiResponse<Note> 
            { 
                Success = true, 
                Message = "Note created successfully",
                Data = note 
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating note for user {UserId}", userId);
            return new ApiResponse<Note> 
            { 
                Success = false, 
                Message = "Failed to create note" 
            };
        }
    }

    public async Task<ApiResponse<Note>> UpdateNoteAsync(Guid id, Guid userId, UpdateNoteRequest request)
    {
        try
        {
            var note = await _context.Notes
                .FirstOrDefaultAsync(n => n.Id == id && n.UserId == userId);

            if (note == null)
            {
                return new ApiResponse<Note> 
                { 
                    Success = false, 
                    Message = "Note not found" 
                };
            }

            // Basic validation using your request model
            if (string.IsNullOrWhiteSpace(request.Title))
            {
                return new ApiResponse<Note> 
                { 
                    Success = false, 
                    Message = "Note title is required" 
                };
            }

            note.Title = request.Title;
            note.Content = request.Content;
            note.Category = request.Category;
            note.Tags = request.Tags;
            note.UpdatedAt = DateTime.UtcNow;

            await _context.SaveChangesAsync();
            
            return new ApiResponse<Note> 
            { 
                Success = true, 
                Message = "Note updated successfully",
                Data = note 
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating note {NoteId}", id);
            return new ApiResponse<Note> 
            { 
                Success = false, 
                Message = "Failed to update note" 
            };
        }
    }

    public async Task<ApiResponse<bool>> DeleteNoteAsync(Guid id, Guid userId)
    {
        try
        {
            var note = await _context.Notes
                .FirstOrDefaultAsync(n => n.Id == id && n.UserId == userId);

            if (note == null)
            {
                return new ApiResponse<bool> 
                { 
                    Success = false, 
                    Message = "Note not found" 
                };
            }

            _context.Notes.Remove(note);
            await _context.SaveChangesAsync();
            
            return new ApiResponse<bool> 
            { 
                Success = true, 
                Message = "Note deleted successfully",
                Data = true 
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting note {NoteId}", id);
            return new ApiResponse<bool> 
            { 
                Success = false, 
                Message = "Failed to delete note" 
            };
        }
    }

    public async Task<ApiResponse<List<string>>> GetUserCategoriesAsync(Guid userId)
    {
        try
        {
            var categories = await _context.Notes
                .Where(n => n.UserId == userId)
                .Select(n => n.Category)
                .Distinct()
                .ToListAsync();

            return new ApiResponse<List<string>> 
            { 
                Success = true, 
                Message = "Categories retrieved successfully",
                Data = categories 
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving categories for user {UserId}", userId);
            return new ApiResponse<List<string>> 
            { 
                Success = false, 
                Message = "Failed to retrieve categories" 
            };
        }
    }

    public async Task<ApiResponse<List<string>>> GetUserTagsAsync(Guid userId)
    {
        try
        {
            var allTags = await _context.Notes
                .Where(n => n.UserId == userId)
                .SelectMany(n => n.Tags)
                .Distinct()
                .ToListAsync();
                
            return new ApiResponse<List<string>> 
            { 
                Success = true, 
                Message = "Tags retrieved successfully",
                Data = allTags 
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving tags for user {UserId}", userId);
            return new ApiResponse<List<string>> 
            { 
                Success = false, 
                Message = "Failed to retrieve tags" 
            };
        }
    }
}
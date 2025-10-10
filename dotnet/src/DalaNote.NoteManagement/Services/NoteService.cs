using Microsoft.EntityFrameworkCore;
using DalaNote.Data.Context;
using DalaNote.NoteManagement.Models.Entities;

public class NoteService : INoteService
{
    private readonly DalaNoteDbContext _context;

    public NoteService(DalaNoteDbContext context)
    {
        _context = context;
    }

    public async Task<List<Note>> GetUserNotesAsync(Guid userId)
    {
        return await _context.Notes
            .Where(n => n.UserId == userId)
            .OrderByDescending(n => n.UpdatedAt)
            .ToListAsync();
    }

    public async Task<Note?> GetNoteAsync(Guid id, Guid userId)
    {
        return await _context.Notes
            .FirstOrDefaultAsync(n => n.Id == id && n.UserId == userId);
    }

    public async Task<Note> CreateNoteAsync(Note note)
    {
        note.Id = Guid.NewGuid();
        note.CreatedAt = DateTime.UtcNow;
        note.UpdatedAt = DateTime.UtcNow;

        _context.Notes.Add(note);
        await _context.SaveChangesAsync();
        
        return note;
    }

    public async Task<Note?> UpdateNoteAsync(Guid id, Guid userId, UpdateNoteRequest request)
    {
        var note = await _context.Notes
            .FirstOrDefaultAsync(n => n.Id == id && n.UserId == userId);
            
        if (note == null) return null;

        note.Title = request.Title;
        note.Content = request.Content;
        note.Category = request.Category;
        note.Tags = request.Tags;
        note.UpdatedAt = DateTime.UtcNow;

        await _context.SaveChangesAsync();
        return note;
    }

    public async Task<bool> DeleteNoteAsync(Guid id, Guid userId)
    {
        var note = await _context.Notes
            .FirstOrDefaultAsync(n => n.Id == id && n.UserId == userId);
            
        if (note == null) return false;

        _context.Notes.Remove(note);
        await _context.SaveChangesAsync();
        return true;
    }

    public async Task<List<string>> GetUserCategoriesAsync(Guid userId)
    {
        return await _context.Notes
            .Where(n => n.UserId == userId)
            .Select(n => n.Category)
            .Distinct()
            .ToListAsync();
    }

    public async Task<List<string>> GetUserTagsAsync(Guid userId)
    {
        var allTags = await _context.Notes
            .Where(n => n.UserId == userId)
            .SelectMany(n => n.Tags)
            .Distinct()
            .ToListAsync();
            
        return allTags;
    }
}
using Microsoft.AspNetCore.Mvc;
using DalaNote.NoteManagement.Services;
using DalaNote.NoteManagement.Models.Entities;

namespace DalaNote.NoteManagement.Controllers;

[ApiController]
[Route("api/[controller]")]
public class NotesController : ControllerBase
{
    private readonly INoteService _noteService;

    public NotesController(INoteService noteService)
    {
        _noteService = noteService;
    }

    [HttpGet]
    public async Task<IActionResult> GetNotes()
    {
        var userId = GetUserId(); // Simple user ID for now
        var notes = await _noteService.GetUserNotesAsync(userId);
        return Ok(notes);
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetNote(Guid id)
    {
        var userId = GetUserId();
        var note = await _noteService.GetNoteAsync(id, userId);
        
        if (note == null) return NotFound();
        return Ok(note);
    }

    [HttpPost]
    public async Task<IActionResult> CreateNote([FromBody] CreateNoteRequest request)
    {
        var userId = GetUserId();
        
        var note = new Note
        {
            Title = request.Title,
            Content = request.Content,
            UserId = userId,
            Category = request.Category,
            Tags = request.Tags
        };

        var createdNote = await _noteService.CreateNoteAsync(note);
        return CreatedAtAction(nameof(GetNote), new { id = createdNote.Id }, createdNote);
    }

    [HttpPut("{id}")]
    public async Task<IActionResult> UpdateNote(Guid id, [FromBody] UpdateNoteRequest request)
    {
        var userId = GetUserId();
        var updatedNote = await _noteService.UpdateNoteAsync(id, userId, request);
        
        if (updatedNote == null) return NotFound();
        return Ok(updatedNote);
    }

    [HttpDelete("{id}")]
    public async Task<IActionResult> DeleteNote(Guid id)
    {
        var userId = GetUserId();
        var result = await _noteService.DeleteNoteAsync(id, userId);
        
        if (!result) return NotFound();
        return NoContent();
    }

    [HttpGet("categories")]
    public async Task<IActionResult> GetCategories()
    {
        var userId = GetUserId();
        var categories = await _noteService.GetUserCategoriesAsync(userId);
        return Ok(categories);
    }

    [HttpGet("tags")]
    public async Task<IActionResult> GetTags()
    {
        var userId = GetUserId();
        var tags = await _noteService.GetUserTagsAsync(userId);
        return Ok(tags);
    }

    // Simple user ID - replace with JWT authentication later
    private Guid GetUserId()
    {
        return Guid.Parse("a1b2c3d4-1234-5678-9101-abcdef123456");
    }
}
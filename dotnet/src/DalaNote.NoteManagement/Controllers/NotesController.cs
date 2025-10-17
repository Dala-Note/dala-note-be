using DalaNote.NoteManagement.Services;
using DalaNote.Common.Models;
namespace DalaNote.NoteManagement.Controllers;
using Microsoft.AspNetCore.Mvc;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

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
    public async Task<ActionResult<ApiResponse<List<Note>>>> GetNotes()
    {
        var userId = GetUserId();
        var result = await _noteService.GetUserNotesAsync(userId);
        return Ok(result);
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<ApiResponse<Note>>> GetNote(Guid id)
    {
        var userId = GetUserId();
        var result = await _noteService.GetNoteAsync(id, userId);
        
        if (!result.Success)
            return NotFound(result);
            
        return Ok(result);
    }

    [HttpPost]
    public async Task<ActionResult<ApiResponse<Note>>> CreateNote([FromBody] CreateNoteRequest request)
    {
        var userId = GetUserId();
        var result = await _noteService.CreateNoteAsync(request, userId); // Pass request directly
        
        if (result.Success)
            return CreatedAtAction(nameof(GetNote), new { id = result.Data!.Id }, result);
        
        return BadRequest(result);
    }

    [HttpPut("{id}")]
    public async Task<ActionResult<ApiResponse<Note>>> UpdateNote(Guid id, [FromBody] UpdateNoteRequest request)
    {
        var userId = GetUserId();
        var result = await _noteService.UpdateNoteAsync(id, userId, request);
        
        if (!result.Success)
            return BadRequest(result);
            
        return Ok(result);
    }

    [HttpDelete("{id}")]
    public async Task<ActionResult<ApiResponse<bool>>> DeleteNote(Guid id)
    {
        var userId = GetUserId();
        var result = await _noteService.DeleteNoteAsync(id, userId);
        
        if (!result.Success)
            return BadRequest(result);
            
        return NoContent();
    }

    [HttpGet("categories")]
    public async Task<ActionResult<ApiResponse<List<string>>>> GetCategories()
    {
        var userId = GetUserId();
        var result = await _noteService.GetUserCategoriesAsync(userId);
        return Ok(result);
    }

    [HttpGet("tags")]
    public async Task<ActionResult<ApiResponse<List<string>>>> GetTags()
    {
        var userId = GetUserId();
        var result = await _noteService.GetUserTagsAsync(userId);
        return Ok(result);
    }

    // Simple user ID, replace with JWT authentication later
    private Guid GetUserId()
    {
        return Guid.Parse("a1b2c3d4-1234-5678-9101-abcdef123456");
    }
}
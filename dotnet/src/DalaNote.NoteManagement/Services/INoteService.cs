using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using DalaNote.Common.Models;

public interface INoteService
{
    Task<ApiResponse<List<Note>>> GetUserNotesAsync(Guid userId);
    Task<ApiResponse<Note>> GetNoteAsync(Guid id, Guid userId);
    Task<ApiResponse<Note>> CreateNoteAsync(CreateNoteRequest request, Guid userId); 
    Task<ApiResponse<Note>> UpdateNoteAsync(Guid id, Guid userId, UpdateNoteRequest request);
    Task<ApiResponse<bool>> DeleteNoteAsync(Guid id, Guid userId);
    Task<ApiResponse<List<string>>> GetUserCategoriesAsync(Guid userId);
    Task<ApiResponse<List<string>>> GetUserTagsAsync(Guid userId);
}
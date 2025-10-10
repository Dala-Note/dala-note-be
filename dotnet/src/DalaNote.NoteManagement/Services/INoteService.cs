public interface INoteService
{
    Task<List<Note>> GetUserNotesAsync(Guid userId);
    Task<Note?> GetNoteAsync(Guid id, Guid userId);
    Task<Note> CreateNoteAsync(Note note);
    Task<Note?> UpdateNoteAsync(Guid id, Guid userId, UpdateNoteRequest request);
    Task<bool> DeleteNoteAsync(Guid id, Guid userId);
    Task<List<string>> GetUserCategoriesAsync(Guid userId);
    Task<List<string>> GetUserTagsAsync(Guid userId);
}
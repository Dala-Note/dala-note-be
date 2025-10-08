namespace DalaNote.NoteManagement.Models.Entities;

public class Note
{
    public Guid Id { get; set; }
    public string Title { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
    public string? Summary { get; set; }
    public Guid AuthorId { get; set; }
    public Guid WorkspaceId { get; set; }
    public Guid? FolderId { get; set; }
    public NoteStatus Status { get; set; } = NoteStatus.Draft;
    public bool IsPublic { get; set; } = false;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? DeletedAt { get; set; }
}
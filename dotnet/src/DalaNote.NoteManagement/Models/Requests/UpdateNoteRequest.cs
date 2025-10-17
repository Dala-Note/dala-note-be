using System.Collections.Generic;

public class UpdateNoteRequest
{
    public string Title { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
    public string Category { get; set; } = "General";
    public List<string> Tags { get; set; } = new List<string>();
}
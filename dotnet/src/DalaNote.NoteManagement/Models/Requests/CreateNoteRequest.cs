using System.Collections.Generic;

public class CreateNoteRequest
{
    public string Title { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
    public string Category { get; set; } = "General";
    public List<string> Tags { get; set; } = new List<string>();
}
using DalaNote.Data.Context;

namespace DalaNote.Data.Context;

public class DalaNoteDbContext : DalaNoteDbContext
{
    public DalaNoteDbContext(DbContextOptions<DalaNoteDbContext> options) : base(options) { }

     public DbSet<Note> Notes => Set<Note>();

}
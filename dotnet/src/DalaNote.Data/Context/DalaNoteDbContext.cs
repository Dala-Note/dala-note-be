using Microsoft.EntityFrameworkCore;
using DalaNote.Common.Models;
using System;
using System.Linq;

namespace DalaNote.Data.Context;

public class DalaNoteDbContext : DbContext
{
    public DalaNoteDbContext(DbContextOptions<DalaNoteDbContext> options) : base(options) { }

    public DbSet<Note> Notes => Set<Note>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Note>(entity =>
        {
            entity.HasKey(n => n.Id);
            entity.Property(n => n.Title).IsRequired().HasMaxLength(200);
            entity.Property(n => n.Content).HasColumnType("text");
            entity.Property(n => n.Tags).HasConversion(
                v => string.Join(',', v),
                v => v.Split(',', StringSplitOptions.RemoveEmptyEntries).ToList()
            );
        });
    }

}
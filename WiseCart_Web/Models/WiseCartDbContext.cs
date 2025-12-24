using System;
using System.Collections.Generic;
using Microsoft.EntityFrameworkCore;

namespace WiseCart_Web.Models;

public partial class WiseCartDbContext : DbContext
{
    public WiseCartDbContext()
    {
    }

    public WiseCartDbContext(DbContextOptions<WiseCartDbContext> options)
        : base(options)
    {
    }

    public virtual DbSet<Brand> Brands { get; set; }

    public virtual DbSet<Category> Categories { get; set; }

    public virtual DbSet<Favorite> Favorites { get; set; }

    public virtual DbSet<PriceHistory> PriceHistories { get; set; }

    public virtual DbSet<Product> Products { get; set; }

    public virtual DbSet<Role> Roles { get; set; }

    public virtual DbSet<SystemLog> SystemLogs { get; set; }

    public virtual DbSet<User> Users { get; set; }

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
        // Connection string appsettings.json'dan okunur, burada fallback yok
        // Sadece uyarıyı kaldırdık
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Brand>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PK__Brands__3214EC075D987F80");

            entity.Property(e => e.Name)
                .HasMaxLength(100)
                .IsUnicode(false);
        });

        modelBuilder.Entity<Category>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PK__Categori__3214EC071309C56F");

            entity.Property(e => e.Name)
                .HasMaxLength(100)
                .IsUnicode(false);
        });

        modelBuilder.Entity<PriceHistory>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PK__PriceHis__3214EC07466B2098");

            entity.ToTable("PriceHistory");

            entity.Property(e => e.Date).HasColumnType("datetime");

            // 📊 FOREIGN KEY İLİŞKİSİ: PriceHistory -> Product (Veri Bütünlüğü)
            // Bir fiyat geçmişi kaydı mutlaka bir ürüne ait olmalıdır
            entity.HasOne(d => d.Product).WithMany(p => p.PriceHistories)
                .HasForeignKey(d => d.ProductId)
                .HasConstraintName("FK__PriceHist__Produ__45F365D3");
        });

        modelBuilder.Entity<Product>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PK__Products__3214EC07A2BBE22D");

            entity.Property(e => e.ImageUrl)
                .HasMaxLength(1000)
                .IsUnicode(false);
            entity.Property(e => e.Model)
                .HasMaxLength(255)
                .IsUnicode(false);
            entity.Property(e => e.Name)
                .HasMaxLength(500)
                .IsUnicode(false);
            entity.Property(e => e.Url)
                .HasMaxLength(1000)
                .IsUnicode(false);
            
            // 📊 SOFT DELETE: IsDeleted kolonu (Varsayılan: false)
            entity.Property(e => e.IsDeleted)
                .HasDefaultValue(false);
            
            // 📊 SOFT DELETE: DeletedAt kolonu (Nullable - sadece silinen ürünlerde dolu)
            entity.Property(e => e.DeletedAt)
                .HasColumnType("datetime");

            // 📊 FOREIGN KEY İLİŞKİSİ: Product -> Brand (Normalizasyon: Marka bilgisi ayrı tabloda)
            // Bir ürün mutlaka bir markaya ait olmalıdır (Veri Bütünlüğü)
            entity.HasOne(d => d.Brand).WithMany(p => p.Products)
                .HasForeignKey(d => d.BrandId)
                .HasConstraintName("FK__Products__BrandI__4316F928");

            // 📊 FOREIGN KEY İLİŞKİSİ: Product -> Category (Normalizasyon: Kategori bilgisi ayrı tabloda)
            // Bir ürün mutlaka bir kategoriye ait olmalıdır (Veri Bütünlüğü)
            entity.HasOne(d => d.Category).WithMany(p => p.Products)
                .HasForeignKey(d => d.CategoryId)
                .HasConstraintName("FK__Products__Catego__4222D4EF");
        });

        modelBuilder.Entity<Role>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PK__Roles__3214EC0799859803");

            entity.Property(e => e.Name)
                .HasMaxLength(50)
                .IsUnicode(false);
        });

        modelBuilder.Entity<SystemLog>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PK__SystemLo__3214EC07D91DB8A2");

            entity.Property(e => e.Date).HasColumnType("datetime");
            entity.Property(e => e.Level)
                .HasMaxLength(50)
                .IsUnicode(false);
            entity.Property(e => e.Message).IsUnicode(false);
        });

        modelBuilder.Entity<Favorite>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PK__Favorit__3214EC07");

            entity.ToTable("Favorites");

            entity.Property(e => e.CreatedAt).HasColumnType("datetime");

            // 📊 FOREIGN KEY İLİŞKİSİ: Favorite -> User (Veri Bütünlüğü)
            // Cascade Delete: Kullanıcı silinirse favorileri de silinir
            entity.HasOne(d => d.User).WithMany()
                .HasForeignKey(d => d.UserId)
                .OnDelete(DeleteBehavior.Cascade)
                .HasConstraintName("FK__Favorites__User");

            // 📊 FOREIGN KEY İLİŞKİSİ: Favorite -> Product (Veri Bütünlüğü)
            // Cascade Delete: Ürün silinirse favorilerden de silinir
            entity.HasOne(d => d.Product).WithMany()
                .HasForeignKey(d => d.ProductId)
                .OnDelete(DeleteBehavior.Cascade)
                .HasConstraintName("FK__Favorites__Product");

            // 📊 INDEX: UNIQUE INDEX - Aynı kullanıcı aynı ürünü iki kez favorilere ekleyemez
            //  (Veri Bütünlüğü + Performans)
            // Composite index: UserId ve ProductId birlikte unique olmalı
            entity.HasIndex(e => new { e.UserId, e.ProductId }).IsUnique();
        });

        modelBuilder.Entity<User>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PK__Users__3214EC074654659C");

            entity.Property(e => e.CreatedAt).HasColumnType("datetime");
            entity.Property(e => e.Email)
                .HasMaxLength(100)
                .IsUnicode(false);
            entity.Property(e => e.PasswordHash)
                .HasMaxLength(255)
                .IsUnicode(false);
            entity.Property(e => e.Username)
                .HasMaxLength(50)
                .IsUnicode(false);

            // ProfileImagePath kolonunu ignore et (profil resmi kullanılmıyor)
            // Entity Framework'ün veritabanındaki fazladan kolonları görmezden gelmesi için
            // Model'de tanımlı olmayan kolonlar otomatik olarak ignore edilir
            // Eğer veritabanında ProfileImagePath varsa, Entity Framework bunu görmezden gelir

            // 📊 FOREIGN KEY İLİŞKİSİ: User -> Role (Normalizasyon: Rol bilgisi ayrı tabloda)
            // Bir kullanıcı bir role sahip olabilir (Veri Bütünlüğü)
            entity.HasOne(d => d.Role).WithMany(p => p.Users)
                .HasForeignKey(d => d.RoleId)
                .HasConstraintName("FK__Users__RoleId__3F466844");
        });

        OnModelCreatingPartial(modelBuilder);
    }

    partial void OnModelCreatingPartial(ModelBuilder modelBuilder);
}

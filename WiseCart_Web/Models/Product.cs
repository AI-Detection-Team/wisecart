using System;
using System.Collections.Generic;

namespace WiseCart_Web.Models;

public partial class Product
{
    public int Id { get; set; }

    public string Name { get; set; } = null!;

    public string? Model { get; set; }

    public double? CurrentPrice { get; set; }

    public int? ReviewCount { get; set; }

    public string? Url { get; set; }

    public string? ImageUrl { get; set; }

    // 📊 NORMALİZASYON: Foreign Key - Kategori bilgisi ayrı tabloda (Categories)
    public int? CategoryId { get; set; }

    // 📊 NORMALİZASYON: Foreign Key - Marka bilgisi ayrı tabloda (Brands)
    public int? BrandId { get; set; }

    // 📊 SOFT DELETE: Ürün silindi mi? (Veritabanında kalır ama listede görünmez)
    public bool IsDeleted { get; set; } = false;

    // 📊 SOFT DELETE: Ürün ne zaman silindi?
    public DateTime? DeletedAt { get; set; }

    // 📊 FOREIGN KEY İLİŞKİSİ: Navigation Property - Product -> Brand (1-N ilişki)
    public virtual Brand? Brand { get; set; }

    // 📊 FOREIGN KEY İLİŞKİSİ: Navigation Property - Product -> Category (1-N ilişki)
    public virtual Category? Category { get; set; }

    // 📊 FOREIGN KEY İLİŞKİSİ: Navigation Property - Product -> PriceHistory (1-N ilişki)
    public virtual ICollection<PriceHistory> PriceHistories { get; set; } = new List<PriceHistory>();
}

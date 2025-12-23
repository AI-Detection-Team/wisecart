using System;
using System.Collections.Generic;

namespace WiseCart_Web.Models;

public partial class PriceHistory
{
    public int Id { get; set; }

    public double Price { get; set; }

    public DateTime? Date { get; set; }

    // 📊 NORMALİZASYON: Foreign Key - Ürün bilgisi ayrı tabloda (Products)
    public int? ProductId { get; set; }

    // 📊 FOREIGN KEY İLİŞKİSİ: Navigation Property - PriceHistory -> Product (N-1 ilişki)
    public virtual Product? Product { get; set; }
}

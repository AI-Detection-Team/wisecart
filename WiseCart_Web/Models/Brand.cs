using System;
using System.Collections.Generic;

namespace WiseCart_Web.Models;

public partial class Brand
{
    public int Id { get; set; }

    public string Name { get; set; } = null!;

    // 📊 FOREIGN KEY İLİŞKİSİ: Navigation Property - Brand -> Products (1-N ilişki)
    // Normalizasyon: Bir markanın birden fazla ürünü olabilir
    public virtual ICollection<Product> Products { get; set; } = new List<Product>();
}

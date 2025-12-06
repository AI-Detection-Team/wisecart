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

    public int? CategoryId { get; set; }

    public int? BrandId { get; set; }

    public virtual Brand? Brand { get; set; }

    public virtual Category? Category { get; set; }

    public virtual ICollection<PriceHistory> PriceHistories { get; set; } = new List<PriceHistory>();
}

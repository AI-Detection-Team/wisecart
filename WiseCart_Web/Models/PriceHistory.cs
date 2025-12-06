using System;
using System.Collections.Generic;

namespace WiseCart_Web.Models;

public partial class PriceHistory
{
    public int Id { get; set; }

    public double Price { get; set; }

    public DateTime? Date { get; set; }

    public int? ProductId { get; set; }

    public virtual Product? Product { get; set; }
}

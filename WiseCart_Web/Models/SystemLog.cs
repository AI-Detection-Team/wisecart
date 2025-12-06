using System;
using System.Collections.Generic;

namespace WiseCart_Web.Models;

public partial class SystemLog
{
    public int Id { get; set; }

    public string? Level { get; set; }

    public string? Message { get; set; }

    public DateTime? Date { get; set; }
}

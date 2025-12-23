using System;
using System.Collections.Generic;

namespace WiseCart_Web.Models;

public partial class User
{
    public int Id { get; set; }

    public string Username { get; set; } = null!;

    public string Email { get; set; } = null!;

    public string PasswordHash { get; set; } = null!;

    // 📊 NORMALİZASYON: Foreign Key - Rol bilgisi ayrı tabloda (Roles)
    public int? RoleId { get; set; }

    public DateTime? CreatedAt { get; set; }

    // 📊 FOREIGN KEY İLİŞKİSİ: Navigation Property - User -> Role (N-1 ilişki)
    public virtual Role? Role { get; set; }
}

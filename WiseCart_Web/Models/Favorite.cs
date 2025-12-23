using System;

namespace WiseCart_Web.Models;

public partial class Favorite
{
    public int Id { get; set; }

    // 📊 NORMALİZASYON: Foreign Key - Kullanıcı bilgisi ayrı tabloda (Users)
    public int UserId { get; set; }

    // 📊 NORMALİZASYON: Foreign Key - Ürün bilgisi ayrı tabloda (Products)
    public int ProductId { get; set; }

    public DateTime CreatedAt { get; set; }

    // 📊 FOREIGN KEY İLİŞKİSİ: Navigation Property - Favorite -> Product (N-1 ilişki)
    public virtual Product Product { get; set; } = null!;

    // 📊 FOREIGN KEY İLİŞKİSİ: Navigation Property - Favorite -> User (N-1 ilişki)
    public virtual User User { get; set; } = null!;
}







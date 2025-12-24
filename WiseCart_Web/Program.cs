using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.EntityFrameworkCore;
using WiseCart_Web.Models; // Kendi proje isminle aynı olmalı
using WiseCart_Web.Services; // OLAP Analytics Service için

var builder = WebApplication.CreateBuilder(args);

// --- 1. VERİTABANI BAĞLANTISI (EKLENEN KISIM) ---
// appsettings.json dosyasındaki "DefaultConnection" ismini okur.
builder.Services.AddDbContext<WiseCartDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));

// OLAP Analytics Service ekle
builder.Services.AddScoped<OlapAnalyticsService>();

// MVC Servislerini Ekle
builder.Services.AddControllersWithViews();
// 📋 İSTER 6: Kullanıcı Tipleri - Authentication yapılandırması (Rol bazlı erişim için)
// Authentication Servisini Ekle
builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie(options =>
    {
        options.LoginPath = "/Account/Login";
        options.AccessDeniedPath = "/Account/AccessDenied";
    });
var app = builder.Build();

// Hata Ayıklama (Development) Modu
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();

app.UseRouting();
app.UseAuthentication();
app.UseAuthorization();

// Varsayılan Rota (Ana Sayfa)
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

app.Run();
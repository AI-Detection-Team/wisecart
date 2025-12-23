using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using Microsoft.EntityFrameworkCore;
using WiseCart_Web.Models;
using WiseCart_Web.Models.ViewModels;

namespace WiseCart_Web.Controllers
{
    // 📋 İSTER 1: Controller - AccountController
    public class AccountController : Controller
    {
        private readonly WiseCartDbContext _context;

        public AccountController(WiseCartDbContext context)
        {
            _context = context;
        }

        // 📋 İSTER 1: Action - Login (GET)
        // --- GİRİŞ YAP (LOGIN) ---
        public IActionResult Login()
        {
            return View();
        }

        // 📋 İSTER 1: Action - Login (POST)
        [HttpPost]
        public async Task<IActionResult> Login(LoginModel model)
        {
            if (ModelState.IsValid)
            {
                // Şifreyi Hashle (Veritabanındaki formatla eşleşmeli)
                string hashedPassword = MD5Hash(model.Password);

                // 📊 PERFORMANS: Eager Loading (Include) - Role bilgisini tek sorguda çek
                // N+1 sorgu problemini önler, kullanıcı ve rol bilgisini birlikte yükler
                var user = await _context.Users
                    .Include(u => u.Role) 
                    .FirstOrDefaultAsync(u => u.Username == model.Username && u.PasswordHash == hashedPassword);

                if (user != null)
                {
                    // 📋 İSTER 6: Kullanıcı Tipleri - Rol bilgisi claim olarak ekleniyor (Admin/User ayrımı için)
                    // Rol adını al (Eğer boşsa 'User' varsay)
                    string roleName = user.Role?.Name ?? "User";

                    var claims = new List<Claim>
                    {
                        new Claim(ClaimTypes.Name, user.Username),
                        new Claim(ClaimTypes.Role, roleName),
                        new Claim("UserId", user.Id.ToString())
                    };

                    var claimsIdentity = new ClaimsIdentity(claims, CookieAuthenticationDefaults.AuthenticationScheme);
                    await HttpContext.SignInAsync(CookieAuthenticationDefaults.AuthenticationScheme, new ClaimsPrincipal(claimsIdentity));

                    return RedirectToAction("Index", "Home");
                }

                ModelState.AddModelError("", "Kullanıcı adı veya şifre hatalı.");
            }
            return View(model);
        }

        // 📋 İSTER 1: Action - Register (GET)
        // --- KAYIT OL (REGISTER) ---
        public IActionResult Register()
        {
            return View();
        }

        // 📋 İSTER 1: Action - Register (POST)
        [HttpPost]
        public async Task<IActionResult> Register(RegisterModel model)
        {
            if (ModelState.IsValid)
            {
                // 📊 PERFORMANS: AnyAsync() - Sadece varlık kontrolü yapar (tüm kaydı çekmez)
                // Count() yerine Any() kullanmak daha performanslıdır
                if (await _context.Users.AnyAsync(u => u.Username == model.Username))
                {
                    ModelState.AddModelError("", "Bu kullanıcı adı zaten alınmış.");
                    return View(model);
                }

                // 'User' rolünün ID'sini bul
                var userRole = await _context.Roles.FirstOrDefaultAsync(r => r.Name == "User");
                if (userRole == null)
                {
                    // Eğer veritabanında 'User' rolü yoksa hata vermesin, oluştursun
                    userRole = new Role { Name = "User" };
                    _context.Roles.Add(userRole);
                    await _context.SaveChangesAsync();
                }

                // Yeni Kullanıcıyı Oluştur
                var newUser = new User
                {
                    Username = model.Username,
                    Email = model.Email,
                    PasswordHash = MD5Hash(model.Password),
                    RoleId = userRole.Id, // Rol ID'sini atıyoruz (String değil!)
                    CreatedAt = DateTime.Now
                };

                _context.Users.Add(newUser);
                await _context.SaveChangesAsync();

                return RedirectToAction("Login");
            }
            return View(model);
        }

        // 📋 İSTER 1: Action - Logout
        public async Task<IActionResult> Logout()
        {
            await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
            return RedirectToAction("Index", "Home");
        }

        // 📋 İSTER 1: Action - AccessDenied
        // --- ERİŞİM REDDEDİLDİ (ACCESS DENIED) ---
        public IActionResult AccessDenied()
        {
            return View();
        }

        // Basit MD5 Hash Fonksiyonu
        private string MD5Hash(string input)
        {
            using (var md5 = MD5.Create())
            {
                var result = md5.ComputeHash(Encoding.ASCII.GetBytes(input));
                return string.Join("", result.Select(x => x.ToString("x2")));
            }
        }
    }
}
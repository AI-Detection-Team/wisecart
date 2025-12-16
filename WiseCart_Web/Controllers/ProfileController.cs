using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using Microsoft.EntityFrameworkCore;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using WiseCart_Web.Models;

namespace WiseCart_Web.Controllers
{
    [Authorize]
    public class ProfileController : Controller
    {
        private readonly WiseCartDbContext _context;

        public ProfileController(WiseCartDbContext context)
        {
            _context = context;
        }

        // GET: Profile
        public async Task<IActionResult> Index()
        {
            var userIdClaim = User.FindFirst("UserId");
            if (userIdClaim == null || !int.TryParse(userIdClaim.Value, out int userId))
            {
                return RedirectToAction("Login", "Account");
            }

            var user = await _context.Users
                .Include(u => u.Role)
                .FirstOrDefaultAsync(u => u.Id == userId);

            if (user == null)
            {
                return NotFound();
            }

            // Favori sayısını hesapla
            var favoriteCount = await _context.Favorites
                .Where(f => f.UserId == userId)
                .CountAsync();

            // Üyelik gün sayısını hesapla
            int membershipDays = 0;
            if (user.CreatedAt.HasValue)
            {
                membershipDays = (DateTime.Now - user.CreatedAt.Value).Days;
            }

            ViewBag.FavoriteCount = favoriteCount;
            ViewBag.MembershipDays = membershipDays;

            return View(user);
        }

        // GET: Profile/Settings
        public async Task<IActionResult> Settings()
        {
            var userIdClaim = User.FindFirst("UserId");
            if (userIdClaim == null || !int.TryParse(userIdClaim.Value, out int userId))
            {
                return RedirectToAction("Login", "Account");
            }

            var user = await _context.Users
                .Include(u => u.Role)
                .FirstOrDefaultAsync(u => u.Id == userId);

            if (user == null)
            {
                return NotFound();
            }

            return View(user);
        }

        // POST: Profile/UpdateProfile
        [HttpPost]
        public async Task<IActionResult> UpdateProfile([FromBody] UpdateProfileModel model)
        {
            var userIdClaim = User.FindFirst("UserId");
            if (userIdClaim == null || !int.TryParse(userIdClaim.Value, out int userId))
            {
                return Json(new { success = false, message = "Kullanıcı bulunamadı." });
            }

            var user = await _context.Users.FindAsync(userId);
            if (user == null)
            {
                return Json(new { success = false, message = "Kullanıcı bulunamadı." });
            }

            // Kullanıcı adı kontrolü
            if (!string.IsNullOrEmpty(model.Username) && model.Username != user.Username)
            {
                if (await _context.Users.AnyAsync(u => u.Username == model.Username && u.Id != userId))
                {
                    return Json(new { success = false, message = "Bu kullanıcı adı zaten kullanılıyor." });
                }
                user.Username = model.Username;
            }

            // Email kontrolü
            if (!string.IsNullOrEmpty(model.Email) && model.Email != user.Email)
            {
                if (await _context.Users.AnyAsync(u => u.Email == model.Email && u.Id != userId))
                {
                    return Json(new { success = false, message = "Bu email zaten kullanılıyor." });
                }
                user.Email = model.Email;
            }

            await _context.SaveChangesAsync();
            return Json(new { success = true, message = "Profil bilgileri güncellendi." });
        }

        // POST: Profile/ChangePassword
        [HttpPost]
        public async Task<IActionResult> ChangePassword([FromBody] ChangePasswordModel model)
        {
            var userIdClaim = User.FindFirst("UserId");
            if (userIdClaim == null || !int.TryParse(userIdClaim.Value, out int userId))
            {
                return Json(new { success = false, message = "Kullanıcı bulunamadı." });
            }

            var user = await _context.Users.FindAsync(userId);
            if (user == null)
            {
                return Json(new { success = false, message = "Kullanıcı bulunamadı." });
            }

            // Mevcut şifre kontrolü
            string currentHash = MD5Hash(model.CurrentPassword);
            if (user.PasswordHash != currentHash)
            {
                return Json(new { success = false, message = "Mevcut şifre yanlış." });
            }

            // Yeni şifre kontrolü
            if (string.IsNullOrEmpty(model.NewPassword) || model.NewPassword.Length < 4)
            {
                return Json(new { success = false, message = "Yeni şifre en az 4 karakter olmalıdır." });
            }

            user.PasswordHash = MD5Hash(model.NewPassword);
            await _context.SaveChangesAsync();

            return Json(new { success = true, message = "Şifre başarıyla değiştirildi." });
        }

        // GET: Profile/Favorites
        public async Task<IActionResult> Favorites()
        {
            var userIdClaim = User.FindFirst("UserId");
            if (userIdClaim == null || !int.TryParse(userIdClaim.Value, out int userId))
            {
                return RedirectToAction("Login", "Account");
            }

            var favorites = await _context.Favorites
                .Include(f => f.Product)
                    .ThenInclude(p => p.Brand)
                .Include(f => f.Product)
                    .ThenInclude(p => p.Category)
                .Where(f => f.UserId == userId)
                .OrderByDescending(f => f.CreatedAt)
                .ToListAsync();

            return View(favorites);
        }

        private string MD5Hash(string input)
        {
            using (var md5 = MD5.Create())
            {
                var result = md5.ComputeHash(Encoding.ASCII.GetBytes(input));
                return string.Join("", result.Select(x => x.ToString("x2")));
            }
        }
    }

    public class UpdateProfileModel
    {
        public string? Username { get; set; }
        public string? Email { get; set; }
    }

    public class ChangePasswordModel
    {
        public string CurrentPassword { get; set; } = string.Empty;
        public string NewPassword { get; set; } = string.Empty;
    }
}

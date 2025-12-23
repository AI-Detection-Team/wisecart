using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using Microsoft.EntityFrameworkCore;
using System.Security.Claims;
using WiseCart_Web.Models;

namespace WiseCart_Web.Controllers
{
    // 📋 İSTER 1: Controller - FavoritesController (API Controller)
    [Authorize]
    [ApiController]
    [Route("api/[controller]")]
    public class FavoritesController : ControllerBase
    {
        private readonly WiseCartDbContext _context;

        public FavoritesController(WiseCartDbContext context)
        {
            _context = context;
        }

        // 📋 İSTER 1: Action - ToggleFavorite
        // POST: api/Favorites/Toggle
        [HttpPost("Toggle")]
        public async Task<IActionResult> ToggleFavorite([FromBody] int productId)
        {
            var userIdClaim = User.FindFirst("UserId");
            if (userIdClaim == null || !int.TryParse(userIdClaim.Value, out int userId))
            {
                return Unauthorized();
            }

            // 📊 PERFORMANS: FirstOrDefaultAsync() - Sadece ilk eşleşen kaydı çeker (tüm listeyi değil)
            var existingFavorite = await _context.Favorites
                .FirstOrDefaultAsync(f => f.UserId == userId && f.ProductId == productId);

            if (existingFavorite != null)
            {
                // Favoriden çıkar
                _context.Favorites.Remove(existingFavorite);
                await _context.SaveChangesAsync();
                return Ok(new { isFavorite = false, message = "Favorilerden çıkarıldı" });
            }
            else
            {
                // Favorilere ekle
                var favorite = new Favorite
                {
                    UserId = userId,
                    ProductId = productId,
                    CreatedAt = DateTime.Now
                };
                _context.Favorites.Add(favorite);
                await _context.SaveChangesAsync();
                return Ok(new { isFavorite = true, message = "Favorilere eklendi" });
            }
        }

        // 📋 İSTER 1: Action - CheckFavorite
        // GET: api/Favorites/Check/{productId}
        [HttpGet("Check/{productId}")]
        public async Task<IActionResult> CheckFavorite(int productId)
        {
            var userIdClaim = User.FindFirst("UserId");
            if (userIdClaim == null || !int.TryParse(userIdClaim.Value, out int userId))
            {
                return Ok(new { isFavorite = false });
            }

            // 📊 PERFORMANS: AnyAsync() - Sadece varlık kontrolü yapar (tüm kaydı çekmez)
            // Count() yerine Any() kullanmak daha performanslıdır
            var isFavorite = await _context.Favorites
                .AnyAsync(f => f.UserId == userId && f.ProductId == productId);

            return Ok(new { isFavorite });
        }
    }
}







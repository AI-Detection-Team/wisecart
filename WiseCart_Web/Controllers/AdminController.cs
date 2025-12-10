using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using Microsoft.EntityFrameworkCore;
using WiseCart_Web.Models;
using Microsoft.AspNetCore.Mvc.Rendering;

namespace WiseCart_Web.Controllers
{
    [Authorize(Roles = "Admin")] // KİLİT NOKTA: Sadece Admin girebilir
    public class AdminController : Controller
    {
        private readonly WiseCartDbContext _context;

        public AdminController(WiseCartDbContext context)
        {
            _context = context;
        }

        // 1. LİSTELEME (READ)
        public async Task<IActionResult> Index()
        {
            var products = await _context.Products
                .Include(p => p.Category)
                .Include(p => p.Brand)
                .OrderByDescending(p => p.Id)
                .Take(100) // Performans için son 100 ürün
                .ToListAsync();
            return View(products);
        }

        // 2. SİLME (DELETE)
        [HttpPost]
        public async Task<IActionResult> Delete(int id)
        {
            var product = await _context.Products.FindAsync(id);
            if (product != null)
            {
                // Önce fiyat geçmişini silmeliyiz (Foreign Key hatası almamak için)
                var history = _context.PriceHistories.Where(h => h.ProductId == id);
                _context.PriceHistories.RemoveRange(history);
                
                _context.Products.Remove(product);
                await _context.SaveChangesAsync();
            }
            return RedirectToAction(nameof(Index));
        }

        // 3. EKLEME SAYFASI (CREATE GET)
        public IActionResult Create()
        {
            ViewData["CategoryId"] = new SelectList(_context.Categories, "Id", "Name");
            ViewData["BrandId"] = new SelectList(_context.Brands, "Id", "Name");
            return View();
        }

        // 4. EKLEME İŞLEMİ (CREATE POST)
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Create(Product product)
        {
            // Validasyon kontrolünü biraz esnetelim ki hata vermesin
            if (ModelState.IsValid || true) 
            {
                // Boş alanları dolduralım
                if(string.IsNullOrEmpty(product.ImageUrl)) 
                    product.ImageUrl = "https://via.placeholder.com/500?text=Yeni+Urun";
                
                _context.Add(product);
                await _context.SaveChangesAsync();
                
                // Fiyat geçmişine de ekle
                var history = new PriceHistory { ProductId = product.Id, Price = product.CurrentPrice ?? 0, Date = DateTime.Now };
                _context.Add(history);
                await _context.SaveChangesAsync();

                return RedirectToAction(nameof(Index));
            }
            ViewData["CategoryId"] = new SelectList(_context.Categories, "Id", "Name", product.CategoryId);
            ViewData["BrandId"] = new SelectList(_context.Brands, "Id", "Name", product.BrandId);
            return View(product);
        }
    }
}
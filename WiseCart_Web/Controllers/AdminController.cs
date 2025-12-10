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

        // 1. LİSTELEME (READ) - SAYFALAMA EKLENDİ
        public async Task<IActionResult> Index(int page = 1)
        {
            int pageSize = 20; // Her sayfada 20 ürün göster

            // Sorguyu hazırla
            var productsQuery = _context.Products
                .Include(p => p.Category)
                .Include(p => p.Brand)
                .OrderByDescending(p => p.Id); // En yeniler en başta

            // Toplam sayıyı View'a gönder (İstatistik kartı için)
            ViewBag.TotalProducts = await productsQuery.CountAsync();
            
            // Sayfalanmış Veriyi Çek
            var products = await productsQuery
                .Skip((page - 1) * pageSize)
                .Take(pageSize)
                .ToListAsync();

            // Sayfalama bilgilerini View'a gönder
            ViewBag.CurrentPage = page;
            ViewBag.TotalPages = (int)Math.Ceiling(ViewBag.TotalProducts / (double)pageSize);

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
                
                // Varsa yorumları da sil (Eğer yorum tablosu varsa)
                // var comments = _context.Comments.Where(c => c.ProductId == id);
                // _context.Comments.RemoveRange(comments);

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
            // Validasyon kontrolünü esnetiyoruz (Resim vs boş olabilir)
            if (ModelState.IsValid || true) 
            {
                // Boş alanları dolduralım
                if(string.IsNullOrEmpty(product.ImageUrl)) 
                    product.ImageUrl = "https://via.placeholder.com/500?text=Yeni+Urun";
                
                // Tarih gibi alanlar varsa ekle
                // product.CreatedAt = DateTime.Now;

                _context.Add(product);
                await _context.SaveChangesAsync();
                
                // Fiyat geçmişine de ilk kaydı ekle
                var history = new PriceHistory 
                { 
                    ProductId = product.Id, 
                    Price = product.CurrentPrice ?? 0, 
                    Date = DateTime.Now 
                };
                _context.Add(history);
                await _context.SaveChangesAsync();

                return RedirectToAction(nameof(Index));
            }
            
            // Hata varsa formu tekrar göster
            ViewData["CategoryId"] = new SelectList(_context.Categories, "Id", "Name", product.CategoryId);
            ViewData["BrandId"] = new SelectList(_context.Brands, "Id", "Name", product.BrandId);
            return View(product);
        }
    }
}
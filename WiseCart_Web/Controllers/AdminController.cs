using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using Microsoft.EntityFrameworkCore;
using WiseCart_Web.Models;
using Microsoft.AspNetCore.Mvc.Rendering;

namespace WiseCart_Web.Controllers
{
    // 📋 İSTER 1: Controller - AdminController
    // 📋 İSTER 6: Kullanıcı Tipleri - Sadece Admin rolü erişebilir
    [Authorize(Roles = "Admin")] // KİLİT NOKTA: Sadece Admin girebilir
    public class AdminController : Controller
    {
        private readonly WiseCartDbContext _context;

        public AdminController(WiseCartDbContext context)
        {
            _context = context;
        }

        // 📋 İSTER 1: Action - Index
        // 📋 İSTER 5: CRUD - READ (Listeleme)
        // 1. LİSTELEME (READ) - SAYFALAMA EKLENDİ
        public async Task<IActionResult> Index(int page = 1)
        {
            int pageSize = 20; // Her sayfada 20 ürün göster

            // Sorguyu hazırla
            // 📊 PERFORMANS: Eager Loading (Include) - Category ve Brand bilgilerini tek sorguda çek
            var productsQuery = _context.Products
                .Include(p => p.Category)
                .Include(p => p.Brand)
                .OrderByDescending(p => p.Id); // En yeniler en başta

            // 📊 PERFORMANS: CountAsync() - Asenkron sayma işlemi
            ViewBag.TotalProducts = await productsQuery.CountAsync();
            
            // 📊 PERFORMANS: Sayfalama (Pagination) - Skip() ve Take() ile sadece gerekli kayıtları çek
            var products = await productsQuery
                .Skip((page - 1) * pageSize)
                .Take(pageSize)
                .ToListAsync();

            // 📋 İSTER 7: ViewBag kullanımı - Sayfalama bilgileri View'a aktarılır
            // Sayfalama bilgilerini View'a gönder
            ViewBag.CurrentPage = page;
            ViewBag.TotalPages = (int)Math.Ceiling(ViewBag.TotalProducts / (double)pageSize);

            return View(products);
        }

        // 📋 İSTER 1: Action - Delete
        // 📋 İSTER 5: CRUD - DELETE (Silme)
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

        // 📋 İSTER 1: Action - Create (GET)
        // 📋 İSTER 5: CRUD - CREATE (Ekleme sayfası)
        // 📋 İSTER 7: ViewData kullanımı - Kategori ve marka listeleri View'a aktarılır
        // 3. EKLEME SAYFASI (CREATE GET)
        public IActionResult Create()
        {
            ViewData["CategoryId"] = new SelectList(_context.Categories, "Id", "Name");
            ViewData["BrandId"] = new SelectList(_context.Brands, "Id", "Name");
            return View();
        }

        // 📋 İSTER 1: Action - Create (POST)
        // 📋 İSTER 5: CRUD - CREATE (Ekleme işlemi)
        // 📋 İSTER 7: TempData kullanımı - Başarı mesajı View'a aktarılır
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

                // 📋 İSTER 7: TempData kullanımı - Başarı mesajı bir sonraki sayfaya aktarılır
                // TempData ile başarı mesajı gönder (ViewData/TempData kullanımı için)
                TempData["SuccessMessage"] = $"Ürün '{product.Name}' başarıyla eklendi!";
                
                return RedirectToAction(nameof(Index));
            }
            
            // Hata varsa formu tekrar göster
            ViewData["CategoryId"] = new SelectList(_context.Categories, "Id", "Name", product.CategoryId);
            ViewData["BrandId"] = new SelectList(_context.Brands, "Id", "Name", product.BrandId);
            return View(product);
        }

        // 📋 İSTER 1: Action - Edit (GET)
        // 📋 İSTER 5: CRUD - UPDATE (Güncelleme sayfası)
        // 📋 İSTER 7: ViewData kullanımı - Kategori ve marka listeleri View'a aktarılır
        // 5. GÜNCELLEME SAYFASI (UPDATE GET)
        public async Task<IActionResult> Edit(int? id)
        {
            if (id == null)
            {
                return NotFound();
            }

            var product = await _context.Products
                .Include(p => p.Category)
                .Include(p => p.Brand)
                .FirstOrDefaultAsync(p => p.Id == id);

            if (product == null)
            {
                return NotFound();
            }

            ViewData["CategoryId"] = new SelectList(_context.Categories, "Id", "Name", product.CategoryId);
            ViewData["BrandId"] = new SelectList(_context.Brands, "Id", "Name", product.BrandId);
            
            return View(product);
        }

        // 📋 İSTER 1: Action - Edit (POST)
        // 📋 İSTER 5: CRUD - UPDATE (Güncelleme işlemi)
        // 📋 İSTER 7: TempData kullanımı - Başarı mesajı View'a aktarılır
        // 6. GÜNCELLEME İŞLEMİ (UPDATE POST)
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Edit(int id, Product product)
        {
            if (id != product.Id)
            {
                return NotFound();
            }

            if (ModelState.IsValid || true)
            {
                try
                {
                    var existingProduct = await _context.Products.FindAsync(id);
                    if (existingProduct == null)
                    {
                        return NotFound();
                    }

                    // Fiyat değiştiyse PriceHistory'ye ekle
                    if (existingProduct.CurrentPrice != product.CurrentPrice)
                    {
                        var history = new PriceHistory
                        {
                            ProductId = product.Id,
                            Price = product.CurrentPrice ?? 0,
                            Date = DateTime.Now
                        };
                        _context.PriceHistories.Add(history);
                    }

                    // Ürün bilgilerini güncelle
                    existingProduct.Name = product.Name;
                    existingProduct.Model = product.Model;
                    existingProduct.CurrentPrice = product.CurrentPrice;
                    existingProduct.ReviewCount = product.ReviewCount;
                    existingProduct.CategoryId = product.CategoryId;
                    existingProduct.BrandId = product.BrandId;
                    existingProduct.ImageUrl = product.ImageUrl;
                    existingProduct.Url = product.Url;

                    await _context.SaveChangesAsync();

                    // 📋 İSTER 7: TempData kullanımı - Başarı mesajı View'a aktarılır
                    // TempData ile başarı mesajı gönder
                    TempData["SuccessMessage"] = $"Ürün '{product.Name}' başarıyla güncellendi!";
                }
                catch (DbUpdateConcurrencyException)
                {
                    if (!ProductExists(product.Id))
                    {
                        return NotFound();
                    }
                    else
                    {
                        throw;
                    }
                }
                return RedirectToAction(nameof(Index));
            }

            ViewData["CategoryId"] = new SelectList(_context.Categories, "Id", "Name", product.CategoryId);
            ViewData["BrandId"] = new SelectList(_context.Brands, "Id", "Name", product.BrandId);
            return View(product);
        }

        private bool ProductExists(int id)
        {
            return _context.Products.Any(e => e.Id == id);
        }
    }
}
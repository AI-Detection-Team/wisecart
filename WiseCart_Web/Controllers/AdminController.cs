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
        // 1. LİSTELEME (READ) - SAYFALAMA EKLENDİ - SADECE SİLİNMEYEN ÜRÜNLER
        public async Task<IActionResult> Index(int page = 1)
        {
            int pageSize = 20; // Her sayfada 20 ürün göster

            // Sorguyu hazırla - Sadece silinmemiş ürünleri göster
            // 📊 PERFORMANS: Eager Loading (Include) - Category ve Brand bilgilerini tek sorguda çek
            // 📊 SOFT DELETE: IsDeleted = false olan ürünleri göster
            var productsQuery = _context.Products
                .Where(p => !p.IsDeleted) // Sadece silinmemiş ürünler
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

            // Silinen ürün sayısını da göster
            ViewBag.DeletedProductsCount = await _context.Products.CountAsync(p => p.IsDeleted);

            // 📋 İSTER 7: ViewBag kullanımı - Sayfalama bilgileri View'a aktarılır
            // Sayfalama bilgilerini View'a gönder
            ViewBag.CurrentPage = page;
            ViewBag.TotalPages = (int)Math.Ceiling(ViewBag.TotalProducts / (double)pageSize);

            return View(products);
        }

        // 📋 İSTER 1: Action - Delete
        // 📋 İSTER 5: CRUD - DELETE (Soft Delete - Yumuşak Silme)
        // 2. SİLME (SOFT DELETE) - Ürün veritabanında kalır ama listede görünmez
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Delete(int id)
        {
            var product = await _context.Products
                .FirstOrDefaultAsync(p => p.Id == id && !p.IsDeleted); // Sadece silinmemiş ürünleri bul
            
            if (product == null)
            {
                TempData["ErrorMessage"] = "Ürün bulunamadı veya zaten silinmiş!";
                return RedirectToAction(nameof(Index));
            }

            var productName = product.Name;

            try
            {
                // SOFT DELETE: Ürünü tamamen silmek yerine işaretle
                product.IsDeleted = true;
                product.DeletedAt = DateTime.Now;
                
                // Favorilerden de kaldır (Kullanıcılar silinen ürünü favorilerinde görmesin)
                var favorites = _context.Favorites.Where(f => f.ProductId == id);
                _context.Favorites.RemoveRange(favorites);

                await _context.SaveChangesAsync();

                // 📋 İSTER 7: TempData kullanımı - Başarı mesajı View'a aktarılır
                TempData["SuccessMessage"] = $"Ürün '{productName}' başarıyla silindi! (Veritabanında saklanıyor)";
            }
            catch (Exception ex)
            {
                TempData["ErrorMessage"] = $"Ürün silinirken bir hata oluştu: {ex.Message}";
            }

            return RedirectToAction(nameof(Index));
        }

        // 📋 İSTER 1: Action - Restore
        // 📋 İSTER 5: CRUD - RESTORE (Geri Yükleme)
        // 3. GERİ YÜKLEME (RESTORE) - Silinen ürünü tekrar aktif et
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Restore(int id)
        {
            var product = await _context.Products
                .FirstOrDefaultAsync(p => p.Id == id && p.IsDeleted); // Sadece silinmiş ürünleri bul
            
            if (product == null)
            {
                TempData["ErrorMessage"] = "Ürün bulunamadı veya zaten aktif!";
                return RedirectToAction(nameof(Deleted));
            }

            var productName = product.Name;

            try
            {
                // Ürünü tekrar aktif et
                product.IsDeleted = false;
                product.DeletedAt = null;

                await _context.SaveChangesAsync();

                TempData["SuccessMessage"] = $"Ürün '{productName}' başarıyla geri yüklendi!";
            }
            catch (Exception ex)
            {
                TempData["ErrorMessage"] = $"Ürün geri yüklenirken bir hata oluştu: {ex.Message}";
            }

            return RedirectToAction(nameof(Deleted));
        }

        // 📋 İSTER 1: Action - Deleted
        // 📋 İSTER 5: CRUD - READ (Silinen Ürünleri Listeleme)
        // 4. SİLİNEN ÜRÜNLER LİSTESİ
        public async Task<IActionResult> Deleted(int page = 1)
        {
            int pageSize = 20; // Her sayfada 20 ürün göster

            // Sadece silinmiş ürünleri göster
            var productsQuery = _context.Products
                .Where(p => p.IsDeleted) // Sadece silinmiş ürünler
                .Include(p => p.Category)
                .Include(p => p.Brand)
                .OrderByDescending(p => p.DeletedAt); // En son silinenler en başta

            ViewBag.TotalDeletedProducts = await productsQuery.CountAsync();
            
            var products = await productsQuery
                .Skip((page - 1) * pageSize)
                .Take(pageSize)
                .ToListAsync();

            ViewBag.CurrentPage = page;
            ViewBag.TotalPages = (int)Math.Ceiling(ViewBag.TotalDeletedProducts / (double)pageSize);
            ViewBag.ActiveProductsCount = await _context.Products.CountAsync(p => !p.IsDeleted);

            return View(products);
        }

        // 📋 İSTER 1: Action - PermanentDelete
        // 📋 İSTER 5: CRUD - PERMANENT DELETE (Kalıcı Silme)
        // 5. KALICI SİLME - Ürünü veritabanından tamamen sil
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> PermanentDelete(int id)
        {
            var product = await _context.Products
                .Include(p => p.PriceHistories)
                .FirstOrDefaultAsync(p => p.Id == id && p.IsDeleted); // Sadece silinmiş ürünleri kalıcı olarak silebiliriz
            
            if (product == null)
            {
                TempData["ErrorMessage"] = "Ürün bulunamadı! Sadece silinmiş ürünler kalıcı olarak silinebilir.";
                return RedirectToAction(nameof(Deleted));
            }

            var productName = product.Name;

            try
            {
                // Önce fiyat geçmişini sil
                var history = _context.PriceHistories.Where(h => h.ProductId == id);
                _context.PriceHistories.RemoveRange(history);
                
                // Favorilerden de sil
                var favorites = _context.Favorites.Where(f => f.ProductId == id);
                _context.Favorites.RemoveRange(favorites);

                // Ürünü tamamen sil
                _context.Products.Remove(product);
                await _context.SaveChangesAsync();

                TempData["SuccessMessage"] = $"Ürün '{productName}' veritabanından kalıcı olarak silindi!";
            }
            catch (Exception ex)
            {
                TempData["ErrorMessage"] = $"Ürün kalıcı olarak silinirken bir hata oluştu: {ex.Message}";
            }

            return RedirectToAction(nameof(Deleted));
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
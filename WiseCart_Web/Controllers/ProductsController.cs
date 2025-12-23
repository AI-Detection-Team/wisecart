using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WiseCart_Web.Models;
using Microsoft.AspNetCore.Mvc.Rendering;
using System.Net.Http; // SOA Loglama için gerekli
using System.Net.Http.Json; // JSON formatında veri göndermek için gerekli

namespace WiseCart_Web.Controllers
{
    // 📋 İSTER 1: Controller - ProductsController
    public class ProductsController : Controller
    {
        private readonly WiseCartDbContext _context;
        private readonly IConfiguration _configuration;

        public ProductsController(WiseCartDbContext context, IConfiguration configuration)
        {
            _context = context;
            _configuration = configuration;
        }

        // 📋 İSTER 1: Action - Index (Filtreleme, Arama ve Sayfalama içerir)
        // 📋 İSTER 2: Esnek View - Dinamik filtreleme ve sayfalama
        // GET: Products (Filtreleme, Arama ve Sayfalama içerir)
        public async Task<IActionResult> Index(string searchString, string category, int page = 1)
        {
            int pageSize = 24; // Her sayfada kaç ürün görünsün?

            // 📊 PERFORMANS: Eager Loading (Include) - Category ve Brand bilgilerini tek sorguda çek
            // N+1 sorgu problemini önler, ilişkili verileri önceden yükler
            // 📊 PERFORMANS: AsQueryable() - Sorguyu erteleyerek filtreleme yapabilmeyi sağlar
            var productsQuery = _context.Products
                .Include(p => p.Category)
                .Include(p => p.Brand)
                .AsQueryable();

            // 2. Kategori Filtresi
            if (!string.IsNullOrEmpty(category))
            {
                productsQuery = productsQuery.Where(p => p.Category.Name == category);
            }

            // 3. Arama Filtresi
            if (!string.IsNullOrEmpty(searchString))
            {
                productsQuery = productsQuery.Where(p => p.Name.Contains(searchString) || p.Brand.Name.Contains(searchString));
            }

            // 📊 PERFORMANS: CountAsync() - Asenkron sayma işlemi (UI thread'i bloklamaz)
            int totalItems = await productsQuery.CountAsync();
            var totalPages = (int)Math.Ceiling(totalItems / (double)pageSize);

            // 📊 PERFORMANS: Sayfalama (Pagination) - Skip() ve Take() ile sadece gerekli kayıtları çek
            // Tüm veriyi belleğe yüklemek yerine sadece sayfa başına 24 ürün çeker
            var products = await productsQuery
                .OrderByDescending(p => p.Id) // En yeniler üstte
                .Skip((page - 1) * pageSize)
                .Take(pageSize)
                .ToListAsync();

            // 6. View'a Bilgileri Gönder
            ViewBag.CurrentPage = page;
            ViewBag.TotalPages = totalPages;
            ViewBag.CurrentCategory = category;
            ViewBag.CurrentSearch = searchString;
            
            // 📊 PERFORMANS: Select() - Sadece Name kolonunu çek (tüm entity yerine)
            // Gereksiz veri transferini önler, bellek kullanımını azaltır
            ViewBag.Categories = await _context.Categories.Select(c => c.Name).Distinct().ToListAsync();
            
            // API URL'lerini ViewBag'e ekle (hardcoded URL yerine configuration'dan)
            ViewBag.PythonApiUrl = _configuration["ApiSettings:PythonApiUrl"] ?? "http://localhost:5001";
            ViewBag.LogServiceUrl = _configuration["ApiSettings:LogServiceUrl"] ?? "http://localhost:4000";

            return View(products);
        }

        // 📋 İSTER 1: Action - Details
        // GET: Products/Details/5 (SOA Loglama Entegre Edildi)
        public async Task<IActionResult> Details(int? id)
        {
            if (id == null) return NotFound();

            // 📊 PERFORMANS: Eager Loading - Category ve Brand bilgilerini tek sorguda çek
            var product = await _context.Products
                .Include(p => p.Category)
                .Include(p => p.Brand)
                .FirstOrDefaultAsync(m => m.Id == id);

            if (product == null) return NotFound();

            // 📊 PERFORMANS: Take(4) - Sadece 4 benzer ürün çek (tüm listeyi çekme)
            // 📊 PERFORMANS: Eager Loading - Category ve Brand bilgilerini tek sorguda çek
            var similarProducts = await _context.Products
                .Include(p => p.Category)
                .Include(p => p.Brand)
                .Where(p => p.CategoryId == product.CategoryId && p.Id != product.Id)
                .OrderBy(x => Guid.NewGuid()) // Rastgele sıralama
                .Take(4)
                .ToListAsync();

            // 📋 İSTER 7: ViewBag kullanımı - Benzer ürünler ve API URL'leri View'a aktarılır
            ViewBag.SimilarProducts = similarProducts;
            
            // API URL'lerini ViewBag'e ekle (hardcoded URL yerine configuration'dan)
            ViewBag.PythonApiUrl = _configuration["ApiSettings:PythonApiUrl"] ?? "http://localhost:5001";

            // --- SOA ENTEGRASYONU: NODE.JS LOGLAMA ---
            // 📊 PERFORMANS: Task.Run() - Async işlemi arka planda çalıştır (Fire and Forget)
            // Kullanıcı bu ürüne baktığında Node.js servisine haber veriyoruz.
            // Bu işlem "Fire and Forget" (Ateşle ve Unut) mantığıyla yapılır, siteyi yavaşlatmaz.
            _ = Task.Run(async () =>
            {
                try
                {
                    using (var client = new HttpClient())
                    {
                        var logData = new
                        {
                            // Kullanıcı giriş yapmışsa adını, yapmamışsa "Misafir" yaz
                            user = User.Identity.IsAuthenticated ? User.Identity.Name : "Misafir",
                            action = "Ürün Görüntüleme",
                            details = $"Ürün: {product.Name} (Fiyat: {product.CurrentPrice} TL)"
                        };
                        
                        // Node.js servisine veri gönder (configuration'dan URL al)
                        var logServiceUrl = _configuration["ApiSettings:LogServiceUrl"] ?? "http://localhost:4000";
                        await client.PostAsJsonAsync($"{logServiceUrl}/api/log", logData);
                    }
                }
                catch
                {
                    // Log servisi kapalıysa site çalışmaya devam etsin, hata verip kullanıcıyı durdurmasın.
                }
            });
            // ------------------------------------------

            return View(product);
        }
    }
}
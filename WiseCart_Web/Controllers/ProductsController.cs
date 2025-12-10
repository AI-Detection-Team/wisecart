using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WiseCart_Web.Models;
using Microsoft.AspNetCore.Mvc.Rendering;

namespace WiseCart_Web.Controllers
{
    public class ProductsController : Controller
    {
        private readonly WiseCartDbContext _context;

        public ProductsController(WiseCartDbContext context)
        {
            _context = context;
        }

        // GET: Products
        public async Task<IActionResult> Index(string searchString, string category, int page = 1)
        {
            int pageSize = 24; // Her sayfada kaç ürün görünsün?

            // 1. Sorguyu Hazırla (Henüz veritabanına gitmedi)
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

            // 4. Toplam Sayıyı Bul (Sayfalama için lazım)
            int totalItems = await productsQuery.CountAsync();
            var totalPages = (int)Math.Ceiling(totalItems / (double)pageSize);

            // 5. Sayfalama Yap ve Veriyi Çek
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
            
            // Kategori Listesini Dropdown için gönder
            ViewBag.Categories = await _context.Categories.Select(c => c.Name).Distinct().ToListAsync();

            return View(products);
        }

        public async Task<IActionResult> Details(int? id)
        {
            if (id == null) return NotFound();

            var product = await _context.Products
                .Include(p => p.Category)
                .Include(p => p.Brand)
                .FirstOrDefaultAsync(m => m.Id == id);

            if (product == null) return NotFound();

            return View(product);
        }
    }
}
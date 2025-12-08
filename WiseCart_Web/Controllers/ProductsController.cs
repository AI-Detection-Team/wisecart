using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WiseCart_Web.Models; // Kendi proje adınla aynı olmalı
using System.Linq;
using System.Threading.Tasks;

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
        public async Task<IActionResult> Index()
        {
            // Veritabanından ilk 50 ürünü çek (Sayfa çok şişmesin diye)
            var products = await _context.Products
                                         .Include(p => p.Category) // Kategorisini de getir
                                         .Include(p => p.Brand)    // Markasını da getir
                                         .Take(50)
                                         .ToListAsync();
            return View(products);
        }

        // GET: Products/Details/5
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
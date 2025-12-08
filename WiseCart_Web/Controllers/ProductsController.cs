using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WiseCart_Web.Models;
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

        // 1. Ürünleri Listeleme Sayfası
        public async Task<IActionResult> Index()
        {
            // Veritabanından ilk 100 ürünü çekelim (Sayfa kasmasın diye limit koyduk)
            // İsterseniz .Take(100) kısmını kaldırıp hepsini çekebilirsiniz.
            var products = await _context.Products
                .Include(p => p.Category)
                .Include(p => p.Brand)
                .OrderByDescending(p => p.Id) // En son eklenenler başta
                .Take(100) 
                .ToListAsync();

            return View(products);
        }

        // 2. Ürün Detay Sayfası
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
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using Microsoft.EntityFrameworkCore;
using WiseCart_Web.Models;

namespace WiseCart_Web.Controllers
{
    [Authorize(Roles = "Admin")] // SADECE ADMIN GİREBİLİR!
    public class AdminController : Controller
    {
        private readonly WiseCartDbContext _context;

        public AdminController(WiseCartDbContext context)
        {
            _context = context;
        }

        // 1. Admin Paneli Ana Sayfası (Ürün Listesi)
        public async Task<IActionResult> Index()
        {
            var products = await _context.Products
                .Include(p => p.Category)
                .Include(p => p.Brand)
                .OrderByDescending(p => p.Id)
                .Take(50) // Performans için son 50 ürün
                .ToListAsync();
            return View(products);
        }

        // 2. Ürün Silme İşlemi
        [HttpPost]
        public async Task<IActionResult> Delete(int id)
        {
            var product = await _context.Products.FindAsync(id);
            if (product != null)
            {
                _context.Products.Remove(product);
                await _context.SaveChangesAsync();
            }
            return RedirectToAction(nameof(Index));
        }

        // 3. Yeni Ürün Ekleme Sayfası (GET)
        public IActionResult Create()
        {
            // Kategorileri ve Markaları Dropdown için gönder
            ViewBag.Categories = _context.Categories.ToList();
            ViewBag.Brands = _context.Brands.ToList();
            return View();
        }

        // 4. Yeni Ürün Kaydetme (POST)
        [HttpPost]
        public async Task<IActionResult> Create(Product product)
        {
            // Basit validasyon ve kayıt
            if (ModelState.IsValid)
            {
                _context.Add(product);
                await _context.SaveChangesAsync();
                return RedirectToAction(nameof(Index));
            }
            return View(product);
        }
    }
}
using System.Diagnostics;
using Microsoft.AspNetCore.Mvc;
using WiseCart_Web.Models;

namespace WiseCart_Web.Controllers;

// 📋 İSTER 1: Controller ve Action - HomeController (3 Action: Index, Privacy, Error)
public class HomeController : Controller
{
    private readonly ILogger<HomeController> _logger;

    public HomeController(ILogger<HomeController> logger)
    {
        _logger = logger;
    }

    // 📋 İSTER 1: Action - Index
    public IActionResult Index()
    {
        return View();
    }

    // 📋 İSTER 1: Action - Privacy
    public IActionResult Privacy()
    {
        return View();
    }

    // 📋 İSTER 1: Action - Error
    [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
    public IActionResult Error()
    {
        return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
    }
}

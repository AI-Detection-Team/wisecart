using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using WiseCart_Web.Models.ViewModels;
using WiseCart_Web.Services;

namespace WiseCart_Web.Controllers;

/// <summary>
/// OLAP Küp Analizi Controller
/// Küp analizi yaparak veri ambarından analitik raporlar oluşturur
/// </summary>
[Authorize(Roles = "Admin")] // Sadece Admin erişebilir
public class AnalyticsController : Controller
{
    private readonly OlapAnalyticsService _analyticsService;

    public AnalyticsController(OlapAnalyticsService analyticsService)
    {
        _analyticsService = analyticsService;
    }

    /// <summary>
    /// Ana analitik dashboard
    /// </summary>
    public async Task<IActionResult> Dashboard()
    {
        var viewModel = new AnalyticsViewModel();

        try
        {
            viewModel.Summary = await _analyticsService.GetDashboardSummaryAsync();
            viewModel.CategoryAnalyses = await _analyticsService.GetCategoryAnalysisAsync();
            viewModel.BrandAnalyses = await _analyticsService.GetBrandAnalysisAsync();
            viewModel.TimeSeriesAnalyses = await _analyticsService.GetTimeSeriesAnalysisAsync("Month");
            viewModel.PriceTrendAnalyses = await _analyticsService.GetPriceTrendAnalysisAsync(10, false);
        }
        catch (Exception ex)
        {
            ViewBag.ErrorMessage = $"Analiz verileri yüklenirken hata oluştu: {ex.Message}";
        }

        return View(viewModel);
    }

    /// <summary>
    /// Kategori bazlı analiz sayfası
    /// </summary>
    public async Task<IActionResult> CategoryAnalysis()
    {
        var analyses = await _analyticsService.GetCategoryAnalysisAsync();
        return View(analyses);
    }

    /// <summary>
    /// Marka bazlı analiz sayfası
    /// </summary>
    public async Task<IActionResult> BrandAnalysis()
    {
        var analyses = await _analyticsService.GetBrandAnalysisAsync();
        return View(analyses);
    }

    /// <summary>
    /// Zaman serisi analizi sayfası
    /// </summary>
    public async Task<IActionResult> TimeSeries(string groupBy = "Month")
    {
        var analyses = await _analyticsService.GetTimeSeriesAnalysisAsync(groupBy);
        ViewBag.GroupBy = groupBy;
        return View(analyses);
    }

    /// <summary>
    /// Fiyat trend analizi sayfası
    /// </summary>
    public async Task<IActionResult> PriceTrend(int topCount = 20, bool showIncreases = true)
    {
        var analyses = await _analyticsService.GetPriceTrendAnalysisAsync(topCount, !showIncreases);
        ViewBag.TopCount = topCount;
        ViewBag.ShowIncreases = showIncreases;
        return View(analyses);
    }

    /// <summary>
    /// JSON API endpoint - Dashboard özet verileri
    /// </summary>
    [HttpGet]
    public async Task<IActionResult> GetDashboardSummary()
    {
        try
        {
            var summary = await _analyticsService.GetDashboardSummaryAsync();
            return Json(summary);
        }
        catch (Exception ex)
        {
            return BadRequest(new { error = ex.Message });
        }
    }

    /// <summary>
    /// JSON API endpoint - Kategori analizi
    /// </summary>
    [HttpGet]
    public async Task<IActionResult> GetCategoryAnalysis()
    {
        try
        {
            var analyses = await _analyticsService.GetCategoryAnalysisAsync();
            return Json(analyses);
        }
        catch (Exception ex)
        {
            return BadRequest(new { error = ex.Message });
        }
    }

    /// <summary>
    /// JSON API endpoint - Zaman serisi analizi
    /// </summary>
    [HttpGet]
    public async Task<IActionResult> GetTimeSeries(string groupBy = "Month")
    {
        try
        {
            var analyses = await _analyticsService.GetTimeSeriesAnalysisAsync(groupBy);
            return Json(analyses);
        }
        catch (Exception ex)
        {
            return BadRequest(new { error = ex.Message });
        }
    }
}


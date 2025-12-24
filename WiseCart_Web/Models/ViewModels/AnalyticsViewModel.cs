namespace WiseCart_Web.Models.ViewModels;

/// <summary>
/// OLAP Küp Analizi için ViewModel sınıfları
/// </summary>
public class AnalyticsViewModel
{
    public List<CategoryAnalysis> CategoryAnalyses { get; set; } = new();
    public List<BrandAnalysis> BrandAnalyses { get; set; } = new();
    public List<TimeSeriesAnalysis> TimeSeriesAnalyses { get; set; } = new();
    public List<PriceTrendAnalysis> PriceTrendAnalyses { get; set; } = new();
    public DashboardSummary Summary { get; set; } = new();
}

public class CategoryAnalysis
{
    public string CategoryName { get; set; } = string.Empty;
    public decimal TotalPrice { get; set; }
    public decimal AveragePrice { get; set; }
    public int ProductCount { get; set; }
    public decimal AveragePriceChangePercent { get; set; }
    public int PriceIncreaseCount { get; set; }
}

public class BrandAnalysis
{
    public string BrandName { get; set; } = string.Empty;
    public decimal TotalPrice { get; set; }
    public decimal AveragePrice { get; set; }
    public int ProductCount { get; set; }
    public int ReviewCount { get; set; }
}

public class TimeSeriesAnalysis
{
    public string Period { get; set; } = string.Empty; // "2024-01", "2024 Q1", vb.
    public int Year { get; set; }
    public int? Quarter { get; set; }
    public int? Month { get; set; }
    public decimal TotalPrice { get; set; }
    public decimal AveragePrice { get; set; }
    public int RecordCount { get; set; }
}

public class PriceTrendAnalysis
{
    public string ProductName { get; set; } = string.Empty;
    public string CategoryName { get; set; } = string.Empty;
    public decimal CurrentPrice { get; set; }
    public decimal? PriceChange { get; set; }
    public decimal? PriceChangePercent { get; set; }
    public bool IsPriceIncrease { get; set; }
}

public class DashboardSummary
{
    public int TotalProducts { get; set; }
    public int TotalCategories { get; set; }
    public int TotalBrands { get; set; }
    public decimal AveragePrice { get; set; }
    public int TotalRecords { get; set; }
    public int PriceIncreaseCount { get; set; }
    public int PriceDecreaseCount { get; set; }
}


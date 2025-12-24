using System.Data;
using Microsoft.Data.SqlClient;
using WiseCart_Web.Models.ViewModels;

namespace WiseCart_Web.Services;

/// <summary>
/// OLAP Küp Analizi Servisi - Veri Ambarından Analiz Verilerini Çeker
/// </summary>
public class OlapAnalyticsService
{
    private readonly string _connectionString;

    public OlapAnalyticsService(IConfiguration configuration)
    {
        // Veri ambarı bağlantı string'i
        var server = configuration.GetConnectionString("DefaultConnection")?.Split(';')
            .FirstOrDefault(s => s.StartsWith("Server="))?.Replace("Server=", "").Trim();
        var database = "WiseCartDW"; // Veri ambarı veritabanı
        
        _connectionString = $"Server={server};Database={database};Trusted_Connection=True;TrustServerCertificate=True;";
    }

    /// <summary>
    /// Dashboard özet verilerini getirir
    /// </summary>
    public async Task<DashboardSummary> GetDashboardSummaryAsync()
    {
        var summary = new DashboardSummary();
        
        using var connection = new SqlConnection(_connectionString);
        await connection.OpenAsync();

        // Genel özet sorgusu
        var query = @"
            SELECT 
                COUNT(DISTINCT dp.ProductKey) AS TotalProducts,
                COUNT(DISTINCT dc.CategoryKey) AS TotalCategories,
                COUNT(DISTINCT db.BrandKey) AS TotalBrands,
                AVG(fs.Price) AS AveragePrice,
                COUNT(*) AS TotalRecords,
                SUM(CASE WHEN fs.IsPriceIncrease = 1 THEN 1 ELSE 0 END) AS PriceIncreaseCount,
                SUM(CASE WHEN fs.IsPriceIncrease = 0 THEN 1 ELSE 0 END) AS PriceDecreaseCount
            FROM FactSales fs
            INNER JOIN DimProduct dp ON fs.ProductKey = dp.ProductKey
            INNER JOIN DimCategory dc ON fs.CategoryKey = dc.CategoryKey
            INNER JOIN DimBrand db ON fs.BrandKey = db.BrandKey";

        using var command = new SqlCommand(query, connection);
        using var reader = await command.ExecuteReaderAsync();
        
        if (await reader.ReadAsync())
        {
            summary.TotalProducts = reader.GetInt32("TotalProducts");
            summary.TotalCategories = reader.GetInt32("TotalCategories");
            summary.TotalBrands = reader.GetInt32("TotalBrands");
            summary.AveragePrice = reader.IsDBNull("AveragePrice") ? 0 : (decimal)reader.GetDouble("AveragePrice");
            summary.TotalRecords = reader.GetInt32("TotalRecords");
            summary.PriceIncreaseCount = reader.GetInt32("PriceIncreaseCount");
            summary.PriceDecreaseCount = reader.GetInt32("PriceDecreaseCount");
        }

        return summary;
    }

    /// <summary>
    /// Kategori bazlı analiz yapar
    /// </summary>
    public async Task<List<CategoryAnalysis>> GetCategoryAnalysisAsync()
    {
        var results = new List<CategoryAnalysis>();
        
        using var connection = new SqlConnection(_connectionString);
        await connection.OpenAsync();

        var query = @"
            SELECT 
                dc.CategoryName,
                SUM(fs.Price) AS TotalPrice,
                AVG(fs.Price) AS AveragePrice,
                COUNT(DISTINCT fs.ProductKey) AS ProductCount,
                AVG(fs.PriceChangePercent) AS AveragePriceChangePercent,
                SUM(CASE WHEN fs.IsPriceIncrease = 1 THEN 1 ELSE 0 END) AS PriceIncreaseCount
            FROM FactSales fs
            INNER JOIN DimCategory dc ON fs.CategoryKey = dc.CategoryKey
            WHERE dc.IsCurrent = 1
            GROUP BY dc.CategoryName
            ORDER BY TotalPrice DESC";

        using var command = new SqlCommand(query, connection);
        using var reader = await command.ExecuteReaderAsync();
        
        while (await reader.ReadAsync())
        {
            results.Add(new CategoryAnalysis
            {
                CategoryName = reader.GetString("CategoryName"),
                TotalPrice = (decimal)reader.GetDouble("TotalPrice"),
                AveragePrice = (decimal)reader.GetDouble("AveragePrice"),
                ProductCount = reader.GetInt32("ProductCount"),
                AveragePriceChangePercent = reader.IsDBNull("AveragePriceChangePercent") 
                    ? 0 : (decimal)reader.GetDouble("AveragePriceChangePercent"),
                PriceIncreaseCount = reader.GetInt32("PriceIncreaseCount")
            });
        }

        return results;
    }

    /// <summary>
    /// Marka bazlı analiz yapar
    /// </summary>
    public async Task<List<BrandAnalysis>> GetBrandAnalysisAsync()
    {
        var results = new List<BrandAnalysis>();
        
        using var connection = new SqlConnection(_connectionString);
        await connection.OpenAsync();

        var query = @"
            SELECT 
                db.BrandName,
                SUM(fs.Price) AS TotalPrice,
                AVG(fs.Price) AS AveragePrice,
                COUNT(DISTINCT fs.ProductKey) AS ProductCount,
                SUM(ISNULL(fs.ReviewCount, 0)) AS ReviewCount
            FROM FactSales fs
            INNER JOIN DimBrand db ON fs.BrandKey = db.BrandKey
            WHERE db.IsCurrent = 1
            GROUP BY db.BrandName
            ORDER BY TotalPrice DESC";

        using var command = new SqlCommand(query, connection);
        using var reader = await command.ExecuteReaderAsync();
        
        while (await reader.ReadAsync())
        {
            results.Add(new BrandAnalysis
            {
                BrandName = reader.GetString("BrandName"),
                TotalPrice = (decimal)reader.GetDouble("TotalPrice"),
                AveragePrice = (decimal)reader.GetDouble("AveragePrice"),
                ProductCount = reader.GetInt32("ProductCount"),
                ReviewCount = reader.GetInt32("ReviewCount")
            });
        }

        return results;
    }

    /// <summary>
    /// Zaman serisi analizi yapar (Yıl, Çeyrek, Ay bazlı)
    /// </summary>
    public async Task<List<TimeSeriesAnalysis>> GetTimeSeriesAnalysisAsync(string groupBy = "Month")
    {
        var results = new List<TimeSeriesAnalysis>();
        
        using var connection = new SqlConnection(_connectionString);
        await connection.OpenAsync();

        string groupByClause = groupBy switch
        {
            "Year" => "dd.Year",
            "Quarter" => "dd.Year, dd.Quarter",
            "Month" => "dd.Year, dd.Month",
            _ => "dd.Year, dd.Month"
        };

        string selectClause = groupBy switch
        {
            "Year" => "CAST(dd.Year AS NVARCHAR(10)) AS Period, dd.Year, NULL AS Quarter, NULL AS Month",
            "Quarter" => "CAST(dd.Year AS NVARCHAR(10)) + ' Q' + CAST(dd.Quarter AS NVARCHAR(1)) AS Period, dd.Year, dd.Quarter, NULL AS Month",
            "Month" => "CAST(dd.Year AS NVARCHAR(10)) + '-' + RIGHT('0' + CAST(dd.Month AS NVARCHAR(2)), 2) AS Period, dd.Year, NULL AS Quarter, dd.Month",
            _ => "CAST(dd.Year AS NVARCHAR(10)) + '-' + RIGHT('0' + CAST(dd.Month AS NVARCHAR(2)), 2) AS Period, dd.Year, NULL AS Quarter, dd.Month"
        };

        var query = $@"
            SELECT 
                {selectClause},
                SUM(fs.Price) AS TotalPrice,
                AVG(fs.Price) AS AveragePrice,
                COUNT(*) AS RecordCount
            FROM FactSales fs
            INNER JOIN DimDate dd ON fs.DateKey = dd.DateKey
            GROUP BY {groupByClause}
            ORDER BY dd.Year DESC, dd.Quarter DESC, dd.Month DESC";

        using var command = new SqlCommand(query, connection);
        using var reader = await command.ExecuteReaderAsync();
        
        while (await reader.ReadAsync())
        {
            results.Add(new TimeSeriesAnalysis
            {
                Period = reader.GetString("Period"),
                Year = reader.GetInt32("Year"),
                Quarter = reader.IsDBNull("Quarter") ? null : reader.GetInt32("Quarter"),
                Month = reader.IsDBNull("Month") ? null : reader.GetInt32("Month"),
                TotalPrice = (decimal)reader.GetDouble("TotalPrice"),
                AveragePrice = (decimal)reader.GetDouble("AveragePrice"),
                RecordCount = reader.GetInt32("RecordCount")
            });
        }

        return results;
    }

    /// <summary>
    /// Fiyat trend analizi yapar (En çok artan/azalan ürünler)
    /// </summary>
    public async Task<List<PriceTrendAnalysis>> GetPriceTrendAnalysisAsync(int topCount = 20, bool ascending = false)
    {
        var results = new List<PriceTrendAnalysis>();
        
        using var connection = new SqlConnection(_connectionString);
        await connection.OpenAsync();

        var orderBy = ascending ? "ASC" : "DESC";
        
        var query = $@"
            SELECT TOP {topCount}
                dp.ProductName,
                dc.CategoryName,
                fs.Price AS CurrentPrice,
                fs.PriceChange,
                fs.PriceChangePercent,
                fs.IsPriceIncrease
            FROM FactSales fs
            INNER JOIN DimProduct dp ON fs.ProductKey = dp.ProductKey AND dp.IsCurrent = 1
            INNER JOIN DimCategory dc ON fs.CategoryKey = dc.CategoryKey AND dc.IsCurrent = 1
            WHERE fs.PriceChange IS NOT NULL
            ORDER BY fs.PriceChangePercent {orderBy}";

        using var command = new SqlCommand(query, connection);
        using var reader = await command.ExecuteReaderAsync();
        
        while (await reader.ReadAsync())
        {
            results.Add(new PriceTrendAnalysis
            {
                ProductName = reader.GetString("ProductName"),
                CategoryName = reader.GetString("CategoryName"),
                CurrentPrice = (decimal)reader.GetDouble("CurrentPrice"),
                PriceChange = reader.IsDBNull("PriceChange") ? null : (decimal?)reader.GetDouble("PriceChange"),
                PriceChangePercent = reader.IsDBNull("PriceChangePercent") ? null : (decimal?)reader.GetDouble("PriceChangePercent"),
                IsPriceIncrease = reader.IsDBNull("IsPriceIncrease") ? false : reader.GetBoolean("IsPriceIncrease")
            });
        }

        return results;
    }
}


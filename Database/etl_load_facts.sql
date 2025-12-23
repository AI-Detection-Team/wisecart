-- ============================================
-- ETL: FACT TABLOLARINI YÜKLEME
-- WiseCartDB (Source) -> WiseCartDW (Target)
-- ============================================

USE WiseCartDW;
GO

-- ============================================
-- 1. FactSales'i Doldur (PriceHistory'den)
-- ============================================
-- Incremental Load: Sadece yeni kayıtları yükle
DECLARE @LastLoadId INT;
SELECT @LastLoadId = ISNULL(LastLoadId, 0) FROM ETLControl WHERE TableName = 'FactSales';

INSERT INTO FactSales (
    [DateKey], [ProductKey], [CategoryKey], [BrandKey],
    [Price], [PriceChange], [PriceChangePercent], [ReviewCount],
    [IsPriceIncrease], [SourceSystemId], [LoadDate]
)
SELECT 
    dd.DateKey,
    dp.ProductKey,
    dp.CategoryKey,
    dp.BrandKey,
    ph.Price,
    -- Önceki fiyatı bul ve değişimi hesapla
    CASE 
        WHEN LAG(ph.Price) OVER (PARTITION BY ph.ProductId ORDER BY ph.Date) IS NOT NULL
        THEN ph.Price - LAG(ph.Price) OVER (PARTITION BY ph.ProductId ORDER BY ph.Date)
        ELSE NULL
    END AS PriceChange,
    -- Yüzde değişim
    CASE 
        WHEN LAG(ph.Price) OVER (PARTITION BY ph.ProductId ORDER BY ph.Date) IS NOT NULL
            AND LAG(ph.Price) OVER (PARTITION BY ph.ProductId ORDER BY ph.Date) > 0
        THEN ((ph.Price - LAG(ph.Price) OVER (PARTITION BY ph.ProductId ORDER BY ph.Date)) 
              / LAG(ph.Price) OVER (PARTITION BY ph.ProductId ORDER BY ph.Date)) * 100
        ELSE NULL
    END AS PriceChangePercent,
    p.ReviewCount,
    -- Fiyat artışı mı?
    CASE 
        WHEN LAG(ph.Price) OVER (PARTITION BY ph.ProductId ORDER BY ph.Date) IS NOT NULL
        THEN CASE WHEN ph.Price > LAG(ph.Price) OVER (PARTITION BY ph.ProductId ORDER BY ph.Date) THEN 1 ELSE 0 END
        ELSE NULL
    END AS IsPriceIncrease,
    ph.Id AS SourceSystemId,
    GETDATE() AS LoadDate
FROM WiseCartDB.dbo.PriceHistory ph
INNER JOIN WiseCartDB.dbo.Products p ON ph.ProductId = p.Id
INNER JOIN DimProduct dp ON p.Id = dp.ProductId AND dp.IsCurrent = 1
INNER JOIN DimDate dd ON CAST(ph.Date AS DATE) = dd.Date
WHERE ph.Id > @LastLoadId  -- Incremental load
    AND ph.Date IS NOT NULL
    AND ph.Price > 0;

-- ETL Control'ü güncelle
DECLARE @RecordCount INT = @@ROWCOUNT;
DECLARE @MaxId INT;
SELECT @MaxId = MAX(SourceSystemId) FROM FactSales;

UPDATE ETLControl 
SET LastLoadDate = GETDATE(), 
    Status = 'Success', 
    RecordCount = @RecordCount,
    LastLoadId = @MaxId
WHERE TableName = 'FactSales';

PRINT CONCAT('✅ FactSales tablosu güncellendi. ', @RecordCount, ' kayıt eklendi.');
GO

-- ============================================
-- 2. FactFavorites'i Doldur (Favorites'den)
-- ============================================
DECLARE @LastLoadId INT;
SELECT @LastLoadId = ISNULL(LastLoadId, 0) FROM ETLControl WHERE TableName = 'FactFavorites';

INSERT INTO FactFavorites (
    [DateKey], [UserKey], [ProductKey], [CategoryKey], [BrandKey],
    [FavoriteCount], [IsActive], [SourceSystemId], [LoadDate]
)
SELECT 
    dd.DateKey,
    du.UserKey,
    dp.ProductKey,
    dp.CategoryKey,
    dp.BrandKey,
    1 AS FavoriteCount,  -- Her kayıt 1 favori ekleme
    1 AS IsActive,  -- Aktif (silinmemiş)
    f.Id AS SourceSystemId,
    GETDATE() AS LoadDate
FROM WiseCartDB.dbo.Favorites f
INNER JOIN DimUser du ON f.UserId = du.UserId AND du.IsCurrent = 1
INNER JOIN DimProduct dp ON f.ProductId = dp.ProductId AND dp.IsCurrent = 1
INNER JOIN DimDate dd ON CAST(f.CreatedAt AS DATE) = dd.Date
WHERE f.Id > @LastLoadId;  -- Incremental load

-- ETL Control'ü güncelle
DECLARE @RecordCount INT = @@ROWCOUNT;
DECLARE @MaxId INT;
SELECT @MaxId = MAX(SourceSystemId) FROM FactFavorites;

UPDATE ETLControl 
SET LastLoadDate = GETDATE(), 
    Status = 'Success', 
    RecordCount = @RecordCount,
    LastLoadId = @MaxId
WHERE TableName = 'FactFavorites';

PRINT CONCAT('✅ FactFavorites tablosu güncellendi. ', @RecordCount, ' kayıt eklendi.');
GO

PRINT '';
PRINT '========================================';
PRINT '✅ TÜM FACT TABLOLARI YÜKLENDİ!';
PRINT '========================================';
PRINT '';






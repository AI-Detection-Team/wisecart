-- ============================================
-- ETL: DIMENSION TABLOLARINI YÜKLEME
-- WiseCartDB (Source) -> WiseCartDW (Target)
-- ============================================

USE WiseCartDW;
GO

-- ============================================
-- 1. DimDate'i Doldur (Son 5 yıl + Gelecek 1 yıl)
-- ============================================
IF NOT EXISTS (SELECT TOP 1 * FROM DimDate)
BEGIN
    DECLARE @StartDate DATE = DATEADD(YEAR, -5, GETDATE());
    DECLARE @EndDate DATE = DATEADD(YEAR, 1, GETDATE());
    DECLARE @CurrentDate DATE = @StartDate;
    
    WHILE @CurrentDate <= @EndDate
    BEGIN
        INSERT INTO DimDate (
            [DateKey], [Date], [Day], [Month], [Year], [Quarter],
            [MonthName], [DayOfWeek], [DayName], [IsWeekend], [IsHoliday]
        )
        VALUES (
            CAST(FORMAT(@CurrentDate, 'yyyyMMdd') AS INT),  -- DateKey: 20250115
            @CurrentDate,
            DAY(@CurrentDate),
            MONTH(@CurrentDate),
            YEAR(@CurrentDate),
            DATEPART(QUARTER, @CurrentDate),
            DATENAME(MONTH, @CurrentDate),  -- Ocak, Şubat, vb.
            DATEPART(WEEKDAY, @CurrentDate),  -- 1=Pazar, 2=Pazartesi, vb.
            DATENAME(WEEKDAY, @CurrentDate),  -- Pazartesi, Salı, vb.
            CASE WHEN DATEPART(WEEKDAY, @CurrentDate) IN (1, 7) THEN 1 ELSE 0 END,  -- Hafta sonu kontrolü
            0  -- IsHoliday (Türkiye için özel günler eklenebilir)
        );
        
        SET @CurrentDate = DATEADD(DAY, 1, @CurrentDate);
    END;
    
    UPDATE ETLControl SET LastLoadDate = GETDATE(), Status = 'Success', RecordCount = @@ROWCOUNT
    WHERE TableName = 'DimDate';
    
    PRINT '✅ DimDate tablosu dolduruldu.';
END
ELSE
BEGIN
    PRINT '⚠️ DimDate tablosu zaten dolu.';
END
GO

-- ============================================
-- 2. DimCategory'i Doldur (WiseCartDB'den)
-- ============================================
MERGE DimCategory AS target
USING (
    SELECT 
        Id AS CategoryId,
        Name AS CategoryName
    FROM WiseCartDB.dbo.Categories
) AS source
ON target.CategoryId = source.CategoryId AND target.IsCurrent = 1
WHEN NOT MATCHED THEN
    INSERT ([CategoryId], [CategoryName], [ValidFrom], [IsCurrent])
    VALUES (source.CategoryId, source.CategoryName, GETDATE(), 1);

UPDATE ETLControl SET LastLoadDate = GETDATE(), Status = 'Success'
WHERE TableName = 'DimCategory';

PRINT '✅ DimCategory tablosu güncellendi.';
GO

-- ============================================
-- 3. DimBrand'i Doldur (WiseCartDB'den)
-- ============================================
MERGE DimBrand AS target
USING (
    SELECT 
        Id AS BrandId,
        Name AS BrandName
    FROM WiseCartDB.dbo.Brands
) AS source
ON target.BrandId = source.BrandId AND target.IsCurrent = 1
WHEN NOT MATCHED THEN
    INSERT ([BrandId], [BrandName], [ValidFrom], [IsCurrent])
    VALUES (source.BrandId, source.BrandName, GETDATE(), 1);

UPDATE ETLControl SET LastLoadDate = GETDATE(), Status = 'Success'
WHERE TableName = 'DimBrand';

PRINT '✅ DimBrand tablosu güncellendi.';
GO

-- ============================================
-- 4. DimProduct'i Doldur (WiseCartDB'den)
-- ============================================
MERGE DimProduct AS target
USING (
    SELECT 
        p.Id AS ProductId,
        p.Name AS ProductName,
        p.Model AS ProductModel,
        dc.CategoryKey,
        db.BrandKey
    FROM WiseCartDB.dbo.Products p
    INNER JOIN DimCategory dc ON p.CategoryId = dc.CategoryId AND dc.IsCurrent = 1
    INNER JOIN DimBrand db ON p.BrandId = db.BrandId AND db.IsCurrent = 1
) AS source
ON target.ProductId = source.ProductId AND target.IsCurrent = 1
WHEN NOT MATCHED THEN
    INSERT ([ProductId], [ProductName], [ProductModel], [CategoryKey], [BrandKey], [ValidFrom], [IsCurrent])
    VALUES (source.ProductId, source.ProductName, source.ProductModel, source.CategoryKey, source.BrandKey, GETDATE(), 1);

UPDATE ETLControl SET LastLoadDate = GETDATE(), Status = 'Success'
WHERE TableName = 'DimProduct';

PRINT '✅ DimProduct tablosu güncellendi.';
GO

-- ============================================
-- 5. DimUser'i Doldur (WiseCartDB'den)
-- ============================================
MERGE DimUser AS target
USING (
    SELECT 
        u.Id AS UserId,
        u.Username,
        r.Name AS UserRole,
        CAST(u.CreatedAt AS DATE) AS RegistrationDate
    FROM WiseCartDB.dbo.Users u
    LEFT JOIN WiseCartDB.dbo.Roles r ON u.RoleId = r.Id
) AS source
ON target.UserId = source.UserId AND target.IsCurrent = 1
WHEN NOT MATCHED THEN
    INSERT ([UserId], [Username], [UserRole], [RegistrationDate], [ValidFrom], [IsCurrent])
    VALUES (source.UserId, source.Username, source.UserRole, source.RegistrationDate, GETDATE(), 1);

UPDATE ETLControl SET LastLoadDate = GETDATE(), Status = 'Success'
WHERE TableName = 'DimUser';

PRINT '✅ DimUser tablosu güncellendi.';
GO

PRINT '';
PRINT '========================================';
PRINT '✅ TÜM DIMENSION TABLOLARI YÜKLENDİ!';
PRINT '========================================';
PRINT '';


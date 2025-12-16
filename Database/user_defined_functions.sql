-- ============================================
-- KULLANICI TANIMLI FONKSİYONLAR
-- En az 2 adet gerekli (İster: 10 puan)
-- ============================================

USE WiseCartDB;  -- Ana veritabanında kullanılacak
GO

-- ============================================
-- FONKSİYON 1: Fiyat Hesaplama Fonksiyonu
-- İndirimli fiyat hesaplama
-- ============================================
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[fn_CalculateDiscountedPrice]') AND type in (N'FN', N'IF', N'TF', N'FS', N'FT'))
    DROP FUNCTION [dbo].[fn_CalculateDiscountedPrice];
GO

CREATE FUNCTION [dbo].[fn_CalculateDiscountedPrice]
(
    @Price FLOAT,
    @DiscountPercent FLOAT
)
RETURNS FLOAT
AS
BEGIN
    DECLARE @Result FLOAT;
    
    -- Negatif indirim olamaz
    IF @DiscountPercent < 0
        SET @DiscountPercent = 0;
    
    -- %100'den fazla indirim olamaz
    IF @DiscountPercent > 100
        SET @DiscountPercent = 100;
    
    -- İndirimli fiyatı hesapla
    SET @Result = @Price * (1 - @DiscountPercent / 100.0);
    
    -- Negatif fiyat olamaz
    IF @Result < 0
        SET @Result = 0;
    
    RETURN @Result;
END;
GO

PRINT '✅ fn_CalculateDiscountedPrice fonksiyonu oluşturuldu.';
GO

-- Kullanım örneği:
-- SELECT dbo.fn_CalculateDiscountedPrice(1000, 15) AS DiscountedPrice;  -- 850.0 döner

-- ============================================
-- FONKSİYON 2: Kategori Bazlı Ortalama Fiyat
-- Belirli bir kategorinin ortalama fiyatını döndürür
-- ============================================
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[fn_GetCategoryAveragePrice]') AND type in (N'FN', N'IF', N'TF', N'FS', N'FT'))
    DROP FUNCTION [dbo].[fn_GetCategoryAveragePrice];
GO

CREATE FUNCTION [dbo].[fn_GetCategoryAveragePrice]
(
    @CategoryId INT
)
RETURNS FLOAT
AS
BEGIN
    DECLARE @AvgPrice FLOAT;
    
    SELECT @AvgPrice = AVG(CAST(CurrentPrice AS FLOAT))
    FROM Products
    WHERE CategoryId = @CategoryId
        AND CurrentPrice IS NOT NULL
        AND CurrentPrice > 0;
    
    -- Eğer kategori bulunamazsa veya ürün yoksa 0 döndür
    RETURN ISNULL(@AvgPrice, 0);
END;
GO

PRINT '✅ fn_GetCategoryAveragePrice fonksiyonu oluşturuldu.';
GO

-- Kullanım örneği:
-- SELECT dbo.fn_GetCategoryAveragePrice(1) AS AveragePrice;

-- ============================================
-- FONKSİYON 3 (BONUS): Fiyat Değişim Yüzdesi
-- İki tarih arasındaki fiyat değişim yüzdesini hesaplar
-- ============================================
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[fn_CalculatePriceChangePercent]') AND type in (N'FN', N'IF', N'TF', N'FS', N'FT'))
    DROP FUNCTION [dbo].[fn_CalculatePriceChangePercent];
GO

CREATE FUNCTION [dbo].[fn_CalculatePriceChangePercent]
(
    @ProductId INT,
    @StartDate DATETIME,
    @EndDate DATETIME
)
RETURNS FLOAT
AS
BEGIN
    DECLARE @StartPrice FLOAT;
    DECLARE @EndPrice FLOAT;
    DECLARE @ChangePercent FLOAT;
    
    -- Başlangıç fiyatını bul
    SELECT TOP 1 @StartPrice = Price
    FROM PriceHistory
    WHERE ProductId = @ProductId
        AND Date >= @StartDate
    ORDER BY Date ASC;
    
    -- Bitiş fiyatını bul
    SELECT TOP 1 @EndPrice = Price
    FROM PriceHistory
    WHERE ProductId = @ProductId
        AND Date <= @EndDate
    ORDER BY Date DESC;
    
    -- Yüzde değişimi hesapla
    IF @StartPrice IS NOT NULL AND @EndPrice IS NOT NULL AND @StartPrice > 0
    BEGIN
        SET @ChangePercent = ((@EndPrice - @StartPrice) / @StartPrice) * 100;
    END
    ELSE
    BEGIN
        SET @ChangePercent = NULL;
    END
    
    RETURN @ChangePercent;
END;
GO

PRINT '✅ fn_CalculatePriceChangePercent fonksiyonu oluşturuldu.';
GO

-- Kullanım örneği:
-- SELECT dbo.fn_CalculatePriceChangePercent(1, '2024-01-01', '2024-12-31') AS PriceChangePercent;

PRINT '';
PRINT '========================================';
PRINT '✅ KULLANICI TANIMLI FONKSİYONLAR OLUŞTURULDU!';
PRINT '========================================';
PRINT '';
PRINT 'Oluşturulan fonksiyonlar:';
PRINT '  1. fn_CalculateDiscountedPrice - İndirimli fiyat hesaplama';
PRINT '  2. fn_GetCategoryAveragePrice - Kategori ortalama fiyatı';
PRINT '  3. fn_CalculatePriceChangePercent - Fiyat değişim yüzdesi (BONUS)';
PRINT '';


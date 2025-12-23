-- ============================================
-- STORED PROCEDURE TEST SCRIPT
-- Azure SQL Database'de çalıştırmak için
-- ============================================
-- ÖNEMLİ: Önce setup_procedures_azure.sql dosyasını çalıştırın!
-- ============================================

USE WiseCartDB;
GO

-- Procedure'ların var olup olmadığını kontrol et
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_GetProductsByPriceRange')
BEGIN
    PRINT '❌ HATA: Stored procedure''lar bulunamadı!';
    PRINT 'Lütfen önce setup_procedures_azure.sql dosyasını çalıştırın.';
    RETURN;
END
GO

-- ============================================
-- PROCEDURE 1: sp_GetProductsByPriceRange
-- ============================================
-- Kullanım: Belirli fiyat aralığındaki ürünleri getirir
-- Örnek: 10.000 TL ile 20.000 TL arasındaki ürünler

PRINT '========================================';
PRINT 'PROCEDURE 1: sp_GetProductsByPriceRange';
PRINT 'Fiyat Aralığı: 10.000 TL - 20.000 TL';
PRINT '========================================';
GO

EXEC sp_GetProductsByPriceRange 
    @MinPrice = 10000,
    @MaxPrice = 20000;
GO

PRINT '';
PRINT '========================================';
PRINT 'PROCEDURE 2: sp_GetCheapProductsByCategory';
PRINT 'Kategori: Laptop';
PRINT '========================================';
GO

-- ============================================
-- PROCEDURE 2: sp_GetCheapProductsByCategory
-- ============================================
-- Kullanım: Bir kategorideki en ucuz 5 ürünü getirir

EXEC sp_GetCheapProductsByCategory 
    @CategoryName = 'Laptop';
GO

PRINT '';
PRINT '========================================';
PRINT 'PROCEDURE 3: sp_GetProductsByRange';
PRINT 'Fiyat Aralığı: 5.000 TL - 15.000 TL';
PRINT '========================================';
GO

-- ============================================
-- PROCEDURE 3: sp_GetProductsByRange
-- ============================================
-- Kullanım: Fiyat aralığına göre ürün getirir

EXEC sp_GetProductsByRange 
    @MinPrice = 5000,
    @MaxPrice = 15000;
GO

PRINT '';
PRINT '✅ TÜM STORED PROCEDURE''LAR BAŞARIYLA ÇALIŞTIRILDI!';
GO


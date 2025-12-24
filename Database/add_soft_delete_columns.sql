-- =============================================
-- Soft Delete Özelliği için Kolon Ekleme Scripti
-- =============================================
-- Bu script Products tablosuna IsDeleted ve DeletedAt kolonlarını ekler
-- Böylece ürünler veritabanından tamamen silinmez, sadece işaretlenir
-- =============================================

USE WiseCartDB;
GO

-- IsDeleted kolonunu ekle (Varsayılan: false - aktif ürünler)
IF NOT EXISTS (
    SELECT * FROM sys.columns 
    WHERE object_id = OBJECT_ID(N'[dbo].[Products]') 
    AND name = 'IsDeleted'
)
BEGIN
    ALTER TABLE Products
    ADD IsDeleted BIT NOT NULL DEFAULT 0;
    
    PRINT '✅ IsDeleted kolonu başarıyla eklendi.';
END
ELSE
BEGIN
    PRINT '⚠️ IsDeleted kolonu zaten mevcut.';
END
GO

-- DeletedAt kolonunu ekle (Ürünün ne zaman silindiğini tutar)
IF NOT EXISTS (
    SELECT * FROM sys.columns 
    WHERE object_id = OBJECT_ID(N'[dbo].[Products]') 
    AND name = 'DeletedAt'
)
BEGIN
    ALTER TABLE Products
    ADD DeletedAt DATETIME NULL;
    
    PRINT '✅ DeletedAt kolonu başarıyla eklendi.';
END
ELSE
BEGIN
    PRINT '⚠️ DeletedAt kolonu zaten mevcut.';
END
GO

-- Mevcut ürünlerin hepsi aktif olarak işaretlensin (güvenlik için)
UPDATE Products
SET IsDeleted = 0, DeletedAt = NULL
WHERE IsDeleted IS NULL OR IsDeleted = 1;
GO

-- Index ekle (Performans için - silinmemiş ürünleri hızlı bulmak için)
IF NOT EXISTS (
    SELECT * FROM sys.indexes 
    WHERE name = 'IX_Products_IsDeleted' 
    AND object_id = OBJECT_ID(N'[dbo].[Products]')
)
BEGIN
    CREATE INDEX IX_Products_IsDeleted ON Products(IsDeleted);
    PRINT '✅ IX_Products_IsDeleted indexi başarıyla oluşturuldu.';
END
ELSE
BEGIN
    PRINT '⚠️ IX_Products_IsDeleted indexi zaten mevcut.';
END
GO

-- Composite Index (IsDeleted ve DeletedAt birlikte - silinen ürünleri sıralamak için)
IF NOT EXISTS (
    SELECT * FROM sys.indexes 
    WHERE name = 'IX_Products_IsDeleted_DeletedAt' 
    AND object_id = OBJECT_ID(N'[dbo].[Products]')
)
BEGIN
    CREATE INDEX IX_Products_IsDeleted_DeletedAt ON Products(IsDeleted, DeletedAt DESC);
    PRINT '✅ IX_Products_IsDeleted_DeletedAt indexi başarıyla oluşturuldu.';
END
ELSE
BEGIN
    PRINT '⚠️ IX_Products_IsDeleted_DeletedAt indexi zaten mevcut.';
END
GO

PRINT '';
PRINT '========================================';
PRINT '✅ Soft Delete özelliği başarıyla eklendi!';
PRINT '========================================';
PRINT '';
PRINT 'Kullanım:';
PRINT '  - Ürün silindiğinde IsDeleted = 1 ve DeletedAt = GETDATE() olur';
PRINT '  - Aktif ürünler: WHERE IsDeleted = 0';
PRINT '  - Silinen ürünler: WHERE IsDeleted = 1';
PRINT '  - Ürün geri yüklendiğinde IsDeleted = 0 ve DeletedAt = NULL olur';
PRINT '';
GO


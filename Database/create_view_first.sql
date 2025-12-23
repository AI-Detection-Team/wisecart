-- ============================================
-- ÖNCE BU SCRIPTİ ÇALIŞTIRIN!
-- vw_ProductDetails view'ını oluşturur
-- ============================================

USE WiseCartDB;
GO

-- View'ı oluştur (eğer yoksa)
IF EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[dbo].[vw_ProductDetails]'))
    DROP VIEW [dbo].[vw_ProductDetails];
GO

CREATE VIEW vw_ProductDetails AS
SELECT 
    p.Id, 
    p.Name, 
    p.CurrentPrice, 
    p.ReviewCount, 
    c.Name AS CategoryName, 
    b.Name AS BrandName,
    p.ImageUrl
FROM Products p
JOIN Categories c ON p.CategoryId = c.Id
JOIN Brands b ON p.BrandId = b.Id;
GO

PRINT '✅ vw_ProductDetails view oluşturuldu!';
PRINT 'Şimdi setup_procedures_azure.sql dosyasını çalıştırabilirsiniz.';
GO


-- 1. Fiyat 0'dan küçük olamaz
ALTER TABLE Products
ADD CONSTRAINT CK_Product_Price CHECK (CurrentPrice >= 0);

-- 2. Stok/Yorum sayısı negatif olamaz
ALTER TABLE Products
ADD CONSTRAINT CK_Product_ReviewCount CHECK (ReviewCount >= 0);

-- 3. Kullanıcı adı benzersiz olmalı (Aynı isimle iki kişi olamaz)
-- (Eğer tabloyu oluştururken unique yapmadıysak bu garanti eder)
ALTER TABLE Users
ADD CONSTRAINT UQ_Username UNIQUE (Username);

-- 4. Email benzersiz olmalı
ALTER TABLE Users
ADD CONSTRAINT UQ_Email UNIQUE (Email);

-- 5. Ürünlerin Markası Boş Olamaz (Zaten kodda var ama SQL tarafında da zorlayalım)
-- (Not: Eğer tabloda boş veri varsa bu hata verebilir, önce veriler temiz olmalı)
-- ALTER TABLE Products ALTER COLUMN Name NVARCHAR(500) NOT NULL; -- Örnek

-- View 1: Ürünlerin Detaylı Listesi (Marka ve Kategori İsimleriyle)
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

-- View 2: Kategori Bazlı Ortalama Fiyat Analizi
CREATE VIEW vw_CategoryStats AS
SELECT 
    c.Name AS CategoryName, 
    COUNT(p.Id) AS ProductCount, 
    AVG(p.CurrentPrice) AS AveragePrice
FROM Products p
JOIN Categories c ON p.CategoryId = c.Id
GROUP BY c.Name;
GO

-- View 3: En Çok Yorumlanan 50 Ürün (Popüler Ürünler)
CREATE VIEW vw_TopReviewedProducts AS
SELECT TOP 50
    p.Name, 
    b.Name AS Brand, 
    p.ReviewCount, 
    p.CurrentPrice
FROM Products p
JOIN Brands b ON p.BrandId = b.Id
ORDER BY p.ReviewCount DESC;
GO

-- View 4: Markalara Göre Ürün Sayısı
CREATE VIEW vw_BrandProductCounts AS
SELECT 
    b.Name AS BrandName, 
    COUNT(p.Id) AS TotalProducts
FROM Products p
JOIN Brands b ON p.BrandId = b.Id
GROUP BY b.Name;
GO

-- View 5: Fiyatı 50.000 TL Üzeri Olan Lüks Ürünler
CREATE VIEW vw_LuxuryProducts AS
SELECT * FROM vw_ProductDetails
WHERE CurrentPrice > 50000;
GO

-- Proc 1: Belirli bir fiyat aralığındaki ürünleri getir
-- Kullanımı: EXEC sp_GetProductsByPriceRange 10000, 20000
CREATE PROCEDURE sp_GetProductsByPriceRange
    @MinPrice float,
    @MaxPrice float
AS
BEGIN
    SELECT * FROM vw_ProductDetails
    WHERE CurrentPrice BETWEEN @MinPrice AND @MaxPrice
    ORDER BY CurrentPrice ASC;
END;
GO

-- Proc 2: Bir kategorideki en ucuz 5 ürünü getir
-- Kullanımı: EXEC sp_GetCheapProductsByCategory 'Laptop'
CREATE PROCEDURE sp_GetCheapProductsByCategory
    @CategoryName nvarchar(50)
AS
BEGIN
    SELECT TOP 5 * FROM vw_ProductDetails
    WHERE CategoryName = @CategoryName
    ORDER BY CurrentPrice ASC;
END;
GO
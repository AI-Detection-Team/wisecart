-- 📊 VERİ BÜTÜNLÜĞÜ: CHECK CONSTRAINT - Fiyat 0'dan küçük olamaz
ALTER TABLE Products
ADD CONSTRAINT CK_Product_Price CHECK (CurrentPrice >= 0);

-- 📊 VERİ BÜTÜNLÜĞÜ: CHECK CONSTRAINT - Stok/Yorum sayısı negatif olamaz
ALTER TABLE Products
ADD CONSTRAINT CK_Product_ReviewCount CHECK (ReviewCount >= 0);

-- 📊 VERİ BÜTÜNLÜĞÜ: UNIQUE CONSTRAINT - Kullanıcı adı benzersiz olmalı (Aynı isimle iki kişi olamaz)
-- (Eğer tabloyu oluştururken unique yapmadıysak bu garanti eder)
ALTER TABLE Users
ADD CONSTRAINT UQ_Username UNIQUE (Username);

-- 📊 VERİ BÜTÜNLÜĞÜ: UNIQUE CONSTRAINT - Email benzersiz olmalı
ALTER TABLE Users
ADD CONSTRAINT UQ_Email UNIQUE (Email);

-- 5. Ürünlerin Markası Boş Olamaz (Zaten kodda var ama SQL tarafında da zorlayalım)
-- (Not: Eğer tabloda boş veri varsa bu hata verebilir, önce veriler temiz olmalı)
-- ALTER TABLE Products ALTER COLUMN Name NVARCHAR(500) NOT NULL; -- Örnek

-- 📊 PERFORMANS: VIEW - Önceden hesaplanmış JOIN sorgusu (Performans optimizasyonu)
-- View 1: Ürünlerin Detaylı Listesi (Marka ve Kategori İsimleriyle)
-- Her seferinde JOIN yapmak yerine view kullanarak sorgu performansını artırır
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

-- 📊 PERFORMANS: VIEW - Önceden hesaplanmış aggregate sorgusu (Performans optimizasyonu)
-- View 2: Kategori Bazlı Ortalama Fiyat Analizi
-- GROUP BY ve AVG işlemleri önceden hesaplanır, sorgu hızlanır
CREATE VIEW vw_CategoryStats AS
SELECT 
    c.Name AS CategoryName, 
    COUNT(p.Id) AS ProductCount, 
    AVG(p.CurrentPrice) AS AveragePrice
FROM Products p
JOIN Categories c ON p.CategoryId = c.Id
GROUP BY c.Name;
GO

-- 📊 PERFORMANS: VIEW + TOP 50 - Sadece ilk 50 kaydı çeker (Performans optimizasyonu)
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

-- 📊 PERFORMANS: VIEW - Önceden hesaplanmış aggregate sorgusu (Performans optimizasyonu)
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

-- 📊 PERFORMANS: STORED PROCEDURE - Önceden derlenmiş sorgu (Performans optimizasyonu)
-- Proc 1: Belirli bir fiyat aralığındaki ürünleri getir
-- Kullanımı: EXEC sp_GetProductsByPriceRange 10000, 20000
-- Stored procedure'lar önceden derlenir ve daha hızlı çalışır
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

-- 📊 PERFORMANS: STORED PROCEDURE + TOP 5 - Önceden derlenmiş sorgu (Performans optimizasyonu)
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




--10.12.2025


-- 📊 VERİ BÜTÜNLÜĞÜ: CHECK CONSTRAINT - Fiyat Asla Negatif Olamaz
ALTER TABLE Products ADD CONSTRAINT CK_Price_Positive CHECK (CurrentPrice >= 0);

-- Ürün İsimleri Tekrar Etmesin (Aynı isimle 2. ürün girilemesin)
-- (Not: Eğer veride tekrar varsa bu hata verir, önce temizlik gerekebilir)
-- ALTER TABLE Products ADD CONSTRAINT UQ_ProductName UNIQUE (Name);

-- 📊 VERİ BÜTÜNLÜĞÜ: CHECK CONSTRAINT - Stok/Yorum Sayısı 0'dan küçük olamaz
ALTER TABLE Products ADD CONSTRAINT CK_Review_Positive CHECK (ReviewCount >= 0);


-- 📊 PERFORMANS: VIEW - Önceden hesaplanmış aggregate sorgusu (Performans optimizasyonu)
-- Kategori Bazlı Fiyat Analizi Raporu
CREATE VIEW vw_CategoryAnalytics AS
SELECT 
    c.Name AS Kategori,
    COUNT(p.Id) AS UrunSayisi,
    AVG(p.CurrentPrice) AS OrtalamaFiyat,
    MAX(p.CurrentPrice) AS EnPahali,
    MIN(p.CurrentPrice) AS EnUcuz
FROM Products p
JOIN Categories c ON p.CategoryId = c.Id
GROUP BY c.Name;
GO




-- 📊 PERFORMANS: STORED PROCEDURE - Önceden derlenmiş sorgu (Performans optimizasyonu)
-- Fiyat Aralığına Göre Ürün Getiren Fonksiyon
CREATE PROCEDURE sp_GetProductsByRange
    @MinPrice float,
    @MaxPrice float
AS
BEGIN
    SELECT Name, CurrentPrice FROM Products
    WHERE CurrentPrice BETWEEN @MinPrice AND @MaxPrice
    ORDER BY CurrentPrice ASC
END;
GO
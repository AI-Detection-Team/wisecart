-- ============================================
-- WISECART VERİ AMBARI (DATA WAREHOUSE) OLUŞTURMA
-- Yıldız Şeması (Star Schema) Tasarımı
-- ============================================

-- 1. VERİ AMBARI VERİTABANI OLUŞTUR
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'WiseCartDW')
BEGIN
    CREATE DATABASE WiseCartDW;
    PRINT '✅ WiseCartDW veritabanı oluşturuldu.';
END
ELSE
BEGIN
    PRINT '⚠️ WiseCartDW veritabanı zaten mevcut.';
END
GO

USE WiseCartDW;
GO

-- ============================================
-- 2. DIMENSION TABLOLARI (Boyut Tabloları)
-- ============================================

-- 2.1. DimDate (Zaman Boyutu) - OLAP için kritik!
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[DimDate]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[DimDate] (
        [DateKey] INT NOT NULL PRIMARY KEY,  -- YYYYMMDD formatında (örn: 20250115)
        [Date] DATE NOT NULL,
        [Day] INT NOT NULL,
        [Month] INT NOT NULL,
        [Year] INT NOT NULL,
        [Quarter] INT NOT NULL,  -- 1, 2, 3, 4
        [MonthName] NVARCHAR(20) NOT NULL,  -- Ocak, Şubat, vb.
        [DayOfWeek] INT NOT NULL,  -- 1=Pazartesi, 7=Pazar
        [DayName] NVARCHAR(20) NOT NULL,  -- Pazartesi, Salı, vb.
        [IsWeekend] BIT NOT NULL,  -- 0=Hafta içi, 1=Hafta sonu
        [IsHoliday] BIT NOT NULL DEFAULT 0  -- Türkiye için özel günler
    );
    
    -- 📊 INDEX: Date kolonu üzerinde index (Tarih bazlı sorguları hızlandırır)
    CREATE INDEX IX_DimDate_Date ON DimDate([Date]);
    
    -- 📊 INDEX: Composite Index - Year ve Month birlikte (Yıl/Ay bazlı analizleri hızlandırır)
    CREATE INDEX IX_DimDate_YearMonth ON DimDate([Year], [Month]);
    
    PRINT '✅ DimDate tablosu oluşturuldu.';
END
GO

-- 2.2. DimCategory (Kategori Boyutu)
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[DimCategory]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[DimCategory] (
        [CategoryKey] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [CategoryId] INT NOT NULL,  -- Source system'den gelen ID
        [CategoryName] NVARCHAR(100) NOT NULL,
        [CategoryDescription] NVARCHAR(500) NULL,
        [ValidFrom] DATE NOT NULL DEFAULT GETDATE(),
        [ValidTo] DATE NULL,  -- SCD Type 2 için (şimdilik NULL)
        [IsCurrent] BIT NOT NULL DEFAULT 1
    );
    
    -- 📊 INDEX: UNIQUE INDEX - CategoryId üzerinde (SCD Type 2 için sadece aktif kayıtlar)
    -- WHERE [IsCurrent] = 1: Sadece aktif kayıtlar için unique constraint
    CREATE UNIQUE INDEX IX_DimCategory_CategoryId ON DimCategory([CategoryId]) WHERE [IsCurrent] = 1;
    
    PRINT '✅ DimCategory tablosu oluşturuldu.';
END
GO

-- 2.3. DimBrand (Marka Boyutu)
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[DimBrand]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[DimBrand] (
        [BrandKey] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [BrandId] INT NOT NULL,  -- Source system'den gelen ID
        [BrandName] NVARCHAR(100) NOT NULL,
        [BrandCountry] NVARCHAR(50) NULL,  -- Ülke bilgisi (opsiyonel)
        [ValidFrom] DATE NOT NULL DEFAULT GETDATE(),
        [ValidTo] DATE NULL,
        [IsCurrent] BIT NOT NULL DEFAULT 1
    );
    
    -- 📊 INDEX: UNIQUE INDEX - BrandId üzerinde (SCD Type 2 için sadece aktif kayıtlar)
    -- WHERE [IsCurrent] = 1: Sadece aktif kayıtlar için unique constraint
    CREATE UNIQUE INDEX IX_DimBrand_BrandId ON DimBrand([BrandId]) WHERE [IsCurrent] = 1;
    
    PRINT '✅ DimBrand tablosu oluşturuldu.';
END
GO

-- 2.4. DimProduct (Ürün Boyutu)
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[DimProduct]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[DimProduct] (
        [ProductKey] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [ProductId] INT NOT NULL,  -- Source system'den gelen ID
        [ProductName] NVARCHAR(500) NOT NULL,
        [ProductModel] NVARCHAR(255) NULL,
        [CategoryKey] INT NOT NULL,  -- DimCategory'e FK
        [BrandKey] INT NOT NULL,  -- DimBrand'e FK
        [ValidFrom] DATE NOT NULL DEFAULT GETDATE(),
        [ValidTo] DATE NULL,
        [IsCurrent] BIT NOT NULL DEFAULT 1
    );
    
    ALTER TABLE [dbo].[DimProduct]
    ADD CONSTRAINT FK_DimProduct_Category FOREIGN KEY ([CategoryKey]) 
        REFERENCES [dbo].[DimCategory]([CategoryKey]);
    
    ALTER TABLE [dbo].[DimProduct]
    ADD CONSTRAINT FK_DimProduct_Brand FOREIGN KEY ([BrandKey]) 
        REFERENCES [dbo].[DimBrand]([BrandKey]);
    
    -- 📊 INDEX: UNIQUE INDEX - ProductId üzerinde (SCD Type 2 için sadece aktif kayıtlar)
    CREATE UNIQUE INDEX IX_DimProduct_ProductId ON DimProduct([ProductId]) WHERE [IsCurrent] = 1;
    
    -- 📊 INDEX: CategoryKey üzerinde index (Kategori bazlı sorguları hızlandırır)
    CREATE INDEX IX_DimProduct_Category ON DimProduct([CategoryKey]);
    
    -- 📊 INDEX: BrandKey üzerinde index (Marka bazlı sorguları hızlandırır)
    CREATE INDEX IX_DimProduct_Brand ON DimProduct([BrandKey]);
    
    PRINT '✅ DimProduct tablosu oluşturuldu.';
END
GO

-- 2.5. DimUser (Kullanıcı Boyutu) - Favoriler analizi için
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[DimUser]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[DimUser] (
        [UserKey] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [UserId] INT NOT NULL,  -- Source system'den gelen ID
        [Username] NVARCHAR(50) NOT NULL,
        [UserRole] NVARCHAR(50) NULL,  -- Admin, User
        [RegistrationDate] DATE NULL,
        [ValidFrom] DATE NOT NULL DEFAULT GETDATE(),
        [ValidTo] DATE NULL,
        [IsCurrent] BIT NOT NULL DEFAULT 1
    );
    
    -- 📊 INDEX: UNIQUE INDEX - UserId üzerinde (SCD Type 2 için sadece aktif kayıtlar)
    CREATE UNIQUE INDEX IX_DimUser_UserId ON DimUser([UserId]) WHERE [IsCurrent] = 1;
    
    PRINT '✅ DimUser tablosu oluşturuldu.';
END
GO

-- ============================================
-- 3. FACT TABLE (Olgu Tablosu) - YILDIZ ŞEMASININ MERKEZİ
-- ============================================

-- 3.1. FactSales (Satış/Fiyat Geçmişi Olgu Tablosu)
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[FactSales]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[FactSales] (
        [FactSalesId] BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        
        -- FOREIGN KEYS (Dimension'lara bağlantılar)
        [DateKey] INT NOT NULL,  -- DimDate
        [ProductKey] INT NOT NULL,  -- DimProduct
        -- 📊 PERFORMANS: Denormalizasyon - CategoryKey ve BrandKey Fact tablosunda tekrarlanır
        -- JOIN işlemlerini azaltarak OLAP sorgularını hızlandırır
        [CategoryKey] INT NOT NULL,  -- DimCategory (denormalize edilmiş, performans için)
        [BrandKey] INT NOT NULL,  -- DimBrand (denormalize edilmiş, performans için)
        
        -- MEASURES (Ölçümler - OLAP Cube'da kullanılacak)
        [Price] FLOAT NOT NULL,  -- Ürün fiyatı
        [PriceChange] FLOAT NULL,  -- Önceki fiyata göre değişim
        [PriceChangePercent] FLOAT NULL,  -- Yüzde değişim
        [ReviewCount] INT NULL,  -- Yorum sayısı
        [IsPriceIncrease] BIT NULL,  -- Fiyat artışı mı? (1=Artış, 0=Azalış)
        
        -- METADATA
        [SourceSystemId] INT NULL,  -- Kaynak sistem ID (PriceHistory.Id)
        [LoadDate] DATETIME NOT NULL DEFAULT GETDATE()  -- ETL yükleme tarihi
    );
    
    -- FOREIGN KEY CONSTRAINTS
    ALTER TABLE [dbo].[FactSales]
    ADD CONSTRAINT FK_FactSales_Date FOREIGN KEY ([DateKey]) 
        REFERENCES [dbo].[DimDate]([DateKey]);
    
    ALTER TABLE [dbo].[FactSales]
    ADD CONSTRAINT FK_FactSales_Product FOREIGN KEY ([ProductKey]) 
        REFERENCES [dbo].[DimProduct]([ProductKey]);
    
    ALTER TABLE [dbo].[FactSales]
    ADD CONSTRAINT FK_FactSales_Category FOREIGN KEY ([CategoryKey]) 
        REFERENCES [dbo].[DimCategory]([CategoryKey]);
    
    ALTER TABLE [dbo].[FactSales]
    ADD CONSTRAINT FK_FactSales_Brand FOREIGN KEY ([BrandKey]) 
        REFERENCES [dbo].[DimBrand]([BrandKey]);
    
    -- 📊 INDEX: Fact tablolarında index'ler performans için kritik! (OLAP sorgularını hızlandırır)
    -- DateKey üzerinde index (Tarih bazlı analizler)
    CREATE INDEX IX_FactSales_Date ON FactSales([DateKey]);
    
    -- ProductKey üzerinde index (Ürün bazlı analizler)
    CREATE INDEX IX_FactSales_Product ON FactSales([ProductKey]);
    
    -- CategoryKey üzerinde index (Kategori bazlı analizler)
    CREATE INDEX IX_FactSales_Category ON FactSales([CategoryKey]);
    
    -- BrandKey üzerinde index (Marka bazlı analizler)
    CREATE INDEX IX_FactSales_Brand ON FactSales([BrandKey]);
    
    -- 📊 INDEX: Composite Index - DateKey ve ProductKey birlikte (Tarih+Ürün bazlı analizler)
    CREATE INDEX IX_FactSales_DateProduct ON FactSales([DateKey], [ProductKey]);
    
    PRINT '✅ FactSales tablosu oluşturuldu.';
END
GO

-- 3.2. FactFavorites (Favoriler Olgu Tablosu) - Kullanıcı davranış analizi için
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[FactFavorites]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[FactFavorites] (
        [FactFavoritesId] BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        
        -- FOREIGN KEYS
        [DateKey] INT NOT NULL,  -- DimDate
        [UserKey] INT NOT NULL,  -- DimUser
        [ProductKey] INT NOT NULL,  -- DimProduct
        [CategoryKey] INT NOT NULL,  -- DimCategory
        [BrandKey] INT NOT NULL,  -- DimBrand
        
        -- MEASURES
        [FavoriteCount] INT NOT NULL DEFAULT 1,  -- Kaç kez favorilere eklendi (genelde 1)
        [IsActive] BIT NOT NULL DEFAULT 1,  -- Hala favorilerde mi?
        
        -- METADATA
        [SourceSystemId] INT NULL,  -- Kaynak sistem ID (Favorites.Id)
        [LoadDate] DATETIME NOT NULL DEFAULT GETDATE()
    );
    
    -- FOREIGN KEY CONSTRAINTS
    ALTER TABLE [dbo].[FactFavorites]
    ADD CONSTRAINT FK_FactFavorites_Date FOREIGN KEY ([DateKey]) 
        REFERENCES [dbo].[DimDate]([DateKey]);
    
    ALTER TABLE [dbo].[FactFavorites]
    ADD CONSTRAINT FK_FactFavorites_User FOREIGN KEY ([UserKey]) 
        REFERENCES [dbo].[DimUser]([UserKey]);
    
    ALTER TABLE [dbo].[FactFavorites]
    ADD CONSTRAINT FK_FactFavorites_Product FOREIGN KEY ([ProductKey]) 
        REFERENCES [dbo].[DimProduct]([ProductKey]);
    
    ALTER TABLE [dbo].[FactFavorites]
    ADD CONSTRAINT FK_FactFavorites_Category FOREIGN KEY ([CategoryKey]) 
        REFERENCES [dbo].[DimCategory]([CategoryKey]);
    
    ALTER TABLE [dbo].[FactFavorites]
    ADD CONSTRAINT FK_FactFavorites_Brand FOREIGN KEY ([BrandKey]) 
        REFERENCES [dbo].[DimBrand]([BrandKey]);
    
    -- 📊 INDEX: FactFavorites tablosunda index'ler (Kullanıcı davranış analizlerini hızlandırır)
    -- DateKey üzerinde index (Tarih bazlı favori analizleri)
    CREATE INDEX IX_FactFavorites_Date ON FactFavorites([DateKey]);
    
    -- UserKey üzerinde index (Kullanıcı bazlı favori analizleri)
    CREATE INDEX IX_FactFavorites_User ON FactFavorites([UserKey]);
    
    -- ProductKey üzerinde index (Ürün bazlı favori analizleri)
    CREATE INDEX IX_FactFavorites_Product ON FactFavorites([ProductKey]);
    
    PRINT '✅ FactFavorites tablosu oluşturuldu.';
END
GO

-- ============================================
-- 4. ETL CONTROL TABLE (ETL Kontrol Tablosu)
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[ETLControl]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[ETLControl] (
        [ETLControlId] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [TableName] NVARCHAR(100) NOT NULL,  -- Hangi tablo için?
        [LastLoadDate] DATETIME NULL,  -- Son yükleme tarihi
        [LastLoadId] INT NULL,  -- Son yüklenen ID (incremental load için)
        [Status] NVARCHAR(50) NULL,  -- Success, Failed, InProgress
        [RecordCount] INT NULL,  -- Kaç kayıt yüklendi?
        [ErrorMessage] NVARCHAR(MAX) NULL  -- Hata mesajı (varsa)
    );
    
    -- 📊 INDEX: UNIQUE INDEX - TableName üzerinde (ETL kontrol tablosunda her tablo için tek kayıt)
    CREATE UNIQUE INDEX IX_ETLControl_TableName ON ETLControl([TableName]);
    
    -- İlk kayıtları ekle
    INSERT INTO ETLControl ([TableName], [LastLoadDate], [Status])
    VALUES 
        ('DimDate', NULL, 'Pending'),
        ('DimCategory', NULL, 'Pending'),
        ('DimBrand', NULL, 'Pending'),
        ('DimProduct', NULL, 'Pending'),
        ('DimUser', NULL, 'Pending'),
        ('FactSales', NULL, 'Pending'),
        ('FactFavorites', NULL, 'Pending');
    
    PRINT '✅ ETLControl tablosu oluşturuldu.';
END
GO

PRINT '';
PRINT '========================================';
PRINT '✅ VERİ AMBARI (YILDIZ ŞEMASI) OLUŞTURULDU!';
PRINT '========================================';
PRINT '';
PRINT 'DIMENSION TABLOLARI:';
PRINT '  1. DimDate (Zaman boyutu)';
PRINT '  2. DimCategory (Kategori boyutu)';
PRINT '  3. DimBrand (Marka boyutu)';
PRINT '  4. DimProduct (Ürün boyutu)';
PRINT '  5. DimUser (Kullanıcı boyutu)';
PRINT '';
PRINT 'FACT TABLOLARI:';
PRINT '  1. FactSales (Fiyat geçmişi olguları)';
PRINT '  2. FactFavorites (Favoriler olguları)';
PRINT '';
PRINT 'ETL KONTROL:';
PRINT '  1. ETLControl (ETL yönetim tablosu)';
PRINT '';
PRINT 'SONRAKI ADIM: ETL scriptlerini çalıştırın!';
PRINT '';


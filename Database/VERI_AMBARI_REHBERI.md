# 🏗️ Veri Ambarı (Data Warehouse) Oluşturma Rehberi

## 📋 GENEL BAKIŞ

Bu rehber, WiseCart projesi için **yıldız şeması (star schema)** ile veri ambarı oluşturma sürecini açıklar.

---

## 🎯 YILDIZ ŞEMASI (STAR SCHEMA) NEDİR?

**Yıldız şeması**, veri ambarı tasarımında en yaygın kullanılan şemadır:

```
        DimDate
           |
           |
    FactSales ---- DimProduct ---- DimCategory
           |           |
           |           |
        DimBrand    DimBrand
```

### Özellikler:
- **Fact Table (Olgu Tablosu)**: Merkezde, ölçümler (measures) içerir
- **Dimension Tables (Boyut Tabloları)**: Etrafında, analiz boyutları içerir
- **Denormalize**: Performans için bazı veriler tekrarlanabilir
- **OLAP için optimize**: Hızlı analiz sorguları için tasarlanmış

---

## 📁 DOSYA YAPISI

```
Database/
├── create_data_warehouse.sql      # Veri ambarı oluşturma
├── etl_load_dimensions.sql        # Dimension tablolarını yükleme
├── etl_load_facts.sql             # Fact tablolarını yükleme
├── user_defined_functions.sql     # Kullanıcı tanımlı fonksiyonlar
├── OLAP_CUBE_REHBERI.md           # OLAP Cube rehberi
├── SSIS_PACKAGE_REHBERI.md        # SSIS package rehberi
└── VERI_AMBARI_REHBERI.md         # Bu dosya
```

---

## 🚀 ADIM ADIM KURULUM

### Adım 1: Veri Ambarı Oluşturma

```sql
-- create_data_warehouse.sql dosyasını çalıştırın
-- Bu script:
-- 1. WiseCartDW veritabanını oluşturur
-- 2. Dimension tablolarını oluşturur (DimDate, DimCategory, DimBrand, DimProduct, DimUser)
-- 3. Fact tablolarını oluşturur (FactSales, FactFavorites)
-- 4. ETLControl tablosunu oluşturur
```

**Çalıştırma:**
```bash
# SQL Server Management Studio veya Azure Data Studio'da
# Dosyayı açın ve F5 ile çalıştırın
```

### Adım 2: Dimension Tablolarını Yükleme

```sql
-- etl_load_dimensions.sql dosyasını çalıştırın
-- Bu script:
-- 1. DimDate'i doldurur (son 5 yıl + gelecek 1 yıl)
-- 2. DimCategory'i WiseCartDB'den yükler
-- 3. DimBrand'i WiseCartDB'den yükler
-- 4. DimProduct'i WiseCartDB'den yükler
-- 5. DimUser'i WiseCartDB'den yükler
```

**Çalıştırma:**
```bash
# SQL Server Management Studio veya Azure Data Studio'da
# Dosyayı açın ve F5 ile çalıştırın
```

### Adım 3: Fact Tablolarını Yükleme

```sql
-- etl_load_facts.sql dosyasını çalıştırın
-- Bu script:
-- 1. FactSales'i PriceHistory'den yükler
-- 2. FactFavorites'i Favorites'den yükler
-- 3. Incremental load yapar (sadece yeni kayıtlar)
```

**Çalıştırma:**
```bash
# SQL Server Management Studio veya Azure Data Studio'da
# Dosyayı açın ve F5 ile çalıştırın
```

### Adım 4: Kullanıcı Tanımlı Fonksiyonlar

```sql
-- user_defined_functions.sql dosyasını çalıştırın
-- Bu script:
-- 1. fn_CalculateDiscountedPrice - İndirimli fiyat hesaplama
-- 2. fn_GetCategoryAveragePrice - Kategori ortalama fiyatı
-- 3. fn_CalculatePriceChangePercent - Fiyat değişim yüzdesi (BONUS)
```

**Çalıştırma:**
```bash
# SQL Server Management Studio veya Azure Data Studio'da
# Dosyayı açın ve F5 ile çalıştırın
```

---

## 🔄 ETL SÜRECİ

### İlk Yükleme (Full Load)
1. `create_data_warehouse.sql` - Veri ambarı oluştur
2. `etl_load_dimensions.sql` - Dimension'ları yükle
3. `etl_load_facts.sql` - Fact'leri yükle

### Günlük Yükleme (Incremental Load)
1. `etl_load_facts.sql` - Sadece yeni kayıtları yükle
2. ETLControl tablosu son yükleme tarihini takip eder

### SSIS Package ile Otomatikleştirme
- `SSIS_PACKAGE_REHBERI.md` dosyasına bakın
- SQL Server Agent Job ile günlük çalıştırma

---

## 📊 VERİ AMBARI YAPISI

### Dimension Tables (Boyut Tabloları)

#### DimDate
- **Amaç**: Zaman bazlı analiz
- **Özellikler**: Year, Quarter, Month, Day, IsWeekend, vb.
- **Kullanım**: Tarih bazlı raporlama

#### DimCategory
- **Amaç**: Kategori bazlı analiz
- **Özellikler**: CategoryName, CategoryDescription
- **Kullanım**: Kategori bazlı fiyat analizi

#### DimBrand
- **Amaç**: Marka bazlı analiz
- **Özellikler**: BrandName, BrandCountry
- **Kullanım**: Marka performans analizi

#### DimProduct
- **Amaç**: Ürün bazlı analiz
- **Özellikler**: ProductName, ProductModel
- **Kullanım**: Ürün bazlı fiyat takibi

#### DimUser
- **Amaç**: Kullanıcı bazlı analiz
- **Özellikler**: Username, UserRole
- **Kullanım**: Kullanıcı davranış analizi

### Fact Tables (Olgu Tabloları)

#### FactSales
- **Amaç**: Fiyat geçmişi analizi
- **Measures**: Price, PriceChange, PriceChangePercent, ReviewCount
- **Dimensions**: DateKey, ProductKey, CategoryKey, BrandKey

#### FactFavorites
- **Amaç**: Favoriler analizi
- **Measures**: FavoriteCount, IsActive
- **Dimensions**: DateKey, UserKey, ProductKey, CategoryKey, BrandKey

---

## 🔍 ÖRNEK SORGULAR

### Kategori Bazlı Ortalama Fiyat
```sql
SELECT 
    dc.CategoryName,
    AVG(fs.Price) AS AveragePrice,
    COUNT(*) AS RecordCount
FROM FactSales fs
INNER JOIN DimCategory dc ON fs.CategoryKey = dc.CategoryKey
GROUP BY dc.CategoryName
ORDER BY AveragePrice DESC;
```

### Aylık Fiyat Değişimi
```sql
SELECT 
    dd.Year,
    dd.MonthName,
    SUM(fs.PriceChange) AS TotalPriceChange,
    AVG(fs.PriceChangePercent) AS AvgPriceChangePercent
FROM FactSales fs
INNER JOIN DimDate dd ON fs.DateKey = dd.DateKey
GROUP BY dd.Year, dd.MonthName
ORDER BY dd.Year, dd.Month;
```

### En Çok Favorilenen Ürünler
```sql
SELECT TOP 10
    dp.ProductName,
    dc.CategoryName,
    db.BrandName,
    SUM(ff.FavoriteCount) AS TotalFavorites
FROM FactFavorites ff
INNER JOIN DimProduct dp ON ff.ProductKey = dp.ProductKey
INNER JOIN DimCategory dc ON ff.CategoryKey = dc.CategoryKey
INNER JOIN DimBrand db ON ff.BrandKey = db.BrandKey
GROUP BY dp.ProductName, dc.CategoryName, db.BrandName
ORDER BY TotalFavorites DESC;
```

---

## ✅ KONTROL LİSTESİ

### Veri Ambarı Oluşturma
- [ ] `create_data_warehouse.sql` çalıştırıldı mı?
- [ ] WiseCartDW veritabanı oluşturuldu mu?
- [ ] Dimension tabloları oluşturuldu mu?
- [ ] Fact tabloları oluşturuldu mu?
- [ ] ETLControl tablosu oluşturuldu mu?

### Veri Yükleme
- [ ] `etl_load_dimensions.sql` çalıştırıldı mı?
- [ ] DimDate dolduruldu mu?
- [ ] DimCategory yüklendi mi?
- [ ] DimBrand yüklendi mi?
- [ ] DimProduct yüklendi mi?
- [ ] DimUser yüklendi mi?
- [ ] `etl_load_facts.sql` çalıştırıldı mı?
- [ ] FactSales yüklendi mi?
- [ ] FactFavorites yüklendi mi?

### Fonksiyonlar
- [ ] `user_defined_functions.sql` çalıştırıldı mı?
- [ ] fn_CalculateDiscountedPrice oluşturuldu mu?
- [ ] fn_GetCategoryAveragePrice oluşturuldu mu?
- [ ] Fonksiyonlar test edildi mi?

### SSIS Package
- [ ] SSIS projesi oluşturuldu mu?
- [ ] 5+ package oluşturuldu mu?
- [ ] Package'lar test edildi mi?

### OLAP Cube
- [ ] SSAS projesi oluşturuldu mu?
- [ ] Cube oluşturuldu mu?
- [ ] 5+ measure tanımlandı mı?
- [ ] 5+ dimension eklendi mi?
- [ ] Cube deploy edildi mi?
- [ ] Cube process edildi mi?

---

## 🎯 SONRAKI ADIMLAR

1. **SSIS Package Oluşturma**: `SSIS_PACKAGE_REHBERI.md` dosyasına bakın
2. **OLAP Cube Oluşturma**: `OLAP_CUBE_REHBERI.md` dosyasına bakın
3. **Web Entegrasyonu**: OLAP Cube'u web'e bağlayın

---

## 📚 EK BİLGİLER

### Yıldız Şeması vs Kar Tanesi Şeması
- **Yıldız Şeması**: Dimension'lar denormalize (daha hızlı)
- **Kar Tanesi Şeması**: Dimension'lar normalize (daha az yer)

### Performans İpuçları
- Index'ler kullanıldı
- Partitioning yapılabilir (büyük fact tabloları için)
- Columnstore index kullanılabilir (SQL Server 2012+)

### Veri Kalitesi
- ETL sırasında veri doğrulama yapılmalı
- Hatalı veriler ayrı tabloya yazılmalı
- Data cleansing package'ları kullanılmalı

---

## 🎉 SONUÇ

Bu rehberi takip ederek:
- ✅ Yıldız şeması ile veri ambarı oluşturuldu
- ✅ Dimension ve Fact tabloları hazır
- ✅ ETL scriptleri hazır
- ✅ Kullanıcı tanımlı fonksiyonlar eklendi

**Veri ambarı hazır! Şimdi SSIS ve OLAP Cube'a geçebilirsiniz!** 🚀






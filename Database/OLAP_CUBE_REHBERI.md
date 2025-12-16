# 📊 OLAP Cube Oluşturma Rehberi

## 🎯 İsterler
- ✅ Multidimensional SSAS projesi oluşturma (10 puan)
- ✅ Küp içerisinde en az 5 adet measure tanımlama (10 puan)
- ✅ Küp içerisinde en az 5 adet dimension barındırma (10 puan)
- ✅ SQL Server Analysis Services kullanarak küp analizi (10 puan)
- ✅ OLAP kübünü bir ön yüze bağlayarak web projesi oluşturma (10 puan)

**Toplam: 50 puan**

---

## 📋 ÖN HAZIRLIK

### 1. SQL Server Analysis Services (SSAS) Kurulumu
- SQL Server kurulumunda **Analysis Services** seçeneğini işaretleyin
- **Multidimensional Mode** seçin (Tabular değil!)

### 2. Visual Studio Kurulumu
- **SQL Server Data Tools (SSDT)** veya **Visual Studio** ile **Analysis Services** projesi şablonu gerekli

---

## 🏗️ YILDIZ ŞEMASI (STAR SCHEMA)

Veri ambarımız zaten **yıldız şeması** ile tasarlandı:

```
        DimDate
           |
           |
    FactSales ---- DimProduct ---- DimCategory
           |           |
           |           |
        DimBrand    DimBrand
```

**Fact Table (Olgu Tablosu):**
- `FactSales` - Fiyat geçmişi verileri

**Dimension Tables (Boyut Tabloları):**
- `DimDate` - Zaman boyutu
- `DimProduct` - Ürün boyutu
- `DimCategory` - Kategori boyutu
- `DimBrand` - Marka boyutu
- `DimUser` - Kullanıcı boyutu (FactFavorites için)

---

## 📦 SSAS PROJESİ OLUŞTURMA ADIMLARI

### Adım 1: Visual Studio'da Yeni Proje
1. **File > New > Project**
2. **Business Intelligence > Analysis Services**
3. **Analysis Services Multidimensional and Data Mining Project** seçin
4. Proje adı: `WiseCartOLAP`

### Adım 2: Data Source (Veri Kaynağı) Oluşturma
1. **Solution Explorer**'da **Data Sources** sağ tık > **New Data Source**
2. **Data Source Wizard** açılır
3. **New** butonuna tıklayın
4. **Connection Properties**:
   - Server name: `localhost` (veya SQL Server adresiniz)
   - Database name: `WiseCartDW` (Veri ambarı!)
   - Authentication: Windows Authentication veya SQL Server Authentication
5. **Data Source Name**: `WiseCartDW_DataSource`
6. **Finish**

### Adım 3: Data Source View (DSV) Oluşturma
1. **Data Source Views** sağ tık > **New Data Source View**
2. **Data Source Wizard**:
   - Data Source: `WiseCartDW_DataSource` seçin
   - **Select Tables and Views**:
     - ✅ `DimDate`
     - ✅ `DimCategory`
     - ✅ `DimBrand`
     - ✅ `DimProduct`
     - ✅ `DimUser`
     - ✅ `FactSales`
     - ✅ `FactFavorites`
3. **Finish**

### Adım 4: CUBE Oluşturma
1. **Cubes** sağ tık > **New Cube**
2. **Cube Wizard**:
   - **Use existing tables** seçin
   - **Select measure group tables**: `FactSales` seçin
   - **Select measures** (en az 5 adet):
     - ✅ `Price` (Sum)
     - ✅ `PriceChange` (Sum)
     - ✅ `PriceChangePercent` (Average)
     - ✅ `ReviewCount` (Sum)
     - ✅ `IsPriceIncrease` (Count)
   - **Select dimensions** (en az 5 adet):
     - ✅ `DimDate`
     - ✅ `DimProduct`
     - ✅ `DimCategory`
     - ✅ `DimBrand`
     - ✅ `DimUser` (FactFavorites'den)
3. **Cube Name**: `WiseCartSalesCube`
4. **Finish**

### Adım 5: DIMENSION Yapılandırması

#### DimDate (Zaman Boyutu)
- **Hierarchy** oluştur:
  - Year > Quarter > Month > Day
- **Attributes**:
  - DateKey
  - Year
  - Quarter
  - Month
  - MonthName
  - Day
  - DayName
  - IsWeekend

#### DimProduct (Ürün Boyutu)
- **Attributes**:
  - ProductKey
  - ProductName
  - ProductModel

#### DimCategory (Kategori Boyutu)
- **Attributes**:
  - CategoryKey
  - CategoryName

#### DimBrand (Marka Boyutu)
- **Attributes**:
  - BrandKey
  - BrandName

#### DimUser (Kullanıcı Boyutu)
- **Attributes**:
  - UserKey
  - Username
  - UserRole

### Adım 6: MEASURE Yapılandırması

**FactSales Measures:**
1. **TotalPrice** - Sum of Price
2. **AveragePrice** - Average of Price
3. **TotalPriceChange** - Sum of PriceChange
4. **AveragePriceChangePercent** - Average of PriceChangePercent
5. **TotalReviewCount** - Sum of ReviewCount
6. **PriceIncreaseCount** - Count of IsPriceIncrease = 1
7. **ProductCount** - Distinct Count of ProductKey

**FactFavorites Measures:**
1. **TotalFavorites** - Sum of FavoriteCount
2. **ActiveFavorites** - Sum of IsActive

---

## 🔧 CUBE DEPLOY VE PROCESS

### Adım 1: Deploy
1. **Solution Explorer**'da projeye sağ tık > **Deploy**
2. **Target Server**: `localhost` (veya SSAS server adresiniz)
3. **Database**: `WiseCartOLAP`
4. **Deploy** butonuna tıklayın

### Adım 2: Process
1. Deploy sonrası **Process** otomatik başlar
2. Veya **Solution Explorer**'da Cube'a sağ tık > **Process**
3. **Process Options**: **Process Full** seçin
4. **Run** butonuna tıklayın

---

## 📊 CUBE ANALİZİ

### SQL Server Management Studio (SSMS) ile
1. **SSMS**'i açın
2. **Connect** > **Analysis Services**
3. **WiseCartOLAP** database'ini genişletin
4. **Cubes** > **WiseCartSalesCube** sağ tık > **Browse**
5. **MDX Query** yazabilirsiniz:

```mdx
SELECT 
    [Measures].[TotalPrice] ON COLUMNS,
    [DimCategory].[CategoryName].MEMBERS ON ROWS
FROM [WiseCartSalesCube]
WHERE [DimDate].[Year].[2024]
```

### Excel ile
1. **Excel** açın
2. **Data** > **From Other Sources** > **From Analysis Services**
3. Server: `localhost`
4. Database: `WiseCartOLAP`
5. Cube: `WiseCartSalesCube`
6. **PivotTable** oluşturun

---

## 🌐 WEB ENTEGRASYONU

### Yöntem 1: Power BI Embedded (Önerilen)
1. **Power BI Desktop** ile cube'a bağlan
2. Rapor oluştur
3. **Power BI Embedded** ile web'e entegre et

### Yöntem 2: ADOMD.NET ile C# (.NET)
```csharp
using Microsoft.AnalysisServices.AdomdClient;

// Connection string
string connectionString = "Provider=MSOLAP;Data Source=localhost;Initial Catalog=WiseCartOLAP;";

using (AdomdConnection conn = new AdomdConnection(connectionString))
{
    conn.Open();
    
    // MDX Query
    string mdx = @"
        SELECT 
            [Measures].[TotalPrice] ON COLUMNS,
            [DimCategory].[CategoryName].MEMBERS ON ROWS
        FROM [WiseCartSalesCube]
    ";
    
    AdomdCommand cmd = new AdomdCommand(mdx, conn);
    AdomdDataReader reader = cmd.ExecuteReader();
    
    // Veriyi oku ve View'a gönder
    while (reader.Read())
    {
        // Process data
    }
}
```

### Yöntem 3: REST API (SSAS REST API)
```csharp
// HTTP Request ile MDX query gönder
var client = new HttpClient();
var response = await client.PostAsync(
    "http://localhost/olap/msmdpump.dll",
    new StringContent(mdxQuery)
);
```

### Yöntem 4: Chart.js / D3.js ile Görselleştirme
- ADOMD.NET'ten gelen veriyi JSON'a çevir
- Chart.js ile grafik oluştur
- Dashboard sayfası oluştur

---

## 📝 ÖRNEK WEB SAYFASI

### Controller (WiseCart_Web/Controllers/AnalyticsController.cs)
```csharp
public class AnalyticsController : Controller
{
    public IActionResult Dashboard()
    {
        // ADOMD.NET ile cube'dan veri çek
        // ViewBag'e gönder
        return View();
    }
}
```

### View (WiseCart_Web/Views/Analytics/Dashboard.cshtml)
```html
@{
    ViewData["Title"] = "Analitik Dashboard";
}

<div class="container">
    <h2>OLAP Cube Analizi</h2>
    
    <!-- Chart.js ile grafikler -->
    <canvas id="priceChart"></canvas>
    <canvas id="categoryChart"></canvas>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
    // Cube'dan gelen veriyi Chart.js ile göster
</script>
```

---

## ✅ KONTROL LİSTESİ

- [ ] SSAS kurulu mu?
- [ ] Veri ambarı (WiseCartDW) oluşturuldu mu?
- [ ] ETL scriptleri çalıştırıldı mı?
- [ ] SSAS projesi oluşturuldu mu?
- [ ] Data Source tanımlandı mı?
- [ ] Data Source View oluşturuldu mu?
- [ ] Cube oluşturuldu mu?
- [ ] En az 5 measure tanımlandı mı?
- [ ] En az 5 dimension eklendi mi?
- [ ] Cube deploy edildi mi?
- [ ] Cube process edildi mi?
- [ ] SSMS ile test edildi mi?
- [ ] Web entegrasyonu yapıldı mı?
- [ ] Dashboard sayfası oluşturuldu mu?

---

## 🎯 SONUÇ

Bu rehberi takip ederek:
- ✅ Multidimensional SSAS projesi oluşturulacak
- ✅ 5+ measure tanımlanacak
- ✅ 5+ dimension eklenecek
- ✅ Cube analizi yapılacak
- ✅ Web'e entegre edilecek

**Toplam 50 puan kazanılacak!** 🎉


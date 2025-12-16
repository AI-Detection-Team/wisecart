# 📦 SSIS Package Oluşturma Rehberi

## 🎯 İsterler
- ✅ ETL adımlarını takip edecek şekilde veri ambarı oluşturma (10 puan)
- ✅ En az 5 adet farklı türde SSIS package oluşturma (10 puan)
- ✅ Oluşturulan veri ambarını temel özellikleri barındırması (10 puan)

**Toplam: 30 puan**

---

## 📋 ÖN HAZIRLIK

### 1. SQL Server Integration Services (SSIS) Kurulumu
- SQL Server kurulumunda **Integration Services** seçeneğini işaretleyin
- **SQL Server Data Tools (SSDT)** kurulu olmalı

### 2. Visual Studio Kurulumu
- **Visual Studio** ile **SQL Server Integration Services Projects** extension'ı gerekli
- Veya **SQL Server Data Tools (SSDT)** ayrı kurulabilir

---

## 🏗️ SSIS PROJESİ OLUŞTURMA

### Adım 1: Yeni Proje
1. **Visual Studio** açın
2. **File > New > Project**
3. **Integration Services Project** seçin
4. Proje adı: `WiseCartETL`
5. **OK**

### Adım 2: Proje Yapısı
```
WiseCartETL/
├── Package.dtsx (Ana package)
├── LoadDimensions.dtsx (Dimension yükleme)
├── LoadFacts.dtsx (Fact yükleme)
├── DataCleansing.dtsx (Veri temizleme)
├── ErrorHandling.dtsx (Hata yönetimi)
└── IncrementalLoad.dtsx (Artımlı yükleme)
```

---

## 📦 PACKAGE 1: LoadDimensions.dtsx
**Tür:** Data Flow Task - Dimension Loading

### Görev:
WiseCartDB'den Dimension tablolarını WiseCartDW'ye yükler.

### Adımlar:
1. **Control Flow**'da **Data Flow Task** ekle
2. **Data Flow** içinde:
   - **OLE DB Source** (WiseCartDB)
     - Connection: `WiseCartDB`
     - Table: `Categories`
   - **Lookup Transformation** (DimCategory'de var mı kontrol)
   - **Conditional Split** (Yeni mi, güncelleme mi?)
   - **OLE DB Destination** (WiseCartDW)
     - Connection: `WiseCartDW`
     - Table: `DimCategory`
     - **Slowly Changing Dimension** wizard kullanılabilir

### Özellikler:
- ✅ SCD Type 2 desteği (tarih bazlı versiyonlama)
- ✅ Hata yönetimi
- ✅ Logging

---

## 📦 PACKAGE 2: LoadFacts.dtsx
**Tür:** Data Flow Task - Fact Loading

### Görev:
PriceHistory ve Favorites tablolarından Fact tablolarına veri yükler.

### Adımlar:
1. **Control Flow**'da **Data Flow Task** ekle
2. **Data Flow** içinde:
   - **OLE DB Source** (WiseCartDB.PriceHistory)
   - **Lookup Transformation** (DimDate, DimProduct lookup)
   - **Derived Column** (DateKey, ProductKey hesaplama)
   - **OLE DB Destination** (WiseCartDW.FactSales)

### Özellikler:
- ✅ Incremental load (sadece yeni kayıtlar)
- ✅ Dimension key lookup
- ✅ Measure hesaplama

---

## 📦 PACKAGE 3: DataCleansing.dtsx
**Tür:** Data Flow Task - Data Quality

### Görev:
Veri temizleme ve doğrulama işlemleri.

### Adımlar:
1. **Data Flow Task** ekle
2. **OLE DB Source** (WiseCartDB.Products)
3. **Data Conversion** (Fiyat formatı düzeltme)
4. **Conditional Split**:
   - Fiyat > 0
   - Fiyat < 200000 (mantıklı üst limit)
   - NULL kontrolü
5. **Derived Column** (Temizlenmiş fiyat)
6. **OLE DB Destination** (Temizlenmiş veri)

### Özellikler:
- ✅ Veri doğrulama
- ✅ Hatalı veri yönlendirme
- ✅ Veri dönüşümü

---

## 📦 PACKAGE 4: ErrorHandling.dtsx
**Tür:** Control Flow - Error Handling & Logging

### Görev:
Hata yönetimi ve loglama.

### Adımlar:
1. **Execute SQL Task** (ETLControl tablosunu kontrol et)
2. **For Loop Container** (Her tablo için)
3. **Try-Catch** benzeri yapı:
   - **Execute Package Task** (LoadDimensions)
   - **OnError Event Handler**:
     - **Execute SQL Task** (Hata kaydı)
     - **Send Mail Task** (Opsiyonel: hata bildirimi)
4. **Execute SQL Task** (ETLControl güncelle)

### Özellikler:
- ✅ Hata yakalama
- ✅ Loglama
- ✅ Bildirim sistemi

---

## 📦 PACKAGE 5: IncrementalLoad.dtsx
**Tür:** Control Flow - Incremental ETL

### Görev:
Sadece yeni/değişen kayıtları yükler.

### Adımlar:
1. **Execute SQL Task** (Son yükleme tarihini al)
2. **Data Flow Task**:
   - **OLE DB Source** (WHERE Date > LastLoadDate)
   - **Lookup** (Zaten var mı?)
   - **Conditional Split** (Yeni kayıtlar)
   - **OLE DB Destination**
3. **Execute SQL Task** (LastLoadDate güncelle)

### Özellikler:
- ✅ Artımlı yükleme
- ✅ Performans optimizasyonu
- ✅ Change Data Capture (CDC) benzeri

---

## 📦 PACKAGE 6 (BONUS): FullETL.dtsx
**Tür:** Control Flow - Master Package

### Görev:
Tüm ETL sürecini koordine eder.

### Adımlar:
1. **Execute SQL Task** (ETL başlangıç logu)
2. **Sequence Container** (Dimension'lar):
   - **Execute Package Task** (LoadDimensions)
3. **Sequence Container** (Fact'ler):
   - **Execute Package Task** (LoadFacts)
4. **Execute SQL Task** (ETL bitiş logu)
5. **Send Mail Task** (Başarı bildirimi)

### Özellikler:
- ✅ Workflow yönetimi
- ✅ Paralel çalıştırma
- ✅ Transaction yönetimi

---

## 🔧 PACKAGE YAPILANDIRMASI

### Connection Managers
1. **WiseCartDB_Connection**
   - Type: OLE DB
   - Provider: SQL Server Native Client
   - Server: localhost
   - Database: WiseCartDB

2. **WiseCartDW_Connection**
   - Type: OLE DB
   - Provider: SQL Server Native Client
   - Server: localhost
   - Database: WiseCartDW

3. **File_Connection** (Log dosyası için)
   - Type: Flat File
   - Path: C:\ETLLogs\WiseCart.log

### Variables
- `User::LastLoadDate` (DATETIME)
- `User::ETLStatus` (STRING)
- `User::RecordCount` (INT32)
- `User::ErrorCount` (INT32)

### Logging
1. **SSIS Logging** etkinleştir
2. **Log Provider**: SQL Server
3. **Log Events**: OnError, OnWarning, OnInformation

---

## 📊 PACKAGE TÜRLERİ ÖZET

| Package | Tür | Açıklama |
|---------|-----|----------|
| LoadDimensions | Data Flow | Dimension yükleme |
| LoadFacts | Data Flow | Fact yükleme |
| DataCleansing | Data Flow | Veri temizleme |
| ErrorHandling | Control Flow | Hata yönetimi |
| IncrementalLoad | Control Flow | Artımlı yükleme |
| FullETL | Control Flow | Master package |

**Toplam: 6 package (5 gerekli + 1 bonus)**

---

## 🚀 PACKAGE ÇALIŞTIRMA

### Visual Studio'dan
1. Package'a sağ tık > **Execute Package**
2. Veya **Debug > Start Debugging**

### SQL Server Agent Job
1. **SQL Server Management Studio** açın
2. **SQL Server Agent > Jobs** sağ tık > **New Job**
3. **Steps** sekmesi:
   - **New Step**
   - Type: **SQL Server Integration Services Package**
   - Package source: **File system**
   - Package: `C:\WiseCartETL\LoadDimensions.dtsx`
4. **Schedule** sekmesi: Günlük/saatlik çalıştırma ayarla

### DTExec ile (Command Line)
```cmd
dtexec /f "C:\WiseCartETL\LoadDimensions.dtsx"
```

---

## ✅ KONTROL LİSTESİ

- [ ] SSIS kurulu mu?
- [ ] Visual Studio SSDT extension'ı var mı?
- [ ] SSIS projesi oluşturuldu mu?
- [ ] Connection Managers tanımlandı mı?
- [ ] Package 1: LoadDimensions oluşturuldu mu?
- [ ] Package 2: LoadFacts oluşturuldu mu?
- [ ] Package 3: DataCleansing oluşturuldu mu?
- [ ] Package 4: ErrorHandling oluşturuldu mu?
- [ ] Package 5: IncrementalLoad oluşturuldu mu?
- [ ] Package 6: FullETL oluşturuldu mu? (Bonus)
- [ ] Logging etkinleştirildi mi?
- [ ] Package'lar test edildi mi?
- [ ] SQL Server Agent Job oluşturuldu mu?

---

## 🎯 SONUÇ

Bu rehberi takip ederek:
- ✅ ETL adımları takip edilecek
- ✅ 5+ farklı türde SSIS package oluşturulacak
- ✅ Veri ambarı temel özellikleri barındıracak

**Toplam 30 puan kazanılacak!** 🎉

---

## 📚 EK KAYNAKLAR

- [Microsoft SSIS Documentation](https://docs.microsoft.com/en-us/sql/integration-services/)
- [SSIS Tutorial](https://docs.microsoft.com/en-us/sql/integration-services/ssis-how-to-create-an-etl-package)
- [SSIS Best Practices](https://docs.microsoft.com/en-us/sql/integration-services/ssis-best-practices)


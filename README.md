# 🛒 WiseCart - Akıllı Fiyat Karşılaştırma ve Ürün Analiz Platformu

WiseCart, yazılım mühendisliği öğrencilerinin seçmeli ve zorunlu derslerini birleştirerek geliştirdiği, teknoloji tabanlı bir e-ticaret çözümüdür.

## 📋 Proje Hakkında

WiseCart, kullanıcıların ürün fiyatlarını karşılaştırmasına, fiyat tahminleri almasına ve favori ürünlerini takip etmesine olanak sağlayan bir web platformudur. Proje, makine öğrenmesi, veri ambarı, servis odaklı mimari ve ileri web programlama teknolojilerini içerir.

## 🏗️ Mimari

### Teknolojiler
- **Backend**: .NET 8.0 (ASP.NET Core MVC)
- **AI/ML**: Python (Flask, scikit-learn, pandas)
- **Veritabanı**: Microsoft SQL Server (OLTP + OLAP)
- **Servisler**: SOAP, gRPC, REST API
- **Frontend**: Bootstrap 5, jQuery, Chart.js
- **Logging**: Node.js (Express)

### Servisler
1. **Python Flask API** (Port 5000) - ML model servisi
2. **Python SOAP Server** (Port 8000) - Döviz kuru servisi
3. **Python gRPC Server** (Port 50051) - Sistem durumu servisi
4. **Node.js Log Service** (Port 4000) - Loglama servisi
5. **.NET Web Application** (Port 5133) - Ana web uygulaması

## 🚀 Kurulum

### Gereksinimler
- .NET 8.0 SDK
- Python 3.8+
- Node.js 16+
- SQL Server 2019+ (veya Docker)
- Visual Studio 2022 veya VS Code

### Adımlar

1. **Repository'yi klonlayın**
```bash
git clone <repository-url>
cd wisecart
```

2. **Python bağımlılıklarını yükleyin**
```bash
cd AI_Engine
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Node.js bağımlılıklarını yükleyin**
```bash
cd ../Log_Service
npm install
```

4. **Veritabanını oluşturun**
- SQL Server'ı başlatın
- `Database/create_all_tables.sql` dosyasını çalıştırın
- `Database/advanced_features.sql` dosyasını çalıştırın

5. **Servisleri başlatın**

**Windows:**
```bash
start_all_services.bat
```

**macOS/Linux:**
```bash
chmod +x SERVISLERI_BASLAT.sh
./SERVISLERI_BASLAT.sh
```

6. **Web uygulamasını açın**
```
http://localhost:5133
```

## 📁 Proje Yapısı

```
wisecart/
├── AI_Engine/              # Python ML servisleri
│   ├── api_server.py      # Flask API
│   ├── soap_server.py     # SOAP servisi
│   ├── grpc_server.py     # gRPC servisi
│   └── train_model.py     # ML model eğitimi
├── Database/               # Veritabanı scriptleri
│   ├── create_all_tables.sql
│   ├── create_data_warehouse.sql
│   └── user_defined_functions.sql
├── Log_Service/           # Node.js log servisi
│   └── server.js
├── WiseCart_Web/          # .NET MVC uygulaması
│   ├── Controllers/
│   ├── Models/
│   └── Views/
└── README.md
```

## 🎯 Özellikler

### Kullanıcı Özellikleri
- ✅ Ürün arama ve filtreleme
- ✅ Fiyat tahmini (ML modeli ile)
- ✅ Favori ürünler
- ✅ Fiyat geçmişi takibi
- ✅ Kullanıcı profili

### Admin Özellikleri
- ✅ Ürün yönetimi (CRUD)
- ✅ Kullanıcı yönetimi
- ✅ Sistem logları

### Teknik Özellikler
- ✅ Servis odaklı mimari (SOA)
- ✅ Veri ambarı (OLAP Cube)
- ✅ Makine öğrenmesi entegrasyonu
- ✅ Real-time loglama

## 📊 Veritabanı

### OLTP (WiseCartDB)
- Products, Users, Categories, Brands
- PriceHistory, Favorites, SystemLogs

### OLAP (WiseCartDW)
- Yıldız şeması (Star Schema)
- Dimension tabloları (DimDate, DimProduct, DimCategory, DimBrand, DimUser)
- Fact tabloları (FactSales, FactFavorites)

## 🔧 Geliştirme

### Environment Variables
`.env.example` dosyasını `.env` olarak kopyalayın ve değerleri doldurun.

### API Endpoints
- **Python API**: `http://localhost:5000/predict`
- **SOAP**: `http://localhost:8000`
- **gRPC**: `localhost:50051`
- **Log Service**: `http://localhost:4000/api/log`

## 📝 Dokümantasyon

- [Veri Ambarı Rehberi](Database/VERI_AMBARI_REHBERI.md)
- [OLAP Cube Rehberi](Database/OLAP_CUBE_REHBERI.md)
- [SSIS Package Rehberi](Database/SSIS_PACKAGE_REHBERI.md)
- [Proje İster Analizi](PROJE_ISTER_ANALIZI.md)

## 👥 Takım

- Proje, yazılım mühendisliği öğrencileri tarafından geliştirilmiştir.

## 📄 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

## 🐛 Sorun Bildirimi

Sorunlar için issue açabilirsiniz.

## 🔄 Güncellemeler

- **v1.0.0** - İlk sürüm
  - Temel CRUD işlemleri
  - ML model entegrasyonu
  - Veri ambarı yapısı
  - OLAP Cube desteği

---

**Not**: Bu proje, yazılım mühendisliği ders projesi kapsamında geliştirilmiştir.

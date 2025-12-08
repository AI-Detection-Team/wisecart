import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setup_database import Base, Product, Category, Brand, PriceHistory, Role
import urllib

# AYARLAR (Kendi sunucu adını kontrol et!)
SERVER_NAME = r"localhost\SQLEXPRESS" 
DATABASE_NAME = "WiseCartDB"
CSV_PATH = "../AI_Engine/cleaned_data.csv"

# Kategoriye Göre Resimler (Görsellik için)
CATEGORY_IMAGES = {
    "Laptop": "https://cdn.vatanbilgisayar.com/Upload/PRODUCT/apple/thumb/114757-1_large.jpg",
    "Telefon": "https://cdn.vatanbilgisayar.com/Upload/PRODUCT/iphone/thumb/135151-1_large.jpg",
    "Tablet": "https://cdn.vatanbilgisayar.com/Upload/PRODUCT/samsung/thumb/139932-1_large.jpg",
    "Televizyon": "https://cdn.vatanbilgisayar.com/Upload/PRODUCT/samsung/thumb/144675-1_large.jpg",
    "AkilliSaat": "https://cdn.vatanbilgisayar.com/Upload/PRODUCT/apple/thumb/141042-1_large.jpg",
    "Monitor": "https://cdn.vatanbilgisayar.com/Upload/PRODUCT/asus/thumb/133748-1_large.jpg"
}
DEFAULT_IMG = "https://via.placeholder.com/500x500?text=Urun"

# Bağlantı
params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    f"Trusted_Connection=yes;"
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
Session = sessionmaker(bind=engine)
session = Session()

def clean_price_value(price_val):
    """Fiyatı temizler: 10.750 -> 10750.0"""
    if pd.isna(price_val): return 0.0
    price_str = str(price_val)
    # Eğer zaten düzgünse (10750.0 gibi)
    if price_str.replace('.', '', 1).isdigit(): return float(price_str)
    
    # Noktaları sil (Binlik ayracı)
    clean_str = price_str.replace(".", "").replace(",", ".")
    try:
        return float(clean_str)
    except:
        return 0.0

def import_data():
    print("🚀 VERİ DÜZELTME VE AKTARIM BAŞLIYOR...")
    
    # 0. Önceki Ürünleri Temizleyelim mi? (Temiz başlangıç için EVET)
    # Dikkat: Bu işlem Users tablosuna dokunmaz, sadece ürünleri sıfırlar.
    try:
        session.query(PriceHistory).delete()
        session.query(Product).delete()
        session.query(Brand).delete()
        session.query(Category).delete()
        session.commit()
        print("🧹 Eski ürün verileri temizlendi.")
    except Exception as e:
        session.rollback()
        print(f"⚠️ Temizleme uyarısı: {e}")

    # 1. Rolleri Ekle
    if not session.query(Role).first():
        session.add(Role(Name="Admin"))
        session.add(Role(Name="User"))
        session.commit()

    # 2. CSV Oku
    try:
        df = pd.read_csv(CSV_PATH)
        print(f"📄 {len(df)} satır veri okundu.")
    except:
        print("❌ CSV bulunamadı!")
        return

    # 3. Kategori ve Marka
    unique_cats = df['Kategori'].unique()
    for cat in unique_cats:
        if not session.query(Category).filter_by(Name=cat).first():
            session.add(Category(Name=cat))
    
    unique_brands = df['Marka'].unique()
    for brand in unique_brands:
        if not session.query(Brand).filter_by(Name=brand).first():
            session.add(Brand(Name=brand))
    
    session.commit()

    cat_map = {c.Name: c.Id for c in session.query(Category).all()}
    brand_map = {b.Name: b.Id for b in session.query(Brand).all()}

    # 4. Ürünleri Ekle
    print("🔹 Ürünler ekleniyor...")
    count = 0
    for _, row in df.iterrows():
        real_price = clean_price_value(row['Fiyat'])
        if real_price == 0: continue

        # Kategoriye uygun resim seç
        cat_name = row['Kategori']
        img_url = CATEGORY_IMAGES.get(cat_name, DEFAULT_IMG)

        product = Product(
            Name=row['Model'],
            Model=row['Model'],
            CurrentPrice=real_price,
            ReviewCount=int(float(row['Yorum_Sayisi'])), # Bazen float gelebilir
            Url=row['Link'],
            ImageUrl=img_url, # YENİ: Resim URL'si
            CategoryId=cat_map.get(cat_name),
            BrandId=brand_map.get(row['Marka'])
        )
        session.add(product)
        session.flush()
        
        history = PriceHistory(Price=real_price, ProductId=product.Id)
        session.add(history)
        
        count += 1
        if count % 500 == 0: print(f"   ... {count} ürün eklendi.")

    session.commit()
    print(f"✅ İŞLEM TAMAM! {count} ürün (Düzeltilmiş Fiyat & Resimler) yüklendi.")

if __name__ == "__main__":
    import_data()
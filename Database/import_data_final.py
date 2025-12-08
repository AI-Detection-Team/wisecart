import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setup_database import Base, Product, Category, Brand, PriceHistory, Role
import urllib

# AYARLAR (Kendi server adınızı yazın!)
SERVER_NAME = r"localhost\SQLEXPRESS" 
DATABASE_NAME = "WiseCartDB"
CSV_PATH = "../AI_Engine/tum_urunler_v3.csv" # Yeni dosya

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

def import_final_data():
    print("🚀 FİNAL VERİ AKTARIMI BAŞLIYOR...")
    
    # 0. Eski Verileri Temizle (Temiz sayfa açıyoruz)
    try:
        session.query(PriceHistory).delete()
        session.query(Product).delete()
        session.query(Brand).delete()
        session.query(Category).delete()
        session.commit()
        print("🧹 Eski veriler silindi.")
    except Exception as e:
        session.rollback()
        print(f"⚠️ Silme uyarısı: {e}")

    # 1. Rolleri Kontrol Et
    if not session.query(Role).first():
        session.add(Role(Name="Admin"))
        session.add(Role(Name="User"))
        session.commit()

    # 2. CSV Oku
    try:
        df = pd.read_csv(CSV_PATH)
        print(f"📄 {len(df)} satır veri okundu.")
    except:
        print(f"❌ '{CSV_PATH}' bulunamadı! Pınar scraper_v3.py'yi çalıştırdı mı?")
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

    # 4. Ürünleri Ekle (RESİMLİ)
    count = 0
    for _, row in df.iterrows():
        try:
            # Fiyat zaten float olmalı ama garanti olsun
            price = float(row['Fiyat'])
            if price < 10: continue # Aşırı ucuz hatalı veriyi atla
            
            # Resim URL (CSV'den gelen)
            img_url = row['Resim']
            if pd.isna(img_url) or img_url == "":
                img_url = "https://via.placeholder.com/500?text=Resim+Yok"

            product = Product(
                Name=row['Model'],
                Model=row['Model'],
                CurrentPrice=price,
                ReviewCount=int(float(row['Yorum_Sayisi'])),
                Url=row['Link'],
                ImageUrl=img_url, # <-- İŞTE BURADA GERÇEK RESİM GELİYOR
                CategoryId=cat_map.get(row['Kategori']),
                BrandId=brand_map.get(row['Marka'])
            )
            session.add(product)
            session.flush()
            
            history = PriceHistory(Price=price, ProductId=product.Id)
            session.add(history)
            count += 1
        except: continue

    session.commit()
    print(f"✅ MÜKEMMEL! {count} adet ürün (Resimli ve Doğru Fiyatlı) yüklendi.")

if __name__ == "__main__":
    import_final_data()
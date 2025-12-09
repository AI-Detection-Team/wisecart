import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setup_database import Base, Product, Category, Brand, PriceHistory, Role
import urllib

# AYARLAR (Kendi sunucunu kontrol et)
SERVER_NAME = r"localhost\SQLEXPRESS" 
DATABASE_NAME = "WiseCartDB"
CSV_PATH = "../AI_Engine/tum_urunler_v3.csv" # Pınar'ın en son çektiği resimli dosya

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
    print("🚀 RESİMLİ VERİ AKTARIMI BAŞLIYOR...")
    
    # 0. Temizlik
    try:
        session.query(PriceHistory).delete()
        session.query(Product).delete()
        session.query(Brand).delete()
        session.query(Category).delete()
        session.commit()
    except: session.rollback()

    # 1. Veriyi Oku
    try:
        df = pd.read_csv(CSV_PATH)
        # Resim sütunu yoksa oluştur (Hata almamak için)
        if 'Resim' not in df.columns: df['Resim'] = "" 
    except:
        print("❌ CSV bulunamadı!")
        return

    # 2. Kategoriler ve Markalar
    for cat in df['Kategori'].unique():
        if not session.query(Category).filter_by(Name=cat).first(): session.add(Category(Name=cat))
    for brand in df['Marka'].unique():
        if not session.query(Brand).filter_by(Name=brand).first(): session.add(Brand(Name=brand))
    session.commit()

    cat_map = {c.Name: c.Id for c in session.query(Category).all()}
    brand_map = {b.Name: b.Id for b in session.query(Brand).all()}

    # 3. Ürünleri Ekle
    count = 0
    for _, row in df.iterrows():
        try:
            # Fiyatı temizle
            price = float(str(row['Fiyat']).replace("TL","").replace(".","").replace(",", ".")) if isinstance(row['Fiyat'], str) else float(row['Fiyat'])
            if price < 10: continue

            # RESİM URL KONTROLÜ
            img_url = row['Resim'] if pd.notna(row['Resim']) and row['Resim'] != "" else "https://via.placeholder.com/300"

            product = Product(
                Name=row['Model'],
                Model=row['Model'],
                CurrentPrice=price,
                ReviewCount=int(float(row['Yorum_Sayisi'])),
                Url=row['Link'],
                ImageUrl=img_url, # <-- BURASI DÜZELTİLDİ
                CategoryId=cat_map.get(row['Kategori']),
                BrandId=brand_map.get(row['Marka'])
            )
            session.add(product)
            session.flush()
            session.add(PriceHistory(Price=price, ProductId=product.Id))
            count += 1
        except: continue

    session.commit()
    print(f"✅ İŞLEM TAMAM! {count} ürün resimleriyle yüklendi.")

if __name__ == "__main__":
    import_final_data()
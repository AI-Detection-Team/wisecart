import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setup_database import Base, Product, Category, Brand, PriceHistory, Role
import urllib

# AYARLAR
SERVER_NAME = r"localhost\SQLEXPRESS" 
DATABASE_NAME = "WiseCartDB"
CSV_PATH = "../AI_Engine/cleaned_data.csv"

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

def import_data():
    print("🚀 MSSQL Veri Aktarımı Başlıyor...")
    
    # 0. Rolleri Ekle (Admin/User)
    if not session.query(Role).first():
        session.add(Role(Name="Admin"))
        session.add(Role(Name="User"))
        session.commit()

    # 1. CSV Oku
    try:
        df = pd.read_csv(CSV_PATH)
        print(f"📄 {len(df)} satır veri okundu.")
    except:
        print("❌ CSV bulunamadı!")
        return

    # 2. Kategori ve Marka (Tekrarsız)
    print("🔹 Kategoriler ve Markalar işleniyor...")
    unique_cats = df['Kategori'].unique()
    for cat in unique_cats:
        if not session.query(Category).filter_by(Name=cat).first():
            session.add(Category(Name=cat))
    
    unique_brands = df['Marka'].unique()
    for brand in unique_brands:
        if not session.query(Brand).filter_by(Name=brand).first():
            session.add(Brand(Name=brand))
    
    session.commit()

    # ID Mapping
    cat_map = {c.Name: c.Id for c in session.query(Category).all()}
    brand_map = {b.Name: b.Id for b in session.query(Brand).all()}

    # 3. Ürünler
    print("🔹 Ürünler ekleniyor...")
    count = 0
    for _, row in df.iterrows():
        try: price = float(row['Fiyat'])
        except: continue

        product = Product(
            Name=row['Model'],
            Model=row['Model'],
            CurrentPrice=price,
            ReviewCount=int(row['Yorum_Sayisi']),
            Url=row['Link'],
            CategoryId=cat_map.get(row['Kategori']),
            BrandId=brand_map.get(row['Marka'])
        )
        session.add(product)
        session.flush() # ID almak için
        
        # Fiyat Geçmişi
        history = PriceHistory(Price=price, ProductId=product.Id)
        session.add(history)
        
        count += 1
        if count % 500 == 0: print(f"   ... {count} ürün eklendi.")

    session.commit()
    print(f"✅ İŞLEM TAMAM! {count} ürün MSSQL'e yüklendi.")

if __name__ == "__main__":
    import_data()